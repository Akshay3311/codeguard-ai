import ast
import re
from typing import List, Dict, Any, Optional
from app.schemas.finding import FindingBase


class CodeSmellDetector(ast.NodeVisitor):
    """
    Traverses Python AST to detect structural code smells, maintainability issues,
    and anti-patterns.
    """

    def __init__(self, file_path: str, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.lines = source_code.splitlines()
        self.findings: List[FindingBase] = []
        self.function_count = 0
        self.class_count = 0
        self.current_nesting = 0
        self.max_nesting = 0

    def _get_snippet(self, start_line: int, end_line: Optional[int] = None) -> str:
        if not self.lines or start_line < 1 or start_line > len(self.lines):
            return ""
        if end_line is None or end_line < start_line:
            end_line = min(start_line + 4, len(self.lines))
        else:
            end_line = min(end_line, start_line + 6, len(self.lines))
        return "\n".join(self.lines[start_line - 1:end_line])

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_count += 1
        func_len = getattr(node, "end_lineno", node.lineno) - node.lineno + 1

        # 1. Long Function Smell (> 50 lines)
        if func_len > 50:
            self.findings.append(FindingBase(
                category="quality",
                severity="medium" if func_len < 100 else "high",
                file=self.file_path,
                line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                title=f"Excessive Function Length ({func_len} lines) in '{node.name}'",
                description=f"Function '{node.name}' contains {func_len} lines of code. Functions exceeding 50 lines violate the Single Responsibility Principle and increase cognitive load.",
                evidence=self._get_snippet(node.lineno, node.lineno + 3),
                source="ast",
                confidence=1.0,
                recommendation="Decompose this function into smaller, single-purpose helper functions.",
                technical_debt_impact=min(10, int(func_len / 15)),
                rag_source="python_clean_code.md#function-design"
            ))

        # 2. Too Many Parameters Smell (> 5 arguments)
        args_count = len(node.args.args)
        if args_count > 5:
            self.findings.append(FindingBase(
                category="quality",
                severity="medium",
                file=self.file_path,
                line=node.lineno,
                end_line=node.lineno,
                title=f"Excessive Parameter Count ({args_count} params) in '{node.name}'",
                description=f"Function '{node.name}' takes {args_count} positional parameters. High parameter counts make function signatures fragile and hard to test.",
                evidence=self._get_snippet(node.lineno),
                source="ast",
                confidence=1.0,
                recommendation="Encapsulate parameters into a dataclass, Pydantic model, or configuration object.",
                technical_debt_impact=4,
                rag_source="python_clean_code.md#parameter-counts"
            ))

        # 3. Mutable Default Argument Smell (def foo(items=[]))
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.findings.append(FindingBase(
                    category="bug",
                    severity="high",
                    file=self.file_path,
                    line=default.lineno,
                    end_line=default.lineno,
                    title=f"Mutable Default Argument in '{node.name}'",
                    description=f"Function '{node.name}' uses a mutable default argument ({type(default).__name__}). In Python, default arguments are evaluated once at definition time, causing state to leak across function invocations.",
                    evidence=self._get_snippet(default.lineno),
                    source="ast",
                    confidence=1.0,
                    recommendation="Use 'None' as the default argument value and initialize the mutable object inside the function body.",
                    technical_debt_impact=6,
                    rag_source="python_clean_code.md#mutable-defaults"
                ))

        # 4. Naming convention check (snake_case for functions)
        if not re.match(r"^[a-z_][a-z0-9_]*$", node.name) and not (node.name.startswith("__") and node.name.endswith("__")):
            if re.match(r"^[a-zA-Z0-9]+$", node.name) and any(c.isupper() for c in node.name):
                self.findings.append(FindingBase(
                    category="quality",
                    severity="low",
                    file=self.file_path,
                    line=node.lineno,
                    end_line=node.lineno,
                    title=f"Non-standard Function Naming '{node.name}'",
                    description=f"Function '{node.name}' uses camelCase or mixed case instead of PEP 8 standard snake_case.",
                    evidence=self._get_snippet(node.lineno),
                    source="ast",
                    confidence=0.9,
                    recommendation=f"Rename function to snake_case (e.g., '{re.sub(r'(?<!^)(?=[A-Z])', '_', node.name).lower()}').",
                    technical_debt_impact=1,
                    rag_source="python_clean_code.md#pep8-naming"
                ))

        # Track nesting
        self.current_nesting += 1
        if self.current_nesting > self.max_nesting:
            self.max_nesting = self.current_nesting
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # Treat async functions same as regular for structural smells

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_count += 1
        
        # Check Class Naming (PascalCase)
        if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
            self.findings.append(FindingBase(
                category="quality",
                severity="low",
                file=self.file_path,
                line=node.lineno,
                end_line=node.lineno,
                title=f"Non-standard Class Naming '{node.name}'",
                description=f"Class '{node.name}' does not follow the PEP 8 PascalCase convention.",
                evidence=self._get_snippet(node.lineno),
                source="ast",
                confidence=0.9,
                recommendation="Rename class to PascalCase / CapWords convention.",
                technical_debt_impact=1,
                rag_source="python_clean_code.md#pep8-naming"
            ))

        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        # Star import smell: from module import *
        for alias in node.names:
            if alias.name == "*":
                self.findings.append(FindingBase(
                    category="quality",
                    severity="medium",
                    file=self.file_path,
                    line=node.lineno,
                    end_line=node.lineno,
                    title=f"Wildcard Import from '{node.module or 'module'}'",
                    description=f"Wildcard import 'from {node.module} import *' pollutes the local namespace, obscures symbol origins, and can cause unexpected naming collisions.",
                    evidence=self._get_snippet(node.lineno),
                    source="ast",
                    confidence=1.0,
                    recommendation="Explicitly import only the required symbols (e.g. 'from module import ClassA, func_b').",
                    technical_debt_impact=3,
                    rag_source="python_clean_code.md#import-hygiene"
                ))
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        for handler in node.handlers:
            # Bare except: or except BaseException:
            if handler.type is None:
                self.findings.append(FindingBase(
                    category="bug",
                    severity="high",
                    file=self.file_path,
                    line=handler.lineno,
                    end_line=handler.lineno,
                    title="Bare 'except:' Clause",
                    description="A bare 'except:' catches all exceptions, including SystemExit, KeyboardInterrupt, and MemoryError, making debugging and process termination unreliable.",
                    evidence=self._get_snippet(handler.lineno),
                    source="ast",
                    confidence=1.0,
                    recommendation="Catch specific exception classes (e.g., 'except ValueError:' or 'except Exception:').",
                    technical_debt_impact=5,
                    rag_source="error_handling_best_practices.md#exception-hierarchy"
                ))
            elif isinstance(handler.type, ast.Name) and handler.type.id in ("Exception", "BaseException"):
                # Check if body is just pass
                if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                    self.findings.append(FindingBase(
                        category="bug",
                        severity="high",
                        file=self.file_path,
                        line=handler.lineno,
                        end_line=handler.lineno,
                        title="Swallowed Exception with 'pass'",
                        description="Catching broad Exception and silently passing hides critical runtime failures, leading to corrupt internal state.",
                        evidence=self._get_snippet(handler.lineno, handler.lineno + 1),
                        source="ast",
                        confidence=1.0,
                        recommendation="Log the exception with traceback or handle the failure gracefully with fallback logic.",
                        technical_debt_impact=6,
                        rag_source="error_handling_best_practices.md#silent-failures"
                    ))
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.current_nesting += 1
        if self.current_nesting > 4:
            self.findings.append(FindingBase(
                category="quality",
                severity="medium",
                file=self.file_path,
                line=node.lineno,
                end_line=node.lineno,
                title=f"Deeply Nested Control Flow (Depth {self.current_nesting})",
                description=f"Control flow exceeds recommended nesting depth of 3 levels (current depth: {self.current_nesting}). Deep nesting drastically increases cyclomatic complexity and risk of logic errors.",
                evidence=self._get_snippet(node.lineno),
                source="ast",
                confidence=0.95,
                recommendation="Refactor nested blocks using guard clauses / early returns, or extract nested logic into helper methods.",
                technical_debt_impact=4,
                rag_source="python_clean_code.md#guard-clauses"
            ))
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_For(self, node: ast.For) -> None:
        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_While(self, node: ast.While) -> None:
        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1


def analyze_code_ast(file_path: str, source_code: str) -> Dict[str, Any]:
    """
    Parses Python source code into AST and extracts code smells and structure.
    """
    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError as e:
        return {
            "syntax_error": True,
            "error_message": f"Syntax error at line {e.lineno}: {e.msg}",
            "findings": [FindingBase(
                category="bug",
                severity="critical",
                file=file_path,
                line=e.lineno,
                end_line=e.lineno,
                title="Syntax Error in Python File",
                description=f"The file contains invalid Python syntax: {e.msg}",
                evidence=source_code.splitlines()[e.lineno - 1] if e.lineno and e.lineno <= len(source_code.splitlines()) else None,
                source="ast",
                confidence=1.0,
                recommendation="Fix Python syntax errors before deploying code.",
                technical_debt_impact=10,
                rag_source="python_clean_code.md"
            )],
            "function_count": 0,
            "class_count": 0,
            "max_nesting": 0
        }

    detector = CodeSmellDetector(file_path, source_code)
    detector.visit(tree)

    return {
        "syntax_error": False,
        "findings": detector.findings,
        "function_count": detector.function_count,
        "class_count": detector.class_count,
        "max_nesting": detector.max_nesting,
        "tree": tree
    }
