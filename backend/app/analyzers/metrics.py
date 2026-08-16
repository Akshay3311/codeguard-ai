import ast
import math
import tokenize
import io
from typing import Dict, Any, Tuple


class ComplexityMetricsCalculator(ast.NodeVisitor):
    """
    Computes McCabe Cyclomatic Complexity, Cognitive Complexity,
    and Halstead Software Metrics for Python source files.
    """

    def __init__(self):
        self.cyclomatic_complexity = 1  # Base complexity for the module
        self.cognitive_complexity = 0
        self.current_nesting = 0
        self.operators = []
        self.operands = []

    def visit_If(self, node: ast.If) -> None:
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += (1 + self.current_nesting)
        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += (1 + self.current_nesting)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += (1 + self.current_nesting)
        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += (1 + self.current_nesting)
        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_While(self, node: ast.While) -> None:
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += (1 + self.current_nesting)
        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += (1 + self.current_nesting)
        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_With(self, node: ast.With) -> None:
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.cyclomatic_complexity += (len(node.values) - 1)
        self.cognitive_complexity += (len(node.values) - 1)
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self.cyclomatic_complexity += 1 + len(node.ifs)
        self.cognitive_complexity += 1 + len(node.ifs)
        self.generic_visit(node)


def calculate_halstead_metrics(source_code: str) -> Dict[str, float]:
    operators = []
    operands = []

    try:
        tokens = tokenize.generate_tokens(io.StringIO(source_code).readline)
        for tok_type, tok_val, _, _, _ in tokens:
            if tok_type in (tokenize.OP, tokenize.NAME) and tok_val in (
                "+", "-", "*", "/", "//", "%", "**", "&", "|", "^", "~", "<<", ">>",
                "==", "!=", "<", ">", "<=", ">=", "in", "not", "is", "and", "or",
                "=", "+=", "-=", "*=", "/=", "%=", "if", "for", "while", "return", "yield"
            ):
                operators.append(tok_val)
            elif tok_type in (tokenize.NAME, tokenize.NUMBER, tokenize.STRING):
                operands.append(tok_val)
    except Exception:
        pass

    n1 = len(set(operators))
    n2 = len(set(operands))
    N1 = len(operators)
    N2 = len(operands)

    vocabulary = n1 + n2
    length = N1 + N2
    volume = length * math.log2(vocabulary) if vocabulary > 0 else 0.0
    difficulty = ((n1 / 2.0) * (N2 / max(1, n2))) if n2 > 0 else 0.0
    effort = difficulty * volume

    return {
        "n1": float(n1),
        "n2": float(n2),
        "N1": float(N1),
        "N2": float(N2),
        "vocabulary": float(vocabulary),
        "length": float(length),
        "volume": round(volume, 2),
        "difficulty": round(difficulty, 2),
        "effort": round(effort, 2)
    }


def calculate_file_metrics(file_path: str, source_code: str) -> Dict[str, Any]:
    lines = source_code.splitlines()
    loc = len(lines)
    sloc = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))

    halstead = calculate_halstead_metrics(source_code)
    volume = halstead["volume"]

    calculator = ComplexityMetricsCalculator()
    try:
        tree = ast.parse(source_code, filename=file_path)
        calculator.visit(tree)
        cyclomatic = calculator.cyclomatic_complexity
        cognitive = calculator.cognitive_complexity
    except Exception:
        cyclomatic = 1.0
        cognitive = 0

    # Maintainability Index (SEI formula capped 0-100)
    # MI = 171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(SLOC)
    if sloc > 0:
        v_term = 5.2 * math.log(max(1.0, volume))
        cc_term = 0.23 * cyclomatic
        loc_term = 16.2 * math.log(max(1.0, float(sloc)))
        raw_mi = 171.0 - v_term - cc_term - loc_term
        mi = max(0.0, min(100.0, raw_mi))
    else:
        mi = 100.0

    return {
        "file_path": file_path,
        "loc": loc,
        "sloc": sloc,
        "cyclomatic_complexity": round(float(cyclomatic), 2),
        "cognitive_complexity": int(cognitive),
        "halstead_volume": round(float(volume), 2),
        "halstead_difficulty": round(float(halstead["difficulty"]), 2),
        "maintainability_index": round(float(mi), 2)
    }
