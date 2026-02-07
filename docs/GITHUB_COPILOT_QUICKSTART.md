# GitHub Copilot Quick Start

Quick reference for enabling GitHub Copilot on the InsightPulse Odoo repository.

📚 **Full Documentation**: [GITHUB_COPILOT_SETUP.md](GITHUB_COPILOT_SETUP.md)

---

## For Organization Admins

### Enable Copilot (One-Time Setup)

1. Go to: `https://github.com/organizations/YOUR_ORG/settings/copilot`
2. Click **"Enable GitHub Copilot"**
3. Choose access policy:
   - ✅ **Recommended**: Allow for specific teams (e.g., `developers`)
   - Or allow for all members
4. Configure policies:
   - ✅ **Allow** suggestions matching public code (with attribution)
   - Add content exclusions for sensitive paths
5. Assign user seats:
   - Go to "Access management" tab
   - Add users or teams
   - Users will receive access within 10 minutes

**Cost**: $19/user/month (annual) or $39/user/month (monthly)

---

## For Developers

### Setup (5 Minutes)

#### VS Code
```bash
# Install extension
# Press Ctrl+P (Cmd+P on Mac)
ext install GitHub.copilot

# Sign in to GitHub
# Click Copilot icon in status bar → "Sign in to GitHub"
```

#### PyCharm / IntelliJ
```
1. Settings → Plugins → Search "GitHub Copilot" → Install
2. Tools → GitHub Copilot → Login to GitHub
```

#### Neovim
```vim
" Add to init.vim
Plug 'github/copilot.vim'

" Then run
:Copilot setup
```

### Verify It's Working

1. Open any Python file in the repository
2. Start typing code
3. Gray text suggestions should appear
4. Press `Tab` to accept, `Esc` to dismiss

---

## Best Practices for Odoo Development

### ✅ DO

```python
# Use descriptive comments for better suggestions
# Create an Odoo expense report model with approval workflow
class ExpenseReport(models.Model):
    _name = 'expense.report'
    # Copilot will suggest relevant fields
```

- Use Copilot for boilerplate (models, views, tests)
- Review all suggestions before accepting
- Run linters and tests after using Copilot
- Check license compatibility for cited code

### ❌ DON'T

- Don't commit Copilot-suggested API keys or secrets
- Don't blindly accept suggestions without review
- Don't skip OCA compliance checks
- Don't ignore security scanning results

---

## Security

### What's Excluded (`.copilotignore`)

Already configured to exclude:
- `.env*` files and secrets
- Credentials and keys (`.pem`, `.key`)
- Large datasets and backups
- Build artifacts (`node_modules/`, `__pycache__/`)
- Vendor dependencies

### Review Suggestions For

- 🔒 Hardcoded credentials
- 📜 License compatibility (we use LGPL-3.0)
- 🛡️ Security vulnerabilities
- ✅ OCA compliance
- 🇵🇭 BIR regulation adherence

---

## Troubleshooting

### No Suggestions Appearing

1. Check Copilot icon (bottom-right in VS Code)
2. Sign in: `GitHub Copilot: Sign in`
3. Check access: `GitHub Copilot: View Status`
4. Restart IDE

### Access Denied

1. Verify org membership
2. Contact admin to assign seat
3. Wait 10 minutes for propagation

### Poor Suggestions

1. Add more context in comments
2. Use descriptive names
3. Add type hints
4. Reference Odoo docs in comments

---

## Quick Links

- 📖 [Full Setup Guide](GITHUB_COPILOT_SETUP.md)
- 🔧 [Contributing Guide](../CONTRIBUTING.md)
- 🏠 [Main README](../README.md)
- 💬 [GitHub Copilot Docs](https://docs.github.com/en/copilot)

---

**Need Help?**
- Open an issue with label `question`
- Contact repo owner: @jgtolentino
- GitHub Support: https://support.github.com
