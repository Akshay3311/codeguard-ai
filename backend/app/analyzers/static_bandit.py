import ast
import re
from typing import List, Optional
from app.schemas.finding import FindingBase


class SecurityASTScanner(ast.NodeVisitor):
    """
    Deterministic AST-based security analysis scanner inspired by Bandit rules.
    Detects critical OWASP vulnerabilities, unsafe function calls, command injection,
    raw SQL injection, insecure deserialization, and hardcoded secrets without executing code.
    """

    def __init__(self, file_path: str, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.lines = source_code.splitlines()
        self.findings: List[FindingBase] = []

        # Secret regex patterns
        self.secret_keywords = re.compile(
            r"(api[_-]?key|secret|password|auth[_-]?token|access[_-]?token|private[_-]?key|jwt[_-]?secret)",
            re.IGNORECASE
        )
        self.sql_keywords = re.compile(
            r"\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|FROM|WHERE)\b",
            re.IGNORECASE
        )

    def _get_snippet(self, line: int) -> str:
        if 1 <= line <= len(self.lines):
            return self.lines[line - 1].strip()
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        func_name = ""
        module_name = ""

        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id

        # 1. Dangerous eval() / exec()
        if func_name in ("eval", "exec", "compile"):
            self.findings.append(FindingBase(
                category="security",
                severity="critical",
                file=self.file_path,
                line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                title=f"Arbitrary Code Execution via '{func_name}()'",
                description=f"Use of '{func_name}()' allows dynamic Python code execution. If untrusted input reaches this call, an attacker can achieve remote code execution (RCE).",
                evidence=self._get_snippet(node.lineno),
                source="bandit",
                confidence=0.98,
                recommendation=f"Replace '{func_name}()' with safe parsing methods such as 'ast.literal_eval()' or standard library data parsers (json, yaml).",
                technical_debt_impact=9,
                rag_source="owasp_top_10_python.md#code-injection"
            ))

        # 2. Subprocess with shell=True (Command Injection)
        if module_name in ("subprocess", "os") or func_name in ("Popen", "run", "call", "check_call", "check_output", "system"):
            for keyword in node.keywords:
                if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    self.findings.append(FindingBase(
                        category="security",
                        severity="critical",
                        file=self.file_path,
                        line=node.lineno,
                        end_line=getattr(node, "end_lineno", node.lineno),
                        title="Command Injection Risk with 'shell=True'",
                        description="Executing subprocesses with 'shell=True' invokes the system shell directly, allowing command chaining (e.g. '; rm -rf') if parameters are not strictly sanitized.",
                        evidence=self._get_snippet(node.lineno),
                        source="bandit",
                        confidence=0.95,
                        recommendation="Set 'shell=False' and pass arguments as a list of strings (e.g. ['git', 'status']).",
                        technical_debt_impact=8,
                        rag_source="owasp_top_10_python.md#command-injection"
                    ))

        # 3. Insecure Deserialization: pickle.loads / pickle.load / yaml.load without SafeLoader
        if (module_name == "pickle" and func_name in ("loads", "load")) or (module_name == "_pickle"):
            self.findings.append(FindingBase(
                category="security",
                severity="critical",
                file=self.file_path,
                line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                title="Insecure Deserialization via 'pickle'",
                description="Python 'pickle' deserialization can execute arbitrary code embedded in malicious pickle payloads via the '__reduce__' protocol.",
                evidence=self._get_snippet(node.lineno),
                source="bandit",
                confidence=0.95,
                recommendation="Use safe serialization formats such as JSON or Protocol Buffers, or verify signatures with HMAC before unpickling.",
                technical_debt_impact=9,
                rag_source="owasp_top_10_python.md#insecure-deserialization"
            ))

        if module_name == "yaml" and func_name == "load":
            has_safe_loader = any(
                k.arg == "Loader" and "SafeLoader" in ast.unparse(k.value)
                for k in node.keywords
            )
            if not has_safe_loader:
                self.findings.append(FindingBase(
                    category="security",
                    severity="high",
                    file=self.file_path,
                    line=node.lineno,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    title="Unsafe YAML Deserialization",
                    description="Calling 'yaml.load()' without 'Loader=yaml.SafeLoader' or using 'yaml.unsafe_load()' allows arbitrary Python object instantiation.",
                    evidence=self._get_snippet(node.lineno),
                    source="bandit",
                    confidence=0.95,
                    recommendation="Use 'yaml.safe_load()' instead of 'yaml.load()'.",
                    technical_debt_impact=7,
                    rag_source="owasp_top_10_python.md#insecure-deserialization"
                ))

        # 4. Weak Hashing: MD5 / SHA1
        if module_name == "hashlib" and func_name in ("md5", "sha1"):
            self.findings.append(FindingBase(
                category="security",
                severity="medium",
                file=self.file_path,
                line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                title=f"Cryptographically Weak Hash Algorithm '{func_name}'",
                description=f"Algorithm '{func_name.upper()}' is vulnerable to collision attacks and should not be used for password hashing, digital signatures, or security tokens.",
                evidence=self._get_snippet(node.lineno),
                source="bandit",
                confidence=0.9,
                recommendation="Use SHA-256 ('hashlib.sha256()') for checksums or Argon2 / bcrypt / PBKDF2 for password hashing.",
                technical_debt_impact=4,
                rag_source="owasp_top_10_python.md#weak-cryptography"
            ))

        # 5. Raw SQL Formatting in database calls (execute with f-string or % or .format)
        if func_name in ("execute", "executemany", "raw", "raw_query"):
            if node.args:
                first_arg = node.args[0]
                if isinstance(first_arg, ast.JoinedStr):
                    self.findings.append(FindingBase(
                        category="security",
                        severity="high",
                        file=self.file_path,
                        line=node.lineno,
                        end_line=getattr(node, "end_lineno", node.lineno),
                        title="SQL Injection Risk in Dynamic SQL Query",
                        description="Constructing SQL queries using f-strings allows untrusted input to alter query structure, resulting in SQL injection vulnerabilities.",
                        evidence=self._get_snippet(node.lineno),
                        source="bandit",
                        confidence=0.92,
                        recommendation="Use parameterized queries with placeholders (e.g., 'cursor.execute(\"SELECT * FROM users WHERE id = %s\", (user_id,))').",
                        technical_debt_impact=8,
                        rag_source="owasp_top_10_python.md#sql-injection"
                    ))
                elif isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Mod):
                    self.findings.append(FindingBase(
                        category="security",
                        severity="high",
                        file=self.file_path,
                        line=node.lineno,
                        end_line=getattr(node, "end_lineno", node.lineno),
                        title="SQL Injection Risk via String Interpolation",
                        description="Constructing SQL queries using '%' string formatting bypasses SQL parameter escaping.",
                        evidence=self._get_snippet(node.lineno),
                        source="bandit",
                        confidence=0.9,
                        recommendation="Replace string interpolation with query parameter binding.",
                        technical_debt_impact=8,
                        rag_source="owasp_top_10_python.md#sql-injection"
                    ))

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        # 6. Hardcoded Secrets detection
        for target in node.targets:
            target_name = ""
            if isinstance(target, ast.Name):
                target_name = target.id
            elif isinstance(target, ast.Attribute):
                target_name = target.attr

            if target_name and self.secret_keywords.search(target_name):
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    val = node.value.value.strip()
                    if len(val) >= 8 and not val.startswith("${") and not val.startswith("ENV_") and val.lower() not in ("none", "null", "test", "dummy", "placeholder", "your_secret_here"):
                        self.findings.append(FindingBase(
                            category="security",
                            severity="high",
                            file=self.file_path,
                            line=node.lineno,
                            end_line=node.lineno,
                            title=f"Potential Hardcoded Secret Assigned to '{target_name}'",
                            description=f"Variable '{target_name}' appears to store a hardcoded sensitive credential or API key in plain text.",
                            evidence=f"{target_name} = '***REDACTED***'",
                            source="bandit",
                            confidence=0.88,
                            recommendation="Extract sensitive credentials into environment variables or a secrets manager.",
                            technical_debt_impact=7,
                            rag_source="owasp_top_10_python.md#secrets-management"
                        ))

        # 7. SQL queries formatted via f-string assignment: query = f"SELECT ... {id}"
        if isinstance(node.value, ast.JoinedStr):
            # Check if any constant part contains SQL keywords
            for part in node.value.values:
                if isinstance(part, ast.Constant) and isinstance(part.value, str):
                    if self.sql_keywords.search(part.value):
                        self.findings.append(FindingBase(
                            category="security",
                            severity="high",
                            file=self.file_path,
                            line=node.lineno,
                            end_line=getattr(node, "end_lineno", node.lineno),
                            title="SQL Injection Risk in Formatted SQL String",
                            description="Building dynamic SQL query strings using f-string interpolation exposes the database to SQL injection attacks.",
                            evidence=self._get_snippet(node.lineno),
                            source="bandit",
                            confidence=0.92,
                            recommendation="Use parameterized SQL queries with query binding rather than direct string interpolation.",
                            technical_debt_impact=8,
                            rag_source="owasp_top_10_python.md#sql-injection"
                        ))
                        break

        self.generic_visit(node)


def scan_file_security(file_path: str, source_code: str) -> List[FindingBase]:
    """
    Runs deterministic AST security checks on a Python source file.
    """
    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError:
        return []

    scanner = SecurityASTScanner(file_path, source_code)
    scanner.visit(tree)
    return scanner.findings
