#!/usr/bin/env python3
"""
Notebook Index Generator for OpenAI Cookbook

Generates searchable indices and documentation from notebook metadata.

Outputs:
  - JSON index with full metadata
  - Markdown index for human browsing
  - Category-specific README files
  - registry.yaml for cookbook.openai.com (if needed)
"""

import argparse
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import nbformat


def find_notebooks(pattern: str, root: Path) -> List[Path]:
    """Find all notebooks matching the pattern."""
    full_pattern = str(root / pattern)
    return sorted([Path(p) for p in glob.glob(full_pattern, recursive=True)])


def extract_notebook_info(nb_path: Path, root: Path) -> Dict:
    """
    Extract metadata and summary from a notebook.

    Returns a dict with notebook information including:
    - path, title, difficulty, tags, category, estimated_time, etc.
    """
    try:
        nb = nbformat.read(nb_path, as_version=4)
    except Exception as e:
        return {
            "path": str(nb_path.relative_to(root)),
            "error": f"Failed to read notebook: {e}",
        }

    metadata = nb.metadata.get("cookbook", {})
    rel_path = nb_path.relative_to(root)

    # Extract summary from first markdown cell
    summary = ""
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            # Get first paragraph
            lines = cell.source.split("\n")
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    summary = line[:200]  # First 200 chars
                    break
            if summary:
                break

    info = {
        "path": str(rel_path),
        "filename": nb_path.name,
        "title": metadata.get("title", nb_path.stem),
        "difficulty": metadata.get("difficulty"),
        "tags": metadata.get("tags", []),
        "category": metadata.get("category"),
        "estimated_time": metadata.get("estimated_time"),
        "openai_models": metadata.get("openai_models", []),
        "prerequisites": metadata.get("prerequisites", []),
        "author": metadata.get("author"),
        "last_updated": metadata.get("last_updated"),
        "summary": summary,
        "cell_count": len(nb.cells),
        "code_cells": sum(1 for c in nb.cells if c.cell_type == "code"),
        "markdown_cells": sum(1 for c in nb.cells if c.cell_type == "markdown"),
    }

    return info


def generate_json_index(notebooks_info: List[Dict], output_path: Path):
    """Generate JSON index file."""
    with open(output_path, 'w') as f:
        json.dump(notebooks_info, f, indent=2, sort_keys=False)
    print(f"✅ Generated JSON index: {output_path}")


def generate_markdown_index(notebooks_info: List[Dict], output_path: Path):
    """Generate Markdown index file."""
    lines = [
        "# Notebook Index",
        "",
        f"Total notebooks: **{len(notebooks_info)}**",
        "",
        "## By Category",
        ""
    ]

    # Group by category
    by_category = defaultdict(list)
    for info in notebooks_info:
        category = info.get("category", "uncategorized")
        by_category[category].append(info)

    # Sort categories
    for category in sorted(by_category.keys()):
        lines.append(f"### {category.title()}")
        lines.append("")

        notebooks = sorted(by_category[category], key=lambda x: x.get("difficulty", "zzz"))

        for nb in notebooks:
            title = nb.get("title", nb.get("filename"))
            path = nb.get("path")
            difficulty = nb.get("difficulty", "N/A")
            est_time = nb.get("estimated_time", "N/A")
            tags = ", ".join(nb.get("tags", [])) if nb.get("tags") else "N/A"

            # Create a badge-style difficulty indicator
            diff_emoji = {
                "beginner": "🟢",
                "intermediate": "🟡",
                "advanced": "🔴",
            }.get(difficulty, "⚪")

            lines.append(
                f"- **[{title}]({path})** "
                f"{diff_emoji} {difficulty} | "
                f"⏱️ {est_time} | "
                f"🏷️ {tags}"
            )

            if nb.get("summary"):
                lines.append(f"  <br/>_{nb['summary']}_")

        lines.append("")

    # By Difficulty section
    lines.extend([
        "## By Difficulty",
        ""
    ])

    for difficulty in ["beginner", "intermediate", "advanced"]:
        matching = [nb for nb in notebooks_info if nb.get("difficulty") == difficulty]
        if matching:
            diff_emoji = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}[difficulty]
            lines.append(f"### {diff_emoji} {difficulty.title()} ({len(matching)})")
            lines.append("")

            for nb in sorted(matching, key=lambda x: x.get("category", "zzz")):
                title = nb.get("title", nb.get("filename"))
                path = nb.get("path")
                category = nb.get("category", "N/A")
                lines.append(f"- [{title}]({path}) - *{category}*")

            lines.append("")

    # By Tags section
    lines.extend([
        "## By Tags",
        ""
    ])

    all_tags = defaultdict(list)
    for nb in notebooks_info:
        for tag in nb.get("tags", []):
            all_tags[tag].append(nb)

    for tag in sorted(all_tags.keys()):
        notebooks = all_tags[tag]
        lines.append(f"### {tag} ({len(notebooks)})")
        lines.append("")

        for nb in notebooks:
            title = nb.get("title", nb.get("filename"))
            path = nb.get("path")
            lines.append(f"- [{title}]({path})")

        lines.append("")

    with open(output_path, 'w') as f:
        f.write("\n".join(lines))

    print(f"✅ Generated Markdown index: {output_path}")


def generate_category_readmes(notebooks_info: List[Dict], root: Path):
    """Generate README.md for each category directory."""
    by_category = defaultdict(list)
    for info in notebooks_info:
        category = info.get("category")
        if category:
            by_category[category].append(info)

    for category, notebooks in by_category.items():
        # Determine category directory (examples/{category})
        category_dir = root / "examples" / category
        if not category_dir.exists():
            continue

        readme_path = category_dir / "README.md"

        lines = [
            f"# {category.replace('-', ' ').title()} Examples",
            "",
            f"This directory contains {len(notebooks)} example(s) for {category}.",
            "",
            "## Examples",
            ""
        ]

        for nb in sorted(notebooks, key=lambda x: (x.get("difficulty", "zzz"), x.get("title", ""))):
            title = nb.get("title", nb.get("filename"))
            filename = nb.get("filename")
            difficulty = nb.get("difficulty", "N/A")
            est_time = nb.get("estimated_time", "N/A")

            diff_emoji = {
                "beginner": "🟢",
                "intermediate": "🟡",
                "advanced": "🔴",
            }.get(difficulty, "⚪")

            lines.append(f"### {diff_emoji} [{title}]({filename})")
            lines.append("")
            lines.append(f"**Difficulty:** {difficulty}  ")
            lines.append(f"**Estimated time:** {est_time}  ")

            if nb.get("tags"):
                lines.append(f"**Tags:** {', '.join(nb['tags'])}  ")

            if nb.get("openai_models"):
                lines.append(f"**Models:** {', '.join(nb['openai_models'])}  ")

            if nb.get("summary"):
                lines.append(f"\n{nb['summary']}")

            lines.append("")

        with open(readme_path, 'w') as f:
            f.write("\n".join(lines))

        print(f"✅ Generated category README: {readme_path}")


def generate_stats_summary(notebooks_info: List[Dict], output_path: Path):
    """Generate statistics summary."""
    stats = {
        "total_notebooks": len(notebooks_info),
        "by_difficulty": defaultdict(int),
        "by_category": defaultdict(int),
        "tags_frequency": defaultdict(int),
        "models_used": defaultdict(int),
    }

    for nb in notebooks_info:
        if nb.get("difficulty"):
            stats["by_difficulty"][nb["difficulty"]] += 1
        if nb.get("category"):
            stats["by_category"][nb["category"]] += 1
        for tag in nb.get("tags", []):
            stats["tags_frequency"][tag] += 1
        for model in nb.get("openai_models", []):
            stats["models_used"][model] += 1

    # Convert defaultdicts to regular dicts for JSON serialization
    stats["by_difficulty"] = dict(stats["by_difficulty"])
    stats["by_category"] = dict(stats["by_category"])
    stats["tags_frequency"] = dict(sorted(stats["tags_frequency"].items(), key=lambda x: x[1], reverse=True))
    stats["models_used"] = dict(sorted(stats["models_used"].items(), key=lambda x: x[1], reverse=True))

    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"✅ Generated statistics: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate searchable index for OpenAI Cookbook notebooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all indices
  python generate_notebook_index.py

  # Generate for specific pattern
  python generate_notebook_index.py --pattern "examples/chat/**/*.ipynb"

  # Customize output directory
  python generate_notebook_index.py --output-dir ./generated-docs
        """
    )

    parser.add_argument(
        "--pattern",
        default="examples/**/*.ipynb",
        help="Glob pattern for notebooks to index (default: examples/**/*.ipynb)"
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory for notebook search (default: current directory)"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for generated files (default: root directory)"
    )

    parser.add_argument(
        "--skip-category-readmes",
        action="store_true",
        help="Skip generating category-specific README files"
    )

    args = parser.parse_args()

    output_dir = args.output_dir or args.root

    # Find notebooks
    notebooks = find_notebooks(args.pattern, args.root)

    if not notebooks:
        print(f"❌ No notebooks found matching pattern: {args.pattern}")
        print(f"   Root directory: {args.root}")
        return 1

    print(f"Found {len(notebooks)} notebook(s) matching pattern: {args.pattern}")
    print(f"{'='*80}\n")

    # Extract info from all notebooks
    print("Extracting notebook information...")
    notebooks_info = []

    for nb_path in notebooks:
        info = extract_notebook_info(nb_path, args.root)
        notebooks_info.append(info)

        if "error" in info:
            print(f"  ⚠️  {info['path']}: {info['error']}")

    print(f"\n✅ Extracted information from {len(notebooks_info)} notebooks\n")

    # Generate outputs
    print("Generating index files...")
    print(f"{'='*80}\n")

    generate_json_index(notebooks_info, output_dir / "notebook_index.json")
    generate_markdown_index(notebooks_info, output_dir / "NOTEBOOK_INDEX.md")
    generate_stats_summary(notebooks_info, output_dir / "notebook_stats.json")

    if not args.skip_category_readmes:
        print()
        generate_category_readmes(notebooks_info, args.root)

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Indexed {len(notebooks_info)} notebooks")
    print(f"Categories: {len(set(nb.get('category') for nb in notebooks_info if nb.get('category')))}")
    print(f"Tags: {len(set(tag for nb in notebooks_info for tag in nb.get('tags', [])))}")
    print("\n✅ Index generation complete!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
