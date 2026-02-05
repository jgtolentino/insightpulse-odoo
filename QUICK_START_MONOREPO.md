# Quick Start: Supabase-first Monorepo

This guide helps you get started with the new Supabase-first monorepo structure.

## 🎯 What Changed?

The repository now follows a Supabase-first layout with clear separation:
- **`supabase/`** → Database & Edge Functions (canonical)
- **`runtime/`** → Execution environment (Odoo, local dev)
- **`tools/claude-plugin/`** → AI agents & automation

## 🚀 Quick Commands

### Validate Structure

```bash
# Basic check
bash scripts/repo_check.sh

# Comprehensive validation
bash scripts/validate_structure.sh
```

### Start Services

```bash
# Start Odoo runtime
bash scripts/odoo_up.sh

# Start Supabase (local)
bash scripts/supabase_up.sh

# Check status
cd runtime/odoo && docker compose ps
```

### Stop Services

```bash
# Stop Odoo
bash scripts/odoo_down.sh

# Stop Supabase
supabase stop
```

## 📁 Where Things Are

### Before → After

| What | Old Location | New Location |
|------|-------------|--------------|
| Database migrations | `supabase/migrations/` | ✅ Same (canonical) |
| Edge Functions | `supabase/functions/` | ✅ Same (canonical) |
| Odoo config | `docker-compose.yml` | `runtime/odoo/docker-compose.yml` |
| Claude agents | `agents/` | `tools/claude-plugin/agents/` |
| Skills library | `skills/` | `tools/claude-plugin/skills/` |
| Custom modules | `addons/` | ✅ Same |
| OCA modules | `oca/` | ✅ Same (or `vendor/oca/`) |

## 🔧 Development Workflow

### 1. Setup Environment

```bash
# Clone repo
git clone --recursive https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Validate structure
bash scripts/validate_structure.sh
```

### 2. Start Development

```bash
# Start all services
bash scripts/odoo_up.sh
bash scripts/supabase_up.sh

# Access services
# Odoo: http://localhost:8069
# Supabase Studio: http://localhost:54323
```

### 3. Make Changes

**Database Changes:**
```bash
# Create migration
supabase migration new your_migration_name

# Edit migration file in supabase/migrations/

# Apply migration
supabase db push
```

**Odoo Module Changes:**
```bash
# Edit files in addons/your_module/

# Restart Odoo to apply
cd runtime/odoo
docker compose restart odoo
```

**Edge Function Changes:**
```bash
# Create function
supabase functions new your_function_name

# Edit function in supabase/functions/your_function_name/index.ts

# Deploy function
supabase functions deploy your_function_name
```

## 🧪 Testing

### Run Validation

```bash
# Full validation suite
bash scripts/validate_structure.sh

# Output:
# ✓ 33 checks passed
# ⚠ 1 warning
# ✗ 0 failed
```

### Test Odoo Runtime

```bash
# Start Odoo
bash scripts/odoo_up.sh

# Check logs
cd runtime/odoo
docker compose logs -f odoo

# Access Odoo
curl http://localhost:8069

# Stop Odoo
bash scripts/odoo_down.sh
```

### Test Supabase

```bash
# Start Supabase
bash scripts/supabase_up.sh

# Check status
supabase status

# Output:
# API URL: http://localhost:54321
# DB URL: postgresql://postgres:postgres@localhost:54322/postgres
# Studio URL: http://localhost:54323
```

## 📚 Documentation

- **[Full Structure Guide](MONOREPO_STRUCTURE.md)** - Comprehensive documentation
- **[Runtime Guide](runtime/README.md)** - Odoo execution details
- **[Claude Plugin Guide](tools/claude-plugin/README.md)** - AI tooling docs
- **[Main README](README.md)** - Project overview

## 🐛 Troubleshooting

### Structure Validation Fails

```bash
# Check what's missing
bash scripts/validate_structure.sh

# Fix missing directories
mkdir -p runtime/odoo
mkdir -p tools/claude-plugin
```

### Docker Compose Issues

```bash
# Validate syntax
cd runtime/odoo
docker compose config

# Check logs
docker compose logs
```

### Supabase Not Starting

```bash
# Check if CLI is installed
supabase --version

# Install if missing
brew install supabase/tap/supabase  # macOS
npm install -g supabase             # npm
```

## 🎓 Common Tasks

### Add a New Edge Function

```bash
# Create function
supabase functions new process_expense

# Edit function
# File: supabase/functions/process_expense/index.ts

# Test locally
supabase functions serve process_expense

# Deploy
supabase functions deploy process_expense
```

### Add a New Odoo Module

```bash
# Create module structure
mkdir -p addons/ipai_new_module
cd addons/ipai_new_module

# Create __manifest__.py
cat > __manifest__.py <<EOF
{
    'name': 'New Module',
    'version': '19.0.1.0.0',
    'category': 'Custom',
    'depends': ['base'],
    'data': [],
    'installable': True,
}
EOF

# Restart Odoo
cd ../../runtime/odoo
docker compose restart odoo
```

### Update OCA Modules

```bash
# Current location (backward compatible)
cd oca/16.0
git pull origin 16.0

# Or future location
cd vendor/oca
git pull
```

### Run Claude Agent

```bash
# Agents now in tools/claude-plugin/
cd tools/claude-plugin

# Run agent (example)
python agents/generator.py
```

## ✅ CI/CD

The new CI workflow validates structure on every PR:

```yaml
# .github/workflows/ci.yml
name: ci
on:
  pull_request:
  push:
    branches: [ main ]
jobs:
  repo-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Repo structure check
        run: bash scripts/repo_check.sh
```

## 🔒 Security

### Environment Variables

Never commit secrets! Use `.env` files:

```bash
# .env (not committed)
ODOO_DB_PASSWORD=your_secure_password
SUPABASE_SERVICE_ROLE_KEY=your_key
```

### Config Files

Runtime configs use environment variables:

```conf
# runtime/odoo/odoo.conf
db_password = ${ODOO_DB_PASSWORD}  # ✅ Good
db_password = hardcoded_password   # ❌ Bad
```

## 💡 Best Practices

1. **Database changes** → Always use Supabase migrations
2. **Business logic** → Prefer Edge Functions over Odoo for new features
3. **Odoo modules** → Use for ERP-specific functionality only
4. **Claude tools** → Keep in `tools/claude-plugin/` for governance
5. **Documentation** → Update when structure changes

## 🆘 Getting Help

- **Structure issues**: See [MONOREPO_STRUCTURE.md](MONOREPO_STRUCTURE.md)
- **Deployment**: See [Deployment Guide](docs/deployment/digitalocean-production.md)
- **Odoo development**: See [OCA Guidelines](https://github.com/OCA/maintainer-tools)
- **Supabase docs**: https://supabase.com/docs

## 🎉 Next Steps

1. ✅ Validate your local setup
2. ✅ Start development services
3. ✅ Make your first change
4. ✅ Run validation before committing
5. ✅ Push to PR and check CI

Happy coding! 🚀
