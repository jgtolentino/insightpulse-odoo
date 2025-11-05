#!/usr/bin/env python3
"""
AI-Powered Conflict Resolver

Uses Claude to intelligently resolve merge conflicts.

Features:
- Semantic understanding of code
- Context-aware decisions
- Pattern matching
- Safe resolution with validation
"""

import os
import re
import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse

try:
    from anthropic import Anthropic
except ImportError:
    print("❌ Error: anthropic package not installed")
    print("Run: pip install anthropic")
    sys.exit(1)


class AIConflictResolver:
    """
    Use Claude to intelligently resolve merge conflicts.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the resolver with Anthropic API key."""
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. "
                "Set it via environment variable or pass to constructor."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.resolved_count = 0
        self.failed_count = 0
        self.model = "claude-sonnet-4-20250514"

    def get_conflicted_files(self) -> List[str]:
        """Get list of files with conflicts."""
        result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=U'],
            capture_output=True,
            text=True,
            check=False
        )

        files = result.stdout.strip().split('\n')
        return [f for f in files if f]  # Filter empty strings

    def extract_conflict_sections(self, file_path: str) -> List[Dict]:
        """
        Extract conflict markers and content.

        Returns list of conflicts with:
        - ours: our version
        - theirs: their version
        - base: common ancestor (if available)
        - line_start: starting line number
        - full_match: complete conflict block
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            return []

        conflicts = []

        # Pattern for conflict markers
        # <<<<<<< HEAD
        # our changes
        # =======
        # their changes
        # >>>>>>> branch
        pattern = r'<<<<<<< .*?\n(.*?)\n=======\n(.*?)\n>>>>>>> (.*?)\n'

        for match in re.finditer(pattern, content, re.DOTALL):
            ours = match.group(1)
            theirs = match.group(2)
            base_ref = match.group(3)

            # Calculate line number
            line_start = content[:match.start()].count('\n') + 1

            conflicts.append({
                'ours': ours,
                'theirs': theirs,
                'base_ref': base_ref,
                'full_match': match.group(0),
                'line_start': line_start
            })

        return conflicts

    def get_file_context(
        self,
        file_path: str,
        conflict_line: int,
        lines_before: int = 10,
        lines_after: int = 10
    ) -> str:
        """Get surrounding context for better AI resolution."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            return f"Error reading file: {e}"

        start = max(0, conflict_line - lines_before - 1)
        end = min(len(lines), conflict_line + lines_after)

        context_lines = lines[start:end]
        return ''.join(context_lines)

    def resolve_with_ai(
        self,
        file_path: str,
        conflict: Dict,
        file_context: str
    ) -> Tuple[str, float, str]:
        """
        Use Claude to resolve conflict.

        Returns:
            (resolved_content, confidence_score, strategy)
        """

        prompt = f"""You are an expert code merge conflict resolver. Given a merge conflict, determine the correct resolution.

**File:** `{file_path}`

**Line:** {conflict['line_start']}

**File Context (surrounding code):**
```
{file_context}
```

**Conflict:**

**Our changes (HEAD):**
```
{conflict['ours']}
```

**Their changes ({conflict['base_ref']}):**
```
{conflict['theirs']}
```

**Task:**
1. Analyze both versions
2. Determine if changes overlap or are complementary
3. Resolve intelligently by:
   - Merging non-conflicting changes
   - Preserving functionality from both sides when possible
   - Choosing the better implementation if mutually exclusive
   - Maintaining syntax correctness
   - Following the file's existing style

**Return JSON:**
```json
{{
  "resolution": "the resolved code without conflict markers",
  "reasoning": "explanation of why this resolution is correct",
  "confidence": 0.95,
  "strategy": "merge|ours|theirs|manual_needed"
}}
```

**Rules:**
- If confidence < 0.8, set strategy to "manual_needed"
- Preserve all functional changes when possible
- Maintain code style consistency
- Keep syntax valid (YAML, Python, JSON, etc.)
- Do NOT include conflict markers in resolution
- Return ONLY the resolved content, no markers

**Important:** The resolution should be the exact text that will replace the conflict, with proper indentation matching the file.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract text content
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)

            # Parse JSON response
            result = json.loads(response_text)

            return (
                result['resolution'],
                float(result['confidence']),
                result['strategy']
            )

        except json.JSONDecodeError as e:
            print(f"    ⚠️  JSON parse error: {e}")
            print(f"    Response: {response_text[:200]}...")
            return "", 0.0, "manual_needed"
        except Exception as e:
            print(f"    ⚠️  API error: {e}")
            return "", 0.0, "manual_needed"

    def resolve_file(self, file_path: str, confidence_threshold: float = 0.8) -> bool:
        """
        Resolve all conflicts in a file.

        Returns True if successful, False if needs manual review.
        """
        print(f"\n🔍 Analyzing conflicts in: {file_path}")

        conflicts = self.extract_conflict_sections(file_path)

        if not conflicts:
            print(f"  ✅ No conflicts found")
            return True

        print(f"  Found {len(conflicts)} conflict(s)")

        # Read full file for context
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                full_content = f.read()
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            return False

        # Resolve each conflict
        resolved_content = full_content

        for i, conflict in enumerate(conflicts, 1):
            print(f"  🤖 Resolving conflict {i}/{len(conflicts)}...")

            # Get surrounding context
            context = self.get_file_context(
                file_path,
                conflict['line_start'],
                lines_before=15,
                lines_after=15
            )

            # AI resolution
            resolution, confidence, strategy = self.resolve_with_ai(
                file_path,
                conflict,
                context
            )

            print(f"    Confidence: {confidence:.0%}")
            print(f"    Strategy: {strategy}")

            if confidence < confidence_threshold or strategy == "manual_needed":
                print(f"    ⚠️  Low confidence - needs manual review")
                return False

            # Replace conflict with resolution
            # Ensure resolution doesn't have trailing newline if original didn't
            if not conflict['full_match'].endswith('\n\n'):
                resolution = resolution.rstrip('\n')

            resolved_content = resolved_content.replace(
                conflict['full_match'],
                resolution + '\n',
                1  # Replace only first occurrence
            )

            self.resolved_count += 1
            print(f"    ✅ Resolved (strategy: {strategy})")

        # Write resolved content
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(resolved_content)
            print(f"  ✅ Resolved {len(conflicts)} conflict(s) in {file_path}")
            return True
        except Exception as e:
            print(f"  ❌ Error writing file: {e}")
            return False

    def resolve_all(
        self,
        max_files: int = 10,
        confidence_threshold: float = 0.8
    ) -> bool:
        """
        Resolve conflicts in all files.

        Returns True if all resolved, False if any need manual review.
        """
        files = self.get_conflicted_files()

        if not files or files == ['']:
            print("✅ No conflicts found")
            return True

        print(f"\n📋 Found {len(files)} file(s) with conflicts:")
        for f in files:
            print(f"  - {f}")

        if len(files) > max_files:
            print(f"\n⚠️  Too many conflicts ({len(files)} > {max_files})")
            print("   Needs manual review")
            return False

        all_resolved = True

        for file_path in files:
            if not self.resolve_file(file_path, confidence_threshold):
                all_resolved = False
                self.failed_count += 1

        print("\n" + "="*60)
        print(f"✅ Resolved: {self.resolved_count} conflicts")
        print(f"⚠️  Failed: {self.failed_count} conflicts")
        print("="*60)

        return all_resolved


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description='AI-powered merge conflict resolver using Claude'
    )
    parser.add_argument(
        '--base-ref',
        required=True,
        help='Base branch reference (e.g., origin/main)'
    )
    parser.add_argument(
        '--head-ref',
        required=True,
        help='Head branch reference (e.g., HEAD)'
    )
    parser.add_argument(
        '--max-auto-resolve',
        type=int,
        default=10,
        help='Maximum number of files to auto-resolve (default: 10)'
    )
    parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.8,
        help='Minimum confidence threshold (0.0-1.0, default: 0.8)'
    )
    parser.add_argument(
        '--api-key',
        help='Anthropic API key (or set ANTHROPIC_API_KEY env var)'
    )

    args = parser.parse_args()

    # Check if we're in a git repository
    if not Path('.git').exists():
        print("❌ Error: Not in a git repository")
        sys.exit(1)

    # Initialize resolver
    try:
        resolver = AIConflictResolver(api_key=args.api_key)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    print(f"🤖 AI Conflict Resolver")
    print(f"Model: {resolver.model}")
    print(f"Confidence threshold: {args.confidence_threshold:.0%}")
    print(f"Max files: {args.max_auto_resolve}")

    # Check if there's already a merge in progress
    merge_head = Path('.git/MERGE_HEAD')
    if not merge_head.exists():
        print(f"\n📥 Starting merge: {args.base_ref}")

        # Attempt merge to create conflict markers
        result = subprocess.run(
            ['git', 'merge', args.base_ref, '--no-commit', '--no-ff'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ No conflicts - merge successful")
            sys.exit(0)
        else:
            print("⚠️  Conflicts detected - attempting AI resolution")
    else:
        print("\n⚠️  Merge already in progress - resolving existing conflicts")

    # Resolve with AI
    success = resolver.resolve_all(
        max_files=args.max_auto_resolve,
        confidence_threshold=args.confidence_threshold
    )

    if not success:
        print("\n❌ Some conflicts could not be auto-resolved")
        print("Manual intervention required")
        sys.exit(1)

    print("\n✅ All conflicts resolved successfully!")
    print("\nNext steps:")
    print("  1. Review the changes: git diff --cached")
    print("  2. Run tests to verify")
    print("  3. Commit: git commit")
    sys.exit(0)


if __name__ == '__main__':
    main()
