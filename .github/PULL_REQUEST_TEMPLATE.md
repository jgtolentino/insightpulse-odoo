# Pull Request

## Description

<!-- Brief description of changes -->

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Infrastructure/DevOps change
- [ ] Dependency update

## Related Issues

<!-- Link to related issues, e.g., "Closes #123" or "Relates to #456" -->

---

## 🚦 Deployment Clearance (for production PRs)

### A. CI / Automation

- [ ] All GitHub Actions green on latest commit
- [ ] `deploy-gates` workflow passed
- [ ] No merge conflicts with main
- [ ] Pre-commit hooks passed locally

**Local verification:**
```bash
make pr-clear
```

### B. Content & Schema

- [ ] No unintended schema changes
- [ ] SQL files validated (if applicable)
- [ ] OpenAPI specs valid (if applicable)
- [ ] No TODO markers in production code

### C. Testing

- [ ] New tests added for new functionality
- [ ] Existing tests pass
- [ ] Manual testing completed

**Test commands:**
```bash
pytest tests/ -v
make test
```

### D. Deployment Wiring

- [ ] Required environment variables documented
- [ ] Secrets configured (or documented in checklist)
- [ ] Infrastructure changes documented
- [ ] Migration scripts provided (if applicable)

### E. Documentation

- [ ] README updated (if needed)
- [ ] CHANGELOG updated
- [ ] API documentation updated (if applicable)
- [ ] Deployment notes added

---

## 📋 Deployment Notes

<!-- If this PR requires special deployment steps, document them here -->

### Pre-Deployment

<!-- Commands to run before deploying -->

```bash
# Example:
# psql "$POSTGRES_URL" -f migrations/001_add_table.sql
```

### Deployment

<!-- Deployment commands -->

```bash
# Example:
# make deploy-service
```

### Post-Deployment

<!-- Verification commands -->

```bash
# Example:
# curl https://api.example.com/health
```

### Rollback Plan

<!-- How to rollback if deployment fails -->

---

## 🔍 Review Checklist (for reviewers)

- [ ] Code follows project style guidelines
- [ ] Changes are well-documented
- [ ] No sensitive information exposed
- [ ] Security best practices followed
- [ ] Performance impact considered
- [ ] Backward compatibility maintained (or breaking changes documented)

---

## 📸 Screenshots / Demos (if applicable)

<!-- Add screenshots or demo links for UI changes -->

---

## 🏷️ Labels

<!-- Add relevant labels: bug, enhancement, documentation, infrastructure, etc. -->

---

## 📚 Additional Context

<!-- Any other information that reviewers should know -->

---

**Note:** For deployment-critical PRs (infrastructure, database changes, new services), ensure you've reviewed:
- `PR_DEPLOYMENT_CHECKLIST.md` - Comprehensive deployment guide
- `BRANCH_PROTECTION_SETUP.md` - Required status checks
- `POST_MERGE_DEPLOYMENT.md` - Post-merge deployment steps
