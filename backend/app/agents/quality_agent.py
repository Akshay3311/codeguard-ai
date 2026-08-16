import json
from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.schemas.finding import FindingBase


class QualityAgent(BaseAgent):
    """
    Code Quality Agent: Analyzes code smells, architectural maintainability,
    naming conventions, function length, parameter counts, and duplicate logic.
    """

    def __init__(self):
        super().__init__(name="quality", role="Senior Software Quality & Refactoring Architect")

    def get_system_prompt(self) -> str:
        return """You are the Code Quality Agent for CodeGuard AI.
Your objective is to review Python code for structural code smells, maintainability issues, clean code violations (PEP 8, SOLID), and refactoring opportunities.

STRICT RULES:
1. Ground your recommendations in the provided RAG knowledge context.
2. Return only valid JSON conforming to this schema:
{
  "summary": "<Overall summary of code quality and maintainability>",
  "agent_findings": [
    {
      "category": "quality",
      "severity": "critical" | "high" | "medium" | "low" | "info",
      "file": "<relative file path>",
      "line": <int>,
      "end_line": <int>,
      "title": "<Concise issue title>",
      "description": "<Detailed explanation of the code smell>",
      "evidence": "<Code snippet>",
      "confidence": <float 0.0-1.0>,
      "recommendation": "<Actionable refactoring advice>",
      "technical_debt_impact": <int 1-10>,
      "rag_source": "<referenced knowledge file or rule>"
    }
  ]
}
"""

    def build_user_prompt(
        self,
        files_data: List[Dict[str, Any]],
        static_findings: List[FindingBase],
        metrics: List[Dict[str, Any]],
        rag_context: str
    ) -> str:
        # Filter static findings relevant to quality
        quality_static = [
            f.model_dump() for f in static_findings if f.category == "quality"
        ]

        files_summary = [
            {
                "file": f["file_path"],
                "loc": f["loc"],
                "cyclomatic_complexity": f.get("cyclomatic_complexity", 1),
                "maintainability_index": f.get("maintainability_index", 100),
                "sample_code": f["content"][:2000] if "content" in f else ""
            }
            for f in files_data[:10]  # limit to first 10 files to control token budget
        ]

        return f"""### RAG KNOWLEDGE STANDARDS:
{rag_context}

### REPOSITORY CODE & METRICS CONTEXT:
{json.dumps(files_summary, indent=2)}

### DETERMINISTIC STATIC ANALYSIS FINDINGS:
{json.dumps(quality_static, indent=2)}

Please analyze the repository files, explain high-impact quality/maintainability problems, prioritize them, and output the required JSON.
"""
