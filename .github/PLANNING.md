# Development Planning & Workflow
**Last Updated:** 2025-11-17
**Maintainers:** InsightPulse AI Team
**Purpose:** Development workflow, sprint planning, and automation patterns

---

## 📋 Quick Reference

### Daily Development Commands

```bash
# Morning startup
./automate.sh start && ./automate.sh health

# Before committing
./scripts/validate-doc-freshness.sh  # Runs automatically via git hook

# Before pushing
./scripts/validate-all.sh            # Full validation

# End of day
./automate.sh backup
```

---

## 🔀 Git Workflow

### Branch Strategy (Git Flow)

```
main (production)
  │
  └─── develop (staging)
        │
        ├─── feature/finance-ssc-core
        ├─── feature/expense-management
        ├─── bugfix/invoice-validation
        └─── hotfix/security-patch
```

#### Branch Naming Convention

| Type | Format | Example | Merges To |
|------|--------|---------|-----------|
| Feature | `feature/<module-name>` | `feature/travel-request` | `develop` |
| Bugfix | `bugfix/<issue-description>` | `bugfix/amount-validation` | `develop` |
| Hotfix | `hotfix/<critical-fix>` | `hotfix/sql-injection` | `main` + `develop` |
| Release | `release/v<version>` | `release/v1.2.0` | `main` |
| Docs | `docs/<topic>` | `docs/api-reference` | `develop` |

### Commit Message Convention (Semantic Commits)

```bash
# Format
<type>(<scope>): <subject>

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation only
style:    Code style (formatting, semicolons)
refactor: Code change that neither fixes bug nor adds feature
perf:     Performance improvement
test:     Adding tests
chore:    Build process or auxiliary tool changes
ci:       CI/CD changes
revert:   Revert previous commit

# Examples
feat(expense): add multi-level approval workflow
fix(invoice): validate BIR form 2307 fields
docs(readme): update installation instructions
chore(deps): upgrade postgres to 15.6
ci(github): add security scanning workflow
```

---

## 📚 Documentation System

### Documentation Hierarchy

```
Layer 1: User-Facing
├── README.md              # Quick start, installation
├── ROADMAP.md             # Long-term vision
└── CHANGELOG.md           # Version history

Layer 2: Developer-Facing
├── .github/PLANNING.md    # This file
├── TASKS.md               # Sprint tasks
├── CONTRIBUTING.md        # Contribution guidelines
└── docs/                  # Technical documentation

Layer 3: AI Assistant Context
├── claude.md              # AI assistant instructions
└── claudedocs/            # Extracted documentation

Layer 4: Code-Level
└── odoo/addons/*/README.md     # Module documentation
```

### Auto-Generated Documentation

**These files are GENERATED - do not edit manually:**

```bash
# Generated markers
<!-- AUTO-GENERATED: Do not edit below this line -->
<!-- GENERATED: 2025-11-08 03:00:00 UTC -->
```

### Documentation Automation

#### Pre-Commit Hook (Validates)
```bash
# Check documentation freshness
./scripts/validate-doc-freshness.sh

# Update auto-generated sections
./scripts/update-auto-sections.sh
```

#### Daily CI Job (Refreshes)
```yaml
# .github/workflows/doc-automation.yml
on:
  schedule:
    - cron: '0 3 * * *'  # 3 AM UTC daily
```

---

## 📅 Sprint Planning

### Sprint Structure (2-Week Sprints)

#### Week 1: Build & Test
- **Mon-Tue:** Planning, architecture review
- **Wed-Thu:** Implementation, unit tests
- **Fri:** Integration tests, documentation

#### Week 2: Refine & Deploy
- **Mon-Tue:** Bug fixes, code review
- **Wed:** Security scan, performance testing
- **Thu:** Staging deployment, smoke tests
- **Fri:** Production deployment, retrospective

### Task Template

```markdown
## Task: [Module Name] - [Feature Description]

**Priority:** High/Medium/Low
**Sprint:** Sprint-XX
**Estimate:** X hours

### Requirements
- [ ] Requirement 1
- [ ] Requirement 2

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

### Testing Checklist
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] BIR compliance tests
- [ ] Multi-tenant isolation tests

### Documentation
- [ ] Module README.md
- [ ] Update CHANGELOG.md
```

---

## 🤖 Automation Patterns

### 1. Documentation Auto-Update

**Trigger:** Code changes in `odoo/addons/`

```bash
# Update architecture documentation
./scripts/update-auto-sections.sh

# Commit if changes detected
if [[ $(git status --porcelain docs/) ]]; then
  git add docs/
  git commit -m "docs: auto-update [skip ci]"
fi
```

### 2. Health Check Auto-Report

**Trigger:** Daily @ 3 AM UTC

```bash
./automate.sh health > health-report.txt

# If failures, create issue
if grep -q "FAIL" health-report.txt; then
  gh issue create \
    --title "🚨 Daily Health Check Failed" \
    --body "$(cat health-report.txt)" \
    --label "automated,urgent"
fi
```

### 3. Backup Automation

**Trigger:** Daily @ 1 AM UTC + Before deployments

```bash
./automate.sh backup

# Retention: 30 days
find backups/ -name "*.sql" -mtime +30 -delete
```

---

## 🚀 Release Process

### Version Numbering (Semantic Versioning)

```
v<MAJOR>.<MINOR>.<PATCH>

MAJOR: Breaking changes
MINOR: New features
PATCH: Bug fixes
```

### Release Checklist

#### Pre-Release
```bash
git checkout -b release/v1.2.0 develop
./scripts/bump-version.sh 1.2.0
./scripts/generate-changelog.sh v1.1.0..HEAD >> CHANGELOG.md
```

#### Testing Phase
```bash
make deploy-staging
./automate.sh test
./scripts/validate-bir-compliance.sh
./scripts/run-performance-tests.sh
```

#### Release Day
```bash
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags

gh release create v1.2.0 \
  --title "v1.2.0" \
  --notes-file CHANGELOG.md
```

---

## 🎯 Best Practices

### DO ✅

1. **Always create a branch** - Never commit to `main` or `develop`
2. **Write tests first** - TDD for new features
3. **Use semantic commits** - Automated changelog
4. **Update documentation** - As you code
5. **Run validation locally** - Before pushing
6. **Keep PRs small** - <500 lines changed

### DON'T ❌

1. **Never commit secrets** - Use environment variables
2. **Never skip tests** - No `--no-verify`
3. **Never push to main** - Always use PR workflow
4. **Never ignore security warnings**
5. **Never break BIR compliance**
6. **Never deploy on Friday** - Unless hotfix

---

## 📊 Metrics & Monitoring

### Development Metrics

**Code Quality:**
- Coverage: >80% (enforced)
- Complexity: <10 cyclomatic (enforced)
- Security: 0 critical vulnerabilities (enforced)

**Velocity:**
- Sprint velocity (story points/sprint)
- Cycle time (idea → production)
- Deployment frequency

---

## 🔗 Quick Links

**Development:**
- [README.md](../README.md) - Installation & usage
- [claude.md](../claude.md) - AI assistant context
- [TASKS.md](../TASKS.md) - Current sprint

**Automation:**
- [CI/CD Workflows](workflows/) - GitHub Actions
- [Scripts](../scripts/) - Automation scripts

**Monitoring:**
- [Grafana](http://localhost:3000) - Metrics dashboard
- [GitHub Actions](https://github.com/jgtolentino/insightpulse-odoo/actions) - CI/CD status

---

**Last Auto-Updated:** 2025-11-17
**Next Review:** 2025-11-15 (weekly)
**Maintained By:** CI/CD Automation + InsightPulse AI Team
