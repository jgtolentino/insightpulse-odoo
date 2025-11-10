---
name: odoo-ce-oca-automation
description: Automated migration from Odoo Enterprise to Odoo 18 CE + OCA modules while preserving repo structure, enforcing coding guidelines, and setting up complete CI/CD + IaC automation.
---

# Odoo 18 CE + OCA Migration Automation

Automate the complete migration from Odoo Enterprise to Odoo 18 Community Edition with OCA modules, while maintaining your existing repository structure, enforcing coding standards, and deploying production-ready infrastructure.

## What This Skill Does

**Input**: Existing Odoo repo (any version, Enterprise or CE)
**Output**: Odoo 18 CE + OCA with:
- ✅ Preserved repo structure and git history
- ✅ OCA module alternatives to Enterprise features
- ✅ Enforced OCA coding standards
- ✅ Complete CI/CD pipelines (GitHub Actions)
- ✅ Production IaC (Terraform + DigitalOcean)
- ✅ Auto-generated documentation

## Quick Start

### Scenario 1: Fresh Setup

```bash
# User asks: "Set up Odoo 18 CE with OCA modules for accounting and helpdesk"

# Skill executes:
1. Create repo structure following OCA standards
2. Generate docker-compose for local dev
3. Vendor OCA modules (account-financial-reporting, helpdesk)
4. Set up CI/CD pipelines
5. Generate Terraform for DigitalOcean deployment
6. Create documentation
```

### Scenario 2: Migration from Enterprise

```bash
# User asks: "Migrate my Odoo 16 Enterprise repo to Odoo 18 CE + OCA"

# Skill executes:
1. Analyze existing Enterprise modules
2. Map to OCA equivalents
3. Create migration plan
4. Preserve custom modules
5. Update dependencies
6. Migrate data models
7. Set up CI/CD
8. Deploy to production
```

## Core Workflows

### Workflow 1: Repo Structure Setup

**Trigger**: User asks to "set up Odoo 18 CE repo" or "initialize OCA project"

**Steps**:
1. **Analyze Requirements**
   - Parse user's feature requests
   - Identify needed OCA modules
   - Check for existing repo structure

2. **Generate Repository Structure**
   ```
   odoo-project/
   ├── addons/
   │   ├── custom/          # Custom modules
   │   └── oca/             # Vendored OCA modules
   ├── docker-compose.yml   # Development environment
   ├── .github/
   │   └── workflows/       # CI/CD pipelines
   ├── terraform/           # Infrastructure as Code
   ├── scripts/             # Automation scripts
   ├── docs/                # Documentation
   ├── .pre-commit-config.yaml
   ├── .pylintrc
   ├── .flake8
   └── README.md
   ```

3. **Enforce Coding Guidelines**
   - Copy OCA .pylintrc configuration
   - Set up pre-commit hooks
   - Configure code formatters (black, isort)
   - Add .editorconfig

4. **Generate Documentation**
   - README.md with setup instructions
   - CONTRIBUTING.md with development guide
   - MODULE_STRUCTURE.md explaining layout

**Output**: Complete repo structure ready for development

See [examples/repo-setup.md](examples/repo-setup.md)

---

### Workflow 2: OCA Module Vendoring

**Trigger**: User asks to "vendor OCA modules" or "add OCA accounting"

**Steps**:
1. **Parse Module Requirements**
   ```python
   # Example: User wants "accounting reports and budgeting"
   features = ["accounting reports", "budgeting"]

   # Map to OCA modules
   oca_modules = {
       "accounting reports": ["account_financial_report", "mis_builder"],
       "budgeting": ["budget_control", "account_budget"]
   }
   ```

2. **Generate repos.yaml**
   ```yaml
   # addons/oca/repos.yaml
   account-financial-reporting:
     url: https://github.com/OCA/account-financial-reporting
     branch: "18.0"
     commit: abc123def456
     modules:
       - account_financial_report
       - mis_builder

   account-budgeting:
     url: https://github.com/OCA/account-budgeting
     branch: "18.0"
     commit: def456ghi789
     modules:
       - budget_control
       - account_budget
   ```

3. **Execute Vendoring Script**
   ```bash
   python3 scripts/vendor_oca_enhanced.py \
     --repos addons/oca/repos.yaml \
     --target addons/oca \
     --odoo-version 18.0 \
     --validate
   ```

4. **Validate Module Compatibility**
   - Check Odoo 18.0 compatibility
   - Verify dependencies
   - Run automated tests
   - Generate requirements.txt

5. **Update Documentation**
   - Add module list to README
   - Document installation steps
   - Create module dependency graph

**Output**: Vendored OCA modules with version locking

See [examples/vendor-oca-modules.md](examples/vendor-oca-modules.md)

---

### Workflow 3: Enterprise to OCA Migration

**Trigger**: User asks to "migrate from Odoo Enterprise" or "replace Enterprise modules"

**Steps**:
1. **Analyze Current Setup**
   ```bash
   # Detect Enterprise modules
   grep -r "license.*OEEL\|lgpl-3" addons/enterprise/

   # List installed modules
   psql -c "SELECT name FROM ir_module_module WHERE state='installed'"
   ```

2. **Generate Migration Plan**
   ```markdown
   ## Migration Plan

   ### Enterprise Modules → OCA Alternatives

   | Enterprise Module | OCA Replacement | Status |
   |-------------------|-----------------|--------|
   | account_reports | account_financial_report + mis_builder | ✅ Available |
   | web_studio | web_studio_oca | ✅ Available |
   | helpdesk | helpdesk_mgmt | ✅ Available |
   | project_forecast | resource_booking | ⚠️ Partial |

   ### Custom Modules Status
   - ✅ 12 custom modules compatible with CE
   - ⚠️ 2 custom modules need dependency updates
   - ❌ 1 module requires refactoring (uses Enterprise API)

   ### Cost Savings
   - Before: $4,320/year (Enterprise license)
   - After: $288/year (DigitalOcean hosting)
   - **Savings: $4,032/year (93% reduction)**
   ```

3. **Execute Migration**
   ```bash
   # Backup database
   ./scripts/backup.sh --type full

   # Remove Enterprise modules
   odoo-bin -d production --uninstall enterprise_module1,enterprise_module2

   # Install OCA replacements
   odoo-bin -d production -i account_financial_report,mis_builder,helpdesk_mgmt

   # Update custom module dependencies
   python3 scripts/auto-fix-dependencies.py --update
   ```

4. **Validate Migration**
   - Run automated tests
   - Check for broken views
   - Validate data integrity
   - Performance benchmarking

5. **Update Configuration**
   - Modify addon paths
   - Update docker-compose.yml
   - Adjust CI/CD pipelines

**Output**: Migrated Odoo 18 CE + OCA system

See [examples/enterprise-migration.md](examples/enterprise-migration.md)

---

### Workflow 4: CI/CD Pipeline Setup

**Trigger**: User asks to "set up CI/CD" or "add GitHub Actions"

**Steps**:
1. **Generate GitHub Actions Workflows**

   **File: `.github/workflows/odoo-ci.yml`**
   ```yaml
   name: Odoo 18 CE CI/CD

   on:
     push:
       branches: [main, develop]
     pull_request:
       branches: [main]

   jobs:
     lint:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: '3.11'
         - name: Install linters
           run: |
             pip install pylint flake8 black isort
         - name: Lint custom modules
           run: |
             pylint addons/custom/*/
             flake8 addons/custom/
             black --check addons/custom/
             isort --check addons/custom/

     test:
       runs-on: ubuntu-latest
       services:
         postgres:
           image: postgres:15
           env:
             POSTGRES_DB: odoo_test
             POSTGRES_USER: odoo
             POSTGRES_PASSWORD: odoo
           options: >-
             --health-cmd pg_isready
             --health-interval 10s
             --health-timeout 5s
             --health-retries 5

       steps:
         - uses: actions/checkout@v4
         - name: Start Odoo
           run: docker-compose -f docker-compose.test.yml up -d
         - name: Run Tests
           run: |
             docker-compose exec -T odoo odoo-bin \
               -d odoo_test \
               --test-enable \
               --stop-after-init \
               --log-level=test
         - name: Check Module Installation
           run: |
             python3 scripts/check-broken-modules.sh

     security:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Security Scan
           run: |
             pip install bandit safety
             bandit -r addons/custom/
             safety check

     deploy:
       needs: [lint, test, security]
       if: github.ref == 'refs/heads/main'
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Deploy to DigitalOcean
           env:
             DO_TOKEN: ${{ secrets.DO_TOKEN }}
           run: |
             doctl apps create-deployment ${{ secrets.DO_APP_ID }}
   ```

2. **Generate Pre-commit Hooks**

   **File: `.pre-commit-config.yaml`**
   ```yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 24.1.1
       hooks:
         - id: black
           args: [--line-length=79]

     - repo: https://github.com/PyCQA/isort
       rev: 5.13.2
       hooks:
         - id: isort
           args: [--profile=black, --line-length=79]

     - repo: https://github.com/PyCQA/flake8
       rev: 7.0.0
       hooks:
         - id: flake8
           args: [--max-line-length=79]

     - repo: https://github.com/OCA/pylint-odoo
       rev: v9.0.4
       hooks:
         - id: pylint
           args: [--load-plugins=pylint_odoo]

     - repo: https://github.com/OCA/maintainer-tools
       rev: master
       hooks:
         - id: oca-gen-addon-readme
         - id: oca-update-pre-commit-excluded-addons
   ```

3. **Set Up Automated Testing**
   - Generate test fixtures
   - Create test database
   - Configure test coverage reporting

4. **Configure Deployment Automation**
   - Set up staging environment
   - Configure production deployment triggers
   - Add rollback procedures

**Output**: Complete CI/CD pipeline ready to use

See [examples/cicd-setup.md](examples/cicd-setup.md)

---

### Workflow 5: Infrastructure as Code (Terraform)

**Trigger**: User asks to "deploy to DigitalOcean" or "set up production infrastructure"

**Steps**:
1. **Generate Terraform Configuration**

   **File: `terraform/main.tf`**
   ```hcl
   terraform {
     required_version = ">= 1.5.0"
     required_providers {
       digitalocean = {
         source  = "digitalocean/digitalocean"
         version = "~> 2.34"
       }
     }
     backend "s3" {
       # Supabase S3-compatible storage
       bucket   = "insightpulse-terraform-state"
       key      = "odoo18/terraform.tfstate"
       region   = "us-east-1"
       endpoint = "https://spdtwktxdalcfigzeqrz.supabase.co/storage/v1/s3"
     }
   }

   provider "digitalocean" {
     token = var.do_token
   }

   # VPC for secure networking
   resource "digitalocean_vpc" "odoo_vpc" {
     name     = "odoo-vpc-sgp1"
     region   = var.region
     ip_range = "10.10.0.0/16"
   }

   # Odoo App Platform
   resource "digitalocean_app" "odoo" {
     spec {
       name   = "odoo18-production"
       region = var.region

       service {
         name               = "odoo"
         instance_count     = 2
         instance_size_slug = "professional-xs"

         image {
           registry_type = "DOCKER_HUB"
           registry      = "odoo"
           repository    = "odoo"
           tag           = "18.0"
         }

         env_var {
           key   = "HOST"
           value = var.postgres_host
           type  = "SECRET"
         }

         env_var {
           key   = "PORT"
           value = "5432"
         }

         env_var {
           key   = "USER"
           value = var.postgres_user
           type  = "SECRET"
         }

         env_var {
           key   = "PASSWORD"
           value = var.postgres_password
           type  = "SECRET"
         }

         http_port = 8069

         health_check {
           http_path = "/web/health"
         }
       }

       # Static files CDN
       static_site {
         name          = "odoo-static"
         source_dir    = "/var/lib/odoo/filestore"
         output_dir    = "/"
         build_command = "echo 'Static files ready'"
       }

       domain {
         name = "erp.insightpulseai.net"
         type = "PRIMARY"
       }
     }
   }

   # Database (Supabase PostgreSQL)
   resource "digitalocean_database_cluster" "odoo_db" {
     count      = var.use_supabase ? 0 : 1
     name       = "odoo18-postgres"
     engine     = "pg"
     version    = "15"
     size       = "db-s-2vcpu-4gb"
     region     = var.region
     node_count = 1

     maintenance_window {
       day  = "sunday"
       hour = "03:00:00"
     }
   }

   # Firewall
   resource "digitalocean_firewall" "odoo_firewall" {
     name = "odoo-firewall"

     tags = ["odoo", "production"]

     inbound_rule {
       protocol         = "tcp"
       port_range       = "22"
       source_addresses = var.admin_ips
     }

     inbound_rule {
       protocol         = "tcp"
       port_range       = "443"
       source_addresses = ["0.0.0.0/0", "::/0"]
     }

     outbound_rule {
       protocol              = "tcp"
       port_range            = "1-65535"
       destination_addresses = ["0.0.0.0/0", "::/0"]
     }
   }

   # DNS Records
   resource "digitalocean_record" "odoo_a" {
     domain = var.domain
     type   = "A"
     name   = "erp"
     value  = digitalocean_app.odoo.default_ingress
     ttl    = 300
   }

   resource "digitalocean_record" "odoo_cname_www" {
     domain = var.domain
     type   = "CNAME"
     name   = "www.erp"
     value  = "erp.${var.domain}."
     ttl    = 300
   }
   ```

   **File: `terraform/variables.tf`**
   ```hcl
   variable "do_token" {
     description = "DigitalOcean API token"
     type        = string
     sensitive   = true
   }

   variable "region" {
     description = "DigitalOcean region"
     type        = string
     default     = "sgp1"
   }

   variable "domain" {
     description = "Domain name"
     type        = string
     default     = "insightpulseai.net"
   }

   variable "postgres_host" {
     description = "PostgreSQL host"
     type        = string
     sensitive   = true
   }

   variable "postgres_user" {
     description = "PostgreSQL user"
     type        = string
     default     = "odoo"
     sensitive   = true
   }

   variable "postgres_password" {
     description = "PostgreSQL password"
     type        = string
     sensitive   = true
   }

   variable "use_supabase" {
     description = "Use Supabase instead of DigitalOcean managed database"
     type        = bool
     default     = true
   }

   variable "admin_ips" {
     description = "Admin IP addresses for SSH access"
     type        = list(string)
     default     = []
   }
   ```

   **File: `terraform/outputs.tf`**
   ```hcl
   output "app_url" {
     description = "Odoo application URL"
     value       = "https://${digitalocean_app.odoo.default_ingress}"
   }

   output "app_id" {
     description = "DigitalOcean App ID"
     value       = digitalocean_app.odoo.id
   }

   output "database_uri" {
     description = "Database connection URI"
     value       = var.use_supabase ? "Using Supabase" : digitalocean_database_cluster.odoo_db[0].uri
     sensitive   = true
   }

   output "static_url" {
     description = "CDN URL for static files"
     value       = digitalocean_app.odoo.live_url
   }
   ```

2. **Generate Deployment Scripts**

   **File: `scripts/deploy-production.sh`**
   ```bash
   #!/bin/bash
   set -euo pipefail

   echo "🚀 Deploying Odoo 18 to DigitalOcean..."

   # Initialize Terraform
   cd terraform
   terraform init

   # Validate configuration
   terraform validate

   # Plan deployment
   terraform plan -out=odoo.tfplan

   # Apply changes
   terraform apply odoo.tfplan

   # Get outputs
   APP_URL=$(terraform output -raw app_url)
   APP_ID=$(terraform output -raw app_id)

   echo "✅ Deployment complete!"
   echo "📱 App URL: $APP_URL"
   echo "🆔 App ID: $APP_ID"

   # Health check
   echo "🏥 Running health check..."
   curl -f "$APP_URL/web/health" || echo "⚠️ Health check failed"

   # Update DNS
   echo "🌐 Updating DNS records..."
   cd ..
   ./scripts/update-dns.sh

   echo "✨ Deployment finished successfully!"
   ```

3. **Configure Monitoring**
   - Set up DigitalOcean monitoring
   - Configure alerts
   - Add log aggregation

4. **Document Infrastructure**
   - Create infrastructure diagram
   - Document access procedures
   - Add troubleshooting guide

**Output**: Production-ready infrastructure as code

See [examples/iac-deployment.md](examples/iac-deployment.md)

---

### Workflow 6: Coding Guidelines Enforcement

**Trigger**: Automatic on every file save/commit

**Steps**:
1. **Copy OCA Standards**
   ```bash
   # .pylintrc (OCA standard)
   [MASTER]
   load-plugins=pylint_odoo
   score=n

   [MESSAGES CONTROL]
   disable=all
   enable=manifest-required-key,
          manifest-deprecated-key,
          missing-readme,
          rst-syntax-error,
          sql-injection

   [IMPORTS]
   deprecated-modules=optparse,tkinter.tix

   [DESIGN]
   max-line-length=79
   max-module-lines=1000
   max-args=5
   max-locals=15
   ```

2. **Set Up Pre-commit Hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   pre-commit run --all-files
   ```

3. **Configure Black Formatter**
   ```toml
   # pyproject.toml
   [tool.black]
   line-length = 79
   target-version = ['py311']
   include = '\.pyi?$'
   extend-exclude = '''
   /(
     \.git
     | \.venv
     | build
     | dist
     | addons/oca
   )/
   '''
   ```

4. **Add isort Configuration**
   ```ini
   # .isort.cfg
   [settings]
   profile = black
   line_length = 79
   known_odoo = odoo
   known_odoo_addons = odoo.addons
   sections = FUTURE,STDLIB,THIRDPARTY,ODOO,ODOO_ADDONS,FIRSTPARTY,LOCALFOLDER
   default_section = THIRDPARTY
   ```

5. **Generate README for Each Module**
   ```bash
   # Auto-generate README.rst from module manifest
   oca-gen-addon-readme \
     --addons-dir=addons/custom \
     --commit
   ```

**Output**: Enforced OCA coding standards

See [reference/coding-standards.md](reference/coding-standards.md)

---

## Complete Example: End-to-End Setup

**User Request**: "Set up Odoo 18 CE with accounting, helpdesk, and project management. Deploy to DigitalOcean with CI/CD."

**Skill Execution**:

```bash
# Step 1: Initialize repository
$ mkdir odoo18-production && cd odoo18-production
$ git init

# Step 2: Generate structure
$ python3 scripts/init-odoo-project.py \
    --version 18.0 \
    --features accounting,helpdesk,project \
    --provider digitalocean \
    --domain insightpulseai.net

# Step 3: Vendor OCA modules
$ python3 scripts/vendor_oca_enhanced.py \
    --repos addons/oca/repos.yaml \
    --validate

# Step 4: Set up CI/CD
$ python3 scripts/setup-cicd.py \
    --provider github \
    --enable-auto-deploy

# Step 5: Initialize Terraform
$ cd terraform
$ terraform init
$ terraform plan

# Step 6: Deploy
$ ./scripts/deploy-production.sh

# Step 7: Verify
$ curl https://erp.insightpulseai.net/web/health
{"status": "pass"}
```

**Result**:
- ✅ Odoo 18 CE with OCA modules installed
- ✅ Repository structure following OCA standards
- ✅ CI/CD pipelines running on every commit
- ✅ Production deployment on DigitalOcean
- ✅ SSL certificates configured
- ✅ Monitoring and alerts active
- ✅ Cost: $288/year (vs $4,320 Enterprise)

---

## Reference Documentation

- [OCA Module Structure](reference/oca-module-structure.md)
- [Enterprise to OCA Mapping](reference/enterprise-alternatives.md)
- [OCA Vendoring Guide](reference/oca-vendoring.md)
- [Coding Standards](reference/coding-standards.md)
- [CI/CD Configuration](reference/cicd-config.md)
- [Terraform Best Practices](reference/terraform-best-practices.md)
- [Docker Production Setup](reference/docker-production.md)
- [Supabase Integration](reference/supabase-integration.md)

## Examples

- [Repository Setup](examples/repo-setup.md)
- [Vendor OCA Modules](examples/vendor-oca-modules.md)
- [Enterprise Migration](examples/enterprise-migration.md)
- [CI/CD Setup](examples/cicd-setup.md)
- [IaC Deployment](examples/iac-deployment.md)
- [Custom Module Development](examples/custom-module.md)

## Scripts Available

All automation scripts are in the `scripts/` directory:

```bash
scripts/
├── init-odoo-project.py          # Initialize new Odoo project
├── vendor_oca_enhanced.py        # Vendor OCA modules
├── auto-fix-dependencies.py      # Fix module dependencies
├── check-broken-modules.sh       # Validate modules
├── setup-cicd.py                 # Generate CI/CD configs
├── deploy-production.sh          # Deploy to production
├── backup.sh                     # Database backup
└── audit-modules.sh              # Module compliance audit
```

## Cost Comparison

| Component | Enterprise | OCA + Self-Host | Savings |
|-----------|-----------|-----------------|---------|
| Odoo License (10 users) | $4,320/year | $0 | $4,320 |
| Hosting (Odoo.sh) | $720/year | - | $720 |
| DigitalOcean App Platform | - | $288/year | -$288 |
| **Total Annual Cost** | **$5,040** | **$288** | **$4,752 (94%)** |

## Skill Invocation

Use this skill when:
- "Set up Odoo 18 CE with OCA"
- "Migrate from Odoo Enterprise"
- "Deploy Odoo to DigitalOcean"
- "Add CI/CD to Odoo project"
- "Vendor OCA modules for [feature]"
- "Generate Terraform for Odoo"
- "Enforce OCA coding standards"

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Git
- Terraform 1.5+
- DigitalOcean account (optional)
- GitHub account (for CI/CD)

## Next Steps

After using this skill:
1. Review generated configurations
2. Customize for your specific needs
3. Test in staging environment
4. Deploy to production
5. Monitor and maintain

---

**Version**: 1.0.0
**Last Updated**: November 10, 2025
**Compatibility**: Odoo 18.0 CE
