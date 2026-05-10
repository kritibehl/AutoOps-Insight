-- Daily incident volume by issue family
SELECT
  DATE(created_at) AS day,
  issue_family,
  COUNT(*) AS incident_count
FROM support_incidents
GROUP BY DATE(created_at), issue_family
ORDER BY day DESC, incident_count DESC;
