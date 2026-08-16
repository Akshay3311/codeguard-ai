# Architectural Decision Log (ADR)

This document records the major technical and architectural decisions made during the design and development of **CodeGuard AI - Multi-Agent AI Code Review & Technical Debt Analyzer**.

---

### Decision 1: Backend Framework Selection (FastAPI)
- **Decision**: Use FastAPI with Uvicorn and Pydantic v2 for the REST API backend.
- **Reason**: FastAPI provides native Python asynchronous (`async`/`await`) request handling, automatic OpenAPI/Swagger interactive documentation (`/docs`), strict runtime schema validation via Pydantic, and lightweight execution speed.
- **Alternative**: Django / Flask.
- **Why rejected**: Django is excessively heavyweight for an asynchronous review pipeline; Flask lacks native async background tasks and automatic type-safe OpenAPI schema validation without multiple third-party plugins.

---

### Decision 2: Database Persistence & Storage Strategy (SQLAlchemy 2.0 Async + Dual DB Support)
- **Decision**: Use SQLAlchemy 2.0 async engine with PostgreSQL for production containerized deployment, and automatic SQLite (`aiosqlite`) fallback for local developer velocity.
- **Reason**: Enables zero-friction local developer onboarding and rapid testing while offering full enterprise relational support and migrations for PostgreSQL in Docker/Kubernetes environments.
- **Alternative**: MongoDB / DynamoDB / pure SQLite.
- **Why rejected**: Relational integrity is essential for linking repositories, analysis runs, file metrics, findings, and prioritized recommendations.

---

### Decision 3: Static Analysis Engine (Deterministic AST + Bandit Rules)
- **Decision**: Combine Python's native `ast` visitor with deterministic security heuristics inspired by Bandit (eval/exec, SQL injection, shell=True, insecure deserialization) and complexity calculations (McCabe Cyclomatic Complexity, Halstead volume, Maintainability Index).
- **Reason**: LLMs alone are non-deterministic, suffer from hallucinations, and have high latency and token costs. Deterministic static tools provide 100% reproducible line-level evidence and zero execution risk.
- **Alternative**: Relying purely on LLMs to read raw source files.
- **Why rejected**: Sending entire codebases to LLMs is cost-prohibitive, exceeds context limits, and produces inconsistent results without reproducible line numbers.

---

### Decision 4: Multi-Provider LLM Abstraction Layer
- **Decision**: Implement an abstract `BaseLLMProvider` supporting OpenAI, Google Gemini, Anthropic Claude, Ollama, and a built-in deterministic Heuristic fallback.
- **Reason**: Prevents vendor lock-in, allows swapping models via `.env` variables, and ensures the entire application and test suite execute flawlessly offline without requiring external API keys.
- **Alternative**: Hardcoding OpenAI API calls.
- **Why rejected**: Breaks offline testing, creates hard dependencies on external network services, and limits deployment flexibility.

---

### Decision 5: RAG Vector Knowledge Retrieval Architecture
- **Decision**: Implement a curated local markdown knowledge base (`data/knowledge/`) paired with TF-IDF/BM25 token-weighted vector embeddings and cosine similarity retrieval.
- **Reason**: Provides instant, deterministic, zero-latency grounding without requiring bulky vector database daemons or external embedding API charges. Injects authoritative software engineering standards (PEP 8, OWASP Top 10, SEI maintainability benchmarks) directly into agent prompts with verifiable citations.
- **Alternative**: Pinecone / Weaviate / Unindexed prompt stuffing.
- **Why rejected**: External vector databases add unnecessary operational complexity for a fixed corpus of engineering best practices; prompt stuffing wastes context tokens.

---

### Decision 6: Multi-Agent Swarm Orchestration
- **Decision**: Implement a decoupled multi-agent swarm consisting of specialized agents (Code Quality, Security, Bug Detection, Technical Debt) unified by a central Review Coordinator.
- **Reason**: Role specialization produces higher precision prompts, avoids cognitive confusion, and allows each agent to focus on distinct risk domains. The Review Coordinator deduplicates overlapping issues and ensures consistent severity ranking.
- **Alternative**: Monolithic single-prompt reviewer or heavy agent frameworks (e.g. AutoGen / CrewAI).
- **Why rejected**: Monolithic prompts miss subtle edge cases; external heavy agent frameworks introduce fragile dependencies and non-deterministic looping.

---

### Decision 7: Frontend Architecture (React + Vite + Modern Vanilla CSS)
- **Decision**: Build a modern, responsive Single Page Application (SPA) using React 18 and Vite with a custom CSS design system using CSS custom properties.
- **Reason**: Delivers fast development rebuilds, clean component modularity, instant responsive interactions, and a bespoke developer-focused dark theme without CSS framework overhead.
- **Alternative**: Server-side rendered Jinja2 templates or Next.js.
- **Why rejected**: Jinja2 lacks interactive live progress polling and rich slide-out code inspection drawers; Next.js adds unnecessary server complexity for an API-backed dashboard.
