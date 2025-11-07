#!/usr/bin/env python3
"""
Skillsmith PR Proposal: Create PR with generated skill candidates
"""
import os, subprocess, json, pathlib, sys, datetime

def run(cmd, **kwargs):
    """Run command and return output"""
    print(f"→ {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kwargs)

def main():
    """Create PR with skill proposals"""
    repo = os.getenv("GITHUB_REPOSITORY") or ""
    run_id = os.getenv("GITHUB_RUN_ID", datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S"))
    branch = f"skillsmith/{run_id}"

    # Check if there are files to propose
    proposed_dir = pathlib.Path("skills/proposed")
    if not proposed_dir.exists() or not list(proposed_dir.glob("*.yaml")):
        print("No skill candidates to propose")
        return

    files = list(proposed_dir.glob("*.yaml"))
    print(f"Found {len(files)} skill candidates to propose")

    # Configure git
    run(["git", "config", "user.email", "bot@insightpulseai.net"])
    run(["git", "config", "user.name", "skillsmith-bot"])

    # Create branch
    try:
        run(["git", "checkout", "-b", branch])
    except subprocess.CalledProcessError:
        print(f"Branch {branch} may already exist, using it")
        run(["git", "checkout", branch])

    # Add and commit
    run(["git", "add", "skills/proposed"])

    # Check if there are changes to commit
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
    if result.returncode == 0:
        print("No changes to commit")
        return

    # Create summary of what's being proposed
    summary_lines = ["# Skillsmith: Proposed Skills\n"]
    summary_lines.append("Auto-generated skill candidates from error mining.\n")
    summary_lines.append(f"\n## Candidates ({len(files)} skills)\n")

    for f in files:
        content = f.read_text()
        # Extract key metadata
        if "id:" in content:
            for line in content.split('\n'):
                if line.startswith('id:'):
                    skill_id = line.split(':', 1)[1].strip()
                    summary_lines.append(f"- **{skill_id}**: {f.name}")
                    break

    summary = "\n".join(summary_lines)

    # Commit
    commit_msg = f"""chore(skillsmith): propose {len(files)} new skills from error mining

Generated {len(files)} skill candidates:
- Mining run: {run_id}
- Source: error_signatures (30d window)

{summary}

To approve:
1. Review skill definitions in skills/proposed/
2. Create autopatch scripts for fixers (if needed)
3. Move approved skills to skills/ directory
4. Set status: approved
5. Run: make retrain
"""
    run(["git", "commit", "-m", commit_msg])

    # Push if we have a repo
    if repo:
        try:
            run(["git", "push", "-u", "origin", branch])
            print(f"✓ Pushed to branch: {branch}")

            # Create PR using gh CLI
            pr_body = f"""{summary}

## Review Process

1. **Review** each skill definition in `skills/proposed/`
2. **Test** guardrails don't cause false positives
3. **Implement** autopatch scripts for fixers (see TODOs in YAML)
4. **Approve** by moving to `skills/` with `status: approved`
5. **Retrain** by running `make retrain`

## Metadata

- Mining run: `{run_id}`
- Source: `error_signatures` (30d window)
- Generated: {datetime.datetime.utcnow().isoformat()}Z
"""
            run([
                "gh", "pr", "create",
                "--title", f"Skillsmith: {len(files)} proposed skills from error mining",
                "--body", pr_body,
                "--repo", repo,
                "--head", branch,
            ])
            print("✓ PR created successfully")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not create PR: {e}")
            print("Changes committed locally on branch:", branch)
    else:
        print(f"Changes committed locally on branch: {branch}")
        print("(No GITHUB_REPOSITORY set, skipping push/PR)")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
