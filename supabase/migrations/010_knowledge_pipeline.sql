-- Knowledge Pipeline Schema
-- Date: 2025-11-05
-- Purpose: Support knowledge scraping → RAG/Training pipeline

-- ===========================================================================
-- 1. MAIN KNOWLEDGE TABLES
-- ===========================================================================

-- Odoo Forum Threads Table
CREATE TABLE IF NOT EXISTS odoo_forum_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Content
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    question_text TEXT,
    question_code JSONB,  -- Array of code snippets
    accepted_answer JSONB,  -- {text, code, author, votes, answered_date}
    other_answers JSONB,  -- Array of answers
    tags TEXT[],

    -- Metrics
    views INTEGER DEFAULT 0,
    votes INTEGER DEFAULT 0,
    answer_count INTEGER DEFAULT 0,
    quality_score FLOAT DEFAULT 0,  -- Auto-calculated: 0-1 scale

    -- Processing flags
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_for_training BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Platform Documentation Table
CREATE TABLE IF NOT EXISTS platform_docs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Content
    platform TEXT NOT NULL,  -- 'docker', 'superset', 'supabase', 'odoo', 'digitalocean'
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    code_blocks JSONB,  -- Array of {language, code}

    -- Metrics
    content_length INTEGER GENERATED ALWAYS AS (length(content)) STORED,
    quality_score FLOAT DEFAULT 0,

    -- Processing flags
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_for_training BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- OCA GitHub Documentation Table
CREATE TABLE IF NOT EXISTS oca_github_docs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Content
    type TEXT NOT NULL CHECK (type IN ('readme', 'wiki', 'github_issue')),
    repo TEXT NOT NULL,  -- Full repo name: 'OCA/account-financial-reporting'
    title TEXT NOT NULL,
    content TEXT,
    question TEXT,  -- For issues
    answers JSONB,  -- For issues: array of comment texts
    url TEXT NOT NULL,
    labels TEXT[],

    -- Metrics
    stars INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    quality_score FLOAT DEFAULT 0,

    -- Processing flags
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_for_training BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Finance SSC Examples (Manually Curated)
CREATE TABLE IF NOT EXISTS finance_ssc_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Content
    category TEXT NOT NULL,  -- 'bir', 'month_end', 'superset', 'agency_ops', etc.
    subcategory TEXT,  -- More specific: '1601c', 'bank_rec', etc.
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    code_example TEXT,
    tags TEXT[],

    -- Metadata
    author TEXT,  -- Who created this example
    source TEXT,  -- 'skill', 'docs', 'manual'
    quality_score FLOAT DEFAULT 1.0,  -- Manually curated = high quality

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================================================================
-- 2. INDEXES FOR PERFORMANCE
-- ===========================================================================

-- Forum threads indexes
CREATE INDEX IF NOT EXISTS idx_forum_url ON odoo_forum_threads(url);
CREATE INDEX IF NOT EXISTS idx_forum_tags ON odoo_forum_threads USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_forum_quality ON odoo_forum_threads(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_forum_scraped_at ON odoo_forum_threads(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_forum_training ON odoo_forum_threads(processed_for_training);

-- Platform docs indexes
CREATE INDEX IF NOT EXISTS idx_docs_platform ON platform_docs(platform);
CREATE INDEX IF NOT EXISTS idx_docs_url ON platform_docs(url);
CREATE INDEX IF NOT EXISTS idx_docs_quality ON platform_docs(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_docs_scraped_at ON platform_docs(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_docs_training ON platform_docs(processed_for_training);

-- OCA GitHub indexes
CREATE INDEX IF NOT EXISTS idx_oca_type ON oca_github_docs(type);
CREATE INDEX IF NOT EXISTS idx_oca_repo ON oca_github_docs(repo);
CREATE INDEX IF NOT EXISTS idx_oca_labels ON oca_github_docs USING GIN(labels);
CREATE INDEX IF NOT EXISTS idx_oca_quality ON oca_github_docs(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_oca_training ON oca_github_docs(processed_for_training);

-- Finance SSC indexes
CREATE INDEX IF NOT EXISTS idx_finance_category ON finance_ssc_examples(category);
CREATE INDEX IF NOT EXISTS idx_finance_subcategory ON finance_ssc_examples(subcategory);
CREATE INDEX IF NOT EXISTS idx_finance_tags ON finance_ssc_examples USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_finance_quality ON finance_ssc_examples(quality_score DESC);

-- ===========================================================================
-- 3. FULL-TEXT SEARCH INDEXES
-- ===========================================================================

-- Forum threads full-text search
CREATE INDEX IF NOT EXISTS idx_forum_fts ON odoo_forum_threads
    USING gin(to_tsvector('english',
        coalesce(question_text, '') || ' ' ||
        coalesce(title, '') || ' ' ||
        coalesce(array_to_string(tags, ' '), '')
    ));

-- Platform docs full-text search
CREATE INDEX IF NOT EXISTS idx_docs_fts ON platform_docs
    USING gin(to_tsvector('english',
        content || ' ' || title
    ));

-- OCA GitHub full-text search
CREATE INDEX IF NOT EXISTS idx_oca_fts ON oca_github_docs
    USING gin(to_tsvector('english',
        coalesce(content, '') || ' ' ||
        coalesce(question, '') || ' ' ||
        title
    ));

-- Finance SSC full-text search
CREATE INDEX IF NOT EXISTS idx_finance_fts ON finance_ssc_examples
    USING gin(to_tsvector('english',
        question || ' ' || answer || ' ' || coalesce(code_example, '')
    ));

-- ===========================================================================
-- 4. TRIGGERS FOR AUTOMATIC UPDATES
-- ===========================================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_forum_threads_updated_at
    BEFORE UPDATE ON odoo_forum_threads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platform_docs_updated_at
    BEFORE UPDATE ON platform_docs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_oca_docs_updated_at
    BEFORE UPDATE ON oca_github_docs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_finance_examples_updated_at
    BEFORE UPDATE ON finance_ssc_examples
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===========================================================================
-- 5. RPC FUNCTIONS FOR RAG SEARCH
-- ===========================================================================

-- Main search function for RAG MCP server
CREATE OR REPLACE FUNCTION search_knowledge(
    query_text TEXT,
    limit_count INT DEFAULT 5,
    source_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    source TEXT,
    title TEXT,
    content TEXT,
    url TEXT,
    quality_score FLOAT,
    relevance FLOAT
) AS $$
BEGIN
    -- Search forum threads
    IF source_filter IS NULL OR source_filter = 'forum' THEN
        RETURN QUERY
        SELECT
            'forum'::TEXT as source,
            t.title,
            t.question_text || E'\n\nAnswer: ' || coalesce((t.accepted_answer->>'text')::TEXT, 'No answer') as content,
            t.url,
            t.quality_score,
            ts_rank(
                to_tsvector('english', coalesce(t.question_text, '') || ' ' || coalesce(t.title, '')),
                plainto_tsquery('english', query_text)
            ) as relevance
        FROM odoo_forum_threads t
        WHERE t.accepted_answer IS NOT NULL
          AND to_tsvector('english', coalesce(t.question_text, '') || ' ' || coalesce(t.title, ''))
              @@ plainto_tsquery('english', query_text)
        ORDER BY relevance DESC, t.quality_score DESC
        LIMIT limit_count;
    END IF;

    -- Search platform docs
    IF source_filter IS NULL OR source_filter = 'docs' THEN
        RETURN QUERY
        SELECT
            ('docs:' || d.platform)::TEXT as source,
            d.title,
            substring(d.content, 1, 1000) as content,
            d.url,
            d.quality_score,
            ts_rank(
                to_tsvector('english', d.content || ' ' || d.title),
                plainto_tsquery('english', query_text)
            ) as relevance
        FROM platform_docs d
        WHERE to_tsvector('english', d.content || ' ' || d.title)
              @@ plainto_tsquery('english', query_text)
        ORDER BY relevance DESC, d.quality_score DESC
        LIMIT limit_count;
    END IF;

    -- Search Finance SSC examples (highest priority)
    IF source_filter IS NULL OR source_filter = 'finance_ssc' THEN
        RETURN QUERY
        SELECT
            ('finance_ssc:' || f.category)::TEXT as source,
            f.question as title,
            f.answer || coalesce(E'\n\nCode:\n' || f.code_example, '') as content,
            NULL::TEXT as url,
            f.quality_score,
            ts_rank(
                to_tsvector('english', f.question || ' ' || f.answer || ' ' || coalesce(f.code_example, '')),
                plainto_tsquery('english', query_text)
            ) as relevance
        FROM finance_ssc_examples f
        WHERE to_tsvector('english', f.question || ' ' || f.answer || ' ' || coalesce(f.code_example, ''))
              @@ plainto_tsquery('english', query_text)
        ORDER BY relevance DESC, f.quality_score DESC
        LIMIT limit_count;
    END IF;

    -- Search OCA GitHub docs
    IF source_filter IS NULL OR source_filter = 'oca' THEN
        RETURN QUERY
        SELECT
            ('oca:' || o.type)::TEXT as source,
            o.title,
            coalesce(o.content, o.question, '') as content,
            o.url,
            o.quality_score,
            ts_rank(
                to_tsvector('english', coalesce(o.content, '') || ' ' || coalesce(o.question, '') || ' ' || o.title),
                plainto_tsquery('english', query_text)
            ) as relevance
        FROM oca_github_docs o
        WHERE to_tsvector('english', coalesce(o.content, '') || ' ' || coalesce(o.question, '') || ' ' || o.title)
              @@ plainto_tsquery('english', query_text)
        ORDER BY relevance DESC, o.quality_score DESC
        LIMIT limit_count;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate quality scores
CREATE OR REPLACE FUNCTION update_quality_scores() RETURNS void AS $$
BEGIN
    -- Forum threads: based on views, votes, answer quality
    UPDATE odoo_forum_threads
    SET quality_score = LEAST(1.0,
        (COALESCE(views, 0)::FLOAT / 1000.0 * 0.3) +
        (COALESCE(votes, 0)::FLOAT / 10.0 * 0.3) +
        (CASE WHEN accepted_answer IS NOT NULL THEN 0.4 ELSE 0 END)
    );

    -- Platform docs: based on content length, code blocks
    UPDATE platform_docs
    SET quality_score = LEAST(1.0,
        (CASE WHEN length(content) > 500 THEN 0.5 ELSE length(content)::FLOAT / 1000.0 END) +
        (CASE WHEN jsonb_array_length(COALESCE(code_blocks, '[]'::jsonb)) > 0 THEN 0.5 ELSE 0 END)
    );

    -- OCA docs: based on repo stars, content type
    UPDATE oca_github_docs
    SET quality_score = LEAST(1.0,
        (COALESCE(stars, 0)::FLOAT / 1000.0 * 0.5) +
        (CASE
            WHEN type = 'readme' THEN 0.5
            WHEN type = 'github_issue' AND jsonb_array_length(COALESCE(answers, '[]'::jsonb)) > 0 THEN 0.5
            ELSE 0.3
        END)
    );
END;
$$ LANGUAGE plpgsql;

-- Function to get knowledge stats
CREATE OR REPLACE FUNCTION get_knowledge_stats()
RETURNS TABLE (
    source TEXT,
    total_count BIGINT,
    high_quality_count BIGINT,
    avg_quality_score FLOAT,
    processed_for_training BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'forum'::TEXT, COUNT(*)::BIGINT, COUNT(*) FILTER (WHERE quality_score > 0.7)::BIGINT,
           AVG(quality_score)::FLOAT, COUNT(*) FILTER (WHERE processed_for_training)::BIGINT
    FROM odoo_forum_threads
    UNION ALL
    SELECT 'docs'::TEXT, COUNT(*)::BIGINT, COUNT(*) FILTER (WHERE quality_score > 0.7)::BIGINT,
           AVG(quality_score)::FLOAT, COUNT(*) FILTER (WHERE processed_for_training)::BIGINT
    FROM platform_docs
    UNION ALL
    SELECT 'oca'::TEXT, COUNT(*)::BIGINT, COUNT(*) FILTER (WHERE quality_score > 0.7)::BIGINT,
           AVG(quality_score)::FLOAT, COUNT(*) FILTER (WHERE processed_for_training)::BIGINT
    FROM oca_github_docs
    UNION ALL
    SELECT 'finance_ssc'::TEXT, COUNT(*)::BIGINT, COUNT(*) FILTER (WHERE quality_score > 0.7)::BIGINT,
           AVG(quality_score)::FLOAT, 0::BIGINT
    FROM finance_ssc_examples;
END;
$$ LANGUAGE plpgsql;

-- ===========================================================================
-- 6. ROW-LEVEL SECURITY (Optional but recommended)
-- ===========================================================================

-- Enable RLS
ALTER TABLE odoo_forum_threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_docs ENABLE ROW LEVEL SECURITY;
ALTER TABLE oca_github_docs ENABLE ROW LEVEL SECURITY;
ALTER TABLE finance_ssc_examples ENABLE ROW LEVEL SECURITY;

-- Allow all operations for authenticated users (adjust as needed)
CREATE POLICY "Allow all for authenticated users" ON odoo_forum_threads
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Allow all for authenticated users" ON platform_docs
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Allow all for authenticated users" ON oca_github_docs
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Allow all for authenticated users" ON finance_ssc_examples
    FOR ALL TO authenticated USING (true);

-- Allow read-only access for anon users (for public knowledge base)
CREATE POLICY "Allow read for anon" ON odoo_forum_threads
    FOR SELECT TO anon USING (true);

CREATE POLICY "Allow read for anon" ON platform_docs
    FOR SELECT TO anon USING (true);

CREATE POLICY "Allow read for anon" ON oca_github_docs
    FOR SELECT TO anon USING (true);

CREATE POLICY "Allow read for anon" ON finance_ssc_examples
    FOR SELECT TO anon USING (true);

-- ===========================================================================
-- 7. SEED DATA (Optional - add some Finance SSC examples)
-- ===========================================================================

INSERT INTO finance_ssc_examples (category, subcategory, question, answer, code_example, tags) VALUES
(
    'bir',
    '1601c',
    'How do I configure BIR Form 1601-C in Odoo 19?',
    'BIR Form 1601-C (Monthly Remittance Return of Income Taxes Withheld) can be configured in Odoo 19 using the custom bir_tax_filing module.

Steps:
1. Install the bir_tax_filing module
2. Configure tax types (see code)
3. Set up withholding tax accounts
4. Configure filing schedule (monthly, on/before 10th of following month)',
    '# Odoo 19 Configuration
from odoo import models, fields

class BIRForm1601C(models.Model):
    _name = ''bir.form.1601c''

    period_month = fields.Selection([
        (''1'', ''January''), (''2'', ''February''), ...
    ])
    filing_deadline = fields.Date()
    total_tax_withheld = fields.Monetary()

    def generate_form(self):
        # Auto-generate from account.move.line
        pass',
    ARRAY['bir', 'tax', '1601c', 'withholding']
),
(
    'month_end',
    'closing',
    'How do I automate month-end closing in Odoo for multi-agency operations?',
    'Month-end closing for multi-agency operations requires:

1. Closing Checklist: Use finance_ssc_closing module
2. Agency Separation: Each agency has own company_id
3. Automated Tasks: Bank reconciliation, journal entries, trial balance
4. Validation: All entries balanced, ATP valid, BIR reports ready

The finance_ssc_closing module provides workflow automation.',
    'from odoo import models

class ClosingPeriod(models.Model):
    _name = ''finance.closing.period''

    agency_ids = fields.Many2many(''res.company'')
    closing_date = fields.Date()
    task_ids = fields.One2many(''finance.closing.task'')

    def run_automated_closing(self):
        for agency in self.agency_ids:
            self.env[''finance.closing.task''].create({
                ''name'': f''Bank Rec - {agency.name}'',
                ''agency_id'': agency.id,
                ''type'': ''bank_reconciliation''
            })
        return True',
    ARRAY['month-end', 'closing', 'automation', 'multi-agency']
);

-- ===========================================================================
-- END OF MIGRATION
-- ===========================================================================

-- Verify migration
DO $$
BEGIN
    RAISE NOTICE 'Knowledge pipeline migration completed successfully';
    RAISE NOTICE 'Tables created: odoo_forum_threads, platform_docs, oca_github_docs, finance_ssc_examples';
    RAISE NOTICE 'Functions created: search_knowledge(), update_quality_scores(), get_knowledge_stats()';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Run quality score calculation: SELECT update_quality_scores();';
    RAISE NOTICE '2. Test search: SELECT * FROM search_knowledge(''odoo month end closing'', 5);';
    RAISE NOTICE '3. Check stats: SELECT * FROM get_knowledge_stats();';
END $$;
