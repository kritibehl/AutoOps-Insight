INSERT INTO incidents (
  incident_id, service, source, severity, issue_type, issue_family,
  symptom, customer_impact, probable_owner, recommended_action,
  escalation_required, status, created_at
) VALUES
('SUP-1001','reporting-api','support_channel','medium','api_timeout','latency_or_timeout','requests timing out after deployment','reporting delayed','reporting_platform_team','Check recent deploys, upstream latency, timeout budgets, and dependency health.', false, 'triaged', NOW()),
('SUP-1002','agentgrid','agentgrid','high','tool_failure','tool_failure','tool call failed during answer generation','customer workflow blocked','platform_runtime_team','Check tool dependency health and retry path.', true, 'escalated', NOW()),
('SUP-1003','agentgrid','agentgrid','high','unsafe_response','unsafe_response','unsafe answer detected','requires safety review','support_operations_team','Escalate to safety review before launch readiness.', true, 'escalated', NOW());

INSERT INTO service_health (
  service, health_status, risk_level, incident_count, escalation_count, updated_at
) VALUES
('reporting-api','degraded','medium',1,0,NOW()),
('agentgrid','degraded','high',2,2,NOW());

INSERT INTO reporting_snapshots (
  report_week, total_incidents, total_escalations, top_issue_family, summary, created_at
) VALUES
('2026-W18',102,51,'unsafe_response','Weekly support analytics summary for incident trends, escalations, and recurring blockers.',NOW());
