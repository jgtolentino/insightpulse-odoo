# Maintainers Guide

This document describes the maintainer system for InsightPulse Odoo modules.

## 📋 Overview

Each addon in the `addons/` directory can declare **maintainers** in its `__manifest__.py` file. Maintainers are automatically notified when their modules are modified in pull requests.

---

## 👥 Current Maintainers

### Core Platform
- **@jgtolentino** - Project lead, core architecture

### Finance Modules

#### ipai_rate_policy
- **@jgtolentino** - Rate calculation logic, P60 compliance

#### ipai_ppm
- **@jgtolentino** - Program/project management, budget tracking

#### ipai_ppm_costsheet
- **@jgtolentino** - Cost sheet analysis, role-based visibility

#### ipai_expense
- **@jgtolentino** - OCR integration, expense workflows

#### ipai_subscriptions
- **@jgtolentino** - Recurring revenue, subscription management

#### ipai_approvals
- **@jgtolentino** - Multi-stage approval workflows

### Operations Modules

#### ipai_saas_ops
- **@jgtolentino** - Multi-tenant provisioning, SaaS operations

#### ipai_procure
- **@jgtolentino** - Procurement, RFQ workflows

#### superset_connector
- **@jgtolentino** - BI dashboard integration

### Knowledge & AI

#### ipai_knowledge_ai
- **@jgtolentino** - Semantic search, pgVector integration

---

## 🔧 How to Declare Maintainers

### In __manifest__.py

Add maintainers to your module manifest:

```python
{
    'name': 'My Awesome Module',
    'version': '1.0.0',
    'category': 'Finance',
    'summary': 'Brief description',
    'depends': ['base'],
    'author': 'InsightPulse',
    'license': 'LGPL-3',
    'maintainers': ['github-username1', 'github-username2'],
    'data': [],
}
```

**Important:**
- Use GitHub usernames (without `@`)
- Maintainers will be auto-mentioned on PRs
- Multiple maintainers are supported

---

## 📬 Maintainer Notifications

### Automatic Mentions

When a PR modifies files in your addon:

1. **Bot scans** changed files
2. **Extracts** addon paths from changes
3. **Reads** `__manifest__.py` for maintainers
4. **Posts comment** mentioning maintainers

**Example notification:**
```markdown
## 👥 Maintainer Notifications

The following addons have been modified in this PR:

- **ipai_rate_policy**: @jgtolentino
- **ipai_ppm**: @jgtolentino @odoo-expert
```

### No Maintainers Warning

If no maintainers are declared:
```markdown
- **custom_module**: ⚠️ No maintainers declared
```

---

## 🛠️ Maintainer Responsibilities

### Code Review
- ✅ Review PRs modifying your addons
- ✅ Approve changes after validation
- ✅ Request changes if needed

### Documentation
- ✅ Keep README.rst up to date
- ✅ Update CHANGELOG.md for significant changes
- ✅ Maintain usage examples

### Testing
- ✅ Ensure tests cover new features
- ✅ Verify CI passes before approval
- ✅ Test locally for complex changes

### Versioning
- ✅ Use `/merge [major|minor|patch]` for version bumps
- ✅ Follow semantic versioning
- ✅ Update version in manifest when needed

### Bug Triage
- ✅ Label issues for your addons
- ✅ Prioritize critical bugs
- ✅ Close resolved issues

---

## 🤖 Bot Commands for Maintainers

### /merge [major|minor|patch|nobump]

**Purpose**: Merge approved PR with optional version bump

**Requirements:**
- You must have `write` or `admin` permission
- PR must have 2+ approvals
- CI must pass

**Usage:**
```bash
/merge patch
```

**Behavior:**
- Merges PR (squash merge)
- Bumps module version (if specified)
- Deletes source branch
- Posts confirmation

### /rebase

**Purpose**: Request PR author to rebase

**Usage:**
```bash
/rebase
```

**Behavior:**
- Posts rebase instructions
- No automatic action (manual step)

### /migration <module>

**Purpose**: Track migration work for module

**Usage:**
```bash
/migration ipai_rate_policy
```

**Behavior:**
- Posts migration checklist
- Adds tracking metadata
- Links to migration issue

---

## 📊 PR Review Workflow

### 1. Notification Phase
- ✅ PR opened
- ✅ Bot mentions maintainers
- ✅ `needs review` label added (if CI passes)

### 2. Review Phase
- ✅ Maintainer reviews code
- ✅ Requests changes or approves
- ✅ Author makes revisions

### 3. Approval Phase
- ✅ 2+ approvals received
- ✅ `approved` label added
- ✅ CI passes

### 4. Merge Phase
- ✅ Wait 5 days (optional)
- ✅ `ready to merge` label added
- ✅ Maintainer uses `/merge` command
- ✅ Branch auto-deleted

---

## 🏷️ Label Management

### Automatic Labels

| Label | When Added | When Removed |
|-------|------------|--------------|
| `needs review` | CI passes, 0 approvals | Approvals received or WIP |
| `approved` | 2+ approvals | Approvals dropped below 2 |
| `ready to merge` | Approved + 5+ days | N/A (stays until merge) |

### Manual Labels

Maintainers can add:
- `priority:high` - Critical fixes
- `type:feature` - New functionality
- `type:bugfix` - Bug fixes
- `type:refactor` - Code refactoring
- `status:blocked` - Blocked by dependency

---

## 📈 Maintainer Metrics

### View Your PRs

```bash
# PRs mentioning you
gh pr list --search "mentions:your-username"

# PRs needing your review
gh pr list --label "needs review"
```

### Module Activity

Check `CHANGELOG.md` for module changes:
```bash
git log --oneline addons/ipai_rate_policy/
```

---

## 🎓 Training & Resources

### Odoo Development
- [Odoo Developer Documentation](https://www.odoo.com/documentation/19.0/developer.html)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)

### Git & GitHub
- [Git Workflow Guide](https://guides.github.com/introduction/flow/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

### InsightPulse Specific
- [MODULES.md](MODULES.md) - Module documentation
- [GITHUB_BOT.md](docs/GITHUB_BOT.md) - Bot automation guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Pre-deployment validation

---

## 🆕 Becoming a Maintainer

### Requirements
1. **Contributions**: Active contributions to the module
2. **Knowledge**: Deep understanding of module functionality
3. **Availability**: Responsive to PRs and issues
4. **Quality**: High-quality code and reviews

### Process
1. Discuss with project lead (@jgtolentino)
2. Add yourself to `__manifest__.py`:
   ```python
   'maintainers': ['existing-maintainer', 'your-username'],
   ```
3. Open PR with addition
4. Existing maintainer approves
5. Merge with `/merge nobump`

---

## 🔄 Stepping Down

If you can no longer maintain a module:

1. Open PR removing yourself from `maintainers`
2. Notify other maintainers
3. Suggest replacement (if available)
4. Document knowledge transfer

---

## 📞 Contact

Questions about maintainer duties?

- **Discussions**: [GitHub Discussions](https://github.com/jgtolentino/insightpulse-odoo/discussions)
- **Email**: support@insightpulse.ai
- **Project Lead**: @jgtolentino

---

## 📝 License

All modules are licensed under **LGPL-3.0** unless otherwise specified in the module manifest.

Maintainers must ensure:
- ✅ Code contributions comply with LGPL-3.0
- ✅ Dependencies are LGPL-3.0 compatible
- ✅ No proprietary code is included

---

**Last Updated**: 2025-10-30
**Active Maintainers**: 1 (jgtolentino)
**Modules Maintained**: 10 enterprise modules
