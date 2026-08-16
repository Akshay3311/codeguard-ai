from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re


class AnalyzeRequest(BaseModel):
    repository_url: str = Field(
        ...,
        description="Public GitHub repository URL (e.g., https://github.com/psf/requests)",
        examples=["https://github.com/octocat/Hello-World"]
    )
    branch: Optional[str] = Field(default="main", description="Target branch to analyze")

    @field_validator("repository_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        v = v.strip()
        github_pattern = r"^https?://(www\.)?(github\.com|gitlab\.com)/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(\.git)?/?$"
        local_pattern = r"^[A-Za-z]:\\[^<>:\"/\\|?*]+|^/[^<>:\"/\\|?*]+"
        
        if not re.match(github_pattern, v) and not re.match(local_pattern, v):
            raise ValueError(
                "Invalid repository URL. Must be a valid GitHub/GitLab URL (e.g. 'https://github.com/owner/repo') or accessible local path."
            )
        return v


class AnalyzeResponse(BaseModel):
    analysis_id: str
    status: str
    repository_url: str
    message: str


class MetricResponse(BaseModel):
    file_path: str
    loc: int
    sloc: int
    cyclomatic_complexity: float
    halstead_volume: float
    maintainability_index: float
    function_count: int
    class_count: int
    cognitive_complexity: int

    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(BaseModel):
    id: str
    priority: int
    title: str
    category: str
    action_items: List[str]
    estimated_effort_hours: float
    rationale: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    repository_id: str
    repository_url: str
    repository_name: str
    status: str
    progress_percentage: int
    current_step: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_files: int
    total_lines: int
    execution_time_seconds: float

    # High-level scores
    health_score: float
    technical_debt_score: float
    security_score: float
    quality_score: float
    bugs_score: float
    debt_remediation_hours: float

    model_config = ConfigDict(from_attributes=True)


class RepositoryResponse(BaseModel):
    id: str
    url: str
    name: str
    owner: Optional[str] = None
    default_branch: str
    created_at: datetime
    updated_at: datetime
    latest_analysis: Optional[AnalysisStatusResponse] = None

    model_config = ConfigDict(from_attributes=True)
