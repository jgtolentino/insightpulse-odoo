-- Row Level Security Policies for Operations Tables

-- Enable RLS on all ops tables
ALTER TABLE ops_heartbeats ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops_webhook_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops_incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops_healing_actions ENABLE ROW LEVEL SECURITY;

-- Heartbeats: service_role can read/write
CREATE POLICY hb_service_role_all ON ops_heartbeats
  FOR ALL TO service_role
  USING (TRUE)
  WITH CHECK (TRUE);

-- Authenticated users can read their own service heartbeats
CREATE POLICY hb_read_own_service ON ops_heartbeats
  FOR SELECT TO authenticated
  USING (
    source = (current_setting('request.jwt.claims', TRUE)::JSON->>'sub')
    OR
    source IN ('synthetic_order_flow', 'edge', 'scheduled')  -- public sources
  );

-- Webhook Queue: service_role only
CREATE POLICY queue_service_role_all ON ops_webhook_queue
  FOR ALL TO service_role
  USING (TRUE)
  WITH CHECK (TRUE);

-- Incidents: service_role full access
CREATE POLICY incidents_service_role_all ON ops_incidents
  FOR ALL TO service_role
  USING (TRUE)
  WITH CHECK (TRUE);

-- Incidents: authenticated users can read
CREATE POLICY incidents_read_authenticated ON ops_incidents
  FOR SELECT TO authenticated
  USING (TRUE);

-- Healing Actions: service_role full access
CREATE POLICY healing_service_role_all ON ops_healing_actions
  FOR ALL TO service_role
  USING (TRUE)
  WITH CHECK (TRUE);

-- Healing Actions: authenticated users can read
CREATE POLICY healing_read_authenticated ON ops_healing_actions
  FOR SELECT TO authenticated
  USING (TRUE);

-- Additional security: Prevent anon access to sensitive tables
-- (anon role gets no policies, so access is denied by default)

-- Optionally, create a read-only role for monitoring dashboards
-- CREATE ROLE monitoring_read;
-- GRANT SELECT ON ops_heartbeats, ops_incidents, ops_healing_actions TO monitoring_read;
