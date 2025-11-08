# Google OAuth Setup - InsightPulse AI

**Last Updated:** 2025-11-08
**Status:** ✅ Configured and Ready
**Test URL:** https://erp.insightpulseai.net/web/login

---

## ✅ Configuration Complete

Google OAuth has been configured with the following credentials:

**Client ID:**
```
[CONFIGURED - See ir_config_parameter table or contact administrator]
```

**Client Secret:**
```
[CONFIGURED - Stored securely in database]
```

**Redirect URI:**
```
https://erp.insightpulseai.net/auth_oauth/signin
```

**Note:** OAuth credentials are stored securely in the database and not version controlled for security.

---

## 🌐 Google Cloud Console Configuration

### Required Settings in Google Cloud Console

Go to: https://console.cloud.google.com/apis/credentials

**OAuth 2.0 Client Configuration:**

```yaml
Application type: Web application
Name: InsightPulse AI - Unified SSO

Authorized JavaScript origins:
  - https://insightpulseai.net
  - https://erp.insightpulseai.net
  - https://superset.insightpulseai.net
  - https://mcp.insightpulseai.net
  - https://n8n.insightpulseai.net
  - https://chat.insightpulseai.net

Authorized redirect URIs:
  - https://erp.insightpulseai.net/auth_oauth/signin
  - https://erp.insightpulseai.net/web/login
  - https://insightpulseai.net/auth_oauth/signin
```

---

## 🔧 Odoo Configuration (Applied)

### Database Configuration

**OAuth Provider: Google OAuth2**
- Enabled: ✅ Yes
- Client ID: Configured
- Auth Endpoint: https://accounts.google.com/o/oauth2/v2/auth
- Scope: openid email profile
- Validation Endpoint: https://www.googleapis.com/oauth2/v1/tokeninfo
- Data Endpoint: https://www.googleapis.com/oauth2/v1/userinfo

**System Parameters:**
- web.base.url: https://erp.insightpulseai.net
- auth_oauth.client_secret_3: (Stored securely)

### Session Cookie Configuration

**Unified SSO Cookies (odoo.conf):**
```ini
session_cookie_domain = .insightpulseai.net
session_cookie_secure = True
session_cookie_httponly = True
session_cookie_samesite = Lax
```

This allows session sharing across ALL subdomains:
- erp.insightpulseai.net
- superset.insightpulseai.net
- mcp.insightpulseai.net
- n8n.insightpulseai.net
- chat.insightpulseai.net

---

## 🧪 Testing

### Test Login Flow

1. **Navigate to:** https://erp.insightpulseai.net/web/login

2. **Look for:** "Sign in with Google" button

3. **Click and authorize:** Should redirect to Google OAuth consent screen

4. **After authorization:** Should be logged into Odoo ERP

### Expected Behavior

✅ **First-time login:**
- Google authorization screen appears
- User grants permission to InsightPulse AI
- User is created in Odoo automatically
- Logged into ERP dashboard

✅ **Subsequent logins:**
- Click "Sign in with Google"
- Immediately logged in (no consent screen)
- Session cookie set for .insightpulseai.net

✅ **Cross-subdomain SSO:**
- Login at erp.insightpulseai.net
- Visit superset.insightpulseai.net
- Already authenticated (no login required)

---

## 🐛 Troubleshooting

### Issue: "Sign in with Google" button not showing

**Possible causes:**
1. OAuth provider not enabled in database
2. Template cache issue
3. JavaScript not loading

**Fix:**
```bash
# Check OAuth provider status
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -c \
  "SELECT name, enabled, client_id FROM auth_oauth_provider WHERE name = 'Google OAuth2';"

# Should show: enabled = t, client_id = 813089342312-...

# Clear assets cache
docker exec insightpulse-odoo-odoo-1 odoo -d odoo19 --stop-after-init

# Restart Odoo
docker restart insightpulse-odoo-odoo-1
```

### Issue: OAuth redirect error

**Error:** `redirect_uri_mismatch`

**Fix:** Verify in Google Cloud Console that redirect URI **exactly** matches:
```
https://erp.insightpulseai.net/auth_oauth/signin
```

**Common mistakes:**
- ❌ Missing trailing slash: `/auth_oauth/signin/`
- ❌ HTTP instead of HTTPS: `http://erp.insightpulseai.net`
- ❌ Wrong subdomain: `www.erp.insightpulseai.net`

### Issue: User creation fails

**Error:** User exists but can't log in via OAuth

**Fix:** Check user email in Odoo matches Google account:
```bash
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -c \
  "SELECT login, email, oauth_provider_id FROM res_users WHERE oauth_provider_id = 3;"
```

### Issue: Session not shared across subdomains

**Check:**
```bash
# Verify session cookie domain
docker exec insightpulse-odoo-odoo-1 grep session_cookie_domain /etc/odoo/odoo.conf

# Should show: session_cookie_domain = .insightpulseai.net
```

**Important:** Domain MUST start with a dot (`.insightpulseai.net`)

---

## 🔒 Security Notes

### OAuth Security

- ✅ Uses HTTPS for all redirects
- ✅ Validates OAuth state parameter
- ✅ Checks OAuth provider endpoint (accounts.google.com)
- ✅ Validates user email before creating account

### Session Security

- ✅ HttpOnly cookies (not accessible via JavaScript)
- ✅ Secure flag (only sent over HTTPS)
- ✅ SameSite=Lax (CSRF protection)
- ✅ Domain-scoped cookies

### Credentials Storage

- ✅ Client secret stored in `ir.config_parameter` (database)
- ❌ NOT stored in version control
- ❌ NOT visible in Odoo UI logs

---

## 📚 Additional Configuration

### Allow Google Workspace Domain Only

To restrict login to specific Google Workspace domain:

```bash
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 << SQL
INSERT INTO ir_config_parameter (key, value)
VALUES ('auth_oauth.google_domain', 'insightpulseai.net')
ON CONFLICT (key) DO UPDATE SET value = 'insightpulseai.net';
SQL
```

### Auto-create Users on First Login

Enable automatic user creation (already enabled):

```bash
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 << SQL
UPDATE auth_oauth_provider
SET body = 'allow_signup'
WHERE name = 'Google OAuth2';
SQL
```

### Set Default User Groups

Assign default groups to OAuth users:

```bash
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 << SQL
-- Get internal user group ID
SELECT id, name FROM res_groups WHERE name = 'Internal User';

-- Assign to OAuth users on creation (requires custom module)
SQL
```

---

## 🚀 Next Steps

After OAuth is working:

1. **Test SSO across subdomains**
   - Login at erp.insightpulseai.net
   - Visit superset.insightpulseai.net
   - Verify auto-authentication

2. **Configure other services**
   - Apache Superset OAuth
   - n8n OAuth
   - Mattermost OAuth

3. **Enable 2FA** (recommended)
   - Install `auth_totp` module
   - Require 2FA for admin users

4. **Audit permissions**
   - Review user access levels
   - Set up role-based access control
   - Document security policies

---

## 📊 Monitoring

### Check OAuth Usage

```bash
# Count OAuth users
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -c \
  "SELECT COUNT(*) FROM res_users WHERE oauth_provider_id = 3;"

# List OAuth users
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -c \
  "SELECT login, email, create_date FROM res_users WHERE oauth_provider_id = 3 ORDER BY create_date DESC LIMIT 10;"
```

### Check Session Activity

```bash
# Active sessions
docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -c \
  "SELECT COUNT(DISTINCT sid) FROM ir_sessions WHERE expiry > NOW();"
```

---

## 🔗 Resources

- **Google OAuth Docs:** https://developers.google.com/identity/protocols/oauth2
- **Odoo OAuth Docs:** https://www.odoo.com/documentation/18.0/developer/reference/backend/oauth.html
- **Odoo Security:** https://www.odoo.com/documentation/18.0/administration/odoo_online/security.html

---

**Support:** jgtolentino_rn@yahoo.com
**Repository:** https://github.com/jgtolentino/insightpulse-odoo
**Issues:** https://github.com/jgtolentino/insightpulse-odoo/issues
