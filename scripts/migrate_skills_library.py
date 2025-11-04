#!/usr/bin/env python3
"""
Skills Library Migration Assistant

Helps migrate and organize Claude Code skills using scraped Odoo knowledge.
Keeps skills library up-to-date as patterns evolve.
"""

import os
import json
from pathlib import Path
from anthropic import Anthropic

def load_all_skills():
    """Load all skills from docs/claude-code-skills/"""
    skills = []
    skills_dir = Path("docs/claude-code-skills/community")

    for skill_path in skills_dir.glob("*/SKILL.md"):
        with open(skill_path) as f:
            skills.append({
                'name': skill_path.parent.name,
                'path': str(skill_path),
                'content': f.read()
            })

    print(f"✅ Loaded {len(skills)} skills")
    return skills

def scrape_odoo_patterns():
    """Load scraped patterns from knowledge base"""
    pattern_file = Path("knowledge/odoo_patterns.json")

    if not pattern_file.exists():
        print("⚠️  No knowledge base found. Run scraper first.")
        return []

    with open(pattern_file) as f:
        patterns = json.load(f)

    print(f"✅ Loaded {len(patterns)} patterns")
    return patterns

def migrate_skill_with_claude(skill, patterns, migration_type):
    """Use Claude to suggest skill improvements based on patterns"""

    client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    # Build context
    pattern_context = "\n".join([
        f"- {p.get('title', 'Unknown')}: {p.get('pattern', '')}"
        for p in patterns[:10]  # Limit to 10 patterns
    ])

    prompt = f"""
    You are helping migrate a Claude Code skill library.

    Current Skill: {skill['name']}
    Current Content (first 500 chars):
    ```
    {skill['content'][:500]}...
    ```

    Recent Odoo Patterns from Forum:
    {pattern_context}

    Migration Type: {migration_type}

    Task: Suggest improvements to this skill based on new patterns.

    Focus on:
    1. Adding new error patterns discovered
    2. Updating outdated solutions
    3. Adding auto-fix scripts
    4. Improving documentation

    Output:
    - What to add
    - What to update
    - What to deprecate

    Be concise and actionable.
    """

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text

def generate_migration_report(skills, patterns):
    """Generate report of suggested skill updates"""

    report = []
    report.append("# Skills Library Migration Report")
    report.append(f"\n**Generated:** {datetime.now().isoformat()}")
    report.append(f"\n**Skills Analyzed:** {len(skills)}")
    report.append(f"\n**Patterns Considered:** {len(patterns)}\n")

    for skill in skills[:5]:  # Limit to 5 skills for token management
        print(f"Analyzing skill: {skill['name']}")

        suggestions = migrate_skill_with_claude(
            skill,
            patterns,
            migration_type="enhance_with_patterns"
        )

        report.append(f"\n## {skill['name']}")
        report.append(f"\n{suggestions}\n")
        report.append("---")

    return "\n".join(report)

def main():
    print("=== Skills Library Migration Assistant ===\n")

    # 1. Load skills
    skills = load_all_skills()

    # 2. Load patterns
    patterns = scrape_odoo_patterns()

    if not patterns:
        print("Run: gh workflow run odoo-knowledge-scraper.yml")
        return

    # 3. Generate migration report
    print("\nGenerating migration suggestions...")
    report = generate_migration_report(skills, patterns)

    # 4. Save report
    os.makedirs("docs/migrations", exist_ok=True)
    report_file = f"docs/migrations/skills_migration_{datetime.now().strftime('%Y%m%d')}.md"

    with open(report_file, 'w') as f:
        f.write(report)

    print(f"\n✅ Migration report: {report_file}")
    print("\nReview the report and apply suggested changes manually.")

if __name__ == "__main__":
    from datetime import datetime
    main()
