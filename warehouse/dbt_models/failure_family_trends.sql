SELECT
    failure_family,
    COUNT(*) as incident_count
FROM incidents
GROUP BY failure_family
ORDER BY incident_count DESC;
