# Odoo 19 Enterprise‑parity + Notion Clone (insightpulseai.net)

## Prereqs
- Ubuntu 22.04+
- Docker + Docker Compose v2
- A DNS A record: insightpulseai.net -> your droplet IP

## One‑shot deploy
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
newgrp docker

curl -L -o odoo19_enterprise_notion.zip "sandbox:/mnt/data/odoo19_enterprise_notion.zip"
unzip odoo19_enterprise_notion.zip -d /opt/odoo19_enterprise
cd /opt/odoo19_enterprise/bundle

cp env/.env.example .env
# Edit .env for EMAIL and optional passwords
./scripts/fetch_oca.sh

docker compose build ocr-api
docker compose up -d
```

## Services
- https://insightpulseai.net → Odoo 19 (TLS via Caddy)
- OnlyOffice: proxied at /onlyoffice/
- Longpolling: proxied internally
- OCR API: proxied at /ocr/

## First login
Open https://insightpulseai.net, create DB, then install:
- OCA: auth_totp, auth_password_policy, auth_session_timeout, queue_job, server_environment,
  web_responsive, web_environment_ribbon, base_user_role, attachment_storage, document,
  account-financial-tools (select those relevant), helpdesk, fieldservice (optional).
- Custom: knowledge_notion_clone, expenseflow_* (optional).

## Backups
Use pg_dump nightly. Example cron:
```bash
echo '0 2 * * * docker exec -i $(docker ps -qf name=postgres)   pg_dump -U ${POSTGRES_USER:-odoo} ${POSTGRES_DB:-odoo} | gzip > /var/backups/odoo_$(date +\%F).sql.gz' | sudo tee /etc/cron.d/odoo_backup
```
