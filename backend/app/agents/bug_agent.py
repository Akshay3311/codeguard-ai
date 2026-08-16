import json
from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.schemas.finding import FindingBase


class BugDetectionAgent(BaseAgent):
    """
    Bug Detection Agent: Analyzes potential logical bugs, edge cases,
    unhandled None values, swallowed exceptions, resource leaks, and type mismatches.
    """

    def __init__(self):
        super().__init__(name="bug_detection", role="Staff Software Reliability & Bug Triage Specialist")

    def get_system_prompt(self) -> str:
        return """You are the Bug Detection Agent for CodeGuard AI.
Your objective is to identify potential runtime errors, edge-case bugs, unhandled exceptions, resource leaks, and race conditions.

STRICT RULES:
1. Label potential issues clearly without claiming certainty unless backed by unambiguous evidence.
2. Ground advice in python exception handling standards.
3. Return only valid JSON conforming to this schema:
{
  "summary": "<Overall summary of runtime reliability risks>",
  "agent_findings": [
    {
      "category": "bug",
      "severity": "critical" | "high" | "medium" | "low" | "info",
      "file": "<relative file path>",
      "line": <int>,
      "end_line": <int>,
      "title": "<Concise bug title>",
      "description": "<Description of how this bug might trigger in production>",
      "evidence": "<Code snippet>",
      "confidence": <float 0.0-1.0>,
      "recommendation": "<How to fix or safeguard against the bug>",
      "technical_debt_impact": <int 1-10>,
      "rag_source": "<referenced knowledge citation>"
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
        bug_static = [
            f.model_dump() for f in static_findings if f.category == "bug"
        ]

        files_summary = [
            {
                "file": f["file_path"],
                "sample_code": f["content"][:2500] if "content" in f else ""
            }
            for f in files_data[:10]
        ]

        return f"""### RAG ERROR HANDLING STANDARDS:
{rag_context}

### REPOSITORY CODE CONTEXT:
{json.dumps(files_summary, indent=2)}

### AST & DETERMINISTIC BUG FINDINGS:
{json.dumps(bug_static, indent=2)}

Please evaluate potential logical bugs, unhandled exceptions, and edge cases, and output the required JSON.
"""
