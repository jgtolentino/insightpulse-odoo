# Google OAuth SSO Setup Guide - InsightPulse AI

**Last Updated:** 2025-11-09
**Target Environment:** Odoo 18 CE on DigitalOcean Droplet (165.227.10.178)
**Primary Domain:** erp.insightpulseai.net
**Session Cookie Domain:** `.insightpulseai.net` (cross-subdomain SSO)

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Google Cloud Console Setup](#phase-1-google-cloud-console-setup)
4. [Phase 2: Odoo OAuth Configuration](#phase-2-odoo-oauth-configuration)
5. [Phase 3: Nginx Configuration](#phase-3-nginx-configuration)
6. [Phase 4: Service-Specific OAuth Integration](#phase-4-service-specific-oauth-integration)
7. [Testing & Validation](#testing--validation)
8. [Troubleshooting](#troubleshooting)
9. [Security Considerations](#security-considerations)

---

## Overview

This guide configures **unified Google OAuth SSO** across all InsightPulse AI services:

- **erp.insightpulseai.net** - Odoo 18 CE (primary authentication service)
- **superset.insightpulseai.net** - Apache Superset analytics
- **mcp.insightpulseai.net** - MCP Coordinator (Next.js)
- **n8n.insightpulseai.net** - n8n workflow automation
- **chat.insightpulseai.net** - Mattermost team chat

### Architecture

```
User → Google OAuth → erp.insightpulseai.net (Odoo) → Session Cookie (.insightpulseai.net)
                           ↓
         All services share session via cookie domain
```

**Key Benefits:**
- ✅ Single sign-on across all subdomains
- ✅ Centralized user management in Odoo
- ✅ No password management (Google handles authentication)
- ✅ Multi-factor authentication via Google

---

## Prerequisites

### Required Information

1. **Google Workspace Account** (admin access for OAuth client creation)
2. **Odoo Admin Credentials** (for database configuration)
3. **Supabase PostgreSQL Access** (for direct database configuration)
4. **SSH Access to Droplet** (165.227.10.178 for Nginx configuration)

### Environment Variables

Export these before running automation scripts:

```bash
# Supabase PostgreSQL (spdtwktxdalcfigzeqrz)
export POSTGRES_HOST="db.spdtwktxdalcfigzeqrz.supabase.co"
export POSTGRES_PORT="5432"
export POSTGRES_USER="postgres.spdtwktxdalcfigzeqrz"
export POSTGRES_PASSWORD="SHWYXDMFAwXI1drT"
export POSTGRES_DB="postgres"

# Google OAuth Credentials (from GCP Console)
export GOOGLE_CLIENT_ID="YOUR_CLIENT_ID_HERE"
export GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET_HERE"

# Odoo Configuration
export ODOO_ADMIN_EMAIL="jgtolentino_rn@yahoo.com"
export SESSION_COOKIE_DOMAIN=".insightpulseai.net"
```

---

## Phase 1: Google Cloud Console Setup

### Step 1.1: Create OAuth Client ID

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Select or create a project: **InsightPulse AI**
3. Click **Create Credentials** → **OAuth client ID**
4. Choose application type: **Web application**
5. Name: `InsightPulse AI - Unified SSO`

### Step 1.2: Configure Authorized Redirect URIs

Add these exact URIs (order matters for Odoo):

```
https://erp.insightpulseai.net/auth_oauth/signin
https://superset.insightpulseai.net/oauth-authorized/google
https://mcp.insightpulseai.net/api/auth/callback/google
https://n8n.insightpulseai.net/rest/oauth2-credential/callback
https://chat.insightpulseai.net/oauth/google/complete
```

### Step 1.3: Obtain Credentials

1. Click **Create**
2. Copy **Client ID** (format: `xxxxx.apps.googleusercontent.com`)
3. Copy **Client Secret** (format: `GOCSPX-xxxxx`)
4. Store securely (you'll need these for automation scripts)

### Step 1.4: Configure OAuth Consent Screen

1. Go to **OAuth consent screen** in GCP Console
2. User Type: **Internal** (if using Google Workspace) or **External**
3. App name: `InsightPulse AI`
4. User support email: `jgtolentino_rn@yahoo.com`
5. Authorized domains: `insightpulseai.net`
6. Scopes: `openid`, `email`, `profile`
7. Save and continue

---

## Phase 2: Odoo OAuth Configuration

### Method 1: Automated Setup (Recommended)

Run the automation script:

```bash
cd /Users/tbwa/Documents/GitHub/insightpulse-odoo

# Export credentials first
export GOOGLE_CLIENT_ID="your-client-id-here"
export GOOGLE_CLIENT_SECRET="your-client-secret-here"

# Run automated setup
chmod +x infra/oauth/setup_oauth.sh
./infra/oauth/setup_oauth.sh
```

**Expected Output:**

```
=== Google OAuth Setup for InsightPulse AI ===

✅ Configuration validated
Postgres Host: db.spdtwktxdalcfigzeqrz.supabase.co
Postgres DB: postgres
Google Client ID: 123456789012-abc...
Session Cookie Domain: .insightpulseai.net

📦 Step 1: Enabling auth_oauth module...
✅ auth_oauth module enabled

🔐 Step 2: Configuring Google OAuth provider...
✅ Google OAuth provider configured

⚙️  Step 3: Configuring system parameters...
✅ System parameters configured

🔍 Step 4: Verifying configuration...
✅ OAuth configuration verified successfully

Next steps:
1. Restart Odoo service: sudo systemctl restart odoo
2. Update Nginx configuration: sudo cp infra/oauth/nginx_oauth.conf /etc/nginx/conf.d/
3. Reload Nginx: sudo nginx -t && sudo systemctl reload nginx
4. Test OAuth login at: https://erp.insightpulseai.net/web/login

=== OAuth Setup Complete ===
```

### Method 2: Manual Setup

#### Step 2.1: Enable auth_oauth Module

```sql
-- Connect to Supabase PostgreSQL
psql "postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres?sslmode=require"

-- Enable auth_oauth module
UPDATE ir_module_module
SET state = 'installed'
WHERE name = 'auth_oauth';

-- Verify
SELECT name, state FROM ir_module_module WHERE name = 'auth_oauth';
```

#### Step 2.2: Configure Google OAuth Provider

Edit `infra/oauth/odoo_oauth_setup.sql` and replace placeholders:

```sql
-- Replace these lines with actual values:
client_id = 'YOUR_GOOGLE_CLIENT_ID',  -- Your actual Client ID
-- AND
client_secret = 'YOUR_GOOGLE_CLIENT_SECRET',  -- Your actual Client Secret
```

Then execute:

```bash
psql "$POSTGRES_URL" < infra/oauth/odoo_oauth_setup.sql
```

#### Step 2.3: Configure System Parameters

```sql
-- Set base URL
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('web.base.url', 'https://erp.insightpulseai.net', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Configure session cookie domain (critical for cross-subdomain SSO)
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('session_cookie_domain', '.insightpulseai.net', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Set session cookie secure flag (required for OAuth)
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('session_cookie_secure', 'true', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Set session cookie SameSite policy (required for cross-site cookies)
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('session_cookie_samesite', 'None', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;

-- Enable OAuth authorization header
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('auth_oauth.authorization_header', 'true', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
```

#### Step 2.4: Restart Odoo Service

SSH to droplet and restart:

```bash
ssh root@165.227.10.178

# Restart Odoo
sudo systemctl restart odoo

# Verify service is running
sudo systemctl status odoo

# Check logs for OAuth initialization
sudo journalctl -u odoo -f | grep -i oauth
```

---

## Phase 3: Nginx Configuration

### Step 3.1: Deploy OAuth-Enabled Nginx Config

SSH to droplet:

```bash
ssh root@165.227.10.178

# Backup existing config
sudo cp /etc/nginx/conf.d/odoo.conf /etc/nginx/conf.d/odoo.conf.backup

# Copy new OAuth config
sudo cp /root/insightpulse-odoo/infra/oauth/nginx_oauth.conf /etc/nginx/conf.d/odoo.conf

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 3.2: Verify SSL Certificates

Ensure wildcard or SAN certificate covers all subdomains:

```bash
# Check certificate domains
sudo certbot certificates

# If renewal needed:
sudo certbot renew --dry-run
```

**Expected Certificate Subject Alternative Names:**
- `erp.insightpulseai.net`
- `superset.insightpulseai.net`
- `mcp.insightpulseai.net`
- `n8n.insightpulseai.net`
- `chat.insightpulseai.net`

Or use wildcard: `*.insightpulseai.net`

---

## Phase 4: Service-Specific OAuth Integration

### 4.1: Apache Superset (superset.insightpulseai.net)

Edit `superset/superset_config.py`:

```python
from flask_appbuilder.security.manager import AUTH_OAUTH

AUTH_TYPE = AUTH_OAUTH

OAUTH_PROVIDERS = [
    {
        'name': 'google',
        'icon': 'fa-google',
        'token_key': 'access_token',
        'remote_app': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
            'api_base_url': 'https://www.googleapis.com/oauth2/v2/',
            'client_kwargs': {
                'scope': 'openid email profile'
            },
            'request_token_url': None,
            'access_token_url': 'https://accounts.google.com/o/oauth2/token',
            'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
            'authorize_params': {
                'hd': 'insightpulseai.net'  # Restrict to your domain
            }
        }
    }
]

# Session cookie settings for cross-subdomain SSO
SESSION_COOKIE_DOMAIN = '.insightpulseai.net'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_HTTPONLY = True
```

Restart Superset:

```bash
docker-compose -f superset/docker-compose.yml restart
```

### 4.2: MCP Coordinator (mcp.insightpulseai.net)

Configure NextAuth.js Google provider in `.env.local`:

```bash
# Google OAuth
GOOGLE_CLIENT_ID="your-client-id-here"
GOOGLE_CLIENT_SECRET="your-client-secret-here"

# NextAuth configuration
NEXTAUTH_URL="https://mcp.insightpulseai.net"
NEXTAUTH_SECRET="generate-random-secret-here"

# Session cookie settings
NEXTAUTH_URL_INTERNAL="http://localhost:3000"
```

Update `pages/api/auth/[...nextauth].ts`:

```typescript
import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"

export default NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  session: {
    strategy: "jwt",
  },
  cookies: {
    sessionToken: {
      name: `__Secure-next-auth.session-token`,
      options: {
        httpOnly: true,
        sameSite: 'none',
        path: '/',
        secure: true,
        domain: '.insightpulseai.net',
      },
    },
  },
})
```

### 4.3: n8n Workflow Automation (n8n.insightpulseai.net)

Configure Google OAuth2 credential in n8n UI:

1. Go to **Settings** → **Credentials** → **New**
2. Credential type: **Google OAuth2 API**
3. Name: `Google SSO`
4. Client ID: `your-client-id-here`
5. Client Secret: `your-client-secret-here`
6. Scope: `openid email profile`
7. Authorization URL: `https://accounts.google.com/o/oauth2/auth`
8. Access Token URL: `https://accounts.google.com/o/oauth2/token`
9. Save

### 4.4: Mattermost Team Chat (chat.insightpulseai.net)

Configure GitLab OAuth (compatible with Google OAuth2) in `config/config.json`:

```json
{
  "GitLabSettings": {
    "Enable": true,
    "Secret": "your-google-client-secret-here",
    "Id": "your-google-client-id-here",
    "Scope": "openid email profile",
    "AuthEndpoint": "https://accounts.google.com/o/oauth2/auth",
    "TokenEndpoint": "https://accounts.google.com/o/oauth2/token",
    "UserApiEndpoint": "https://www.googleapis.com/oauth2/v1/userinfo"
  },
  "ServiceSettings": {
    "SiteURL": "https://chat.insightpulseai.net",
    "SessionCookieName": "MMSID",
    "SessionCookieDomain": ".insightpulseai.net"
  }
}
```

Restart Mattermost:

```bash
sudo systemctl restart mattermost
```

---

## Testing & Validation

### Test 1: Odoo OAuth Login

1. Navigate to: `https://erp.insightpulseai.net/web/login`
2. Look for **"Sign in with Google"** button
3. Click and authenticate with Google account
4. Verify redirect to Odoo dashboard
5. Check session cookie in browser DevTools:
   - Name: `session_id`
   - Domain: `.insightpulseai.net`
   - Secure: `true`
   - SameSite: `None`

### Test 2: Cross-Subdomain Session Persistence

1. Log in to `erp.insightpulseai.net` with Google OAuth
2. Open new tab: `https://superset.insightpulseai.net`
3. Verify automatic login (session shared)
4. Open another tab: `https://mcp.insightpulseai.net`
5. Verify automatic login

### Test 3: Session Timeout

1. Log in to any service
2. Wait for session timeout (default: 1 hour)
3. Verify automatic redirect to Google OAuth
4. Verify re-authentication required

### Test 4: Multi-Device Login

1. Log in on desktop browser
2. Log in on mobile browser
3. Verify both sessions active
4. Log out on desktop
5. Verify mobile session still active (independent sessions)

---

## Troubleshooting

### Issue: "Sign in with Google" button not showing

**Symptoms:**
- OAuth button missing on `/web/login` page

**Solutions:**

1. **Verify auth_oauth module is installed:**
   ```sql
   SELECT name, state FROM ir_module_module WHERE name = 'auth_oauth';
   -- Expected: state = 'installed'
   ```

2. **Check OAuth provider configuration:**
   ```sql
   SELECT name, enabled, client_id FROM auth_oauth_provider WHERE name = 'Google';
   -- Expected: enabled = true, client_id populated
   ```

3. **Restart Odoo:**
   ```bash
   sudo systemctl restart odoo
   ```

4. **Check browser console for JavaScript errors:**
   - Open DevTools → Console
   - Look for errors related to OAuth

### Issue: "redirect_uri_mismatch" error

**Symptoms:**
- Google shows error: "Error 400: redirect_uri_mismatch"

**Solutions:**

1. **Verify redirect URI in GCP Console:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Check authorized redirect URIs include: `https://erp.insightpulseai.net/auth_oauth/signin`

2. **Check Odoo base URL:**
   ```sql
   SELECT key, value FROM ir_config_parameter WHERE key = 'web.base.url';
   -- Expected: value = 'https://erp.insightpulseai.net'
   ```

3. **Verify Nginx proxy headers:**
   ```bash
   sudo nginx -T | grep proxy_set_header
   # Should include:
   #   proxy_set_header X-Forwarded-Proto $scheme;
   #   proxy_set_header Host $host;
   ```

### Issue: Session not shared across subdomains

**Symptoms:**
- Login works on `erp.insightpulseai.net`
- Other subdomains require separate login

**Solutions:**

1. **Verify session cookie domain:**
   ```sql
   SELECT key, value FROM ir_config_parameter WHERE key = 'session_cookie_domain';
   -- Expected: value = '.insightpulseai.net' (note the leading dot)
   ```

2. **Check browser cookie in DevTools:**
   - Domain should be: `.insightpulseai.net`
   - SameSite should be: `None`
   - Secure should be: `true`

3. **Verify SSL certificates:**
   ```bash
   sudo certbot certificates
   # All subdomains must have valid SSL certificates
   ```

4. **Restart Odoo and Nginx:**
   ```bash
   sudo systemctl restart odoo
   sudo systemctl reload nginx
   ```

### Issue: "invalid_client" error

**Symptoms:**
- Google shows error: "Error 401: invalid_client"

**Solutions:**

1. **Verify client secret is correct:**
   ```sql
   SELECT client_secret FROM auth_oauth_provider_data
   WHERE provider_id = (SELECT id FROM auth_oauth_provider WHERE name = 'Google');
   ```

2. **Re-run setup script with correct credentials:**
   ```bash
   export GOOGLE_CLIENT_SECRET="correct-secret-here"
   ./infra/oauth/setup_oauth.sh
   ```

### Issue: Infinite redirect loop

**Symptoms:**
- Browser keeps redirecting between Odoo and Google
- URL changes rapidly

**Solutions:**

1. **Clear browser cookies:**
   - DevTools → Application → Cookies → Clear all

2. **Check Nginx proxy configuration:**
   ```bash
   sudo nginx -T | grep proxy_redirect
   # Should be: proxy_redirect off;
   ```

3. **Verify no conflicting session cookies:**
   ```bash
   # Check for multiple session cookies with different domains
   # Should only have one session_id cookie with domain .insightpulseai.net
   ```

### Debug Mode

Enable Odoo debug mode for detailed OAuth logs:

```bash
# Edit Odoo config
sudo nano /etc/odoo/odoo.conf

# Add or update:
log_level = debug
log_handler = odoo.addons.auth_oauth:DEBUG

# Restart Odoo
sudo systemctl restart odoo

# Watch logs
sudo journalctl -u odoo -f | grep -i oauth
```

---

## Security Considerations

### 1. Client Secret Protection

**DO:**
- Store client secret in environment variables
- Use Supabase Vault for production secrets
- Never commit client secret to git

**DON'T:**
- Hardcode client secret in config files
- Share client secret in Slack/email
- Store client secret in frontend code

### 2. Session Cookie Security

**Enforced Settings:**
- `HttpOnly: true` - Prevents JavaScript access
- `Secure: true` - HTTPS only
- `SameSite: None` - Required for cross-site cookies (but requires HTTPS)
- `Domain: .insightpulseai.net` - Cross-subdomain sharing

### 3. Google OAuth Consent Screen

**Best Practices:**
- Use "Internal" user type if using Google Workspace
- Restrict to specific Google domain (`hd: insightpulseai.net`)
- Minimize requested scopes (only `openid email profile`)
- Display privacy policy URL

### 4. Nginx Security Headers

**Required Headers:**
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 5. Regular Security Audits

**Checklist:**
- [ ] Rotate client secret every 90 days
- [ ] Review authorized users monthly
- [ ] Monitor OAuth login failures
- [ ] Check for unauthorized redirect URIs
- [ ] Verify SSL certificate validity

### 6. Incident Response Plan

**If client secret compromised:**

1. **Immediate Actions:**
   ```bash
   # Revoke old credentials in GCP Console
   # Generate new client ID and secret
   # Update all services with new credentials
   ```

2. **Rotate Credentials:**
   ```bash
   export GOOGLE_CLIENT_ID="new-client-id"
   export GOOGLE_CLIENT_SECRET="new-secret"
   ./infra/oauth/setup_oauth.sh
   ```

3. **Force Logout All Users:**
   ```sql
   -- Clear all active sessions
   DELETE FROM ir_session;
   ```

4. **Notify Users:**
   - Send email about security incident
   - Require re-authentication

---

## Next Steps

After successful OAuth setup:

1. **Configure Additional Services:**
   - See `docs/MODULE_INSTALLATION_GUIDE.md` for Odoo modules
   - See `docs/INFRASTRUCTURE_ARCHITECTURE.md` for full architecture

2. **Enable Multi-Factor Authentication:**
   - Configure Google Workspace MFA
   - All users will inherit MFA from Google

3. **Monitor OAuth Usage:**
   ```sql
   -- Check OAuth login activity
   SELECT
     u.login,
     u.create_date AS first_login,
     MAX(s.create_date) AS last_login
   FROM res_users u
   LEFT JOIN ir_session s ON s.user_id = u.id
   WHERE u.oauth_provider_id IS NOT NULL
   GROUP BY u.id
   ORDER BY last_login DESC;
   ```

4. **Backup Configuration:**
   ```bash
   # Export OAuth configuration
   pg_dump "$POSTGRES_URL" \
     --table=auth_oauth_provider \
     --table=auth_oauth_provider_data \
     --table=ir_config_parameter \
     > oauth_config_backup_$(date +%Y%m%d).sql
   ```

---

## References

- [Odoo 18 CE Authentication Documentation](https://www.odoo.com/documentation/18.0/administration/on_premise/deploy.html#authentication)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Nginx Reverse Proxy Best Practices](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)

---

**Maintainer:** InsightPulse AI Team
**Support:** jgtolentino_rn@yahoo.com
**Last Tested:** 2025-11-09 with Odoo 18 CE
