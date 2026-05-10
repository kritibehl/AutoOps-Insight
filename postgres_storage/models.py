from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True)
    incident_id = Column(String, unique=True, index=True)
    service = Column(String, index=True)
    source = Column(String, index=True)
    severity = Column(String, index=True)
    issue_type = Column(String, index=True)
    issue_family = Column(String, index=True)
    symptom = Column(Text)
    customer_impact = Column(Text)
    probable_owner = Column(String)
    recommended_action = Column(Text)
    escalation_required = Column(Boolean, default=False)
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)

class ServiceHealth(Base):
    __tablename__ = "service_health"

    id = Column(Integer, primary_key=True)
    service = Column(String, index=True)
    health_status = Column(String)
    risk_level = Column(String)
    incident_count = Column(Integer, default=0)
    escalation_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True)
    incident_id = Column(String, ForeignKey("incidents.incident_id"))
    escalation_path = Column(Text)
    owner = Column(String)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReportingSnapshot(Base):
    __tablename__ = "reporting_snapshots"

    id = Column(Integer, primary_key=True)
    report_week = Column(String, index=True)
    total_incidents = Column(Integer)
    total_escalations = Column(Integer)
    top_issue_family = Column(String)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
