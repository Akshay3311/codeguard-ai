# CodeGuard AI REST API Reference

The backend exposes a type-safe REST API powered by FastAPI.

Interactive OpenAPI Documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Endpoints Summary

### 1. Health Check
`GET /health`
- **Description**: Verifies service status, database connectivity, RAG knowledge base indexing status, and configured LLM provider.
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "CodeGuard AI",
  "version": "1.0.0",
  "environment": "development",
  "database": "healthy",
  "rag_knowledge_base": {
    "status": "ready",
    "chunks_loaded": 18
  },
  "llm_provider": "heuristic"
}
```

---

### 2. Start Repository Analysis
`POST /api/v1/analyze`
- **Description**: Submits a GitHub/GitLab repository URL or local path for asynchronous analysis.
- **Request Body**:
```json
{
  "repository_url": "https://github.com/psf/requests",
  "branch": "main"
}
```
- **Response `202 Accepted`**:
```json
{
  "analysis_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "queued",
  "repository_url": "https://github.com/psf/requests",
  "message": "Repository analysis has been queued successfully."
}
```

---

### 3. Get Analysis Status
`GET /api/v1/analysis/{analysis_id}`
- **Description**: Retrieves live execution progress percentage, status step, and high-level health/debt scores.
- **Response `200 OK`**:
```json
{
  "analysis_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "repository_name": "requests",
  "status": "completed",
  "progress_percentage": 100,
  "current_step": "Analysis completed successfully",
  "health_score": 92.5,
  "technical_debt_score": 7.5,
  "security_score": 98.0,
  "quality_score": 88.0,
  "bugs_score": 95.0,
  "debt_remediation_hours": 3.5,
  "total_files": 24,
  "total_lines": 3420,
  "execution_time_seconds": 2.45
}
```

---

### 4. Get Findings
`GET /api/v1/analysis/{analysis_id}/findings`
- **Query Parameters**:
  - `category` (optional): `security`, `quality`, `bug`, `debt`
  - `severity` (optional): `critical`, `high`, `medium`, `low`, `info`
  - `file_path` (optional): substring filter
- **Response `200 OK`**: Array of structured findings.

---

### 5. Get Comprehensive Review Report
`GET /api/v1/analysis/{analysis_id}/report`
- **Description**: Retrieves complete review report containing executive summary, scores, findings summary, detailed findings, module metrics, and prioritized remediation recommendations.

---

### 6. Get Global Statistics
`GET /api/v1/overview/stats`
- **Description**: Returns aggregated metrics across all historical repository scans.
