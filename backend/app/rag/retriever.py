from typing import List, Dict, Any, Optional
from app.rag.kb_loader import load_knowledge_base, KnowledgeChunk
from app.rag.embeddings import SimpleVectorIndex
from app.core.config import settings
from app.core.logging import logger


class KnowledgeRetriever:
    """
    RAG Retriever that maintains the indexed software engineering knowledge base
    and returns contextual citations for agent reasoning.
    """

    _instance: Optional["KnowledgeRetriever"] = None

    def __init__(self):
        self.index = SimpleVectorIndex()
        self.chunks: List[KnowledgeChunk] = []
        self._is_initialized = False

    @classmethod
    def get_instance(cls) -> "KnowledgeRetriever":
        if cls._instance is None:
            cls._instance = KnowledgeRetriever()
            cls._instance.initialize()
        return cls._instance

    def initialize(self, kb_dir: Optional[str] = None) -> None:
        try:
            self.chunks = load_knowledge_base(kb_dir)
            docs = [c.to_dict() for c in self.chunks]
            self.index.fit_and_index(docs)
            self._is_initialized = True
            logger.info(f"KnowledgeRetriever initialized with {len(docs)} document chunks.")
        except Exception as e:
            logger.error(f"Failed to initialize KnowledgeRetriever: {e}")
            self._is_initialized = False

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        if not self._is_initialized:
            self.initialize()

        k = top_k or settings.RAG_TOP_K
        results = self.index.query(query, top_k=k)
        return results

    def get_context_str(self, query: str, top_k: Optional[int] = None) -> str:
        """
        Formats retrieved knowledge into a clean Markdown citation block for LLM prompts.
        """
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return "No matching engineering standard found in knowledge base."

        formatted_lines = []
        for i, item in enumerate(results, 1):
            formatted_lines.append(
                f"### [Citation {i}] {item['title']} - {item['section']} (Source: {item['source_path']})\n"
                f"{item['content']}\n"
            )
        return "\n".join(formatted_lines)


retriever = KnowledgeRetriever.get_instance()
