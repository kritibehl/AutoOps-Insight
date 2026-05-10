-- Recurring failure patterns by service and issue type
SELECT
  service,
  issue_type,
  COUNT(*) AS recurrence_count
FROM support_incidents
GROUP BY service, issue_type
HAVING COUNT(*) >= 3
ORDER BY recurrence_count DESC;
