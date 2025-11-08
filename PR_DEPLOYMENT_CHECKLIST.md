# 🚦 Deployment Clearance Checklist - PR #326

## Executive Summary
This PR adds the complete **InsightPulse T&E MVP Bundle** - an end-to-end deployable stack with Odoo modules, OCR service, Auth Hub, Superset dashboards, warehouse views, and Skillsmith error mining. Before merging, clear these four deployment lanes:

1. **CI Status** - All automation passing
2. **Content Drift** - No Section 19 or DBML issues
3. **Data/Migrations** - Schema changes handled properly
4. **Deployment Wiring** - Env vars and secrets configured

---

## ✅ A. CI / Automation

- [ ] All GitHub Actions green on latest commit (no skipped required jobs)
- [ ] `deploy-gates.yml` workflow passed
- [ ] `tee-mvp-ci.yml` workflow passed (OpenAPI + blocking evals)
- [ ] No merge conflicts remaining
- [ ] Pre-commit hooks passed locally

**Commands to verify:**
```bash
# Run all clearance checks locally
make pr:clear

# Check specific gates
make pr:ci
```

---

## ✅ B. Content & Schema

- [ ] No DBML schema changes in this PR (T&E MVP uses existing Odoo schema)
- [ ] All SQL files in `warehouse/` validated
- [ ] OpenAPI spec (`openapi/expense-intake.json`) valid
- [ ] No orphan references or TODO markers

**Commands to verify:**
```bash
# Validate warehouse SQL
psql "$POSTGRES_URL" --dry-run -f warehouse/views.sql
psql "$POSTGRES_URL" --dry-run -f warehouse/mv_refresh.sql

# Validate Skillsmith SQL
psql "$POSTGRES_URL" --dry-run -f skillsmith/sql/skillsmith.sql
```

---

## ✅ C. Data / Migrations

- [ ] **No Alembic migration required** - This PR adds new services and modules without modifying core Odoo tables
- [ ] Warehouse views are idempotent (CREATE VIEW IF NOT EXISTS)
- [ ] Materialized views have refresh strategy documented
- [ ] Skillsmith functions use CREATE OR REPLACE
- [ ] Rollback plan: Simply drop new views/functions if needed

**Rollback commands (if needed):**
```sql
-- Rollback warehouse views
DROP VIEW IF EXISTS public.vw_expense_fact;
DROP MATERIALIZED VIEW IF EXISTS public.mv_expense_7d;

-- Rollback Skillsmith schema
DROP VIEW IF EXISTS public.error_candidates;
DROP MATERIALIZED VIEW IF EXISTS public.error_signatures;
DROP FUNCTION IF EXISTS public.normalize_error_message(text);
DROP FUNCTION IF EXISTS public.error_fingerprint(text, text, text);
```

---

## ✅ D. Odoo Models & Runtime

- [ ] New Odoo modules defined in `odoo/modules/`:
  - `ip_expense_ocr` - OCR intake controller
  - `ip_expense_policy` - Policy management
  - `ip_expense_match` - Expense matching
  - `ip_expense_audit` - Audit trail
- [ ] All modules have valid `__manifest__.py`
- [ ] Dependencies declared correctly (hr_expense, mail, account)
- [ ] No circular dependencies
- [ ] Test modules load: `odoo-bin -d test_db -i ip_expense_ocr --test-enable --stop-after-init`

**Commands to verify:**
```bash
# On Odoo droplet
sudo odoo -c /etc/odoo/odoo.conf -d odoo_prod -i ip_expense_ocr,ip_expense_policy,ip_expense_match,ip_expense_audit --stop-after-init --log-level=test
```

---

## ✅ E. Deployment Wiring

### Required GitHub Secrets/Variables

**GitHub Actions → Variables:**
- [ ] `ODOO_HOST` = `erp.insightpulseai.net`
- [ ] `OCR_HOST` = `ocr.insightpulseai.net`

**GitHub Actions → Secrets:**
- [ ] `SUPABASE_DB_HOST`
- [ ] `SUPABASE_DB_PORT` (default: 5432)
- [ ] `SUPABASE_DB_NAME` (default: postgres)
- [ ] `SUPABASE_DB_USER`
- [ ] `SUPABASE_DB_PASSWORD`

**Commands to verify:**
```bash
# Check secrets are set
make pr:secrets

# Test warehouse connection
psql "postgresql://$SUPABASE_DB_USER:$SUPABASE_DB_PASSWORD@$SUPABASE_DB_HOST:$SUPABASE_DB_PORT/$SUPABASE_DB_NAME?sslmode=require" -c "SELECT version();"
```

### Infrastructure Endpoints

- [ ] Nginx config for `erp.insightpulseai.net` deployed
- [ ] Nginx config for `ocr.insightpulseai.net` deployed
- [ ] Nginx config for `insightpulseai.net` (Auth Hub) deployed
- [ ] SSL certificates valid for all domains
- [ ] Health endpoints return 200:
  - `https://ocr.insightpulseai.net/health`
  - `https://erp.insightpulseai.net/web/health`

**Commands to deploy:**
```bash
# Copy Nginx configs
sudo cp infra/nginx/erp.insightpulseai.net.conf /etc/nginx/sites-available/
sudo cp infra/nginx/ocr.insightpulseai.net.conf /etc/nginx/sites-available/
sudo cp infra/nginx/insightpulseai.net.conf /etc/nginx/sites-available/

# Enable sites
sudo ln -s /etc/nginx/sites-available/erp.insightpulseai.net.conf /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/ocr.insightpulseai.net.conf /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/insightpulseai.net.conf /etc/nginx/sites-enabled/

# Test and reload
sudo nginx -t && sudo systemctl reload nginx
```

---

## ✅ F. Release Hygiene

- [ ] PR title semantic: `feat: Add InsightPulse T&E MVP Bundle`
- [ ] Labels set: `enhancement`, `tee-mvp`, `production-ready`
- [ ] CHANGELOG entry added (or will be added post-merge)
- [ ] Documentation updated:
  - `TEE_MVP_README.md` included
  - Deployment steps clear
  - Makefile targets documented

---

## 🚀 G. Deployment Sequence

### 1. Pre-Deployment (Before Merge)
```bash
# On local machine
make pr:clear
pytest tests/test_ocr_endpoints.py tests/test_warehouse_views.py
```

### 2. Database Setup (After Merge)
```bash
# Apply warehouse views
psql "$POSTGRES_URL" -f warehouse/views.sql
psql "$POSTGRES_URL" -f warehouse/mv_refresh.sql

# Apply Skillsmith schema
psql "$POSTGRES_URL" -f skillsmith/sql/skillsmith.sql

# Schedule MV refresh (pg_cron or cron)
psql "$POSTGRES_URL" -c "
  SELECT cron.schedule(
    'refresh-expense-mv',
    '0 * * * *',
    \$\$REFRESH MATERIALIZED VIEW public.mv_expense_7d\$\$
  );
"
```

### 3. OCR Service (SGP1 Droplet)
```bash
# Build and deploy
cd /opt/insightpulse-odoo
git pull origin main
make tee-ocr-build
make tee-ocr-run

# Verify
curl https://ocr.insightpulseai.net/health
```

### 4. Auth Hub (Optional - DO App Platform)
```bash
# Deploy via DO dashboard or CLI
cd authhub
doctl apps create --spec runtime.yaml
```

### 5. Odoo Modules (ERP Droplet)
```bash
# Copy modules
sudo cp -r odoo/modules/* /mnt/extra-addons/

# Install
make tee-odoo-upgrade

# Verify
curl https://erp.insightpulseai.net/web/database/selector
```

### 6. Superset Dashboards (Optional)
```bash
cd superset
./superset_bootstrap.sh
docker compose up -d
```

### 7. Post-Deployment Verification
```bash
# Run health checks
make tee-health

# Test end-to-end flow
curl -X POST https://ocr.insightpulseai.net/classify/expense \
  -H "Content-Type: application/json" \
  -d '{"text":"Restaurant meal $45.20"}'
```

---

## ✅ H. Final Gate

- [ ] "Dry-run" deploy on staging or preview OK
- [ ] Sign-off by: **Owner + Ops** (required reviewers)
- [ ] Post-merge monitoring plan documented
- [ ] Rollback procedure tested and documented above

---

## 📊 Quick Verification Commands

```bash
# Run all checks
make pr:clear

# Individual checks
make pr:ci          # CI validation
make pr:dbml        # Schema compilation
make pr:schema      # TODO marker check
make pr:secrets     # Secrets documentation
make tee-health     # Service health

# Test suite
pytest tests/test_ocr_endpoints.py -v
pytest tests/test_warehouse_views.py -v
pytest odoo/tests/test_intake_contract.py -v
pytest odoo/tests/test_qweb_oauth_block.py -v
```

---

## 🔗 Related Documentation

- Main README: `TEE_MVP_README.md`
- Makefile targets: `make help | grep tee-`
- CI workflows: `.github/workflows/tee-mvp-ci.yml`
- Infrastructure: `infra/nginx/*.conf`

---

## ✅ Approval Required

**Reviewers:** @jgtolentino (Owner), @ops-team (Ops)

**Merge Strategy:** Squash and merge (preserving commit history in PR)

**Post-Merge:** Create release tag `v1.0.0-tee-mvp` and deploy to production

---

**Last Updated:** 2025-11-07
**PR:** #326
**Branch:** `claude/insightpulse-tee-mvp-bundle-011CUtujai9jYsuxwf9rBcBT`
