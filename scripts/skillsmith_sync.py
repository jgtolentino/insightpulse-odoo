#!/usr/bin/env python3
"""
Sync section 19 (skills inventory) in claude.md from docs/claude-code-skills/*
"""
import argparse
import pathlib
import re
import sys


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claude-md", required=True)
    ap.add_argument("--skills-dir", required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    return ap.parse_args()


SEC_START_RE = re.compile(r"(?m)^##\s*19\b.*?$")
SEC_HEADER = "## 19 Skills Inventory"


def list_skills(skills_dir: str):
    root = pathlib.Path(skills_dir)
    if not root.exists():
        return []
    skills = []
    for p in sorted(root.glob("*")):
        if p.is_dir():
            md = p / "SKILL.md"
            if not md.exists():
                md = p / "README.md"
            skills.append(
                {
                    "name": p.name.replace("_", "-"),
                    "path": str(p),
                    "doc": str(md) if md.exists() else "",
                }
            )
    return skills


def render_section(skills):
    lines = [SEC_HEADER, "", "| Skill | Doc |", "|---|---|"]
    for s in skills:
        doc = s["doc"]
        link = f"[link]({doc})" if doc else ""
        lines.append(f"| `{s['name']}` | {link} |")
    return "\n".join(lines) + "\n"


def replace_section(md_text, new_section):
    sec19_match = SEC_START_RE.search(md_text)
    if not sec19_match:
        return md_text.rstrip() + "\n\n" + new_section
    start = sec19_match.start()
    tail = md_text[start:]
    mnext = re.search(r"(?m)^##\s*\d+\b.*$", tail[len(SEC_HEADER) :])
    end = start + (mnext.start() + len(SEC_HEADER) if mnext else len(tail))
    return md_text[:start] + new_section + md_text[end:]


def main():
    a = parse_args()
    with open(a.claude_md, "r", encoding="utf-8", errors="ignore") as f:
        md = f.read()
    skills = list_skills(a.skills_dir)
    new_section = render_section(skills)

    current = ""
    sec_match = SEC_START_RE.search(md)
    if sec_match:
        cur_tail = md[sec_match.start() :]
        mnext = re.search(r"(?m)^##\s*\d+\b.*$", cur_tail[len(SEC_HEADER) :])
        current = cur_tail[
            : (mnext.start() + len(SEC_HEADER) if mnext else len(cur_tail))
        ]

    changed = current.strip() != new_section.strip()

    if a.check and changed:
        print("⚠️  Drift detected: section 19 differs from filesystem skills.")
        print("----- proposed section 19 -----")
        print(new_section)
        sys.exit(1)
    if a.check and not changed:
        print("✅ Section 19 up-to-date")
        return

    if a.write:
        updated = replace_section(md, new_section)
        with open(a.claude_md, "w", encoding="utf-8") as f:
            f.write(updated)
        print("✅ Updated section 19 in", a.claude_md)
        return

    print(new_section)


if __name__ == "__main__":
    main()
