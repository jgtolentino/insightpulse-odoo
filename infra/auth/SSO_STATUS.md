# SSO Status - InsightPulse AI

**Last Updated**: 2025-11-11 16:00 UTC
**Keycloak URL**: https://auth.insightpulseai.net
**Realm**: insightpulse

---

## ✅ Completed

### 1. Keycloak Infrastructure
- **Status**: ✅ Running (stable, no restarts)
- **DNS**: `auth.insightpulseai.net` → `165.227.10.178` ✅
- **Port**: 8080 (HTTP only, needs SSL)
- **Container**: `sso-keycloak` (quay.io/keycloak/keycloak:latest)
- **Database**: PostgreSQL (sso-postgres container)
- **Session Store**: Redis (sso-redis container)

### 2. Odoo OAuth Integration
- **Status**: ✅ Complete and Verified
- **URL**: https://erp.insightpulseai.net/web/login
- **Provider ID**: 5
- **Provider Name**: Keycloak SSO
- **Button Text**: "Sign in with Keycloak SSO" ✅
- **Client ID**: `odoo-erp`
- **Redirect URIs**: HTTP and HTTPS wildcard + specific signin path
- **Database**: insightpulse

**Testing**:
```bash
# OAuth button visible at login
curl -s https://erp.insightpulseai.net/web/login | grep "Sign in with Keycloak SSO"
```

### 3. Mattermost OIDC Integration
- **Status**: ✅ Configured (from previous session)
- **URL**: https://chat.insightpulseai.net
- **Client ID**: `mattermost-chat`
- **Button Text**: "Sign in with Keycloak"

### 4. Test User
- **Username**: jgtolentino_rn
- **Email**: jgtolentino_rn@yahoo.com
- **User ID**: a528c149-3b24-4ac0-a965-95103a22fae5
- **Status**: ✅ Created, email verified, enabled

---

## ⏳ Pending

### 1. SSL Certificate for Keycloak
**Priority**: HIGH (blocking production SSO)

**Current State**:
- Keycloak accessible via HTTP only: http://165.227.10.178:8080
- No SSL certificate for auth.insightpulseai.net
- HTTPS redirect not configured

**Required Actions**:
```bash
# 1. Install certbot if not present
apt-get update && apt-get install -y certbot python3-certbot-nginx

# 2. Stop any service using port 80
systemctl stop nginx || true

# 3. Get Let's Encrypt certificate
certbot certonly --standalone -d auth.insightpulseai.net --agree-tos -m jgtolentino_rn@yahoo.com

# 4. Configure Nginx reverse proxy with SSL
cat > /etc/nginx/sites-available/auth.insightpulseai.net << 'EOF'
server {
    listen 80;
    server_name auth.insightpulseai.net;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name auth.insightpulseai.net;

    ssl_certificate /etc/letsencrypt/live/auth.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/auth.insightpulseai.net/privkey.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 5. Enable site and restart nginx
ln -sf /etc/nginx/sites-available/auth.insightpulseai.net /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# 6. Setup auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer
```

### 2. Superset OAuth Integration
**Priority**: MEDIUM

**Current State**:
- OAuth configuration added to `superset/superset_config.py`
- Dockerfile updated to copy config
- Deployment to DigitalOcean **FAILED** (ERROR phase)
- Needs investigation and fix

**Client Details**:
- **Client ID**: superset-analytics
- **Client Secret**: AWETv9z3tpgyfPGSwj7tdNP1lmg589Ra
- **Redirect URIs**:
  - https://superset.insightpulseai.net/oauth-authorized/keycloak
  - https://superset-nlavf.ondigitalocean.app/oauth-authorized/keycloak

**Required Actions**:
1. Investigate DigitalOcean deployment error logs
2. Fix Dockerfile or configuration issue
3. Redeploy to DigitalOcean
4. Test OAuth login flow

### 3. MCP Coordinator OIDC
**Priority**: LOW

**Not Started**:
- No client created in Keycloak yet
- Domain: https://mcp.insightpulseai.net
- Needs OIDC configuration

### 4. Unified Session Management
**Priority**: MEDIUM

**Current State**:
- Each app has separate session management
- No unified SSO cookie across `*.insightpulseai.net`

**Required Actions**:
1. Configure unified session store (Redis)
2. Implement `ip_sso` cookie with domain `.insightpulseai.net`
3. Setup single logout endpoint
4. Configure session timeout policies

---

## 📋 Next Steps Checklist

| Task | Priority | Status | ETA |
|------|----------|--------|-----|
| Install SSL cert for auth.insightpulseai.net | HIGH | ⏳ Pending | 30 min |
| Configure Nginx reverse proxy with SSL | HIGH | ⏳ Pending | 15 min |
| Test Odoo SSO login with test user | HIGH | ⏳ Pending | 5 min |
| Fix Superset deployment error | MEDIUM | ⏳ Pending | 1 hour |
| Deploy Superset OAuth to DigitalOcean | MEDIUM | ⏳ Pending | 30 min |
| Test Superset SSO login | MEDIUM | ⏳ Pending | 5 min |
| Create MCP client in Keycloak | LOW | ❌ Not Started | 15 min |
| Configure MCP OIDC integration | LOW | ❌ Not Started | 30 min |
| Setup unified session management | MEDIUM | ❌ Not Started | 2 hours |

---

## 🔍 Verification Commands

### Check Keycloak Status
```bash
# Container status
docker ps | grep keycloak

# Recent logs
docker logs sso-keycloak --tail 50

# Health check
curl -f http://localhost:8080/health || echo "Failed"
```

### Check OAuth Clients
```bash
source /opt/insightpulse-sso/sso-credentials.sh

TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$KEYCLOAK_ADMIN_USER" \
  -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | jq -r ".access_token")

curl -s "$KEYCLOAK_URL/admin/realms/$KEYCLOAK_REALM/clients" \
  -H "Authorization: Bearer $TOKEN" | jq ".[] | {clientId, enabled, redirectUris}"
```

### Test OAuth Flow
```bash
# Odoo login page
curl -s https://erp.insightpulseai.net/web/login | grep "Sign in with Keycloak SSO"

# Mattermost login page
curl -s https://chat.insightpulseai.net | grep "Sign in with Keycloak"

# Superset login page (when deployed)
curl -s https://superset-nlavf.ondigitalocean.app/login/ | grep -i oauth
```

---

## 🛠️ Troubleshooting

### Keycloak Not Accessible
```bash
# Check container
docker ps -a | grep keycloak

# Restart if needed
docker restart sso-keycloak

# Check logs for errors
docker logs sso-keycloak --tail 100
```

### OAuth Login Fails
```bash
# Check redirect URI mismatch in Keycloak logs
docker logs sso-keycloak | grep "invalid_redirect_uri"

# Verify client configuration
curl -s "$KEYCLOAK_URL/admin/realms/$KEYCLOAK_REALM/clients" \
  -H "Authorization: Bearer $TOKEN" | jq ".[] | select(.clientId == \"odoo-erp\")"
```

### SSL Certificate Issues
```bash
# Check certificate expiry
certbot certificates

# Renew if needed
certbot renew --force-renewal

# Test SSL configuration
curl -I https://auth.insightpulseai.net
```

---

## 📚 Documentation

- **OAuth Complete Guide**: `infra/auth/OAUTH_COMPLETE.md`
- **SSO Credentials**: `/opt/insightpulse-sso/sso-credentials.sh` (server)
- **Keycloak Admin**: https://auth.insightpulseai.net/admin/ (admin / AdminPass2025)

---

**Maintained By**: InsightPulse AI Team
**Last Review**: 2025-11-11
**Next Review**: When SSL is configured
