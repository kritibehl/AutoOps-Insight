from typing import List, Optional, Literal
from pydantic import BaseModel, Field


Severity = Literal["low", "medium", "high", "critical"]


class EvidenceLine(BaseModel):
    line_number: int
    text: str


class RecentOccurrence(BaseModel):
    id: int
    created_at: str
    filename: Optional[str] = None
    failure_family: str
    severity: str
    confidence: float


class RecurrenceInfo(BaseModel):
    total_count: int = 0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    is_recurring: bool = False
    recent_occurrences: List[RecentOccurrence] = Field(default_factory=list)


class IncidentAnalysis(BaseModel):
    predicted_issue: str = Field(..., description="Final issue label exposed to clients")
    confidence: float = Field(..., ge=0.0, le=1.0)

    failure_family: str = Field(..., description="Normalized operational taxonomy label")
    severity: Severity = Field(..., description="Estimated operational severity")

    signature: str = Field(..., description="Stable normalized fingerprint for recurring failures")
    summary: str = Field(..., description="Short structured summary")

    likely_cause: Optional[str] = None
    first_remediation_step: Optional[str] = None
    next_debugging_action: Optional[str] = None
    probable_owner: Optional[str] = None
    release_blocking: bool = False

    evidence: List[EvidenceLine] = Field(default_factory=list)
    recurrence: Optional[RecurrenceInfo] = None

    used_rule_based_detection: bool = False
    used_ml_prediction: bool = False
