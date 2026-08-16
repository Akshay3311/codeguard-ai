import sys
from pathlib import Path
import pytest
import pytest_asyncio

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.session import init_db
from app.rag.retriever import retriever


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db_and_rag():
    await init_db()
    retriever.initialize()
    yield
