import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    url = Column(String(512), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=True)
    default_branch = Column(String(100), default="main")
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    analyses = relationship("AnalysisRun", back_populates="repository", cascade="all, delete-orphan")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id"), nullable=False, index=True)
    status = Column(String(50), default="queued", index=True)
    progress_percentage = Column(Integer, default=0)
    current_step = Column(String(255), default="Initialized")
    error_message = Column(Text, nullable=True)

    commit_hash = Column(String(64), nullable=True)
    branch = Column(String(100), default="main")
    total_files = Column(Integer, default=0)
    total_lines = Column(Integer, default=0)
    execution_time_seconds = Column(Float, default=0.0)

    health_score = Column(Float, default=100.0)
    technical_debt_score = Column(Float, default=0.0)
    security_score = Column(Float, default=100.0)
    quality_score = Column(Float, default=100.0)
    bugs_score = Column(Float, default=100.0)
    debt_remediation_hours = Column(Float, default=0.0)

    executive_summary = Column(Text, nullable=True)
    architecture_overview = Column(Text, nullable=True)
    agent_logs = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), default=get_utc_now, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    repository = relationship("Repository", back_populates="analyses")
    findings = relationship("Finding", back_populates="analysis", cascade="all, delete-orphan")
    metrics = relationship("TechnicalDebtMetric", back_populates="analysis", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="analysis", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analysis_runs.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    file_path = Column(String(512), nullable=False, index=True)
    line_number = Column(Integer, nullable=True)
    end_line_number = Column(Integer, nullable=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    source = Column(String(100), default="ast")
    confidence = Column(Float, default=1.0)
    recommendation = Column(Text, nullable=False)
    technical_debt_impact = Column(Integer, default=1)
    rag_source = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    analysis = relationship("AnalysisRun", back_populates="findings")


class TechnicalDebtMetric(Base):
    __tablename__ = "technical_debt_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analysis_runs.id"), nullable=False, index=True)
    file_path = Column(String(512), nullable=False)
    loc = Column(Integer, default=0)
    sloc = Column(Integer, default=0)
    cyclomatic_complexity = Column(Float, default=1.0)
    halstead_volume = Column(Float, default=0.0)
    maintainability_index = Column(Float, default=100.0)
    function_count = Column(Integer, default=0)
    class_count = Column(Integer, default=0)
    cognitive_complexity = Column(Integer, default=0)

    analysis = relationship("AnalysisRun", back_populates="metrics")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analysis_runs.id"), nullable=False, index=True)
    priority = Column(Integer, default=1)
    title = Column(String(255), nullable=False)
    action_items = Column(JSON, default=list)
    category = Column(String(50), default="general")
    estimated_effort_hours = Column(Float, default=1.0)
    rationale = Column(Text, nullable=True)

    analysis = relationship("AnalysisRun", back_populates="recommendations")
