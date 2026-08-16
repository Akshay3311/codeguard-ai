import time
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.logging import logger
from app.database.models import AnalysisRun, Repository, Finding, TechnicalDebtMetric, Recommendation
from app.database.session import AsyncSessionLocal
from app.services.repo_service import RepoService
from app.analyzers.file_filter import discover_python_files
from app.analyzers.ast_visitor import analyze_code_ast
from app.analyzers.metrics import calculate_file_metrics
from app.analyzers.static_bandit import scan_file_security
from app.agents.quality_agent import QualityAgent
from app.agents.security_agent import SecurityAgent
from app.agents.bug_agent import BugDetectionAgent
from app.agents.coordinator import ReviewCoordinator
from app.schemas.finding import FindingBase


class AnalysisEngine:
    """
    Core orchestrator that runs the end-to-end analysis pipeline asynchronously.
    """

    def __init__(self):
        self.quality_agent = QualityAgent()
        self.security_agent = SecurityAgent()
        self.bug_agent = BugDetectionAgent()
        self.coordinator = ReviewCoordinator()

    async def _update_progress(
        self,
        analysis_id: str,
        status: str,
        progress: int,
        step_name: str,
        error_msg: str = None
    ) -> None:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
            run = result.scalar_one_or_none()
            if run:
                run.status = status
                run.progress_percentage = progress
                run.current_step = step_name
                if error_msg:
                    run.error_message = error_msg
                await session.commit()

    async def execute_analysis(self, analysis_id: str, repo_url: str, branch: str = "main") -> None:
        """
        Executes complete analysis workflow in the background.
        """
        start_time = time.time()
        temp_dir = None

        try:
            # Step 1: Initialize & Clone
            await self._update_progress(analysis_id, "cloning", 15, "Cloning repository...")
            temp_dir, commit_hash, active_branch, repo_name = RepoService.clone_repository(repo_url, branch)

            # Step 2: Discover and Filter Files
            await self._update_progress(analysis_id, "parsing", 30, "Discovering & filtering Python source files...")
            discovered_files, total_files_count, total_loc = discover_python_files(temp_dir)

            if total_files_count == 0:
                await self._update_progress(
                    analysis_id, "completed", 100, "Analysis complete (No Python files found)",
                    error_msg=None
                )
                async with AsyncSessionLocal() as session:
                    res = await session.execute(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
                    run = res.scalar_one_or_none()
                    if run:
                        run.status = "completed"
                        run.total_files = 0
                        run.total_lines = 0
                        run.health_score = 100.0
                        run.technical_debt_score = 0.0
                        run.executive_summary = "No Python files found in this repository to analyze."
                        run.completed_at = datetime.now(timezone.utc)
                        run.execution_time_seconds = round(time.time() - start_time, 2)
                        await session.commit()
                return

            # Step 3: AST Parsing & Metrics
            await self._update_progress(analysis_id, "analyzing", 50, "Parsing AST and calculating code complexity metrics...")
            files_data: List[Dict[str, Any]] = []
            static_findings: List[FindingBase] = []
            metrics_list: List[Dict[str, Any]] = []

            for rel_path in discovered_files:
                abs_path = Path(temp_dir) / rel_path
                try:
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()

                    # Calculate complexity metrics
                    m = calculate_file_metrics(rel_path, code)
                    metrics_list.append(m)

                    # AST code smell detection
                    ast_res = analyze_code_ast(rel_path, code)
                    static_findings.extend(ast_res["findings"])

                    # Static security scanning (Bandit AST)
                    sec_res = scan_file_security(rel_path, code)
                    static_findings.extend(sec_res)

                    files_data.append({
                        "file_path": rel_path,
                        "loc": m["loc"],
                        "sloc": m["sloc"],
                        "cyclomatic_complexity": m["cyclomatic_complexity"],
                        "maintainability_index": m["maintainability_index"],
                        "content": code
                    })
                except Exception as file_err:
                    logger.warning(f"Error analyzing file {rel_path}: {file_err}")

            # Step 4: RAG Retrieval & Multi-Agent Swarm
            await self._update_progress(analysis_id, "agent_evaluation", 75, "Running specialized AI agents (Quality, Security, Bug Detection)...")
            agent_logs: Dict[str, Any] = {}
            raw_agent_findings: List[FindingBase] = list(static_findings)

            # Run Quality Agent
            quality_res = await self.quality_agent.analyze(files_data, static_findings, metrics_list)
            agent_logs["quality_agent"] = quality_res.get("summary", "")
            raw_agent_findings.extend(quality_res.get("findings", []))

            # Run Security Agent
            security_res = await self.security_agent.analyze(files_data, static_findings, metrics_list)
            agent_logs["security_agent"] = security_res.get("summary", "")
            raw_agent_findings.extend(security_res.get("findings", []))

            # Run Bug Agent
            bug_res = await self.bug_agent.analyze(files_data, static_findings, metrics_list)
            agent_logs["bug_agent"] = bug_res.get("summary", "")
            raw_agent_findings.extend(bug_res.get("findings", []))

            # Step 5: Review Coordinator & Technical Debt Calculation
            await self._update_progress(analysis_id, "synthesizing", 90, "Review Coordinator deduplicating & computing technical debt...")
            coord_res = await self.coordinator.coordinate(
                raw_findings=raw_agent_findings,
                metrics=metrics_list,
                files_data=files_data,
                total_lines=total_loc,
                agent_logs=agent_logs
            )

            # Step 6: Persist everything to Database
            await self._update_progress(analysis_id, "persisting", 98, "Persisting findings and reports to database...")
            execution_seconds = round(time.time() - start_time, 2)
            debt_res = coord_res["debt_results"]

            async with AsyncSessionLocal() as session:
                res = await session.execute(select(AnalysisRun).where(AnalysisRun.id == analysis_id))
                run = res.scalar_one_or_none()
                if run:
                    run.status = "completed"
                    run.progress_percentage = 100
                    run.current_step = "Analysis completed successfully"
                    run.commit_hash = commit_hash
                    run.branch = active_branch
                    run.total_files = total_files_count
                    run.total_lines = total_loc
                    run.execution_time_seconds = execution_seconds
                    run.health_score = debt_res["overall_health_score"]
                    run.technical_debt_score = debt_res["overall_debt_score"]
                    run.security_score = debt_res["security_score"]
                    run.quality_score = debt_res["quality_score"]
                    run.bugs_score = debt_res["bugs_score"]
                    run.debt_remediation_hours = debt_res["remediation_hours"]
                    run.executive_summary = coord_res["executive_summary"]
                    run.agent_logs = agent_logs
                    run.completed_at = datetime.now(timezone.utc)

                    # Save findings
                    for f in coord_res["findings"]:
                        finding_db = Finding(
                            analysis_id=analysis_id,
                            category=f.category,
                            severity=f.severity,
                            file_path=f.file,
                            line_number=f.line,
                            end_line_number=f.end_line,
                            title=f.title,
                            description=f.description,
                            evidence=f.evidence,
                            source=f.source,
                            confidence=f.confidence,
                            recommendation=f.recommendation,
                            technical_debt_impact=f.technical_debt_impact,
                            rag_source=f.rag_source
                        )
                        session.add(finding_db)

                    # Save file metrics
                    for m in metrics_list:
                        metric_db = TechnicalDebtMetric(
                            analysis_id=analysis_id,
                            file_path=m["file_path"],
                            loc=m["loc"],
                            sloc=m["sloc"],
                            cyclomatic_complexity=m["cyclomatic_complexity"],
                            halstead_volume=m["halstead_volume"],
                            maintainability_index=m["maintainability_index"],
                            cognitive_complexity=m["cognitive_complexity"]
                        )
                        session.add(metric_db)

                    # Save recommendations
                    for r in coord_res["recommendations"]:
                        rec_db = Recommendation(
                            analysis_id=analysis_id,
                            priority=r["priority"],
                            title=r["title"],
                            category=r["category"],
                            action_items=r["action_items"],
                            estimated_effort_hours=r["estimated_effort_hours"],
                            rationale=r.get("rationale")
                        )
                        session.add(rec_db)

                    await session.commit()
                    logger.info(f"Analysis {analysis_id} completed successfully in {execution_seconds}s")

        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}", exc_info=True)
            await self._update_progress(
                analysis_id=analysis_id,
                status="failed",
                progress=100,
                step_name="Analysis failed",
                error_msg=str(e)
            )
        finally:
            if temp_dir:
                RepoService.cleanup_temp_dir(temp_dir)


analysis_engine = AnalysisEngine()
