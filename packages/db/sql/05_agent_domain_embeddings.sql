-- Agent Domain-Specific Embeddings for Multi-Agent Knowledge Base
-- Extension to existing scout schema for agent-specific RAG retrieval
--
-- Apply with:
-- psql "$POSTGRES_URL" -f packages/db/sql/05_agent_domain_embeddings.sql

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create agent domain embeddings table
CREATE TABLE IF NOT EXISTS scout.agent_domain_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_domain TEXT NOT NULL CHECK (agent_domain IN ('odoo_developer', 'finance_ssc_expert', 'bi_architect', 'devops_engineer', 'orchestrator')),
    document_id UUID, -- Foreign key to scout.bir_documents if applicable
    content_type TEXT NOT NULL CHECK (content_type IN ('odoo_doc', 'bir_regulation', 'superset_doc', 'infra_doc', 'oca_guideline', 'general')),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI text-embedding-3-small
    metadata JSONB DEFAULT '{}',
    source_url TEXT,
    indexed_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for efficient similarity search
CREATE INDEX IF NOT EXISTS idx_agent_domain_embeddings_agent
    ON scout.agent_domain_embeddings(agent_domain);

CREATE INDEX IF NOT EXISTS idx_agent_domain_embeddings_content_type
    ON scout.agent_domain_embeddings(content_type);

CREATE INDEX IF NOT EXISTS idx_agent_domain_embeddings_vector
    ON scout.agent_domain_embeddings USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Create GIN index for metadata search
CREATE INDEX IF NOT EXISTS idx_agent_domain_embeddings_metadata
    ON scout.agent_domain_embeddings USING gin (metadata);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION scout.update_agent_domain_embeddings_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_agent_domain_embeddings_timestamp
    ON scout.agent_domain_embeddings;

CREATE TRIGGER trigger_update_agent_domain_embeddings_timestamp
    BEFORE UPDATE ON scout.agent_domain_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION scout.update_agent_domain_embeddings_timestamp();

-- Create function for agent-specific similarity search
CREATE OR REPLACE FUNCTION scout.search_agent_knowledge(
    p_agent_domain TEXT,
    p_query_embedding vector(1536),
    p_match_threshold FLOAT DEFAULT 0.7,
    p_match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    content TEXT,
    content_type TEXT,
    similarity FLOAT,
    metadata JSONB,
    source_url TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ade.id,
        ade.title,
        ade.content,
        ade.content_type,
        1 - (ade.embedding <=> p_query_embedding) AS similarity,
        ade.metadata,
        ade.source_url
    FROM scout.agent_domain_embeddings ade
    WHERE ade.agent_domain = p_agent_domain
        AND 1 - (ade.embedding <=> p_query_embedding) > p_match_threshold
    ORDER BY ade.embedding <=> p_query_embedding
    LIMIT p_match_count;
END;
$$ LANGUAGE plpgsql;

-- Create function for cross-agent knowledge search
CREATE OR REPLACE FUNCTION scout.search_all_agent_knowledge(
    p_query_embedding vector(1536),
    p_match_threshold FLOAT DEFAULT 0.7,
    p_match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    agent_domain TEXT,
    title TEXT,
    content TEXT,
    content_type TEXT,
    similarity FLOAT,
    metadata JSONB,
    source_url TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ade.id,
        ade.agent_domain,
        ade.title,
        ade.content,
        ade.content_type,
        1 - (ade.embedding <=> p_query_embedding) AS similarity,
        ade.metadata,
        ade.source_url
    FROM scout.agent_domain_embeddings ade
    WHERE 1 - (ade.embedding <=> p_query_embedding) > p_match_threshold
    ORDER BY ade.embedding <=> p_query_embedding
    LIMIT p_match_count;
END;
$$ LANGUAGE plpgsql;

-- Create view for agent knowledge statistics
CREATE OR REPLACE VIEW scout.agent_knowledge_stats AS
SELECT
    agent_domain,
    content_type,
    COUNT(*) AS document_count,
    MAX(indexed_at) AS last_indexed,
    COUNT(DISTINCT EXTRACT(MONTH FROM indexed_at)) AS months_active
FROM scout.agent_domain_embeddings
GROUP BY agent_domain, content_type
ORDER BY agent_domain, content_type;

-- Insert sample seed data for testing
INSERT INTO scout.agent_domain_embeddings (agent_domain, content_type, title, content, metadata, source_url)
VALUES
    (
        'odoo_developer',
        'oca_guideline',
        'OCA Module Structure Guidelines',
        'All Odoo modules must follow OCA structure: __init__.py, __manifest__.py, models/, views/, security/, data/, static/, i18n/. Use AGPL-3 license only.',
        '{"version": "19.0", "category": "guidelines"}',
        'https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst'
    ),
    (
        'finance_ssc_expert',
        'bir_regulation',
        'BIR Form 1601-C Filing Requirements',
        'Monthly Remittance Return of Income Taxes Withheld on Compensation. Due on 10th day of month following tax period. Requires quarterly alphalist (SAWT) submission.',
        '{"form": "1601-C", "frequency": "monthly", "deadline_day": 10}',
        'https://www.bir.gov.ph/index.php/tax-information/withholding-tax.html'
    ),
    (
        'bi_architect',
        'superset_doc',
        'Superset Row-Level Security (RLS) Configuration',
        'RLS in Superset restricts data access per user. Define base and regular filters using Jinja templates. Apply to datasets for multi-tenancy.',
        '{"version": "3.0", "feature": "RLS"}',
        'https://superset.apache.org/docs/security#row-level-security'
    ),
    (
        'devops_engineer',
        'infra_doc',
        'DigitalOcean App Platform Zero-Downtime Deployments',
        'App Platform performs rolling updates by default. Configure health checks at /health endpoint. Use --force-rebuild for fresh deployments.',
        '{"platform": "DO App Platform", "feature": "deployments"}',
        'https://docs.digitalocean.com/products/app-platform/how-to/manage-deployments/'
    );

-- Note: Actual embeddings need to be generated using OpenAI API
-- Run scripts/index_agent_knowledge.py after applying this migration

COMMENT ON TABLE scout.agent_domain_embeddings IS 'Agent-specific knowledge base for RAG retrieval in multi-agent orchestrator system';
COMMENT ON FUNCTION scout.search_agent_knowledge IS 'Search knowledge base for specific agent domain using cosine similarity';
COMMENT ON FUNCTION scout.search_all_agent_knowledge IS 'Search across all agent domains for cross-agent knowledge discovery';
