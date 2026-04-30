SELECT
    DATE(created_at) as day,
    COUNT(*) as total_incidents,
    SUM(CASE WHEN action = 'hold_release' THEN 1 ELSE 0 END) as hold_release_count,
    SUM(CASE WHEN action = 'investigate' THEN 1 ELSE 0 END) as investigate_count
FROM incidents
GROUP BY day
ORDER BY day DESC;
