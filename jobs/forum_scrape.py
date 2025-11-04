#!/usr/bin/env python3
"""
Forum Scraper - Odoo Community Forum Posts

Runs every 10 minutes via cron:
*/10 * * * * /usr/local/bin/python3 /opt/stack/jobs/forum_scrape.py >> /var/log/forum_scrape.log 2>&1

Fetches posts from Odoo forum, normalizes data, and upserts to mcp.forum_posts table.
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import requests
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Forum API configuration
FORUM_API_BASE = "https://www.odoo.com/forum"
FORUM_TOPICS = [
    "help-1",           # General Help
    "odoo-19",          # Odoo 19.0
    "odoo-18",          # Odoo 18.0
    "accounting-3",     # Accounting
    "development-4",    # Development
]


def get_supabase_client() -> Client:
    """Initialize Supabase client."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def fetch_forum_posts(topic: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch recent posts from Odoo forum topic.

    Args:
        topic: Forum topic identifier (e.g., 'help-1', 'odoo-19')
        limit: Maximum number of posts to fetch

    Returns:
        List of normalized post dictionaries
    """
    url = f"{FORUM_API_BASE}/{topic}?limit={limit}&order=date_desc"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # TODO: Parse HTML or JSON response
        # This is a skeleton - actual implementation depends on forum API format
        posts = []

        logger.info(f"Fetched {len(posts)} posts from {topic}")
        return posts

    except requests.RequestException as e:
        logger.error(f"Error fetching forum posts from {topic}: {e}")
        return []


def normalize_post(raw_post: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize raw forum post to database schema.

    Schema: mcp.forum_posts
    - id (text, PK): Forum post ID
    - topic (text): Forum topic/category
    - title (text): Post title
    - content (text): Post body content
    - author (text): Post author username
    - created_at (timestamptz): Post creation timestamp
    - updated_at (timestamptz): Last update timestamp
    - views (int): View count
    - replies (int): Reply count
    - tags (text[]): Post tags
    - url (text): Direct URL to post
    - metadata (jsonb): Additional metadata
    """
    return {
        "id": raw_post.get("id"),
        "topic": raw_post.get("topic"),
        "title": raw_post.get("title"),
        "content": raw_post.get("content"),
        "author": raw_post.get("author"),
        "created_at": raw_post.get("created_at"),
        "updated_at": raw_post.get("updated_at", raw_post.get("created_at")),
        "views": raw_post.get("views", 0),
        "replies": raw_post.get("replies", 0),
        "tags": raw_post.get("tags", []),
        "url": raw_post.get("url"),
        "metadata": {
            "raw": raw_post,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }
    }


def upsert_posts(client: Client, posts: List[Dict[str, Any]]) -> int:
    """
    Upsert forum posts to mcp.forum_posts table.

    Args:
        client: Supabase client
        posts: List of normalized post dictionaries

    Returns:
        Number of posts upserted
    """
    if not posts:
        return 0

    try:
        result = client.table("forum_posts").upsert(
            posts,
            on_conflict="id"
        ).execute()

        count = len(result.data) if result.data else 0
        logger.info(f"Upserted {count} forum posts")
        return count

    except Exception as e:
        logger.error(f"Error upserting forum posts: {e}")
        return 0


def create_schema_if_needed(client: Client):
    """Create mcp.forum_posts table if it doesn't exist."""
    create_table_sql = """
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

    CREATE INDEX IF NOT EXISTS idx_forum_posts_topic ON mcp.forum_posts(topic);
    CREATE INDEX IF NOT EXISTS idx_forum_posts_created_at ON mcp.forum_posts(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_forum_posts_tags ON mcp.forum_posts USING GIN(tags);
    """

    try:
        # Note: This requires direct SQL execution via psql or pg client
        # Supabase client doesn't support raw SQL DDL
        logger.info("Schema creation should be done manually via psql")

    except Exception as e:
        logger.error(f"Error creating schema: {e}")


def main():
    """Main scraper execution."""
    logger.info("Starting forum scraper...")

    try:
        # Initialize Supabase client
        client = get_supabase_client()
        logger.info("Supabase client initialized")

        # Fetch and process posts from all topics
        total_upserted = 0

        for topic in FORUM_TOPICS:
            logger.info(f"Processing topic: {topic}")

            # Fetch raw posts
            raw_posts = fetch_forum_posts(topic)

            # Normalize posts
            normalized_posts = [normalize_post(post) for post in raw_posts]

            # Upsert to database
            count = upsert_posts(client, normalized_posts)
            total_upserted += count

        logger.info(f"Scraper completed successfully. Total posts upserted: {total_upserted}")
        return 0

    except Exception as e:
        logger.error(f"Fatal error in forum scraper: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
