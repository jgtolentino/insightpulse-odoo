# Security Policy

This repository is part of the InsightPulseAI platform and powers our Odoo 18 CE stack.

We use:

- GitHub Advanced Security (code scanning + secret scanning)
- Trivy-based dependency scanning via GitHub Actions
- CI pipelines that validate documentation and OCA compliance

## Reporting a Vulnerability

If you believe you have found a security issue in this repository:

1. **Do not** open a public issue.
2. Instead, use the private GitHub security advisories flow:
   https://github.com/jgtolentino/insightpulse-odoo/security/advisories/new

We will review, triage, and respond as quickly as possible.

## Scope

This policy covers:

- All code in this repository
- GitHub Actions workflows defined under `.github/workflows/`
- Documentation or examples that could impact production deployments
- Visual Compliance Agent validators and automation

## Security Standards

### Odoo Module Security

All custom Odoo modules must:

- Follow OCA security guidelines
- Implement proper access control (ir.model.access.csv and record rules)
- Sanitize user input to prevent SQL injection and XSS
- Use LGPL-3 license to ensure open source compliance

### CI/CD Security

GitHub Actions workflows:

- Use pinned versions for actions (e.g., `@v4` not `@latest`)
- Limit permissions to minimum required scope
- Never expose secrets in logs
- Use environment protection rules for production deployments

### Dependency Management

We scan dependencies for vulnerabilities:

- Python packages via `pip-audit` and GitHub Dependabot
- Docker images via Trivy
- GitHub Actions via Dependabot version updates

## Visual Compliance Agent

The Visual Compliance Agent includes security-focused validators:

- **Manifest validation** - Ensures LGPL-3 license compliance
- **Directory structure** - Prevents scattered code that could hide vulnerabilities
- **Module naming** - Enforces predictable module identification
- **Documentation** - Requires security documentation in README.rst

Run locally:
```bash
python agents/visual-compliance/src/visual_agent.py
```

## Contact

For security questions not covered by this policy:
- Email: security@insightpulseai.net
- GitHub: @jgtolentino
