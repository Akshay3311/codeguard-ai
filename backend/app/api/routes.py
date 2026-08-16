from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pathlib import Path

from app.database.session import get_db
from app.database.models import Repository, AnalysisRun, Finding, TechnicalDebtMetric, Recommendation
from app.schemas.analysis import (
    AnalyzeRequest,
    AnalyzeResponse,
    AnalysisStatusResponse,
    RepositoryResponse,
    MetricResponse,
    RecommendationResponse,
)
from app.schemas.finding import FindingResponse, FindingSummary
from app.schemas.report import FullReportResponse, ScoreBreakdown
from app.services.analysis_engine import analysis_engine
from app.core.logging import logger

router = APIRouter(prefix="/api/v1", tags=["Analysis"])


@router.post("/analyze", response_model=AnalyzeResponse, status_code=202)
async def start_analysis(
    payload: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a repository URL for asynchronous code review and technical debt analysis.
    """
    repo_url = payload.repository_url.strip()
    branch = payload.branch or "main"

    # Find or create repository
    res = await db.execute(select(Repository).where(Repository.url == repo_url))
    repo = res.scalar_one_or_none()

    if not repo:
        clean_url = repo_url.rstrip("/")
        name = Path(clean_url).name.replace(".git", "") or "repository"
        repo = Repository(
            url=repo_url,
            name=name,
            default_branch=branch
        )
        db.add(repo)
        await db.commit()
        await db.refresh(repo)

    # Create new AnalysisRun
    analysis = AnalysisRun(
        repository_id=repo.id,
        status="queued",
        progress_percentage=5,
        current_step="Queued for analysis",
        branch=branch
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    # Launch background task
    background_tasks.add_task(
        analysis_engine.execute_analysis,
        analysis_id=analysis.id,
        repo_url=repo_url,
        branch=branch
    )

    logger.info(f"Queued analysis {analysis.id} for repository {repo_url}")

    return AnalyzeResponse(
        analysis_id=analysis.id,
        status="queued",
        repository_url=repo_url,
        message="Repository analysis has been queued successfully."
    )


@router.get("/analysis/{analysis_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    analysis_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the current execution status, progress percentage, and top-level scores.
    """
    res = await db.execute(
        select(AnalysisRun, Repository)
        .join(Repository, AnalysisRun.repository_id == Repository.id)
        .where(AnalysisRun.id == analysis_id)
    )
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    run, repo = row
    return AnalysisStatusResponse(
        analysis_id=run.id,
        repository_id=repo.id,
        repository_url=repo.url,
        repository_name=repo.name,
        status=run.status,
        progress_percentage=run.progress_percentage,
        current_step=run.current_step,
        error_message=run.error_message,
        created_at=run.created_at,
        completed_at=run.completed_at,
        total_files=run.total_files,
        total_lines=run.total_lines,
        execution_time_seconds=run.execution_time_seconds,
        health_score=run.health_score,
        technical_debt_score=run.technical_debt_score,
        security_score=run.security_score,
        quality_score=run.quality_score,
        bugs_score=run.bugs_score,
        debt_remediation_hours=run.debt_remediation_hours
    )


@router.get("/analysis/{analysis_id}/findings", response_model=List[FindingResponse])
async def get_analysis_findings(
    analysis_id: str,
    category: Optional[str] = Query(None, description="Filter by category: security, quality, bug, debt"),
    severity: Optional[str] = Query(None, description="Filter by severity: critical, high, medium, low, info"),
    file_path: Optional[str] = Query(None, description="Filter by file path substring"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves detailed findings for an analysis with optional category and severity filtering.
    """
    query = select(Finding).where(Finding.analysis_id == analysis_id)

    if category:
        query = query.where(Finding.category == category.lower())
    if severity:
        query = query.where(Finding.severity == severity.lower())
    if file_path:
        query = query.where(Finding.file_path.ilike(f"%{file_path}%"))

    # Order by severity priority
    res = await db.execute(query)
    findings = res.scalars().all()

    return [
        FindingResponse(
            id=f.id,
            analysis_id=f.analysis_id,
            category=f.category,
            severity=f.severity,
            file=f.file_path,
            line=f.line_number,
            end_line=f.end_line_number,
            title=f.title,
            description=f.description,
            evidence=f.evidence,
            source=f.source,
            confidence=f.confidence,
            recommendation=f.recommendation,
            technical_debt_impact=f.technical_debt_impact,
            rag_source=f.rag_source,
            created_at=f.created_at
        )
        for f in findings
    ]


@router.get("/analysis/{analysis_id}/report", response_model=FullReportResponse)
async def get_full_report(
    analysis_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves the complete comprehensive review report including all findings, metrics,
    prioritized roadmap recommendations, and executive summaries.
    """
    # Fetch run and repo
    res = await db.execute(
        select(AnalysisRun, Repository)
        .join(Repository, AnalysisRun.repository_id == Repository.id)
        .where(AnalysisRun.id == analysis_id)
    )
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    run, repo = row

    # Fetch findings
    res_findings = await db.execute(select(Finding).where(Finding.analysis_id == analysis_id))
    db_findings = res_findings.scalars().all()

    # Fetch metrics
    res_metrics = await db.execute(select(TechnicalDebtMetric).where(TechnicalDebtMetric.analysis_id == analysis_id))
    db_metrics = res_metrics.scalars().all()

    # Fetch recommendations
    res_recs = await db.execute(
        select(Recommendation).where(Recommendation.analysis_id == analysis_id).order_by(Recommendation.priority)
    )
    db_recs = res_recs.scalars().all()

    # Compute finding summary counts
    summary = FindingSummary(total_findings=len(db_findings))
    for f in db_findings:
        if f.severity in summary.by_severity:
            summary.by_severity[f.severity] += 1
        if f.category in summary.by_category:
            summary.by_category[f.category] += 1

    findings_resp = [
        FindingResponse(
            id=f.id,
            analysis_id=f.analysis_id,
            category=f.category,
            severity=f.severity,
            file=f.file_path,
            line=f.line_number,
            end_line=f.end_line_number,
            title=f.title,
            description=f.description,
            evidence=f.evidence,
            source=f.source,
            confidence=f.confidence,
            recommendation=f.recommendation,
            technical_debt_impact=f.technical_debt_impact,
            rag_source=f.rag_source,
            created_at=f.created_at
        )
        for f in db_findings
    ]

    metrics_resp = [
        MetricResponse(
            file_path=m.file_path,
            loc=m.loc,
            sloc=m.sloc,
            cyclomatic_complexity=m.cyclomatic_complexity,
            halstead_volume=m.halstead_volume,
            maintainability_index=m.maintainability_index,
            function_count=m.function_count,
            class_count=m.class_count,
            cognitive_complexity=m.cognitive_complexity
        )
        for m in db_metrics
    ]

    recs_resp = [
        RecommendationResponse(
            id=r.id,
            priority=r.priority,
            title=r.title,
            category=r.category,
            action_items=r.action_items or [],
            estimated_effort_hours=r.estimated_effort_hours,
            rationale=r.rationale
        )
        for r in db_recs
    ]

    return FullReportResponse(
        analysis_id=run.id,
        repository_id=repo.id,
        repository_url=repo.url,
        repository_name=repo.name,
        commit_hash=run.commit_hash,
        branch=run.branch,
        status=run.status,
        execution_time_seconds=run.execution_time_seconds,
        created_at=run.created_at,
        completed_at=run.completed_at,
        executive_summary=run.executive_summary or "Analysis complete.",
        architecture_overview=run.architecture_overview,
        scores=ScoreBreakdown(
            overall_health_score=run.health_score,
            technical_debt_score=run.technical_debt_score,
            security_score=run.security_score,
            quality_score=run.quality_score,
            bugs_score=run.bugs_score,
            debt_remediation_hours=run.debt_remediation_hours
        ),
        total_files_analyzed=run.total_files,
        total_lines_of_code=run.total_lines,
        findings_summary=summary,
        findings=findings_resp,
        metrics=metrics_resp,
        recommendations=recs_resp,
        agent_logs=run.agent_logs or {}
    )


@router.get("/repositories", response_model=List[RepositoryResponse])
async def list_repositories(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    Lists previously analyzed repositories with their latest analysis run status.
    """
    res = await db.execute(
        select(Repository).order_by(desc(Repository.updated_at)).limit(limit)
    )
    repos = res.scalars().all()

    results = []
    for r in repos:
        latest_res = await db.execute(
            select(AnalysisRun)
            .where(AnalysisRun.repository_id == r.id)
            .order_by(desc(AnalysisRun.created_at))
            .limit(1)
        )
        latest_run = latest_res.scalar_one_or_none()

        latest_status = None
        if latest_run:
            latest_status = AnalysisStatusResponse(
                analysis_id=latest_run.id,
                repository_id=r.id,
                repository_url=r.url,
                repository_name=r.name,
                status=latest_run.status,
                progress_percentage=latest_run.progress_percentage,
                current_step=latest_run.current_step,
                error_message=latest_run.error_message,
                created_at=latest_run.created_at,
                completed_at=latest_run.completed_at,
                total_files=latest_run.total_files,
                total_lines=latest_run.total_lines,
                execution_time_seconds=latest_run.execution_time_seconds,
                health_score=latest_run.health_score,
                technical_debt_score=latest_run.technical_debt_score,
                security_score=latest_run.security_score,
                quality_score=latest_run.quality_score,
                bugs_score=latest_run.bugs_score,
                debt_remediation_hours=latest_run.debt_remediation_hours
            )

        results.append(RepositoryResponse(
            id=r.id,
            url=r.url,
            name=r.name,
            owner=r.owner,
            default_branch=r.default_branch,
            created_at=r.created_at,
            updated_at=r.updated_at,
            latest_analysis=latest_status
        ))

    return results


@router.get("/overview/stats")
async def get_overview_stats(db: AsyncSession = Depends(get_db)):
    """
    Provides aggregated dashboard metrics across all historical analyses.
    """
    total_repos_res = await db.execute(select(func.count(Repository.id)))
    total_repos = total_repos_res.scalar() or 0

    total_analyses_res = await db.execute(select(func.count(AnalysisRun.id)))
    total_analyses = total_analyses_res.scalar() or 0

    findings_res = await db.execute(select(func.count(Finding.id)))
    total_findings = findings_res.scalar() or 0

    crit_res = await db.execute(select(func.count(Finding.id)).where(Finding.severity == "critical"))
    critical_issues = crit_res.scalar() or 0

    high_res = await db.execute(select(func.count(Finding.id)).where(Finding.severity == "high"))
    high_issues = high_res.scalar() or 0

    med_res = await db.execute(select(func.count(Finding.id)).where(Finding.severity == "medium"))
    medium_issues = med_res.scalar() or 0

    low_res = await db.execute(select(func.count(Finding.id)).where(Finding.severity.in_(["low", "info"])))
    low_issues = low_res.scalar() or 0

    avg_debt_res = await db.execute(
        select(func.avg(AnalysisRun.technical_debt_score)).where(AnalysisRun.status == "completed")
    )
    avg_debt = avg_debt_res.scalar() or 0.0

    return {
        "total_repositories": total_repos,
        "total_analyses": total_analyses,
        "total_findings": total_findings,
        "critical_issues": critical_issues,
        "high_issues": high_issues,
        "medium_issues": medium_issues,
        "low_issues": low_issues,
        "average_technical_debt": round(float(avg_debt), 1)
    }
