# Runbook: Observability Minimum Standard (Odoo + Supabase + n8n)

## Standard
- Health endpoints for each service
- Structured logs (JSON preferred) where possible
- Correlation IDs for cross-service tracing
- Alerts for:
  - service down
  - repeated failures (n8n)
  - DB connectivity failures

## Odoo
- Capture container logs + nginx access/error logs
- Define a health check endpoint:
  - HTTP 200 on `/web/login` or a dedicated `/health` route via nginx (preferred)
- Alert on:
  - 5xx spikes
  - login page unavailable
  - DB connection errors

## Supabase
- Edge Function logs enabled
- RPC latency monitoring (where available)
- Alert on:
  - function error rate
  - auth failures spikes
  - DB timeouts

## n8n
- Log every failed workflow run
- Enable retry/backoff on IO steps
- Push failures to Zoho mail notifier (via SMTP) or internal webhook
