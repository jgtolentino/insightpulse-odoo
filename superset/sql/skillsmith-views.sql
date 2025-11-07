-- Superset Dashboard Supporting Views
-- Creates necessary views and tables for skillsmith-unified-monitoring dashboard

-- ============================================================================
-- 1. CONFIDENCE TRACKING TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.confidence_updates (
    id BIGSERIAL PRIMARY KEY,
    skill_id TEXT NOT NULL,
    fingerprint UUID,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    hits_before INTEGER,
    hits_after INTEGER,
    confidence NUMERIC(4,3),
    action TEXT,
    reason TEXT,
    impact_ratio NUMERIC(6,2)
);

CREATE INDEX IF NOT EXISTS idx_confidence_updates_skill
    ON public.confidence_updates(skill_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_confidence_updates_timestamp
    ON public.confidence_updates(timestamp DESC);

-- ============================================================================
-- 2. TRM DATASET TRACKING TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.trm_dataset (
    id BIGSERIAL PRIMARY KEY,
    entry_id TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    kind TEXT NOT NULL,
    task TEXT,
    fingerprint UUID,
    confidence NUMERIC(4,3),
    hits_7d INTEGER,
    hits_30d INTEGER,
    impact_score NUMERIC(10,2),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trm_dataset_source
    ON public.trm_dataset(source, kind);

CREATE INDEX IF NOT EXISTS idx_trm_dataset_approved
    ON public.trm_dataset(approved_at DESC);

-- ============================================================================
-- 3. ERROR CATALOG TRACKING TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.error_catalog (
    code TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    severity TEXT,
    fingerprint UUID,
    hits_7d INTEGER DEFAULT 0,
    hits_30d INTEGER DEFAULT 0,
    active_guardrails JSONB,
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_error_catalog_severity
    ON public.error_catalog(severity, hits_7d DESC);

CREATE INDEX IF NOT EXISTS idx_error_catalog_category
    ON public.error_catalog(category);

-- ============================================================================
-- 4. SKILLS METADATA VIEW
-- ============================================================================

CREATE OR REPLACE VIEW public.skills_metadata AS
SELECT
    id,
    name,
    kind,
    status,
    priority,
    (match->>'fingerprint')::uuid as fingerprint,
    (metadata->>'confidence')::numeric(4,3) as confidence,
    (metadata->>'hits_7d')::integer as hits_7d,
    (metadata->>'hits_30d')::integer as hits_30d,
    (metadata->>'impact_score')::numeric(10,2) as impact_score,
    (metadata->>'auto_generated')::boolean as auto_generated,
    (metadata->>'last_updated')::timestamptz as last_updated
FROM (
    SELECT
        jsonb_build_object(
            'id', id,
            'name', name,
            'kind', kind,
            'status', status,
            'priority', priority,
            'match', match,
            'metadata', metadata
        ) as row_data
    FROM public.skills
) sub,
LATERAL jsonb_to_record(sub.row_data) AS x(
    id TEXT,
    name TEXT,
    kind TEXT,
    status TEXT,
    priority TEXT,
    match JSONB,
    metadata JSONB
);

-- ============================================================================
-- 5. CONFIDENCE HISTORY AGGREGATE VIEW
-- ============================================================================

CREATE OR REPLACE VIEW public.confidence_history_summary AS
SELECT
    skill_id,
    COUNT(*) as total_updates,
    AVG(confidence) as avg_confidence,
    MIN(confidence) as min_confidence,
    MAX(confidence) as max_confidence,
    SUM(CASE WHEN action = 'boosted' THEN 1 ELSE 0 END) as boost_count,
    SUM(CASE WHEN action = 'reduced' THEN 1 ELSE 0 END) as reduce_count,
    MAX(timestamp) as last_updated
FROM public.confidence_updates
GROUP BY skill_id;

-- ============================================================================
-- 6. ERROR IMPACT ANALYSIS VIEW
-- ============================================================================

CREATE OR REPLACE VIEW public.error_impact_analysis AS
SELECT
    es.fp,
    es.component,
    es.kind,
    es.norm_msg,
    es.hits_7d,
    es.hits_30d,
    (es.hits_7d * 0.7 + es.hits_30d * 0.3) as impact_score,
    CASE
        WHEN es.hits_7d > es.hits_30d / 4 THEN 'increasing'
        WHEN es.hits_7d < es.hits_30d / 5 THEN 'decreasing'
        ELSE 'stable'
    END as trend,
    COALESCE(sm.id, 'NONE') as skill_id,
    COALESCE(sm.kind, 'NONE') as skill_kind,
    COALESCE(sm.confidence, 0) as skill_confidence,
    CASE
        WHEN sm.id IS NOT NULL THEN true
        ELSE false
    END as has_guardrail
FROM public.error_signatures es
LEFT JOIN public.skills_metadata sm ON es.fp = sm.fingerprint
WHERE es.hits_7d > 0;

-- ============================================================================
-- 7. TRAINING PIPELINE STATS VIEW
-- ============================================================================

CREATE OR REPLACE VIEW public.training_pipeline_stats AS
SELECT
    COUNT(*) as total_examples,
    COUNT(CASE WHEN source = 'skillsmith-production' THEN 1 END) as skillsmith_count,
    COUNT(CASE WHEN source = 'forum' THEN 1 END) as forum_count,
    COUNT(CASE WHEN source = 'manual' THEN 1 END) as manual_count,
    COUNT(CASE WHEN kind = 'guardrail' THEN 1 END) as guardrail_count,
    COUNT(CASE WHEN kind = 'fixer' THEN 1 END) as fixer_count,
    AVG(confidence) as avg_confidence,
    SUM(impact_score) as total_impact,
    MAX(approved_at) as last_addition,
    COUNT(CASE WHEN approved_at > NOW() - INTERVAL '7 days' THEN 1 END) as added_last_7d
FROM public.trm_dataset;

-- ============================================================================
-- 8. CATALOG COVERAGE STATS VIEW
-- ============================================================================

CREATE OR REPLACE VIEW public.catalog_coverage_stats AS
SELECT
    COUNT(*) as total_patterns,
    COUNT(CASE WHEN active_guardrails IS NOT NULL
               AND jsonb_array_length(active_guardrails) > 0 THEN 1 END) as covered_patterns,
    ROUND(
        100.0 * COUNT(CASE WHEN active_guardrails IS NOT NULL
                           AND jsonb_array_length(active_guardrails) > 0 THEN 1 END)
        / NULLIF(COUNT(*), 0),
        1
    ) as coverage_pct,
    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_count,
    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_count,
    COUNT(CASE WHEN severity = 'medium' THEN 1 END) as medium_count,
    COUNT(CASE WHEN severity = 'low' THEN 1 END) as low_count,
    SUM(hits_7d) as total_hits_7d,
    SUM(hits_30d) as total_hits_30d
FROM public.error_catalog;

-- ============================================================================
-- 9. WEEKLY TREND ANALYSIS VIEW
-- ============================================================================

CREATE OR REPLACE VIEW public.weekly_trends AS
SELECT
    DATE_TRUNC('week', timestamp) as week,
    COUNT(DISTINCT skill_id) as active_skills,
    SUM(hits_after) as total_errors,
    AVG(confidence) as avg_confidence,
    COUNT(CASE WHEN action = 'boosted' THEN 1 END) as skills_improved,
    COUNT(CASE WHEN action = 'reduced' THEN 1 END) as skills_degraded
FROM public.confidence_updates
GROUP BY DATE_TRUNC('week', timestamp)
ORDER BY week DESC;

-- ============================================================================
-- 10. GRANT PERMISSIONS
-- ============================================================================

-- Grant read access to Superset service account
-- Adjust role name based on your setup
GRANT SELECT ON public.confidence_updates TO superset_service;
GRANT SELECT ON public.trm_dataset TO superset_service;
GRANT SELECT ON public.error_catalog TO superset_service;
GRANT SELECT ON public.skills_metadata TO superset_service;
GRANT SELECT ON public.confidence_history_summary TO superset_service;
GRANT SELECT ON public.error_impact_analysis TO superset_service;
GRANT SELECT ON public.training_pipeline_stats TO superset_service;
GRANT SELECT ON public.catalog_coverage_stats TO superset_service;
GRANT SELECT ON public.weekly_trends TO superset_service;

-- Also grant on base tables used by views
GRANT SELECT ON public.error_signatures TO superset_service;
GRANT SELECT ON public.skills TO superset_service;

-- ============================================================================
-- SETUP COMPLETE
-- ============================================================================

-- Refresh materialized view
REFRESH MATERIALIZED VIEW public.error_signatures;

-- Verify setup
SELECT
    'confidence_updates' as table_name,
    COUNT(*) as row_count
FROM public.confidence_updates
UNION ALL
SELECT
    'trm_dataset',
    COUNT(*)
FROM public.trm_dataset
UNION ALL
SELECT
    'error_catalog',
    COUNT(*)
FROM public.error_catalog
UNION ALL
SELECT
    'error_signatures',
    COUNT(*)
FROM public.error_signatures;
