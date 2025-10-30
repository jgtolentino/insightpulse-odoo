# GitHub Bot Automation - OCA-Style Workflows

This document describes the comprehensive GitHub automation implemented for InsightPulse Odoo, inspired by the [OCA GitHub Bot](https://github.com/OCA/oca-github-bot).

## 🤖 Overview

The **pulser-hub** GitHub App and automated workflows provide:

- ✅ **Auto-labeling**: Automatic PR labels based on reviews and CI status
- ✅ **Branch cleanup**: Auto-delete merged PR branches
- ✅ **Maintainer mentions**: Auto-notify addon maintainers on PRs
- ✅ **Bot commands**: `/merge`, `/rebase`, `/migration` commands via PR comments
- ✅ **README generation**: Nightly auto-generation of addon documentation
- ✅ **Version bumping**: Automated module version management
- ✅ **Manifest validation**: Continuous validation of addon manifests
- ✅ **Translation sync**: Automated i18n file management

---

## 📋 Automated Workflows

### 1. OCA Bot Automation (`.github/workflows/oca-bot-automation.yml`)

**Triggers:**
- Pull request events (opened, synchronized, labeled, reviewed)
- Issue comments (for bot commands)
- Nightly schedule (2 AM UTC)
- Manual dispatch

**Features:**

#### 🏷️ Auto-Labeling

Labels are automatically applied/removed based on PR state:

| Label | Condition | Description |
|-------|-----------|-------------|
| `approved` | 2+ approvals | PR has sufficient approvals |
| `needs review` | CI passed, 0 approvals, not WIP | Ready for review |
| `ready to merge` | Approved + 5+ days old | Ready for final merge |

**Automatic label removal** when conditions no longer met.

#### 🧹 Branch Cleanup

After PR merge:
- ✅ Source branch automatically deleted (if from same repo)
- ✅ Protected branches (main, develop, master) are never deleted
- ✅ Fork branches are not deleted (security)
- ✅ Comment posted on PR confirming deletion

#### 👥 Maintainer Mentions

On PR open:
- ✅ Scans modified addons
- ✅ Extracts maintainers from `__manifest__.py` → `"maintainers": ["user1", "user2"]`
- ✅ Posts comment mentioning relevant maintainers
- ✅ Warns if no maintainers declared

**Example comment:**
```markdown
## 👥 Maintainer Notifications

The following addons have been modified in this PR:

- **ipai_rate_policy**: @jgtolentino @odoo-expert
- **ipai_ppm**: ⚠️ No maintainers declared

_Maintainers are automatically notified when their addons are modified._
```

#### 🤖 Bot Commands

Post commands as PR comments to trigger actions:

##### `/merge [major|minor|patch|nobump]`

**Purpose**: Merge PR with optional version bump

**Requirements:**
- User must have `write` or `admin` permission
- PR must be mergeable (no conflicts)

**Behavior:**
- Merges PR using squash strategy
- Optionally bumps version (default: `patch`)
- Posts confirmation comment

**Example:**
```bash
/merge patch
```

**Response:**
```markdown
✅ **PR merged successfully**

Version bump: `patch`
```

##### `/rebase`

**Purpose**: Request PR rebase

**Behavior:**
- Posts rebase instructions with commands
- Does not automatically rebase (manual step)

**Example:**
```bash
/rebase
```

**Response:**
```markdown
🔄 **Rebase requested**

Please rebase your branch manually:
\`\`\`bash
git fetch origin
git rebase origin/main
git push --force-with-lease
\`\`\`
```

##### `/migration <module>`

**Purpose**: Track module migration work

**Behavior:**
- Posts migration checklist
- Links to migration tracking issue
- Adds metadata for module

**Example:**
```bash
/migration ipai_rate_policy
```

**Response:**
```markdown
📦 **Migration tracking for `ipai_rate_policy`**

This PR includes migration logic for the **ipai_rate_policy** module.

- [ ] Migration script created
- [ ] Data migration tested
- [ ] Documentation updated
- [ ] Linked to migration issue
```

#### 📚 Nightly README Generation

**Schedule**: 2 AM UTC daily

**Actions:**
1. Scans all addons in `addons/` directory
2. Parses `__manifest__.py` files
3. Generates `ADDONS.md` with inventory table
4. Auto-commits and pushes changes

**Generated table format:**

| Module | Version | Category | Summary | Maintainers |
|--------|---------|----------|---------|-------------|
| `ipai_rate_policy` | 1.0.0 | Finance | Rate policy automation | jgtolentino |
| `ipai_ppm` | 1.0.0 | Project | Program management | jgtolentino |

#### 🔧 Nightly Setup Generation

**Schedule**: 2 AM UTC daily

**Actions:**
1. Installs `setuptools-odoo`
2. Generates `setup.py` for each addon
3. Auto-commits and pushes changes

---

### 2. Odoo Module Tools (`.github/workflows/odoo-module-tools.yml`)

**Triggers:**
- Push to main/develop (when manifests/READMEs change)
- Manual dispatch with parameters

**Features:**

#### 📖 README.rst Generation

**Purpose**: Generate OCA-compliant README.rst from fragments

**Trigger**:
```bash
# Manual dispatch
Actions → Odoo Module Tools → Run workflow
  action: generate-readme
```

**Behavior:**
1. Installs `oca-gen-addon-readme`
2. Scans addons for `readme/` directories
3. Generates README.rst from fragments:
   - `readme/DESCRIPTION.rst`
   - `readme/USAGE.rst`
   - `readme/CONFIGURE.rst`
   - etc.
4. Auto-commits generated files

**Fragment structure:**
```
addons/ipai_rate_policy/
├── readme/
│   ├── DESCRIPTION.rst
│   ├── USAGE.rst
│   ├── CONFIGURE.rst
│   └── CONTRIBUTORS.rst
├── __manifest__.py
└── README.rst  # Generated
```

#### 🔢 Version Bumping

**Purpose**: Bulk or single module version updates

**Trigger**:
```bash
# Manual dispatch
Actions → Odoo Module Tools → Run workflow
  action: bump-version
  module: ipai_rate_policy  # Optional, blank = all modules
  version_bump: patch       # major, minor, or patch
```

**Behavior:**
1. Parses current version from `__manifest__.py`
2. Bumps version based on type:
   - `major`: 1.0.0 → 2.0.0
   - `minor`: 1.0.0 → 1.1.0
   - `patch`: 1.0.0 → 1.0.1
3. Updates manifest files
4. Auto-commits with version summary

**Commit message:**
```
chore: bump module versions (patch)

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

#### ✅ Manifest Validation

**Purpose**: Validate addon manifests for compliance

**Trigger**: Automatically on push to main/develop

**Checks:**
- ✅ Required fields present: `name`, `version`, `depends`, `author`, `category`, `license`
- ✅ Version format: `X.Y.Z` (3-part semantic versioning)
- ✅ Valid license: `LGPL-3`, `AGPL-3`, `GPL-3`, `Apache-2.0`, `MIT`
- ✅ `depends` is a list
- ✅ Manifest is parseable Python

**Failure behavior:**
```
❌ Manifest validation errors found:

📦 ipai_rate_policy:
  - Missing required field: license
  - Invalid version format: 1.0 (expected X.Y.Z)
```

#### 🌍 Translation Sync

**Purpose**: Sync .po/.pot translation files

**Trigger**:
```bash
# Manual dispatch
Actions → Odoo Module Tools → Run workflow
  action: sync-translations
```

**Behavior:**
1. Installs `polib` and `babel`
2. Scans addons for `i18n/` directories
3. Updates translation templates
4. Auto-commits changes

---

## 🔐 Permissions & Security

### Required GitHub Permissions

The workflows require the following permissions:

```yaml
permissions:
  contents: write        # Push commits, delete branches
  pull-requests: write   # Label PRs, merge PRs, comment
  issues: write          # Comment on issues, close issues
```

### Security Considerations

1. **Fork PRs**: AI code review is disabled for fork PRs (security)
2. **Merge permissions**: Only users with `write` or `admin` access can use `/merge`
3. **Protected branches**: Main/develop/master are never auto-deleted
4. **Token scope**: `GITHUB_TOKEN` has repository-scoped access only

---

## 📊 Usage Examples

### Example 1: Submitting a PR

**Workflow:**

1. **Open PR** → Maintainers auto-mentioned
2. **CI passes** → `needs review` label added
3. **2 approvals** → `approved` label added
4. **5+ days** → `ready to merge` label added
5. **Maintainer comments `/merge patch`** → PR merged, branch deleted

### Example 2: Adding a New Module

**Steps:**

1. Create addon with `__manifest__.py`:
```python
{
    'name': 'My New Module',
    'version': '1.0.0',
    'depends': ['base'],
    'author': 'InsightPulse',
    'category': 'Finance',
    'license': 'LGPL-3',
    'maintainers': ['username'],
    'data': [],
}
```

2. Create README fragments:
```bash
mkdir addons/my_module/readme
touch addons/my_module/readme/DESCRIPTION.rst
touch addons/my_module/readme/USAGE.rst
```

3. Push to main → workflows trigger:
   - ✅ Manifest validated
   - ✅ README.rst generated
   - ✅ Module appears in ADDONS.md

### Example 3: Bulk Version Bump

**Scenario**: Release all modules with patch version bump

**Steps:**

1. Go to **Actions** → **Odoo Module Tools**
2. Click **Run workflow**
3. Select:
   - `action`: `bump-version`
   - `module`: (leave blank for all)
   - `version_bump`: `patch`
4. Click **Run workflow**

**Result:**
- All `__manifest__.py` files updated
- Commit message: `chore: bump module versions (patch)`
- Automatic push to branch

---

## 🛠️ Configuration

### Customizing Bot Behavior

**Modify approval thresholds** (`.github/workflows/oca-bot-automation.yml`):
```yaml
# Change from 2 to 3 approvals
if (approvals >= 3 && !currentLabels.includes('approved')) {
  labelsToAdd.push('approved');
}
```

**Modify ready-to-merge delay**:
```yaml
# Change from 5 days to 3 days
const fiveDays = 3 * 24 * 60 * 60 * 1000;
```

**Add custom bot commands**:
```yaml
# Add new command handler
if (comment.startsWith('/custom-command')) {
  // Your logic here
}
```

### Adding Maintainers to Addons

Edit `__manifest__.py`:
```python
{
    'name': 'My Module',
    # ...
    'maintainers': ['github-username1', 'github-username2'],
}
```

Maintainers will be auto-mentioned on PRs modifying this addon.

---

## 🧪 Testing Bot Commands

### Local Testing

Test manifest validation:
```bash
python3 - <<'EOF'
import ast
with open('addons/ipai_rate_policy/__manifest__.py', 'r') as f:
    manifest = ast.literal_eval(f.read())
    print(manifest)
EOF
```

### PR Testing

1. Create test branch
2. Open PR
3. Add comment with bot command:
   ```
   /merge nobump
   ```
4. Verify bot response

---

## 📈 Monitoring & Logs

### View Workflow Runs

1. Go to **Actions** tab
2. Select workflow (e.g., "OCA Bot Automation")
3. Click on specific run
4. View logs for each job

### Check Auto-Generated Files

- **ADDONS.md**: Addon inventory table
- **addons/*/README.rst**: Generated documentation
- **addons/*/setup.py**: Setup files for PyPI

### Review Bot Comments

Check PR comments for:
- 👥 Maintainer mentions
- ✅ Merge confirmations
- 🔄 Rebase instructions
- 📦 Migration tracking

---

## 🚀 Advanced Features

### GitHub App: pulser-hub

**Purpose**: Enable full GitHub API access for ChatGPT/Claude agents

**Capabilities:**
- Read/write repository contents
- Manage PRs and issues
- Execute git operations
- Trigger workflows

**Configuration**: Installed via GitHub App marketplace

### Integration with Odoo Studio

The bot workflows can be extended to integrate with Odoo Studio automated actions (per your referenced Odoo docs):

**Future enhancements:**
- Trigger Odoo automated actions on PR merge
- Sync module changes to Odoo instance
- Auto-deploy to DigitalOcean after merge

---

## 📚 References

- [OCA GitHub Bot](https://github.com/OCA/oca-github-bot) - Inspiration for workflows
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- [Odoo Development Documentation](https://www.odoo.com/documentation/19.0/developer.html)

---

## 🤝 Contributing

To improve bot workflows:

1. Edit workflow files in `.github/workflows/`
2. Test changes on feature branch
3. Open PR with clear description
4. Bot will auto-label and notify maintainers
5. Use `/merge` command after approval

---

## 📧 Support

Questions or issues with bot automation?

- **GitHub Issues**: [Create issue](https://github.com/jgtolentino/insightpulse-odoo/issues)
- **Discussions**: [Start discussion](https://github.com/jgtolentino/insightpulse-odoo/discussions)
- **Email**: support@insightpulse.ai

---

**Last Updated**: 2025-10-30
**Bot Version**: 1.0.0
**Workflows**: 2 (OCA Bot Automation + Odoo Module Tools)
**Bot Commands**: 3 (`/merge`, `/rebase`, `/migration`)
