# InsightPulse Odoo - Quick Reference Card

## 🚀 One-Line Deployments

```bash
# Full deployment (everything)
make deploy-now

# Fast deployment (Odoo + DO App only)
make deploy-fast

# Database changes only
make deploy-db

# Documentation only
make deploy-docs
```

---

## 🇵🇭 Philippine Accounting Setup

```bash
# Auto-install PH localization
make setup-ph-localization

# Verify installation
make verify-ph-localization

# Or manual on droplet
ssh root@165.227.10.178
./scripts/setup-ph-localization.sh
```

**Manual steps after install:**
1. Login → Settings → Companies → Set Country: Philippines, Currency: PHP
2. Accounting → Taxes → Verify VAT 12%, Zero-rated, Exempt
3. Create test invoice → Verify accounting entries

---

## 📊 Monitoring & Logs

```bash
# Deployment status
make deployment-status

# Tail logs
make logs              # DO App logs
make odoo-logs         # Odoo droplet logs

# Health checks
make health-check

# All info
make info
```

---

## 🐳 Docker Commands

```bash
# Build image
make deploy-odoo-image

# View images
docker images | grep insightpulse-odoo

# Clean up
make clean-docker
```

---

## 🔄 Rollback

```bash
# Quick rollback
make rollback

# Manual rollback
doctl apps deployments list b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9
doctl apps deployments rollback b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9 <DEPLOYMENT_ID>
```

---

## 🔐 Odoo Access

**Database Manager:**
- URL: https://erp.insightpulseai.net/web/database/manager
- Master Password: `2ca2a768b7c9016f52364921bb78ab2a359da05a23dd0bf1`

**Odoo Login:**
- URL: https://erp.insightpulseai.net
- Database: `insightpulse_prod`
- Admin: Your admin email/password

---

## 🗄️ Supabase

```bash
# Link project
supabase link --project-ref spdtwktxdalcfigzeqrz

# Push migrations
supabase db push

# Deploy functions
supabase functions deploy search answer ingest

# Check status
supabase status
```

---

## ☁️ DigitalOcean

```bash
# App ID
export DO_APP_ID=b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9

# Update app
doctl apps update $DO_APP_ID --spec infra/do/ade-ocr-service.yaml

# Create deployment
doctl apps create-deployment $DO_APP_ID

# View logs
doctl apps logs $DO_APP_ID --follow
```

---

## 🧪 Testing

```bash
# Run tests
make test

# Health checks
make health-check

# Verify PH setup
make verify-ph-localization
```

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `Makefile` | All commands (`make help`) |
| `DEPLOYMENT_GUIDE.md` | Complete deployment guide |
| `ODOO_SAAS_MIGRATION_PLAN.md` | SaaS → Self-hosted migration |
| `SUPERSET_DASHBOARD_EXAMPLES.md` | 40+ dashboard SQL queries |
| `DEPLOYMENT_STATUS_FINAL.md` | Current infrastructure status |

---

## 🔑 Required Secrets

```bash
# GitHub Container Registry
export CR_PAT="ghp_..."

# Supabase
export SUPABASE_ACCESS_TOKEN="sbp_..."
export SUPABASE_ANON_KEY="eyJ..."

# DigitalOcean
export DIGITALOCEAN_ACCESS_TOKEN="dop_..."
```

**Persist in ~/.zshrc:**
```bash
echo 'export CR_PAT="ghp_..."' >> ~/.zshrc
echo 'export SUPABASE_ACCESS_TOKEN="sbp_..."' >> ~/.zshrc
echo 'export DIGITALOCEAN_ACCESS_TOKEN="dop_..."' >> ~/.zshrc
source ~/.zshrc
```

---

## 🆘 Emergency Contacts

- **Odoo Issues**: Check `make odoo-logs`
- **DO App Issues**: Check `make logs`
- **Database Issues**: Check `supabase status`
- **Deployment Fails**: Run `make rollback`

**Support:**
- Email: jgtolentino_rn@yahoo.com
- GitHub: https://github.com/jgtolentino/insightpulse-odoo/issues

---

## 🎯 Common Workflows

### Deploy New Feature
```bash
git checkout -b feature/my-feature
# ... make changes ...
git add .
git commit -m "feat: my feature"
git push origin feature/my-feature
gh pr create
# After merge to main → auto-deploys
```

### Update Dependencies
```bash
pip install new-package
pip freeze > requirements.txt
make deploy-fast
```

### Database Migration
```bash
# Create migration in supabase/migrations/
supabase db push
make deploy-db
```

### Update Superset Dashboard
```bash
# Edit docs/SUPERSET_DASHBOARD_EXAMPLES.md
# Copy SQL to Superset UI
# Save dashboard
```

---

## 💡 Tips & Tricks

**Speed up builds:**
```bash
export DOCKER_BUILDKIT=1
```

**Parallel operations:**
```bash
make deploy-supabase & make deploy-odoo-image & wait
```

**Watch deployment:**
```bash
watch -n 5 'make deployment-status'
```

**Quick health:**
```bash
curl -I https://erp.insightpulseai.net/web/login
```

---

**Print this:** `cat QUICK_REFERENCE.md` or `make help`
