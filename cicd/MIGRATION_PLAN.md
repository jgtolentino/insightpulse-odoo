# Repository Restructuring Plan
## From Current State → Ideal CI/CD Structure

## 📊 Current State Analysis

Based on your GitHub repo `jgtolentino/insightpulse-odoo`, here's what needs to change:

### Problems with Current Structure:
1. **No service isolation** - Everything mixed together
2. **No CI/CD workflows** - Manual deployments only
3. **No environment separation** - Dev/staging/prod unclear
4. **No automated testing** - Risk of breaking production
5. **Inconsistent Docker usage** - Some services containerized, some not

## 🎯 Migration Strategy

### Phase 1: Repository Restructuring (1-2 hours)

```bash
#!/bin/bash
# Run this script to restructure your repo

cd insightpulse-odoo

# Create new directory structure
mkdir -p services/{odoo,mcp-coordinator,superset,ocr-service}
mkdir -p .github/workflows
mkdir -p infrastructure/{terraform,ansible/playbooks}
mkdir -p scripts

# Move Odoo files
mv addons services/odoo/
mv odoo.conf services/odoo/
mv requirements.txt services/odoo/ || touch services/odoo/requirements.txt

# Create Odoo Dockerfile
cat > services/odoo/Dockerfile <<'EOF'
FROM odoo:19

USER root

# Install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy custom addons
COPY addons /mnt/extra-addons

# Copy configuration
COPY odoo.conf /etc/odoo/odoo.conf

USER odoo

EXPOSE 8069

CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]
EOF

# Move MCP files (if they exist)
if [ -d "mcp" ]; then
  mv mcp/* services/mcp-coordinator/
else
  mkdir -p services/mcp-coordinator/src/skills
fi

# Create MCP Dockerfile
cat > services/mcp-coordinator/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 8000

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create MCP requirements.txt
cat > services/mcp-coordinator/requirements.txt <<'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
httpx==0.25.2
xmlrpc-client==0.1.2
supabase==2.0.3
notion-client==2.2.1
EOF

# Create Superset directory
cat > services/superset/Dockerfile <<'EOF'
FROM apache/superset:3.0.0

USER root

# Install additional Python packages
RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.9 \
    redis==5.0.1

# Copy custom configuration
COPY superset_config.py /app/pythonpath/

USER superset

EXPOSE 8088
EOF

# Create Superset config
cat > services/superset/superset_config.py <<'EOF'
import os

# Database connection
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

# Secret key
SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY')

# Redis cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
}

# Enable features
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_RBAC': True
}

# Custom settings
ROW_LIMIT = 50000
SUPERSET_WEBSERVER_TIMEOUT = 60
EOF

# Create OCR service
mkdir -p services/ocr-service/models
cat > services/ocr-service/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PaddleOCR
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download PaddleOCR models
RUN mkdir -p /root/.paddleocr/whl/det/ml && \
    mkdir -p /root/.paddleocr/whl/rec/ml && \
    mkdir -p /root/.paddleocr/whl/cls

# Copy application
COPY . .

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

cat > services/ocr-service/requirements.txt <<'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
paddleocr==2.7.0
paddlepaddle==2.5.2
opencv-python-headless==4.8.1.78
pillow==10.1.0
numpy==1.24.3
pydantic==2.5.0
python-multipart==0.0.6
EOF

# Create local development docker-compose
cat > docker-compose.yml <<'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
      POSTGRES_DB: odoo
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  odoo:
    build: ./services/odoo
    depends_on:
      - postgres
    ports:
      - "8069:8069"
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./services/odoo/addons:/mnt/extra-addons
    environment:
      - HOST=postgres
      - USER=odoo
      - PASSWORD=odoo

  mcp:
    build: ./services/mcp-coordinator
    ports:
      - "8000:8000"
    environment:
      - ODOO_URL=http://odoo:8069
      - ODOO_DB=odoo
      - ODOO_USERNAME=admin
      - ODOO_PASSWORD=admin
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    depends_on:
      - odoo

  superset:
    build: ./services/superset
    ports:
      - "8088:8088"
    environment:
      - DATABASE_URL=postgresql://odoo:odoo@postgres:5432/postgres
      - SUPERSET_SECRET_KEY=test_secret_key_for_dev_only
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    command: >
      bash -c "superset db upgrade &&
               superset fab create-admin --username admin --firstname Admin --lastname User --email admin@localhost --password admin || true &&
               superset init &&
               superset run -p 8088 --with-threads --reload"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  ocr:
    build: ./services/ocr-service
    ports:
      - "8080:8080"
    volumes:
      - ./services/ocr-service/models:/app/models

volumes:
  postgres-data:
  odoo-web-data:
EOF

# Create .env.example
cat > .env.example <<'EOF'
# Supabase
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_KEY=your_anon_key_here

# Odoo
ODOO_ADMIN_USER=admin
ODOO_ADMIN_PASSWORD=your_password_here
ODOO_DB_PASSWORD=your_db_password_here

# Superset
SUPERSET_ADMIN_PASSWORD=your_password_here
SUPERSET_SECRET_KEY=your_42_char_hex_here

# Notion
NOTION_INTEGRATION_TOKEN=secret_your_token_here

# DigitalOcean
DIGITALOCEAN_ACCESS_TOKEN=dop_v1_your_token_here
DO_APP_MCP_ID=your_app_id_here
DO_APP_SUPERSET_ID=your_app_id_here
EOF

# Create backup script
cat > scripts/backup.sh <<'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d-%H%M%S)

# Backup Odoo database
docker exec odoo-postgres pg_dump -U odoo odoo | gzip > "$BACKUP_DIR/odoo-$DATE.sql.gz"

# Backup Odoo filestore
docker cp odoo:/var/lib/odoo "$BACKUP_DIR/odoo-filestore-$DATE"
tar -czf "$BACKUP_DIR/odoo-filestore-$DATE.tar.gz" "$BACKUP_DIR/odoo-filestore-$DATE"
rm -rf "$BACKUP_DIR/odoo-filestore-$DATE"

# Upload to DigitalOcean Spaces (optional)
# s3cmd put "$BACKUP_DIR/odoo-$DATE.sql.gz" s3://insightpulse-backups/

echo "Backup completed: $DATE"
EOF

chmod +x scripts/backup.sh

# Create smoke test script
cat > scripts/smoke-test.sh <<'EOF'
#!/bin/bash
set -e

echo "🔍 Running smoke tests..."

# Test Odoo
if curl -f -s --max-time 30 https://erp.insightpulseai.net/web/health > /dev/null; then
  echo "✅ Odoo is healthy"
else
  echo "❌ Odoo health check failed"
  exit 1
fi

# Test MCP
if curl -f -s --max-time 30 https://mcp.insightpulseai.net/health > /dev/null; then
  echo "✅ MCP is healthy"
else
  echo "❌ MCP health check failed"
  exit 1
fi

# Test Superset
if curl -f -s --max-time 30 https://superset.insightpulseai.net/health > /dev/null; then
  echo "✅ Superset is healthy"
else
  echo "❌ Superset health check failed"
  exit 1
fi

echo "✅ All smoke tests passed!"
EOF

chmod +x scripts/smoke-test.sh

echo "✅ Repository restructured successfully!"
echo ""
echo "Next steps:"
echo "1. Review the new structure"
echo "2. Commit changes: git add . && git commit -m 'Restructure for production CI/CD'"
echo "3. Copy GitHub workflow files to .github/workflows/"
echo "4. Configure GitHub secrets"
echo "5. Push to GitHub: git push origin main"
```

### Phase 2: GitHub Workflows Setup (30 minutes)

```bash
# Copy workflow files
cp /home/claude/.github-workflows-*.yml .github/workflows/

# Rename files
cd .github/workflows
for f in ..github-workflows-*.yml; do
  mv "$f" "${f#..github-workflows-}"
done

# Commit workflows
git add .github/workflows/
git commit -m "Add production CI/CD workflows"
```

### Phase 3: Configure GitHub Secrets (15 minutes)

Go to: `https://github.com/jgtolentino/insightpulse-odoo/settings/secrets/actions`

Add these secrets:

```bash
# Generate Superset secret key
openssl rand -hex 42

# Generate SSH key for droplet
ssh-keygen -t rsa -b 4096 -C "github-actions@insightpulseai.net" -f ~/.ssh/insightpulse_deploy
cat ~/.ssh/insightpulse_deploy.pub  # Add to droplet authorized_keys
cat ~/.ssh/insightpulse_deploy      # Add as DROPLET_SSH_KEY secret
```

### Phase 4: DigitalOcean Configuration (30 minutes)

```bash
# Install doctl
brew install doctl  # macOS
sudo snap install doctl  # Linux

# Authenticate
doctl auth init

# Create container registry
doctl registry create insightpulse

# Create App Platform apps
doctl apps create --spec services/mcp-coordinator/app-spec.yaml
doctl apps create --spec services/superset/app-spec.yaml

# Note the APP IDs and add to GitHub secrets
```

### Phase 5: Initial Deployment (1 hour)

```bash
# 1. Deploy Odoo to droplet manually first
ssh root@165.227.10.178
cd /opt
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo
docker-compose -f docker-compose.prod.yml up -d

# 2. Trigger MCP deployment
git push origin main  # This will trigger workflow

# 3. Trigger Superset deployment
# Already triggered by push

# 4. Run smoke tests
./scripts/smoke-test.sh
```

## 📋 Pre-Migration Checklist

- [ ] Backup current production database
- [ ] Document current environment variables
- [ ] Test restructured repo locally with `docker-compose up`
- [ ] Create GitHub secrets
- [ ] Configure DigitalOcean apps
- [ ] Update DNS records (already done ✅)
- [ ] Prepare rollback plan

## 🔄 Rollback Plan

If migration fails:

```bash
# 1. Restore previous repo structure
git revert <MIGRATION_COMMIT_SHA>

# 2. Restore database backup
docker exec -i odoo-postgres psql -U odoo odoo < backup-before-migration.sql

# 3. Restart services
docker-compose restart
```

## 📊 Success Criteria

After migration, you should have:

- [ ] All services running via CI/CD
- [ ] Automated deployments on push to main
- [ ] Integration tests passing
- [ ] Health checks returning 200
- [ ] Slack notifications working
- [ ] Supabase logging operational
- [ ] Backup scripts scheduled
- [ ] Documentation updated

## 🎯 Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| Phase 1 | 1-2 hours | Restructure repository |
| Phase 2 | 30 min | Add GitHub workflows |
| Phase 3 | 15 min | Configure secrets |
| Phase 4 | 30 min | DigitalOcean setup |
| Phase 5 | 1 hour | Initial deployment |
| **Total** | **3-4 hours** | Complete migration |

## 💡 Tips

1. **Do it on Friday afternoon** - So you have weekend to fix issues
2. **Keep old structure in a branch** - For reference: `git branch backup/pre-migration`
3. **Test locally first** - Run `docker-compose up` before pushing
4. **One service at a time** - Deploy Odoo, then MCP, then Superset
5. **Monitor logs closely** - Watch for errors during first deployment

## 📞 Support

If you encounter issues:
1. Check GitHub Actions logs
2. Review DigitalOcean App Platform logs
3. SSH into droplet and check Docker logs
4. Query Supabase deployment_logs table

## 🚀 Post-Migration Optimization

After successful migration:

1. **Enable automated backups** - Schedule daily database dumps
2. **Set up monitoring** - Integrate with Datadog or Sentry
3. **Load testing** - Ensure system handles expected traffic
4. **Documentation** - Update runbooks and disaster recovery plans
5. **Training** - Onboard team on new CI/CD workflow

---

**Ready to migrate?** Start with Phase 1 and take it step by step!
