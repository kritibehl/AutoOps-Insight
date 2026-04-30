-- Base incident table (mirrors AutoOps output)
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP,
    repo_name TEXT,
    workflow_name TEXT,
    run_id TEXT,
    incident_type TEXT,
    failure_family TEXT,
    signature TEXT,
    recurrence_total INTEGER,
    confidence FLOAT,
    likely_trigger TEXT,
    trigger_confidence FLOAT,
    root_cause TEXT,
    release_decision TEXT,
    decision_confidence FLOAT,
    action TEXT
);

-- Daily aggregated metrics
CREATE TABLE incident_daily_summary AS
SELECT
    DATE(created_at) as day,
    COUNT(*) as total_incidents,
    SUM(CASE WHEN action = 'hold_release' THEN 1 ELSE 0 END) as hold_release_count,
    SUM(CASE WHEN action = 'investigate' THEN 1 ELSE 0 END) as investigate_count
FROM incidents
GROUP BY day;
