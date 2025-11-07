# InsightPulse AI Landing Page

Unified login portal for all InsightPulse AI services.

## Features

- ✅ **Unified Authentication** - Single sign-on to all services
- ✅ **Service Dashboard** - Visual access to Odoo, OCR, Superset
- ✅ **Health Monitoring** - Real-time service status checks
- ✅ **Mobile Responsive** - Works on all devices
- ✅ **Secure** - HTTPS, security headers, CORS protection
- ✅ **Minimal** - Single HTML file, no dependencies

## Services

| Service | URL | Status | Purpose |
|---------|-----|--------|---------|
| **Landing Page** | https://insightpulseai.net | ⏳ Pending | Unified portal |
| **Odoo ERP** | https://erp.insightpulseai.net | ✅ Live | Finance, HR, Expenses |
| **OCR Service** | https://ocr.insightpulseai.net | ✅ Live | Receipt processing |
| **Superset BI** | https://superset.insightpulseai.net | ⏳ Pending | Analytics dashboards |

## Quick Deploy

### Prerequisites
- Droplet: 165.227.10.178 (Odoo droplet)
- SSH access configured
- Nginx installed
- Certbot installed

### One-Command Deployment

```bash
cd landing-page
chmod +x deploy-landing.sh
./deploy-landing.sh
```

### Manual Deployment

```bash
# 1. Create web directory
ssh root@165.227.10.178 "mkdir -p /var/www/insightpulseai.net"

# 2. Upload files
scp index.html root@165.227.10.178:/var/www/insightpulseai.net/

# 3. Set permissions
ssh root@165.227.10.178 "chown -R www-data:www-data /var/www/insightpulseai.net"
ssh root@165.227.10.178 "chmod -R 755 /var/www/insightpulseai.net"

# 4. Configure Nginx
scp nginx-landing.conf root@165.227.10.178:/etc/nginx/sites-available/insightpulseai.net
ssh root@165.227.10.178 "ln -sf /etc/nginx/sites-available/insightpulseai.net /etc/nginx/sites-enabled/"

# 5. Obtain SSL certificate
ssh root@165.227.10.178 "certbot certonly --nginx -d insightpulseai.net -d www.insightpulseai.net --non-interactive --agree-tos --email jgtolentino_rn@yahoo.com"

# 6. Test and reload Nginx
ssh root@165.227.10.178 "nginx -t && systemctl reload nginx"

# 7. Verify
curl -I https://insightpulseai.net
```

## Authentication Flow

1. **User visits** `https://insightpulseai.net`
2. **Enters credentials** (username + password)
3. **JavaScript authenticates** via Odoo API
4. **Session stored** in browser sessionStorage
5. **Redirect to Odoo** with active session
6. **Session shared** across all `.insightpulseai.net` subdomains

## Technical Details

### Single Page Application
- **Technology**: Vanilla HTML + CSS + JavaScript
- **Size**: < 20 KB (uncompressed)
- **Dependencies**: None (zero npm packages)
- **Browser Support**: Modern browsers (ES6+)

### Security Features
- HTTPS-only (301 redirect from HTTP)
- HSTS preload ready
- CORS configured for subdomains
- XSS protection
- Content Security Policy headers
- Secure session handling

### Odoo API Integration

The landing page authenticates against Odoo's JSON-RPC API:

```javascript
POST https://erp.insightpulseai.net/web/session/authenticate
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "params": {
    "db": "odoo",
    "login": "username",
    "password": "password"
  }
}

Response:
{
  "result": {
    "uid": 2,
    "session_id": "abc123...",
    "username": "username",
    ...
  }
}
```

### Service Health Checks

On page load, the landing page checks:
- **OCR Service**: `GET https://ocr.insightpulseai.net/health`
- **Odoo ERP**: `HEAD https://erp.insightpulseai.net`
- **Superset**: `GET https://superset.insightpulseai.net` (when available)

Status badges update in real-time based on health check results.

## File Structure

```
landing-page/
├── index.html              # Main landing page (SPA)
├── nginx-landing.conf      # Nginx virtual host config
├── deploy-landing.sh       # Automated deployment script
└── README.md               # This file
```

## Customization

### Update Service URLs

Edit `index.html`, lines 150-154:

```javascript
const services = {
    odoo: 'https://erp.insightpulseai.net',
    superset: 'https://superset.insightpulseai.net',
    ocr: 'https://ocr.insightpulseai.net'
};
```

### Change Color Scheme

Edit CSS gradient in `<style>` section:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Replace `#667eea` (purple) and `#764ba2` (darker purple) with your brand colors.

### Add/Remove Services

Edit the `services-grid` section in HTML:

```html
<a href="https://your-service.insightpulseai.net" class="service-card">
    <div class="service-icon">🎯</div>
    <h3>Your Service</h3>
    <p>Service description</p>
    <span class="service-status status-live">✓ Live</span>
</a>
```

## DNS Configuration

Ensure DNS records point to the Odoo droplet:

```
insightpulseai.net.     A       165.227.10.178
www.insightpulseai.net. CNAME   insightpulseai.net.
```

## Monitoring

### Check Deployment Status

```bash
# Test landing page
curl -I https://insightpulseai.net

# Check Nginx config
ssh root@165.227.10.178 "nginx -t"

# View access logs
ssh root@165.227.10.178 "tail -f /var/log/nginx/insightpulseai.access.log"

# Check SSL certificate
ssh root@165.227.10.178 "certbot certificates | grep insightpulseai.net"
```

### Health Endpoints

```bash
# OCR service
curl https://ocr.insightpulseai.net/health | jq

# Odoo ERP
curl -I https://erp.insightpulseai.net
```

## Troubleshooting

### Landing page not loading

**Check Nginx**:
```bash
ssh root@165.227.10.178 "systemctl status nginx"
ssh root@165.227.10.178 "nginx -t"
```

**Check file permissions**:
```bash
ssh root@165.227.10.178 "ls -la /var/www/insightpulseai.net/"
```

### SSL certificate errors

**Verify certificate**:
```bash
ssh root@165.227.10.178 "certbot certificates"
```

**Renew certificate**:
```bash
ssh root@165.227.10.178 "certbot renew --force-renewal"
ssh root@165.227.10.178 "systemctl reload nginx"
```

### Authentication not working

**Check Odoo API**:
```bash
curl -X POST https://erp.insightpulseai.net/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","params":{"db":"odoo","login":"admin","password":"test"}}'
```

**Check browser console**:
- Open Developer Tools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for failed API calls

### CORS errors

**Verify Nginx CORS headers**:
```bash
curl -I -H "Origin: https://insightpulseai.net" https://erp.insightpulseai.net
```

Should include:
```
Access-Control-Allow-Origin: https://insightpulseai.net
Access-Control-Allow-Credentials: true
```

## Security Considerations

### Production Checklist

- ✅ HTTPS-only (no HTTP access)
- ✅ HSTS enabled (max-age 1 year)
- ✅ Security headers present
- ✅ CORS restricted to subdomains only
- ✅ Session credentials not stored in localStorage
- ✅ SSL certificate auto-renewal enabled
- ⏳ Rate limiting (recommended)
- ⏳ Fail2Ban protection (recommended)

### Password Security

**DO**:
- Use strong, unique passwords for Odoo admin
- Enable 2FA on Odoo accounts
- Rotate passwords regularly (90 days)

**DON'T**:
- Hardcode credentials in JavaScript
- Store plaintext passwords in browser storage
- Share admin credentials

## Performance

### Metrics

- **Page Load**: < 500ms (target)
- **Time to Interactive**: < 1s
- **Bundle Size**: < 20 KB
- **Requests**: 1 (single HTML file)
- **Caching**: Static assets cached 30 days

### Optimization

- No external dependencies (zero npm packages)
- Inline CSS and JavaScript
- Minify for production (optional)
- Enable gzip compression in Nginx

## Future Enhancements

- [ ] Remember me functionality (secure cookies)
- [ ] Password reset flow
- [ ] Multi-factor authentication (2FA)
- [ ] Service status dashboard (uptime monitoring)
- [ ] Dark mode toggle
- [ ] Localization (multi-language support)
- [ ] Admin panel for service management

## Support

**System Owner**: Jake Tolentino
**Email**: jgtolentino_rn@yahoo.com
**Documentation**: `/docs/PRODUCTION_DEPLOYMENT_OCR_2025-11-06.md`

---

**Last Updated**: 2025-11-06
**Version**: 1.0.0
**License**: Proprietary
