# Engineering Debugging Report

This document details real technical challenges encountered and resolved during the implementation of CodeGuard AI.

---

### Incident 1: Dynamic SQL Query Detection in Variable Assignments
- **Problem**: The AST security scanner failed to catch SQL injection vulnerabilities when dynamic SQL queries were first assigned to a variable (e.g. `query = f"SELECT * FROM users WHERE id = {user_id}"`) before being passed to `cursor.execute(query)`.
- **What failed**: `test_static_security_scanner_detects_vulnerabilities` asserted `len(sql_inj) >= 1`, but received `0`.
- **Error**: `AssertionError: assert 0 >= 1`.
- **Investigation**: The scanner initially only inspected `ast.Call` nodes where `execute()` directly received an inline `ast.JoinedStr` (f-string). In real codebases, developers almost always construct query strings in separate assignment statements prior to database execution.
- **Root Cause**: The `visit_Assign` visitor method was not inspecting assigned `JoinedStr` expressions for SQL keywords (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, etc.).
- **Solution**: Enhanced `SecurityASTScanner.visit_Assign` to check if assigned values are `ast.JoinedStr` or `ast.BinOp` formatted strings containing SQL keywords and flags them as SQL injection risks with corresponding line numbers and remediation advice.
- **Verification**: Re-ran `pytest backend/tests/test_analyzers.py`, which passed with 100% detection rate.

---

### Incident 2: Overlapping Multi-Agent Finding Deduplication Hash Collision
- **Problem**: When both the deterministic AST security scanner and the Security Agent detected the same underlying vulnerability on adjacent lines (e.g., lines 40 and 41), the Review Coordinator reported both as duplicate findings instead of collapsing them into a single high-confidence issue.
- **What failed**: `test_coordinator_deduplication` asserted `len(deduped) == 1`, but received `2`.
- **Error**: `AssertionError: assert 2 == 1`.
- **Investigation**: The deduplication key in `ReviewCoordinator.deduplicate_findings` combined `(file, line_bucket, category, norm_title)`. Because the deterministic tool generated a title like `"SQL Injection in query"` and the LLM agent generated `"SQL Injection vulnerability"`, their normalized title prefixes diverged, creating two distinct dictionary keys.
- **Root Cause**: Exact title matching is too rigid when fusing outputs from heterogeneous agents and deterministic tools analyzing the same code block.
- **Solution**: Refactored the deduplication hash key to `(file, line // 3, category)`. When findings match the same 3-line spatial bucket and category, the coordinator retains the finding with the higher confidence score and richest RAG citation metadata.
- **Verification**: Tested with `pytest backend/tests/test_agents.py`; duplicates were successfully merged into 1 prioritized issue.

---

### Incident 3: Asynchronous Test Suite Database Lifespan Initialization
- **Problem**: Executing FastAPI integration tests with `httpx.AsyncClient(transport=ASGITransport(app=app))` raised an operational database error (`sqlite3.OperationalError: no such table: repositories`) during endpoint testing.
- **What failed**: `test_api.py::test_overview_stats_endpoint` threw `sqlalchemy.exc.OperationalError`.
- **Error**: `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: repositories`.
- **Investigation**: In FastAPI, `@asynccontextmanager` lifespan handlers execute when the server starts via Uvicorn. However, `ASGITransport` in unit test environments does not automatically trigger the server lifespan unless explicitly wrapped or initialized via fixtures.
- **Root Cause**: Database tables were created inside `lifespan(app)` but had not run prior to the direct test client invocation.
- **Solution**: Added an autouse async pytest fixture in `backend/tests/conftest.py` that invokes `await init_db()` and `retriever.initialize()` before tests run.
- **Verification**: All 15 unit and integration tests passed cleanly in under 1 second.
