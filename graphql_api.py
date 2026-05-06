from __future__ import annotations

from collections import Counter, defaultdict
from typing import List, Optional

import strawberry
from strawberry.fastapi import GraphQLRouter

from storage.history import (
    get_all_analyses,
    get_analysis_by_id,
    get_report_summary,
    get_top_recurring_signatures,
)


@strawberry.type
class Incident:
    id: int
    created_at: str
    filename: Optional[str]
    predicted_issue: str
    failure_family: str
    severity: str
    signature: str
    confidence: float
    release_blocking: bool
    probable_owner: Optional[str]
    summary: Optional[str]


@strawberry.type
class FailureFamilyCount:
    failure_family: str
    total_count: int


@strawberry.type
class RecurringSignature:
    signature: str
    failure_family: str
    severity: str
    total_count: int
    first_seen: Optional[str]
    last_seen: Optional[str]


@strawberry.type
class MetricsSummary:
    total_analyses: int
    release_blockers: int
    release_risk: str
    top_failure_families: List[FailureFamilyCount]
    top_recurring_signatures: List[RecurringSignature]


@strawberry.type
class NoisyService:
    service: str
    total_count: int
    release_blocking_count: int


@strawberry.type
class RecurrenceHeatmapCell:
    failure_family: str
    signature: str
    total_count: int
    severity: str


def _to_incident(row: dict) -> Incident:
    return Incident(
        id=int(row["id"]),
        created_at=str(row.get("created_at") or ""),
        filename=row.get("filename"),
        predicted_issue=str(row.get("predicted_issue") or ""),
        failure_family=str(row.get("failure_family") or ""),
        severity=str(row.get("severity") or ""),
        signature=str(row.get("signature") or ""),
        confidence=float(row.get("confidence") or 0.0),
        release_blocking=bool(row.get("release_blocking")),
        probable_owner=row.get("probable_owner"),
        summary=row.get("summary"),
    )


def _to_recurring(row: dict) -> RecurringSignature:
    return RecurringSignature(
        signature=str(row.get("signature") or ""),
        failure_family=str(row.get("failure_family") or ""),
        severity=str(row.get("severity") or ""),
        total_count=int(row.get("total_count") or 0),
        first_seen=row.get("first_seen"),
        last_seen=row.get("last_seen"),
    )


@strawberry.type
class Query:
    @strawberry.field
    def incidents(self, limit: int = 50) -> List[Incident]:
        return [_to_incident(row) for row in get_all_analyses(limit=limit)]

    @strawberry.field
    def incident(self, id: int) -> Optional[Incident]:
        row = get_analysis_by_id(id)
        return _to_incident(row) if row else None

    @strawberry.field
    def metrics_summary(self) -> MetricsSummary:
        summary = get_report_summary()
        families = [
            FailureFamilyCount(
                failure_family=str(item.get("failure_family") or ""),
                total_count=int(item.get("total_count") or 0),
            )
            for item in summary.get("top_failure_families", [])
        ]
        recurring = [
            _to_recurring(item)
            for item in summary.get("top_recurring_signatures", [])
        ]
        return MetricsSummary(
            total_analyses=int(summary.get("total_analyses") or 0),
            release_blockers=int(summary.get("release_blockers") or 0),
            release_risk=str(summary.get("release_risk") or "unknown"),
            top_failure_families=families,
            top_recurring_signatures=recurring,
        )

    @strawberry.field
    def noisy_services(self, limit: int = 10) -> List[NoisyService]:
        rows = get_all_analyses(limit=1000)
        totals = Counter()
        blockers = Counter()

        for row in rows:
            service = (
                row.get("probable_owner")
                or row.get("filename")
                or "unknown"
            )
            totals[str(service)] += 1
            if row.get("release_blocking"):
                blockers[str(service)] += 1

        return [
            NoisyService(
                service=service,
                total_count=count,
                release_blocking_count=blockers[service],
            )
            for service, count in totals.most_common(limit)
        ]

    @strawberry.field
    def recurrence_heatmap(self, limit: int = 25) -> List[RecurrenceHeatmapCell]:
        recurring = get_top_recurring_signatures(limit=limit)
        return [
            RecurrenceHeatmapCell(
                failure_family=str(row.get("failure_family") or ""),
                signature=str(row.get("signature") or ""),
                total_count=int(row.get("total_count") or 0),
                severity=str(row.get("severity") or ""),
            )
            for row in recurring
        ]


schema = strawberry.Schema(query=Query)
graphql_router = GraphQLRouter(schema)
