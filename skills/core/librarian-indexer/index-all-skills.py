#!/usr/bin/env python3
"""
Index All Skills

This script scans the skills directory, parses all SKILL.md files,
and creates a searchable index.

Usage:
    python index-all-skills.py
    python index-all-skills.py --output skills/INDEX.json
"""

import os
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict


class SkillIndexer:
    """Create searchable index of all skills."""

    def __init__(self, skills_dir: str = "skills/"):
        self.skills_dir = skills_dir
        self.index = {
            "skills": [],
            "by_category": {},
            "by_expertise": {},
            "by_tags": {},
            "dependencies": {},
            "total_count": 0,
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }

    def scan_and_index(self) -> Dict:
        """
        Scan skills directory and build index.

        Returns:
            Complete index dictionary
        """
        print(f"🔍 Scanning {self.skills_dir} for SKILL.md files...")

        skill_files = []
        for root, dirs, files in os.walk(self.skills_dir):
            for file in files:
                if file == "SKILL.md":
                    skill_path = os.path.join(root, file)
                    skill_files.append(skill_path)

        print(f"Found {len(skill_files)} skill files")

        # Parse each skill
        for skill_path in skill_files:
            print(f"📝 Parsing: {skill_path}")
            skill_data = self.parse_skill(skill_path)

            if skill_data:
                self.index["skills"].append(skill_data)

                # Index by category
                category = skill_data["category"]
                if category not in self.index["by_category"]:
                    self.index["by_category"][category] = []
                self.index["by_category"][category].append(skill_data["id"])

                # Index by expertise
                expertise = skill_data["expertise_level"]
                if expertise not in self.index["by_expertise"]:
                    self.index["by_expertise"][expertise] = []
                self.index["by_expertise"][expertise].append(skill_data["id"])

                # Index by tags
                for tag in skill_data.get("tags", []):
                    if tag not in self.index["by_tags"]:
                        self.index["by_tags"][tag] = []
                    self.index["by_tags"][tag].append(skill_data["id"])

                # Index dependencies
                if skill_data.get("dependencies"):
                    self.index["dependencies"][skill_data["id"]] = skill_data["dependencies"]

        self.index["total_count"] = len(self.index["skills"])

        print(f"✅ Indexed {self.index['total_count']} skills")
        print(f"   Categories: {len(self.index['by_category'])}")
        print(f"   Expertise levels: {len(self.index['by_expertise'])}")
        print(f"   Tags: {len(self.index['by_tags'])}")

        return self.index

    def parse_skill(self, skill_path: str) -> Optional[Dict]:
        """
        Parse a SKILL.md file and extract metadata.

        Args:
            skill_path: Path to SKILL.md file

        Returns:
            Skill metadata dictionary or None if parsing fails
        """
        try:
            with open(skill_path, 'r') as f:
                content = f.read()

            # Extract skill ID from frontmatter or content
            skill_id = self._extract_field(content, "Skill ID")
            if not skill_id:
                skill_id = Path(skill_path).parent.name

            # Extract other metadata
            skill_data = {
                "id": skill_id,
                "name": self._extract_field(content, "name") or self._extract_title(content),
                "version": self._extract_field(content, "Version", "version"),
                "category": self._extract_field(content, "Category", "category") or "Uncategorized",
                "expertise_level": self._extract_field(content, "Expertise Level", "expertise_level") or "Intermediate",
                "file_path": skill_path,
                "last_updated": self._extract_field(content, "Last Updated", "last_updated") or datetime.now().strftime("%Y-%m-%d"),
                "description": self._extract_purpose(content),
                "capabilities": self._extract_capabilities(content),
                "tags": self._extract_tags(content),
                "dependencies": self._extract_dependencies(content),
                "source_module": self._extract_field(content, "Source Module"),
            }

            return skill_data

        except Exception as e:
            print(f"⚠️  Error parsing {skill_path}: {e}")
            return None

    def _extract_field(self, content: str, *field_names: str) -> Optional[str]:
        """Extract a field value from skill content."""
        for field_name in field_names:
            # Try **Field:** format
            pattern = rf"\*\*{field_name}:\*\*\s*`?([^`\n]+)`?"
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

            # Try field: format
            pattern = rf"^{field_name}:\s*(.+)$"
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown heading."""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return "Untitled Skill"

    def _extract_purpose(self, content: str) -> str:
        """Extract purpose/description section."""
        # Look for ## Purpose or ## 🎯 Purpose
        pattern = r"##\s+(?:🎯\s+)?Purpose\s*\n\n(.+?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            description = match.group(1).strip()
            # Truncate to first paragraph or 500 chars
            first_para = description.split("\n\n")[0]
            if len(first_para) > 500:
                return first_para[:497] + "..."
            return first_para
        return "No description available"

    def _extract_capabilities(self, content: str) -> List[str]:
        """Extract capabilities list."""
        capabilities = []

        # Look for Key Capabilities section
        pattern = r"\*\*Key Capabilities:\*\*\s*\n((?:[\d\.].*?\n)+)"
        match = re.search(pattern, content)
        if match:
            caps_text = match.group(1)
            # Extract numbered list items
            for line in caps_text.split("\n"):
                line = line.strip()
                if re.match(r"[\d\.]+\s+", line):
                    cap = re.sub(r"^[\d\.]+\s+", "", line)
                    cap = re.sub(r"[✅🔍📚🔄💡🏗️]", "", cap).strip()
                    if cap:
                        capabilities.append(cap)

        return capabilities

    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content."""
        tags = []

        # Look for explicit tags
        tags_match = re.search(r"\*\*Tags:\*\*\s*(.+)", content)
        if tags_match:
            tags_text = tags_match.group(1)
            tags = [t.strip() for t in tags_text.split(",")]

        # Also extract from category
        category = self._extract_field(content, "Category")
        if category:
            tags.append(category.lower())

        # Extract from title
        title = self._extract_title(content)
        title_words = re.findall(r"\b[A-Z][a-z]+\b", title)
        tags.extend([w.lower() for w in title_words if len(w) > 3])

        # Remove duplicates
        tags = list(set(tags))

        return tags

    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract skill dependencies."""
        dependencies = []

        # Look for Related Skills or Prerequisites section
        patterns = [
            r"##\s+Related Skills\s*\n\n(.*?)(?=\n##|\Z)",
            r"##\s+Prerequisites\s*\n\n(.*?)(?=\n##|\Z)",
            r"\*\*Related Skills:\*\*\s*\n(.*?)(?=\n\n|\Z)"
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                deps_text = match.group(1)
                # Extract skill IDs in backticks
                deps = re.findall(r"`([a-z-]+)`", deps_text)
                dependencies.extend(deps)

        # Remove duplicates
        dependencies = list(set(dependencies))

        return dependencies

    def save_index(self, output_path: str):
        """Save index to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.index, f, indent=2)

        print(f"💾 Saved index to: {output_path}")

    def generate_readme(self, output_path: str):
        """Generate SKILLS_INDEX.md with human-readable index."""
        content = f"""# Skills Index

**Total Skills:** {self.index['total_count']}
**Last Updated:** {self.index['last_updated']}

## By Category

"""

        for category, skill_ids in sorted(self.index['by_category'].items()):
            content += f"### {category} ({len(skill_ids)} skills)\n\n"
            for skill_id in skill_ids:
                skill = next(s for s in self.index['skills'] if s['id'] == skill_id)
                content += f"- **[{skill['name']}]({skill['file_path']})** - {skill['expertise_level']}\n"
                if skill['description']:
                    first_line = skill['description'].split("\n")[0]
                    content += f"  {first_line}\n"
            content += "\n"

        content += f"""
## By Expertise Level

"""

        for expertise, skill_ids in sorted(self.index['by_expertise'].items()):
            content += f"### {expertise} ({len(skill_ids)} skills)\n\n"
            for skill_id in skill_ids:
                skill = next(s for s in self.index['skills'] if s['id'] == skill_id)
                content += f"- [{skill['name']}]({skill['file_path']})\n"
            content += "\n"

        content += f"""
## By Tags

"""

        for tag, skill_ids in sorted(self.index['by_tags'].items()):
            if len(skill_ids) > 1:  # Only show tags with multiple skills
                content += f"**{tag}** ({len(skill_ids)}): "
                skill_names = [next(s['name'] for s in self.index['skills'] if s['id'] == sid)
                             for sid in skill_ids]
                content += ", ".join(skill_names) + "\n\n"

        # Save
        with open(output_path, 'w') as f:
            f.write(content)

        print(f"📄 Generated human-readable index: {output_path}")

    def search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Search skills by query.

        Args:
            query: Search query
            filters: Optional filters {"category": "Finance", "expertise": "Expert"}

        Returns:
            List of matching skills
        """
        results = []
        query_lower = query.lower()

        for skill in self.index['skills']:
            # Apply filters
            if filters:
                if filters.get("category") and skill["category"] != filters["category"]:
                    continue
                if filters.get("expertise") and skill["expertise_level"] != filters["expertise"]:
                    continue

            # Calculate relevance score
            score = 0.0

            # Check name
            if query_lower in skill["name"].lower():
                score += 5.0

            # Check description
            if query_lower in skill["description"].lower():
                score += 3.0

            # Check tags
            for tag in skill.get("tags", []):
                if query_lower in tag.lower():
                    score += 2.0

            # Check capabilities
            for cap in skill.get("capabilities", []):
                if query_lower in cap.lower():
                    score += 1.0

            if score > 0:
                results.append({
                    **skill,
                    "relevance_score": score
                })

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Index all skills and create searchable catalog"
    )
    parser.add_argument(
        "--skills-dir",
        default="skills/",
        help="Skills directory to scan"
    )
    parser.add_argument(
        "--output",
        default="skills/INDEX.json",
        help="Output path for JSON index"
    )
    parser.add_argument(
        "--readme",
        default="skills/SKILLS_INDEX.md",
        help="Output path for human-readable index"
    )
    parser.add_argument(
        "--search",
        help="Search query to test index"
    )

    args = parser.parse_args()

    # Create indexer
    indexer = SkillIndexer(args.skills_dir)

    # Build index
    index = indexer.scan_and_index()

    # Save index
    indexer.save_index(args.output)

    # Generate README
    indexer.generate_readme(args.readme)

    # Test search if provided
    if args.search:
        print(f"\n🔍 Testing search: '{args.search}'")
        results = indexer.search(args.search)
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. {result['name']} (score: {result['relevance_score']})")
            print(f"   {result['description'][:100]}...")

    print("\n✨ Indexing complete!")


if __name__ == "__main__":
    main()
