import os
from typing import List, Dict, Any
from pathlib import Path
from app.core.config import settings
from app.core.logging import logger


class KnowledgeChunk:
    def __init__(self, doc_id: str, title: str, section: str, content: str, source_path: str):
        self.doc_id = doc_id
        self.title = title
        self.section = section
        self.content = content
        self.source_path = source_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "section": self.section,
            "content": self.content,
            "source_path": self.source_path
        }


def load_knowledge_base(kb_dir: str = None) -> List[KnowledgeChunk]:
    """
    Loads all markdown knowledge documents, chunks them by markdown headings,
    and attaches source metadata.
    """
    if kb_dir is None:
        kb_dir = settings.KNOWLEDGE_BASE_DIR

    kb_path = Path(kb_dir).resolve()
    chunks: List[KnowledgeChunk] = []

    if not kb_path.exists():
        logger.warning(f"Knowledge base directory does not exist: {kb_path}")
        return chunks

    for md_file in kb_path.glob("*.md"):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                raw_text = f.read()

            lines = raw_text.splitlines()
            current_title = md_file.stem.replace("_", " ").title()
            current_section = "General"
            current_buffer = []

            for line in lines:
                if line.startswith("# "):
                    current_title = line[2:].strip()
                elif line.startswith("## "):
                    # Save previous section if not empty
                    if current_buffer:
                        content = "\n".join(current_buffer).strip()
                        if content:
                            chunk_id = f"{md_file.name}#{current_section.lower().replace(' ', '-')}"
                            chunks.append(KnowledgeChunk(
                                doc_id=chunk_id,
                                title=current_title,
                                section=current_section,
                                content=content,
                                source_path=md_file.name
                            ))
                        current_buffer = []
                    current_section = line[3:].strip()
                else:
                    current_buffer.append(line)

            # Flush last buffer
            if current_buffer:
                content = "\n".join(current_buffer).strip()
                if content:
                    chunk_id = f"{md_file.name}#{current_section.lower().replace(' ', '-')}"
                    chunks.append(KnowledgeChunk(
                        doc_id=chunk_id,
                        title=current_title,
                        section=current_section,
                        content=content,
                        source_path=md_file.name
                    ))

        except Exception as e:
            logger.error(f"Error loading knowledge doc {md_file}: {e}")

    logger.info(f"Loaded {len(chunks)} knowledge chunks from {kb_path}")
    return chunks
