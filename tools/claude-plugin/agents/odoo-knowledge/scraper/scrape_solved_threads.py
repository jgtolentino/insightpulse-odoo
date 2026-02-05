#!/usr/bin/env python3
"""
Odoo Forum Scraper - Extracts solved issues for prevention/auto-fix
Target: 100 pages of solved custom module issues
Output: Guardrails + Auto-patches
"""
import json
import time
import random
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing playwright...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.sync_api import sync_playwright

BASE_URL = "https://www.odoo.com/forum/help-1"
QUERY = "?filters=solved&search=custom&sorting=last_activity_date+desc"
MAX_PAGES = 100
OUTPUT_DIR = Path(__file__).parent.parent / "knowledge"
OUTPUT_FILE = OUTPUT_DIR / "solved_issues_raw.json"

def scrape_forum_pages():
    """Scrape solved thread listings from Odoo forum"""
    results = []

    with sync_playwright() as p:
        print("🚀 Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(15000)

        start_url = f"{BASE_URL}{QUERY}"
        print(f"📍 Starting: {start_url}")
        page.goto(start_url)

        for page_idx in range(MAX_PAGES):
            print(f"📄 Scraping page {page_idx + 1}/{MAX_PAGES}...")

            try:
                # Wait for content to load
                page.wait_for_selector("table tr", timeout=10000)
                rows = page.query_selector_all("table tr")[1:]  # Skip header

                for row in rows:
                    link = row.query_selector("td a")
                    if not link:
                        continue

                    title = link.inner_text().strip()
                    path = link.get_attribute("href")
                    url = f"https://www.odoo.com{path}" if path.startswith("/") else path

                    # Extract tags
                    tags = [
                        t.inner_text().strip()
                        for t in row.query_selector_all("td a")[1:]
                    ]

                    results.append({
                        "title": title,
                        "url": url,
                        "tags": tags,
                        "page": page_idx + 1
                    })

                print(f"   ✅ Collected {len([r for r in results if r['page'] == page_idx + 1])} issues")

                # Find and click next page
                next_btn = page.query_selector("a[rel='next']")
                if not next_btn:
                    print("✅ Reached last page")
                    break

                next_btn.click()
                # Random delay to avoid rate limiting
                time.sleep(random.uniform(1.5, 3.0))

            except Exception as e:
                print(f"⚠️  Error on page {page_idx + 1}: {e}")
                continue

        browser.close()

    print(f"\n✅ Total collected: {len(results)} solved issues")
    return results

def save_results(data):
    """Save scraped data to JSON"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"💾 Saved to: {OUTPUT_FILE}")
    print(f"📊 Stats:")
    print(f"   - Total issues: {len(data)}")
    print(f"   - Pages scraped: {max(d['page'] for d in data)}")

    # Count by tag
    tag_counts = {}
    for issue in data:
        for tag in issue['tags']:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print(f"   - Top tags: {dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5])}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Odoo Forum Scraper - Solved Issues Only")
    print("=" * 60)

    data = scrape_forum_pages()
    save_results(data)

    print("\n✅ Scraping complete!")
    print(f"Next step: Run process_solutions.py to extract fixes")
