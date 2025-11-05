# Automation & DevOps Excellence Expert

**Skill ID:** `automation-devops-expert`
**Version:** 1.0.0
**Category:** Automation, DevOps, CI/CD
**Expertise Level:** Expert

---

## 🎯 Purpose

This skill enables an AI agent to design and implement comprehensive automation strategies, including CI/CD pipelines, automated deployment, infrastructure as code, and DevOps best practices.

### Key Capabilities
- GitHub Actions workflow automation
- Multi-environment deployment strategies
- Infrastructure as Code (Terraform, Ansible)
- Automated testing and quality gates
- Self-healing and auto-remediation

---

## 🧠 Core Competencies

### 1. CI/CD Pipeline Design

#### GitHub Actions Workflows
Automated workflows for validation, testing, and deployment:
```yaml
name: Continuous Integration

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate Structure
        run: python3 scripts/validate-repo-structure.py

      - name: Run Tests
        run: pytest tests/ -v

      - name: Generate Report
        run: python3 scripts/generate-structure-report.py

      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: health-report
          path: structure-health-report.json
```

### 2. Deployment Automation

#### Multi-Stage Deployment
```bash
#!/bin/bash
# scripts/deployment/deploy-production.sh

set -e

echo "🚀 Deploying to production..."

# Pre-deployment checks
./scripts/validate-all.sh

# Build artifacts
docker-compose build

# Deploy with zero downtime
docker-compose up -d --no-deps --build app

# Health check
./scripts/health-check.sh

# Rollback on failure
if [ $? -ne 0 ]; then
    echo "❌ Deployment failed, rolling back..."
    docker-compose rollback
    exit 1
fi

echo "✅ Deployment successful!"
```

### 3. Infrastructure as Code

#### Terraform Configuration
```hcl
# infrastructure/terraform/main.tf

resource "digitalocean_droplet" "app" {
  image  = "ubuntu-22-04-x64"
  name   = "insightpulse-app"
  region = "nyc3"
  size   = "s-2vcpu-4gb"

  provisioner "remote-exec" {
    inline = [
      "apt-get update",
      "apt-get install -y docker.io docker-compose",
      "git clone https://github.com/jgtolentino/insightpulse-odoo.git",
      "cd insightpulse-odoo && make init && make prod"
    ]
  }
}
```

### 4. Automated Scripts Library

#### Script Categories
- **Setup**: Initial project configuration
- **Deployment**: Production deployment automation
- **Maintenance**: Backup, restore, updates
- **Validation**: Structure and code verification
- **Utilities**: Helper scripts and tools

**Example:**
```bash
# scripts/maintenance/backup.sh
#!/bin/bash
set -e

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "💾 Creating backup..."

# Database backup
docker-compose exec -T postgres pg_dump -U odoo odoo > \
    "$BACKUP_DIR/db-$TIMESTAMP.sql"

# File backup
tar -czf "$BACKUP_DIR/files-$TIMESTAMP.tar.gz" data/

echo "✅ Backup created: $TIMESTAMP"
```

### 5. Makefile Automation

#### Unified Command Interface
```makefile
# Makefile

.PHONY: validate test deploy backup

validate: ## Run all validation checks
	@python3 scripts/validate-repo-structure.py
	@bash scripts/validate-makefile.sh
	@python3 scripts/generate-structure-report.py

test: ## Run all tests
	@pytest tests/unit/ -v
	@pytest tests/integration/ -v
	@pytest tests/e2e/ -v

deploy-prod: ## Deploy to production
	@./scripts/deployment/deploy-production.sh

backup: ## Create database backup
	@./scripts/maintenance/backup.sh
```

---

## ✅ Validation Criteria

### Automation Quality
- ✅ Workflows execute in <15 minutes
- ✅ Zero manual steps in deployment
- ✅ Automatic rollback on failure
- ✅ Self-documenting (help messages)
- ✅ Idempotent operations

### Coverage Metrics
- ✅ 100% of deployments automated
- ✅ 95%+ of manual tasks scripted
- ✅ Daily automated backups
- ✅ Continuous validation in CI/CD

---

## 🎯 Usage Examples

### Example 1: Automated Deployment
```bash
# One-command production deployment
make deploy-prod

# Output:
🚀 Deploying to production...
✓ Pre-deployment validation passed
✓ Building Docker images
✓ Deploying with zero downtime
✓ Health check passed
✅ Deployment successful!
```

### Example 2: CI/CD Integration
```yaml
# Workflow triggered on every push
on: [push]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make validate
      - run: make test
      - run: make health-report
```

### Example 3: Infrastructure Provisioning
```bash
# Deploy complete infrastructure
cd infrastructure/terraform
terraform init
terraform plan
terraform apply

# Result: Fully configured production environment in 10 minutes
```

---

## 📊 Success Metrics

### Automation Effectiveness
- **Deployment Frequency**: 10+ per day
- **Lead Time**: <1 hour
- **MTTR**: <5 minutes
- **Change Failure Rate**: <5%

### Efficiency Gains
- **Manual Work Reduction**: 80%+
- **Deployment Time**: 90% faster
- **Error Rate**: 95% reduction
- **Cost Savings**: $15,000/year

---

## 🔗 Related Skills
- `repo-architect-ai-engineer` - Architecture design
- `validation-expert` - Validation automation
- `testing-expert` - Test automation

---

**Maintained by:** InsightPulse AI Team
**License:** AGPL-3.0
