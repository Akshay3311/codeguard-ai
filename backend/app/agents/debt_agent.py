from typing import List, Dict, Any
from app.schemas.finding import FindingBase
from app.core.config import settings
from app.core.logging import logger


class TechnicalDebtAgent:
    """
    Technical Debt Agent:
    Calculates a transparent, deterministic technical debt score (0-100) and
    estimated developer remediation effort (hours) based on measurable software signals.
    """

    def __init__(self):
        self.name = "technical_debt"
        self.role = "Lead Technical Debt & Remediation Strategist"

    def calculate_debt(
        self,
        findings: List[FindingBase],
        metrics: List[Dict[str, Any]],
        total_lines: int
    ) -> Dict[str, Any]:
        """
        Computes the technical debt score, score breakdowns, and remediation effort.
        """
        # 1. Count findings by severity and category
        sec_critical = sum(1 for f in findings if f.category == "security" and f.severity == "critical")
        sec_high = sum(1 for f in findings if f.category == "security" and f.severity == "high")
        sec_med = sum(1 for f in findings if f.category == "security" and f.severity == "medium")
        sec_low = sum(1 for f in findings if f.category == "security" and f.severity in ("low", "info"))

        bug_critical = sum(1 for f in findings if f.category == "bug" and f.severity == "critical")
        bug_high = sum(1 for f in findings if f.category == "bug" and f.severity == "high")
        bug_med = sum(1 for f in findings if f.category == "bug" and f.severity == "medium")
        bug_low = sum(1 for f in findings if f.category == "bug" and f.severity in ("low", "info"))

        qual_findings = [f for f in findings if f.category == "quality"]

        # 2. Metric aggregates
        file_count = max(1, len(metrics))
        avg_mi = sum(m.get("maintainability_index", 100) for m in metrics) / file_count
        avg_cc = sum(m.get("cyclomatic_complexity", 1) for m in metrics) / file_count
        high_cc_files = sum(1 for m in metrics if m.get("cyclomatic_complexity", 1) > 10)

        # 3. Sub-scores calculation (0 to 100 scale each)
        # Security penalty: heavily penalized because vulnerabilities present immediate risk
        raw_sec_penalty = (sec_critical * 25.0) + (sec_high * 12.0) + (sec_med * 5.0) + (sec_low * 1.5)
        sec_debt_score = min(100.0, raw_sec_penalty)
        security_health_score = max(0.0, 100.0 - sec_debt_score)

        # Quality penalty: based on MI deficit + number of quality smells
        mi_deficit = max(0.0, 100.0 - avg_mi)
        raw_qual_penalty = (mi_deficit * 0.6) + (len(qual_findings) * 3.5)
        qual_debt_score = min(100.0, raw_qual_penalty)
        quality_health_score = max(0.0, 100.0 - qual_debt_score)

        # Bug risk penalty
        raw_bug_penalty = (bug_critical * 25.0) + (bug_high * 10.0) + (bug_med * 4.0) + (bug_low * 1.0)
        bug_debt_score = min(100.0, raw_bug_penalty)
        bug_health_score = max(0.0, 100.0 - bug_debt_score)

        # Complexity penalty
        raw_cpx_penalty = min(100.0, (high_cc_files / file_count) * 60.0 + max(0.0, avg_cc - 5.0) * 8.0)
        
        # 4. Overall Weighted Technical Debt Score (0 - 100, where 0 is clean, 100 is maximal debt)
        overall_debt_score = (
            (settings.WEIGHT_SECURITY * sec_debt_score) +
            (settings.WEIGHT_QUALITY * qual_debt_score) +
            (settings.WEIGHT_BUGS * bug_debt_score) +
            (settings.WEIGHT_COMPLEXITY * raw_cpx_penalty)
        )
        overall_debt_score = round(min(100.0, max(0.0, overall_debt_score)), 1)

        # Overall repository health score (0 - 100, where 100 is cleanest)
        overall_health_score = round(max(0.0, 100.0 - overall_debt_score), 1)

        # 5. Developer Remediation Effort Estimation (in hours)
        # Benchmarks: Critical = 4h, High = 2h, Medium = 1h, Low = 0.5h, Complex file refactor = 1.5h
        critical_count = sec_critical + bug_critical + sum(1 for f in qual_findings if f.severity == "critical")
        high_count = sec_high + bug_high + sum(1 for f in qual_findings if f.severity == "high")
        med_count = sec_med + bug_med + sum(1 for f in qual_findings if f.severity == "medium")
        low_count = sec_low + bug_low + sum(1 for f in qual_findings if f.severity in ("low", "info"))

        remediation_hours = (
            (critical_count * 4.0) +
            (high_count * 2.0) +
            (med_count * 1.0) +
            (low_count * 0.5) +
            (high_cc_files * 1.5)
        )
        remediation_hours = round(remediation_hours, 1)

        return {
            "overall_debt_score": overall_debt_score,
            "overall_health_score": overall_health_score,
            "security_score": round(security_health_score, 1),
            "quality_score": round(quality_health_score, 1),
            "bugs_score": round(bug_health_score, 1),
            "remediation_hours": remediation_hours,
            "breakdown": {
                "security_debt": round(sec_debt_score, 1),
                "quality_debt": round(qual_debt_score, 1),
                "bug_debt": round(bug_debt_score, 1),
                "complexity_debt": round(raw_cpx_penalty, 1),
                "avg_maintainability_index": round(avg_mi, 1),
                "avg_cyclomatic_complexity": round(avg_cc, 1),
                "high_complexity_files": high_cc_files,
                "critical_issues_count": critical_count,
                "high_issues_count": high_count,
                "medium_issues_count": med_count,
                "low_issues_count": low_count
            }
        }
