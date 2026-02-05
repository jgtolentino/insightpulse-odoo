#!/usr/bin/env python3
"""
Odoo Forum Scraper - Simple version using requests (no browser needed)
Target: 100 pages of solved custom module issues
Output: Guardrails + Auto-patches
"""
import json
import time
import random
import sys
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"])
    import requests
    from bs4 import BeautifulSoup

BASE_URL = "https://www.odoo.com/forum/help-1"
MAX_PAGES = 100
OUTPUT_DIR = Path(__file__).parent.parent / "knowledge"
OUTPUT_FILE = OUTPUT_DIR / "solved_issues_raw.json"

# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

def scrape_forum_pages():
    """Scrape solved thread listings from Odoo forum"""
    results = []
    session = requests.Session()
    session.headers.update(HEADERS)

    print("=" * 60)
    print("🔍 Odoo Forum Scraper - Solved Issues Only")
    print("=" * 60)

    # Start with search for solved custom issues
    current_page = 1

    while current_page <= MAX_PAGES:
        # Build URL for current page
        if current_page == 1:
            url = f"{BASE_URL}?filters=solved&search=custom&sorting=last_activity_date+desc"
        else:
            url = f"{BASE_URL}/page/{current_page}?filters=solved&search=custom&sorting=last_activity_date+desc"

        print(f"\n📄 Scraping page {current_page}/{MAX_PAGES}...")
        print(f"   URL: {url}")

        try:
            # Fetch the page
            response = session.get(url, timeout=15)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # Find all thread rows
            thread_rows = soup.select('table.table tr')

            if not thread_rows or len(thread_rows) <= 1:
                print("   ⚠️  No threads found, might be last page")
                break

            page_count = 0

            for row in thread_rows[1:]:  # Skip header row
                # Find the main link
                link_elem = row.select_one('td a')
                if not link_elem:
                    continue

                title = link_elem.get_text(strip=True)
                href = link_elem.get('href', '')

                if not href:
                    continue

                # Build full URL
                full_url = urljoin(BASE_URL, href)

                # Extract tags (other links in the row)
                tag_links = row.select('td a')[1:]
                tags = [tag.get_text(strip=True) for tag in tag_links if tag.get_text(strip=True)]

                results.append({
                    "title": title,
                    "url": full_url,
                    "tags": tags,
                    "page": current_page
                })

                page_count += 1

            print(f"   ✅ Collected {page_count} issues from this page")

            # Check for next page link
            next_link = soup.select_one('a[rel="next"]')
            if not next_link:
                print("\n✅ Reached last page (no more 'next' link)")
                break

            current_page += 1

            # Random delay to avoid rate limiting
            delay = random.uniform(1.5, 3.5)
            time.sleep(delay)

        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Error fetching page: {e}")
            # Continue to next page
            current_page += 1
            time.sleep(5)
            continue

        except Exception as e:
            print(f"   ⚠️  Unexpected error: {e}")
            current_page += 1
            continue

    print(f"\n{'=' * 60}")
    print(f"✅ Total collected: {len(results)} solved issues")
    print(f"{'=' * 60}")
    return results

def save_results(data):
    """Save scraped data to JSON"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n💾 Saved to: {OUTPUT_FILE}")
    print(f"\n📊 Statistics:")
    print(f"   - Total issues: {len(data)}")
    print(f"   - Pages scraped: {max(d['page'] for d in data) if data else 0}")

    # Count by tag
    tag_counts = {}
    for issue in data:
        for tag in issue['tags']:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    if tag_counts:
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"\n   - Top 10 tags:")
        for tag, count in top_tags:
            print(f"      • {tag}: {count}")

if __name__ == "__main__":
    print("\n🚀 Starting scraper...")

    data = scrape_forum_pages()
    save_results(data)

    print("\n" + "=" * 60)
    print("✅ Scraping complete!")
    print("=" * 60)
    print(f"\nNext step: Run process_solutions.py to extract fixes")
