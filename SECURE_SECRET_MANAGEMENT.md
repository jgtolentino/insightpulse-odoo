# Secure Secret Management Guide

**Important**: Never commit secrets to git or share them in chat/tickets. This guide shows how to inject secrets securely at deployment time.

---

## ✅ Non-Secret Values (Safe to Hardcode)

These can be committed to repository or shown publicly:

```bash
GITHUB_APP_ID=2191216
ALLOWED_ORIGINS=https://pulse-hub-web-an645.ondigitalocean.app
PORT=8080
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
```

## ❌ Secret Values (NEVER Commit or Share)

You must inject these locally using one of the methods below:
- `GITHUB_PRIVATE_KEY` (your PEM file content)
- `GITHUB_WEBHOOK_SECRET` (from GitHub App settings)
- `GITHUB_CLIENT_SECRET` (from GitHub App settings)
- `SUPABASE_SERVICE_ROLE_KEY` (from Supabase dashboard)

---

## 🔐 Deployment Methods

### Option A: Docker Compose (Recommended for Development/Self-Hosted)

**1. Create `docker-compose.yml`:**

```yaml
version: "3.9"

services:
  pulse-hub-api:
    image: node:20-alpine
    working_dir: /app
    command: sh -c "npm ci && npm start"
    ports:
      - "3000:3000"
    environment:
      # Non-secret values (safe to commit)
      PORT: "3000"
      GITHUB_APP_ID: "2191216"
      ALLOWED_ORIGINS: "https://pulse-hub-web-an645.ondigitalocean.app"
      SUPABASE_URL: "https://spdtwktxdalcfigzeqrz.supabase.co"
      NODE_ENV: "production"

      # Point to Docker secrets (mounted as files)
      GITHUB_PRIVATE_KEY_FILE: /run/secrets/github_private_key
      GITHUB_WEBHOOK_SECRET_FILE: /run/secrets/github_webhook_secret
      GITHUB_CLIENT_SECRET_FILE: /run/secrets/github_client_secret
      SUPABASE_SERVICE_ROLE_KEY_FILE: /run/secrets/supabase_service_role_key

    secrets:
      - github_private_key
      - github_webhook_secret
      - github_client_secret
      - supabase_service_role_key

    volumes:
      - ./services/pulse-hub-api:/app

    restart: unless-stopped

secrets:
  github_private_key:
    file: ./secrets/github_private_key.pem
  github_webhook_secret:
    file: ./secrets/github_webhook_secret.txt
  github_client_secret:
    file: ./secrets/github_client_secret.txt
  supabase_service_role_key:
    file: ./secrets/supabase_service_role_key.txt
```

**2. Create secrets directory (YOU do this locally, not me):**

```bash
# Create secure secrets directory
mkdir -p secrets
chmod 700 secrets

# Create each secret file (paste YOUR actual values)
# These commands won't echo to screen or save in history

# GitHub Private Key (paste your full PEM file)
cat > secrets/github_private_key.pem <<'EOF'
-----BEGIN RSA PRIVATE KEY-----
...PASTE YOUR ACTUAL KEY HERE...
-----END RSA PRIVATE KEY-----
EOF
chmod 600 secrets/github_private_key.pem

# Webhook Secret (single line, no echo)
read -rsp "GitHub Webhook Secret: " SECRET && \
  echo "$SECRET" > secrets/github_webhook_secret.txt && \
  chmod 600 secrets/github_webhook_secret.txt && \
  unset SECRET && echo

# Client Secret (single line, no echo)
read -rsp "GitHub Client Secret: " SECRET && \
  echo "$SECRET" > secrets/github_client_secret.txt && \
  chmod 600 secrets/github_client_secret.txt && \
  unset SECRET && echo

# Supabase Service Role Key (single line, no echo)
read -rsp "Supabase Service Role Key: " SECRET && \
  echo "$SECRET" > secrets/supabase_service_role_key.txt && \
  chmod 600 secrets/supabase_service_role_key.txt && \
  unset SECRET && echo
```

**3. Add secrets/ to .gitignore:**

```bash
echo "/secrets/" >> .gitignore
git add .gitignore
git commit -m "chore: ensure secrets directory is never committed"
```

**4. Start services:**

```bash
docker compose up -d
docker compose logs -f pulse-hub-api
```

---

### Option B: Systemd Service (Production Linux Server)

**1. Create `/etc/systemd/system/pulse-hub-api.service`:**

```ini
[Unit]
Description=Pulse Hub API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pulse-hub
WorkingDirectory=/srv/pulse-hub-api

# Non-secret environment variables
Environment=PORT=3000
Environment=GITHUB_APP_ID=2191216
Environment=ALLOWED_ORIGINS=https://pulse-hub-web-an645.ondigitalocean.app
Environment=SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
Environment=NODE_ENV=production

# Load secrets from secure file (not world-readable)
EnvironmentFile=/etc/pulse-hub-api/secrets.env

# Point to PEM file location
Environment=GITHUB_PRIVATE_KEY_FILE=/etc/pulse-hub-api/github_app_private_key.pem

ExecStart=/usr/bin/npm start
Restart=always
RestartSec=5

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/srv/pulse-hub-api

[Install]
WantedBy=multi-user.target
```

**2. Create secret files (YOU do this on the server):**

```bash
# Create secrets directory (root only)
sudo install -d -m 0750 /etc/pulse-hub-api
sudo chown root:pulse-hub /etc/pulse-hub-api

# Create secrets.env (no echo, restrictive permissions)
sudo bash -c 'umask 0177 && cat > /etc/pulse-hub-api/secrets.env <<EOF
# Paste your secrets here (this file is mode 0600, not world-readable)
GITHUB_WEBHOOK_SECRET=YOUR_WEBHOOK_SECRET_HERE
GITHUB_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
SUPABASE_SERVICE_ROLE_KEY=YOUR_SUPABASE_KEY_HERE
EOF'

# Set proper ownership
sudo chown root:pulse-hub /etc/pulse-hub-api/secrets.env
sudo chmod 0640 /etc/pulse-hub-api/secrets.env

# Create PEM file (paste your actual key)
sudo bash -c 'umask 0177 && cat > /etc/pulse-hub-api/github_app_private_key.pem <<EOF
-----BEGIN RSA PRIVATE KEY-----
...PASTE YOUR ACTUAL KEY HERE...
-----END RSA PRIVATE KEY-----
EOF'

# Set proper ownership and permissions
sudo chown root:pulse-hub /etc/pulse-hub-api/github_app_private_key.pem
sudo chmod 0640 /etc/pulse-hub-api/github_app_private_key.pem
```

**3. Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable pulse-hub-api
sudo systemctl start pulse-hub-api
sudo systemctl status pulse-hub-api --no-pager
```

---

### Option C: DigitalOcean App Platform (Already Configured)

For DO App Platform, you DON'T use files. Instead:

1. Go to: **Apps** → **pulse-hub-web** → **Settings** → **Environment Variables**
2. Set each secret directly in the dashboard:
   - `GITHUB_WEBHOOK_SECRET` → Paste your value, mark as SECRET
   - `GITHUB_CLIENT_SECRET` → Paste your value, mark as SECRET
   - `GITHUB_PRIVATE_KEY` → Paste your PEM content, mark as SECRET
   - `SUPABASE_SERVICE_ROLE_KEY` → Already set
3. **Save** → DO auto-redeploys

**Important**: DO does NOT support `*_FILE` suffix. Use direct env vars only.

---

## ✅ Verification (Without Exposing Secrets)

After deployment, verify everything works WITHOUT showing secrets:

### 1. Health Check
```bash
curl -s http://localhost:3000/health | jq
# Expected: {"status":"ok","service":"pulse-hub-api",...}
```

### 2. Check Logs (redacted)
```bash
# Docker Compose
docker compose logs pulse-hub-api | grep "Environment configuration"

# Systemd
sudo journalctl -u pulse-hub-api -n 50 | grep "Environment configuration"

# Expected output (secrets are redacted):
# Environment configuration loaded:
#   PORT: 3000
#   GITHUB_APP_ID: 2191216
#   GITHUB_CLIENT_ID: ***
#   GITHUB_CLIENT_SECRET: ***
#   GITHUB_WEBHOOK_SECRET: ***
#   GITHUB_PRIVATE_KEY: *** (loaded)
#   SUPABASE_URL: https://...
#   SUPABASE_SERVICE_ROLE_KEY: ***
```

### 3. Test Webhook (via GitHub)
1. Go to your GitHub App: https://github.com/settings/apps/pulser-hub
2. Click **Advanced** → **Recent Deliveries**
3. Pick any delivery → Click **Redeliver**
4. Check your server logs for: `Received GitHub event: ...`
5. If signature verification passes → webhook secret is correct ✅

### 4. Test Installation (via GitHub)
1. Install the app on a test repository
2. Check logs for: `Installation created: ...`
3. If no errors → private key is working ✅

---

## 🔍 Troubleshooting

### "GITHUB_WEBHOOK_SECRET is required but not set"
→ You didn't create the secret file or env var. Follow steps above.

### "Failed to read secret from file: /run/secrets/..."
→ Docker secret file doesn't exist. Check `docker compose config` and `secrets/` directory.

### "Invalid webhook signature"
→ Webhook secret is wrong. Double-check the value matches GitHub App settings.

### "Error generating JWT"
→ Private key is wrong or malformed. Ensure you copied the ENTIRE PEM file including headers.

---

## 📝 Security Checklist

- [ ] Secrets never committed to git (check `.gitignore`)
- [ ] Secret files have restrictive permissions (0600 or 0640)
- [ ] Secrets not echoed to terminal during setup
- [ ] Logs redact secret values (only show `***`)
- [ ] Production uses env vars or file-based secrets (not hardcoded)
- [ ] Development uses Docker secrets or `.env.local` (not `.env`)

---

## 🎯 Summary

**What I provided** (safe to commit):
- Code that reads from `*_FILE` env vars
- Deployment templates with placeholder paths
- Non-secret configuration values

**What YOU provide** (locally, never share):
- Actual secret values from GitHub App settings
- Actual PEM private key file
- Actual Supabase service role key

**How it works**:
1. Code checks for `GITHUB_WEBHOOK_SECRET_FILE` first
2. If set, reads from that file path
3. Otherwise falls back to `GITHUB_WEBHOOK_SECRET` env var
4. Logs show `***` instead of actual values

This way secrets stay in your environment/files and never in the codebase!

---

**Last Updated**: November 2, 2025
**Security Level**: Production-ready with proper secret isolation
