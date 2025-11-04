-- MCP Forum Posts Table
-- Schema: mcp.forum_posts
-- Purpose: Store scraped Odoo community forum posts for MCP knowledge base

CREATE SCHEMA IF NOT EXISTS mcp;

CREATE TABLE IF NOT EXISTS mcp.forum_posts (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    author TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    views INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    tags TEXT[],
    url TEXT,
    metadata JSONB,
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_forum_posts_topic ON mcp.forum_posts(topic);
CREATE INDEX IF NOT EXISTS idx_forum_posts_created_at ON mcp.forum_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forum_posts_tags ON mcp.forum_posts USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_forum_posts_author ON mcp.forum_posts(author);
CREATE INDEX IF NOT EXISTS idx_forum_posts_scraped_at ON mcp.forum_posts(scraped_at DESC);

-- Full-text search index on title and content
CREATE INDEX IF NOT EXISTS idx_forum_posts_search ON mcp.forum_posts
USING GIN(to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(content, '')));

-- Comments
COMMENT ON TABLE mcp.forum_posts IS 'Odoo community forum posts scraped for MCP knowledge base';
COMMENT ON COLUMN mcp.forum_posts.id IS 'Unique forum post identifier';
COMMENT ON COLUMN mcp.forum_posts.topic IS 'Forum topic/category (e.g., help-1, odoo-19)';
COMMENT ON COLUMN mcp.forum_posts.title IS 'Post title';
COMMENT ON COLUMN mcp.forum_posts.content IS 'Post body content';
COMMENT ON COLUMN mcp.forum_posts.author IS 'Post author username';
COMMENT ON COLUMN mcp.forum_posts.created_at IS 'Post creation timestamp';
COMMENT ON COLUMN mcp.forum_posts.updated_at IS 'Last update timestamp';
COMMENT ON COLUMN mcp.forum_posts.views IS 'View count';
COMMENT ON COLUMN mcp.forum_posts.replies IS 'Reply count';
COMMENT ON COLUMN mcp.forum_posts.tags IS 'Post tags array';
COMMENT ON COLUMN mcp.forum_posts.url IS 'Direct URL to post';
COMMENT ON COLUMN mcp.forum_posts.metadata IS 'Additional metadata (raw post data, scraping metadata)';
COMMENT ON COLUMN mcp.forum_posts.scraped_at IS 'Timestamp when post was scraped';

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON mcp.forum_posts TO svc_mcp;
