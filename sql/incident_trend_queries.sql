-- Weekly incident volume by issue family
SELECT
  DATE_TRUNC('week', created_at) AS report_week,
  issue_family,
  COUNT(*) AS incident_count,
  SUM(CASE WHEN escalation_required = 1 THEN 1 ELSE 0 END) AS escalation_count
FROM support_incidents
GROUP BY report_week, issue_family
ORDER BY report_week DESC, incident_count DESC;

-- Recommended action distribution
SELECT
  action,
  COUNT(*) AS action_count
FROM support_incidents
GROUP BY action
ORDER BY action_count DESC;

-- Stakeholder-facing issue summary
SELECT
  issue_family,
  COUNT(*) AS incident_count,
  MAX(recurrence_total) AS max_recurrence,
  SUM(CASE WHEN escalation_required = 1 THEN 1 ELSE 0 END) AS escalations
FROM support_incidents
GROUP BY issue_family
ORDER BY escalations DESC, incident_count DESC;
