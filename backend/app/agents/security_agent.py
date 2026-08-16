import json
from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.schemas.finding import FindingBase


class SecurityAgent(BaseAgent):
    """
    Security Agent: Focuses on OWASP Top 10 vulnerabilities, injection flaws,
    hardcoded secrets, insecure deserialization, dangerous functions, and authentication risks.
    """

    def __init__(self):
        super().__init__(name="security", role="Principal Application Security Engineer")

    def get_system_prompt(self) -> str:
        return """You are the Security Agent for CodeGuard AI.
Your objective is to evaluate Python code for critical security vulnerabilities, OWASP Top 10 risks, injection attacks, hardcoded credentials, and unsafe third-party library invocations.

STRICT RULES:
1. Ground your recommendations in the provided OWASP & secure coding RAG context.
2. Return only valid JSON conforming to this schema:
{
  "summary": "<Overall executive summary of security posture and vulnerability surface>",
  "agent_findings": [
    {
      "category": "security",
      "severity": "critical" | "high" | "medium" | "low" | "info",
      "file": "<relative file path>",
      "line": <int>,
      "end_line": <int>,
      "title": "<Concise vulnerability title>",
      "description": "<Detailed exploit scenario and impact>",
      "evidence": "<Code snippet>",
      "confidence": <float 0.0-1.0>,
      "recommendation": "<Remediation steps>",
      "technical_debt_impact": <int 1-10>,
      "rag_source": "<referenced security knowledge citation>"
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
        security_static = [
            f.model_dump() for f in static_findings if f.category == "security"
        ]

        files_summary = [
            {
                "file": f["file_path"],
                "sample_code": f["content"][:2500] if "content" in f else ""
            }
            for f in files_data[:10]
        ]

        return f"""### RAG SECURITY GUIDELINES:
{rag_context}

### REPOSITORY CODE CONTEXT:
{json.dumps(files_summary, indent=2)}

### DETERMINISTIC SECURITY FINDINGS (BANDIT & AST):
{json.dumps(security_static, indent=2)}

Please analyze the code for security risks, validate deterministic findings, provide contextual explanation for each issue, and output the required JSON.
"""
