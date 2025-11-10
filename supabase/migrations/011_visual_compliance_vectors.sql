-- Visual Compliance Agent - RAG/CAG Knowledge Graph with Vector Embeddings
-- Date: 2025-11-10
-- Purpose: Vector-based knowledge graph for OCA compliance validation

-- ===========================================================================
-- 1. ENABLE PGVECTOR EXTENSION
-- ===========================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ===========================================================================
-- 2. OCA GUIDELINES TABLE (Canonical Compliance Rules)
-- ===========================================================================

CREATE TABLE IF NOT EXISTS oca_guidelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Content identification
    repository TEXT NOT NULL,  -- 'OCA/maintainer-tools', 'OCA/odoo-community.org', etc.
    doc_path TEXT NOT NULL,  -- Path within repository
    section TEXT NOT NULL,  -- Section name (e.g., 'Module Manifest', 'Python Guidelines')
    url TEXT NOT NULL,  -- GitHub URL to specific section

    -- Raw content
    content_type TEXT NOT NULL CHECK (content_type IN ('markdown', 'rst', 'python', 'xml')),
    raw_content TEXT NOT NULL,
    content_hash TEXT NOT NULL,  -- SHA-256 hash for deduplication

    -- Hierarchical chunking
    parent_chunk_id UUID REFERENCES oca_guidelines(id) ON DELETE CASCADE,
    chunk_index INTEGER DEFAULT 0,
    chunk_total INTEGER DEFAULT 1,

    -- Vector embedding (text-embedding-3-large, 3072 dimensions)
    embedding vector(3072),

    -- Compliance metadata
    compliance_category TEXT NOT NULL CHECK (compliance_category IN (
        'manifest', 'python', 'xml', 'security', 'structure', 'dependencies', 'tools'
    )),
    severity TEXT NOT NULL CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    auto_fixable BOOLEAN DEFAULT FALSE,

    -- Deduplication tracking
    canonical_url TEXT,  -- URL to canonical source if this is a duplicate
    similarity_score FLOAT,  -- Cosine similarity to canonical (if duplicate)

    -- Timestamps
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_validated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(repository, doc_path, section, chunk_index),
    UNIQUE(content_hash)
);

-- ===========================================================================
-- 3. ODOO OFFICIAL DOCS TABLE (Odoo 18.0 Documentation)
-- ===========================================================================

CREATE TABLE IF NOT EXISTS odoo_official_docs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Content identification
    doc_section TEXT NOT NULL,  -- 'developer', 'applications', 'administration'
    doc_category TEXT NOT NULL,  -- 'manifests', 'orm', 'views', 'security', etc.
    title TEXT NOT NULL,
    url TEXT NOT NULL,

    -- Raw content
    content_type TEXT NOT NULL CHECK (content_type IN ('markdown', 'rst', 'html')),
    raw_content TEXT NOT NULL,
    content_hash TEXT NOT NULL,

    -- Hierarchical chunking
    parent_chunk_id UUID REFERENCES odoo_official_docs(id) ON DELETE CASCADE,
    chunk_index INTEGER DEFAULT 0,
    chunk_total INTEGER DEFAULT 1,

    -- Vector embedding (text-embedding-3-large, 3072 dimensions)
    embedding vector(3072),

    -- Odoo version specificity
    odoo_version TEXT NOT NULL DEFAULT '18.0',
    applies_to_ce BOOLEAN DEFAULT TRUE,
    applies_to_enterprise BOOLEAN DEFAULT FALSE,

    -- Deduplication tracking
    canonical_url TEXT,
    similarity_score FLOAT,

    -- Timestamps
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_validated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(url, chunk_index),
    UNIQUE(content_hash)
);

-- ===========================================================================
-- 4. COMPLIANCE VIOLATIONS TABLE (Detected Issues)
-- ===========================================================================

CREATE TABLE IF NOT EXISTS compliance_violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Session tracking
    session_id UUID NOT NULL,

    -- Violation details
    violation_type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    description TEXT NOT NULL,

    -- Module context
    module_name TEXT NOT NULL,
    module_path TEXT NOT NULL,
    file_path TEXT,
    line_number INTEGER,

    -- RAG context (what guidelines were used)
    relevant_guideline_ids UUID[],  -- References to oca_guidelines
    relevant_doc_ids UUID[],  -- References to odoo_official_docs

    -- LLM enhancement
    llm_suggestion TEXT,  -- GPT-4o-mini enhanced explanation
    auto_fixable BOOLEAN DEFAULT FALSE,
    fix_command TEXT,  -- Suggested fix command

    -- Migration complexity
    migration_complexity TEXT CHECK (migration_complexity IN ('LOW', 'MEDIUM', 'HIGH')),
    estimated_hours FLOAT,

    -- Resolution tracking
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'wont_fix', 'duplicate')),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================================================================
-- 5. OCA MODULE EXAMPLES TABLE (Code Examples from OCA Repos)
-- ===========================================================================

CREATE TABLE IF NOT EXISTS oca_module_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Module identification
    oca_repository TEXT NOT NULL,  -- 'OCA/account-financial-reporting', etc.
    module_name TEXT NOT NULL,
    odoo_version TEXT NOT NULL,

    -- Example details
    example_type TEXT NOT NULL CHECK (example_type IN (
        'model', 'view', 'controller', 'wizard', 'report', 'security', 'data', 'test'
    )),
    file_path TEXT NOT NULL,
    code_snippet TEXT NOT NULL,
    code_hash TEXT NOT NULL,

    -- Context
    description TEXT,
    usage_pattern TEXT,  -- How this pattern is commonly used

    -- Vector embedding (for code similarity search)
    embedding vector(3072),

    -- Quality metrics
    stars INTEGER DEFAULT 0,  -- Repository stars (proxy for quality)
    forks INTEGER DEFAULT 0,
    last_commit_date TIMESTAMP WITH TIME ZONE,

    -- Deduplication tracking
    canonical_example_id UUID REFERENCES oca_module_examples(id) ON DELETE SET NULL,
    similarity_score FLOAT,

    -- Timestamps
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    UNIQUE(oca_repository, module_name, file_path),
    UNIQUE(code_hash)
);

-- ===========================================================================
-- 6. COMPLIANCE SESSIONS TABLE (Validation Session Tracking)
-- ===========================================================================

CREATE TABLE IF NOT EXISTS compliance_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Session metadata
    session_type TEXT NOT NULL CHECK (session_type IN (
        'full_scan', 'incremental', 'skill_execution', 'ci_validation'
    )),
    trigger_source TEXT NOT NULL CHECK (trigger_source IN (
        'manual', 'github_action', 'pre_commit', 'skill_invocation', 'scheduled'
    )),

    -- Scope
    repository_path TEXT NOT NULL,
    modules_scanned TEXT[],
    skills_executed TEXT[],  -- Which skills from skills.yaml were run

    -- Results summary
    total_modules INTEGER DEFAULT 0,
    compliant_modules INTEGER DEFAULT 0,
    total_violations INTEGER DEFAULT 0,
    critical_violations INTEGER DEFAULT 0,
    high_violations INTEGER DEFAULT 0,
    medium_violations INTEGER DEFAULT 0,
    low_violations INTEGER DEFAULT 0,
    auto_fixable_violations INTEGER DEFAULT 0,

    -- RAG/CAG metrics
    guidelines_retrieved INTEGER DEFAULT 0,  -- How many OCA guidelines were queried
    docs_retrieved INTEGER DEFAULT 0,  -- How many Odoo docs were queried
    avg_retrieval_time_ms FLOAT,
    llm_enhancement_used BOOLEAN DEFAULT FALSE,

    -- Execution metadata
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds FLOAT GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (completed_at - started_at))
    ) STORED,

    -- Error tracking
    status TEXT DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================================================================
-- 7. INDEXES FOR PERFORMANCE
-- ===========================================================================

-- OCA Guidelines indexes
CREATE INDEX IF NOT EXISTS idx_oca_guidelines_repository ON oca_guidelines(repository);
CREATE INDEX IF NOT EXISTS idx_oca_guidelines_category ON oca_guidelines(compliance_category);
CREATE INDEX IF NOT EXISTS idx_oca_guidelines_severity ON oca_guidelines(severity);
CREATE INDEX IF NOT EXISTS idx_oca_guidelines_hash ON oca_guidelines(content_hash);
CREATE INDEX IF NOT EXISTS idx_oca_guidelines_canonical ON oca_guidelines(canonical_url) WHERE canonical_url IS NOT NULL;

-- Odoo Official Docs indexes
CREATE INDEX IF NOT EXISTS idx_odoo_docs_section ON odoo_official_docs(doc_section);
CREATE INDEX IF NOT EXISTS idx_odoo_docs_category ON odoo_official_docs(doc_category);
CREATE INDEX IF NOT EXISTS idx_odoo_docs_version ON odoo_official_docs(odoo_version);
CREATE INDEX IF NOT EXISTS idx_odoo_docs_hash ON odoo_official_docs(content_hash);
CREATE INDEX IF NOT EXISTS idx_odoo_docs_canonical ON odoo_official_docs(canonical_url) WHERE canonical_url IS NOT NULL;

-- Compliance Violations indexes
CREATE INDEX IF NOT EXISTS idx_violations_session ON compliance_violations(session_id);
CREATE INDEX IF NOT EXISTS idx_violations_module ON compliance_violations(module_name);
CREATE INDEX IF NOT EXISTS idx_violations_severity ON compliance_violations(severity);
CREATE INDEX IF NOT EXISTS idx_violations_status ON compliance_violations(status);
CREATE INDEX IF NOT EXISTS idx_violations_type ON compliance_violations(violation_type);

-- OCA Module Examples indexes
CREATE INDEX IF NOT EXISTS idx_oca_examples_repo ON oca_module_examples(oca_repository);
CREATE INDEX IF NOT EXISTS idx_oca_examples_module ON oca_module_examples(module_name);
CREATE INDEX IF NOT EXISTS idx_oca_examples_type ON oca_module_examples(example_type);
CREATE INDEX IF NOT EXISTS idx_oca_examples_hash ON oca_module_examples(code_hash);
CREATE INDEX IF NOT EXISTS idx_oca_examples_stars ON oca_module_examples(stars DESC);

-- Compliance Sessions indexes
CREATE INDEX IF NOT EXISTS idx_sessions_type ON compliance_sessions(session_type);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON compliance_sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_trigger ON compliance_sessions(trigger_source);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON compliance_sessions(started_at DESC);

-- ===========================================================================
-- 8. VECTOR SIMILARITY INDEXES (IVFFLAT)
-- ===========================================================================

-- OCA Guidelines vector index (approximate nearest neighbor search)
-- Using 100 lists for ~10K-100K rows (adjust based on expected data size)
CREATE INDEX IF NOT EXISTS idx_oca_guidelines_embedding ON oca_guidelines
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Odoo Official Docs vector index
CREATE INDEX IF NOT EXISTS idx_odoo_docs_embedding ON odoo_official_docs
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- OCA Module Examples vector index (for code similarity)
CREATE INDEX IF NOT EXISTS idx_oca_examples_embedding ON oca_module_examples
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 50);

-- ===========================================================================
-- 9. TRIGGERS FOR AUTOMATIC UPDATES
-- ===========================================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_oca_guidelines_updated_at
    BEFORE UPDATE ON oca_guidelines
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_odoo_docs_updated_at
    BEFORE UPDATE ON odoo_official_docs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_violations_updated_at
    BEFORE UPDATE ON compliance_violations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_oca_examples_updated_at
    BEFORE UPDATE ON oca_module_examples
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON compliance_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===========================================================================
-- 10. ROW-LEVEL SECURITY
-- ===========================================================================

-- Enable RLS on all tables
ALTER TABLE oca_guidelines ENABLE ROW LEVEL SECURITY;
ALTER TABLE odoo_official_docs ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_violations ENABLE ROW LEVEL SECURITY;
ALTER TABLE oca_module_examples ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_sessions ENABLE ROW LEVEL SECURITY;

-- Allow all for authenticated users (service role for Celery workers)
CREATE POLICY "Allow all for authenticated" ON oca_guidelines FOR ALL TO authenticated USING (true);
CREATE POLICY "Allow all for authenticated" ON odoo_official_docs FOR ALL TO authenticated USING (true);
CREATE POLICY "Allow all for authenticated" ON compliance_violations FOR ALL TO authenticated USING (true);
CREATE POLICY "Allow all for authenticated" ON oca_module_examples FOR ALL TO authenticated USING (true);
CREATE POLICY "Allow all for authenticated" ON compliance_sessions FOR ALL TO authenticated USING (true);

-- Allow read-only for anon (public knowledge base access)
CREATE POLICY "Allow read for anon" ON oca_guidelines FOR SELECT TO anon USING (true);
CREATE POLICY "Allow read for anon" ON odoo_official_docs FOR SELECT TO anon USING (true);
CREATE POLICY "Allow read for anon" ON oca_module_examples FOR SELECT TO anon USING (true);

-- ===========================================================================
-- 11. RPC FUNCTIONS FOR VECTOR SEARCH
-- ===========================================================================

-- Function: Search OCA guidelines using vector similarity
CREATE OR REPLACE FUNCTION search_oca_guidelines(
    query_embedding vector(3072),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    category_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    repository TEXT,
    section TEXT,
    content TEXT,
    url TEXT,
    compliance_category TEXT,
    severity TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        g.id,
        g.repository,
        g.section,
        g.raw_content AS content,
        g.url,
        g.compliance_category,
        g.severity,
        1 - (g.embedding <=> query_embedding) AS similarity
    FROM oca_guidelines g
    WHERE g.canonical_url IS NULL  -- Exclude duplicates
      AND (category_filter IS NULL OR g.compliance_category = category_filter)
      AND 1 - (g.embedding <=> query_embedding) >= match_threshold
    ORDER BY g.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Search Odoo official docs using vector similarity
CREATE OR REPLACE FUNCTION search_odoo_docs(
    query_embedding vector(3072),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    section_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    doc_section TEXT,
    doc_category TEXT,
    title TEXT,
    content TEXT,
    url TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.doc_section,
        d.doc_category,
        d.title,
        d.raw_content AS content,
        d.url,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM odoo_official_docs d
    WHERE d.canonical_url IS NULL  -- Exclude duplicates
      AND (section_filter IS NULL OR d.doc_section = section_filter)
      AND 1 - (d.embedding <=> query_embedding) >= match_threshold
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Search OCA module examples (code similarity)
CREATE OR REPLACE FUNCTION search_oca_examples(
    query_embedding vector(3072),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    example_type_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    oca_repository TEXT,
    module_name TEXT,
    example_type TEXT,
    code_snippet TEXT,
    description TEXT,
    stars INTEGER,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.oca_repository,
        e.module_name,
        e.example_type,
        e.code_snippet,
        e.description,
        e.stars,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM oca_module_examples e
    WHERE e.canonical_example_id IS NULL  -- Exclude duplicates
      AND (example_type_filter IS NULL OR e.example_type = example_type_filter)
      AND 1 - (e.embedding <=> query_embedding) >= match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Get compliance session stats
CREATE OR REPLACE FUNCTION get_compliance_stats(
    session_id_param UUID DEFAULT NULL
)
RETURNS TABLE (
    total_sessions BIGINT,
    avg_duration_seconds FLOAT,
    total_violations BIGINT,
    avg_guidelines_retrieved FLOAT,
    avg_docs_retrieved FLOAT,
    auto_fix_rate FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT AS total_sessions,
        AVG(duration_seconds)::FLOAT AS avg_duration_seconds,
        SUM(s.total_violations)::BIGINT AS total_violations,
        AVG(s.guidelines_retrieved)::FLOAT AS avg_guidelines_retrieved,
        AVG(s.docs_retrieved)::FLOAT AS avg_docs_retrieved,
        CASE
            WHEN SUM(s.total_violations) > 0
            THEN (SUM(s.auto_fixable_violations)::FLOAT / SUM(s.total_violations))
            ELSE 0
        END AS auto_fix_rate
    FROM compliance_sessions s
    WHERE session_id_param IS NULL OR s.id = session_id_param;
END;
$$ LANGUAGE plpgsql;

-- ===========================================================================
-- 12. DEDUPLICATION FUNCTION
-- ===========================================================================

-- Function: Find and mark duplicate content using semantic similarity
CREATE OR REPLACE FUNCTION mark_duplicate_guidelines(
    similarity_threshold FLOAT DEFAULT 0.95
)
RETURNS TABLE (
    duplicate_id UUID,
    canonical_id UUID,
    similarity_score FLOAT
) AS $$
BEGIN
    -- Mark duplicates in oca_guidelines
    WITH duplicates AS (
        SELECT
            g1.id AS duplicate_id,
            g2.id AS canonical_id,
            1 - (g1.embedding <=> g2.embedding) AS similarity_score
        FROM oca_guidelines g1
        CROSS JOIN LATERAL (
            SELECT id, embedding
            FROM oca_guidelines g2
            WHERE g2.id < g1.id  -- Only compare with earlier IDs (canonical)
              AND g2.canonical_url IS NULL  -- Don't compare with duplicates
            ORDER BY g1.embedding <=> g2.embedding
            LIMIT 1
        ) g2
        WHERE g1.canonical_url IS NULL  -- Only process non-duplicates
          AND 1 - (g1.embedding <=> g2.embedding) >= similarity_threshold
    )
    UPDATE oca_guidelines g
    SET
        canonical_url = (SELECT url FROM oca_guidelines WHERE id = d.canonical_id),
        similarity_score = d.similarity_score
    FROM duplicates d
    WHERE g.id = d.duplicate_id
    RETURNING d.duplicate_id, d.canonical_id, d.similarity_score;
END;
$$ LANGUAGE plpgsql;

-- ===========================================================================
-- END OF MIGRATION
-- ===========================================================================

-- Verify migration
DO $$
BEGIN
    RAISE NOTICE 'Visual Compliance Agent RAG/CAG migration completed successfully';
    RAISE NOTICE 'Tables created: oca_guidelines, odoo_official_docs, compliance_violations, oca_module_examples, compliance_sessions';
    RAISE NOTICE 'Vector indexes created with IVFFLAT (lists=100)';
    RAISE NOTICE 'Functions created: search_oca_guidelines(), search_odoo_docs(), search_oca_examples(), get_compliance_stats(), mark_duplicate_guidelines()';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Start Celery workers: docker-compose up celery-ingestion celery-embedding';
    RAISE NOTICE '2. Ingest OCA guidelines: celery -A visual_compliance.celery_app call tasks.ingest_oca_repository';
    RAISE NOTICE '3. Generate embeddings: celery -A visual_compliance.celery_app call tasks.generate_embeddings';
    RAISE NOTICE '4. Run deduplication: SELECT * FROM mark_duplicate_guidelines(0.95);';
    RAISE NOTICE '5. Test vector search: SELECT * FROM search_oca_guidelines(query_embedding, 0.7, 5);';
END $$;
