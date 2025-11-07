# Superset Analytics for T&E MVP

Reverse‑proxy at https://superset.${DOMAIN_ROOT} → http://127.0.0.1:8088

Set OAuth later; for MVP use admin login.

## Dashboards

- `te_overview.json` - T&E Overview Dashboard
- `te_manager.json` - Manager Dashboard
- `te_audit.json` - Audit Dashboard

## Deployment

```bash
cd superset
chmod +x superset_bootstrap.sh
./superset_bootstrap.sh
docker compose up -d
```

## Access

Default credentials: admin / admin (change in production)
