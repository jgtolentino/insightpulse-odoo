#!/usr/bin/env python3
"""
Solution Processor - Simple version using requests (no browser)
Extracts fixes and converts to guardrails/patches
"""
import json
import re
import time
import random
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"])
    import requests
    from bs4 import BeautifulSoup

INPUT_FILE = Path(__file__).parent.parent / "knowledge" / "solved_issues_raw.json"
OUTPUT_FILE = Path(__file__).parent.parent / "knowledge" / "solutions_processed.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def clean_text(text):
    """Clean and normalize text"""
    return re.sub(r"\s+", " ", text).strip()

def extract_code_blocks(soup):
    """Extract code snippets from BeautifulSoup"""
    code_blocks = []

    # Find <pre> and <code> tags
    for pre in soup.find_all(['pre', 'code']):
        code = pre.get_text()
        if code and len(code.strip()) > 10:
            code_blocks.append(code.strip())

    return code_blocks

def categorize_issue(title, tags, body):
    """Categorize issue type and module"""
    title_lower = title.lower()
    body_lower = body.lower()

    # Module detection
    module = "unknown"
    if "pos" in tags or "pos" in title_lower:
        module = "pos"
    elif "portal" in tags or "portal" in title_lower:
        module = "portal"
    elif "account" in tags or "invoice" in title_lower or "account" in title_lower:
        module = "accounting"
    elif "manifest" in title_lower or "install" in title_lower:
        module = "installation"
    elif "website" in tags or "website" in title_lower:
        module = "website"
    elif "stock" in tags or "inventory" in title_lower:
        module = "inventory"
    elif "sale" in tags or "sales" in title_lower:
        module = "sales"

    # Error type detection
    error_type = "general"
    if "not installable" in title_lower or "skipped" in title_lower:
        error_type = "manifest_error"
    elif "view" in title_lower or "xml" in title_lower:
        error_type = "view_error"
    elif "sync" in title_lower or "not saved" in title_lower:
        error_type = "sync_error"
    elif "field" in title_lower and "custom" in title_lower:
        error_type = "custom_field_error"
    elif "number" in title_lower or "sequence" in title_lower:
        error_type = "sequence_error"

    return {
        "module": module,
        "error_type": error_type
    }

def process_thread(url, session, max_retries=3):
    """Extract solution from individual thread"""
    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # Get thread body (first post)
            body_elem = soup.select_one('.o_wforum_read')
            body = clean_text(body_elem.get_text()) if body_elem else ""

            # Get accepted answer
            accepted = soup.select_one('.o_wforum_answer.accepted_answer, .accepted_answer')
            solution = clean_text(accepted.get_text()) if accepted else ""

            # If no accepted answer, try first answer
            if not solution:
                first_answer = soup.select_one('.o_wforum_answer')
                solution = clean_text(first_answer.get_text()) if first_answer else ""

            # Extract code blocks
            code_blocks = extract_code_blocks(soup)

            return {
                "body": body[:500],  # Truncate for storage
                "solution": solution[:1000],
                "code_blocks": code_blocks[:3],  # Keep top 3 code blocks
                "has_code": len(code_blocks) > 0
            }

        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                return {"body": "", "solution": "", "code_blocks": [], "error": str(e), "has_code": False}
            time.sleep(2 ** attempt)

        except Exception as e:
            return {"body": "", "solution": "", "code_blocks": [], "error": str(e), "has_code": False}

def process_all(limit=None):
    """Process all scraped issues"""
    if not INPUT_FILE.exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        print("   Run scrape_solved_threads_simple.py first!")
        return

    with open(INPUT_FILE) as f:
        issues = json.load(f)

    total = len(issues)
    process_limit = limit or total

    print(f"📥 Loaded {total} issues")
    print(f"🔄 Processing {min(process_limit, total)} threads...")
    print("   (This may take a while - fetching thread content)\n")

    results = []
    session = requests.Session()
    session.headers.update(HEADERS)

    for i, issue in enumerate(issues[:process_limit]):
        print(f"   [{i+1}/{min(process_limit, total)}] {issue['title'][:60]}...", end=" ")

        thread_data = process_thread(issue['url'], session)
        category = categorize_issue(issue['title'], issue['tags'], thread_data.get('body', ''))

        result = {
            **issue,
            **thread_data,
            **category
        }

        results.append(result)

        if thread_data.get('error'):
            print(f"⚠️  {thread_data['error'][:30]}")
        else:
            status = "✅" if thread_data.get('has_code') else "📝"
            print(status)

        # Rate limiting
        if (i + 1) % 10 == 0:
            # Save checkpoint every 10 issues
            with open(OUTPUT_FILE, "w") as f:
                json.dump(results, f, indent=2)
            print(f"   💾 Checkpoint saved ({len(results)} issues)")

        time.sleep(random.uniform(1.0, 2.5))

    # Final save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Processed {len(results)} issues")
    print(f"💾 Saved to: {OUTPUT_FILE}")

    # Generate stats
    modules = {}
    error_types = {}
    with_code = sum(1 for r in results if r.get('has_code'))

    for r in results:
        modules[r['module']] = modules.get(r['module'], 0) + 1
        error_types[r['error_type']] = error_types.get(r['error_type'], 0) + 1

    print(f"\n📊 Statistics:")
    print(f"   - Issues with code: {with_code}/{len(results)}")
    print(f"\n   - Module breakdown:")
    for module, count in sorted(modules.items(), key=lambda x: x[1], reverse=True):
        print(f"      • {module}: {count}")

    print(f"\n   - Error types:")
    for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
        print(f"      • {error_type}: {count}")

    return results

if __name__ == "__main__":
    import sys

    # Allow limiting number of issues to process (for testing)
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None

    if limit:
        print(f"ℹ️  Processing first {limit} issues only (test mode)")

    process_all(limit=limit)
