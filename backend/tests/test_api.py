import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert "CodeGuard AI" in data["service"]
        assert "rag_knowledge_base" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_analyze_invalid_url():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/analyze", json={"repository_url": "not-a-valid-url"})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_overview_stats_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/overview/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_repositories" in data
        assert "critical_issues" in data
        assert "average_technical_debt" in data
