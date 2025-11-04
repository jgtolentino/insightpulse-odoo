# InsightPulse Odoo - Repository Restructure & CI/CD Plan

## 🎯 Objective
Transform `github.com/jgtolentino/insightpulse-odoo` into a production-grade monorepo with automated CI/CD for:
- Odoo 19 ERP (Finance SSC)
- MCP Coordinator
- Apache Superset
- PaddleOCR Service

## 📊 Current State Analysis

### Infrastructure Inventory
```yaml
DNS (Squarespace):
  - insightpulseai.net (A → 162.159.140.98, Cloudflare)
  - erp.insightpulseai.net (A → 165.227.10.178, Droplet)
  - mcp.insightpulseai.net (CNAME → pulse-hub-web-an645.ondigitalocean.app)
  - superset.insightpulseai.net (CNAME → superset-nlavf.ondigitalocean.app)
  - ocr.insightpulseai.net (A → 162.159.140.98, Cloudflare)

DigitalOcean Resources:
  - Project: fin-workspace (29cde7a1-8280-46ad-9fdf-dea7b21a7825)
  - Droplet: ipai-odoo-erp (165.227.10.178)
  - App: mcp-coordinator (pulse-hub-web)
  - App: superset (superset-nlavf)
  - Agent: odoobe-expert

Supabase:
  - Project: spdtwktxdalcfigzeqrz
  - Database: PostgreSQL 15
  - Extensions: pgvector, pg_stat_statements
```

### Problems with Current Repo
1. ❌ No automated deployments
2. ❌ Manual Docker commands on droplet
3. ❌ No CI testing pipeline
4. ❌ Mixed deployment strategies (droplet vs App Platform)
5. ❌ No database migration automation
6. ❌ Missing environment config management

## 🏗️ Target Architecture

### Monorepo Structure
```
insightpulse-odoo/
├── .github/
│   └── workflows/
│       ├── odoo-deploy.yml          # Droplet → Container Registry → SSH deploy
│       ├── mcp-deploy.yml           # App Platform auto-sync
│       ├── superset-deploy.yml      # App Platform auto-sync
│       ├── ocr-service-deploy.yml   # GPU service deployment
│       ├── db-migrate.yml           # Supabase migrations
│       └── smoke-tests.yml          # Post-deploy validation
│
├── services/
│   ├── odoo/
│   │   ├── Dockerfile.production
│   │   ├── docker-compose.prod.yml
│   │   ├── addons/
│   │   │   ├── finance_ssc/         # Finance Shared Service Center
│   │   │   │   ├── __manifest__.py
│   │   │   │   ├── models/
│   │   │   │   │   ├── month_end_closing.py
│   │   │   │   │   ├── bir_filing.py
│   │   │   │   │   └── agency.py     # RIM, CKVC, BOM, etc.
│   │   │   │   ├── views/
│   │   │   │   └── security/
│   │   │   ├── bir_compliance/      # BIR forms (1601-C, 1702, 2550Q)
│   │   │   ├── expense_management/   # SAP Concur alternative
│   │   │   ├── travel_request/
│   │   │   └── procurement_sourcing/ # SAP Ariba alternative
│   │   ├── oca-dependencies.txt
│   │   └── odoo.conf
│   │
│   ├── mcp-coordinator/
│   │   ├── Dockerfile
│   │   ├── app.yaml                 # App Platform spec
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── odoo-skills/
│   │   │   └── superset-skills/
│   │   └── package.json
│   │
│   ├── superset/
│   │   ├── Dockerfile
│   │   ├── app.yaml
│   │   ├── superset_config.py
│   │   └── dashboards/
│   │       ├── finance-ssc.json
│   │       └── bir-compliance.json
│   │
│   └── paddle-ocr/
│       ├── Dockerfile.gpu
│       ├── requirements.txt
│       ├── app.py
│       └── models/                  # PaddleOCR-VL weights
│
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── droplets.tf
│   │   ├── app-platform.tf
│   │   ├── container-registry.tf
│   │   └── variables.tf
│   │
│   ├── supabase/
│   │   ├── config.toml
│   │   ├── migrations/
│   │   │   ├── 20250101000000_init_schema.sql
│   │   │   ├── 20250102000000_finance_ssc_tables.sql
│   │   │   └── 20250103000000_agency_config.sql
│   │   └── seed.sql
│   │
│   └── ansible/
│       ├── inventory/
│       │   └── production.ini
│       ├── playbooks/
│       │   ├── odoo-droplet-setup.yml
│       │   └── ocr-droplet-setup.yml
│       └── roles/
│           ├── docker/
│           └── nginx/
│
├── scripts/
│   ├── deploy-odoo.sh
│   ├── backup-production.sh
│   ├── smoke-test.sh
│   ├── db-sync-supabase-to-odoo.sh
│   └── generate-bir-reports.sh
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   ├── DEVELOPMENT.md
│   └── runbooks/
│       ├── incident-response.md
│       └── rollback-procedure.md
│
├── .env.example
├── .dockerignore
├── .gitignore
├── docker-compose.dev.yml          # Local development
└── README.md
```

## 🔄 CI/CD Workflows

### 1. Odoo Deployment Workflow

```yaml
# .github/workflows/odoo-deploy.yml
name: Deploy Odoo to Production

on:
  push:
    branches: [main]
    paths:
      - 'services/odoo/**'
  workflow_dispatch:

env:
  DROPLET_IP: 165.227.10.178
  REGISTRY: registry.digitalocean.com/insightpulse
  IMAGE_NAME: odoo
  
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Odoo module tests
        run: |
          docker-compose -f services/odoo/docker-compose.test.yml up --abort-on-container-exit
      
      - name: Lint custom modules
        run: |
          pip install pylint-odoo
          pylint --rcfile=.pylintrc services/odoo/addons/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_TOKEN }}
      
      - name: Build multi-arch image
        run: |
          doctl registry login
          
          docker buildx create --use
          docker buildx build \
            --platform linux/amd64 \
            -f services/odoo/Dockerfile.production \
            -t $REGISTRY/$IMAGE_NAME:${{ github.sha }} \
            -t $REGISTRY/$IMAGE_NAME:latest \
            --build-arg ODOO_VERSION=19.0 \
            --build-arg OCA_MODULES="$(cat services/odoo/oca-dependencies.txt)" \
            --push \
            services/odoo
      
      - name: Scan image for vulnerabilities
        run: |
          doctl registry repo scan $IMAGE_NAME

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Backup production database
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ env.DROPLET_IP }}
          username: root
          key: ${{ secrets.DROPLET_SSH_KEY }}
          script: |
            # Backup to Spaces
            docker exec odoo-db pg_dump -U odoo -F c > /tmp/odoo-backup.dump
            s3cmd put /tmp/odoo-backup.dump \
              s3://insightpulse-backups/odoo/$(date +%Y%m%d-%H%M%S).dump
      
      - name: Deploy to droplet
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ env.DROPLET_IP }}
          username: root
          key: ${{ secrets.DROPLET_SSH_KEY }}
          script: |
            cd /opt/insightpulse-odoo
            
            # Pull latest code
            git pull origin main
            
            # Login to registry
            doctl registry login
            
            # Pull new image
            docker pull ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            
            # Rolling update with health checks
            docker-compose up -d --no-deps --scale odoo=2 odoo
            sleep 30
            curl -f http://localhost:8069/web/health || exit 1
            
            # Scale down old container
            docker-compose up -d --no-deps --scale odoo=1 odoo
      
      - name: Run smoke tests
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ env.DROPLET_IP }}
          username: root
          key: ${{ secrets.DROPLET_SSH_KEY }}
          script: |
            bash /opt/insightpulse-odoo/scripts/smoke-test.sh
      
      - name: Notify deployment
        if: always()
        run: |
          curl -X POST https://mcp.insightpulseai.net/webhooks/deployment \
            -H "Content-Type: application/json" \
            -d '{
              "service": "odoo",
              "version": "${{ github.sha }}",
              "status": "${{ job.status }}",
              "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
            }'
```

### 2. App Platform Auto-Deploy

```yaml
# .github/workflows/mcp-deploy.yml
name: Deploy MCP Coordinator

on:
  push:
    branches: [main]
    paths:
      - 'services/mcp-coordinator/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_TOKEN }}
      
      - name: Update App Platform
        run: |
          # App Platform auto-deploys from GitHub
          # We just trigger a redeploy
          doctl apps create-deployment ${{ secrets.MCP_APP_ID }} --wait
      
      - name: Health check
        run: |
          sleep 60
          curl -f https://mcp.insightpulseai.net/health
```

### 3. Database Migration Workflow

```yaml
# .github/workflows/db-migrate.yml
name: Supabase Migrations

on:
  push:
    branches: [main]
    paths:
      - 'infrastructure/supabase/migrations/**'
  workflow_dispatch:

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Supabase CLI
        uses: supabase/setup-cli@v1
      
      - name: Run migrations
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_TOKEN }}
          SUPABASE_DB_PASSWORD: ${{ secrets.SUPABASE_DB_PASSWORD }}
        run: |
          supabase link --project-ref spdtwktxdalcfigzeqrz
          supabase db push
      
      - name: Verify schema
        run: |
          supabase db diff
```

## 📦 Production Docker Compose

```yaml
# services/odoo/docker-compose.prod.yml
version: '3.8'

services:
  odoo:
    image: registry.digitalocean.com/insightpulse/odoo:latest
    restart: always
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-data:/var/lib/odoo
      - ./addons:/mnt/extra-addons:ro
      - ./odoo.conf:/etc/odoo/odoo.conf:ro
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  db:
    image: postgres:15-alpine
    restart: always
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=odoo
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    command: postgres -c max_connections=200 -c shared_buffers=512MB
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - odoo

volumes:
  odoo-data:
  postgres-data:
```

## 🔐 Secrets Management

### GitHub Secrets Required
```bash
# DigitalOcean
DIGITALOCEAN_TOKEN=dop_v1_xxxxx
DROPLET_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----

# Supabase
SUPABASE_TOKEN=sbp_xxxxx
SUPABASE_DB_PASSWORD=xxxxx

# App IDs
MCP_APP_ID=xxxxx
SUPERSET_APP_ID=xxxxx

# Odoo
ODOO_ADMIN_PASSWORD=xxxxx
POSTGRES_PASSWORD=xxxxx
```

### How to Set Secrets
```bash
# Using GitHub CLI
gh secret set DIGITALOCEAN_TOKEN -b "dop_v1_xxxxx"
gh secret set DROPLET_SSH_KEY < ~/.ssh/id_ed25519

# Or via GitHub UI
# Repository → Settings → Secrets and variables → Actions → New repository secret
```

## 🚀 Deployment Steps

### Phase 1: Repository Restructure (Day 1)
```bash
# 1. Backup current repo
git clone https://github.com/jgtolentino/insightpulse-odoo insightpulse-odoo-backup

# 2. Create new structure
cd insightpulse-odoo
git checkout -b restructure

# 3. Move files to new structure
mkdir -p services/{odoo,mcp-coordinator,superset,paddle-ocr}
mkdir -p infrastructure/{terraform,supabase,ansible}
mkdir -p .github/workflows scripts docs

# 4. Migrate Odoo addons
mv custom_addons/* services/odoo/addons/

# 5. Create OCA dependencies list
cat > services/odoo/oca-dependencies.txt <<EOF
account-financial-tools
account-invoicing
server-tools
web
queue
EOF

# 6. Create production Dockerfile
cp services/odoo/Dockerfile services/odoo/Dockerfile.production
# Edit as shown above

# 7. Commit and push
git add .
git commit -m "feat: restructure repo for production CI/CD"
git push origin restructure
```

### Phase 2: CI/CD Setup (Day 2-3)
```bash
# 1. Create GitHub Actions workflows
cp /path/to/workflows/*.yml .github/workflows/

# 2. Set up GitHub secrets
gh secret set DIGITALOCEAN_TOKEN -b "$(cat ~/.config/doctl/config.yaml | grep token)"
gh secret set DROPLET_SSH_KEY < ~/.ssh/id_ed25519

# 3. Create DigitalOcean Container Registry
doctl registry create insightpulse --subscription-tier basic

# 4. Configure droplet for automated deployments
ssh root@165.227.10.178 << 'EOF'
  # Install doctl
  cd /usr/local/bin
  wget https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz
  tar xf doctl-1.104.0-linux-amd64.tar.gz
  rm doctl-1.104.0-linux-amd64.tar.gz
  
  # Configure doctl
  doctl auth init -t $DIGITALOCEAN_TOKEN
  
  # Clone repo
  cd /opt
  git clone https://github.com/jgtolentino/insightpulse-odoo.git
  cd insightpulse-odoo
  
  # Set up systemd service
  cp scripts/odoo.service /etc/systemd/system/
  systemctl enable odoo
  systemctl start odoo
EOF

# 5. Test workflow
git checkout main
git merge restructure
git push origin main
# GitHub Actions will trigger automatically
```

### Phase 3: App Platform Migration (Day 4-5)
```bash
# 1. Create App Platform specs
cat > services/mcp-coordinator/app.yaml <<EOF
name: mcp-coordinator
services:
- name: web
  github:
    repo: jgtolentino/insightpulse-odoo
    branch: main
    deploy_on_push: true
  source_dir: services/mcp-coordinator
  envs:
  - key: SUPABASE_URL
    value: https://spdtwktxdalcfigzeqrz.supabase.co
  - key: SUPABASE_ANON_KEY
    type: SECRET
  http_port: 3000
  routes:
  - path: /
EOF

# 2. Create or update apps
doctl apps create --spec services/mcp-coordinator/app.yaml
doctl apps create --spec services/superset/app.yaml

# 3. Add custom domains
doctl apps update $MCP_APP_ID --spec - <<EOF
domains:
- domain: mcp.insightpulseai.net
  type: PRIMARY
EOF
```

### Phase 4: Terraform Infrastructure (Day 6-7)
```bash
# 1. Initialize Terraform
cd infrastructure/terraform
terraform init

# 2. Plan infrastructure
terraform plan \
  -var="do_token=$DIGITALOCEAN_TOKEN" \
  -var="project_id=29cde7a1-8280-46ad-9fdf-dea7b21a7825"

# 3. Apply (this will create/update resources)
terraform apply

# 4. Output connection strings
terraform output -json > ../../.env.production
```

## 🧪 Testing Strategy

### Smoke Test Script
```bash
#!/bin/bash
# scripts/smoke-test.sh

set -e

echo "🧪 Running smoke tests..."

# 1. Odoo health check
echo "Testing Odoo..."
curl -f https://erp.insightpulseai.net/web/health || exit 1

# 2. MCP health check
echo "Testing MCP Coordinator..."
curl -f https://mcp.insightpulseai.net/health || exit 1

# 3. Superset health check
echo "Testing Superset..."
curl -f https://superset.insightpulseai.net/health || exit 1

# 4. Database connectivity
echo "Testing database..."
ssh root@165.227.10.178 "docker exec odoo-db psql -U odoo -c 'SELECT 1'" || exit 1

# 5. Odoo API test
echo "Testing Odoo API..."
curl -f https://erp.insightpulseai.net/web/database/list || exit 1

# 6. Finance SSC module check
echo "Testing Finance SSC module..."
ssh root@165.227.10.178 "docker exec odoo-web odoo shell -c '
from odoo import fields
print(fields.Date.context_today(self))
'" || exit 1

echo "✅ All smoke tests passed!"
```

## 📊 Monitoring Setup

### DigitalOcean Monitoring
```bash
# Enable monitoring on droplet
doctl compute droplet get 165.227.10.178 --format ID,Monitoring

# Set up alerts
doctl monitoring alert create \
  --type v1/insights/droplet/cpu \
  --description "High CPU on Odoo droplet" \
  --compare GreaterThan \
  --value 90 \
  --window 5m \
  --entities 165.227.10.178
```

### Supabase Logs Integration
```sql
-- infrastructure/supabase/migrations/20250104000000_deployment_logs.sql
CREATE TABLE deployment_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  service text NOT NULL,
  version text NOT NULL,
  status text NOT NULL CHECK (status IN ('success', 'failure', 'rollback')),
  deployed_at timestamptz NOT NULL DEFAULT now(),
  deployed_by text,
  metadata jsonb
);

CREATE INDEX idx_deployment_logs_service ON deployment_logs(service);
CREATE INDEX idx_deployment_logs_deployed_at ON deployment_logs(deployed_at DESC);
```

## 🔄 Rollback Procedure

```bash
# scripts/rollback.sh
#!/bin/bash

SERVICE=$1
VERSION=$2

case $SERVICE in
  odoo)
    ssh root@165.227.10.178 << EOF
      cd /opt/insightpulse-odoo
      docker pull registry.digitalocean.com/insightpulse/odoo:$VERSION
      docker-compose up -d --no-deps odoo
EOF
    ;;
  mcp)
    doctl apps create-deployment $MCP_APP_ID \
      --force-rebuild \
      --git-branch-name $VERSION
    ;;
  *)
    echo "Unknown service: $SERVICE"
    exit 1
    ;;
esac
```

## 🎯 Success Metrics

After implementation, you should have:

- ✅ Zero-downtime deployments via rolling updates
- ✅ Automated database backups before each deploy
- ✅ <5 minute deployment time
- ✅ Automatic rollback on health check failure
- ✅ Container image vulnerability scanning
- ✅ Full deployment audit trail in Supabase

## 📚 Next Steps

1. **Week 1:** Repository restructure + CI/CD workflows
2. **Week 2:** Terraform infrastructure + monitoring
3. **Week 3:** Integration testing + documentation
4. **Week 4:** Production cutover + team training

---

**Need help with any phase?** Let me know which section you want to tackle first.
