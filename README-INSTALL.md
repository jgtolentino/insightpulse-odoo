# Install
1) `cp config/.env.example config/.env` → fill DB/SMTP/ADMIN_PASS.
2) `docker compose -f deploy/docker-compose.yml up -d`
3) `bash scripts/install_modules.sh`
4) `bash scripts/freeze-urls.sh`

# Upgrade
`docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d $ODOO_DB -u insightpulse_enterprise --stop-after-init`

# Backup
`bash scripts/backup-db.sh`
