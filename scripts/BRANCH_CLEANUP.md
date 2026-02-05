# Branch Consolidation & Cleanup

Automated GitOps tool for safely consolidating and cleaning up branches in the repository.

## Purpose

- Merge priority branches (`chore/`, `fix/`, `refactor/`) into main
- Delete branches that are already merged
- Delete redundant branches (no diff from main)
- Preserve branches with unmerged work for manual review

## Features

- **Safe**: Dry-run mode by default
- **Idempotent**: Re-runnable without side effects
- **Conservative**: Only deletes merged/redundant branches
- **Transparent**: Detailed reporting and classification

## Usage

### Manual Execution

```bash
# Dry run (default - no changes)
bash scripts/branch_cleanup.sh

# Apply changes
DRY_RUN=false bash scripts/branch_cleanup.sh

# Custom repository
REPO_URL=https://github.com/Insightpulseai/odoo.git \
DRY_RUN=false \
bash scripts/branch_cleanup.sh
```

### GitHub Actions

**Manual Trigger:**
1. Go to Actions → Branch Cleanup
2. Click "Run workflow"
3. Select dry run mode (true/false)

**Automatic Schedule:**
- Runs monthly on the 1st at midnight (UTC)
- Always in dry-run mode for safety
- Review output, then run manually with `dry_run=false`

## Branch Classification

### Merged Branches → Delete
Branches already merged into main via PR or direct merge.

### Redundant Branches → Delete
Branches with no differences from main (empty or rebased).

### Priority Merge → Merge & Delete
Branches matching patterns:
- `chore/*` - Maintenance work
- `fix/*` - Bug fixes
- `refactor/*` - Code improvements

These are merged with `--no-ff` to preserve history.

### Divergent → Manual Review
Branches with unmerged commits that don't match priority patterns.
Requires manual review and decision.

## Example Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 1: Classify Branches
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ Merged: feature/old-implementation
  ≈ Redundant (no diff): hotfix/empty-branch
  → Priority merge: chore/update-dependencies
  ⚠ Divergent (manual review): feature/new-architecture

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 2: Merge Priority Branches
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔀 Merging: chore/update-dependencies
  ✅ Merged successfully

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 3: Delete Redundant Branches
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Deleting: feature/old-implementation
    ✅ Deleted
  Deleting: hotfix/empty-branch
    ✅ Deleted

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Merged branches:    1
Redundant branches: 1
Priority merges:    1
Divergent (review): 1
```

## Configuration

### Environment Variables

- `REPO_URL` - Repository URL (default: `https://github.com/Insightpulseai/odoo.git`)
- `REPO_DIR` - Local directory name (default: `odoo`)
- `DRY_RUN` - Dry run mode (default: `true`)
- `MAIN_BRANCH` - Main branch name (default: `main`)

### Customizing Merge Patterns

Edit the script to modify which branches are auto-merged:

```bash
# Current pattern (line ~80):
if echo "$branch" | grep -qE '^(chore/|fix/|refactor/)'; then

# Add more patterns:
if echo "$branch" | grep -qE '^(chore/|fix/|refactor/|docs/|style/)'; then
```

## Safety Features

1. **Dry Run Default**: No changes unless explicitly disabled
2. **Merge Conflict Handling**: Aborts merge on conflict, preserves branch
3. **Protected Branches**: Cannot delete protected branches
4. **Manual Review Queue**: Divergent branches flagged for review
5. **Verification Steps**: Post-cleanup validation and reporting

## Rollback

If a branch was deleted incorrectly:

```bash
# Find the commit SHA from git reflog or GitHub
git reflog | grep <branch-name>

# Recreate branch
git checkout -b restore/<branch-name> <commit-sha>
git push origin restore/<branch-name>
```

## Integration

### With CI/CD

```yaml
# .github/workflows/branch-cleanup.yml (already created)
name: Branch Cleanup
on:
  schedule:
    - cron: '0 0 1 * *'  # Monthly
  workflow_dispatch:
    inputs:
      dry_run:
        default: 'true'
jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash scripts/branch_cleanup.sh
```

### With Pre-deployment Checks

```bash
# Before major deployments, clean up branches
DRY_RUN=true bash scripts/branch_cleanup.sh
# Review output
DRY_RUN=false bash scripts/branch_cleanup.sh
```

## Governance

### Monthly Review Process

1. **Automated run** (1st of month, dry-run)
2. **Review output** in Actions logs
3. **Manual approval** via workflow dispatch
4. **Verify** main branch integrity
5. **Document** any manual branch preservations

### Branch Protection

Ensure `main` has protection rules:
- Require PR reviews
- Require status checks
- Prevent force push
- Prevent deletion

Verify with:
```bash
gh api repos/Insightpulseai/odoo/branches/main/protection
```

## Troubleshooting

### "Permission denied" when deleting

Branch may be protected or you lack permissions.

**Solution**: Check protection rules or use admin token.

### Merge conflicts

Priority branches with conflicts are skipped.

**Solution**: Manually merge with conflict resolution, then re-run.

### Divergent branches accumulate

Too many branches flagged for manual review.

**Solution**: Regularly review and merge/close divergent branches.

## Related Documentation

- [MONOREPO_STRUCTURE.md](../MONOREPO_STRUCTURE.md) - Repository layout
- [CI/CD Workflows](../.github/workflows/) - Automation pipelines
- [Git Workflow](https://docs.github.com/en/get-started/quickstart/github-flow) - GitHub flow guide
