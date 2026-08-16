from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


SeverityType = Literal["critical", "high", "medium", "low", "info"]
CategoryType = Literal["security", "quality", "bug", "debt"]


class FindingBase(BaseModel):
    category: CategoryType = Field(..., description="Category of the finding: security, quality, bug, debt")
    severity: SeverityType = Field(..., description="Severity level: critical, high, medium, low, info")
    file: str = Field(..., description="Relative file path where the issue was found")
    line: Optional[int] = Field(None, description="Starting line number (1-indexed)")
    end_line: Optional[int] = Field(None, description="Ending line number (1-indexed)")
    title: str = Field(..., description="Concise, descriptive title of the issue")
    description: str = Field(..., description="Detailed explanation of why this is an issue")
    evidence: Optional[str] = Field(None, description="Code snippet or syntactic evidence")
    source: str = Field("ast", description="Source tool or agent: ast, bandit, radon, quality_agent, security_agent, bug_agent")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    recommendation: str = Field(..., description="Actionable recommendation to fix or refactor")
    technical_debt_impact: int = Field(default=1, ge=1, le=10, description="Technical debt impact score (1 to 10)")
    rag_source: Optional[str] = Field(None, description="Referenced engineering standard or rule citation")


class FindingCreate(FindingBase):
    pass


class FindingResponse(FindingBase):
    id: str
    analysis_id: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FindingSummary(BaseModel):
    total_findings: int = 0
    by_severity: dict[str, int] = Field(default_factory=lambda: {
        "critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0
    })
    by_category: dict[str, int] = Field(default_factory=lambda: {
        "security": 0, "quality": 0, "bug": 0, "debt": 0
    })
