-- Process Intelligence Schema for Supabase/PostgreSQL
-- Stores SAP process events, analysis results, and forecasts

-- Create schema
CREATE SCHEMA IF NOT EXISTS pi;

-- Set search path
SET search_path TO pi, public;

-- Event traces table (raw SAP events)
CREATE TABLE IF NOT EXISTS pi.events (
    id BIGSERIAL PRIMARY KEY,
    process_id TEXT NOT NULL,
    process_type TEXT NOT NULL,
    case_id TEXT NOT NULL,
    activity TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    user_id TEXT,
    resource TEXT,
    lifecycle TEXT DEFAULT 'complete',
    duration_seconds NUMERIC,
    payload JSONB,
    metadata JSONB,
    source TEXT DEFAULT 'sap',
    system_id TEXT DEFAULT 'SAP_PROD',
    inserted_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS events_process_idx ON pi.events(process_id, process_type);
CREATE INDEX IF NOT EXISTS events_case_idx ON pi.events(case_id, event_time);
CREATE INDEX IF NOT EXISTS events_activity_idx ON pi.events(activity);
CREATE INDEX IF NOT EXISTS events_time_idx ON pi.events(event_time DESC);
CREATE INDEX IF NOT EXISTS events_metadata_idx ON pi.events USING GIN(metadata);

-- Process variants table
CREATE TABLE IF NOT EXISTS pi.variants (
    id BIGSERIAL PRIMARY KEY,
    process_id TEXT NOT NULL,
    process_type TEXT NOT NULL,
    total_cases INT NOT NULL,
    total_variants INT NOT NULL,
    conformance_rate NUMERIC(5,2),
    avg_case_duration_seconds NUMERIC,
    variant_summary JSONB NOT NULL,
    deviations JSONB DEFAULT '[]'::jsonb,
    computed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS variants_process_idx ON pi.variants(process_id, process_type);
CREATE INDEX IF NOT EXISTS variants_time_idx ON pi.variants(computed_at DESC);

-- Bottlenecks table
CREATE TABLE IF NOT EXISTS pi.bottlenecks (
    id BIGSERIAL PRIMARY KEY,
    process_id TEXT NOT NULL,
    process_type TEXT NOT NULL,
    activity TEXT NOT NULL,
    avg_wait_time_seconds NUMERIC NOT NULL,
    p90_wait_time_seconds NUMERIC NOT NULL,
    frequency INT NOT NULL,
    impact_score NUMERIC(5,2),
    root_cause_hypothesis TEXT,
    details JSONB,
    computed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS bottlenecks_process_idx ON pi.bottlenecks(process_id, process_type);
CREATE INDEX IF NOT EXISTS bottlenecks_activity_idx ON pi.bottlenecks(activity);
CREATE INDEX IF NOT EXISTS bottlenecks_impact_idx ON pi.bottlenecks(impact_score DESC);

-- KPI forecasts table
CREATE TABLE IF NOT EXISTS pi.kpi_forecasts (
    id BIGSERIAL PRIMARY KEY,
    process_id TEXT NOT NULL,
    process_type TEXT NOT NULL,
    kpi_type TEXT NOT NULL,
    predicted_value NUMERIC NOT NULL,
    confidence_lower NUMERIC,
    confidence_upper NUMERIC,
    confidence_score NUMERIC(5,2),
    model_version TEXT,
    risk_factors JSONB DEFAULT '[]'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,
    model_meta JSONB,
    computed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS forecasts_process_idx ON pi.kpi_forecasts(process_id, process_type);
CREATE INDEX IF NOT EXISTS forecasts_kpi_idx ON pi.kpi_forecasts(kpi_type);
CREATE INDEX IF NOT EXISTS forecasts_time_idx ON pi.kpi_forecasts(computed_at DESC);

-- Resource utilization table
CREATE TABLE IF NOT EXISTS pi.resource_utilization (
    id BIGSERIAL PRIMARY KEY,
    process_id TEXT NOT NULL,
    process_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    total_activities INT NOT NULL,
    avg_activity_duration_seconds NUMERIC,
    utilization_percentage NUMERIC(5,2),
    workload_distribution JSONB,
    computed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS resource_process_idx ON pi.resource_utilization(process_id, process_type);
CREATE INDEX IF NOT EXISTS resource_id_idx ON pi.resource_utilization(resource_id);

-- Process diagrams table
CREATE TABLE IF NOT EXISTS pi.diagrams (
    id BIGSERIAL PRIMARY KEY,
    process_id TEXT NOT NULL,
    process_type TEXT NOT NULL,
    diagram_format TEXT NOT NULL,
    diagram_url TEXT,
    local_path TEXT,
    statistics JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS diagrams_process_idx ON pi.diagrams(process_id, process_type);

-- Row Level Security (RLS)
ALTER TABLE pi.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE pi.variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE pi.bottlenecks ENABLE ROW LEVEL SECURITY;
ALTER TABLE pi.kpi_forecasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE pi.resource_utilization ENABLE ROW LEVEL SECURITY;
ALTER TABLE pi.diagrams ENABLE ROW LEVEL SECURITY;

-- Default policies (modify based on your tenancy model)
CREATE POLICY "Enable read access for authenticated users" ON pi.events
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON pi.variants
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON pi.bottlenecks
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON pi.kpi_forecasts
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON pi.resource_utilization
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON pi.diagrams
    FOR SELECT USING (auth.role() = 'authenticated');

-- Service role policies (for API inserts)
CREATE POLICY "Enable insert for service role" ON pi.events
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Enable insert for service role" ON pi.variants
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Enable insert for service role" ON pi.bottlenecks
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Enable insert for service role" ON pi.kpi_forecasts
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Enable insert for service role" ON pi.resource_utilization
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Enable insert for service role" ON pi.diagrams
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- Materialized views for Superset dashboards

-- P2P Conformance Trend
CREATE MATERIALIZED VIEW IF NOT EXISTS pi.mv_p2p_conformance_trend AS
SELECT
    DATE_TRUNC('day', computed_at) AS date,
    AVG(conformance_rate) AS avg_conformance_rate,
    COUNT(*) AS analysis_count
FROM pi.variants
WHERE process_type = 'PROCURE_TO_PAY'
GROUP BY DATE_TRUNC('day', computed_at)
ORDER BY date DESC;

CREATE INDEX ON pi.mv_p2p_conformance_trend(date DESC);

-- Bottleneck Hotspots
CREATE MATERIALIZED VIEW IF NOT EXISTS pi.mv_bottleneck_hotspots AS
SELECT
    activity,
    process_type,
    AVG(p90_wait_time_seconds) AS avg_p90_wait,
    AVG(impact_score) AS avg_impact_score,
    COUNT(*) AS occurrence_count,
    MAX(computed_at) AS last_detected
FROM pi.bottlenecks
GROUP BY activity, process_type
ORDER BY avg_impact_score DESC;

CREATE INDEX ON pi.mv_bottleneck_hotspots(avg_impact_score DESC);

-- Refresh function (call from cron)
CREATE OR REPLACE FUNCTION pi.refresh_materialized_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY pi.mv_p2p_conformance_trend;
    REFRESH MATERIALIZED VIEW CONCURRENTLY pi.mv_bottleneck_hotspots;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT USAGE ON SCHEMA pi TO authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA pi TO service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA pi TO authenticated;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA pi TO service_role;

COMMENT ON SCHEMA pi IS 'Process Intelligence: SAP process mining and analytics data';
COMMENT ON TABLE pi.events IS 'Raw SAP process event traces (IEEE XES compliant)';
COMMENT ON TABLE pi.variants IS 'Process variant analysis results';
COMMENT ON TABLE pi.bottlenecks IS 'Detected process bottlenecks with impact scores';
COMMENT ON TABLE pi.kpi_forecasts IS 'Predicted KPIs (throughput, delay, anomaly risk, cost)';
COMMENT ON TABLE pi.resource_utilization IS 'Resource and user utilization metrics';
COMMENT ON TABLE pi.diagrams IS 'Generated process diagrams (Draw.io, Mermaid, BPMN)';
