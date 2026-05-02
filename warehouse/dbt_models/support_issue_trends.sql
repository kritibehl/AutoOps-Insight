SELECT
    issue_family,
    COUNT(*) AS issue_count,
    AVG(confidence) AS avg_confidence
FROM support_incidents
GROUP BY issue_family
ORDER BY issue_count DESC;
