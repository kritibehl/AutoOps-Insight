-- Service health summary by source
SELECT
  source,
  COUNT(*) AS incident_count,
  SUM(CASE WHEN escalation_required = 1 THEN 1 ELSE 0 END) AS escalation_count,
  COUNT(DISTINCT issue_family) AS issue_family_count
FROM support_incidents
GROUP BY source
ORDER BY escalation_count DESC, incident_count DESC;

-- Recurring blocker report
SELECT
  signature,
  issue_family,
  MAX(recurrence_total) AS recurrence_total,
  action
FROM support_incidents
GROUP BY signature, issue_family, action
HAVING MAX(recurrence_total) >= 3
ORDER BY recurrence_total DESC;

-- Business-impact reporting query
SELECT
  source,
  issue_family,
  action,
  COUNT(*) AS impacted_cases
FROM support_incidents
GROUP BY source, issue_family, action
ORDER BY impacted_cases DESC;
