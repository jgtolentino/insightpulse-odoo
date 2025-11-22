# Odoo Module Deployment Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-22
**Purpose:** Step-by-step guide for deploying IPAI custom modules to production

---

## Overview

This guide documents the deployment procedure for IPAI custom Odoo CE modules to production (`erp.insightpulseai.net`).

**Available Modules:**
- `ipai_ce_cleaner` - Enterprise/IAP removal
- `ipai_expense` - PH expense & travel workflows
- `ipai_equipment` - Equipment booking system
- `ipai_ocr_expense` - OCR integration for expenses
- `ipai_finance_monthly_closing` - Finance closing + BIR tasks

---

## Deployment Methods

### Method 1: Automated Script (Recommended)

Use the deployment script that follows the `deploy_odoo_module` skill from the Agent Skills Architecture.

**Deploy single module:**
```bash
cd /home/user/odoo-ce
./scripts/deploy-odoo-modules.sh ipai_expense
```

**Deploy multiple modules:**
```bash
./scripts/deploy-odoo-modules.sh ipai_expense ipai_equipment ipai_finance_monthly_closing
```

**Deploy all modules:**
```bash
./scripts/deploy-odoo-modules.sh --all
```

**What the script does:**
1. ✅ Validates modules exist locally
2. ✅ Checks CE/OCA compliance (no Enterprise deps)
3. ✅ Rsyncs modules to `/opt/odoo/custom-addons/` on server
4. ✅ Restarts Odoo container
5. ✅ Optionally upgrades modules in Odoo
6. ✅ Checks Odoo health endpoint

### Method 2: Manual Deployment

**Step-by-step manual process:**

```bash
# 1. Validate module locally
ls -la addons/ipai_expense
cat addons/ipai_expense/__manifest__.py

# 2. Check CE/OCA compliance
grep -r "OEEL" addons/ipai_expense  # Should return empty
grep -r "odoo.com" addons/ipai_expense  # Should be empty (except comments)

# 3. Rsync to server
rsync -avz --delete \
  --exclude="*.pyc" \
  --exclude="__pycache__" \
  addons/ipai_expense/ \
  root@erp.insightpulseai.net:/opt/odoo/custom-addons/ipai_expense/

# 4. Restart Odoo container
ssh root@erp.insightpulseai.net "docker restart odoo-odoo-1"

# Wait 10 seconds for Odoo to start
sleep 10

# 5. Upgrade module (optional)
ssh root@erp.insightpulseai.net \
  "docker exec odoo-odoo-1 odoo -d odoo -u ipai_expense --workers=0 --stop-after-init"

# 6. Restart again after upgrade
ssh root@erp.insightpulseai.net "docker restart odoo-odoo-1"

# 7. Check health
curl -I https://erp.insightpulseai.net/web/health
```

---

## Pre-Deployment Checklist

Before deploying any module:

- [ ] Module exists in `addons/` directory
- [ ] `__manifest__.py` is present and valid
- [ ] No Enterprise modules in `depends` list
- [ ] No `OEEL` license references
- [ ] No `odoo.com` links in user-facing code
- [ ] CI checks pass (GitHub Actions green)
- [ ] Local testing completed
- [ ] Database backup taken (if schema changes)
- [ ] SSH access to `root@erp.insightpulseai.net` configured

---

## Post-Deployment Steps

After deployment:

1. **Access Odoo:**
   - Navigate to https://erp.insightpulseai.net/web
   - Log in as admin

2. **Update Apps List:**
   - Go to **Apps** → Three dots menu → **Update Apps List**
   - This refreshes the module list

3. **Install or Upgrade Module:**

   **For new installation:**
   - Search for module name (e.g., "IPAI Expense")
   - Click **Install**

   **For upgrade:**
   - Search for module name
   - If upgrade available, click **Upgrade**

4. **Verify Installation:**
   - Check module appears in Apps list
   - Test basic functionality
   - Check Odoo logs for errors:
     ```bash
     ssh root@erp.insightpulseai.net "docker logs odoo-odoo-1 --tail 100"
     ```

---

## Troubleshooting

### Module Won't Install

**Symptom:** Module doesn't appear in Apps list or fails to install

**Diagnosis:**
```bash
# Check if module exists on server
ssh root@erp.insightpulseai.net "ls -la /opt/odoo/custom-addons/ipai_expense"

# Check Odoo logs
ssh root@erp.insightpulseai.net "docker logs odoo-odoo-1 --tail 100 | grep -i error"
```

**Common Causes:**
- Missing dependency module
- Syntax error in Python code
- Missing `ir.model.access.csv` file
- Wrong `depends` list in `__manifest__.py`

**Solution:**
1. Fix issue locally
2. Redeploy module
3. Restart Odoo
4. Try installation again

### CI Fails with Enterprise Module Detected

**Symptom:** GitHub Actions fails with "Enterprise module detected"

**Diagnosis:**
```bash
# Check for Enterprise references
grep -r "OEEL" addons/ipai_expense
grep -r "enterprise" addons/ipai_expense/__manifest__.py
```

**Solution:**
1. Remove Enterprise module from `depends` list
2. Find CE/OCA alternative
3. Update code to use CE-only features
4. Commit changes
5. Wait for CI to pass
6. Redeploy

### Odoo Won't Start After Deployment

**Symptom:** Odoo container crashes or won't start

**Diagnosis:**
```bash
# Check container status
ssh root@erp.insightpulseai.net "docker ps -a | grep odoo"

# Check logs
ssh root@erp.insightpulseai.net "docker logs odoo-odoo-1 --tail 200"
```

**Common Causes:**
- Syntax error in Python code
- Missing Python dependency
- Database migration failure

**Solution:**
1. Restore from backup if available
2. Fix syntax errors locally
3. Redeploy corrected code
4. Restart Odoo

### Module Upgrade Fails

**Symptom:** Module upgrade command fails or times out

**Diagnosis:**
```bash
# Run upgrade manually and watch logs
ssh root@erp.insightpulseai.net \
  "docker exec odoo-odoo-1 odoo -d odoo -u ipai_expense --workers=0 --stop-after-init --log-level=debug"
```

**Common Causes:**
- Database schema change incompatible
- Missing migration script
- Circular dependency

**Solution:**
1. Check migration logs
2. Add migration script if needed (`migrations/18.0.1.0.1/pre-migrate.py`)
3. Restore from backup if critical
4. Contact Odoo CE community for help

---

## Rollback Procedure

If deployment causes issues:

**Step 1: Restore Previous Module Version**
```bash
# Get previous version from git
git log --oneline addons/ipai_expense  # Find commit hash
git checkout <commit-hash> addons/ipai_expense

# Redeploy old version
./scripts/deploy-odoo-modules.sh ipai_expense
```

**Step 2: Restore Database (if schema changed)**
```bash
# Connect to server
ssh root@erp.insightpulseai.net

# Restore from backup
cd /opt/odoo-ce/backups
docker exec odoo-db-1 psql -U odoo < odoo-backup-YYYYMMDD.sql
```

**Step 3: Restart Odoo**
```bash
ssh root@erp.insightpulseai.net "docker restart odoo-odoo-1"
```

---

## Best Practices

1. **Always deploy during maintenance windows** (low usage periods)
2. **Test in staging first** (if available)
3. **Take database backup before schema changes**
4. **Deploy one module at a time** for easier troubleshooting
5. **Monitor logs for 5-10 minutes after deployment**
6. **Notify users before deploying critical modules**
7. **Have rollback plan ready**
8. **Document deployment in changelog**

---

## Deployment Schedule

**Recommended deployment times (PH time):**
- **Weekdays:** 6:00 PM - 8:00 PM (after business hours)
- **Weekends:** Anytime

**Avoid deploying during:**
- Month-end closing (last 3 days of month)
- BIR filing deadlines
- Peak usage hours (9:00 AM - 5:00 PM PH time)

---

## Related Documentation

- **Agent Skills Registry:** `agents/AGENT_SKILLS_REGISTRY.yaml` → `deploy_odoo_module` skill
- **Execution Procedures:** `agents/procedures/EXECUTION_PROCEDURES.yaml` → `build_new_feature`
- **Module Service Matrix:** `specs/MODULE_SERVICE_MATRIX.md`
- **Project Spec:** `spec.md`
- **Implementation Plan:** `plan.md`

---

## Support

**If deployment fails:**
1. Check troubleshooting section above
2. Review Odoo logs: `docker logs odoo-odoo-1`
3. Consult knowledge base: `agents/knowledge/KNOWLEDGE_BASE_INDEX.yaml`
4. Create GitHub issue with logs and error messages

**Contacts:**
- **Infrastructure:** DevOps team
- **Odoo Modules:** Platform Team
- **Emergency:** Restore from backup first, debug later

---

**Document Version:** 1.0.0
**Last Review:** 2025-11-22
**Next Review:** Monthly (check for updates)
