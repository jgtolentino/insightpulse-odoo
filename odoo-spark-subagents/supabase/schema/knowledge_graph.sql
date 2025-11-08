-- ============================================================================
-- Knowledge Graph Schema: Foundation for Exponential Automation Growth
-- ============================================================================
-- Purpose: Store and retrieve Odoo knowledge with semantic search
-- Impact: Enables agents to learn from community, docs, and past runs

-- Extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- 1. SKILLS LIBRARY (Auto-growing capability database)
-- ============================================================================

CREATE TABLE IF NOT EXISTS skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  category TEXT NOT NULL, -- 'odoo', 'git', 'automation', 'conflict'
  content TEXT NOT NULL, -- Full SKILL.md markdown
  embedding vector(3072), -- OpenAI text-embedding-3-large

  -- Learning metrics
  usage_count INT DEFAULT 0,
  success_count INT DEFAULT 0,
  failure_count INT DEFAULT 0,
  success_rate FLOAT GENERATED ALWAYS AS (
    CASE
      WHEN usage_count = 0 THEN 0.5
      ELSE success_count::FLOAT / usage_count
    END
  ) STORED,

  -- Provenance
  created_from_trace_id TEXT, -- OTEL trace that generated this skill
  parent_skill_id UUID REFERENCES skills(id), -- If evolved from another skill
  version INT DEFAULT 1,

  -- Metadata
  examples JSONB, -- Example inputs/outputs
  dependencies TEXT[], -- Required other skills
  tags TEXT[],

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deprecated_at TIMESTAMPTZ,
  deprecated_by UUID REFERENCES skills(id)
);

-- Index for vector similarity search
CREATE INDEX ON skills USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Index for active skills lookup
CREATE INDEX ON skills(category, deprecated_at)
  WHERE deprecated_at IS NULL;

-- Auto-update timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER skills_updated_at
  BEFORE UPDATE ON skills
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- 2. ODOO KNOWLEDGE BASE (Scraped docs, forum, issues)
-- ============================================================================

CREATE TABLE IF NOT EXISTS odoo_knowledge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type TEXT NOT NULL, -- 'docs', 'forum', 'github_issue', 'discussion'
  source_url TEXT NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  embedding vector(3072),

  -- Structured metadata
  odoo_version TEXT, -- '19.0', '18.0', etc.
  module_name TEXT, -- 'account', 'sale', etc.
  topic TEXT, -- 'migration', 'api', 'workflow', etc.

  -- Quality signals
  upvotes INT DEFAULT 0,
  is_solved BOOLEAN DEFAULT FALSE,
  solution_id UUID REFERENCES odoo_knowledge(id),

  -- Scraping metadata
  scraped_at TIMESTAMPTZ DEFAULT NOW(),
  last_updated TIMESTAMPTZ,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON odoo_knowledge USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX ON odoo_knowledge(source_type, odoo_version, is_solved);
CREATE INDEX ON odoo_knowledge(module_name) WHERE module_name IS NOT NULL;

-- Dedupe check: same URL shouldn't be indexed twice
CREATE UNIQUE INDEX ON odoo_knowledge(source_url);

-- ============================================================================
-- 3. ERROR KNOWLEDGE (Failures → Skills pipeline)
-- ============================================================================

CREATE TABLE IF NOT EXISTS error_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  error_signature TEXT NOT NULL, -- Normalized error message
  error_type TEXT NOT NULL, -- 'odoo_validation', 'python_exception', 'git_conflict', etc.

  -- Context
  agent_name TEXT, -- Which agent encountered this
  trace_id TEXT NOT NULL, -- OTEL trace
  context JSONB, -- Full error context

  -- Learning
  occurrences INT DEFAULT 1,
  first_seen TIMESTAMPTZ DEFAULT NOW(),
  last_seen TIMESTAMPTZ DEFAULT NOW(),

  -- Resolution
  resolved BOOLEAN DEFAULT FALSE,
  resolution_skill_id UUID REFERENCES skills(id),
  resolution_notes TEXT,
  resolved_at TIMESTAMPTZ,

  -- Embedding for similar error search
  embedding vector(3072),

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON error_patterns USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX ON error_patterns(error_type, resolved);
CREATE INDEX ON error_patterns(agent_name, resolved);

-- Dedupe: same signature → increment occurrences
CREATE UNIQUE INDEX ON error_patterns(error_signature);

-- ============================================================================
-- 4. AGENT EXECUTION HISTORY (Learning dataset)
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trace_id TEXT UNIQUE NOT NULL,
  agent_name TEXT NOT NULL,

  -- Input/Output
  input JSONB NOT NULL,
  plan JSONB,
  output JSONB,

  -- Outcome
  status TEXT NOT NULL, -- 'success', 'failure', 'partial'
  outcome_type TEXT, -- 'pr_created', 'tool_executed', 'conflict_detected'

  -- Human feedback (for RL training)
  human_approved BOOLEAN,
  human_feedback TEXT,
  approval_timestamp TIMESTAMPTZ,

  -- Performance
  duration_ms INT,
  confidence_score FLOAT,

  -- Skills used
  skills_used UUID[], -- Array of skill IDs

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON agent_runs(agent_name, status, human_approved);
CREATE INDEX ON agent_runs(created_at DESC);
CREATE INDEX ON agent_runs USING GIN(skills_used);

-- ============================================================================
-- 5. OCA COMPATIBILITY MATRIX (Conflict prevention)
-- ============================================================================

CREATE TABLE IF NOT EXISTS oca_module_compatibility (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Module combination
  modules TEXT[] NOT NULL, -- Sorted array of module names
  modules_hash TEXT GENERATED ALWAYS AS (md5(array_to_string(modules, ','))) STORED,

  -- Odoo version
  odoo_version TEXT NOT NULL,

  -- Test result
  compatible BOOLEAN NOT NULL,
  install_time_ms INT,
  test_output JSONB,

  -- Conflict details (if incompatible)
  conflict_type TEXT, -- 'dependency', 'python_version', 'data_conflict'
  conflict_details JSONB,

  -- Test metadata
  tested_at TIMESTAMPTZ DEFAULT NOW(),
  test_environment TEXT, -- 'docker', 'kubernetes', etc.

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX ON oca_module_compatibility(modules_hash, odoo_version);
CREATE INDEX ON oca_module_compatibility(compatible, odoo_version);
CREATE INDEX ON oca_module_compatibility USING GIN(modules);

-- ============================================================================
-- 6. MIGRATION PATTERNS (Migration intelligence)
-- ============================================================================

CREATE TABLE IF NOT EXISTS migration_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Version transition
  from_version TEXT NOT NULL,
  to_version TEXT NOT NULL,
  module_name TEXT,

  -- Pattern
  pattern_type TEXT NOT NULL, -- 'field_rename', 'model_rename', 'api_change', 'data_migration'
  pattern_description TEXT NOT NULL,

  -- Code
  before_code TEXT,
  after_code TEXT,
  migration_script TEXT,

  -- Metadata
  source_url TEXT, -- GitHub PR, forum post, etc.
  confidence FLOAT, -- How confident we are this pattern works
  usage_count INT DEFAULT 0,

  -- Embedding for similar pattern search
  embedding vector(3072),

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON migration_patterns USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE INDEX ON migration_patterns(from_version, to_version, pattern_type);
CREATE INDEX ON migration_patterns(module_name) WHERE module_name IS NOT NULL;

-- ============================================================================
-- 7. SEARCH FUNCTIONS (Semantic retrieval)
-- ============================================================================

-- Search skills by natural language query
CREATE OR REPLACE FUNCTION search_skills(
  query_embedding vector(3072),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 5
)
RETURNS TABLE (
  skill_id UUID,
  skill_name TEXT,
  skill_content TEXT,
  similarity FLOAT,
  success_rate FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    s.id,
    s.name,
    s.content,
    1 - (s.embedding <=> query_embedding) AS similarity,
    s.success_rate
  FROM skills s
  WHERE
    s.deprecated_at IS NULL
    AND 1 - (s.embedding <=> query_embedding) > match_threshold
  ORDER BY s.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Search Odoo knowledge
CREATE OR REPLACE FUNCTION search_odoo_knowledge(
  query_embedding vector(3072),
  target_version TEXT DEFAULT NULL,
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 10
)
RETURNS TABLE (
  knowledge_id UUID,
  title TEXT,
  content TEXT,
  source_url TEXT,
  similarity FLOAT,
  is_solved BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    ok.id,
    ok.title,
    ok.content,
    ok.source_url,
    1 - (ok.embedding <=> query_embedding) AS similarity,
    ok.is_solved
  FROM odoo_knowledge ok
  WHERE
    (target_version IS NULL OR ok.odoo_version = target_version)
    AND 1 - (ok.embedding <=> query_embedding) > match_threshold
  ORDER BY ok.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Search similar errors
CREATE OR REPLACE FUNCTION search_similar_errors(
  query_embedding vector(3072),
  match_threshold FLOAT DEFAULT 0.8,
  match_count INT DEFAULT 5
)
RETURNS TABLE (
  error_id UUID,
  error_signature TEXT,
  resolution_skill_id UUID,
  similarity FLOAT,
  occurrences INT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    ep.id,
    ep.error_signature,
    ep.resolution_skill_id,
    1 - (ep.embedding <=> query_embedding) AS similarity,
    ep.occurrences
  FROM error_patterns ep
  WHERE
    ep.resolved = TRUE
    AND 1 - (ep.embedding <=> query_embedding) > match_threshold
  ORDER BY ep.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 8. ANALYTICS VIEWS (Track exponential growth)
-- ============================================================================

CREATE OR REPLACE VIEW skill_growth_metrics AS
SELECT
  DATE_TRUNC('week', created_at) AS week,
  COUNT(*) AS new_skills,
  COUNT(*) FILTER (WHERE created_from_trace_id IS NOT NULL) AS auto_generated,
  ROUND(
    COUNT(*) FILTER (WHERE created_from_trace_id IS NOT NULL)::NUMERIC /
    NULLIF(COUNT(*), 0) * 100,
    2
  ) AS auto_generated_pct
FROM skills
GROUP BY week
ORDER BY week DESC;

CREATE OR REPLACE VIEW agent_improvement_metrics AS
SELECT
  agent_name,
  DATE_TRUNC('week', created_at) AS week,
  COUNT(*) AS total_runs,
  COUNT(*) FILTER (WHERE status = 'success') AS successes,
  ROUND(
    COUNT(*) FILTER (WHERE status = 'success')::NUMERIC /
    NULLIF(COUNT(*), 0) * 100,
    2
  ) AS success_rate_pct,
  AVG(confidence_score) AS avg_confidence
FROM agent_runs
GROUP BY agent_name, week
ORDER BY agent_name, week DESC;

CREATE OR REPLACE VIEW knowledge_growth_metrics AS
SELECT
  DATE_TRUNC('week', scraped_at) AS week,
  source_type,
  COUNT(*) AS documents_added,
  COUNT(DISTINCT module_name) AS modules_covered
FROM odoo_knowledge
GROUP BY week, source_type
ORDER BY week DESC, source_type;

-- ============================================================================
-- 9. ROW LEVEL SECURITY (Optional - for multi-tenant)
-- ============================================================================

-- Enable RLS
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE odoo_knowledge ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY service_role_all ON skills FOR ALL TO service_role USING (true);
CREATE POLICY service_role_all ON odoo_knowledge FOR ALL TO service_role USING (true);
CREATE POLICY service_role_all ON agent_runs FOR ALL TO service_role USING (true);

-- Allow anon to read public knowledge
CREATE POLICY anon_read_skills ON skills FOR SELECT TO anon USING (deprecated_at IS NULL);
CREATE POLICY anon_read_knowledge ON odoo_knowledge FOR SELECT TO anon USING (true);

-- ============================================================================
-- 10. INITIAL SEED DATA
-- ============================================================================

-- Seed with existing skills from index/seeds/skills.jsonl
INSERT INTO skills (name, category, content, tags) VALUES
  ('automation_executor', 'odoo', 'OpenAPI-first Odoo atomic tool invoker with dry-run default and idempotency keys.', ARRAY['odoo', 'api', 'tools']),
  ('git_specialist', 'git', 'Git sub-agent that prepares safe branches, commits and draft PRs with RL confidence and traceparent.', ARRAY['git', 'pr', 'safety']),
  ('automation_gap_analyzer', 'automation', 'Scans repo for CI/CD and quality gaps; emits a patch plan and routes to git-specialist to open a draft PR.', ARRAY['ci', 'automation', 'quality'])
ON CONFLICT (name) DO NOTHING;

COMMENT ON TABLE skills IS 'Self-improving library of agent capabilities. Grows through auto-harvesting from successful runs.';
COMMENT ON TABLE odoo_knowledge IS 'Continuously updated index of Odoo documentation, forum posts, and community knowledge.';
COMMENT ON TABLE error_patterns IS 'Error → Resolution knowledge base. Failures become preventive skills.';
COMMENT ON TABLE agent_runs IS 'Execution history for RL training. Human feedback creates ground truth for model improvement.';
COMMENT ON TABLE oca_module_compatibility IS 'Pre-computed compatibility matrix for OCA module combinations. Prevents conflicts before installation.';
COMMENT ON TABLE migration_patterns IS 'Learned patterns from successful Odoo version migrations. Enables automated upgrade suggestions.';
