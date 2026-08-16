# Technical Architecture: CodeGuard AI

## 1. System Overview
CodeGuard AI is an automated code review and technical debt analyzer designed for Python repositories. It combines deterministic static AST analysis, software engineering complexity metrics, RAG knowledge retrieval, and a specialized multi-agent swarm coordinated by an executive Review Coordinator.

```mermaid
flowchart TD
    subgraph Client
        Browser[React + Vite Web Dashboard]
    end

    subgraph API Layer
        FastAPI[FastAPI REST API /api/v1]
        Health[Health Endpoint /health]
    end

    subgraph Core Processing Pipeline
        RepoService[Repo Ingestor & Sandbox]
        FileFilter[File Discovery & Filter]
        ASTEngine[Python AST Visitor]
        MetricsEngine[McCabe & Halstead Calculator]
        BanditScanner[Deterministic Security Scanner]
    end

    subgraph RAG Knowledge System
        KB[(Markdown Knowledge Base)]
        VectorIndex[Vector Index & Retriever]
    end

    subgraph Specialized Multi-Agent Swarm
        QualityAgent[Code Quality Agent]
        SecurityAgent[Security Agent]
        BugAgent[Bug Detection Agent]
        DebtAgent[Technical Debt Agent]
        Coordinator[Review Coordinator]
    end

    subgraph Persistence Layer
        DB[(PostgreSQL / SQLite Database)]
    end

    Browser -->|HTTP REST| FastAPI
    FastAPI -->|Background Task| RepoService
    RepoService --> FileFilter
    FileFilter --> ASTEngine & MetricsEngine & BanditScanner
    
    KB --> VectorIndex
    VectorIndex --> QualityAgent & SecurityAgent & BugAgent
    
    ASTEngine & MetricsEngine & BanditScanner --> QualityAgent & SecurityAgent & BugAgent
    QualityAgent & SecurityAgent & BugAgent --> DebtAgent
    DebtAgent --> Coordinator
    Coordinator --> DB
    DB --> FastAPI
```

## 2. Multi-Agent Swarm Responsibilities
1. **Code Quality Agent**: Analyzes code smells, function length, parameter counts, naming conventions (PEP 8), and maintainability deficits.
2. **Security Agent**: Evaluates OWASP Top 10 vulnerabilities, command injection (`shell=True`), raw SQL queries, unsafe `eval`/`exec`, insecure deserialization (`pickle`), and hardcoded secrets.
3. **Bug Detection Agent**: Detects potential runtime bugs, mutable default arguments, swallowed exceptions (`except: pass`), resource leaks, and unhandled `None` risks.
4. **Technical Debt Agent**: Calculates the transparent mathematical technical debt score (0-100) and estimated developer remediation hours based on measurable signals.
5. **Review Coordinator**: Merges findings from all agents and deterministic tools, deduplicates overlapping issues, assigns priorities, and generates the executive report.
