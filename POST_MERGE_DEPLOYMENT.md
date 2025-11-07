# Post-Merge Deployment Runbook - PR #326

**T&E MVP Bundle Deployment Sequence**

---

## 📋 Pre-Deployment Checklist

Before running deployment commands, verify:

- ✅ PR #326 merged to `main`
- ✅ All CI workflows green
- ✅ Required secrets/variables configured (run `make pr-secrets` to verify)
- ✅ SSH access to ERP droplet (erp.insightpulseai.net)
- ✅ SSH access to OCR droplet (SGP1)
- ✅ Supabase credentials valid
- ✅ Backup of production database taken

---

## 🚀 Deployment Sequence

### Step 1: Database Setup (Supabase)

**Duration:** ~2 minutes

```bash
# Set connection string
export POSTGRES_URL="postgresql://$SUPABASE_DB_USER:$SUPABASE_DB_PASSWORD@$SUPABASE_DB_HOST:$SUPABASE_DB_PORT/$SUPABASE_DB_NAME?sslmode=require"

# 1. Apply warehouse views
psql "$POSTGRES_URL" -f warehouse/views.sql

# 2. Apply materialized views
psql "$POSTGRES_URL" -f warehouse/mv_refresh.sql

# 3. Apply Skillsmith schema
psql "$POSTGRES_URL" -f skillsmith/sql/skillsmith.sql

# 4. Verify views created
psql "$POSTGRES_URL" -c "SELECT viewname FROM pg_views WHERE schemaname = 'public' AND viewname LIKE 'vw_expense%';"
psql "$POSTGRES_URL" -c "SELECT matviewname FROM pg_matviews WHERE schemaname = 'public';"

# 5. Schedule materialized view refresh (pg_cron)
psql "$POSTGRES_URL" -c "
  SELECT cron.schedule(
    'refresh-expense-mv',
    '0 * * * *',
    \$\$REFRESH MATERIALIZED VIEW public.mv_expense_7d\$\$
  );
"

echo "✅ Database setup complete"
```

**Rollback (if needed):**
```bash
psql "$POSTGRES_URL" -f warehouse/rollback.sql  # Drop views
```

---

### Step 2: OCR Service Deployment (SGP1 Droplet)

**Duration:** ~5 minutes

```bash
# SSH to OCR droplet
ssh user@ocr.insightpulseai.net

# Navigate to repo
cd /opt/insightpulse-odoo

# Pull latest
git pull origin main

# Build OCR service
make tee-ocr-build

# Run OCR service
make tee-ocr-run

# Verify container running
docker ps | grep ip-ocr

# Test health endpoint
curl -s https://ocr.insightpulseai.net/health | jq

# Expected: {"ok": true}

# Test classification endpoint
curl -X POST https://ocr.insightpulseai.net/classify/expense \
  -H "Content-Type: application/json" \
  -d '{"text":"Restaurant dinner $45.20"}' | jq

# Expected: {"category": "Meals", "conf": 0.70}

echo "✅ OCR service deployed and verified"
```

**Rollback (if needed):**
```bash
docker stop ip-ocr
docker rm ip-ocr
# Restore previous version from backup
```

---

### Step 3: Odoo Module Installation (ERP Droplet)

**Duration:** ~10 minutes

```bash
# SSH to ERP droplet
ssh user@erp.insightpulseai.net

# Navigate to repo
cd /opt/insightpulse-odoo

# Pull latest
git pull origin main

# Copy modules to addons path
sudo cp -r odoo/modules/ip_expense_* /mnt/extra-addons/

# Verify copy
ls -la /mnt/extra-addons/ | grep ip_expense

# Install modules (with test mode)
sudo odoo -c /etc/odoo/odoo.conf \
  -d odoo_prod \
  -i ip_expense_ocr,ip_expense_policy,ip_expense_match,ip_expense_audit \
  --test-enable \
  --log-level=test \
  --stop-after-init

# If tests pass, restart Odoo
sudo systemctl restart odoo

# Verify service running
sudo systemctl status odoo

# Check module installation
sudo odoo -c /etc/odoo/odoo.conf \
  -d odoo_prod \
  --log-level=info \
  --stop-after-init \
  -c "import odoo; env = odoo.api.Environment.manage(); print([m.name for m in env['ir.module.module'].search([('name', 'like', 'ip_expense')])])"

echo "✅ Odoo modules installed and verified"
```

**Rollback (if needed):**
```bash
sudo odoo -c /etc/odoo/odoo.conf -d odoo_prod -u ip_expense_ocr,ip_expense_policy,ip_expense_match,ip_expense_audit --stop-after-init
sudo systemctl restart odoo
```

---

### Step 4: Nginx Configuration (If not already deployed)

**Duration:** ~3 minutes

```bash
# Copy Nginx configs
sudo cp infra/nginx/erp.insightpulseai.net.conf /etc/nginx/sites-available/
sudo cp infra/nginx/ocr.insightpulseai.net.conf /etc/nginx/sites-available/
sudo cp infra/nginx/insightpulseai.net.conf /etc/nginx/sites-available/

# Create symlinks
sudo ln -sf /etc/nginx/sites-available/erp.insightpulseai.net.conf /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/ocr.insightpulseai.net.conf /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/insightpulseai.net.conf /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload if test passes
sudo systemctl reload nginx

echo "✅ Nginx configured"
```

---

### Step 5: Auth Hub Deployment (Optional)

**Duration:** ~5 minutes

**Option A: DigitalOcean App Platform**

```bash
cd authhub

# Deploy via doctl
doctl apps create --spec runtime.yaml

# Or update existing app
doctl apps update $APP_ID --spec runtime.yaml
```

**Option B: Local/VM Deployment**

```bash
cd authhub

# Install dependencies
pip install -r requirements.txt

# Run with systemd
sudo cp authhub.service /etc/systemd/system/
sudo systemctl enable authhub
sudo systemctl start authhub

# Verify
curl https://insightpulseai.net/sso/health
```

---

### Step 6: Superset Dashboards (Optional)

**Duration:** ~10 minutes

```bash
cd superset

# Make bootstrap executable
chmod +x superset_bootstrap.sh

# Run bootstrap
./superset_bootstrap.sh

# Start Superset
docker compose up -d

# Verify
curl -s http://localhost:8088/health

# Import dashboards
docker compose exec superset superset import-dashboards -p /dashboards/te_overview.json
docker compose exec superset superset import-dashboards -p /dashboards/te_manager.json
docker compose exec superset superset import-dashboards -p /dashboards/te_audit.json

echo "✅ Superset deployed"
```

---

### Step 7: Health Checks

**Duration:** ~2 minutes

```bash
# Run comprehensive health check
make tee-health

# Manual verification
echo "=== OCR Service ==="
curl -s https://ocr.insightpulseai.net/health

echo "=== Odoo ERP ==="
curl -s https://erp.insightpulseai.net/web/health

echo "=== Auth Hub ==="
curl -s https://insightpulseai.net/sso/health

echo "=== Warehouse Views ==="
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM public.vw_expense_fact;"

echo "=== Skillsmith Functions ==="
psql "$POSTGRES_URL" -c "SELECT public.normalize_error_message('Test error with UUID 12345678-1234-1234-1234-123456789012');"
```

---

### Step 8: End-to-End Test

**Duration:** ~5 minutes

```bash
# 1. Test OCR classification
CATEGORY=$(curl -s -X POST https://ocr.insightpulseai.net/classify/expense \
  -H "Content-Type: application/json" \
  -d '{"text":"Business lunch at restaurant"}' | jq -r '.category')

echo "Classified as: $CATEGORY"

# 2. Test expense intake (requires authentication)
# Use Odoo web interface or API client
curl -X POST https://erp.insightpulseai.net/ip/expense/intake \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=YOUR_SESSION_ID" \
  -d '{
    "merchant": "Test Restaurant",
    "total": 45.20,
    "category": "Meals",
    "conf": 0.85,
    "idempotency_key": "test-deploy-001"
  }'

# 3. Verify expense created in Odoo
# Login to https://erp.insightpulseai.net and check Expenses module

# 4. Verify warehouse view updated
psql "$POSTGRES_URL" -c "
  SELECT * FROM public.vw_expense_fact
  WHERE x_idempotency_key = 'test-deploy-001';
"

echo "✅ End-to-end test complete"
```

---

## 📊 Post-Deployment Monitoring

### First 24 Hours

Monitor these metrics:

```bash
# OCR service logs
docker logs -f ip-ocr --tail=100

# Odoo logs
sudo journalctl -u odoo -f

# Nginx access logs
sudo tail -f /var/log/nginx/erp.insightpulseai.net.access.log
sudo tail -f /var/log/nginx/ocr.insightpulseai.net.access.log

# Database connections
psql "$POSTGRES_URL" -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'postgres';"

# Materialized view refresh status
psql "$POSTGRES_URL" -c "
  SELECT jobname, last_run, next_run, status
  FROM cron.job
  WHERE jobname = 'refresh-expense-mv';
"
```

### Key Performance Indicators

- **OCR Response Time:** < 2 seconds
- **Odoo Page Load:** < 3 seconds
- **Warehouse Query Time:** < 500ms
- **Error Rate:** < 0.1%

---

## 🚨 Rollback Procedures

### Emergency Rollback

```bash
# 1. Stop new services
docker stop ip-ocr
sudo systemctl stop authhub

# 2. Uninstall Odoo modules
ssh user@erp.insightpulseai.net
sudo odoo -c /etc/odoo/odoo.conf -d odoo_prod \
  -u ip_expense_ocr,ip_expense_policy,ip_expense_match,ip_expense_audit \
  --stop-after-init
sudo systemctl restart odoo

# 3. Drop warehouse views
psql "$POSTGRES_URL" -f warehouse/rollback.sql

# 4. Revert Nginx configs
sudo rm /etc/nginx/sites-enabled/ocr.insightpulseai.net.conf
sudo systemctl reload nginx
```

---

## 📞 Support Contacts

- **Owner:** @jgtolentino
- **Ops Team:** @ops-team
- **Emergency:** Create incident in GitHub Issues

---

## ✅ Deployment Sign-Off

After successful deployment, update:

1. **CHANGELOG.md** - Add release notes
2. **GitHub Release** - Create `v1.0.0-tee-mvp` tag
3. **Documentation** - Update deployment status
4. **Team Notification** - Announce in Slack/Discord

```bash
# Create release tag
git tag -a v1.0.0-tee-mvp -m "T&E MVP Bundle - Production Release"
git push origin v1.0.0-tee-mvp

# Create GitHub release
gh release create v1.0.0-tee-mvp \
  --title "T&E MVP Bundle v1.0.0" \
  --notes-file RELEASE_NOTES.md
```

---

**Deployment completed:** ✅
**Date:** _____________
**Deployed by:** _____________
**Sign-off:** _____________

---

**Last Updated:** 2025-11-07
**For PR:** #326 (InsightPulse T&E MVP Bundle)
