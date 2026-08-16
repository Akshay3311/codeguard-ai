from typing import List, Dict, Any, Tuple
from app.schemas.finding import FindingBase
from app.schemas.analysis import RecommendationResponse
from app.agents.debt_agent import TechnicalDebtAgent
from app.agents.llm_provider import get_llm_provider
from app.core.logging import logger


class ReviewCoordinator:
    """
    Review Coordinator:
    Orchestrates the multi-agent outputs, normalizes findings, deduplicates overlapping issues,
    assigns priorities, and compiles the final comprehensive review report.
    """

    def __init__(self):
        self.debt_agent = TechnicalDebtAgent()
        self.provider = get_llm_provider()

    def deduplicate_findings(self, raw_findings: List[FindingBase]) -> List[FindingBase]:
        """
        Deduplicates findings based on (file, line_bucket, category).
        When duplicates occur between deterministic tools and LLM agents, merges evidence
        and retains the highest confidence and most specific recommendation.
        """
        seen_keys: Dict[Tuple, FindingBase] = {}

        for f in raw_findings:
            # Line bucket (within 3 lines)
            line_bucket = (f.line // 3) if f.line is not None else 0
            key = (f.file, line_bucket, f.category)

            if key in seen_keys:
                existing = seen_keys[key]
                # Prefer more detailed recommendation or higher confidence
                if f.confidence > existing.confidence or (f.rag_source and not existing.rag_source):
                    seen_keys[key] = f
            else:
                seen_keys[key] = f

        deduped = list(seen_keys.values())
        
        # Sort by severity priority: critical -> high -> medium -> low -> info
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        deduped.sort(key=lambda x: severity_order.get(x.severity, 5))
        
        logger.info(f"Deduplication reduced {len(raw_findings)} raw findings to {len(deduped)} unique issues.")
        return deduped

    def generate_recommendations(
        self,
        findings: List[FindingBase],
        debt_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes prioritized actionable recommendations and remediation roadmap.
        """
        recommendations = []
        priority = 1

        # 1. Security roadmap item if critical/high security issues exist
        sec_issues = [f for f in findings if f.category == "security"]
        if sec_issues:
            critical_sec = [f for f in sec_issues if f.severity in ("critical", "high")]
            action_items = [f"Fix {f.title} in '{f.file}' (line {f.line or 'N/A'})" for f in sec_issues[:5]]
            recommendations.append({
                "id": f"rec-{priority}",
                "priority": priority,
                "title": "Remediate High-Risk Security Vulnerabilities",
                "category": "security",
                "action_items": action_items,
                "estimated_effort_hours": round(len(critical_sec) * 3.0 + len(sec_issues) * 0.5, 1),
                "rationale": "Security flaws present immediate compliance and exploit risks. These should be patched before release."
            })
            priority += 1

        # 2. Reliability & Bug Fixes
        bug_issues = [f for f in findings if f.category == "bug"]
        if bug_issues:
            action_items = [f"Resolve {f.title} in '{f.file}'" for f in bug_issues[:5]]
            recommendations.append({
                "id": f"rec-{priority}",
                "priority": priority,
                "title": "Harden Error Handling & Fix Runtime Risks",
                "category": "bug",
                "action_items": action_items,
                "estimated_effort_hours": round(len(bug_issues) * 1.5, 1),
                "rationale": "Unhandled exceptions and swallowed errors lead to silent failures and state corruption."
            })
            priority += 1

        # 3. Maintainability & Code Quality
        qual_issues = [f for f in findings if f.category == "quality"]
        if qual_issues or debt_results.get("breakdown", {}).get("high_complexity_files", 0) > 0:
            action_items = [f"Refactor {f.title} in '{f.file}'" for f in qual_issues[:5]]
            recommendations.append({
                "id": f"rec-{priority}",
                "priority": priority,
                "title": "Refactor High-Complexity Functions & Improve Maintainability",
                "category": "quality",
                "action_items": action_items or ["Modularize complex procedures and reduce cyclomatic complexity."],
                "estimated_effort_hours": round(len(qual_issues) * 1.0 + 2.0, 1),
                "rationale": "High cyclomatic complexity and long methods increase testing burden and regression risk."
            })
            priority += 1

        # 4. Clean Code Standards
        if not recommendations:
            recommendations.append({
                "id": "rec-1",
                "priority": 1,
                "title": "Maintain High Code Quality Standards",
                "category": "general",
                "action_items": ["Codebase exhibits high quality. Continue following PEP 8 and writing comprehensive unit tests."],
                "estimated_effort_hours": 0.0,
                "rationale": "No critical or high severity defects detected."
            })

        return recommendations

    async def coordinate(
        self,
        raw_findings: List[FindingBase],
        metrics: List[Dict[str, Any]],
        files_data: List[Dict[str, Any]],
        total_lines: int,
        agent_logs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinates the entire analysis results, computes technical debt, and prepares final report data.
        """
        # 1. Deduplicate findings
        deduped_findings = self.deduplicate_findings(raw_findings)

        # 2. Calculate deterministic technical debt
        debt_results = self.debt_agent.calculate_debt(deduped_findings, metrics, total_lines)

        # 3. Generate prioritized recommendations
        recommendations = self.generate_recommendations(deduped_findings, debt_results)

        # 4. Generate executive summary
        critical_count = sum(1 for f in deduped_findings if f.severity == "critical")
        high_count = sum(1 for f in deduped_findings if f.severity == "high")
        health = debt_results["overall_health_score"]

        if critical_count > 0:
            health_desc = f"CRITICAL ATTENTION REQUIRED: {critical_count} critical issues detected."
        elif high_count > 0:
            health_desc = f"MODERATE RISK: {high_count} high-priority issues require remediation."
        else:
            health_desc = "GOOD QUALITY: Codebase conforms to software engineering standards."

        summary = (
            f"CodeGuard AI analyzed {len(files_data)} Python files ({total_lines} lines of code). "
            f"Overall Code Health Score: {health}/100. Technical Debt Score: {debt_results['overall_debt_score']}/100. "
            f"{health_desc} Estimated total remediation effort is {debt_results['remediation_hours']} developer hours."
        )

        return {
            "findings": deduped_findings,
            "debt_results": debt_results,
            "recommendations": recommendations,
            "executive_summary": summary,
            "agent_logs": agent_logs
        }
