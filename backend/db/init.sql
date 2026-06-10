CREATE TABLE IF NOT EXISTS scan_results (
    id         SERIAL PRIMARY KEY,
    scan_type  VARCHAR(50),
    status     VARCHAR(20),
    data       TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alerts (
    id          SERIAL PRIMARY KEY,
    severity    VARCHAR(20),
    title       VARCHAR(200),
    detail      TEXT,
    tool        VARCHAR(100),
    fix         TEXT,
    risk_level  VARCHAR(20),
    ai_analysis TEXT,
    resolved    INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_severity   ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved   ON alerts(resolved);
CREATE INDEX IF NOT EXISTS idx_scans_created_at  ON scan_results(created_at);
