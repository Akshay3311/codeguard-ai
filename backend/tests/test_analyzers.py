import pytest
from pathlib import Path
from app.analyzers.ast_visitor import analyze_code_ast
from app.analyzers.metrics import calculate_file_metrics
from app.analyzers.static_bandit import scan_file_security

FIXTURE_VULN = Path(__file__).parent / "fixtures" / "sample_vulnerable_app.py"
FIXTURE_CLEAN = Path(__file__).parent / "fixtures" / "sample_clean_app.py"


def test_ast_visitor_detects_code_smells():
    with open(FIXTURE_VULN, "r", encoding="utf-8") as f:
        code = f.read()

    res = analyze_code_ast("sample_vulnerable_app.py", code)
    assert res["syntax_error"] is False
    findings = res["findings"]

    # Check that mutable default argument was caught
    mutable_defaults = [f for f in findings if "Mutable Default" in f.title]
    assert len(mutable_defaults) >= 1
    assert mutable_defaults[0].category == "bug"
    assert mutable_defaults[0].severity == "high"

    # Check excessive parameters
    param_findings = [f for f in findings if "Parameter Count" in f.title]
    assert len(param_findings) >= 1
    assert param_findings[0].category == "quality"

    # Check deep nesting
    nesting_findings = [f for f in findings if "Nested" in f.title]
    assert len(nesting_findings) >= 1

    # Check swallowed exception
    swallowed = [f for f in findings if "Swallowed Exception" in f.title]
    assert len(swallowed) >= 1


def test_static_security_scanner_detects_vulnerabilities():
    with open(FIXTURE_VULN, "r", encoding="utf-8") as f:
        code = f.read()

    findings = scan_file_security("sample_vulnerable_app.py", code)
    
    # 1. Command Injection
    cmd_inj = [f for f in findings if "Command Injection" in f.title]
    assert len(cmd_inj) >= 1
    assert cmd_inj[0].severity == "critical"

    # 2. Dynamic eval()
    eval_inj = [f for f in findings if "Arbitrary Code Execution" in f.title]
    assert len(eval_inj) >= 1
    assert eval_inj[0].severity == "critical"

    # 3. SQL Injection via f-string
    sql_inj = [f for f in findings if "SQL Injection" in f.title]
    assert len(sql_inj) >= 1

    # 4. Weak MD5 Hash
    hash_weak = [f for f in findings if "Weak Hash" in f.title]
    assert len(hash_weak) >= 1

    # 5. Hardcoded secret
    secret = [f for f in findings if "Hardcoded Secret" in f.title]
    assert len(secret) >= 1


def test_metrics_calculation():
    with open(FIXTURE_VULN, "r", encoding="utf-8") as f:
        vuln_code = f.read()
    with open(FIXTURE_CLEAN, "r", encoding="utf-8") as f:
        clean_code = f.read()

    vuln_m = calculate_file_metrics("sample_vulnerable_app.py", vuln_code)
    clean_m = calculate_file_metrics("sample_clean_app.py", clean_code)

    assert vuln_m["cyclomatic_complexity"] > clean_m["cyclomatic_complexity"]
    assert vuln_m["cognitive_complexity"] > clean_m["cognitive_complexity"]
    assert clean_m["maintainability_index"] > vuln_m["maintainability_index"]
    assert clean_m["maintainability_index"] >= 75.0
