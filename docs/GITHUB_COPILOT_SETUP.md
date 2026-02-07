# GitHub Copilot Setup Guide

This guide explains how to enable and configure GitHub Copilot for the InsightPulse Odoo organization repository.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Organization-Level Setup](#organization-level-setup)
- [Repository-Level Configuration](#repository-level-configuration)
- [User Setup](#user-setup)
- [Copilot Features](#copilot-features)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

GitHub Copilot is an AI-powered code completion tool that helps developers write code faster and with fewer errors. For organization repositories, Copilot can be enabled at both the organization and repository levels.

### Benefits for InsightPulse Odoo

- **Faster Development**: AI-assisted code completion for Python, JavaScript, XML, and other languages
- **Odoo Module Development**: Context-aware suggestions for Odoo models, views, and controllers
- **Code Quality**: Consistent coding patterns and best practices
- **Documentation**: Auto-generate docstrings and comments
- **Test Writing**: Assistance with creating unit tests and test cases

---

## Prerequisites

### For Organization Owners

- **GitHub Organization**: Organization must be on GitHub Team or GitHub Enterprise Cloud
- **Billing Setup**: Active payment method configured
- **Admin Access**: Organization owner or admin permissions

### For Developers

- **GitHub Account**: Personal GitHub account with organization access
- **IDE Setup**: VS Code, JetBrains, or Neovim with Copilot extension
- **Repository Access**: Read or write access to organization repositories

### Cost Considerations

- **GitHub Copilot for Business**: $19/user/month (billed annually) or $39/user/month (billed monthly)
- **GitHub Copilot Individual**: $10/month or $100/year (per user, not organization-wide)
- **Free for Students/Teachers**: Available through GitHub Education

**Note**: Verify current pricing at https://github.com/features/copilot/plans as prices may change.

---

## Organization-Level Setup

### Step 1: Enable Copilot for Organization

1. **Navigate to Organization Settings**
   - Go to `https://github.com/orgs/YOUR_ORG/settings`
   - Or click organization avatar → Settings

2. **Access Copilot Settings**
   - In left sidebar, click **"Copilot"** under "Code, planning, and automation"
   - Or go directly to: `https://github.com/organizations/YOUR_ORG/settings/copilot`

3. **Enable Copilot for Organization**
   - Click **"Enable GitHub Copilot"**
   - Review and accept the terms
   - Choose billing frequency (monthly or annual)

4. **Configure Access Policies**
   
   Choose one of the following policies:

   - **Allow for all members**: Everyone in organization gets access
   - **Allow for specific members/teams**: Grant access selectively
   - **Disabled**: No access (default)

   **Recommended for InsightPulse Odoo**: Allow for specific teams (e.g., `developers`, `contributors`)

### Step 2: Configure Organization Policies

1. **Public Code Policy**
   - Navigate to **"Policies and features"** tab
   - Configure **"Suggestions matching public code"**:
     - ✅ **Allow** - Show suggestions that match public code (with attribution)
     - ❌ **Block** - Filter out suggestions matching public code
   
   **Recommended**: Allow (helps identify potential licensing issues)

2. **Content Exclusions** (Optional)
   - Configure files/paths to exclude from Copilot analysis
   - Add sensitive directories like:
     - `.env*` files
     - `secrets/`
     - `config/production/`

### Step 3: Assign User Seats

1. **Add Users/Teams**
   - Go to **"Access management"** tab
   - Click **"Add people"** or **"Add teams"**
   - Search and select users/teams
   - Click **"Add to Copilot"**

2. **Manage Seats**
   - View current seat usage
   - Remove users as needed
   - Track billing per seat

---

## Repository-Level Configuration

### Enable Copilot for This Repository

1. **Repository Settings**
   - Navigate to repository: `https://github.com/jgtolentino/insightpulse-odoo`
   - Click **"Settings"** tab
   - Click **"Code & automation"** → **"Copilot"** (if available)

2. **Repository Policies**
   
   Organization admins can configure repository-specific policies:
   
   - ✅ **Allow Copilot**: Enable for this repository
   - ❌ **Disable Copilot**: Block for this repository
   - ⚙️ **Use organization default**: Inherit organization settings (recommended)

### Configure `.copilotignore` (Optional)

Create a `.copilotignore` file in repository root to exclude files:

```gitignore
# Exclude sensitive configuration
.env*
*.key
*.pem
secrets/

# Exclude generated files
node_modules/
*.pyc
__pycache__/
.coverage
htmlcov/

# Exclude vendor dependencies
vendor/
third_party/

# Exclude large data files
datasets/
backups/
*.sql
*.dump
```

### IDE-Specific Configuration

Configure Copilot settings in your IDE for optimal Odoo development:

**VS Code** (`settings.json`):
```json
{
  "github.copilot.enable": {
    "*": true,
    "python": true,
    "xml": true,
    "yaml": true
  },
  "github.copilot.editor.enableAutoCompletions": true
}
```

**PyCharm/IntelliJ** (Settings → Tools → GitHub Copilot):
- Enable inline completions
- Enable for Python, XML, YAML files
- Configure keybindings as preferred

**Note**: GitHub Copilot configuration is managed at the IDE level, not via repository files.

---

## User Setup

### For VS Code Users

1. **Install Extension**
   ```bash
   # Open VS Code
   # Press Ctrl+P (Cmd+P on Mac)
   # Type: ext install GitHub.copilot
   ```

2. **Sign In**
   - Click GitHub Copilot icon in status bar
   - Click "Sign in to GitHub"
   - Authorize VS Code in browser

3. **Verify Access**
   - Open any Python file in repository
   - Start typing code
   - Copilot suggestions appear in gray text
   - Press `Tab` to accept, `Esc` to dismiss

4. **Configure Settings**
   - Open Settings (Ctrl+,)
   - Search "Copilot"
   - Configure preferences:
     - ✅ Enable/disable inline suggestions
     - ✅ Enable/disable Copilot for specific languages
     - ✅ Configure keybindings

### For JetBrains IDEs (PyCharm, IntelliJ)

1. **Install Plugin**
   - Open IDE
   - Go to Settings → Plugins
   - Search "GitHub Copilot"
   - Click Install and restart

2. **Authenticate**
   - Tools → GitHub Copilot → Login to GitHub
   - Authorize in browser

3. **Configure**
   - Settings → Tools → GitHub Copilot
   - Enable/disable features

### For Neovim Users

1. **Install Plugin**
   ```vim
   " Using vim-plug
   Plug 'github/copilot.vim'
   
   " Or using packer.nvim
   use 'github/copilot.vim'
   ```

2. **Setup**
   ```vim
   :Copilot setup
   ```

---

## Copilot Features

### Code Completion

- **Inline Suggestions**: Gray text appears as you type
- **Multi-line Completions**: Full function/method suggestions
- **Context-Aware**: Uses surrounding code and comments

### Copilot Chat (Business/Enterprise)

- **Ask Questions**: "How do I create an Odoo model?"
- **Explain Code**: "What does this function do?"
- **Generate Tests**: "Create unit tests for this class"
- **Fix Issues**: "Why is this code failing?"

### Copilot for Pull Requests

- **PR Summaries**: Auto-generate PR descriptions
- **Code Reviews**: Suggestions during review
- **Commit Messages**: Generate conventional commit messages

---

## Best Practices

### For InsightPulse Odoo Development

1. **Use Descriptive Comments**
   ```python
   # Create an Odoo model for expense reports with approval workflow
   class ExpenseReport(models.Model):
       # Copilot will suggest relevant fields and methods
   ```

2. **Leverage Copilot for Boilerplate**
   - Odoo model declarations
   - XML view definitions
   - Test case scaffolding
   - API endpoint handlers

3. **Review All Suggestions**
   - ⚠️ Copilot suggestions may not follow Odoo best practices
   - Always review for:
     - OCA compliance
     - Security vulnerabilities
     - Performance implications
     - BIR regulation adherence

4. **Use Copilot with Existing Tools**
   - Combine with `pre-commit` hooks
   - Run linters (`pylint`, `flake8`)
   - Execute test suite
   - Use CodeQL for security scanning

### Security Considerations

1. **Never Commit Secrets**
   - Copilot may suggest API keys from training data
   - Always use environment variables
   - Review suggestions for hardcoded credentials

2. **Validate Public Code Matches**
   - When Copilot shows (citation), review license
   - Ensure compatibility with LGPL-3.0
   - Document sources in comments

3. **Sensitive Repositories**
   - Use `.copilotignore` for sensitive files
   - Configure content exclusions at org level
   - Disable for specific security-critical repos

---

## Troubleshooting

### Copilot Not Working

**Problem**: No suggestions appear

**Solutions**:
1. Check Copilot status icon (bottom-right in VS Code)
2. Verify GitHub authentication: `GitHub Copilot: Sign in`
3. Check organization access: `GitHub Copilot: View Status`
4. Ensure repository is not in `.copilotignore`
5. Restart IDE/editor

### Access Denied

**Problem**: "You don't have access to GitHub Copilot"

**Solutions**:
1. Verify organization membership
2. Contact organization admin to assign seat
3. Check billing status (for organization)
4. Wait up to 10 minutes for seat assignment to propagate

### Poor Suggestions

**Problem**: Suggestions are not relevant to Odoo development

**Solutions**:
1. Add more context in comments
2. Use descriptive variable/function names
3. Keep related code in same file
4. Add type hints for Python code
5. Reference Odoo documentation in comments

### Performance Issues

**Problem**: IDE slows down with Copilot enabled

**Solutions**:
1. Increase IDE memory allocation
2. Disable Copilot for large files (>10K lines)
3. Exclude generated files in `.copilotignore`
4. Update to latest Copilot extension

### License Concerns

**Problem**: Suggestion matches public code

**Solutions**:
1. Review the citation provided
2. Check license compatibility
3. Rewrite code if incompatible
4. Enable "Block suggestions matching public code" at org level

---

## Additional Resources

### Official Documentation

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Copilot for Business](https://docs.github.com/en/copilot/copilot-business)
- [Managing Copilot in Organizations](https://docs.github.com/en/copilot/managing-copilot-business)

### InsightPulse Odoo Resources

- [Contributing Guide](../CONTRIBUTING.md)
- [Development Setup](../README.md#quick-start)
- [Code Quality Standards](../CONTRIBUTING.md#code-quality-standards)
- [OCA Compliance](../OCA_COMPLIANCE_REPORT.md)

### Community Support

- **GitHub Copilot**: https://github.com/github-copilot
- **VS Code Copilot**: https://github.com/microsoft/vscode-copilot-release
- **InsightPulse Discussions**: https://github.com/jgtolentino/insightpulse-odoo/discussions

---

## Questions?

If you need help enabling Copilot for this repository:

1. **Organization Admins**: Contact the repository owner (@jgtolentino)
2. **Developers**: Open an issue with label `question`
3. **GitHub Support**: https://support.github.com (for billing/access issues)

---

**Last Updated**: 2026-02-07  
**Maintained By**: InsightPulse Odoo Team
