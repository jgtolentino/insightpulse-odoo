#!/usr/bin/env python3
"""
Odoo Forum Scraper - Firecrawl Edition
Production-grade scraper using Firecrawl API for reliability

Benefits over Playwright:
- No browser overhead
- Built-in proxy rotation
- Automatic markdown conversion
- Better rate limiting
- No 403 errors from forum
- Handles JavaScript rendering
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from firecrawl import FirecrawlApp
except ImportError:
    print("Installing firecrawl-py...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "firecrawl-py"])
    from firecrawl import FirecrawlApp

try:
    from supabase import create_client, Client
except ImportError:
    print("Installing supabase...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase"])
    from supabase import create_client, Client

# Configuration
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

FORUM_BASE_URL = "https://www.odoo.com/forum/help-1"
MAX_PAGES = 100
OUTPUT_DIR = Path(__file__).parent.parent / "knowledge"
OUTPUT_FILE = OUTPUT_DIR / "solved_issues_raw.json"


class FirecrawlOdooScraper:
    """
    Odoo forum scraper using Firecrawl for production reliability
    """

    def __init__(self, api_key: str = None, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize Firecrawl scraper

        Args:
            api_key: Firecrawl API key (get from firecrawl.dev)
            supabase_url: Supabase project URL
            supabase_key: Supabase service role key
        """
        self.api_key = api_key or FIRECRAWL_API_KEY
        if not self.api_key:
            raise ValueError(
                "FIRECRAWL_API_KEY not set. Get one from https://firecrawl.dev"
            )

        self.firecrawl = FirecrawlApp(api_key=self.api_key)

        # Supabase for knowledge storage
        if supabase_url and supabase_key:
            self.supabase = create_client(supabase_url, supabase_key)
        else:
            self.supabase = None

        self.results = []

    def scrape_forum_page(self, page_num: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape a single forum page for solved threads

        Args:
            page_num: Page number to scrape

        Returns:
            List of thread metadata (title, URL, tags)
        """
        # Construct URL with filters
        url = f"{FORUM_BASE_URL}?filters=solved&search=custom&sorting=last_activity_date+desc&page={page_num}"

        print(f"📄 Scraping page {page_num}: {url}")

        try:
            # Firecrawl scrapes and returns clean markdown
            result = self.firecrawl.scrape_url(
                url,
                params={
                    'formats': ['markdown', 'html'],
                    'onlyMainContent': True,
                    'waitFor': 2000,  # Wait for JavaScript
                }
            )

            # Parse thread listings from result
            threads = self._parse_thread_listings(result)

            print(f"   ✅ Found {len(threads)} threads")
            return threads

        except Exception as e:
            print(f"   ❌ Error scraping page {page_num}: {e}")
            return []

    def _parse_thread_listings(self, scrape_result: Dict) -> List[Dict[str, Any]]:
        """
        Extract thread metadata from Firecrawl result

        Args:
            scrape_result: Firecrawl API response

        Returns:
            List of thread dictionaries
        """
        threads = []

        # Firecrawl returns clean markdown - easier to parse
        markdown = scrape_result.get('markdown', '')
        html = scrape_result.get('html', '')

        # Parse thread links from markdown
        # Format: [Thread Title](https://www.odoo.com/forum/help-1/thread-12345)
        import re

        # Match forum thread URLs
        pattern = r'\[([^\]]+)\]\((https://www\.odoo\.com/forum/[^)]+)\)'
        matches = re.findall(pattern, markdown)

        for title, url in matches:
            # Only include "solved" threads
            if 'solved' in markdown.lower() or 'answered' in markdown.lower():
                threads.append({
                    'title': title.strip(),
                    'url': url,
                    'tags': self._extract_tags_from_context(markdown, title),
                    'scraped_at': datetime.now().isoformat()
                })

        return threads

    def _extract_tags_from_context(self, markdown: str, title: str) -> List[str]:
        """
        Extract tags from thread context

        Args:
            markdown: Page markdown content
            title: Thread title

        Returns:
            List of tags
        """
        tags = []

        # Common Odoo tags
        tag_keywords = {
            'pos': ['pos', 'point of sale'],
            'accounting': ['accounting', 'invoice', 'payment'],
            'portal': ['portal', 'customer'],
            'website': ['website', 'ecommerce'],
            'inventory': ['inventory', 'stock', 'warehouse'],
            'manufacturing': ['manufacturing', 'mrp'],
            'sales': ['sales', 'crm', 'quotation'],
        }

        title_lower = title.lower()
        markdown_lower = markdown.lower()

        for tag, keywords in tag_keywords.items():
            if any(keyword in title_lower or keyword in markdown_lower for keyword in keywords):
                tags.append(tag)

        return tags

    def scrape_thread_details(self, thread_url: str) -> Dict[str, Any]:
        """
        Scrape individual thread for question, answer, and code

        Args:
            thread_url: Full URL to forum thread

        Returns:
            Thread details including accepted answer and code blocks
        """
        print(f"   🔍 Scraping thread: {thread_url}")

        try:
            result = self.firecrawl.scrape_url(
                thread_url,
                params={
                    'formats': ['markdown'],
                    'onlyMainContent': True,
                    'waitFor': 2000,
                }
            )

            markdown = result.get('markdown', '')

            # Parse question and answer from markdown
            details = self._parse_thread_content(markdown, thread_url)

            return details

        except Exception as e:
            print(f"   ❌ Error scraping thread {thread_url}: {e}")
            return {
                'url': thread_url,
                'error': str(e)
            }

    def _parse_thread_content(self, markdown: str, url: str) -> Dict[str, Any]:
        """
        Extract question, answer, and code from thread markdown

        Args:
            markdown: Thread content in markdown
            url: Thread URL

        Returns:
            Parsed thread content
        """
        # Split by common section markers
        sections = markdown.split('\n\n')

        question = ""
        answer = ""
        code_blocks = []

        # Extract code blocks
        import re
        code_pattern = r'```[\w]*\n(.*?)```'
        code_blocks = re.findall(code_pattern, markdown, re.DOTALL)

        # Simple heuristic: First large section = question, next = answer
        # (Can be improved with ML classification)
        if len(sections) >= 2:
            question = sections[0]
            answer = '\n\n'.join(sections[1:3])  # Next 2 sections

        return {
            'url': url,
            'question': question.strip()[:1000],  # Limit size
            'answer': answer.strip()[:2000],
            'code_blocks': code_blocks,
            'markdown': markdown[:5000],  # Store full markdown (limited)
            'scraped_at': datetime.now().isoformat()
        }

    def scrape_all_pages(self, max_pages: int = MAX_PAGES) -> List[Dict[str, Any]]:
        """
        Scrape multiple forum pages

        Args:
            max_pages: Maximum number of pages to scrape

        Returns:
            All scraped threads
        """
        all_threads = []

        for page in range(1, max_pages + 1):
            print(f"\n{'='*60}")
            print(f"Page {page}/{max_pages}")
            print(f"{'='*60}")

            # Get thread listings
            threads = self.scrape_forum_page(page)

            # Scrape details for each thread (with rate limiting)
            for i, thread in enumerate(threads, 1):
                print(f"  [{i}/{len(threads)}] {thread['title'][:60]}...")

                # Get full thread details
                details = self.scrape_thread_details(thread['url'])

                # Merge metadata + details
                full_thread = {**thread, **details}
                all_threads.append(full_thread)

                # Store in Supabase if configured
                if self.supabase:
                    self._store_in_supabase(full_thread)

                # Rate limiting - Firecrawl has built-in limits
                time.sleep(1)  # Be polite

            # Pause between pages
            time.sleep(2)

        self.results = all_threads
        return all_threads

    def _store_in_supabase(self, thread: Dict[str, Any]):
        """
        Store thread in Supabase knowledge base

        Args:
            thread: Thread data to store
        """
        if not self.supabase:
            return

        try:
            self.supabase.table('mcp.forum_posts').upsert({
                'id': thread['url'],  # Use URL as unique ID
                'topic': 'help-1',
                'title': thread['title'],
                'content': thread.get('answer', ''),
                'metadata': {
                    'question': thread.get('question', ''),
                    'code_blocks': thread.get('code_blocks', []),
                    'tags': thread.get('tags', []),
                    'scraped_at': thread.get('scraped_at'),
                },
                'url': thread['url'],
                'tags': thread.get('tags', []),
                'created_at': thread.get('scraped_at'),
                'updated_at': thread.get('scraped_at'),
            }).execute()

        except Exception as e:
            print(f"   ⚠️  Error storing in Supabase: {e}")

    def save_to_json(self, output_file: Path = OUTPUT_FILE):
        """
        Save scraped threads to JSON file

        Args:
            output_file: Path to output JSON file
        """
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Saved {len(self.results)} threads to: {output_file}")

        # Generate stats
        self._print_stats()

    def _print_stats(self):
        """Print scraping statistics"""
        if not self.results:
            return

        print(f"\n{'='*60}")
        print("📊 SCRAPING STATISTICS")
        print(f"{'='*60}")
        print(f"Total threads scraped: {len(self.results)}")

        # Count tags
        tag_counts = {}
        for thread in self.results:
            for tag in thread.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        print(f"\nTop tags:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {tag}: {count}")

        # Count with code blocks
        with_code = sum(1 for t in self.results if t.get('code_blocks'))
        print(f"\nThreads with code examples: {with_code} ({with_code/len(self.results)*100:.1f}%)")


def main():
    """Main scraper execution"""
    print("🔥 Firecrawl Odoo Forum Scraper")
    print("="*60)

    # Check environment
    if not FIRECRAWL_API_KEY:
        print("❌ FIRECRAWL_API_KEY not set!")
        print("Get API key from: https://firecrawl.dev")
        print("\nThen run:")
        print("  export FIRECRAWL_API_KEY='your_api_key_here'")
        return 1

    # Initialize scraper
    scraper = FirecrawlOdooScraper(
        api_key=FIRECRAWL_API_KEY,
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY
    )

    # Scrape forum
    print(f"\n🎯 Target: {MAX_PAGES} pages of solved threads\n")

    threads = scraper.scrape_all_pages(max_pages=MAX_PAGES)

    # Save results
    scraper.save_to_json()

    print(f"\n✅ Scraping complete!")
    print(f"Next step: Process solutions with AI")
    print(f"  python process_solutions.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
