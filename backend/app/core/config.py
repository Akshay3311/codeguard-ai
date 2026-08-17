from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================
# PROJECT PATHS
# ============================================================

# Project structure:
#
# codeguard-ai/
# ├── backend/
# │   └── app/
# │       └── core/
# │           └── config.py
# ├── data/
# │   └── knowledge/
# ├── frontend/
# └── ...
#
# parents[0] = core
# parents[1] = app
# parents[2] = backend
# parents[3] = codeguard-ai

PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ============================================================
# DEFAULT DIRECTORIES
# ============================================================

DEFAULT_KNOWLEDGE_BASE_DIR = (
    PROJECT_ROOT / "data" / "knowledge"
)

DEFAULT_STORAGE_DIR = (
    PROJECT_ROOT / "storage"
)


# ============================================================
# SETTINGS
# ============================================================

class Settings(BaseSettings):

    # ========================================================
    # APPLICATION
    # ========================================================

    PROJECT_NAME: str = Field(
        default="CodeGuard AI",
        description="Application name"
    )

    VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )

    API_V1_STR: str = Field(
        default="/api/v1",
        description="API version prefix"
    )

    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment"
    )


    # ========================================================
    # DATABASE
    # ========================================================

    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./codeguard.db",
        description=(
            "Async database connection string. "
            "Can be PostgreSQL or SQLite."
        )
    )

    SYNC_DATABASE_URL: str = Field(
        default="sqlite:///./codeguard.db",
        description=(
            "Synchronous database connection string "
            "for migrations or synchronous tools."
        )
    )


    # ========================================================
    # STORAGE & TEMPORARY DIRECTORIES
    # ========================================================

    STORAGE_DIR: str = Field(
        default=str(DEFAULT_STORAGE_DIR),
        description=(
            "Directory for temporary repository clones "
            "and file cache."
        )
    )

    MAX_REPO_SIZE_MB: int = Field(
        default=50,
        description="Maximum repository size in MB"
    )

    MAX_FILE_SIZE_KB: int = Field(
        default=500,
        description="Maximum individual file size in KB"
    )

    MAX_FILES_TO_ANALYZE: int = Field(
        default=100,
        description="Maximum Python files to analyze per run"
    )


    # ========================================================
    # AI / LLM CONFIGURATION
    # ========================================================

    LLM_PROVIDER: str = Field(
        default="heuristic",
        description=(
            "LLM provider: heuristic, gemini, openai, "
            "anthropic, or ollama"
        )
    )


    # --------------------------------------------------------
    # OpenAI
    # --------------------------------------------------------

    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )

    OPENAI_MODEL: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model name"
    )


    # --------------------------------------------------------
    # Google Gemini
    # --------------------------------------------------------

    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API key"
    )

    GEMINI_MODEL: str = Field(
        default="gemini-1.5-flash",
        description="Google Gemini model name"
    )


    # --------------------------------------------------------
    # Anthropic
    # --------------------------------------------------------

    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )

    ANTHROPIC_MODEL: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Anthropic model name"
    )


    # --------------------------------------------------------
    # Ollama
    # --------------------------------------------------------

    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL"
    )

    OLLAMA_MODEL: str = Field(
        default="llama3",
        description="Ollama model name"
    )


    # ========================================================
    # RAG / KNOWLEDGE BASE
    # ========================================================

    KNOWLEDGE_BASE_DIR: str = Field(
        default=str(DEFAULT_KNOWLEDGE_BASE_DIR),
        description=(
            "Absolute path to the project-level "
            "data/knowledge directory."
        )
    )

    RAG_TOP_K: int = Field(
        default=3,
        description=(
            "Number of knowledge chunks retrieved "
            "per agent query."
        )
    )


    # ========================================================
    # TECHNICAL DEBT SCORING WEIGHTS
    # ========================================================

    WEIGHT_SECURITY: float = Field(
        default=0.35,
        description="Weight for security issues"
    )

    WEIGHT_QUALITY: float = Field(
        default=0.25,
        description="Weight for code quality and code smells"
    )

    WEIGHT_BUGS: float = Field(
        default=0.20,
        description="Weight for potential bugs"
    )

    WEIGHT_COMPLEXITY: float = Field(
        default=0.15,
        description="Weight for cyclomatic complexity"
    )

    WEIGHT_DUPLICATION: float = Field(
        default=0.05,
        description="Weight for duplicate logic"
    )


    # ========================================================
    # CORS
    # ========================================================

    CORS_ORIGINS: List[str] = Field(
        default=[
            # Local development
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",

            # Production frontend
            "https://codeguard-ai-silk.vercel.app",
        ],
        description="Allowed frontend origins"
    )


    # ========================================================
    # PYDANTIC SETTINGS
    # ========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# ============================================================
# GLOBAL SETTINGS INSTANCE
# ============================================================

settings = Settings()
