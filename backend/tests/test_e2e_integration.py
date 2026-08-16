import pytest
import os
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.session import AsyncSessionLocal
from app.database.models import AnalysisRun, Repository, Finding, TechnicalDebtMetric
from sqlalchemy import select

FIXTURES_DIR = str((Path(__file__).parent / "fixtures").resolve())


@pytest.mark.asyncio
async def test_full_analysis_workflow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Trigger analysis on sample fixture directory
        res = await client.post("/api/v1/analyze", json={
            "repository_url": FIXTURES_DIR,
            "branch": "main"
        })
        assert res.status_code == 202
        data = res.json()
        analysis_id = data["analysis_id"]
        assert analysis_id
        assert data["status"] == "queued"

        # 2. Check status endpoint
        status_res = await client.get(f"/api/v1/analysis/{analysis_id}")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert status_data["analysis_id"] == analysis_id

        # 3. Check findings endpoint
        findings_res = await client.get(f"/api/v1/analysis/{analysis_id}/findings")
        assert findings_res.status_code == 200

        # 4. Check full report endpoint
        report_res = await client.get(f"/api/v1/analysis/{analysis_id}/report")
        assert report_res.status_code == 200
        report_data = report_res.json()
        assert report_data["analysis_id"] == analysis_id
        assert "scores" in report_data
        assert "findings" in report_data
        assert "recommendations" in report_data
        assert len(report_data["findings"]) >= 5
        assert len(report_data["recommendations"]) >= 1
        assert report_data["scores"]["overall_health_score"] <= 90.0
        assert report_data["scores"]["technical_debt_score"] >= 10.0
