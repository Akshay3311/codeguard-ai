import pytest
from app.agents.debt_agent import TechnicalDebtAgent
from app.schemas.finding import FindingBase


def test_technical_debt_calculation_clean_code():
    agent = TechnicalDebtAgent()
    findings = []
    metrics = [{
        "file_path": "clean.py",
        "loc": 50,
        "sloc": 40,
        "cyclomatic_complexity": 2.0,
        "maintainability_index": 92.0
    }]
    
    res = agent.calculate_debt(findings, metrics, total_lines=50)
    
    assert res["overall_debt_score"] < 5.0
    assert res["overall_health_score"] >= 95.0
    assert res["remediation_hours"] == 0.0


def test_technical_debt_calculation_vulnerable_code():
    agent = TechnicalDebtAgent()
    findings = [
        FindingBase(
            category="security",
            severity="critical",
            file="vuln.py",
            line=10,
            title="Command Injection",
            description="...",
            source="bandit",
            confidence=0.95,
            recommendation="Fix it",
            technical_debt_impact=9
        ),
        FindingBase(
            category="bug",
            severity="high",
            file="vuln.py",
            line=20,
            title="Mutable Default",
            description="...",
            source="ast",
            confidence=1.0,
            recommendation="Fix it",
            technical_debt_impact=6
        )
    ]
    metrics = [{
        "file_path": "vuln.py",
        "loc": 120,
        "sloc": 100,
        "cyclomatic_complexity": 18.0,
        "maintainability_index": 55.0
    }]

    res = agent.calculate_debt(findings, metrics, total_lines=120)

    # Debt score must be > 15 and health score < 85
    assert res["overall_debt_score"] > 15.0
    assert res["overall_health_score"] < 85.0
    assert res["remediation_hours"] >= 6.0  # 4h for critical + 2h for high
