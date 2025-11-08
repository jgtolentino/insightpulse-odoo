-- ═══════════════════════════════════════════════════════════════
-- Odoo-Supabase Event Bridge - Core Schema
-- ═══════════════════════════════════════════════════════════════

-- Core event/audit tables
CREATE TABLE IF NOT EXISTS audit_event (
  id BIGSERIAL PRIMARY KEY,
  source TEXT NOT NULL CHECK (source IN ('odoo','supabase','bridge')),
  event_type TEXT NOT NULL,
  resource_id TEXT,
  payload JSONB NOT NULL,
  correlation_id UUID DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_event_created ON audit_event (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_event (event_type);
CREATE INDEX IF NOT EXISTS idx_audit_event_correlation ON audit_event (correlation_id);
CREATE INDEX IF NOT EXISTS idx_audit_event_source ON audit_event (source);

-- Outbox for actions destined to Odoo
CREATE TABLE IF NOT EXISTS odoo_action_outbox (
  id BIGSERIAL PRIMARY KEY,
  action TEXT NOT NULL,               -- e.g., account.move.post
  args JSONB NOT NULL,                -- opaque payload
  status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','sent','applied','error')),
  last_error TEXT,
  correlation_id UUID DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  applied_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_outbox_status ON odoo_action_outbox (status);
CREATE INDEX IF NOT EXISTS idx_outbox_created ON odoo_action_outbox (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_outbox_correlation ON odoo_action_outbox (correlation_id);

-- RLS: read for authenticated, write only via edge/service role
ALTER TABLE audit_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE odoo_action_outbox ENABLE ROW LEVEL SECURITY;

-- Policies for audit_event
DROP POLICY IF EXISTS audit_event_read ON audit_event;
CREATE POLICY audit_event_read ON audit_event
  FOR SELECT
  USING (auth.role() IN ('authenticated','service_role'));

DROP POLICY IF EXISTS audit_event_insert_edge ON audit_event;
CREATE POLICY audit_event_insert_edge ON audit_event
  FOR INSERT
  TO PUBLIC
  WITH CHECK (auth.role() = 'service_role');

-- Policies for outbox
DROP POLICY IF EXISTS outbox_read_sr ON odoo_action_outbox;
CREATE POLICY outbox_read_sr ON odoo_action_outbox
  FOR SELECT
  USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS outbox_write_sr ON odoo_action_outbox;
CREATE POLICY outbox_write_sr ON odoo_action_outbox
  FOR INSERT
  WITH CHECK (auth.role() = 'service_role');

DROP POLICY IF EXISTS outbox_update_sr ON odoo_action_outbox;
CREATE POLICY outbox_update_sr ON odoo_action_outbox
  FOR UPDATE
  USING (auth.role() = 'service_role');

-- Comments for documentation
COMMENT ON TABLE audit_event IS 'Event log for all Odoo-Supabase bridge events';
COMMENT ON TABLE odoo_action_outbox IS 'Outbox queue for actions to be applied in Odoo';

COMMENT ON COLUMN audit_event.source IS 'Event source: odoo, supabase, or bridge';
COMMENT ON COLUMN audit_event.event_type IS 'Event type (e.g., res.partner.updated)';
COMMENT ON COLUMN audit_event.resource_id IS 'Resource ID (e.g., partner ID)';
COMMENT ON COLUMN audit_event.payload IS 'Event payload as JSON';
COMMENT ON COLUMN audit_event.correlation_id IS 'Correlation ID for tracking related events';

COMMENT ON COLUMN odoo_action_outbox.action IS 'Action to execute in Odoo (e.g., account.move.post)';
COMMENT ON COLUMN odoo_action_outbox.args IS 'Action arguments as JSON';
COMMENT ON COLUMN odoo_action_outbox.status IS 'Action status: queued, sent, applied, or error';
COMMENT ON COLUMN odoo_action_outbox.last_error IS 'Last error message if status is error';

-- Realtime: Enable publication for audit_event table
-- Note: In Supabase Studio/GUI, also enable Realtime on the schema/table
-- ALTER PUBLICATION supabase_realtime ADD TABLE audit_event;
