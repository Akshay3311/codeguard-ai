import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "CodeGuard AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development")

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./codeguard.db",
        description="Async database connection string. Can be PostgreSQL or SQLite."
    )
    SYNC_DATABASE_URL: str = Field(
        default="sqlite:///./codeguard.db",
        description="Synchronous database connection string for migrations or sync tools."
    )

    # Storage & Temporary Directories
    STORAGE_DIR: str = Field(
        default="./storage",
        description="Directory for temporary repository clones and file cache."
    )
    MAX_REPO_SIZE_MB: int = Field(default=50, description="Max repo size in MB to clone")
    MAX_FILE_SIZE_KB: int = Field(default=500, description="Max single file size in KB")
    MAX_FILES_TO_ANALYZE: int = Field(default=100, description="Max python files per analysis run")

    # AI / LLM Configuration
    LLM_PROVIDER: str = Field(
        default="heuristic",
        description="Provider to use: 'heuristic', 'gemini', 'openai', 'anthropic', 'ollama'"
    )
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    GEMINI_API_KEY: Optional[str] = Field(default=None)
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None)
    ANTHROPIC_MODEL: str = Field(default="claude-3-5-sonnet-20241022")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="llama3")

    # RAG / Knowledge Base
    KNOWLEDGE_BASE_DIR: str = Field(
        default="./data/knowledge",
        description="Path to knowledge base markdown files"
    )
    RAG_TOP_K: int = Field(default=3, description="Number of knowledge chunks to retrieve per agent query")

    # Technical Debt Scoring Weights
    WEIGHT_SECURITY: float = Field(default=0.35, description="Weight for security issues in debt calculation")
    WEIGHT_QUALITY: float = Field(default=0.25, description="Weight for code quality & smells")
    WEIGHT_BUGS: float = Field(default=0.20, description="Weight for potential bugs")
    WEIGHT_COMPLEXITY: float = Field(default=0.15, description="Weight for cyclomatic complexity")
    WEIGHT_DUPLICATION: float = Field(default=0.05, description="Weight for duplicate logic")

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173", "*"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
