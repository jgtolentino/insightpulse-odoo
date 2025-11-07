-- Operations Tables for Auto-Healing and Monitoring
-- Schema for heartbeats, webhooks, and incidents

-- Heartbeats table
CREATE TABLE IF NOT EXISTS ops_heartbeats (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  source TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('ok', 'warn', 'fail')),
  meta JSONB DEFAULT '{}'::JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_ops_heartbeats_source_created
  ON ops_heartbeats(source, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ops_heartbeats_status
  ON ops_heartbeats(status);

-- Webhook queue (generic async processing)
CREATE TABLE IF NOT EXISTS ops_webhook_queue (
  id BIGSERIAL PRIMARY KEY,
  topic TEXT NOT NULL,
  payload JSONB NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'processing', 'done', 'error')),
  idempotency_key TEXT,
  error TEXT,
  attempts INT NOT NULL DEFAULT 0,
  next_run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (idempotency_key)
);

-- Indexes for queue processing
CREATE INDEX IF NOT EXISTS idx_ops_webhook_queue_status_next_run
  ON ops_webhook_queue(status, next_run_at)
  WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_ops_webhook_queue_topic
  ON ops_webhook_queue(topic);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_ops_webhook_queue_updated_at
  BEFORE UPDATE ON ops_webhook_queue
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Incidents table
CREATE TABLE IF NOT EXISTS ops_incidents (
  id BIGSERIAL PRIMARY KEY,
  sev TEXT NOT NULL CHECK (sev IN ('P0', 'P1', 'P2')),
  title TEXT NOT NULL,
  details JSONB DEFAULT '{}'::JSONB,
  status TEXT NOT NULL DEFAULT 'open'
    CHECK (status IN ('open', 'ack', 'closed')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  acknowledged_at TIMESTAMPTZ,
  closed_at TIMESTAMPTZ,
  resolved_by TEXT
);

-- Indexes for incident management
CREATE INDEX IF NOT EXISTS idx_ops_incidents_status
  ON ops_incidents(status);
CREATE INDEX IF NOT EXISTS idx_ops_incidents_sev_created
  ON ops_incidents(sev, created_at DESC);

-- Auto-healing actions log
CREATE TABLE IF NOT EXISTS ops_healing_actions (
  id BIGSERIAL PRIMARY KEY,
  error_id TEXT NOT NULL,  -- e.g., ODOO-LONGPOLL-STALL
  handler TEXT NOT NULL,   -- e.g., restart_longpoll.sh
  triggered_by TEXT NOT NULL,  -- alert|manual|scheduled
  status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'success', 'failed')),
  output TEXT,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX IF NOT EXISTS idx_ops_healing_actions_error_id
  ON ops_healing_actions(error_id);
CREATE INDEX IF NOT EXISTS idx_ops_healing_actions_status
  ON ops_healing_actions(status);

-- Comments
COMMENT ON TABLE ops_heartbeats IS 'System heartbeat monitoring';
COMMENT ON TABLE ops_webhook_queue IS 'Async webhook processing queue with retry';
COMMENT ON TABLE ops_incidents IS 'Operational incidents tracking';
COMMENT ON TABLE ops_healing_actions IS 'Auto-healing actions audit log';

-- Grant permissions (adjust as needed)
-- For now, only service_role can access these tables
-- Add more granular RLS policies as needed
