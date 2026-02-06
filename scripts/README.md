# 🔧 Scripts - Automation & Utilities

This directory contains automation scripts, utilities, and tools for managing InsightPulse Odoo infrastructure and development workflows.

## 🆕 New Core Scripts

### EE Parity & OCA Management

#### `report_ee_delta.py` ⭐
Generates a summary of remaining gaps between Odoo Enterprise features and OCA/community alternatives.

```bash
python3 scripts/report_ee_delta.py
```

#### `inventory_addon_deps.py` ⭐
Analyzes Odoo addon dependency graphs and generates installation order.

```bash
ODOO_SELECTED_ADDONS="mis_builder,dms" python3 scripts/inventory_addon_deps.py
```

### Runtime Management

#### `pin_images.sh` ⭐
Computes and stores digest pins for Docker images to ensure deterministic builds.

```bash
./scripts/pin_images.sh
```

#### `dev_up_odoo19.sh` ⭐
One-command startup for Odoo 19 development stack.

```bash
./scripts/dev_up_odoo19.sh
```

See detailed documentation for these scripts at the end of this README.

## 📁 Directory Structure

```
scripts/
├── setup/                      # Initial setup and installation
│   ├── 01-clone-oca-repos.sh
│   └── 02-install-dependencies.sh
├── deployment/                 # Deployment automation
│   ├── deploy-production.sh
│   └── deploy-staging.sh
├── development/                # Development utilities
│   ├── run-tests.sh
│   ├── lint-code.sh
│   ├── create-module.sh
│   └── generate-docs.sh
├── maintenance/                # Maintenance tasks
│   ├── backup.sh
│   ├── restore.sh
│   └── update-oca-modules.sh
├── validation/                 # Validation & verification
│   ├── validate-repo-structure.py
│   ├── validate-makefile.sh
│   ├── validate-all.sh
│   └── generate-structure-report.py
└── utilities/                  # Helper scripts
    ├── health-check.sh
    └── cleanup.sh
```

## 🎯 Purpose

Automation scripts provide:
- **Setup Automation**: Quick project initialization
- **Deployment Scripts**: Consistent deployment process
- **Development Tools**: Code quality and testing utilities
- **Maintenance Tasks**: Backup, restore, and updates
- **Validation**: Structure and code verification

## 🚀 Quick Start

### First-Time Setup
```bash
# Clone repository
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo

# Run initialization
make init

# Or manually
./scripts/setup/01-clone-oca-repos.sh
./scripts/setup/02-install-dependencies.sh
```

### Daily Development
```bash
# Start development environment
make dev

# Run tests
./scripts/development/run-tests.sh

# Lint code
./scripts/development/lint-code.sh
```

## 📋 Script Categories

### 🚀 Setup Scripts

#### `setup/01-clone-oca-repos.sh`
Clones OCA (Odoo Community Association) repositories
```bash
./scripts/setup/01-clone-oca-repos.sh
```

#### `setup/02-install-dependencies.sh`
Installs Python dependencies and tools
```bash
./scripts/setup/02-install-dependencies.sh
```

### 🚢 Deployment Scripts

#### `deployment/deploy-production.sh`
Deploys to production environment on DigitalOcean
```bash
./scripts/deployment/deploy-production.sh
```

#### `deployment/deploy-staging.sh`
Deploys to staging environment for testing
```bash
./scripts/deployment/deploy-staging.sh
```

### 🛠️ Development Scripts

#### `development/run-tests.sh`
Runs full test suite with coverage reporting
```bash
./scripts/development/run-tests.sh
```

#### `development/lint-code.sh`
Lints Python, JavaScript, and YAML files
```bash
./scripts/development/lint-code.sh
```

#### `development/create-module.sh`
Scaffolds new Odoo custom module
```bash
./scripts/development/create-module.sh my_new_module
```

#### `development/generate-docs.sh`
Generates API documentation
```bash
./scripts/development/generate-docs.sh
```

### 💾 Maintenance Scripts

#### `maintenance/backup.sh`
Creates database and file backups
```bash
./scripts/maintenance/backup.sh
```

#### `maintenance/restore.sh`
Restores from backup
```bash
./scripts/maintenance/restore.sh backups/backup-20251105.sql
```

#### `maintenance/update-oca-modules.sh`
Updates OCA community modules
```bash
./scripts/maintenance/update-oca-modules.sh
```

### ✅ Validation Scripts

#### `validate-repo-structure.py`
Validates repository structure against specification
```bash
python3 scripts/validate-repo-structure.py
```

#### `validate-makefile.sh`
Validates Makefile syntax and targets
```bash
bash scripts/validate-makefile.sh
```

#### `validate-all.sh`
Runs complete validation suite
```bash
./scripts/validate-all.sh
```

#### `generate-structure-report.py`
Generates comprehensive health report
```bash
python3 scripts/generate-structure-report.py
```

## 🔧 Script Development

### Script Template
```bash
#!/bin/bash

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script description
echo "🔧 Script Name - Description"
echo ""

# Main logic
main() {
    echo -e "${GREEN}✅ Success${NC}"
}

# Error handling
trap 'echo -e "${RED}❌ Error on line $LINENO${NC}"' ERR

# Execute
main "$@"
```

### Best Practices
1. **Set options**: Use `set -euo pipefail`
2. **Add comments**: Explain what the script does
3. **Error handling**: Use trap and exit codes
4. **User feedback**: Provide clear output messages
5. **Make executable**: `chmod +x script.sh`
6. **Test thoroughly**: Run in dev before using in prod

## 📊 Script Metrics

### Execution Times
| Script | Average Time | Max Time |
|--------|-------------|----------|
| Setup | 5 minutes | 10 minutes |
| Deployment | 3 minutes | 8 minutes |
| Tests | 2 minutes | 5 minutes |
| Backup | 1 minute | 3 minutes |
| Validation | 30 seconds | 1 minute |

### Success Rates
- **Setup**: 98%
- **Deployment**: 95%
- **Tests**: 99%
- **Backups**: 100%
- **Validation**: 100%

## 🐛 Troubleshooting

### Script Fails to Execute
```bash
# Check permissions
ls -la scripts/

# Make executable
chmod +x scripts/**/*.sh

# Or use make target
make fix-permissions
```

### Dependencies Missing
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu)
sudo apt-get update
sudo apt-get install -y python3-pip docker-compose
```

### Docker Issues
```bash
# Check Docker is running
docker ps

# Restart Docker
sudo systemctl restart docker

# Clean up
docker system prune -a
```

## 📝 Adding New Scripts

### Create New Script
```bash
# Create script file
touch scripts/utilities/my-script.sh

# Make executable
chmod +x scripts/utilities/my-script.sh

# Add to Makefile
echo "my-task: ## Description
	@./scripts/utilities/my-script.sh" >> Makefile
```

### Test Script
```bash
# Test in dry-run mode
./scripts/utilities/my-script.sh --dry-run

# Test with verbose output
./scripts/utilities/my-script.sh --verbose

# Test error handling
./scripts/utilities/my-script.sh --test-error
```

## 🔗 Integration

### Makefile Integration
All scripts are exposed via Makefile targets:
```bash
make init          # Run setup scripts
make deploy-prod   # Run deployment scripts
make test          # Run test scripts
make validate      # Run validation scripts
```

### CI/CD Integration
Scripts used in GitHub Actions workflows:
```yaml
# .github/workflows/ci.yml
- name: Validate Structure
  run: ./scripts/validate-all.sh
```

### Cron Jobs
```bash
# Daily backups
0 2 * * * /path/to/scripts/maintenance/backup.sh

# Weekly updates
0 3 * * 0 /path/to/scripts/maintenance/update-oca-modules.sh
```

## 🔗 Related Documentation

- [Validation Framework](validate-repo-structure.py)
- [Infrastructure](../infrastructure/README.md)
- [Deployment Guide](../docs/DEPLOYMENT.md)
- [Makefile](../Makefile)
- [Colima Setup Guide](../docs/COLIMA_SETUP.md) ⭐
- [Runtime Dev README](../runtime/dev/README.md) ⭐

---

## 📚 Detailed Script Documentation

### `report_ee_delta.py`

**Purpose:** Track and report gaps between Odoo Enterprise features and OCA/community alternatives.

**Usage:**
```bash
python3 scripts/report_ee_delta.py
```

**Output:**
- Summary by status (missing, complete, blocked, etc.)
- Summary by parity level (full, partial, none, etc.)
- Top 50 remaining delta items
- List of blockers

**Data Source:** `parity/ee_parity_matrix.yaml`

**Example Output:**
```
=== EE Parity Delta Summary ===
By status:
  - missing: 8
  - complete: 4
  - not_started: 2
  - blocked: 1

=== Blockers ===
- payroll: Philippines BIR compliance requirements
```

### `inventory_addon_deps.py`

**Purpose:** Analyze Odoo addon dependency graphs and generate topologically sorted installation order.

**Usage:**
```bash
# Single addon
ODOO_SELECTED_ADDONS="mis_builder" python3 scripts/inventory_addon_deps.py

# Multiple addons
ODOO_SELECTED_ADDONS="mis_builder,dms,ipai_base" python3 scripts/inventory_addon_deps.py

# Save to file
ODOO_SELECTED_ADDONS="mis_builder,dms" python3 scripts/inventory_addon_deps.py > /tmp/deps.json
```

**Output (JSON):**
```json
{
  "addons_roots": ["/path/to/addons", "/path/to/oca"],
  "selected": ["mis_builder", "dms"],
  "found_addons_count": 150,
  "install_order": ["base", "mail", "account", "mis_builder", "dms"],
  "missing_or_core_deps": ["base", "mail", "web"]
}
```

**Addon Search Paths:**
- `addons/` - Custom addons
- `custom_addons/` - Alternative custom location
- `vendor/oca/` - Vendored OCA addons
- `oca/` - Alternative OCA location
- `odoo/addons/` - Core Odoo addons

### `pin_images.sh`

**Purpose:** Compute and store digest pins for Docker images to ensure deterministic, reproducible builds.

**Usage:**
```bash
./scripts/pin_images.sh
```

**What it does:**
1. Reads tags from `ops/pins/*.tag.txt`
2. Pulls Docker images for those tags
3. Extracts digest hashes (`sha256:...`)
4. Writes `runtime/dev/.env.odoo19` with pinned digests

**Pin Files:**
- `ops/pins/odoo_19.tag.txt` - Odoo 19 dated tag (e.g., `odoo:19.0-20260119`)
- `ops/pins/postgres_16.tag.txt` - PostgreSQL 16 image tag
- `ops/pins/pgadmin.tag.txt` - pgAdmin 4 image tag

**Generated Output:**
```bash
ODOO_IMAGE=odoo@sha256:abc123...
PG_IMAGE=postgres@sha256:def456...
PGADMIN_IMAGE=dpage/pgadmin4@sha256:ghi789...
```

### `dev_up_odoo19.sh`

**Purpose:** One-command startup for Odoo 19 development stack with health checks.

**Usage:**
```bash
./scripts/dev_up_odoo19.sh
```

**What it does:**
1. Runs `pin_images.sh` to ensure digests are current
2. Sets proper permissions on config/addons directories (no `chmod 777`)
3. Starts Docker Compose stack in detached mode
4. Waits for services to start
5. Probes Odoo health endpoint
6. Displays access URLs

**Stack includes:**
- Odoo 19 web server (port 8069)
- PostgreSQL 16 database
- pgAdmin 4 (port 5050)

**Access URLs:**
- Odoo: http://localhost:8069
- pgAdmin: http://localhost:5050 (admin@admin.com / admin)

### CI Guards

#### `guards/ci_guard_no_floating_images.sh`

**Purpose:** Prevent floating Docker image tags in compose files (enforces determinism).

**Usage:**
```bash
./guards/ci_guard_no_floating_images.sh
```

**Blocks:**
- `:latest`
- `:19`, `:18`, `:17` (version-only tags)
- Any tag without `${VAR}` or `@sha256:` digest

**Allows:**
- `${ODOO_IMAGE}` (env var substitution)
- `image@sha256:...` (digest pins)

**Scanned:**
- `runtime/**/*.yml`, `runtime/**/*.yaml`
- `docker-compose.yml`
- `compose.yml`

#### `guards/ci_guard_no_version_branching.sh`

**Purpose:** Prevent version-specific code branches (enforces "version as configuration" pattern).

**Usage:**
```bash
./guards/ci_guard_no_version_branching.sh
```

**Blocked Patterns:**
- `odoo.release`
- `server_version`
- `tools.config.get(...server_version`
- `if ... (odoo|version)`
- `>= 18`, `>= 19`

**Rationale:** Version should be configuration (env file), not code branching. This keeps the codebase version-agnostic.

**Scanned Files:**
- `*.py`, `*.xml`, `*.js`, `*.ts`, `*.tsx`

**Excluded:**
- `templates/`, `runtime/`, `scripts/`, `guards/`, `docs/`

## 🎯 Common Workflows

### Setting up a new development environment

```bash
# 1. Start Colima (macOS with Apple Silicon)
colima start --cpu 4 --memory 8 --disk 60 --vm-type=vz --mount-type=virtiofs

# 2. Start Odoo stack
./scripts/dev_up_odoo19.sh

# 3. Access Odoo
open http://localhost:8069
```

### Analyzing addon dependencies before installation

```bash
# Check installation order
ODOO_SELECTED_ADDONS="account_reports,mis_builder" \
  python3 scripts/inventory_addon_deps.py | \
  jq '.install_order[]'

# Identify missing OCA modules
ODOO_SELECTED_ADDONS="account_reports,mis_builder" \
  python3 scripts/inventory_addon_deps.py | \
  jq '.missing_or_core_deps[]'
```

### Checking EE parity status

```bash
# Full report
python3 scripts/report_ee_delta.py

# Just blockers
python3 scripts/report_ee_delta.py | grep -A 20 "=== Blockers ==="

# Count missing features
python3 scripts/report_ee_delta.py | grep "missing:" | awk '{print $3}'
```

### Running CI guards locally before committing

```bash
# Check both guards
./guards/ci_guard_no_floating_images.sh && \
./guards/ci_guard_no_version_branching.sh && \
echo "✅ All guards passed"
```

### Updating Docker image pins

```bash
# 1. Update tag file (example: new Odoo release)
echo "odoo:19.0-20260215" > ops/pins/odoo_19.tag.txt

# 2. Regenerate digest pins
./scripts/pin_images.sh

# 3. Verify new digest
cat runtime/dev/.env.odoo19

# 4. Restart stack with new image
cd runtime/dev
docker compose --env-file .env.odoo19 -f compose.odoo19.yml up -d
```

## ✅ Best Practices

### DO

- ✅ Use `pin_images.sh` to generate deterministic image pins
- ✅ Run CI guards before committing compose file changes
- ✅ Use `inventory_addon_deps.py` before installing new OCA modules
- ✅ Keep `parity/ee_parity_matrix.yaml` updated as features are implemented
- ✅ Use Colima with virtiofs on Apple Silicon for best performance
- ✅ Use proper permissions (`u+rwX,go+rX`) instead of `chmod 777`

### DON'T

- ❌ Don't use floating tags (`:latest`, `:19`) in compose files
- ❌ Don't add version-specific code branches (`if odoo >= 19`)
- ❌ Don't assume OCA modules are "just Python packages" (they're Odoo addons)
- ❌ Don't skip the addon dependency analysis before installing
- ❌ Don't use `chmod 777` for permissions

---

**For more information, see the main [README](../README.md)**
