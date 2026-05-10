-- Service health summary by escalation and severity
SELECT
  service,
  severity,
  COUNT(*) AS incident_count,
  SUM(CASE WHEN status = 'escalated' THEN 1 ELSE 0 END) AS escalated_count
FROM support_incidents
GROUP BY service, severity
ORDER BY escalated_count DESC, incident_count DESC;
