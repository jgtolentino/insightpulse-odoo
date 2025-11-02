# DigitalOcean Environment Variable Fix

**Issue**: App crashing on boot due to environment variables set to literal placeholders like `${GITHUB_APP_ID}` instead of actual values.

**Symptoms**:
- Python services: `ValueError: invalid literal for int() with base 10: '${GITHUB_APP_ID}'`
- Node services: Runtime errors or undefined behavior
- App status: Deploy failed / Unhealthy

---

## 🔧 Immediate Fix (DO Dashboard)

### Step 1: Access Environment Variables

1. Go to: https://cloud.digitalocean.com/apps
2. Select the failing app (e.g., `pulser-hub-mcp` or `pulse-hub-web`)
3. Navigate to: **Settings** → **Environment Variables**

### Step 2: Fix Literal Placeholders

For each environment variable that shows a value like `${VARIABLE_NAME}`:

**❌ WRONG** (will crash):
```
Key: GITHUB_APP_ID
Value: ${GITHUB_APP_ID}
```

**✅ CORRECT**:
```
Key: GITHUB_APP_ID
Value: 2191216
```

**Common Variables to Check**:
- `GITHUB_APP_ID` → Set to `2191216` (numeric, no quotes)
- `GITHUB_CLIENT_ID` → Set to `Iv23liwGL7fnYySPPAjS`
- `GITHUB_WEBHOOK_SECRET` → Set to actual secret value
- `GITHUB_PRIVATE_KEY` → Set to actual PEM key content
- `ODOO_URL` → Set to actual Odoo instance URL
- `ODOO_DB`, `ODOO_USER`, `ODOO_PASSWORD` → Set to actual values

### Step 3: Save and Redeploy

1. Click **Save** after fixing values
2. DigitalOcean will automatically trigger a redeploy
3. Monitor deployment logs in **Activity** tab
4. Check health endpoint once deployed

---

## 📋 Verification

### Test Health Endpoints

**pulse-hub-web**:
```bash
curl -I https://pulse-hub-web-an645.ondigitalocean.app/health
# Expected: HTTP/2 200
```

**pulser-hub-mcp** (after Node migration is merged):
```bash
curl https://your-mcp-app.ondigitalocean.app/healthz
# Expected: {"ok":true,"service":"pulser-hub-mcp",...}
```

### Check Deployment Logs

```bash
# If you have doctl installed
doctl apps logs <APP_ID> --follow

# Look for:
# ✅ "Server listening on..."
# ✅ "Connected to..."
# ❌ "ValueError"
# ❌ "undefined"
```

---

## 🛡️ Prevention: App Spec Best Practices

### ❌ DO NOT Use Placeholders in app.yaml Values

**WRONG**:
```yaml
envs:
  - key: GITHUB_APP_ID
    value: "${GITHUB_APP_ID}"  # ❌ DO will pass this literally!
```

### ✅ Use One of These Approaches

**Option 1: Hardcode non-secret values** (recommended for app IDs):
```yaml
envs:
  - key: GITHUB_APP_ID
    value: "2191216"  # ✅ Actual value
```

**Option 2: Leave secrets blank in spec, set in dashboard**:
```yaml
envs:
  - key: GITHUB_WEBHOOK_SECRET
    scope: RUN_TIME
    type: SECRET
    value: ""  # ✅ Leave blank, set in DO dashboard
```

**Option 3: Use DO encrypted secrets** (for committed specs):
```yaml
envs:
  - key: GITHUB_CLIENT_SECRET
    scope: RUN_TIME
    type: SECRET
    value: EV[1:xxx...]  # ✅ DO encrypted value
```

### ⚠️ Note on Variable Interpolation

DigitalOcean App Platform **does not** interpolate shell-style `${VAR}` syntax in `value:` fields.
- Shell scripts (e.g., `build_command`) → `${VAR}` works ✅
- YAML `value:` fields → `${VAR}` passed literally ❌

---

## 🐍 Python: Add Robust Env Validation

For Python services, add this helper to prevent cryptic errors:

### Before (fragile):
```python
import os

GITHUB_APP_ID = int(os.getenv("GITHUB_APP_ID", "2191216"))
# ❌ Crashes with ValueError if set to "${GITHUB_APP_ID}"
```

### After (robust):
```python
import os
import sys

def require_int_env(name: str, default: str | None = None) -> int:
    """Get an integer environment variable with clear error messages."""
    raw = (os.getenv(name) or default or "").strip()

    if not raw:
        sys.exit(f"❌ {name} is required but not set. "
                 f"Set it in DigitalOcean: Apps → Settings → Environment Variables")

    if not raw.isdigit():
        sys.exit(f"❌ {name} must be an integer (got: '{raw}'). "
                 f"Check DigitalOcean dashboard for literal placeholders like '${{{name}}}'")

    return int(raw)

def require_string_env(name: str, default: str | None = None) -> str:
    """Get a string environment variable with clear error messages."""
    value = os.getenv(name) or default

    if not value:
        sys.exit(f"❌ {name} is required but not set. "
                 f"Set it in DigitalOcean: Apps → Settings → Environment Variables")

    # Warn if looks like a placeholder
    if value.startswith("${") and value.endswith("}"):
        sys.exit(f"❌ {name} is set to a placeholder ('{value}'). "
                 f"Replace with the actual value in DigitalOcean dashboard")

    return value

# Usage
GITHUB_APP_ID = require_int_env("GITHUB_APP_ID", "2191216")
GITHUB_WEBHOOK_SECRET = require_string_env("GITHUB_WEBHOOK_SECRET")
GITHUB_PRIVATE_KEY = require_string_env("GITHUB_PRIVATE_KEY")
```

---

## 🟢 Node/TypeScript: Add Env Validation

For Node/TypeScript services, add this helper:

### Create `src/env.ts`:
```typescript
function requireIntEnv(name: string, defaultValue?: string): number {
  const raw = (process.env[name] || defaultValue || '').trim();

  if (!raw) {
    console.error(`❌ ${name} is required but not set.`);
    console.error(`   Set it in DigitalOcean: Apps → Settings → Environment Variables`);
    process.exit(1);
  }

  const parsed = parseInt(raw, 10);
  if (isNaN(parsed)) {
    console.error(`❌ ${name} must be a number (got: '${raw}').`);
    console.error(`   Check DigitalOcean dashboard for literal placeholders like '\${${name}}'`);
    process.exit(1);
  }

  return parsed;
}

function requireStringEnv(name: string, defaultValue?: string): string {
  const value = process.env[name] || defaultValue;

  if (!value) {
    console.error(`❌ ${name} is required but not set.`);
    console.error(`   Set it in DigitalOcean: Apps → Settings → Environment Variables`);
    process.exit(1);
  }

  // Warn if looks like a placeholder
  if (value.startsWith('${') && value.endsWith('}')) {
    console.error(`❌ ${name} is set to a placeholder ('${value}').`);
    console.error(`   Replace with the actual value in DigitalOcean dashboard`);
    process.exit(1);
  }

  return value;
}

// Export validated environment variables
export const env = {
  GITHUB_APP_ID: requireIntEnv('GITHUB_APP_ID'),
  GITHUB_CLIENT_ID: requireStringEnv('GITHUB_CLIENT_ID'),
  GITHUB_CLIENT_SECRET: requireStringEnv('GITHUB_CLIENT_SECRET'),
  GITHUB_WEBHOOK_SECRET: requireStringEnv('GITHUB_WEBHOOK_SECRET'),
  PORT: parseInt(process.env.PORT || '3000', 10),
};
```

### Usage in `src/index.ts`:
```typescript
import { env } from './env.js';

console.log(`GitHub App ID: ${env.GITHUB_APP_ID}`);
// If env vars are wrong, app will exit immediately with clear error message
```

---

## 📊 Current App Status

### pulse-hub-web
- **Status**: ✅ Likely OK (uses Node/TypeScript, handles envs correctly)
- **Health**: https://pulse-hub-web-an645.ondigitalocean.app/health
- **Env Vars in Spec**: All set to actual values (lines 37-53 in infra/do/pulse-hub-web.yaml)

### pulser-hub-mcp
- **Status**: ⚠️ Was Python (would crash), migrating to Node/TypeScript
- **Fix**: Migration to Node/TypeScript in PR (removes Python `int()` issue)
- **Required Envs**: ODOO_* (not GITHUB_*) after migration

### Key Insight
The MCP server migration from Python to Node/TypeScript (in current PR) automatically fixes the `int("${GITHUB_APP_ID}")` crash because:
1. Old code: `int(os.getenv("GITHUB_APP_ID"))` → crashes on placeholder
2. New code: Uses ODOO_* env vars, not GITHUB_*
3. New code is TypeScript with better error handling

---

## 🎯 Action Items

### Immediate (if app is currently crashing)
1. [ ] Check DO dashboard for environment variables with `${...}` placeholders
2. [ ] Replace all placeholders with actual values
3. [ ] Save and wait for automatic redeploy
4. [ ] Verify health endpoints return 200

### Short-term (after MCP migration is merged)
1. [ ] Remove GITHUB_* env vars from MCP server (now uses ODOO_*)
2. [ ] Set ODOO_* env vars in DO dashboard for MCP server
3. [ ] Add env validation helpers to all services
4. [ ] Document required env vars in each service's README

### Long-term (best practices)
1. [ ] Use DO encrypted secrets (EV[...]) for all secrets in committed specs
2. [ ] Add pre-deploy validation script that checks for placeholders
3. [ ] Create environment variable checklist for each service
4. [ ] Add monitoring/alerts for startup failures

---

## 🔍 Troubleshooting Checklist

- [ ] All env vars set in DO dashboard (not just in YAML)
- [ ] No `${...}` placeholders in env var values
- [ ] Numeric vars (like GITHUB_APP_ID) have no quotes around numbers
- [ ] Secret vars marked with `type: SECRET` and proper scope
- [ ] Health endpoint returns 200 after deploy
- [ ] Runtime logs show no "undefined" or "ValueError" errors

---

**Last Updated**: November 2, 2025
**Related PR**: MCP Server Python → Node/TypeScript Migration
