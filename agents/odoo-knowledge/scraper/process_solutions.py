#!/usr/bin/env python3
"""
Solution Processor - Extracts fixes and converts to guardrails/patches
"""
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

INPUT_FILE = Path(__file__).parent.parent / "knowledge" / "solved_issues_raw.json"
OUTPUT_FILE = Path(__file__).parent.parent / "knowledge" / "solutions_processed.json"
GUARDRAILS_DIR = Path(__file__).parent.parent / "guardrails"
PATCHES_DIR = Path(__file__).parent.parent / "autopatches"

def clean_text(text):
    """Clean and normalize text"""
    return re.sub(r"\s+", " ", text).strip()

def extract_code_blocks(text):
    """Extract code snippets from text"""
    # Match markdown code blocks and indented code
    code_pattern = r"```[\w]*\n(.*?)```|(?:^|\n)((?:    .*\n)+)"
    matches = re.findall(code_pattern, text, re.DOTALL)
    return [m[0] or m[1] for m in matches if m[0] or m[1]]

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

def process_thread(url, max_retries=3):
    """Extract solution from individual thread"""
    for attempt in range(max_retries):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=15000)

                # Wait for content
                page.wait_for_selector(".thread, .accepted_answer, .answer", timeout=10000)

                # Get thread body
                body_elem = page.query_selector(".thread")
                body = clean_text(body_elem.inner_text()) if body_elem else ""

                # Get accepted answer (if exists)
                solution_elem = page.query_selector(".accepted_answer")
                solution = clean_text(solution_elem.inner_text()) if solution_elem else ""

                # If no accepted answer, get first answer
                if not solution:
                    answer_elem = page.query_selector(".answer")
                    solution = clean_text(answer_elem.inner_text()) if answer_elem else ""

                # Extract code blocks
                code_blocks = extract_code_blocks(body + " " + solution)

                browser.close()

                return {
                    "body": body[:500],  # Truncate for storage
                    "solution": solution[:1000],
                    "code_blocks": code_blocks
                }

        except Exception as e:
            if attempt == max_retries - 1:
                return {"body": "", "solution": "", "code_blocks": [], "error": str(e)}
            time.sleep(2 ** attempt)

def process_all():
    """Process all scraped issues"""
    with open(INPUT_FILE) as f:
        issues = json.load(f)

    print(f"📥 Loaded {len(issues)} issues")
    print("🔄 Processing threads (this may take a while)...")

    results = []
    for i, issue in enumerate(issues[:50]):  # Start with first 50 for testing
        print(f"   [{i+1}/{min(50, len(issues))}] {issue['title'][:60]}...")

        thread_data = process_thread(issue['url'])
        category = categorize_issue(issue['title'], issue['tags'], thread_data.get('body', ''))

        results.append({
            **issue,
            **thread_data,
            **category
        })

    # Save processed data
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Processed {len(results)} issues")
    print(f"💾 Saved to: {OUTPUT_FILE}")

    # Generate stats
    modules = {}
    error_types = {}
    for r in results:
        modules[r['module']] = modules.get(r['module'], 0) + 1
        error_types[r['error_type']] = error_types.get(r['error_type'], 0) + 1

    print(f"\n📊 Module breakdown: {modules}")
    print(f"📊 Error types: {error_types}")

    return results

if __name__ == "__main__":
    import time
    process_all()
