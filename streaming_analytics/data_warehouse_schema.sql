CREATE TABLE dim_service (
  service_id INTEGER PRIMARY KEY,
  service_name TEXT NOT NULL,
  owner_team TEXT,
  business_domain TEXT
);

CREATE TABLE dim_region (
  region_id INTEGER PRIMARY KEY,
  region_name TEXT NOT NULL
);

CREATE TABLE fact_operational_event (
  event_id TEXT PRIMARY KEY,
  service_id INTEGER,
  region_id INTEGER,
  event_type TEXT,
  latency_ms INTEGER,
  error_rate REAL,
  event_timestamp TIMESTAMP,
  anomaly_flag BOOLEAN,
  FOREIGN KEY (service_id) REFERENCES dim_service(service_id),
  FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
);

CREATE TABLE fact_service_health_daily (
  service_id INTEGER,
  event_day DATE,
  event_count INTEGER,
  avg_latency_ms REAL,
  avg_error_rate REAL,
  anomaly_count INTEGER,
  PRIMARY KEY (service_id, event_day)
);
