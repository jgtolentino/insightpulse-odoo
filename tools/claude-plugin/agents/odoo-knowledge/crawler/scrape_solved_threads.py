#!/usr/bin/env python3
"""
Odoo Forum Scraper - Solved Threads Only
Extracts troubleshooting knowledge for auto-patching and prevention guardrails
"""

import json
import time
import random
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.odoo.com/forum/help-1"
SOLVED_FILTER = "?filters=solved&search=custom&sorting=last_activity_date+desc"
MAX_PAGES = 100
OUTPUT_DIR = Path(__file__).parent.parent / "knowledge"

def scrape_solved_threads():
    """Scrape solved custom module threads from Odoo forum"""
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(15000)

        print(f"🔍 Starting scrape: {MAX_PAGES} pages")
        page.goto(BASE_URL + SOLVED_FILTER)

        for page_num in range(1, MAX_PAGES + 1):
            print(f"📄 Scraping page {page_num}/{MAX_PAGES}")

            try:
                # Wait for content
                page.wait_for_selector("table tr", timeout=10000)
                rows = page.query_selector_all("table tr")[1:]  # Skip header

                for row in rows:
                    try:
                        link = row.query_selector("td a")
                        if not link:
                            continue

                        title = link.inner_text().strip()
                        path = link.get_attribute("href")
                        url = f"https://www.odoo.com{path}" if path else None

                        if not url:
                            continue

                        # Extract tags
                        tags = [
                            t.inner_text().strip()
                            for t in row.query_selector_all("td a")[1:]
                            if t.inner_text().strip()
                        ]

                        results.append({
                            "title": title,
                            "url": url,
                            "tags": tags,
                            "page": page_num
                        })
                    except Exception as e:
                        print(f"⚠️  Error parsing row: {e}")
                        continue

                # Navigate to next page
                next_btn = page.query_selector("a[rel='next']")
                if not next_btn:
                    print("✅ Reached last page")
                    break

                next_btn.click()
                time.sleep(random.uniform(1.5, 3.0))  # Rate limiting

            except Exception as e:
                print(f"❌ Error on page {page_num}: {e}")
                break

        browser.close()

    print(f"✅ Scraped {len(results)} solved threads")
    return results

def save_results(data):
    """Save scraped data to JSON"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "solved_threads_raw.json"

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"💾 Saved to {output_file}")
    return output_file

if __name__ == "__main__":
    threads = scrape_solved_threads()
    save_results(threads)
