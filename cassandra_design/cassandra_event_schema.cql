CREATE KEYSPACE IF NOT EXISTS autoops_events
WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'us_central': 3
};

CREATE TABLE IF NOT EXISTS autoops_events.incident_events_by_service_day (
  service text,
  event_day date,
  event_ts timestamp,
  event_id text,
  severity text,
  issue_family text,
  source text,
  escalated boolean,
  payload text,
  PRIMARY KEY ((service, event_day), event_ts, event_id)
) WITH CLUSTERING ORDER BY (event_ts DESC);

CREATE TABLE IF NOT EXISTS autoops_events.incident_events_by_issue_family_day (
  issue_family text,
  event_day date,
  event_ts timestamp,
  event_id text,
  service text,
  severity text,
  escalated boolean,
  payload text,
  PRIMARY KEY ((issue_family, event_day), event_ts, event_id)
) WITH CLUSTERING ORDER BY (event_ts DESC);

CREATE TABLE IF NOT EXISTS autoops_events.escalations_by_day (
  event_day date,
  severity text,
  event_ts timestamp,
  event_id text,
  service text,
  issue_family text,
  owner text,
  payload text,
  PRIMARY KEY ((event_day, severity), event_ts, event_id)
) WITH CLUSTERING ORDER BY (event_ts DESC);
