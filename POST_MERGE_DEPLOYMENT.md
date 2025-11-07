# Post-Merge Deployment (Odoo 18 MVP)

## 0) One-time server prep

```bash
sudo apt-get update && sudo apt-get install -y \
  nginx python3-certbot-nginx docker.io docker-compose-plugin
sudo usermod -aG docker $USER
sudo mkdir -p /opt/insightpulse-odoo && sudo chown $USER:$USER /opt/insightpulse-odoo
```

## 1) Nginx & TLS

Copy these files from `infra/nginx/` to `/etc/nginx/sites-available/`:

- `erp.insightpulseai.net.conf`
- `deepwiki.insightpulseai.net.conf`

Then:

```bash
sudo ln -sf /etc/nginx/sites-available/erp.insightpulseai.net.conf /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/deepwiki.insightpulseai.net.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d erp.insightpulseai.net -d deepwiki.insightpulseai.net
```

## 2) Required GitHub Actions settings

Variables (Actions → Variables):
```
DEPLOY_HOST=<droplet ip or host>
DEPLOY_USER=<ssh user, e.g. root>
DEPLOY_PATH=/opt/insightpulse-odoo
ODOO_FQDN=erp.insightpulseai.net
LOG_LEVEL=info
```

Secrets (Actions → Secrets):
```
SSH_PRIVATE_KEY
```

*(Optionally add: SUPABASE_* and SLACK_WEBHOOK, etc.)*

## 3) Release & deploy

```bash
git tag v18.0.0
git push origin v18.0.0
```

GitHub Actions → **deploy-prod** builds & pushes:
- `ghcr.io/<org>/insightpulse-odoo/odoo18:latest`
- `ghcr.io/<org>/insightpulse-odoo/deepwiki:latest` (if DeepWiki present)

Then it SSH-deploys docker-compose to the server.

## 4) Health checks

On server (automated by workflow):
```bash
docker compose -f /opt/insightpulse-odoo/docker-compose.yml ps
curl -fsS http://127.0.0.1:8069/ | head -c 80
curl -fsS http://127.0.0.1:8098/health || true
```

Externally:
```bash
curl -I https://erp.insightpulseai.net
curl -s https://deepwiki.insightpulseai.net/health
```

## 5) Odoo module upgrade

If your MVP includes custom modules:
```bash
sudo docker compose -f /opt/insightpulse-odoo/docker-compose.yml exec -T odoo \
  odoo -d odoo -u all --stop-after-init
```

## 6) Canary & rollback

Create a new tag for each release (`v18.0.1`, `v18.0.2`, …).
To rollback, re-run the workflow on an older tag or:
```bash
ssh $DEPLOY_HOST "cd /opt/insightpulse-odoo && docker compose up -d"
```

## 7) Nightly DeepWiki (optional)

Use `.github/workflows/deepwiki-nightly.yml` if present to keep indexes fresh.

---

**Done.** Your Odoo 18 MVP is production-deployable with GHCR images, Nginx TLS, and SSH-based compose rollout.
