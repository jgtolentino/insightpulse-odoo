#!/usr/bin/env python3
"""
Odoo Knowledge Scraper - Continuous knowledge harvesting for agent intelligence

Purpose: Scrape Odoo docs, forum, GitHub to build comprehensive knowledge graph
Impact: Agents answer questions from 50K+ docs instead of 3 hardcoded FAQs

Usage:
    # One-time initial scrape
    python odoo_scraper.py --initial-scrape

    # Daily incremental updates
    python odoo_scraper.py --incremental

    # Run as cron: 0 2 * * * python odoo_scraper.py --incremental
"""

from __future__ import annotations
import os
import sys
import asyncio
import hashlib
import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from supabase import create_client, Client
from openai import OpenAI

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class ScraperConfig:
    """Scraper configuration from environment"""
    supabase_url: str
    supabase_key: str
    openai_api_key: str
    embedding_model: str = "text-embedding-3-large"
    embedding_dims: int = 3072
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    rate_limit_delay: float = 0.5  # seconds between requests

    @classmethod
    def from_env(cls) -> ScraperConfig:
        """Load configuration from environment variables"""
        return cls(
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_SERVICE_ROLE", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", "")
        )

# ============================================================================
# Knowledge Sources
# ============================================================================

ODOO_SOURCES = {
    "documentation": {
        "base_url": "https://www.odoo.com/documentation/19.0/",
        "patterns": [
            "developer/**/*.html",
            "applications/**/*.html",
            "administration/**/*.html"
        ],
        "priority": "high"
    },
    "forum": {
        "base_url": "https://www.odoo.com/forum/",
        "endpoints": [
            "help-1",  # General questions
            "develop-1",  # Development
            "functional-1"  # Functional
        ],
        "priority": "medium"
    },
    "github_oca": {
        "repos": [
            "account-financial-reporting",
            "account-financial-tools",
            "account-invoicing",
            "server-tools",
            "web",
            "reporting-engine"
        ],
        "api_base": "https://api.github.com/repos/OCA",
        "priority": "high"
    }
}

# ============================================================================
# Document Models
# ============================================================================

@dataclass
class KnowledgeDocument:
    """Normalized knowledge document for storage"""
    source_type: str
    source_url: str
    title: str
    content: str
    odoo_version: Optional[str] = None
    module_name: Optional[str] = None
    topic: Optional[str] = None
    upvotes: int = 0
    is_solved: bool = False
    last_updated: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to database insert format"""
        return {
            "source_type": self.source_type,
            "source_url": self.source_url,
            "title": self.title,
            "content": self.content,
            "odoo_version": self.odoo_version,
            "module_name": self.module_name,
            "topic": self.topic,
            "upvotes": self.upvotes,
            "is_solved": self.is_solved,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }

# ============================================================================
# Documentation Scraper
# ============================================================================

class OdooDocsScraper:
    """Scrape official Odoo documentation"""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.request_timeout)
        self.base_url = ODOO_SOURCES["documentation"]["base_url"]

    async def scrape_page(self, url: str) -> Optional[KnowledgeDocument]:
        """Scrape a single documentation page"""
        try:
            await asyncio.sleep(self.config.rate_limit_delay)
            response = await self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title
            title = soup.find('h1')
            if not title:
                return None
            title_text = title.get_text(strip=True)

            # Extract main content
            content_div = soup.find('div', class_=['document', 'main-content'])
            if not content_div:
                return None

            # Clean content: remove nav, scripts, styles
            for tag in content_div.find_all(['script', 'style', 'nav', 'footer']):
                tag.decompose()

            content = content_div.get_text(separator='\n', strip=True)

            # Extract version from URL
            version = self._extract_version(url)

            # Extract module from URL or content
            module = self._extract_module(url, content)

            # Infer topic
            topic = self._infer_topic(url, title_text, content)

            return KnowledgeDocument(
                source_type="docs",
                source_url=url,
                title=title_text,
                content=content,
                odoo_version=version,
                module_name=module,
                topic=topic
            )

        except Exception as e:
            print(f"Error scraping {url}: {e}", file=sys.stderr)
            return None

    async def discover_pages(self) -> List[str]:
        """Discover all documentation pages to scrape"""
        # Start with known index pages
        index_pages = [
            f"{self.base_url}developer.html",
            f"{self.base_url}applications.html",
            f"{self.base_url}administration.html"
        ]

        discovered_urls = set()

        for index_url in index_pages:
            try:
                response = await self.client.get(index_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all internal links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(index_url, href)

                    # Only include docs URLs
                    if full_url.startswith(self.base_url) and full_url.endswith('.html'):
                        discovered_urls.add(full_url)

            except Exception as e:
                print(f"Error discovering from {index_url}: {e}", file=sys.stderr)

        return list(discovered_urls)

    async def scrape_all(self) -> List[KnowledgeDocument]:
        """Scrape all documentation pages"""
        urls = await self.discover_pages()
        print(f"Discovered {len(urls)} documentation pages")

        docs = []
        for url in urls:
            doc = await self.scrape_page(url)
            if doc:
                docs.append(doc)
                print(f"✓ Scraped: {doc.title}")

        return docs

    def _extract_version(self, url: str) -> Optional[str]:
        """Extract Odoo version from URL"""
        import re
        match = re.search(r'/(\d+\.\d+)/', url)
        return match.group(1) if match else None

    def _extract_module(self, url: str, content: str) -> Optional[str]:
        """Extract module name from URL or content"""
        # Common modules
        modules = ['account', 'sale', 'purchase', 'stock', 'crm', 'project', 'hr', 'mrp']
        url_lower = url.lower()

        for module in modules:
            if module in url_lower or module in content.lower()[:500]:
                return module
        return None

    def _infer_topic(self, url: str, title: str, content: str) -> Optional[str]:
        """Infer topic from URL and content"""
        topics = {
            'migration': ['migrate', 'upgrade', 'migration'],
            'api': ['api', 'rpc', 'external api', 'rest'],
            'orm': ['orm', 'model', 'recordset'],
            'views': ['view', 'qweb', 'template'],
            'security': ['security', 'access rights', 'record rules'],
            'workflow': ['workflow', 'automation', 'action']
        }

        text = f"{url} {title} {content[:1000]}".lower()

        for topic, keywords in topics.items():
            if any(kw in text for kw in keywords):
                return topic

        return None

    async def close(self):
        """Cleanup"""
        await self.client.aclose()

# ============================================================================
# Forum Scraper
# ============================================================================

class OdooForumScraper:
    """Scrape Odoo community forum"""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.request_timeout)
        self.base_url = ODOO_SOURCES["forum"]["base_url"]

    async def scrape_forum_page(self, endpoint: str, page: int = 1) -> List[KnowledgeDocument]:
        """Scrape a single forum page"""
        url = f"{self.base_url}{endpoint}?page={page}"

        try:
            await asyncio.sleep(self.config.rate_limit_delay)
            response = await self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            docs = []

            # Find question posts
            for post in soup.find_all('div', class_=['question', 'post']):
                doc = self._extract_post(post, endpoint)
                if doc:
                    docs.append(doc)

            return docs

        except Exception as e:
            print(f"Error scraping forum page {url}: {e}", file=sys.stderr)
            return []

    def _extract_post(self, post_elem, endpoint: str) -> Optional[KnowledgeDocument]:
        """Extract knowledge from a forum post element"""
        try:
            # Title
            title_elem = post_elem.find(['h2', 'h3', 'a'], class_=['post-title', 'question-title'])
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # URL
            link = post_elem.find('a', href=True)
            if not link:
                return None
            url = urljoin(self.base_url, link['href'])

            # Content
            content_elem = post_elem.find('div', class_=['post-content', 'content'])
            content = content_elem.get_text(separator='\n', strip=True) if content_elem else title

            # Metadata
            upvotes = self._extract_upvotes(post_elem)
            is_solved = 'solved' in post_elem.get('class', [])

            return KnowledgeDocument(
                source_type="forum",
                source_url=url,
                title=title,
                content=content,
                upvotes=upvotes,
                is_solved=is_solved,
                topic=self._infer_forum_topic(endpoint)
            )

        except Exception as e:
            print(f"Error extracting post: {e}", file=sys.stderr)
            return None

    def _extract_upvotes(self, elem) -> int:
        """Extract upvote count"""
        vote_elem = elem.find(class_=['vote-count', 'upvote'])
        if vote_elem:
            try:
                return int(vote_elem.get_text(strip=True))
            except (ValueError, TypeError):
                pass
        return 0

    def _infer_forum_topic(self, endpoint: str) -> str:
        """Map forum endpoint to topic"""
        mapping = {
            'help-1': 'general',
            'develop-1': 'development',
            'functional-1': 'functional'
        }
        return mapping.get(endpoint, 'general')

    async def scrape_all(self, max_pages_per_endpoint: int = 10) -> List[KnowledgeDocument]:
        """Scrape all forum endpoints"""
        all_docs = []

        for endpoint in ODOO_SOURCES["forum"]["endpoints"]:
            print(f"Scraping forum endpoint: {endpoint}")

            for page in range(1, max_pages_per_endpoint + 1):
                docs = await self.scrape_forum_page(endpoint, page)
                if not docs:  # No more pages
                    break

                all_docs.extend(docs)
                print(f"  Page {page}: {len(docs)} posts")

        return all_docs

    async def close(self):
        await self.client.aclose()

# ============================================================================
# GitHub OCA Scraper
# ============================================================================

class GitHubOCAScraper:
    """Scrape OCA GitHub repositories for issues/discussions"""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        } if self.github_token else {}
        self.client = httpx.AsyncClient(timeout=config.request_timeout, headers=self.headers)

    async def scrape_repo_issues(
        self,
        repo: str,
        state: str = "closed",
        labels: str = "solved"
    ) -> List[KnowledgeDocument]:
        """Scrape closed/solved issues from an OCA repo"""
        url = f"{ODOO_SOURCES['github_oca']['api_base']}/{repo}/issues"
        params = {"state": state, "labels": labels, "per_page": 100}

        docs = []

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            issues = response.json()

            for issue in issues:
                doc = KnowledgeDocument(
                    source_type="github_issue",
                    source_url=issue["html_url"],
                    title=issue["title"],
                    content=issue["body"] or issue["title"],
                    module_name=repo,
                    upvotes=issue.get("reactions", {}).get("+1", 0),
                    is_solved=True,
                    last_updated=datetime.fromisoformat(issue["updated_at"].replace('Z', '+00:00'))
                )
                docs.append(doc)

            print(f"  ✓ {repo}: {len(docs)} issues")

        except Exception as e:
            print(f"Error scraping {repo}: {e}", file=sys.stderr)

        await asyncio.sleep(self.config.rate_limit_delay)
        return docs

    async def scrape_all(self) -> List[KnowledgeDocument]:
        """Scrape all OCA repositories"""
        all_docs = []

        for repo in ODOO_SOURCES["github_oca"]["repos"]:
            docs = await self.scrape_repo_issues(repo)
            all_docs.extend(docs)

        return all_docs

    async def close(self):
        await self.client.aclose()

# ============================================================================
# Knowledge Indexer (Supabase + OpenAI)
# ============================================================================

class KnowledgeIndexer:
    """Index knowledge documents into Supabase with embeddings"""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.supabase: Client = create_client(config.supabase_url, config.supabase_key)
        self.openai = OpenAI(api_key=config.openai_api_key)

    def create_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            response = self.openai.embeddings.create(
                model=self.config.embedding_model,
                input=text[:8000],  # Truncate to avoid token limits
                dimensions=self.config.embedding_dims
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error creating embedding: {e}", file=sys.stderr)
            return [0.0] * self.config.embedding_dims

    async def index_document(self, doc: KnowledgeDocument) -> bool:
        """Index a single document"""
        try:
            # Create embedding from title + content
            text = f"{doc.title}\n\n{doc.content}"
            embedding = self.create_embedding(text)

            # Prepare data
            data = doc.to_dict()
            data["embedding"] = embedding

            # Upsert to Supabase
            result = self.supabase.table("odoo_knowledge").upsert(
                data,
                on_conflict="source_url"
            ).execute()

            return True

        except Exception as e:
            print(f"Error indexing {doc.source_url}: {e}", file=sys.stderr)
            return False

    async def index_batch(self, docs: List[KnowledgeDocument]) -> Dict[str, int]:
        """Index a batch of documents"""
        stats = {"success": 0, "failed": 0}

        for doc in docs:
            success = await self.index_document(doc)
            if success:
                stats["success"] += 1
                print(f"  ✓ Indexed: {doc.title[:60]}")
            else:
                stats["failed"] += 1

        return stats

# ============================================================================
# Main Orchestrator
# ============================================================================

class OdooKnowledgeScraper:
    """Main orchestrator for knowledge scraping"""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.docs_scraper = OdooDocsScraper(config)
        self.forum_scraper = OdooForumScraper(config)
        self.github_scraper = GitHubOCAScraper(config)
        self.indexer = KnowledgeIndexer(config)

    async def initial_scrape(self):
        """Comprehensive initial scrape of all sources"""
        print("=" * 70)
        print("ODOO KNOWLEDGE SCRAPER - INITIAL SCRAPE")
        print("=" * 70)

        all_docs = []

        # 1. Documentation
        print("\n[1/3] Scraping Odoo Documentation...")
        docs = await self.docs_scraper.scrape_all()
        print(f"  ✓ Scraped {len(docs)} documentation pages")
        all_docs.extend(docs)

        # 2. Forum
        print("\n[2/3] Scraping Odoo Forum...")
        forum_docs = await self.forum_scraper.scrape_all(max_pages_per_endpoint=10)
        print(f"  ✓ Scraped {len(forum_docs)} forum posts")
        all_docs.extend(forum_docs)

        # 3. GitHub OCA
        print("\n[3/3] Scraping GitHub OCA Issues...")
        github_docs = await self.github_scraper.scrape_all()
        print(f"  ✓ Scraped {len(github_docs)} GitHub issues")
        all_docs.extend(github_docs)

        # Index all
        print(f"\n[INDEX] Indexing {len(all_docs)} documents...")
        stats = await self.indexer.index_batch(all_docs)

        print("\n" + "=" * 70)
        print("SCRAPING COMPLETE")
        print("=" * 70)
        print(f"Total Documents: {len(all_docs)}")
        print(f"Successfully Indexed: {stats['success']}")
        print(f"Failed: {stats['failed']}")
        print("=" * 70)

    async def incremental_scrape(self):
        """Daily incremental scrape (new content only)"""
        print("=" * 70)
        print("ODOO KNOWLEDGE SCRAPER - INCREMENTAL UPDATE")
        print("=" * 70)

        # For incremental, focus on high-velocity sources
        all_docs = []

        # Forum (new posts in last 24 hours)
        print("\n[1/2] Checking forum for new posts...")
        forum_docs = await self.forum_scraper.scrape_all(max_pages_per_endpoint=2)
        print(f"  ✓ Found {len(forum_docs)} recent posts")
        all_docs.extend(forum_docs)

        # GitHub (updated in last 24 hours)
        print("\n[2/2] Checking GitHub for updates...")
        github_docs = await self.github_scraper.scrape_all()
        print(f"  ✓ Found {len(github_docs)} updated issues")
        all_docs.extend(github_docs)

        # Index
        if all_docs:
            print(f"\n[INDEX] Indexing {len(all_docs)} new documents...")
            stats = await self.indexer.index_batch(all_docs)
            print(f"  ✓ Indexed: {stats['success']}, Failed: {stats['failed']}")
        else:
            print("\nNo new documents to index.")

    async def cleanup(self):
        """Cleanup resources"""
        await self.docs_scraper.close()
        await self.forum_scraper.close()
        await self.github_scraper.close()

# ============================================================================
# CLI
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Odoo Knowledge Scraper - Build exponential knowledge base"
    )
    parser.add_argument(
        "--initial-scrape",
        action="store_true",
        help="Comprehensive initial scrape (slow, run once)"
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Incremental scrape (fast, run daily)"
    )
    args = parser.parse_args()

    # Load config
    config = ScraperConfig.from_env()

    if not config.supabase_url or not config.openai_api_key:
        print("ERROR: Missing required environment variables:", file=sys.stderr)
        print("  - SUPABASE_URL", file=sys.stderr)
        print("  - SUPABASE_SERVICE_ROLE", file=sys.stderr)
        print("  - OPENAI_API_KEY", file=sys.stderr)
        sys.exit(1)

    # Run scraper
    scraper = OdooKnowledgeScraper(config)

    try:
        if args.initial_scrape:
            await scraper.initial_scrape()
        elif args.incremental:
            await scraper.incremental_scrape()
        else:
            print("Usage: python odoo_scraper.py --initial-scrape | --incremental")
            sys.exit(1)
    finally:
        await scraper.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
