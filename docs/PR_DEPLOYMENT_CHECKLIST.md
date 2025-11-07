# 🚀 PR Deployment Checklist

Use this checklist before merging any PR that affects production deployments.

---

## A. CI/CD & Automation ✅

- [ ] All CI workflows passing (no failures)
- [ ] `auto-heal-smoke` workflow green
- [ ] `auto-patch-nightly` shows "No changes" or opened a bot PR that was reviewed
- [ ] Security scans passed (Trivy, dependency scanning)
- [ ] No critical vulnerabilities introduced
- [ ] Docker images built successfully
- [ ] Integration tests passed

---

## B. Code Quality 📝

- [ ] Code reviewed by at least one other developer
- [ ] No merge conflicts
- [ ] All TODOs/FIXMEs addressed or documented
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated with PR changes
- [ ] Commit messages follow conventional commits

---

## C. Data & Migrations 💾

- [ ] Database migrations tested in staging
- [ ] Backward compatibility verified
- [ ] Data migration scripts tested (if applicable)
- [ ] Rollback plan documented
- [ ] Healer impact assessed (no unexpected restarts during migration window)
- [ ] Backup taken before deployment

---

## D. Odoo Module Changes 🔧

- [ ] `__manifest__.py` version bumped
- [ ] Dependencies declared correctly
- [ ] ACL permissions defined
- [ ] Views validated
- [ ] Models tested
- [ ] Odoo 19 compatibility checked (`make odoo19:scan`)
- [ ] OCA compliance validated (if applicable)

---

## E. Infrastructure Changes 🏗️

- [ ] Docker Compose changes tested locally
- [ ] Environment variables documented
- [ ] Secrets updated in vault (if needed)
- [ ] DigitalOcean App Platform specs validated
- [ ] Health check endpoints working
- [ ] Resource limits appropriate
- [ ] SSL/TLS certificates valid

---

## F. Testing & QA 🧪

- [ ] Unit tests passed
- [ ] Integration tests passed
- [ ] E2E tests passed (if applicable)
- [ ] Manual smoke tests completed
- [ ] Load testing completed (for performance changes)
- [ ] Browser compatibility checked (for frontend changes)

---

## G. Deployment Sequence 📋

### Pre-Deployment

1. [ ] Announce deployment window in team chat
2. [ ] Create database backup:
   ```bash
   make backup
   ```
3. [ ] Tag current production version:
   ```bash
   git tag -a v$(date +%Y%m%d-%H%M) -m "Pre-deployment snapshot"
   git push origin --tags
   ```

### Staging Deployment

4. [ ] Deploy to staging:
   ```bash
   make deploy-staging
   ```
5. [ ] Run staging smoke tests:
   ```bash
   bash scripts/smoke_test_staging.sh
   ```
6. [ ] Verify health checks pass
7. [ ] Test critical user flows

### Production Deployment

8. [ ] Deploy to production:
   ```bash
   make deploy-prod
   ```
9. [ ] Monitor deployment:
   ```bash
   watch -n 5 'doctl apps get-deployment $APP_ID $DEPLOYMENT_ID'
   ```
10. [ ] Verify health checks pass
11. [ ] Start healers in prod:
    ```bash
    make healing:start
    ```
12. [ ] Verify timers scheduled:
    ```bash
    make healing:status
    ```
13. [ ] Test critical user flows in production
14. [ ] Monitor error logs for 15 minutes:
    ```bash
    make logs-odoo
    ```

### Post-Deployment

15. [ ] Update deployment documentation
16. [ ] Announce deployment complete
17. [ ] Close deployment incident ticket
18. [ ] Monitor metrics for 24 hours
19. [ ] Review healer actions after 24 hours

---

## H. Rollback Plan 🔄

**If deployment fails:**

1. [ ] Immediately execute rollback:
   ```bash
   make rollback
   ```
2. [ ] Verify rollback successful:
   ```bash
   bash scripts/health-check-all-services.sh
   ```
3. [ ] Restore database backup (if needed):
   ```bash
   make restore BACKUP_FILE=backups/backup-YYYYMMDD-HHMMSS.sql
   ```
4. [ ] Notify team of rollback
5. [ ] Create post-mortem ticket
6. [ ] Document failure reason

---

## I. Monitoring & Alerts 📊

- [ ] Prometheus metrics collecting
- [ ] Grafana dashboards updated
- [ ] Alert rules configured
- [ ] Slack/Discord notifications working
- [ ] PagerDuty integrated (for critical services)
- [ ] Error tracking enabled (Sentry/etc)

---

## J. Security 🔒

- [ ] No secrets in code
- [ ] Environment variables secured
- [ ] API keys rotated (if needed)
- [ ] SSL certificates valid
- [ ] CORS policies correct
- [ ] Rate limiting configured
- [ ] WAF rules updated (if applicable)

---

## K. Performance 🚀

- [ ] No N+1 queries introduced
- [ ] Database indexes appropriate
- [ ] Cache warming tested
- [ ] CDN configured (if applicable)
- [ ] Asset optimization complete
- [ ] Memory usage within limits

---

## L. Documentation 📚

- [ ] README updated
- [ ] API documentation updated
- [ ] Deployment guide current
- [ ] Troubleshooting guide updated
- [ ] Architecture diagrams accurate
- [ ] Runbooks updated

---

## Special Checks for Specific Changes

### For Supabase Changes
- [ ] Edge Functions deployed
- [ ] RLS policies tested
- [ ] Database migrations applied
- [ ] Connection pooling verified

### For Superset Changes
- [ ] Dashboard migrations tested
- [ ] Chart configurations validated
- [ ] Database connections working
- [ ] User permissions correct

### For Auto-Healing Changes
- [ ] Healer scripts syntax validated
- [ ] Systemd units tested
- [ ] Timer intervals appropriate
- [ ] Alert thresholds tuned
- [ ] Logs rotation configured

---

## Emergency Contacts

**On-Call Engineer:** (Rotate weekly)
**DevOps Lead:** jgtolentino_rn@yahoo.com
**Support Email:** support@insightpulseai.com

---

## Post-Deployment Verification Script

Run this after every deployment:

```bash
#!/bin/bash
# scripts/post-deployment-verification.sh

echo "🔍 Post-Deployment Verification"
echo "================================"

# Check all services
bash scripts/health-check-all-services.sh

# Verify Odoo
curl -f https://erp.insightpulseai.net/web/health || echo "❌ Odoo health check failed"

# Verify Superset
curl -f https://superset.insightpulseai.net/health || echo "❌ Superset health check failed"

# Check database connections
python3 auto-healing/remediation/fix_db_connections.py

# Verify healers active
make healing:status

# Check recent logs for errors
docker logs insightpulse-odoo --tail 100 | grep -i error || echo "✅ No errors in last 100 lines"

echo ""
echo "✅ Post-deployment verification complete"
```

---

## Approval

- [ ] **Tech Lead Approved:** _________________ (Date: ________)
- [ ] **DevOps Approved:** _________________ (Date: ________)
- [ ] **QA Approved:** _________________ (Date: ________)

---

## Deployment Log

| Date | PR # | Deployed By | Result | Rollback? | Notes |
|------|------|-------------|--------|-----------|-------|
|      |      |             |        |           |       |

---

**Template Version:** 1.1.0
**Last Updated:** 2025-11-07
**Maintained By:** InsightPulse DevOps Team
