# AI Usage & Transparency Log

This document records the AI tools, methodologies, and architectural contributions utilized during the engineering of **CodeGuard AI**.

---

### AI Tools Utilized
1. **Google Antigravity Agent (Gemini 3.7 Flash High)**:
   - **Role**: Technical co-pilot, automated boilerplate scaffolding, test authoring assistance, and system planning.
2. **Local Heuristic AI Engine & RAG Retriever**:
   - **Role**: Deterministic offline knowledge retrieval and agent reasoning fallback engine.
3. **Pluggable LLM Providers (OpenAI GPT-4o-mini / Google Gemini 1.5 Flash)**:
   - **Role**: Specialized reasoning agents providing contextual natural language explanations and refactoring roadmaps.

---

### Major Assistance Received
- Structuring the multi-agent swarm architecture and Review Coordinator deduplication pipeline.
- Designing the mathematical formula for normalized Technical Debt scoring and developer remediation effort estimation.
- Drafting AST visitor rules for Python clean code and OWASP security pattern identification.
- Building the comprehensive test suite with mock fixtures and FastAPI test client harnesses.

---

### Code & Architectural Decisions Driven by the Engineer
- **AST-First Deterministic Scanning**: Established the design principle that static tools must execute first before LLM invocation, preventing token waste and hallucinated line numbers.
- **RAG Knowledge Grounding**: Curated authentic Markdown knowledge documents directly representing PEP 8, SEI Maintainability standards, and OWASP Top 10 Python best practices.
- **Strict Pydantic Schema Validation**: Enforced that all agent outputs pass strict Pydantic v2 validation before entering database persistence or application state.
- **Safe Sandboxed Execution**: Guaranteed that user repositories are analyzed purely via static parsing and tokenization—strictly prohibiting dynamic execution of untrusted repository code.
