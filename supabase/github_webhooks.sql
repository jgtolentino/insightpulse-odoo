-- GitHub Webhooks Tables
-- Run this migration in Supabase SQL editor

-- Table: github_webhooks
-- Stores all incoming GitHub webhook events
CREATE TABLE IF NOT EXISTS github_webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type TEXT NOT NULL,
  delivery_id TEXT NOT NULL UNIQUE,
  payload JSONB NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_github_webhooks_event_type ON github_webhooks(event_type);
CREATE INDEX IF NOT EXISTS idx_github_webhooks_received_at ON github_webhooks(received_at);
CREATE INDEX IF NOT EXISTS idx_github_webhooks_delivery_id ON github_webhooks(delivery_id);

-- Table: github_installations
-- Tracks GitHub App installations
CREATE TABLE IF NOT EXISTS github_installations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  installation_id BIGINT NOT NULL UNIQUE,
  account_login TEXT NOT NULL,
  account_type TEXT NOT NULL,
  action TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_github_installations_account ON github_installations(account_login);
CREATE INDEX IF NOT EXISTS idx_github_installations_id ON github_installations(installation_id);

-- Enable Row Level Security
ALTER TABLE github_webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE github_installations ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Service role only (backend API access)
CREATE POLICY "Service role only" ON github_webhooks
  FOR ALL
  USING (auth.role() = 'service_role');

CREATE POLICY "Service role only" ON github_installations
  FOR ALL
  USING (auth.role() = 'service_role');

-- Comments
COMMENT ON TABLE github_webhooks IS 'Stores all incoming GitHub webhook events for auditing and processing';
COMMENT ON TABLE github_installations IS 'Tracks GitHub App installations and their metadata';
