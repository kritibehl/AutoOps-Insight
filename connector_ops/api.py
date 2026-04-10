from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from connector_ops.service import (
    connector_analytics,
    list_connector_runs,
    list_connectors,
    run_connector,
    upsert_connector_config,
)

router = APIRouter(prefix="", tags=["connector-ops"])


class ConnectorConfigIn(BaseModel):
    connector_name: str
    source_system: str
    target_system: str
    source_endpoint: str
    target_endpoint: str
    field_mapping: dict[str, str]
    required_source_fields: list[str]
    required_target_fields: list[str]
    retry_limit: int = 3
    retry_backoff_seconds: float = 0.5
    is_enabled: bool = True


class ConnectorRunIn(BaseModel):
    connector_name: str
    source_payload: list[dict[str, Any]]
    fail_mode: str | None = None


@router.post("/connectors")
def create_or_update_connector(body: ConnectorConfigIn):
    return upsert_connector_config(
        connector_name=body.connector_name,
        source_system=body.source_system,
        target_system=body.target_system,
        source_endpoint=body.source_endpoint,
        target_endpoint=body.target_endpoint,
        field_mapping=body.field_mapping,
        required_source_fields=body.required_source_fields,
        required_target_fields=body.required_target_fields,
        retry_limit=body.retry_limit,
        retry_backoff_seconds=body.retry_backoff_seconds,
        is_enabled=body.is_enabled,
    )


@router.get("/connectors")
def get_connectors():
    return {"items": list_connectors()}


@router.post("/connectors/run")
def execute_connector(body: ConnectorRunIn):
    return run_connector(
        connector_name=body.connector_name,
        source_payload=body.source_payload,
        fail_mode=body.fail_mode,
    )


@router.get("/connectors/runs")
def get_connector_runs(limit: int = 50):
    return {"items": list_connector_runs(limit=limit)}


@router.get("/connectors/analytics")
def get_connector_analytics():
    return connector_analytics()
