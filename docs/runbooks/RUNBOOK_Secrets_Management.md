# Runbook: Secrets Management (Org-wide)

## Policy
- No secrets in git.
- All runtime secrets in:
  1) GitHub Environments (repo/org) for CI/CD
  2) Supabase secrets for Edge Functions
  3) DO droplet secrets via environment files mounted outside repo (or secret manager if added)

## Required Secret Sets

### CI (GitHub)
- DO_MANAGED_PG_HOST
- DO_MANAGED_PG_PORT
- DO_MANAGED_PG_USER
- DO_MANAGED_PG_DB
- DO_MANAGED_PG_PASSWORD
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY

### Supabase Edge Functions
- SERVICE_ROLE_KEY (or equivalent)
- Any upstream API keys used by agents/workflows

## Rotation
- Rotate on schedule or incident
- Validate with automated preflight (CI job)
