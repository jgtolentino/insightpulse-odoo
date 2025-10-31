# Quick Start: Leverage Your GitHub Integrations

You have **DigitalOcean GitHub App** installed. Here's how to use it in 5 minutes.

## 🎯 What You Get

- ✅ **Auto-deploy** when you push to `main`
- ✅ **PR previews** for testing before merge
- ✅ **Status checks** on commits
- ✅ **Health monitoring** with auto-rollback

## 🚀 Deploy in 3 Steps

### Step 1: Deploy the App

```bash
# Install doctl (if needed)
brew install doctl  # macOS
# or download: https://docs.digitalocean.com/reference/doctl/

# Authenticate
doctl auth init

# Deploy app (uses DigitalOcean GitHub App)
./.do/deploy.sh
```

### Step 2: Set Secrets

In DigitalOcean Dashboard:
1. Go to your app
2. **Settings** → **App-Level Environment Variables**
3. Add secret:
   - `ODOO_ADMIN_PASSWORD` = your-strong-password

### Step 3: Push to Deploy

```bash
# Make any change
echo "# Updated" >> README.md
git add README.md
git commit -m "test: trigger deploy"
git push origin main

# DigitalOcean GitHub App automatically:
# 1. Builds Docker image
# 2. Runs health checks
# 3. Deploys to production
# 4. Posts status to GitHub
```

That's it! Your app is live at the URL shown in DO dashboard.

## 🎨 Enable PR Previews

1. Go to your app in DO dashboard
2. **Settings** → **General**
3. Enable **"Deploy Pull Request Previews"**

Now every PR gets a unique preview URL:
```
https://pr-123-insightpulse-<random>.ondigitalocean.app
```

## 📋 Full Setup Guide

See [docs/INTEGRATIONS_GUIDE.md](docs/INTEGRATIONS_GUIDE.md) for:
- Docker Desktop + MCP integration
- Claude AI configuration
- GitHub Actions integration
- Advanced workflows

## 🐛 Troubleshooting

**Deploy not triggering?**
```bash
# Check webhook deliveries
# GitHub → Settings → Webhooks → Recent Deliveries

# Validate spec
doctl apps spec validate .do/app.yaml
```

**Build failing?**
```bash
# Check logs
doctl apps logs $(doctl apps list --format ID --no-header) --type BUILD
```

**Health check failing?**
```bash
# Check if health endpoint works locally
docker build -t test .
docker run -p 8069:8069 test
curl http://localhost:8069/web/health
```

## 📚 Resources

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Full Integrations Guide](docs/INTEGRATIONS_GUIDE.md)
- [Production Deployment Guide](PRODUCTION_DEPLOYMENT.md)
