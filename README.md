# CodeGuard AI
### *Multi-Agent AI Code Review & Technical Debt Analyzer*

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF.svg)](https://vitejs.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-15%20Passing-brightgreen.svg)]()

> **One-Line Description**: CodeGuard AI is an enterprise-grade AI developer productivity platform that analyzes GitHub repositories using deterministic static analysis, software metrics, RAG knowledge retrieval, specialized multi-agent AI, and an executive Review Coordinator to identify code-quality issues, security risks, potential bugs, maintainability problems, and technical debt.

---

## 1. Problem Statement & Why AI is Required

Modern software engineering repositories often contain tens of thousands of lines of code. Manual code review is slow, prone to human error, and struggles to systematically enforce security best practices, maintainability guidelines, and debt tracking across large teams.

Traditional static analysis tools (e.g. linters) detect rigid syntactic patterns, but they lack semantic understanding, cannot explain exploit impacts, and produce unprioritized lists of warnings that overwhelm developers.

**Why AI + Deterministic Analysis is Required**:
CodeGuard AI utilizes a hybrid architecture:
1. **Deterministic Static Analysis & Metrics** provides 100% reproducible line-level evidence, cyclomatic complexity calculations, and AST pattern matching with zero hallucination.
2. **RAG (Retrieval-Augmented Generation)** grounds evaluations in authoritative software engineering and security standards (PEP 8, OWASP Top 10 Python, SEI Maintainability benchmarks).
3. **Specialized Multi-Agent AI** reasons about the semantic context of findings, filters noise, explains business impact, and synthesizes a prioritized remediation roadmap.

---

## 2. Target Users

- **Software Developers & Reviewers**: Instant feedback on pull requests and code quality with contextual refactoring recommendations.
- **Engineering Managers & Tech Leads**: Transparent technical debt metrics, remediation effort estimations (developer hours), and architecture health tracking.
- **QA & Security Teams**: Automated screening for OWASP vulnerabilities, command/SQL injections, and insecure deserialization.
- **Students & Junior Engineers**: Educational explanations citing standard software engineering principles.

---

## 3. Core Architecture & Workflow

```
GitHub / Local Repository URL
              ↓
  Repository Sandbox Ingestion (git clone depth=1)
              ↓
  File Discovery & Filtering (.gitignore, size limits)
              ↓
  Python AST Parsing & Metrics Extraction (McCabe CC, Halstead, MI)
              ↓
  Deterministic Security Scanning (Bandit AST Heuristics)
              ↓
  RAG Knowledge Base Retrieval (TF-IDF & Cosine Similarity)
              ↓
┌───────────────────────────────────────────────────────────┐
│              Specialized Multi-Agent Swarm                │
│                                                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐  │
│  │  Quality Agent  │ │ Security Agent  │ │  Bug Agent  │  │
│  └─────────────────┘ └─────────────────┘ └─────────────┘  │
└───────────────────────────────────────────────────────────┘
              ↓
  Technical Debt Agent (Mathematical Scoring Formula)
              ↓
  Review Coordinator (Deduplication, Prioritization & Synthesis)
              ↓
  Database Persistence (PostgreSQL / SQLite)
              ↓
  React + Vite Developer Dashboard & Markdown/JSON Export
```

---

## 4. Multi-Agent Swarm

CodeGuard AI features 5 distinct, specialized agents:
- **Code Quality Agent**: Analyzes code smells, function length (>50 lines), parameter counts (>5), naming hygiene, and maintainability deficits.
- **Security Agent**: Evaluates OWASP Top 10 vulnerabilities, command injection (`shell=True`), dynamic SQL strings, arbitrary code execution (`eval`/`exec`), insecure deserialization (`pickle`), and hardcoded credentials.
- **Bug Detection Agent**: Identifies edge-case risks, unhandled exceptions, swallowed errors (`except: pass`), mutable default parameters, and resource leaks.
- **Technical Debt Agent**: Calculates the transparent mathematical technical debt score (0-100) and estimated developer remediation hours based on measurable signals.
- **Review Coordinator**: Normalizes schema output, deduplicates overlapping issues across tools and agents, assigns priorities, and generates the executive report.

---

## 5. Technical Debt Scoring Methodology

The Technical Debt Agent computes a transparent, measurable score (0–100):

$$\text{Debt Score} = \min\left(100, \, w_{\text{sec}} \cdot S_{\text{sec}} + w_{\text{qual}} \cdot S_{\text{qual}} + w_{\text{bug}} \cdot S_{\text{bug}} + w_{\text{cpx}} \cdot S_{\text{cpx}}\right)$$

Where:
- $S_{\text{sec}}$: Security vulnerability penalty ($\text{Critical} \times 25 + \text{High} \times 12 + \text{Medium} \times 5$)
- $S_{\text{qual}}$: Code smell & Maintainability Index deficit ($(100 - \text{Avg MI}) \times 0.6 + \text{Smells} \times 3.5$)
- $S_{\text{bug}}$: Potential runtime bugs penalty ($\text{Critical} \times 25 + \text{High} \times 10 + \text{Medium} \times 4$)
- $S_{\text{cpx}}$: Complexity penalty based on proportion of modules with Cyclomatic Complexity $> 10$

**Remediation Effort Calculation**:
$$\text{Remediation Hours} = (\text{Critical} \times 4.0\text{h}) + (\text{High} \times 2.0\text{h}) + (\text{Medium} \times 1.0\text{h}) + (\text{Low} \times 0.5\text{h}) + (\text{Complex Files} \times 1.5\text{h})$$

---

## 6. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0 (Async), `aiosqlite`, `asyncpg`, `psycopg2-binary`.
- **Code Analysis**: Python `ast`, `tokenize`, Bandit AST rules, McCabe Cyclomatic Complexity, Halstead Metrics, SEI Maintainability Index.
- **RAG & Vector Retrieval**: Curated Markdown KB, TF-IDF/BM25 Vector Index, Cosine Similarity Retriever.
- **AI Layer**: Abstract `BaseLLMProvider` supporting OpenAI, Google Gemini, Anthropic, Ollama, and local deterministic Heuristic AI.
- **Frontend**: React 18, Vite, Lucide Icons, Custom Responsive CSS Design System.
- **Infrastructure**: Docker, Docker Compose, PostgreSQL 16.
- **Testing**: `pytest`, `pytest-asyncio`, `httpx`.

---

## 7. Installation & Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd codeguard-ai
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**:
   ```bash
   cd ../frontend
   npm install
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

5. **Run the Application**:
   - Start the FastAPI Backend:
     ```bash
     cd backend
     python -m uvicorn app.main:app --reload --port 8000
     ```
   - Start the React Frontend:
     ```bash
     cd frontend
     npm run dev
     ```
   - Access the dashboard at `http://localhost:5173` and API docs at `http://localhost:8000/docs`.

---

## 8. Docker Deployment

To run the full stack with PostgreSQL via Docker Compose:
```bash
docker-compose up --build
```
This starts:
- PostgreSQL on port `5432`
- CodeGuard AI unified container (Backend API + Built Frontend) on port `8000`.

---

## 9. Running Tests

Run the automated pytest test suite:
```bash
python -m pytest backend/tests -v
```
All 15 test suites validate AST parsing, complexity metrics, Bandit security scanning, RAG retrieval, agent coordination, debt formulas, and REST API endpoints.

---

## 10. Project Structure

```
codeguard-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes & /health endpoint
│   │   ├── core/         # Settings & structured logging
│   │   ├── database/     # SQLAlchemy models & async session
│   │   ├── schemas/      # Pydantic v2 schemas
│   │   ├── analyzers/    # AST parser, metrics, Bandit scanner, file filter
│   │   ├── rag/          # KB loader, vector index, retriever
│   │   ├── agents/       # Quality, Security, Bug, Debt agents & Review Coordinator
│   │   ├── services/     # Ingestion & analysis orchestrator
│   │   └── main.py       # Application entry point
│   ├── tests/            # Pytest test suite & evaluation fixtures
│   └── requirements.txt
│
├── frontend/
│   ├── src/              # React components & CSS design system
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── data/
│   └── knowledge/        # Markdown software engineering standards
│
├── docs/                 # Architecture, Milestones, and API reference
├── README.md
├── AI_USAGE.md
├── DECISION_LOG.md
├── DEBUGGING_REPORT.md
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

---

## 11. Codenixia 10 Milestones Summary

CodeGuard AI demonstrates complete end-to-end execution of all 10 Milestones:
- **Milestone 1**: Problem Discovery & Hybrid AI Solution Design
- **Milestone 2**: Software Engineering & Security Knowledge Strategy
- **Milestone 3**: Python Processing Pipeline & AST Parsing
- **Milestone 4**: Complexity Metrics (McCabe, Halstead, Maintainability Index)
- **Milestone 5**: Intelligence Layer & Multi-Provider LLM Abstraction
- **Milestone 6**: Evidence-Backed RAG Knowledge Retrieval
- **Milestone 7**: Multi-Agent Swarm with Review Coordinator
- **Milestone 8**: FastAPI REST API & Modern React Dashboard
- **Milestone 9**: Docker & Docker Compose Infrastructure
- **Milestone 10**: Testing, Health Monitoring, and Comprehensive Engineering Logs

---

## 12. Security & Safe Execution Notice
CodeGuard AI executes **zero untrusted repository code**. All files are analyzed purely via static Abstract Syntax Trees, tokenization, and pattern matching inside sandboxed temporary directories that are automatically removed after analysis.
