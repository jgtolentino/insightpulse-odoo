# One-Click Deployment Options

Deploy the complete InsightPulse automation system with **4 automation modes** in one click.

## ✨ Option 1: DigitalOcean App Platform (Recommended)

**One-Click Deploy:**

```bash
doctl apps create --spec infra/do/one-click-deploy.yaml
```

**What Gets Deployed:**
- ✅ Odoo 19 with ipai_agent addon pre-installed
- ✅ OCR services (PaddleOCR + DeepSeek-OCR-7B)
- ✅ Pulse Hub Web UI
- ✅ PostgreSQL 15 database
- ✅ SSL certificates (automatic)
- ✅ All 4 automation modes active

**Cost:** $24/month (Basic plan)

**URL After Deploy:**
- Odoo: `https://your-app.ondigitalocean.app/odoo`
- OCR: `https://your-app.ondigitalocean.app/ocr`
- Web UI: `https://your-app.ondigitalocean.app`

---

## 🚀 Option 2: GitHub Actions Workflow Dispatch

**One-Click from GitHub UI:**

1. Go to: https://github.com/jgtolentino/insightpulse-odoo/actions
2. Select "One-Click Deploy All"
3. Click "Run workflow"
4. Select environment: `production`
5. Click green "Run workflow" button

**What Gets Deployed:**
- ✅ Latest code from main branch
- ✅ Odoo addon installation
- ✅ OCR service updates
- ✅ Frontend deployment to Vercel
- ✅ Database migrations
- ✅ Health checks and validation

**Time:** ~5 minutes

---

## 🎯 Option 3: Deploy to Existing Droplet

**One-Line Command:**

```bash
curl -sSL https://raw.githubusercontent.com/jgtolentino/insightpulse-odoo/main/scripts/deploy.sh | bash
```

**What Happens:**
1. Pulls latest code
2. Installs ipai_agent addon
3. Updates OCR services
4. Restarts all services
5. Runs health checks
6. Reports status

**Prerequisites:**
- Existing droplet at 188.166.237.231
- Docker and docker-compose installed
- SSH access configured

---

## 📱 Option 4: Vercel Deploy Button (Frontend Only)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/jgtolentino/insightpulse-odoo&project-name=pulse-hub-web&repository-name=pulse-hub-web)

Deploys only the Pulse Hub Web UI to Vercel.

---

## Comparison

| Option | Time | Cost | What's Included | Best For |
|--------|------|------|-----------------|----------|
| **DO App Platform** | 10 min | $24/mo | Everything | New deployments |
| **GitHub Actions** | 5 min | Free | Code updates | Existing infra |
| **Existing Droplet** | 2 min | Free | Updates only | Current setup |
| **Vercel Button** | 3 min | Free | Frontend only | UI development |

---

## After Deployment

### Verify 4 Automation Modes

**1. Odoo Discuss (`@ipai-bot`)**
```
Login to: https://your-app.ondigitalocean.app/odoo
Open: Discuss → AI Agent Support channel
Type: @ipai-bot Hello!
```

**2. Pulse Hub Web UI**
```
Open: https://your-app.ondigitalocean.app
Click: One-Click Deployment button
```

**3. AI Agent API**
```bash
curl -X POST https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Deploy latest OCR updates"}'
```

**4. GitHub PR Bot (`@claude`)**
```
Open any PR: https://github.com/jgtolentino/insightpulse-odoo/pulls
Comment: @claude review this implementation
```

---

## Recommended Path

For **new users**:
1. Use **Option 1** (DigitalOcean App Platform)
2. Click deploy, wait 10 minutes
3. Access all 4 automation modes immediately

For **existing users** (current setup at 188.166.237.231):
1. Use **Option 3** (existing droplet script)
2. Activates automation on current infrastructure
3. Zero downtime deployment

---

**Next Steps:** After deployment completes, see [QUICKSTART_ODOO_AUTOMATION.md](QUICKSTART_ODOO_AUTOMATION.md) for usage examples.
