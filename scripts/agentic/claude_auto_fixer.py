#!/usr/bin/env python3
"""
Claude Code Auto-Fixer - Agentic system for automatic CI failure resolution.

Uses Anthropic Claude Sonnet 4.5 to analyze errors and apply fixes autonomously.

Usage:
    python claude_auto_fixer.py \
        --error-log error.txt \
        --category dependency_missing \
        --confidence 87 \
        --suggested-fix fix.txt \
        --auto-commit true
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    from anthropic import Anthropic
    from pydantic import BaseModel, Field
    from tenacity import retry, stop_after_attempt, wait_exponential
except ImportError:
    print("❌ Agentic verification dependencies not installed.")
    print("   Run: pip install -e '.[agentic-verification]'")
    sys.exit(1)


class FixProposal(BaseModel):
    """Structured fix proposal from Claude"""

    category: str = Field(description="Error category")
    files_to_modify: List[str] = Field(description="Files that need changes")
    changes: List[Dict[str, str]] = Field(description="Specific changes to apply")
    tests_to_run: List[str] = Field(description="Tests to verify fix")
    commit_message: str = Field(description="Conventional commit message")
    risk_level: str = Field(description="low, medium, or high")
    confidence: float = Field(description="Confidence in fix (0.0-1.0)")


class ClaudeAutoFixer:
    """Autonomous CI failure fixer using Claude Code"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def analyze_and_fix(
        self, error_log: str, category: str, confidence: float, suggested_fix: str
    ) -> FixProposal:
        """Analyze error and generate fix proposal"""

        system_prompt = """You are an expert DevOps engineer and Python developer specializing in CI/CD automation.

Your task is to analyze CI failures and propose MINIMAL, SAFE fixes that resolve the issue without introducing new problems.

Guidelines:
1. Make the smallest possible change that fixes the error
2. Preserve existing functionality and tests
3. Follow project conventions and style
4. Never remove tests or skip validation
5. Add new tests only if needed for regression prevention
6. Use conventional commit format
7. Provide risk assessment (low/medium/high)

Output your fix proposal as structured JSON."""

        user_prompt = f"""Analyze this CI failure and propose a fix:

**Error Category**: {category}
**ML Confidence**: {confidence}%

**Error Log** (last 200 lines):
```
{error_log}
```

**ML Suggested Fix**:
```
{suggested_fix}
```

**Project Context**:
- Language: Python 3.11+
- Framework: Odoo CE 18.0
- Testing: pytest with coverage
- CI: GitHub Actions
- Project: Finance SSC platform

**Task**: Propose a MINIMAL fix that resolves this error.

Return JSON with this structure:
{{
  "category": "{category}",
  "files_to_modify": ["path/to/file1.py", "path/to/file2.yml"],
  "changes": [
    {{
      "file": "path/to/file1.py",
      "action": "edit",
      "description": "Add missing import",
      "before": "import requests",
      "after": "import requests\\nimport pytest_cov"
    }}
  ],
  "tests_to_run": ["tests/test_api.py"],
  "commit_message": "fix(ci): add missing pytest-cov dependency\\n\\nResolves CI failure in tee-mvp-ci workflow",
  "risk_level": "low",
  "confidence": 0.95
}}
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.2,  # Low temperature for deterministic fixes
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        # Parse JSON response
        response_text = response.content[0].text

        # Extract JSON if wrapped in markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        try:
            fix_data = json.loads(response_text)
            return FixProposal(**fix_data)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Failed to parse Claude response: {e}")
            print(f"Response: {response_text[:500]}")
            raise

    def apply_fix(self, proposal: FixProposal) -> bool:
        """Apply proposed fix to files"""
        print(f"\n🔧 Applying fix for: {proposal.category}")
        print(f"   Risk Level: {proposal.risk_level}")
        print(f"   Confidence: {proposal.confidence:.1%}")
        print(f"   Files to modify: {len(proposal.files_to_modify)}")

        if proposal.risk_level == "high" and proposal.confidence < 0.90:
            print("⚠️  High risk fix with confidence < 90%, skipping auto-apply")
            return False

        for change in proposal.changes:
            file_path = Path(change["file"])

            if change["action"] == "edit":
                self._apply_edit(file_path, change)
            elif change["action"] == "create":
                self._create_file(file_path, change)
            elif change["action"] == "delete":
                self._delete_file(file_path, change)

        return True

    def _apply_edit(self, file_path: Path, change: Dict):
        """Apply edit to existing file"""
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}, skipping")
            return

        content = file_path.read_text()

        if "before" in change and "after" in change:
            # String replacement
            if change["before"] in content:
                updated_content = content.replace(change["before"], change["after"])
                file_path.write_text(updated_content)
                print(f"✅ Edited: {file_path}")
            else:
                print(f"⚠️  Pattern not found in {file_path}: {change['before'][:50]}")
        elif "line_number" in change and "new_line" in change:
            # Line replacement
            lines = content.splitlines(keepends=True)
            line_num = change["line_number"] - 1  # 0-indexed
            if 0 <= line_num < len(lines):
                lines[line_num] = change["new_line"] + "\n"
                file_path.write_text("".join(lines))
                print(f"✅ Edited line {change['line_number']} in {file_path}")
            else:
                print(f"⚠️  Invalid line number: {change['line_number']}")

    def _create_file(self, file_path: Path, change: Dict):
        """Create new file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(change.get("content", ""))
        print(f"✅ Created: {file_path}")

    def _delete_file(self, file_path: Path, change: Dict):
        """Delete file"""
        if file_path.exists():
            file_path.unlink()
            print(f"✅ Deleted: {file_path}")

    def run_tests(self, tests: List[str]) -> bool:
        """Run specified tests to verify fix"""
        if not tests:
            print("ℹ️  No specific tests to run, skipping verification")
            return True

        print(f"\n🧪 Running {len(tests)} tests for verification...")

        for test in tests:
            result = subprocess.run(
                ["pytest", test, "-v"], capture_output=True, text=True
            )

            if result.returncode != 0:
                print(f"❌ Test failed: {test}")
                print(result.stdout[-500:])  # Last 500 chars
                return False

            print(f"✅ Test passed: {test}")

        return True


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description="Claude Code Auto-Fixer")
    parser.add_argument("--error-log", required=True, help="Path to error log file")
    parser.add_argument("--category", required=True, help="ML-detected error category")
    parser.add_argument(
        "--confidence", required=True, type=float, help="ML confidence (0-100)"
    )
    parser.add_argument(
        "--suggested-fix", required=True, help="Path to ML suggested fix"
    )
    parser.add_argument(
        "--auto-commit",
        type=lambda x: x.lower() == "true",
        default=False,
        help="Auto-commit if tests pass",
    )

    args = parser.parse_args()

    # Read inputs
    error_log = Path(args.error_log).read_text()
    suggested_fix = Path(args.suggested_fix).read_text()

    # Initialize fixer
    fixer = ClaudeAutoFixer()

    # Analyze and generate fix
    print(f"🤖 Analyzing CI failure with Claude Sonnet 4.5...")
    proposal = fixer.analyze_and_fix(
        error_log=error_log,
        category=args.category,
        confidence=args.confidence,
        suggested_fix=suggested_fix,
    )

    # Save proposal
    proposal_path = Path("fix-proposal.json")
    proposal_path.write_text(proposal.model_dump_json(indent=2))
    print(f"📄 Fix proposal saved to {proposal_path}")

    # Apply fix
    success = fixer.apply_fix(proposal)

    if not success:
        print("❌ Fix not applied (high risk or low confidence)")
        sys.exit(1)

    # Run verification tests
    if proposal.tests_to_run:
        tests_passed = fixer.run_tests(proposal.tests_to_run)

        if not tests_passed:
            print("❌ Verification tests failed, reverting changes")
            subprocess.run(["git", "checkout", "."], check=False)
            sys.exit(1)

    # Auto-commit if requested and tests passed
    if args.auto_commit:
        print(f"\n✅ All checks passed, committing fix...")
        print(f"   Commit message: {proposal.commit_message[:60]}...")
        # Commit will be done by GitHub Actions workflow

    print("\n✅ Auto-fix complete!")
    sys.exit(0)


if __name__ == "__main__":
    main()
