import pytest
from app.agents.coordinator import ReviewCoordinator
from app.schemas.finding import FindingBase


def test_coordinator_deduplication():
    coordinator = ReviewCoordinator()
    
    # Duplicate findings on same file and line bucket
    raw_findings = [
        FindingBase(
            category="security",
            severity="critical",
            file="app/db.py",
            line=40,
            title="SQL Injection in query",
            description="AST check detected raw sql formatting",
            source="bandit",
            confidence=0.90,
            recommendation="Use parameterized query",
            technical_debt_impact=8
        ),
        FindingBase(
            category="security",
            severity="critical",
            file="app/db.py",
            line=41,
            title="SQL Injection vulnerability",
            description="Security Agent detected user input in raw SQL",
            source="security_agent",
            confidence=0.95,
            recommendation="Use parameterized query with DB-API binding",
            technical_debt_impact=8,
            rag_source="owasp_top_10_python.md#sql-injection"
        )
    ]

    deduped = coordinator.deduplicate_findings(raw_findings)
    assert len(deduped) == 1
    # Should retain the higher confidence/RAG-backed finding
    assert deduped[0].confidence == 0.95
    assert deduped[0].rag_source == "owasp_top_10_python.md#sql-injection"


@pytest.mark.asyncio
async def test_coordinator_full_workflow():
    coordinator = ReviewCoordinator()
    raw_findings = [
        FindingBase(
            category="security",
            severity="critical",
            file="app/views.py",
            line=15,
            title="Command Injection",
            description="shell=True",
            source="bandit",
            confidence=0.95,
            recommendation="Set shell=False",
            technical_debt_impact=8
        )
    ]
    metrics = [{
        "file_path": "app/views.py",
        "loc": 60,
        "sloc": 50,
        "cyclomatic_complexity": 5.0,
        "maintainability_index": 70.0
    }]
    files_data = [{"file_path": "app/views.py", "loc": 60}]

    res = await coordinator.coordinate(
        raw_findings=raw_findings,
        metrics=metrics,
        files_data=files_data,
        total_lines=60,
        agent_logs={"security_agent": "Detected 1 critical vulnerability"}
    )

    assert len(res["findings"]) == 1
    assert len(res["recommendations"]) >= 1
    assert res["recommendations"][0]["category"] == "security"
    assert "CodeGuard AI analyzed" in res["executive_summary"]
