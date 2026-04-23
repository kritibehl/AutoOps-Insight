from typing import List, Optional
from pydantic import BaseModel, Field


class IncidentRecord(BaseModel):
    id: Optional[int] = None
    created_at: Optional[str] = None
    repo_name: Optional[str] = None
    workflow_name: Optional[str] = None
    run_id: Optional[str] = None
    incident_type: str
    failure_family: str
    signature: str
    recurrence_total: int = 1
    confidence: float
    likely_trigger: Optional[str] = None
    trigger_confidence: Optional[float] = None
    root_cause: Optional[str] = None
    release_decision: str
    decision_confidence: float
    decision_reason: List[str] = Field(default_factory=list)
    action: str


class IngestResponse(BaseModel):
    status: str
    repo: Optional[str] = None
    workflow: Optional[str] = None
    run_id: Optional[str] = None
    incident_type: str
    failure_family: str
    signature: str
    recurrence_total: int
    confidence: float
    likely_trigger: Optional[str] = None
    trigger_confidence: Optional[float] = None
    root_cause: Optional[str] = None
    release_decision: str
    decision_confidence: float
    decision_reason: List[str] = Field(default_factory=list)
    action: str


class IncidentsResponse(BaseModel):
    items: List[IncidentRecord]


class MetricsResponse(BaseModel):
    total_analyses: int
    hold_release_count: int
    investigate_count: int
    top_failure_family: Optional[str] = None


class DashboardSummaryResponse(BaseModel):
    top_failures: list
    noisy_services: list
    action_summary: dict
    recurrence_heatmap: list
