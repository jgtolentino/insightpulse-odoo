---
description: Deploy to DigitalOcean App Platform with health checks
---

# Deploy to Production

Deploy the current branch to production with safety checks:

1. **Pre-deployment checks:**
   - [ ] All tests pass: `pytest odoo/tests -q`
   - [ ] Linters pass: `black . && flake8 . && pylint addons/`
   - [ ] No uncommitted changes: `git status`
   - [ ] On correct branch (not `main`)
   - [ ] PR approved and merged

2. **Staging deployment:**
   ```bash
   doctl apps create-deployment {staging_app_id} --wait
   ```

3. **Staging validation:**
   - [ ] Health check: `curl https://staging.insightpulseai.net/health`
   - [ ] Smoke tests pass
   - [ ] No errors in logs: `doctl apps logs {staging_app_id} --tail 100`

4. **Production deployment (blue-green):**
   ```bash
   doctl apps create-deployment {prod_app_id} --wait
   ```

5. **Production validation:**
   - [ ] Health check: `curl https://insightpulseai.net/health`
   - [ ] Key endpoints responding (<500ms)
   - [ ] No error spikes in Prometheus
   - [ ] Database connections healthy

6. **Rollback plan:**
   - If errors detected, rollback: `doctl apps rollback {prod_app_id}`
   - Notify team on Slack
   - Create incident report

**Safety**: Blue-green deployment, auto-rollback on failure
