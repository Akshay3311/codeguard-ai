from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database.session import get_db
from app.rag.retriever import retriever
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint verifying:
    - Service uptime
    - Database connection
    - RAG Knowledge Base readiness
    - Configured LLM provider
    """
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    rag_status = "ready" if retriever._is_initialized else "initializing"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "rag_knowledge_base": {
            "status": rag_status,
            "chunks_loaded": len(retriever.chunks)
        },
        "llm_provider": settings.LLM_PROVIDER
    }
