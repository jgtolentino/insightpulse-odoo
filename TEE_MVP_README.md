# InsightPulse T&E MVP — End‑to‑End Install

This guide deploys:
- Odoo T&E modules (policy, OCR intake, match, audit)
- OCR + Smol‑LLM service on SGP1 droplet (FastAPI)
- Superset analytics at https://superset.${DOMAIN_ROOT}
- Unified SSO (Auth Hub cookie stamper)
- Warehouse views + materialized summaries
- Skillsmith error→skill loop + scheduled mining

## Prereqs
- Domain DNS pointing to droplets/app platform per your environment
- SSH to Odoo droplet (ERP), OCR droplet
- Supabase project (Postgres) with credentials
- DO App Platform for Superset (or VM with Docker)
- Python 3.10+ locally for tooling

## 1) Configure
```bash
cp .env.example .env  &&  export $(grep -v '^#' .env | xargs)
```

## 2) Odoo: install modules (ERP droplet, no Docker)
- Copy `odoo/modules/*` into `/mnt/extra-addons/` on the ERP droplet.
- Ensure `/etc/odoo/odoo.conf` includes `addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons`
- Upgrade modules:
```bash
sudo odoo -c /etc/odoo/odoo.conf -d odoo_prod -u ip_expense_ocr,ip_expense_policy,ip_expense_match,ip_expense_audit --stop-after-init
sudo systemctl restart odoo
```
- Verify Google OAuth buttons on `/web/login?debug=assets` are visible.

## 3) OCR service (SGP1 droplet)
- Build & run container (or run via uvicorn):
```bash
cd ocrsvc && docker build -t ip-ocr:latest .
docker run -d --name ip-ocr -p 127.0.0.1:${OCR_PORT}:8080 --restart=always --env-file ../.env ip-ocr:latest
```
- Nginx site: copy `infra/nginx/ocr.insightpulseai.net.conf` → `/etc/nginx/sites-available/`, enable & reload.
- Test:
```bash
curl -s https://${OCR_HOST}/health
```

## 4) Auth Hub (unified cookie)
- Run locally or deploy to DO App Platform:
```bash
cd authhub && pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port ${AUTHHUB_PORT}
```
- Nginx for root/landing can proxy to Auth Hub for `/sso/cookie`.

## 5) Superset
- If using Docker on a VM: `cd superset && ./superset_bootstrap.sh && docker compose up -d`
- On DO App Platform: set env vars and deploy `apache/superset:latest`, mount `dashboards/*.json` during init.
- Import dashboards from `superset/dashboards/` and set refresh schedule.

## 6) Warehouse (Supabase)
- Apply: `psql ... -f warehouse/views.sql` and `warehouse/mv_refresh.sql` (cron hourly).

## 7) Skillsmith
- Apply SQL: `psql ... -f skillsmith/sql/skillsmith.sql`
- Schedule CI (GitHub Actions): provided in `.github/workflows/skillsmith.yml`.
- Manual run: `make skills-mine`

## 8) End‑to‑end test
- Expo app → capture receipt → receives draft expense in Odoo.
- OCR returns merchant/date/total/category, Odoo webhook creates draft.
- Superset Overview loads <3 s.
- Inject synthetic error → proposed skill file appears under `skills/proposed`.

## ✅ Verification (Eval-Complete)

* Odoo 18 **JSON controller** contract validated (idempotency + `type='json'`).
* QWeb **login inheritance** validated on the effective login page.
* OAuth link presence checked via curl (non-fatal if no provider enabled).
* Optional evals cover OCR and warehouse without coupling to Odoo runtime.

## 🔐 GitHub Secrets Setup

Before running CI, configure these in your repository:

**Actions → Variables:**
- `ODOO_HOST` = erp.insightpulseai.net
- `OCR_HOST` = ocr.insightpulseai.net

**Actions → Secrets:**
- `SUPABASE_DB_HOST`
- `SUPABASE_DB_PORT`
- `SUPABASE_DB_NAME`
- `SUPABASE_DB_USER`
- `SUPABASE_DB_PASSWORD`
