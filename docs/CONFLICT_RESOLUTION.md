# 🤖 Automated Conflict Resolution System

Complete guide to the InsightPulse Odoo automated conflict resolution system.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Components](#components)
5. [Usage Guide](#usage-guide)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## 🎯 Overview

The InsightPulse Odoo conflict resolution system provides **automated, intelligent merge conflict resolution** using a 3-tier strategy:

```
┌─────────────────────────────────────────────┐
│   TIER 1: Simple Conflicts (Auto-Fix)      │
│   • Whitespace/formatting                   │
│   • Import reordering                       │
│   • Non-overlapping changes                 │
│   SUCCESS RATE: ~70%                        │
├─────────────────────────────────────────────┤
│   TIER 2: AI Resolution (Claude)            │
│   • Semantic understanding                  │
│   • Context-aware merging                   │
│   • Pattern matching                        │
│   SUCCESS RATE: ~25%                        │
├─────────────────────────────────────────────┤
│   TIER 3: Human Review (Flag for Review)    │
│   • Complex logic conflicts                 │
│   • Business rule changes                   │
│   SUCCESS RATE: ~5% (needs human)           │
└─────────────────────────────────────────────┘
```

### Key Features

- ✅ **Automatic conflict detection** on pull requests
- ✅ **AI-powered resolution** using Claude Sonnet 4
- ✅ **YAML-specific semantic merge** for workflow files
- ✅ **File-type specific strategies** (lock files, configs, etc.)
- ✅ **Validation checks** (YAML, Python, JSON syntax)
- ✅ **Rerere integration** (remembers past resolutions)
- ✅ **Manual fallback** with helper scripts

---

## 🏗️ Architecture

### System Components

```
┌──────────────────────────────────────────────────────────┐
│                     GitHub Actions                        │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  auto-resolve-conflicts.yml                        │  │
│  │  • Detects conflicts on PR                         │  │
│  │  • Triggers resolution pipeline                    │  │
│  │  • Posts results as PR comment                     │  │
│  └────────────────────────────────────────────────────┘  │
│                          ▼                                │
└──────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌────────────────┐ ┌──────────────┐ ┌─────────────────┐
│  Simple Merge  │ │ AI Resolver  │ │  Manual Helper  │
│   Strategies   │ │   (Claude)   │ │     Script      │
│                │ │              │ │                 │
│ • Patience     │ │ • Semantic   │ │ • Interactive   │
│ • Ours/Theirs  │ │ • Context    │ │ • Validation    │
│ • YAML merge   │ │ • AI-powered │ │ • Editor integration
└────────────────┘ └──────────────┘ └─────────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           ▼
              ┌────────────────────────┐
              │   Validation Layer     │
              │ • Syntax checks        │
              │ • Test execution       │
              │ • Commit if successful │
              └────────────────────────┘
```

### File Structure

```
insightpulse-odoo/
├── .github/
│   ├── workflows/
│   │   └── auto-resolve-conflicts.yml    # GitHub Action workflow
│   └── scripts/
│       ├── ai-conflict-resolver.py       # AI-powered resolver
│       └── yaml-merge.py                 # YAML semantic merge
│
├── scripts/
│   ├── resolve-conflicts.sh              # Manual helper script
│   └── setup/
│       └── configure-git-merge-strategies.sh  # Git config
│
├── docs/
│   └── CONFLICT_RESOLUTION.md            # This file
│
└── .gitattributes                        # Merge strategies config
```

---

## 🚀 Quick Start

### 1. Initial Setup

Run the configuration script to set up Git merge strategies:

```bash
./scripts/setup/configure-git-merge-strategies.sh
```

This will:
- Enable rerere (Reuse Recorded Resolution)
- Configure merge drivers for different file types
- Create/update `.gitattributes`
- Make scripts executable

### 2. Configure GitHub Secrets

For AI-powered resolution, add your Anthropic API key to GitHub Secrets:

1. Go to your repository settings
2. Navigate to **Secrets and variables** → **Actions**
3. Add new secret:
   - Name: `ANTHROPIC_API_KEY`
   - Value: Your Anthropic API key

### 3. Test the System

Create a test branch and simulate a conflict:

```bash
# Create test branch
git checkout -b test-conflict-resolution

# Make changes to a YAML file
echo "test: value" >> .github/workflows/ci-unified.yml

# Commit
git commit -am "Test: add config"

# Try to merge main (if there are conflicts)
git fetch origin main
git merge origin/main

# The system should detect and attempt to resolve automatically
```

---

## 🔧 Components

### 1. GitHub Action Workflow

**File:** `.github/workflows/auto-resolve-conflicts.yml`

**Triggers:**
- On pull request open/update
- Manual workflow dispatch

**Jobs:**
1. **detect-conflicts** - Check if conflicts exist
2. **auto-resolve** - Attempt automatic resolution
3. **no-conflicts** - Report clean merge

**Features:**
- Multiple merge strategies (patience, ours, theirs)
- AI-powered resolution using Claude
- Syntax validation (YAML, Python, JSON)
- Automatic commit and push
- PR comments with results

### 2. AI Conflict Resolver

**File:** `.github/scripts/ai-conflict-resolver.py`

**How it works:**

1. **Detects conflicts** - Scans for Git conflict markers
2. **Extracts context** - Gets surrounding code for better understanding
3. **Calls Claude API** - Sends conflict to AI for resolution
4. **Validates response** - Checks confidence score and strategy
5. **Applies resolution** - Replaces conflict markers with resolved code

**Configuration:**

```python
# Confidence threshold (default: 0.8)
resolver.resolve_all(confidence_threshold=0.8)

# Max files to auto-resolve (default: 10)
resolver.resolve_all(max_files=10)
```

**Example usage:**

```bash
# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run resolver
python .github/scripts/ai-conflict-resolver.py \
  --base-ref origin/main \
  --head-ref HEAD \
  --max-auto-resolve 10 \
  --confidence-threshold 0.8
```

### 3. YAML Semantic Merge

**File:** `.github/scripts/yaml-merge.py`

**Features:**
- Understands YAML structure (dicts, lists, scalars)
- Merges lists intelligently (by ID/name if available)
- Preserves both changes when possible
- Maintains YAML formatting

**Strategy:**

```python
# Dictionaries: recursive merge
{ours} + {theirs} = {merged}

# Lists with IDs: merge by identifier
- name: item1      - name: item1
  value: A    +      value: B    = merged by name
- name: item2      - name: item3

# Scalars: prefer who changed
base: 1            base: 1
ours: 2     +      theirs: 1    = ours (we changed, they didn't)
```

### 4. Manual Resolution Helper

**File:** `scripts/resolve-conflicts.sh`

**Usage:**

```bash
# Basic usage
./scripts/resolve-conflicts.sh feature/my-branch

# With options
./scripts/resolve-conflicts.sh feature/my-branch \
  --base-branch develop \
  --auto-commit

# Skip AI resolution
./scripts/resolve-conflicts.sh feature/my-branch --skip-ai
```

**What it does:**

1. Checks out branch
2. Fetches and merges base branch
3. Attempts AI resolution (unless `--skip-ai`)
4. Opens editor for manual resolution if needed
5. Validates resolved files
6. Commits changes (if `--auto-commit`)

---

## 📖 Usage Guide

### Scenario 1: Automatic Resolution on PR

**When:** You open a pull request with conflicts

**What happens:**

1. GitHub Action detects conflicts
2. Attempts simple merge strategies first
3. Falls back to AI resolution if needed
4. Posts comment on PR with results

**Success:**
```
✅ Merge conflicts automatically resolved!

Strategy used: ai-powered

Conflicted files:
- .github/workflows/odoo_addon.yml

Validation:
- ✅ YAML syntax check passed
- ✅ Python syntax check passed
- ✅ JSON syntax check passed
```

**Failure:**
```
⚠️ Unable to automatically resolve conflicts

These conflicts require human review:
- custom/finance_ssc/models/account_move.py

Next steps:
1. Checkout the branch locally
2. Run: ./scripts/resolve-conflicts.sh your-branch
```

### Scenario 2: Manual Resolution Locally

**When:** Automatic resolution fails or you prefer manual control

**Steps:**

```bash
# 1. Checkout your branch
git checkout feature/my-feature

# 2. Run resolution helper
./scripts/resolve-conflicts.sh feature/my-feature

# 3. The script will:
#    - Fetch latest changes
#    - Attempt merge
#    - Try AI resolution
#    - Open editor if needed
#    - Validate files
#    - Commit (if you choose)

# 4. Push when ready
git push origin feature/my-feature
```

### Scenario 3: Resolving Specific File Types

#### YAML Files

YAML files use semantic merge automatically (via `.gitattributes`):

```bash
# Git will use yaml-merge.py automatically
git merge origin/main

# Check if YAML is valid
python -c "import yaml; yaml.safe_load(open('file.yml'))"
```

#### Lock Files

Lock files (package-lock.json, yarn.lock, etc.) automatically prefer "theirs":

```bash
# These are accepted from base branch automatically
# Regenerate after merge:
npm install  # or yarn, pip, etc.
```

#### Python Files

Standard merge with validation:

```bash
# After resolving, validate syntax
python -m py_compile file.py

# Or use the helper which validates automatically
./scripts/resolve-conflicts.sh feature/my-feature
```

### Scenario 4: Testing Conflict Resolution

Before relying on the system, test it:

```bash
# 1. Create test branch
git checkout -b test-conflict-$(date +%s)

# 2. Introduce intentional conflict
echo "new_value: test" >> .github/workflows/ci-unified.yml
git commit -am "Test conflict"

# 3. Merge main to create conflict
git merge origin/main

# 4. Test AI resolver
export ANTHROPIC_API_KEY="your-key"
python .github/scripts/ai-conflict-resolver.py \
  --base-ref origin/main \
  --head-ref HEAD

# 5. Check result
git diff

# 6. Clean up
git merge --abort
git checkout main
git branch -D test-conflict-*
```

---

## ⚙️ Configuration

### Git Configuration

The system configures Git with:

```bash
# Rerere - remember resolutions
git config rerere.enabled true
git config rerere.autoupdate true

# Conflict style - show base, ours, theirs
git config merge.conflictstyle diff3

# Merge drivers
git config merge.yaml.driver "python .github/scripts/yaml-merge.py %O %A %B"
git config merge.ours.driver true
git config merge.theirs.driver "git merge-file --theirs %O %A %B"

# Better diff algorithm
git config diff.algorithm patience
```

### File-Specific Strategies

Configured in `.gitattributes`:

```gitattributes
# YAML - semantic merge
*.yml merge=yaml

# Lock files - prefer theirs
package-lock.json merge=theirs

# Environment - prefer ours
.env merge=ours

# Documentation - union merge (combine both)
*.md merge=union
```

### Environment Variables

Required for AI resolution:

```bash
# Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional: Override default model
export AI_MODEL="claude-sonnet-4-20250514"
```

### GitHub Action Configuration

Customize in `.github/workflows/auto-resolve-conflicts.yml`:

```yaml
- name: AI-Powered Resolution
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    python .github/scripts/ai-conflict-resolver.py \
      --base-ref "origin/$BASE_BRANCH" \
      --head-ref HEAD \
      --max-auto-resolve 10 \          # Max files to auto-resolve
      --confidence-threshold 0.8       # Min confidence (0-1)
```

---

## 🔍 Troubleshooting

### Issue: AI Resolution Not Triggered

**Symptoms:**
- GitHub Action runs but skips AI resolution
- No Claude API calls in logs

**Causes:**
1. `ANTHROPIC_API_KEY` not set in GitHub Secrets
2. Too many conflicts (exceeds `max-auto-resolve`)
3. Python dependencies not installed

**Solutions:**

```bash
# Check GitHub secret
# Go to Settings → Secrets → Check ANTHROPIC_API_KEY exists

# Check logs for error messages
# Look for: "ANTHROPIC_API_KEY not set"

# Test locally
export ANTHROPIC_API_KEY="your-key"
python .github/scripts/ai-conflict-resolver.py --help

# Check dependencies
pip install anthropic pyyaml gitpython
```

### Issue: YAML Merge Fails

**Symptoms:**
- YAML conflicts not auto-resolved
- Merge markers still present in YAML files

**Causes:**
1. YAML merge driver not configured
2. Invalid YAML syntax in conflict
3. Git attributes not loaded

**Solutions:**

```bash
# Reconfigure Git
./scripts/setup/configure-git-merge-strategies.sh

# Check Git config
git config --list | grep merge.yaml

# Should show:
# merge.yaml.driver=python .github/scripts/yaml-merge.py %O %A %B

# Check .gitattributes
cat .gitattributes | grep yaml

# Test YAML merge manually
python .github/scripts/yaml-merge.py base.yml ours.yml theirs.yml
```

### Issue: Validation Fails After Resolution

**Symptoms:**
- Conflicts resolved but commit fails
- Syntax errors in resolved files

**Causes:**
1. AI resolution introduced syntax errors
2. Incomplete conflict resolution
3. Invalid code before merge

**Solutions:**

```bash
# Check specific file type
python -c "import yaml; yaml.safe_load(open('file.yml'))"  # YAML
python -m py_compile file.py  # Python
python -c "import json; json.load(open('file.json'))"  # JSON

# Re-run with manual review
./scripts/resolve-conflicts.sh feature/branch --skip-ai

# Check conflict markers remain
git diff --check

# Look for remaining markers
grep -r "<<<<<<< " .
grep -r "=======" .
grep -r ">>>>>>> " .
```

### Issue: GitHub Action Fails with Permissions

**Symptoms:**
- Action runs but cannot push
- Error: "Permission denied"

**Causes:**
1. Insufficient token permissions
2. Branch protection rules
3. Repository settings

**Solutions:**

```yaml
# Check workflow permissions
permissions:
  contents: write        # Need write to push
  pull-requests: write   # Need write to comment

# Check branch protection
# Go to Settings → Branches → Check protection rules
# May need to allow Actions to bypass

# Check token scope
# Go to Settings → Actions → General
# Workflow permissions → Read and write permissions
```

### Issue: Rerere Not Working

**Symptoms:**
- Same conflicts appear repeatedly
- Rerere not remembering resolutions

**Causes:**
1. Rerere not enabled
2. Rerere cache cleared
3. Conflict differs slightly each time

**Solutions:**

```bash
# Enable rerere
git config rerere.enabled true
git config rerere.autoupdate true

# Check rerere status
git rerere status

# View recorded resolutions
git rerere diff

# Check rerere cache
ls -la .git/rr-cache/

# Manually train rerere
# 1. Create conflict
git merge branch-with-conflict
# 2. Resolve manually
# ... edit files ...
git add resolved-file
# 3. Commit
git commit
# 4. Rerere now knows this resolution
```

---

## 💡 Best Practices

### 1. Keep PRs Small

**Why:** Smaller PRs = fewer conflicts = higher auto-resolution success

**How:**
```bash
# Instead of one large PR
git checkout -b large-feature
# ... make 50 changes across 20 files ...

# Do multiple smaller PRs
git checkout -b feature-part1  # 5 files
git checkout -b feature-part2  # 5 files
git checkout -b feature-part3  # 5 files
```

### 2. Merge Main Frequently

**Why:** Reduces divergence = easier merges

**How:**
```bash
# Daily or after major changes
git checkout feature/my-branch
git fetch origin main
git merge origin/main

# Or rebase if preferred (no merge commits)
git rebase origin/main
```

### 3. Use Semantic Commits

**Why:** Helps AI understand intent

**How:**
```bash
# Good commits (AI can understand intent)
git commit -m "feat: add BIR 1601C validation"
git commit -m "fix: resolve month-end closing bug"
git commit -m "refactor: extract common validation logic"

# Bad commits (AI has no context)
git commit -m "updates"
git commit -m "fix"
git commit -m "wip"
```

### 4. Test Before Pushing

**Why:** Catch issues early

**How:**
```bash
# After resolving conflicts, test locally
./scripts/resolve-conflicts.sh feature/branch

# Run tests
make test
# or
pytest tests/

# Check specific modules
python -m pytest tests/test_bir_compliance.py

# Only push if tests pass
git push origin feature/branch
```

### 5. Review AI Resolutions

**Why:** AI is not perfect, verify critical changes

**How:**
```bash
# After AI resolution, review changes
git diff

# Check specific files
git diff .github/workflows/odoo_addon.yml

# Look for logical errors (syntax may be correct but logic wrong)
# Especially for business logic files

# If unsure, test thoroughly
make test-all
```

### 6. Train Rerere

**Why:** Git learns your patterns

**How:**
```bash
# When you manually resolve a conflict
# 1. Git records it automatically (if rerere enabled)
# 2. Next time same conflict = automatic resolution

# Check what rerere knows
git rerere status
git rerere diff

# To train rerere on a specific pattern:
# 1. Create conflict
# 2. Resolve manually
# 3. Complete merge
# 4. Rerere remembers
```

### 7. Use Proper File Types in .gitattributes

**Why:** Enables smart merge strategies

**How:**
```gitattributes
# Add new file types as needed

# Custom config format
*.custom merge=ours

# Special data format
*.data merge=union

# Binary format
*.special binary
```

### 8. Monitor Success Rates

**Why:** Identify patterns in failures

**How:**
```bash
# Check GitHub Action logs
# Look for patterns in:
# - Which files fail most often
# - Which types of conflicts (YAML, Python, etc.)
# - Confidence scores from AI

# Example log analysis:
gh run list --workflow=auto-resolve-conflicts.yml --limit 50
gh run view <run-id> --log | grep "confidence:"
```

### 9. Document Complex Merges

**Why:** Help future you and teammates

**How:**
```bash
# When manually resolving complex conflict, document
git commit -m "Merge main into feature/complex

Resolved conflicts in:
- finance_ssc/models/account_move.py
  - Combined new validation logic from both branches
  - Kept our BIR compliance checks
  - Added their performance optimization

- bir_compliance/models/bir_form.py
  - Updated form structure to latest BIR spec
  - Preserved our custom field validations
"
```

### 10. Fallback Plan

**Why:** System may fail, have backup process

**How:**
```bash
# If auto-resolution fails
# 1. Use manual helper
./scripts/resolve-conflicts.sh feature/branch

# 2. If that fails, manual resolution
git merge origin/main
# ... edit files manually ...
git add .
git commit

# 3. Ask for help if stuck
# - Check docs
# - Ask team
# - Create issue with details
```

---

## 📊 Success Metrics

Track these metrics to measure system effectiveness:

### Auto-Resolution Rate
```
Auto-resolved PRs / Total PRs with conflicts

Target: > 80%
```

### Average Resolution Time
```
Time from conflict detection to resolution

Target: < 5 minutes (automated)
Target: < 30 minutes (manual with helper)
```

### Validation Pass Rate
```
Successful validations / Total resolutions

Target: > 95%
```

### Post-Merge Test Success
```
Tests passing after merge / Total merges

Target: > 99%
```

---

## 🆘 Getting Help

### Documentation
- This guide: `docs/CONFLICT_RESOLUTION.md`
- Git merge drivers: https://git-scm.com/docs/gitattributes
- Rerere: https://git-scm.com/docs/git-rerere

### Command Help
```bash
# AI resolver help
python .github/scripts/ai-conflict-resolver.py --help

# Manual helper help
./scripts/resolve-conflicts.sh --help

# Git config script
./scripts/setup/configure-git-merge-strategies.sh
```

### Support Channels
- GitHub Issues: Report bugs or request features
- Team Chat: Ask in #dev-ops or #engineering
- Code Review: Request help in PR comments

---

## 🔄 System Updates

To update the conflict resolution system:

```bash
# 1. Pull latest changes
git pull origin main

# 2. Re-run setup
./scripts/setup/configure-git-merge-strategies.sh

# 3. Test
./scripts/resolve-conflicts.sh --help

# 4. Check GitHub Action
# Push a test branch and create PR
```

---

## 📝 Contributing

To improve the conflict resolution system:

1. **Report Issues:** Create GitHub issue with:
   - Conflict details
   - Expected vs actual behavior
   - Logs/screenshots

2. **Submit PRs:**
   - Update scripts in `.github/scripts/` or `scripts/`
   - Update documentation
   - Add tests if applicable

3. **Share Patterns:**
   - Document successful resolution patterns
   - Add to `.gitattributes` if useful
   - Update this guide

---

**Need help?** Contact the DevOps team or create an issue on GitHub.

**Last updated:** 2025-11-05
