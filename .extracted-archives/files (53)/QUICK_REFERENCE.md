# InsightPulse AI - CI/CD Quick Reference

## 🚀 Quick Deploy

```bash
# Deploy all services to production
git push origin main

# Deploy to staging
git push origin staging

# Manual deployment
gh workflow run deploy-odoo.yml
gh workflow run deploy-mcp.yml
gh workflow run deploy-superset.yml
```

## 🏥 Health Checks

```bash
# One-liner to check all services
curl -s https://erp.insightpulseai.net/web/health && \
curl -s https://mcp.insightpulseai.net/health && \
curl -s https://superset.insightpulseai.net/health && \
echo "✅ All services healthy"
```

## 📊 View Logs

```bash
# Odoo logs
ssh root@165.227.10.178 'docker logs odoo --tail 100 -f'

# MCP logs
doctl apps logs $(doctl apps list --format ID --no-header | head -1) --type run --tail 100 --follow

# Superset logs
doctl apps logs $(doctl apps list --format ID --no-header | sed -n 2p) --type run --tail 100 --follow

# All deployment logs from Supabase
curl -s "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/deployment_logs?order=deployed_at.desc&limit=10" \
  -H "apikey: $SUPABASE_ANON_KEY" | jq .
```

## 🔄 Rollback

```bash
# Rollback Odoo (on droplet)
ssh root@165.227.10.178
docker stop odoo
docker run -d --name odoo <PREVIOUS_IMAGE>

# Rollback App Platform service
doctl apps list-deployments <APP_ID> --format ID,Created --no-header
doctl apps create-deployment <APP_ID> <PREVIOUS_DEPLOYMENT_ID>
```

## 🧪 Run Tests

```bash
# Integration tests
gh workflow run integration-tests.yml

# Local tests
docker-compose up -d
./scripts/smoke-test.sh
docker-compose down
```

## 💾 Backup

```bash
# Manual backup on droplet
ssh root@165.227.10.178 '/opt/insightpulse-odoo/scripts/backup.sh'

# Restore backup
ssh root@165.227.10.178
cd /backup
gunzip odoo-YYYYMMDD-HHMMSS.sql.gz
docker exec -i odoo-postgres psql -U odoo odoo < odoo-YYYYMMDD-HHMMSS.sql
```

## 🔧 Common Tasks

### Update Odoo Module

```bash
# SSH to droplet
ssh root@165.227.10.178

# Update module
docker exec odoo odoo -u finance_ssc -d odoo --stop-after-init

# Restart Odoo
docker restart odoo
```

### Add New MCP Skill

```bash
# Create skill file
cat > services/mcp-coordinator/src/skills/my_new_skill.py <<EOF
# Your skill code here
EOF

# Commit and push (triggers auto-deploy)
git add services/mcp-coordinator/src/skills/my_new_skill.py
git commit -m "Add new MCP skill"
git push origin main

# Verify deployment
curl https://mcp.insightpulseai.net/skills | jq '.skills[] | select(.name=="my_new_skill")'
```

### Create Superset Dashboard

```bash
# Export dashboard JSON from Superset UI
# Then save to repo
cp dashboard.json services/superset/dashboards/

# Commit and push
git add services/superset/dashboards/
git commit -m "Add new Superset dashboard"
git push origin main

# Import via MCP
curl -X POST https://mcp.insightpulseai.net/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "superset_automation",
    "action": "import_dashboards",
    "params": {
      "source": "services/superset/dashboards/dashboard.json"
    }
  }'
```

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check GitHub Actions logs
gh run list --workflow=deploy-<service>.yml
gh run view <RUN_ID>

# Check App Platform logs
doctl apps list-deployments <APP_ID>
doctl apps get-deployment <APP_ID> <DEPLOYMENT_ID>
```

### Database Connection Issues

```bash
# Test connection from Odoo
docker exec odoo odoo shell -c "env['ir.config_parameter'].sudo().get_param('database.uuid')"

# Test Supabase connection
curl -s "https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/" \
  -H "apikey: $SUPABASE_ANON_KEY"
```

### SSL Certificate Issues

```bash
# Renew Let's Encrypt certificate on droplet
ssh root@165.227.10.178
certbot renew --nginx
nginx -t && nginx -s reload
```

## 📱 Monitoring URLs

- **GitHub Actions**: https://github.com/jgtolentino/insightpulse-odoo/actions
- **DigitalOcean Console**: https://cloud.digitalocean.com/projects/29cde7a1-8280-46ad-9fdf-dea7b21a7825
- **Supabase Dashboard**: https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz

## 🔐 Security Commands

```bash
# Rotate Odoo admin password
docker exec -it odoo odoo shell
>>> env['res.users'].browse(2).password = 'new_password'
>>> env.cr.commit()

# Rotate Superset secret key
# Update GitHub secret SUPERSET_SECRET_KEY_PROD
openssl rand -hex 42

# Then trigger redeployment
gh workflow run deploy-superset.yml
```

## 📊 Metrics

```bash
# Service uptime
curl -s https://mcp.insightpulseai.net/metrics

# Database stats
docker exec odoo-postgres psql -U odoo -c "SELECT pg_size_pretty(pg_database_size('odoo'));"

# Request counts (if using Nginx logs)
ssh root@165.227.10.178 'cat /var/log/nginx/access.log | wc -l'
```

## 🎯 Emergency Contacts

- **DevOps Lead**: Jake Tolentino
- **Slack Channel**: #insightpulse-alerts
- **On-call Rotation**: Check PagerDuty

## 📚 Documentation Links

- [Full Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Migration Plan](./MIGRATION_PLAN.md)
- [Odoo Module Docs](./services/odoo/addons/README.md)
- [MCP Skills Docs](./services/mcp-coordinator/src/skills/README.md)

## 💡 Pro Tips

1. **Always test locally first**: `docker-compose up` before pushing
2. **Use staging branch**: Test changes before merging to main
3. **Monitor Slack**: All deployment notifications go there
4. **Keep Supabase logs**: Query regularly to spot patterns
5. **Backup before major changes**: Run `scripts/backup.sh` first

---

**Last Updated**: 2025-11-04  
**Production Status**: ✅ Ready  
**Version**: 1.0.0
