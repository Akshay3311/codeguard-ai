import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.schemas.finding import FindingBase
from app.agents.llm_provider import BaseLLMProvider, get_llm_provider
from app.rag.retriever import retriever
from app.core.logging import logger


class BaseAgent(ABC):
    """
    Abstract base class for all specialized CodeGuard AI agents.
    Provides structured prompt construction, RAG knowledge injection,
    and Pydantic output validation.
    """

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.provider: BaseLLMProvider = get_llm_provider()

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Returns the specialized system prompt defining the agent's persona and rules."""
        pass

    @abstractmethod
    def build_user_prompt(
        self,
        files_data: List[Dict[str, Any]],
        static_findings: List[FindingBase],
        metrics: List[Dict[str, Any]],
        rag_context: str
    ) -> str:
        """Constructs the prompt containing source code context, static results, and RAG citations."""
        pass

    async def analyze(
        self,
        files_data: List[Dict[str, Any]],
        static_findings: List[FindingBase],
        metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executes the agent workflow:
        1. Query RAG for domain-specific engineering standards
        2. Format structured prompts
        3. Call LLM provider
        4. Validate and return structured findings
        """
        try:
            # 1. RAG Retrieval for this agent's domain
            rag_query = f"{self.name} {self.role} python code best practices standards"
            rag_context = retriever.get_context_str(rag_query, top_k=2)

            system_prompt = self.get_system_prompt()
            user_prompt = self.build_user_prompt(files_data, static_findings, metrics, rag_context)

            # 2. Call LLM
            llm_response = await self.provider.generate_json(system_prompt, user_prompt)
            
            # 3. Parse and validate findings
            raw_findings = llm_response.get("agent_findings", [])
            valid_findings: List[FindingBase] = []

            for item in raw_findings:
                try:
                    # Validate against Pydantic schema
                    f = FindingBase(
                        category=item.get("category", "quality"),
                        severity=item.get("severity", "medium"),
                        file=item.get("file", "unknown.py"),
                        line=item.get("line"),
                        end_line=item.get("end_line"),
                        title=item.get("title", "Detected Issue"),
                        description=item.get("description", ""),
                        evidence=item.get("evidence"),
                        source=f"{self.name}_agent",
                        confidence=float(item.get("confidence", 0.85)),
                        recommendation=item.get("recommendation", ""),
                        technical_debt_impact=int(item.get("technical_debt_impact", 3)),
                        rag_source=item.get("rag_source")
                    )
                    valid_findings.append(f)
                except Exception as ve:
                    logger.warning(f"Skipping malformed agent finding from {self.name}: {ve}")

            summary = llm_response.get("summary", f"{self.name} analysis complete.")

            return {
                "agent_name": self.name,
                "status": "success",
                "summary": summary,
                "findings": valid_findings,
                "raw_response": llm_response
            }

        except Exception as e:
            logger.error(f"Agent {self.name} failed: {e}", exc_info=True)
            return {
                "agent_name": self.name,
                "status": "fallback",
                "summary": f"Agent {self.name} experienced an error; falling back to deterministic findings.",
                "findings": [],
                "error": str(e)
            }
