from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.database.session import init_db
from app.rag.retriever import retriever

from app.api.health import router as health_router
from app.api.routes import router as api_router


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application lifecycle.
    Initializes database and RAG knowledge base at startup.
    """

    logger.info(
        f"Starting {settings.PROJECT_NAME} "
        f"v{settings.VERSION}..."
    )

    # --------------------------------------------------------
    # Initialize database
    # --------------------------------------------------------

    try:
        await init_db()
        logger.info(
            "Database tables verified/created successfully."
        )
    except Exception as exc:
        logger.exception(
            f"Database initialization failed: {exc}"
        )
        raise

    # --------------------------------------------------------
    # Initialize RAG knowledge retriever
    # --------------------------------------------------------

    try:
        retriever.initialize()

        logger.info(
            "Knowledge retriever initialized successfully."
        )

    except Exception as exc:
        logger.exception(
            f"RAG knowledge initialization failed: {exc}"
        )

        # Do not necessarily stop the complete API if
        # knowledge initialization fails.
        # The application can still serve non-RAG endpoints.

    logger.info("Application startup completed.")

    yield

    # --------------------------------------------------------
    # Shutdown
    # --------------------------------------------------------

    logger.info("Shutting down application...")


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Multi-Agent AI Code Review & Technical Debt "
        "Analyzer with deterministic static analysis, "
        "RAG, and review coordination."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=settings.CORS_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(health_router)

app.include_router(api_router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
        "api": f"{settings.API_V1_STR}/analyze",
    }


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
