from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.finding import FindingResponse, FindingSummary
from app.schemas.analysis import MetricResponse, RecommendationResponse


class ScoreBreakdown(BaseModel):
    overall_health_score: float = Field(..., description="Overall code health score (0-100, 100 is best)")
    technical_debt_score: float = Field(..., description="Technical debt score (0-100, 0 is best)")
    security_score: float = Field(..., description="Security posture score (0-100, 100 is best)")
    quality_score: float = Field(..., description="Code maintainability & quality score (0-100, 100 is best)")
    bugs_score: float = Field(..., description="Bug safety score (0-100, 100 is best)")
    debt_remediation_hours: float = Field(..., description="Estimated engineering hours to remediate debt")


class AgentExecutionLog(BaseModel):
    agent_name: str
    status: str
    findings_count: int
    summary: str


class FullReportResponse(BaseModel):
    analysis_id: str
    repository_id: str
    repository_url: str
    repository_name: str
    commit_hash: Optional[str] = None
    branch: str = "main"
    status: str
    execution_time_seconds: float
    created_at: datetime
    completed_at: Optional[datetime] = None

    # Overall Summary
    executive_summary: str
    architecture_overview: Optional[str] = None
    
    # High-level Scores
    scores: ScoreBreakdown
    
    # Quantitative Summary
    total_files_analyzed: int
    total_lines_of_code: int
    findings_summary: FindingSummary

    # Details
    findings: List[FindingResponse] = []
    metrics: List[MetricResponse] = []
    recommendations: List[RecommendationResponse] = []
    agent_logs: Dict[str, Any] = Field(default_factory=dict)
