## ✅ Assistant Readiness
- [ ] `.cursorrules` still enforces **Odoo 18 CE** (no Enterprise / 19)
- [ ] `CLAUDE` commands unaffected or updated
- [ ] `TASKS.md` updated (no open **CRITICAL**)
- [ ] `PLANNING.md` still reflects this change's sprint
- [ ] `ARCHITECTURE.md` updated if interfaces changed

## 🚦 Deployment
- [ ] passes `assistant-guard`
- [ ] passes `deploy-gates` (schema/content/edge)
- [ ] safe to tag release

## 📝 Description

<!-- Briefly describe what this PR changes and why -->

## 🎯 Related

- Closes #
- Related to #
- Epic: <!-- Epic 1-10 from PRD -->

## 🧪 Testing

<!-- How was this tested? -->
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Test coverage: ____%

## 📸 Screenshots (if applicable)

<!-- Add screenshots or GIFs for UI changes -->

## 🔍 Code Quality

- [ ] Linted (black, flake8, pylint)
- [ ] No hardcoded secrets
- [ ] Docstrings added
- [ ] Type hints added
- [ ] CHANGELOG.md updated

## 🔒 Security

- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] BIR compliance maintained (immutable accounting)
- [ ] RLS rules validated (multi-company isolation)

## 📚 Documentation

- [ ] README updated (if public API changed)
- [ ] Module README.md added/updated
- [ ] OpenAPI spec updated (if controller added)
- [ ] Architecture diagram updated (if structure changed)

## 🚀 Deployment Notes

<!-- Any special deployment steps? -->
- [ ] Database migration required
- [ ] OCA module update required
- [ ] Environment variable changes
- [ ] Manual post-deploy steps: <!-- list here -->

## ✅ Reviewer Checklist

For Reviewers:
- [ ] Code follows Odoo 18 CE standards
- [ ] Tests are comprehensive
- [ ] No performance regressions
- [ ] Security best practices followed
- [ ] Documentation is clear
- [ ] Ready for production deployment
