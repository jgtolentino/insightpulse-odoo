# Knowledge Pipeline Implementation Plan
## Unified Approach: Fixing Existing + Building Comprehensive Pipeline

**Date:** 2025-11-05
**Branch:** `claude/review-known-implementation-011CUqWm5hGSnXeBsuhgLLVj`
**Goal:** Implement production-ready knowledge scraping → RAG/Training pipeline

---

## 🎯 Executive Decision: RAG First, Training Later

Based on the analysis in `KNOWLEDGE_AGENT_IMPLEMENTATION_REVIEW.md`:

### Phase 1 (Weeks 1-2): **RAG Approach** ✅ RECOMMENDED
- Faster time-to-value (days vs weeks)
- Lower risk (no training required)
- Uses Claude's reasoning + your domain knowledge
- Cost: ~$1,000/year (realistic for Finance SSC usage)
- Can handle complex code generation

### Phase 2 (Months 3-6): **Fine-tuning** (Conditional)
- Only if RAG accuracy < 80%
- Only if you have 50K+ high-quality examples
- Use 1.5B+ model (not 0.5B)
- Requires GPU infrastructure

**Decision: Implement RAG first, evaluate for 3 months, then decide on fine-tuning.**

---

## 📋 Implementation Roadmap

### Week 1: Fix Existing + Supabase Foundation

#### Day 1-2: Fix Critical Issues in Existing Knowledge Agent
- [ ] Fix hardcoded paths (use config parameters)
- [ ] Add dependency validation (Playwright)
- [ ] Implement concurrency control
- [ ] Update GitHub Actions to use same scraper
- [ ] Add basic tests

#### Day 3-4: Supabase Schema & Integration
- [ ] Create Supabase tables (odoo_forum_threads, platform_docs, oca_github_docs)
- [ ] Add full-text search indexes
- [ ] Create RPC functions for similarity search
- [ ] Update existing scraper to save to Supabase

#### Day 5: Testing & Deployment
- [ ] Test scraper with Supabase integration
- [ ] Deploy fixed module to staging
- [ ] Run manual scrape and verify Supabase data
- [ ] Set up cron job for daily scraping

### Week 2: Platform Scrapers + Data Collection

#### Day 1-2: Platform Documentation Scraper
- [ ] Implement multi-platform scraper (Docker, Superset, Supabase, Odoo, DigitalOcean)
- [ ] Add rate limiting and respectful crawling
- [ ] Test on each platform
- [ ] Set up weekly cron job

#### Day 3: OCA GitHub Scraper
- [ ] Implement GitHub API scraper (READMEs, issues)
- [ ] Add quality filtering (stars, comments)
- [ ] Test with top 100 OCA repos
- [ ] Set up monthly cron job

#### Day 4-5: Data Quality & Preparation
- [ ] Implement quality filtering pipeline
- [ ] Add deduplication logic
- [ ] Create manual Finance SSC examples
- [ ] Verify 1000+ high-quality examples collected

### Week 3: RAG Implementation + MCP Server

#### Day 1-2: RAG MCP Server
- [ ] Create finance-ssc-rag MCP server
- [ ] Implement semantic search in Supabase
- [ ] Add context augmentation for Claude queries
- [ ] Test with sample Finance SSC questions

#### Day 3: Integration & Testing
- [ ] Integrate RAG MCP with Claude Code
- [ ] Test 50 real Finance SSC queries
- [ ] Measure accuracy vs. baseline
- [ ] Document performance metrics

#### Day 4-5: Deployment & Monitoring
- [ ] Deploy RAG MCP to DigitalOcean
- [ ] Set up Superset dashboard for metrics
- [ ] Create user documentation
- [ ] Train team on new system

### Week 4: Training Infrastructure (Prep for Phase 2)

#### Day 1-2: Dataset Preparation Pipeline
- [ ] Implement prepare_dataset.py
- [ ] Format for instruction tuning
- [ ] Create eval dataset (10% holdout)
- [ ] Generate first training dataset

#### Day 3-4: Training Scripts (Ready but Not Run)
- [ ] Set up Unsloth training script
- [ ] Configure for Lambda Labs GPU
- [ ] Create GitHub Actions workflow
- [ ] Document training process

#### Day 5: Evaluation Framework
- [ ] Create model evaluation script
- [ ] Define accuracy thresholds
- [ ] Set up A/B testing framework
- [ ] Document decision criteria for Phase 2

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  EXISTING (Fixed)                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ odoo_knowledge_agent (Odoo Module)                   │  │
│  │ - Cron job (weekly)                                  │  │
│  │ - Scrapes Odoo forum                                 │  │
│  │ - Stores in Supabase (NEW)                           │  │
│  │ - UI for manual triggering                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                    ↓ (Data flows to Supabase)
┌─────────────────────────────────────────────────────────────┐
│  NEW: Multi-Source Scraping                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Platform     │  │ OCA GitHub   │  │ Manual       │    │
│  │ Docs Scraper │  │ Scraper      │  │ Finance SSC  │    │
│  │ (Weekly)     │  │ (Monthly)    │  │ Examples     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                    ↓ (All data in Supabase)
┌─────────────────────────────────────────────────────────────┐
│  Supabase Knowledge Base                                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ - odoo_forum_threads (Q&A pairs)                   │    │
│  │ - platform_docs (Documentation)                    │    │
│  │ - oca_github_docs (Code examples)                  │    │
│  │ - finance_ssc_examples (Curated examples)          │    │
│  │                                                     │    │
│  │ Features:                                          │    │
│  │ - Full-text search (pg_tsvector)                   │    │
│  │ - Similarity search (pgvector - future)            │    │
│  │ - Quality scoring                                  │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                    ↓ (Used by)
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: RAG MCP Server (Weeks 1-3)                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │ finance-ssc-rag                                     │    │
│  │                                                     │    │
│  │ Tools:                                             │    │
│  │ - query_with_knowledge(question)                   │    │
│  │   → Search Supabase for relevant examples         │    │
│  │   → Augment context                                │    │
│  │   → Query Claude Sonnet                            │    │
│  │                                                     │    │
│  │ - search_knowledge(query, filters)                 │    │
│  │   → Direct Supabase search                         │    │
│  │                                                     │    │
│  │ Benefits:                                          │    │
│  │ ✅ Fast implementation (1 week)                    │    │
│  │ ✅ Keeps Claude's reasoning                        │    │
│  │ ✅ Instant updates as data grows                   │    │
│  │ ✅ No training infrastructure needed               │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                    ↓ (Alternative future path)
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: Fine-tuning (Conditional - Months 3-6)           │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Training Pipeline (Only if RAG < 80% accuracy)     │    │
│  │                                                     │    │
│  │ 1. Dataset Preparation                             │    │
│  │    - prepare_dataset.py                            │    │
│  │    - Quality filtering                             │    │
│  │    - Instruction formatting                        │    │
│  │                                                     │    │
│  │ 2. Model Training                                  │    │
│  │    - Base: Qwen2.5-1.5B (NOT 0.5B)                │    │
│  │    - Method: LoRA with Unsloth                     │    │
│  │    - GPU: Lambda Labs spot instances               │    │
│  │    - Cost: $2/week                                 │    │
│  │                                                     │    │
│  │ 3. Deployment                                      │    │
│  │    - Ollama on DigitalOcean                        │    │
│  │    - MCP server: finance-ssc-model                 │    │
│  │    - A/B test vs RAG approach                      │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
insightpulse-odoo/
├── addons/custom/odoo_knowledge_agent/    # EXISTING (will be fixed)
│   ├── models/
│   │   └── knowledge_agent.py             # FIX: Remove hardcoded paths
│   ├── data/
│   │   └── cron_forum_scraper.xml         # FIX: Add concurrency control
│   └── ...
│
├── scrapers/                               # NEW
│   ├── __init__.py
│   ├── odoo_forum_scraper.py              # Enhanced scraper with Supabase
│   ├── platform_docs_scraper.py           # Multi-platform doc scraper
│   ├── oca_github_scraper.py              # OCA GitHub scraper
│   └── requirements.txt                   # BeautifulSoup, requests, supabase-py
│
├── mcp-servers/                            # NEW
│   ├── finance-ssc-rag/                   # PHASE 1: RAG approach
│   │   ├── server.py
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   └── finance-ssc-model/                 # PHASE 2: Fine-tuned model (future)
│       ├── server.py
│       ├── pyproject.toml
│       └── README.md
│
├── training/                               # PHASE 2: Training pipeline (prep)
│   ├── prepare_dataset.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   ├── config.yaml
│   ├── requirements.txt
│   └── README.md
│
├── supabase/migrations/                    # NEW
│   ├── 010_knowledge_pipeline.sql         # Schema for knowledge tables
│   └── 011_knowledge_search_functions.sql # RPC functions
│
├── scripts/                                # NEW
│   ├── cron_forum_scraper.sh              # Updated for Supabase
│   ├── cron_docs_scraper.sh
│   ├── cron_oca_scraper.sh
│   └── test_rag_accuracy.py               # Evaluation script
│
└── docs/
    ├── KNOWLEDGE_AGENT_IMPLEMENTATION_REVIEW.md  # EXISTING (my review)
    ├── KNOWLEDGE_PIPELINE_IMPLEMENTATION_PLAN.md  # THIS FILE
    └── KNOWLEDGE_PIPELINE_USER_GUIDE.md           # TO BE CREATED
```

---

## 🔧 Technical Specifications

### Supabase Schema

```sql
-- Main knowledge tables
CREATE TABLE odoo_forum_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    question_text TEXT,
    question_code JSONB,
    accepted_answer JSONB,
    other_answers JSONB,
    tags TEXT[],
    views INTEGER DEFAULT 0,
    votes INTEGER DEFAULT 0,
    quality_score FLOAT DEFAULT 0,  -- NEW: Auto-calculated quality
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_for_training BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE platform_docs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    code_blocks JSONB,
    quality_score FLOAT DEFAULT 0,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_for_training BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE oca_github_docs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL,  -- 'readme', 'issue'
    repo TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    question TEXT,
    answers JSONB,
    url TEXT NOT NULL,
    labels TEXT[],
    stars INTEGER DEFAULT 0,
    quality_score FLOAT DEFAULT 0,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_for_training BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE finance_ssc_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL,  -- 'bir', 'month_end', 'superset', etc.
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    code_example TEXT,
    tags TEXT[],
    quality_score FLOAT DEFAULT 1.0,  -- Manually curated = high quality

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for fast search
CREATE INDEX idx_forum_tags ON odoo_forum_threads USING GIN(tags);
CREATE INDEX idx_forum_quality ON odoo_forum_threads(quality_score DESC);
CREATE INDEX idx_docs_platform ON platform_docs(platform);
CREATE INDEX idx_docs_quality ON platform_docs(quality_score DESC);
CREATE INDEX idx_oca_repo ON oca_github_docs(repo);
CREATE INDEX idx_finance_category ON finance_ssc_examples(category);

-- Full-text search
CREATE INDEX idx_forum_fts ON odoo_forum_threads
    USING gin(to_tsvector('english', question_text || ' ' || coalesce(title, '')));
CREATE INDEX idx_docs_fts ON platform_docs
    USING gin(to_tsvector('english', content || ' ' || title));
CREATE INDEX idx_finance_fts ON finance_ssc_examples
    USING gin(to_tsvector('english', question || ' ' || answer));

-- RPC function for semantic search (full-text for now, pgvector later)
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
            t.question_text || E'\n\nAnswer: ' || (t.accepted_answer->>'text')::TEXT as content,
            t.url,
            t.quality_score,
            ts_rank(to_tsvector('english', t.question_text), plainto_tsquery('english', query_text)) as relevance
        FROM odoo_forum_threads t
        WHERE t.accepted_answer IS NOT NULL
          AND to_tsvector('english', t.question_text) @@ plainto_tsquery('english', query_text)
        ORDER BY relevance DESC, t.quality_score DESC
        LIMIT limit_count;
    END IF;

    -- Search platform docs
    IF source_filter IS NULL OR source_filter = 'docs' THEN
        RETURN QUERY
        SELECT
            'docs'::TEXT as source,
            d.title,
            substring(d.content, 1, 1000) as content,
            d.url,
            d.quality_score,
            ts_rank(to_tsvector('english', d.content), plainto_tsquery('english', query_text)) as relevance
        FROM platform_docs d
        WHERE to_tsvector('english', d.content) @@ plainto_tsquery('english', query_text)
        ORDER BY relevance DESC, d.quality_score DESC
        LIMIT limit_count;
    END IF;

    -- Search Finance SSC examples
    IF source_filter IS NULL OR source_filter = 'finance_ssc' THEN
        RETURN QUERY
        SELECT
            'finance_ssc'::TEXT as source,
            f.question as title,
            f.answer as content,
            NULL::TEXT as url,
            f.quality_score,
            ts_rank(to_tsvector('english', f.question || ' ' || f.answer), plainto_tsquery('english', query_text)) as relevance
        FROM finance_ssc_examples f
        WHERE to_tsvector('english', f.question || ' ' || f.answer) @@ plainto_tsquery('english', query_text)
        ORDER BY relevance DESC, f.quality_score DESC
        LIMIT limit_count;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate quality score
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

    -- OCA docs: based on repo stars, issue comments
    UPDATE oca_github_docs
    SET quality_score = LEAST(1.0,
        (COALESCE(stars, 0)::FLOAT / 1000.0 * 0.5) +
        (CASE WHEN type = 'readme' THEN 0.5
              WHEN type = 'issue' AND jsonb_array_length(COALESCE(answers, '[]'::jsonb)) > 0 THEN 0.5
              ELSE 0 END)
    );
END;
$$ LANGUAGE plpgsql;
```

### RAG MCP Server Implementation

```python
# mcp-servers/finance-ssc-rag/server.py
"""
Finance SSC RAG MCP Server
Retrieval-Augmented Generation using Supabase knowledge base + Claude
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from supabase import create_client, Client
import os
import anthropic

app = Server("finance-ssc-rag")

# Initialize clients
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.tool()
def query_with_knowledge(question: str, max_context_items: int = 3):
    """
    Query Claude with relevant knowledge from scraped data

    Args:
        question: User's question about Odoo/Finance SSC
        max_context_items: Number of relevant examples to include

    Returns:
        Answer augmented with domain knowledge
    """

    # 1. Search Supabase for relevant knowledge
    results = supabase.rpc('search_knowledge', {
        'query_text': question,
        'limit_count': max_context_items
    }).execute()

    # 2. Build context from retrieved knowledge
    context_parts = []
    for i, item in enumerate(results.data, 1):
        context_parts.append(f"""
**Example {i} (from {item['source']}):**
Title: {item['title']}
Content: {item['content'][:500]}...
URL: {item.get('url', 'N/A')}
Relevance: {item['relevance']:.2f}
""")

    context = "\n\n".join(context_parts) if context_parts else "No relevant examples found in knowledge base."

    # 3. Build augmented prompt
    augmented_prompt = f"""You are a Finance SSC expert specializing in Odoo ERP, BIR compliance, and multi-agency operations.

Use the following knowledge base examples to help answer the question. These are real-world solutions from:
- Odoo community forum (solved threads)
- Official documentation (Docker, Superset, Supabase, Odoo)
- OCA GitHub repositories
- Curated Finance SSC examples

KNOWLEDGE BASE CONTEXT:
{context}

USER QUESTION:
{question}

Provide a comprehensive answer that:
1. Directly addresses the question
2. References the knowledge base examples when relevant
3. Includes code examples if applicable
4. Provides step-by-step instructions
5. Mentions potential gotchas or common mistakes

If the knowledge base doesn't have relevant information, use your general knowledge but mention that."""

    # 4. Query Claude with augmented context
    response = claude.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        messages=[{"role": "user", "content": augmented_prompt}]
    )

    return {
        "answer": response.content[0].text,
        "context_used": len(results.data),
        "sources": [{"title": r['title'], "url": r.get('url'), "source": r['source']} for r in results.data]
    }

@app.tool()
def search_knowledge(
    query: str,
    source_filter: str = None,
    limit: int = 10
):
    """
    Search the knowledge base directly

    Args:
        query: Search query
        source_filter: Filter by source ('forum', 'docs', 'finance_ssc', 'oca')
        limit: Max results to return

    Returns:
        List of matching knowledge items
    """
    results = supabase.rpc('search_knowledge', {
        'query_text': query,
        'limit_count': limit,
        'source_filter': source_filter
    }).execute()

    return results.data

@app.tool()
def get_finance_ssc_examples(category: str = None):
    """
    Get curated Finance SSC examples by category

    Args:
        category: Filter by category (bir, month_end, superset, etc.)

    Returns:
        List of Finance SSC examples
    """
    query = supabase.table('finance_ssc_examples').select('*')

    if category:
        query = query.eq('category', category)

    query = query.order('quality_score', desc=True).limit(10)
    results = query.execute()

    return results.data

@app.tool()
def update_quality_scores():
    """
    Recalculate quality scores for all knowledge items

    Returns:
        Status message
    """
    supabase.rpc('update_quality_scores').execute()
    return {"status": "Quality scores updated successfully"}

if __name__ == "__main__":
    stdio_server(app)
```

---

## 📊 Success Metrics

### Phase 1 (RAG) - Week 3 Evaluation

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Accuracy** | >85% | Eval set of 50 Finance SSC questions |
| **Response Time** | <5 seconds | Average query time |
| **Context Relevance** | >80% | Manual review of retrieved examples |
| **User Satisfaction** | >4/5 | Survey after 1 week usage |
| **Cost per Query** | <$0.02 | Claude API usage tracking |

### Phase 2 (Fine-tuning) - Only if RAG < 80%

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Training Accuracy** | >90% | Eval set accuracy |
| **Inference Speed** | <2 seconds | Ollama query time |
| **Model Size** | <3GB | GGUF file size |
| **Quality vs Claude** | >80% of Claude quality | A/B test |
| **Cost Savings** | $1,000+/year | API cost reduction |

---

## 🚀 Quick Start (Week 1)

```bash
# Day 1: Fix existing knowledge agent
cd ~/insightpulse-odoo
git checkout claude/review-known-implementation-011CUqWm5hGSnXeBsuhgLLVj

# Apply fixes to knowledge agent
# (See fixes below)

# Day 2: Set up Supabase schema
cd supabase/migrations
# Create 010_knowledge_pipeline.sql
# Run migration

# Day 3: Create scrapers directory
mkdir -p scrapers mcp-servers/finance-ssc-rag training scripts

# Install dependencies
pip install supabase-py beautifulsoup4 requests PyGithub anthropic

# Day 4: Implement and test forum scraper
python scrapers/odoo_forum_scraper.py

# Day 5: Deploy to staging
# Test complete pipeline
```

---

## 🔥 Critical Fixes to Existing Knowledge Agent

### Fix 1: Remove Hardcoded Paths

```python
# addons/custom/odoo_knowledge_agent/models/knowledge_agent.py

def _run_forum_scraper(self):
    """Execute the forum scraper script"""
    self.ensure_one()

    try:
        self.write({'state': 'running'})

        # FIXED: Use config parameter instead of hardcoded path
        scraper_path = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_knowledge_agent.scraper_path',
            default='/opt/insightpulse-odoo/scrapers/odoo_forum_scraper.py'
        )

        if not Path(scraper_path).exists():
            raise FileNotFoundError(f"Scraper script not found: {scraper_path}. Configure via Settings > Technical > System Parameters")

        # FIXED: Use same Python interpreter as Odoo
        python_exe = sys.executable

        # FIXED: Validate dependencies
        playwright_check = subprocess.run(
            [python_exe, '-c', 'import playwright'],
            capture_output=True
        )
        if playwright_check.returncode != 0:
            raise ImportError("Playwright not installed. Run: pip install playwright && python -m playwright install chromium")

        # Run scraper
        result = subprocess.run(
            [python_exe, scraper_path],
            capture_output=True,
            text=True,
            timeout=3600,
            env={**os.environ, 'PYTHONPATH': ...}  # Preserve environment
        )

        # ... rest of the method
```

### Fix 2: Add Concurrency Control

```python
@api.model
def cron_scrape_forum(self):
    """Cron job to scrape Odoo forum for solved issues"""

    # NEW: Check if another scrape is already running
    running_scrapes = self.search([('state', '=', 'running')])
    if running_scrapes:
        _logger.info("Scrape already running, skipping this cron run")
        return

    _logger.info("🔍 Starting scheduled forum scraping...")

    # Rest of the method...
```

### Fix 3: Integrate with Supabase

```python
def _run_forum_scraper(self):
    # ... after successful scrape ...

    if result.returncode == 0:
        data = json.load(open(output_file))

        # NEW: Upload to Supabase
        self._upload_to_supabase(data)

        self.write({'state': 'done', ...})

def _upload_to_supabase(self, threads):
    """Upload scraped threads to Supabase for RAG"""
    from supabase import create_client

    supabase_url = self.env['ir.config_parameter'].sudo().get_param('supabase.url')
    supabase_key = self.env['ir.config_parameter'].sudo().get_param('supabase.key')

    if not supabase_url or not supabase_key:
        _logger.warning("Supabase not configured, skipping upload")
        return

    supabase = create_client(supabase_url, supabase_key)

    for thread in threads:
        try:
            # Check if already exists
            existing = supabase.table('odoo_forum_threads')\
                .select('id')\
                .eq('url', thread['url'])\
                .execute()

            if not existing.data:
                supabase.table('odoo_forum_threads').insert({
                    'title': thread['title'],
                    'url': thread['url'],
                    'tags': thread.get('tags', []),
                    'scraped_at': fields.Datetime.now().isoformat()
                }).execute()
                _logger.info(f"Uploaded to Supabase: {thread['title']}")
        except Exception as e:
            _logger.error(f"Error uploading thread: {e}")
```

---

## 📖 Next Steps

1. **Review this plan** with team
2. **Decide**: RAG-only or RAG→Training path
3. **Assign resources**: Developer time, GPU budget (if training)
4. **Set timeline**: 3 weeks for Phase 1, evaluate, then decide on Phase 2
5. **Begin implementation**: Start with Week 1 tasks

---

**END OF IMPLEMENTATION PLAN**

**Estimated Total Effort:**
- Phase 1 (RAG): 3 weeks (1 developer)
- Phase 2 (Training): 2-4 weeks (if needed)

**Expected ROI:**
- Research time saved: 20 hours/week × $50/hr = $52,000/year
- API cost savings: $1,000/year (Phase 1) or $24,000/year (Phase 2)
- Improved accuracy: 85%+ (Phase 1) or 90%+ (Phase 2)

**Risk Level:**
- Phase 1: LOW (proven technology stack)
- Phase 2: MEDIUM (model training has uncertainties)
