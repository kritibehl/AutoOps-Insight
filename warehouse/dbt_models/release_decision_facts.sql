SELECT
    release_decision,
    COUNT(*) as decision_count,
    AVG(decision_confidence) as avg_confidence
FROM incidents
GROUP BY release_decision;
