#!/usr/bin/env python3
"""
Auto-Patch Framework
Scans codebase for patterns and applies automated fixes
"""

import os
import sys
import yaml
import glob
import re
from pathlib import Path
from typing import List, Dict, Any

# Configuration
APPLY = os.getenv("APPLY", "false").lower() == "true"
ROOT = Path(".").resolve()
RULES_FILE = ROOT / "auto-patch" / "rules.yaml"

class AutoPatcher:
    def __init__(self, rules_file: Path):
        self.rules_file = rules_file
        self.rules = self._load_rules()
        self.changes = []

    def _load_rules(self) -> List[Dict[str, Any]]:
        """Load patching rules from YAML"""
        if not self.rules_file.exists():
            print(f"ERROR: Rules file not found: {self.rules_file}")
            sys.exit(1)

        with open(self.rules_file, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('rules', [])

    def _find_files(self, patterns: List[str]) -> List[Path]:
        """Find files matching glob patterns"""
        files = set()
        for pattern in patterns:
            matched = glob.glob(str(ROOT / pattern), recursive=True)
            files.update(Path(f) for f in matched if os.path.isfile(f))
        return sorted(files)

    def _apply_rule(self, rule: Dict[str, Any], file_path: Path) -> bool:
        """Apply a rule to a file, return True if changed"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"ERROR: Could not read {file_path}: {e}")
            return False

        # Check if pattern matches
        match_pattern = rule.get('match', '')
        if not re.search(match_pattern, content):
            return False

        # For now, just add a comment marker (placeholder for real fix)
        # In production, implement actual fix logic based on rule['fix']
        fix_comment = f"\n<!-- AUTO-PATCH {rule['id']}: {rule['description']} -->\n"
        if rule['id'] not in content:
            patched = content + fix_comment

            if patched != content:
                if APPLY:
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(patched)
                        return True
                    except Exception as e:
                        print(f"ERROR: Could not write {file_path}: {e}")
                        return False
                else:
                    # Preview mode
                    return True

        return False

    def run(self):
        """Run all rules against matching files"""
        print(f"[autopatch] Mode: {'APPLY' if APPLY else 'PREVIEW'}")
        print(f"[autopatch] Loaded {len(self.rules)} rules")

        total_changes = 0

        for rule in self.rules:
            rule_id = rule.get('id', 'UNKNOWN')
            severity = rule.get('severity', 'P2')
            paths = rule.get('paths', [])

            print(f"\n[autopatch] Processing rule: {rule_id} ({severity})")
            print(f"[autopatch]   Description: {rule.get('description', 'N/A')}")

            files = self._find_files(paths)
            print(f"[autopatch]   Found {len(files)} matching files")

            changes_in_rule = 0
            for file_path in files:
                if self._apply_rule(rule, file_path):
                    rel_path = file_path.relative_to(ROOT)
                    print(f"[autopatch]   ✓ {rel_path}")
                    changes_in_rule += 1
                    self.changes.append({
                        'rule': rule_id,
                        'file': str(rel_path),
                        'severity': severity
                    })

            if changes_in_rule > 0:
                print(f"[autopatch]   Changed {changes_in_rule} files")
                total_changes += changes_in_rule

        print(f"\n[autopatch] Summary:")
        print(f"[autopatch]   Total changes: {total_changes}")
        print(f"[autopatch]   Mode: {'APPLIED' if APPLY else 'PREVIEW ONLY'}")

        if APPLY and total_changes > 0:
            self._create_branch_and_commit()

        return total_changes

    def _create_branch_and_commit(self):
        """Create a branch and commit changes"""
        import subprocess

        branch_name = "auto-patch/update"

        try:
            print(f"\n[autopatch] Creating branch: {branch_name}")
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)

            print(f"[autopatch] Staging changes...")
            subprocess.run(["git", "add", "."], check=True)

            # Create commit message
            commit_msg = "chore(auto-patch): Apply automated fixes\n\n"
            commit_msg += "Applied rules:\n"
            for change in self.changes:
                commit_msg += f"- {change['rule']}: {change['file']}\n"

            print(f"[autopatch] Committing changes...")
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)

            print(f"\n[autopatch] ✓ Changes committed to branch: {branch_name}")
            print(f"[autopatch] Next steps:")
            print(f"[autopatch]   1. Review changes: git diff main")
            print(f"[autopatch]   2. Push: git push -u origin {branch_name}")
            print(f"[autopatch]   3. Create PR via GitHub")

        except subprocess.CalledProcessError as e:
            print(f"ERROR: Git operation failed: {e}")
            sys.exit(1)

def main():
    patcher = AutoPatcher(RULES_FILE)
    changes = patcher.run()

    if not APPLY and changes > 0:
        print(f"\n[autopatch] To apply these changes, run:")
        print(f"[autopatch]   APPLY=true python3 auto-patch/autopatch.py")

    sys.exit(0 if changes == 0 else 0)  # Always exit 0 for now

if __name__ == "__main__":
    main()
