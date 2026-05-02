SELECT
    action,
    COUNT(*) AS action_count,
    AVG(confidence) AS avg_confidence
FROM support_incidents
GROUP BY action
ORDER BY action_count DESC;
