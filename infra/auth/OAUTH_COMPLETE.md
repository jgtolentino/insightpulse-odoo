# ✅ OAuth/OIDC Configuration - COMPLETE

**Date**: 2025-11-11 15:30 UTC
**Status**: Odoo ✅ | Mattermost ✅ | Superset ⏳

---

## Overview

Single Sign-On (SSO) infrastructure is **fully operational** for Odoo and Mattermost, with Superset configuration ready for deployment.

### Keycloak Identity Provider
- **URL**: https://auth.insightpulseai.net
- **Realm**: insightpulse
- **SSL**: Let's Encrypt (expires 2026-02-09)
- **Status**: ✅ Production Ready

### Databases
- **Odoo Databases**: 2 (insightpulse, postgres)
- **Active Database**: insightpulse (OAuth configured ✅)

---

## 1. Odoo OAuth ✅ COMPLETE

### Configuration Status
- **Provider ID**: 5
- **Provider Name**: Keycloak SSO
- **Database**: insightpulse
- **Button Text**: "Sign in with Keycloak SSO"
- **Status**: ✅ Complete and Verified

### Access URLs
- Main Login: https://erp.insightpulseai.net/web/login
- Discuss: https://erp.insightpulseai.net/odoo/discuss

### OAuth Details
```yaml
Client ID: odoo-erp
Client Secret: rJEXkppNKG5R9GmguCql9DyRILKYZbqv
Auth Endpoint: https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/auth
Token Endpoint: https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/token
UserInfo Endpoint: https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/userinfo
Scope: openid email profile
```

### Redirect URIs (Keycloak)
- `https://erp.insightpulseai.net/*`
- `https://erp.insightpulseai.net/auth_oauth/signin`

### Testing
1. Go to https://erp.insightpulseai.net/web/login
2. Click **"Sign in with Keycloak SSO"** button
3. Login with: jgtolentino_rn@yahoo.com
4. Redirects back to Odoo as authenticated user

---

## 2. Mattermost OIDC ✅ COMPLETE

### Configuration Status
- **Method**: mmctl CLI
- **Status**: ✅ Configured

### Access URL
- Login: https://chat.insightpulseai.net

### OIDC Details
```yaml
Client ID: mattermost-chat
Client Secret: IO62ksIybTPBQ8QzbfZP8537gEdco30H
Discovery URL: https://auth.insightpulseai.net/realms/insightpulse/.well-known/openid-configuration
Button Text: "Sign in with Keycloak"
```

### Redirect URIs (Keycloak)
- `https://chat.insightpulseai.net/*`

### Testing
1. Go to https://chat.insightpulseai.net
2. Click **"Sign in with Keycloak"** button
3. Login with: jgtolentino_rn@yahoo.com
4. Redirects back to Mattermost as authenticated user

---

## 3. Superset OAuth ⏳ PENDING DEPLOYMENT

### Configuration Status
- **Status**: ⏳ Configuration file ready, awaiting DigitalOcean deployment
- **File**: `/opt/insightpulse-sso/superset_oauth_config.py` on server

### Access URL
- Login: https://superset-nlavf.ondigitalocean.app/login/

### OAuth Details
```yaml
Client ID: superset-analytics
Client Secret: AWETv9z3tpgyfPGSwj7tdNP1lmg589Ra
Auth Endpoint: https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/auth
Token Endpoint: https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/token
UserInfo Endpoint: https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/userinfo
```

### Redirect URIs (Keycloak)
- `https://superset-nlavf.ondigitalocean.app/oauth-authorized/keycloak`

### Deployment Steps
1. Access DigitalOcean App Platform Superset deployment
2. Copy `/opt/insightpulse-sso/superset_oauth_config.py` to deployment
3. Append or merge into existing `superset_config.py`
4. Ensure `AUTH_TYPE = AUTH_OAUTH` is set
5. Restart Superset application
6. Test at: https://superset-nlavf.ondigitalocean.app/login/

---

## 4. Test User Account

**Created**: 2025-11-11 15:18 UTC

```yaml
Username: jgtolentino_rn
Email: jgtolentino_rn@yahoo.com
User ID: a528c149-3b24-4ac0-a965-95103a22fae5
First Name: Jake
Last Name: Tolentino
Email Verified: Yes
Enabled: Yes
Temporary Password: ChangeMe123!
Required Action: UPDATE_PASSWORD (on first login)
```

### First Login Steps
1. Go to https://auth.insightpulseai.net
2. Click "Sign in"
3. Enter username: `jgtolentino_rn` and password: `ChangeMe123!`
4. Set new permanent password when prompted
5. After password change, can use SSO across all applications

---

## 5. Keycloak Endpoints Reference

### InsightPulse Realm Endpoints

| Endpoint | URL |
|----------|-----|
| **Authorization** | https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/auth |
| **Token** | https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/token |
| **UserInfo** | https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/userinfo |
| **Logout** | https://auth.insightpulseai.net/realms/insightpulse/protocol/openid-connect/logout |
| **OIDC Discovery** | https://auth.insightpulseai.net/realms/insightpulse/.well-known/openid-configuration |
| **Admin Console** | https://auth.insightpulseai.net/admin/ |

---

## 6. User Management

### Create Users via Admin Console
1. Go to: https://auth.insightpulseai.net/admin/
2. Login: admin / AdminPass2025
3. Select: **InsightPulse** realm (dropdown top-left)
4. Navigate: Users → Create new user
5. Fill in: Username, Email, First Name, Last Name
6. Set: Email Verified: ON, Enabled: ON
7. Click: Create
8. Navigate: Credentials tab → Set Password
9. Enter password, disable "Temporary" if permanent

### Create Users via CLI
```bash
ssh root@165.227.10.178
source /opt/insightpulse-sso/sso-credentials.sh

TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$KEYCLOAK_ADMIN_USER" \
  -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | jq -r '.access_token')

curl -X POST "$KEYCLOAK_URL/admin/realms/$KEYCLOAK_REALM/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "firstName": "First",
    "lastName": "Last",
    "enabled": true,
    "emailVerified": true,
    "credentials": [{
      "type": "password",
      "value": "SecurePassword123!",
      "temporary": true
    }]
  }'
```

---

## 7. Security

### Credentials Storage
- **Location**: `/opt/insightpulse-sso/sso-credentials.sh` (chmod 600)
- **Contents**: All OAuth client IDs and secrets
- **Access**: Root user only

### SSL/TLS
- **Certificate**: Let's Encrypt
- **Expires**: 2026-02-09
- **Auto-Renewal**: Configured via certbot

### Session Management
- **Backend**: Redis (sso-redis container)
- **Cookie**: KEYCLOAK_SESSION
- **Token Lifespan**: 3600 seconds (1 hour)

---

## 8. Troubleshooting

### Odoo SSO Button Not Appearing
```bash
# Restart Odoo
ssh root@165.227.10.178 'docker restart odoo19'

# Wait for restart
sleep 15

# Check browser at: https://erp.insightpulseai.net/web/login
```

### Mattermost SSO Button Not Appearing
```bash
# Check OIDC settings
docker exec mattermost-mattermost-1 mmctl --local config get OpenIdSettings

# Restart Mattermost
docker restart mattermost-mattermost-1
```

### Keycloak Issues
```bash
# Check status
ssh root@165.227.10.178 'docker ps | grep keycloak'

# Check logs
ssh root@165.227.10.178 'docker logs sso-keycloak --tail 100'

# Restart if needed
ssh root@165.227.10.178 'docker restart sso-keycloak'
```

---

## 9. Quick Commands

### Check SSO Status
```bash
# Test Keycloak HTTPS
curl -I https://auth.insightpulseai.net/realms/insightpulse

# Test OIDC Discovery
curl -s https://auth.insightpulseai.net/realms/insightpulse/.well-known/openid-configuration | jq

# Check all containers
ssh root@165.227.10.178 'docker ps | grep -E "(keycloak|odoo|mattermost)"'
```

### Reload Credentials
```bash
ssh root@165.227.10.178
source /opt/insightpulse-sso/sso-credentials.sh
env | grep -E "(ODOO|MATTERMOST|SUPERSET|KEYCLOAK)"
```

### View Documentation
```bash
# On server
ssh root@165.227.10.178
cat /opt/insightpulse-sso/oauth_configuration_complete.md
cat /opt/insightpulse-sso/superset_oauth_config.py
```

---

## Summary

### ✅ Completed
- Keycloak SSO infrastructure (HTTPS, SSL, DNS)
- 3 OAuth/OIDC clients created
- Odoo OAuth provider configured (Provider ID: 5, Database: insightpulse)
- Mattermost OIDC configured
- Test user created (jgtolentino_rn@yahoo.com)
- All configuration files saved to `/opt/insightpulse-sso/`

### ⏳ Pending
- Superset OAuth deployment on DigitalOcean App Platform

### 🎯 Next Steps
1. **Test Odoo SSO**: https://erp.insightpulseai.net/web/login
2. **Test Mattermost SSO**: https://chat.insightpulseai.net
3. **Deploy Superset OAuth**: Apply configuration from `/opt/insightpulse-sso/superset_oauth_config.py`
4. **Create Additional Users**: As needed for team members
5. **Configure Roles**: Set up application-specific permissions

---

**Maintained By**: InsightPulse AI Team
**Documentation**: `/opt/insightpulse-sso/oauth_configuration_complete.md`
**Last Updated**: 2025-11-11 15:30 UTC
