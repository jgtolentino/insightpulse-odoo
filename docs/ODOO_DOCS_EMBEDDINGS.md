# Odoo Documentation Embeddings System

**Purpose:** Semantic search over Odoo 19.0 developer documentation using vector embeddings
**Technology:** PostgreSQL pgvector + OpenAI embeddings
**Use Case:** AI-assisted Odoo development with context-aware documentation retrieval

---

## Overview

This system creates searchable embeddings of the entire Odoo 19.0 developer reference documentation, enabling:

- **Semantic Search:** Find relevant docs by meaning, not just keywords
- **AI Context:** Feed accurate documentation context to Claude/GPT for better code generation
- **Developer Efficiency:** Instant access to relevant documentation snippets

---

## Architecture

```
Odoo Documentation (HTML)
    ↓
BeautifulSoup Scraper
    ↓
Content Chunking (500 words, 50 overlap)
    ↓
OpenAI text-embedding-3-small (1536 dims)
    ↓
PostgreSQL with pgvector
    ↓
Semantic Search Interface
```

---

## Prerequisites

### 1. PostgreSQL with pgvector Extension

**Supabase Configuration:**
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 2. Environment Variables

```bash
# Add to ~/.zshrc or .env
export OPENAI_API_KEY="sk-..."
export SUPABASE_PASSWORD="your_supabase_password"

# Verify
echo $OPENAI_API_KEY
echo $SUPABASE_PASSWORD
```

### 3. Python Dependencies

```bash
pip install psycopg2-binary requests beautifulsoup4 openai
```

---

## Installation

### Step 1: Run Embedding Pipeline

```bash
# Full documentation crawl (depth=2, ~500 pages)
python3 scripts/odoo-docs-embeddings.py

# Expected output:
# 🚀 Odoo Documentation Embeddings Pipeline
# ✅ Connected to database
# ✅ Database schema created
# 📚 Fetching Odoo documentation...
# ✅ Fetched 500 documentation sections
# 🧠 Generating embeddings...
# ✅ Stored 1500 embeddings
# 🔍 Testing semantic search...
```

**Estimated Time:** 30-60 minutes (depending on rate limits)
**Cost:** ~$0.10 USD (100K tokens @ $0.02/1M for text-embedding-3-small)

### Step 2: Verify Database

```sql
-- Check embeddings count
SELECT COUNT(*) FROM odoo_docs_embeddings;

-- Sample record
SELECT url, title, metadata 
FROM odoo_docs_embeddings 
LIMIT 1;

-- Check embedding dimensions
SELECT vector_dims(embedding) 
FROM odoo_docs_embeddings 
LIMIT 1;
-- Should return: 1536
```

---

## Usage

### 1. Semantic Search (Python)

```python
from odoo_docs_embeddings import OdooDocsEmbedder

embedder = OdooDocsEmbedder()
embedder.connect_db()

# Search for relevant documentation
results = embedder.semantic_search(
    query="How do I create a custom Odoo model with computed fields?",
    top_k=5
)

for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Similarity: {result['similarity']:.2%}")
    print(f"Content: {result['content'][:200]}...\n")
```

### 2. SQL Semantic Search

```sql
-- Direct SQL search (requires query embedding)
WITH query_embedding AS (
  SELECT embedding 
  FROM odoo_docs_embeddings 
  WHERE content LIKE '%models.Model%' 
  LIMIT 1
)
SELECT 
  url,
  title,
  content,
  1 - (embedding <=> (SELECT embedding FROM query_embedding)) AS similarity
FROM odoo_docs_embeddings
ORDER BY embedding <=> (SELECT embedding FROM query_embedding)
LIMIT 10;
```

### 3. Claude Code Integration

**Use Case:** AI-assisted Odoo module development

```python
# In Claude Code context
from odoo_docs_embeddings import OdooDocsEmbedder

def get_odoo_context(task_description: str) -> str:
    """Fetch relevant Odoo documentation for AI context"""
    embedder = OdooDocsEmbedder()
    embedder.connect_db()
    
    results = embedder.semantic_search(task_description, top_k=3)
    
    context = "# Relevant Odoo Documentation\n\n"
    for result in results:
        context += f"## {result['title']}\n"
        context += f"Source: {result['url']}\n\n"
        context += f"{result['content']}\n\n---\n\n"
    
    return context

# Example usage
task = "Create a multi-company expense report model with BIR compliance"
odoo_docs_context = get_odoo_context(task)

# Feed to Claude
prompt = f"""
{odoo_docs_context}

Task: {task}

Generate Odoo 19.0 module code following OCA standards.
"""
```

---

## Database Schema

```sql
CREATE TABLE odoo_docs_embeddings (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,                    -- Documentation page URL
    section_id TEXT NOT NULL,             -- Heading ID (anchor)
    title TEXT NOT NULL,                  -- Section title
    content TEXT NOT NULL,                -- Chunked content
    content_hash TEXT UNIQUE NOT NULL,    -- SHA256 for deduplication
    embedding vector(1536),               -- OpenAI embedding
    metadata JSONB,                       -- Additional context
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_odoo_docs_url ON odoo_docs_embeddings(url);
CREATE INDEX idx_odoo_docs_hash ON odoo_docs_embeddings(content_hash);
CREATE INDEX idx_odoo_docs_embedding ON odoo_docs_embeddings 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_odoo_docs_metadata ON odoo_docs_embeddings USING gin(metadata);
```

**Metadata Structure:**
```json
{
  "odoo_version": "19.0",
  "heading_level": "h2",
  "doc_type": "developer_reference",
  "chunk_index": 0,
  "total_chunks": 3
}
```

---

## Performance Optimization

### 1. Index Tuning

```sql
-- Rebuild IVFFlat index with optimal lists
DROP INDEX idx_odoo_docs_embedding;
CREATE INDEX idx_odoo_docs_embedding ON odoo_docs_embeddings 
    USING ivfflat (embedding vector_cosine_ops) 
    WITH (lists = 100);  -- Adjust based on dataset size
```

**Rule of Thumb:** `lists = rows / 1000` (100 lists for 100K rows)

### 2. Query Optimization

```sql
-- Use EXPLAIN ANALYZE to check performance
EXPLAIN ANALYZE
SELECT url, title, 
       1 - (embedding <=> '[...]'::vector) AS similarity
FROM odoo_docs_embeddings
ORDER BY embedding <=> '[...]'::vector
LIMIT 10;

-- Expected: Index Scan using idx_odoo_docs_embedding
```

### 3. Caching Strategy

- Cache frequently searched embeddings in Redis
- Pre-compute embeddings for common queries
- Use connection pooling (Supabase pooler: port 6543)

---

## Maintenance

### Update Documentation

```bash
# Incremental update (fetch only new/changed pages)
python3 scripts/odoo-docs-embeddings.py --incremental

# Full refresh (re-process all documentation)
python3 scripts/odoo-docs-embeddings.py --full-refresh
```

### Monitor Costs

```sql
-- Count embeddings
SELECT COUNT(*) FROM odoo_docs_embeddings;

-- Estimate OpenAI cost
-- Formula: (total_tokens / 1_000_000) * $0.02
-- Average: 500 words = 750 tokens per chunk
SELECT 
  COUNT(*) * 750 / 1000000.0 * 0.02 AS estimated_cost_usd
FROM odoo_docs_embeddings;
```

### Cleanup

```sql
-- Remove outdated embeddings
DELETE FROM odoo_docs_embeddings
WHERE metadata->>'odoo_version' < '19.0';

-- Remove duplicates (keep latest)
DELETE FROM odoo_docs_embeddings
WHERE id NOT IN (
  SELECT MAX(id)
  FROM odoo_docs_embeddings
  GROUP BY content_hash
);
```

---

## Troubleshooting

### Issue: Connection Timeout

```python
# Increase timeout
DB_CONFIG = {
    'host': 'aws-1-us-east-1.pooler.supabase.com',
    'port': 6543,
    'connect_timeout': 30,  # Add this
    ...
}
```

### Issue: Rate Limiting (OpenAI)

```python
import time

def generate_embedding_with_retry(text: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return generate_embedding(text)
        except Exception as e:
            if "rate_limit" in str(e).lower():
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"⏳ Rate limit hit, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

### Issue: pgvector Extension Missing

```sql
-- Check if extension exists
SELECT * FROM pg_available_extensions WHERE name = 'vector';

-- Install (requires superuser)
CREATE EXTENSION vector;

-- Verify
\dx vector
```

---

## Advanced Use Cases

### 1. Multi-Version Support

```sql
-- Add version column
ALTER TABLE odoo_docs_embeddings
ADD COLUMN odoo_version TEXT DEFAULT '19.0';

-- Create partial index per version
CREATE INDEX idx_odoo_docs_v19 
ON odoo_docs_embeddings(embedding) 
WHERE metadata->>'odoo_version' = '19.0';
```

### 2. Hybrid Search (Keyword + Semantic)

```sql
-- Combine full-text search with vector similarity
WITH keyword_results AS (
  SELECT id, url, title, 
         ts_rank(to_tsvector('english', content), websearch_to_tsquery('english', 'computed fields')) AS keyword_score
  FROM odoo_docs_embeddings
  WHERE to_tsvector('english', content) @@ websearch_to_tsquery('english', 'computed fields')
),
semantic_results AS (
  SELECT id, url, title,
         1 - (embedding <=> '[query_embedding]'::vector) AS semantic_score
  FROM odoo_docs_embeddings
  ORDER BY embedding <=> '[query_embedding]'::vector
  LIMIT 100
)
SELECT 
  COALESCE(k.url, s.url) AS url,
  COALESCE(k.title, s.title) AS title,
  COALESCE(k.keyword_score, 0) * 0.3 + COALESCE(s.semantic_score, 0) * 0.7 AS combined_score
FROM keyword_results k
FULL OUTER JOIN semantic_results s ON k.id = s.id
ORDER BY combined_score DESC
LIMIT 10;
```

### 3. Context Window Optimization

```python
def get_optimized_context(query: str, max_tokens: int = 4000) -> str:
    """Retrieve documentation context within token budget"""
    results = embedder.semantic_search(query, top_k=10)
    
    context = ""
    current_tokens = 0
    
    for result in results:
        # Estimate tokens (rough: 1 token ≈ 4 chars)
        chunk_tokens = len(result['content']) // 4
        
        if current_tokens + chunk_tokens > max_tokens:
            break
        
        context += f"## {result['title']}\n{result['content']}\n\n"
        current_tokens += chunk_tokens
    
    return context
```

---

## Cost Analysis

**One-Time Setup:**
- Embedding generation: ~$0.10 USD (100K tokens @ $0.02/1M)
- Storage: ~50 MB (1500 embeddings × 1536 dims × 4 bytes)

**Ongoing:**
- Query embeddings: $0.00002 per query (100 tokens)
- Storage: Free (Supabase free tier: 500MB)

**Total Estimated Cost:** <$1 USD per year

---

## Next Steps

1. **Expand Coverage:**
   - Add Odoo user documentation
   - Include OCA module documentation
   - Scrape Odoo forum solutions

2. **Improve Search:**
   - Implement hybrid search (keyword + semantic)
   - Add metadata filtering (by module, topic)
   - Enable multi-language support

3. **Integration:**
   - Create Claude Code skill
   - Build Slack bot for team access
   - Add to InsightPulse AI portal

---

**Maintainer:** InsightPulse AI Team
**Repository:** https://github.com/jgtolentino/insightpulse-odoo
**Script:** `scripts/odoo-docs-embeddings.py`
**Database:** Supabase (spdtwktxdalcfigzeqrz)
