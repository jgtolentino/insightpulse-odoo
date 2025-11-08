# Unified Landing Page Deployment Guide

**Last Updated:** 2025-11-08
**Target:** https://insightpulseai.net
**Purpose:** Deploy unified authentication portal for all InsightPulse services

---

## Prerequisites

- SSH access to production server
- Nginx installed and configured
- SSL certificates for insightpulseai.net
- Odoo 18 running on port 8069

---

## Deployment Steps

### 1. Copy Portal Files to Production

```bash
# SSH into production server
ssh user@insightpulseai.net

# Navigate to project directory
cd /home/odoo/insightpulse-odoo

# Pull latest changes
git pull origin main

# Verify portal files exist
ls -la portal/
# Should see: index.html, login.html, static/

# Set correct permissions
chmod 755 portal/
chmod 644 portal/index.html
chmod 644 portal/login.html
chmod -R 755 portal/static/
```

### 2. Update Nginx Configuration

```bash
# Backup existing config
sudo cp /etc/nginx/sites-available/insightpulseai.net /etc/nginx/sites-available/insightpulseai.net.bak

# Copy new config
sudo cp infra/nginx/insightpulseai.net.conf /etc/nginx/sites-available/insightpulseai.net

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx

# Check nginx status
sudo systemctl status nginx
```

### 3. Verify Deployment

**Test Landing Page:**
```bash
curl -I https://insightpulseai.net
# Should return: HTTP/2 200
# Content-Type: text/html

curl https://insightpulseai.net | grep "InsightPulse AI"
# Should show HTML with "InsightPulse AI" title
```

**Test Static Assets:**
```bash
curl -I https://insightpulseai.net/static/css/insightpulse-theme.css
# Should return: HTTP/2 200
# Content-Type: text/css
```

**Test Odoo API Proxy:**
```bash
curl -X POST https://insightpulseai.net/web/database/list \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}'
# Should return: {"jsonrpc":"2.0","id":1,"result":["odoo19","odoo_prod"]}
```

### 4. Test Authentication Flow

**Open in Browser:**
1. Navigate to https://insightpulseai.net
2. Enter credentials:
   - Username: `admin`
   - Password: `admin`
3. Click "Sign In to All Services"
4. Should see: "✓ Authentication successful! Redirecting..."
5. Should redirect to: https://erp.insightpulseai.net
6. Should be logged in to Odoo ERP

**Verify Service Cards Unlock:**
- After successful login, all 4 service cards should show ✓ instead of 🔒
- Cards should be clickable and not grayed out

---

## Troubleshooting

### Landing Page Not Loading

**Problem:** 404 Not Found when accessing https://insightpulseai.net

**Solution:**
```bash
# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Verify portal directory exists
ls -la /home/odoo/insightpulse-odoo/portal/

# Check nginx config syntax
sudo nginx -t

# Verify file permissions
ls -la /home/odoo/insightpulse-odoo/portal/index.html
# Should show: -rw-r--r-- (644)
```

### Authentication Not Working

**Problem:** "Authentication failed" error when logging in

**Solution:**
```bash
# Verify Odoo is running
docker ps | grep odoo
# Should show: insightpulse-odoo-odoo-1

# Test Odoo API directly
curl -X POST http://localhost:8069/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"db":"odoo19","login":"admin","password":"admin"},"id":1}'

# Check Odoo logs
docker logs insightpulse-odoo-odoo-1 --tail 50

# Verify database exists
docker exec insightpulse-odoo-db-1 psql -U odoo -l | grep odoo19
```

### Static Assets Not Loading

**Problem:** CSS/JS files return 404

**Solution:**
```bash
# Verify static directory exists
ls -la /home/odoo/insightpulse-odoo/portal/static/css/

# Check nginx static location config
sudo nginx -T | grep -A 5 "location /static/"

# Verify file permissions
sudo chmod -R 755 /home/odoo/insightpulse-odoo/portal/static/
```

### Session Cookies Not Shared

**Problem:** Login works but service cards don't unlock

**Solution:**
```bash
# Check browser console for cookie errors
# Open DevTools → Application → Cookies → https://insightpulseai.net

# Verify nginx cookie configuration
sudo nginx -T | grep -A 10 "location /web/session/"

# Test session info endpoint
curl -X POST https://insightpulseai.net/web/session/get_session_info \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=YOUR_SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}'
```

---

## Rollback Procedure

If deployment fails, rollback to previous configuration:

```bash
# Restore previous nginx config
sudo cp /etc/nginx/sites-available/insightpulseai.net.bak /etc/nginx/sites-available/insightpulseai.net

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Verify rollback
curl -I https://insightpulseai.net
```

---

## Production Checklist

- [ ] Portal files copied to production
- [ ] Nginx configuration updated
- [ ] SSL certificates valid
- [ ] Landing page loads (HTTP 200)
- [ ] Static assets load (CSS, JS)
- [ ] Authentication API works
- [ ] Login flow completes successfully
- [ ] Service cards unlock after login
- [ ] Redirect to ERP works
- [ ] Session persists across subdomains

---

## Security Notes

- All traffic uses HTTPS (SSL/TLS)
- Session cookies are `Secure` and `HttpOnly`
- CORS configured for subdomain access
- CSP headers applied
- XSS protection enabled
- CSRF tokens validated by Odoo

---

## Performance Optimization

**Enable Gzip Compression:**
```nginx
# Add to server block
gzip on;
gzip_types text/css application/javascript application/json;
gzip_min_length 1000;
```

**Enable Browser Caching:**
```nginx
# Static assets already have 30-day cache
# Add for HTML:
location = /index.html {
    expires 1h;
    add_header Cache-Control "public, must-revalidate";
}
```

**Enable HTTP/2 Server Push:**
```nginx
# Add to server block
http2_push /static/css/insightpulse-theme.css;
```

---

## Monitoring

**Check Access Logs:**
```bash
sudo tail -f /var/log/nginx/access.log | grep insightpulseai.net
```

**Check Error Logs:**
```bash
sudo tail -f /var/log/nginx/error.log
```

**Monitor Odoo:**
```bash
docker logs insightpulse-odoo-odoo-1 --follow
```

---

**Support:** jgtolentino_rn@yahoo.com
**Documentation:** https://github.com/jgtolentino/insightpulse-odoo/docs
**Issues:** https://github.com/jgtolentino/insightpulse-odoo/issues
