import pytest
from app.rag.kb_loader import load_knowledge_base
from app.rag.embeddings import SimpleVectorIndex
from app.rag.retriever import KnowledgeRetriever


def test_knowledge_base_loading():
    chunks = load_knowledge_base()
    assert len(chunks) > 0
    # Verify metadata fields
    for c in chunks:
        assert c.doc_id
        assert c.title
        assert c.section
        assert len(c.content) > 0


def test_vector_similarity_retrieval():
    retriever = KnowledgeRetriever()
    retriever.initialize()
    
    # Query for SQL injection
    sql_results = retriever.retrieve("SQL injection parameter binding", top_k=2)
    assert len(sql_results) > 0
    assert any("SQL Injection" in r["section"] or "SQL" in r["content"] for r in sql_results)

    # Query for function length / clean code
    func_results = retriever.retrieve("function length single responsibility", top_k=2)
    assert len(func_results) > 0
    assert any("Function" in r["section"] or "Clean" in r["title"] for r in func_results)


def test_context_string_formatting():
    retriever = KnowledgeRetriever()
    retriever.initialize()
    
    context = retriever.get_context_str("pickle deserialization security", top_k=1)
    assert "### [Citation 1]" in context
    assert "Source:" in context
