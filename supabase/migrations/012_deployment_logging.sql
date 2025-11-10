-- Migration: 012_deployment_logging.sql
-- Purpose: Create deployment and integration test logging tables
-- Date: 2025-11-10
-- Required for: integration-tests.yml, deploy-mcp.yml, ai-training.yml workflows

-- =============================================================================
-- DEPLOYMENT LOGS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.deployment_logs (
    id BIGSERIAL PRIMARY KEY,
    service TEXT NOT NULL,
    environment TEXT NOT NULL CHECK (environment IN ('production', 'staging', 'development')),
    status TEXT NOT NULL CHECK (status IN ('success', 'failure', 'pending', 'cancelled')),
    commit_sha TEXT NOT NULL,
    commit_message TEXT,
    deployed_by TEXT NOT NULL,
    deployed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deployment_duration_seconds INTEGER,
    build_logs JSONB,
    error_message TEXT,
    rollback_available BOOLEAN DEFAULT TRUE,
    previous_deployment_id BIGINT REFERENCES public.deployment_logs(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for deployment_logs
CREATE INDEX IF NOT EXISTS idx_deployment_logs_service ON public.deployment_logs(service);
CREATE INDEX IF NOT EXISTS idx_deployment_logs_environment ON public.deployment_logs(environment);
CREATE INDEX IF NOT EXISTS idx_deployment_logs_status ON public.deployment_logs(status);
CREATE INDEX IF NOT EXISTS idx_deployment_logs_deployed_at ON public.deployment_logs(deployed_at DESC);
CREATE INDEX IF NOT EXISTS idx_deployment_logs_commit_sha ON public.deployment_logs(commit_sha);
CREATE INDEX IF NOT EXISTS idx_deployment_logs_service_env ON public.deployment_logs(service, environment);

-- Enable Row Level Security
ALTER TABLE public.deployment_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for deployment_logs
CREATE POLICY "Allow public read access to deployment logs"
    ON public.deployment_logs FOR SELECT
    USING (true);

CREATE POLICY "Allow service role full access to deployment logs"
    ON public.deployment_logs FOR ALL
    USING (auth.role() = 'service_role');

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_deployment_logs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_deployment_logs_updated_at
    BEFORE UPDATE ON public.deployment_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_deployment_logs_updated_at();

-- =============================================================================
-- INTEGRATION TEST LOGS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.integration_test_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    environment TEXT NOT NULL CHECK (environment IN ('production', 'staging', 'development')),
    test_suite TEXT NOT NULL,
    test_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('passed', 'failed', 'skipped', 'error')),
    duration_ms INTEGER,
    services JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_message TEXT,
    error_stack TEXT,
    commit TEXT,
    workflow_run_id TEXT,
    test_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for integration_test_logs
CREATE INDEX IF NOT EXISTS idx_integration_test_logs_timestamp ON public.integration_test_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_integration_test_logs_environment ON public.integration_test_logs(environment);
CREATE INDEX IF NOT EXISTS idx_integration_test_logs_test_suite ON public.integration_test_logs(test_suite);
CREATE INDEX IF NOT EXISTS idx_integration_test_logs_status ON public.integration_test_logs(status);
CREATE INDEX IF NOT EXISTS idx_integration_test_logs_commit ON public.integration_test_logs(commit);
CREATE INDEX IF NOT EXISTS idx_integration_test_logs_workflow_run_id ON public.integration_test_logs(workflow_run_id);

-- Enable Row Level Security
ALTER TABLE public.integration_test_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for integration_test_logs
CREATE POLICY "Allow public read access to integration test logs"
    ON public.integration_test_logs FOR SELECT
    USING (true);

CREATE POLICY "Allow service role full access to integration test logs"
    ON public.integration_test_logs FOR ALL
    USING (auth.role() = 'service_role');

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Function to get latest deployment for a service
CREATE OR REPLACE FUNCTION get_latest_deployment(service_name TEXT, env TEXT DEFAULT 'production')
RETURNS TABLE (
    id BIGINT,
    service TEXT,
    environment TEXT,
    status TEXT,
    commit_sha TEXT,
    deployed_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        dl.id,
        dl.service,
        dl.environment,
        dl.status,
        dl.commit_sha,
        dl.deployed_at
    FROM public.deployment_logs dl
    WHERE dl.service = service_name
      AND dl.environment = env
    ORDER BY dl.deployed_at DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get test success rate
CREATE OR REPLACE FUNCTION get_test_success_rate(
    test_suite_name TEXT DEFAULT NULL,
    hours_back INTEGER DEFAULT 24
)
RETURNS TABLE (
    test_suite TEXT,
    total_tests BIGINT,
    passed_tests BIGINT,
    failed_tests BIGINT,
    success_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        itl.test_suite,
        COUNT(*)::BIGINT AS total_tests,
        COUNT(*) FILTER (WHERE itl.status = 'passed')::BIGINT AS passed_tests,
        COUNT(*) FILTER (WHERE itl.status = 'failed')::BIGINT AS failed_tests,
        ROUND(
            (COUNT(*) FILTER (WHERE itl.status = 'passed')::NUMERIC / NULLIF(COUNT(*), 0)) * 100,
            2
        ) AS success_rate
    FROM public.integration_test_logs itl
    WHERE (test_suite_name IS NULL OR itl.test_suite = test_suite_name)
      AND itl.timestamp > NOW() - (hours_back || ' hours')::INTERVAL
    GROUP BY itl.test_suite
    ORDER BY success_rate DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log deployment
CREATE OR REPLACE FUNCTION log_deployment(
    p_service TEXT,
    p_environment TEXT,
    p_status TEXT,
    p_commit_sha TEXT,
    p_commit_message TEXT DEFAULT NULL,
    p_deployed_by TEXT DEFAULT 'github-actions',
    p_deployment_duration INTEGER DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    v_deployment_id BIGINT;
BEGIN
    INSERT INTO public.deployment_logs (
        service,
        environment,
        status,
        commit_sha,
        commit_message,
        deployed_by,
        deployment_duration_seconds,
        error_message
    ) VALUES (
        p_service,
        p_environment,
        p_status,
        p_commit_sha,
        p_commit_message,
        p_deployed_by,
        p_deployment_duration,
        p_error_message
    )
    RETURNING id INTO v_deployment_id;

    RETURN v_deployment_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- SAMPLE DATA (for testing)
-- =============================================================================

-- Insert sample deployment log
INSERT INTO public.deployment_logs (
    service,
    environment,
    status,
    commit_sha,
    commit_message,
    deployed_by,
    deployed_at
) VALUES (
    'mcp-coordinator',
    'production',
    'success',
    'initial',
    'Initial deployment logging setup',
    'system',
    NOW()
) ON CONFLICT DO NOTHING;

-- Insert sample integration test log
INSERT INTO public.integration_test_logs (
    timestamp,
    environment,
    test_suite,
    test_name,
    status,
    duration_ms,
    services,
    commit,
    workflow_run_id
) VALUES (
    NOW(),
    'production',
    'integration-tests',
    'Service Health Checks',
    'passed',
    1500,
    '{"odoo": "success", "mcp": "success", "superset": "success"}'::jsonb,
    'initial',
    'setup-run'
) ON CONFLICT DO NOTHING;

-- =============================================================================
-- GRANTS
-- =============================================================================

-- Grant access to authenticated users
GRANT SELECT ON public.deployment_logs TO authenticated;
GRANT SELECT ON public.integration_test_logs TO authenticated;

-- Grant full access to service role
GRANT ALL ON public.deployment_logs TO service_role;
GRANT ALL ON public.integration_test_logs TO service_role;

-- Grant usage on sequences
GRANT USAGE, SELECT ON SEQUENCE public.deployment_logs_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE public.integration_test_logs_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.deployment_logs_id_seq TO service_role;
GRANT ALL ON SEQUENCE public.integration_test_logs_id_seq TO service_role;

-- Grant execute on functions
GRANT EXECUTE ON FUNCTION get_latest_deployment(TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION get_test_success_rate(TEXT, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION log_deployment(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT, INTEGER, TEXT) TO service_role;

COMMENT ON TABLE public.deployment_logs IS 'Deployment audit log for all services (MCP, Odoo, Superset, AI Training)';
COMMENT ON TABLE public.integration_test_logs IS 'Integration test results from GitHub Actions workflows';
COMMENT ON FUNCTION get_latest_deployment(TEXT, TEXT) IS 'Get the latest deployment record for a specific service and environment';
COMMENT ON FUNCTION get_test_success_rate(TEXT, INTEGER) IS 'Calculate test success rate for a test suite over specified time period';
COMMENT ON FUNCTION log_deployment(TEXT, TEXT, TEXT, TEXT, TEXT, TEXT, INTEGER, TEXT) IS 'Convenience function to log a deployment event';
