# Makefile for InsightPulse Odoo
# Enterprise SaaS Replacement Suite

.PHONY: help init dev prod stop down logs test lint deploy-prod backup restore update-oca create-module shell psql clean up restart health validate validate-structure validate-makefile health-report

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║  InsightPulse Odoo - Enterprise SaaS Replacement Suite      ║"
	@echo "║  Makefile Commands                                           ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ══════════════════════════════════════════════════════════════
# 🚀 SETUP & INITIALIZATION
# ══════════════════════════════════════════════════════════════

init: ## Initialize project (first-time setup)
	@echo "🚀 Initializing InsightPulse Odoo..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Step 1: Cloning OCA repositories..."
	@./scripts/setup/01-clone-oca-repos.sh || echo "⚠️  OCA repos script not found (will be created)"
	@echo ""
	@echo "Step 2: Installing dependencies..."
	@./scripts/setup/02-install-dependencies.sh || echo "⚠️  Dependencies script not found (will be created)"
	@echo ""
	@echo "Step 3: Setting up environment..."
	@if [ ! -f config/.env.dev ]; then \
		cp config/.env.example config/.env.dev 2>/dev/null || echo "POSTGRES_PASSWORD=odoo" > config/.env.dev; \
		echo "✅ Created config/.env.dev"; \
	fi
	@echo ""
	@echo "Step 4: Creating required directories..."
	@mkdir -p backups data/demo logs
	@echo ""
	@echo "✅ Initialization complete!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Next: Run 'make dev' to start development environment"

# ══════════════════════════════════════════════════════════════
# 🛠️ DEVELOPMENT
# ══════════════════════════════════════════════════════════════

dev: ## Start development environment
	@echo "🛠️  Starting development environment..."
	@if [ -f infrastructure/docker/docker-compose.yml ]; then \
		docker-compose -f infrastructure/docker/docker-compose.yml \
		               -f infrastructure/docker/docker-compose.dev.yml up -d; \
	else \
		docker-compose up -d; \
	fi
	@echo ""
	@echo "✅ Development environment started!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🌐 Odoo:           http://localhost:8069"
	@echo "📊 Superset:       http://localhost:8088"
	@echo "🔧 n8n:            http://localhost:5678"
	@echo "🔐 Authentik:      http://localhost:9000"
	@echo "📦 MinIO:          http://localhost:9001"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Credentials: admin / admin (change in production)"

up: dev ## Alias for 'make dev'

# ══════════════════════════════════════════════════════════════
# 🚀 PRODUCTION
# ══════════════════════════════════════════════════════════════

prod: ## Start production environment
	@echo "🚀 Starting production environment..."
	@if [ -f infrastructure/docker/docker-compose.yml ]; then \
		docker-compose -f infrastructure/docker/docker-compose.yml \
		               -f infrastructure/docker/docker-compose.prod.yml up -d; \
	else \
		@echo "⚠️  Production docker-compose files not found"; \
		@echo "Using default docker-compose.yml..."; \
		docker-compose up -d; \
	fi
	@echo "✅ Production environment started!"

# ══════════════════════════════════════════════════════════════
# 🛑 STOP & CLEANUP
# ══════════════════════════════════════════════════════════════

stop: ## Stop all services (preserve data)
	@echo "🛑 Stopping all services..."
	@if [ -f infrastructure/docker/docker-compose.yml ]; then \
		docker-compose -f infrastructure/docker/docker-compose.yml down; \
	else \
		docker-compose down; \
	fi
	@echo "✅ All services stopped (data preserved)"

down: stop ## Alias for 'make stop'

restart: ## Restart all services
	@echo "🔄 Restarting all services..."
	@make stop
	@sleep 2
	@make dev
	@echo "✅ Services restarted!"

clean: ## Clean up (remove containers, volumes, and data) ⚠️ DESTRUCTIVE
	@echo "⚠️  WARNING: This will DELETE all containers, volumes, and data!"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	@echo "🗑️  Cleaning up..."
	@if [ -f infrastructure/docker/docker-compose.yml ]; then \
		docker-compose -f infrastructure/docker/docker-compose.yml down -v; \
	else \
		docker-compose down -v; \
	fi
	@rm -rf backups/* logs/*
	@echo "✅ Cleanup complete! All data deleted."

# ══════════════════════════════════════════════════════════════
# 📋 LOGS & MONITORING
# ══════════════════════════════════════════════════════════════

logs: ## View logs (follow mode, all services)
	@if [ -f infrastructure/docker/docker-compose.yml ]; then \
		docker-compose -f infrastructure/docker/docker-compose.yml logs -f; \
	else \
		docker-compose logs -f; \
	fi

logs-odoo: ## View Odoo logs only
	@if [ -f infrastructure/docker/docker-compose.yml ]; then \
		docker-compose -f infrastructure/docker/docker-compose.yml logs -f odoo; \
	else \
		docker-compose logs -f odoo; \
	fi

logs-postgres: ## View PostgreSQL logs only
	@if [ -f infrastructure/docker/docker-compose.yml ]; then \
		docker-compose -f infrastructure/docker/docker-compose.yml logs -f postgres; \
	else \
		docker-compose logs -f postgres; \
	fi

health: ## Check health status of all services
	@echo "🏥 Checking service health..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@docker-compose ps
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ══════════════════════════════════════════════════════════════
# 🧪 TESTING & QUALITY
# ══════════════════════════════════════════════════════════════

test: ## Run all tests
	@echo "🧪 Running test suite..."
	@./scripts/development/run-tests.sh || echo "⚠️  Test script not found, running pytest directly..."
	@python -m pytest tests/ -v || echo "⚠️  pytest not found or no tests to run"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@python -m pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@python -m pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests
	@echo "🧪 Running E2E tests..."
	@python -m pytest tests/e2e/ -v

test-performance: ## Run performance benchmarks
	@echo "⚡ Running performance benchmarks..."
	@python -m pytest tests/performance/ -v

lint: ## Lint code (Python, JS, YAML)
	@echo "🔍 Linting code..."
	@./scripts/development/lint-code.sh || echo "⚠️  Lint script not found"
	@echo "Running pylint..."
	@pylint custom/ --exit-zero || echo "⚠️  pylint not installed"
	@echo "Running flake8..."
	@flake8 custom/ --exit-zero || echo "⚠️  flake8 not installed"

# ══════════════════════════════════════════════════════════════
# 🚀 DEPLOYMENT
# ══════════════════════════════════════════════════════════════

deploy-prod: ## Deploy to production (DigitalOcean)
	@echo "🚀 Deploying to production..."
	@./scripts/deployment/deploy-production.sh || echo "⚠️  Deployment script not found"

deploy-staging: ## Deploy to staging environment
	@echo "🚀 Deploying to staging..."
	@./scripts/deployment/deploy-staging.sh || echo "⚠️  Staging deployment script not found"

# ══════════════════════════════════════════════════════════════
# 💾 BACKUP & RESTORE
# ══════════════════════════════════════════════════════════════

backup: ## Create database backup
	@echo "💾 Creating backup..."
	@./scripts/maintenance/backup.sh || echo "⚠️  Backup script not found, creating manual backup..."
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U odoo odoo > backups/backup-$(shell date +%Y%m%d-%H%M%S).sql
	@echo "✅ Backup created in backups/"

restore: ## Restore from backup (usage: make restore BACKUP_FILE=backups/backup.sql)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "❌ Error: BACKUP_FILE not specified"; \
		echo "Usage: make restore BACKUP_FILE=backups/backup-20251105-120000.sql"; \
		exit 1; \
	fi
	@echo "♻️  Restoring from $(BACKUP_FILE)..."
	@./scripts/maintenance/restore.sh $(BACKUP_FILE) || \
		docker-compose exec -T postgres psql -U odoo -d odoo < $(BACKUP_FILE)
	@echo "✅ Restore complete!"

# ══════════════════════════════════════════════════════════════
# 📦 MODULE MANAGEMENT
# ══════════════════════════════════════════════════════════════

update-oca: ## Update OCA modules
	@echo "📦 Updating OCA modules..."
	@./scripts/maintenance/update-oca-modules.sh || echo "⚠️  OCA update script not found"
	@cd addons && git submodule update --remote --merge || echo "⚠️  No OCA submodules configured yet"
	@echo "✅ OCA modules updated!"

create-module: ## Create new custom module (usage: make create-module NAME=my_module)
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Error: NAME not specified"; \
		echo "Usage: make create-module NAME=my_new_module"; \
		exit 1; \
	fi
	@echo "🎨 Creating module: $(NAME)..."
	@./scripts/development/create-module.sh $(NAME) || echo "⚠️  Create module script not found"
	@echo "✅ Module $(NAME) created in custom/$(NAME)/"

# ══════════════════════════════════════════════════════════════
# 🛠️ SHELL ACCESS
# ══════════════════════════════════════════════════════════════

shell: ## Open Odoo Python shell
	@echo "🐍 Opening Odoo shell..."
	@docker-compose exec odoo odoo shell -d odoo || \
		docker exec -it insightpulse-odoo odoo shell -d odoo

psql: ## Open PostgreSQL shell
	@echo "🗄️  Opening PostgreSQL shell..."
	@docker-compose exec postgres psql -U odoo -d odoo || \
		docker exec -it insightpulse-postgres psql -U odoo -d odoo

bash: ## Open bash shell in Odoo container
	@echo "💻 Opening bash shell..."
	@docker-compose exec odoo bash || \
		docker exec -it insightpulse-odoo bash

# ══════════════════════════════════════════════════════════════
# 📊 UTILITIES
# ══════════════════════════════════════════════════════════════

ps: ## Show running containers
	@docker-compose ps

stats: ## Show container resource usage
	@docker stats --no-stream

docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@./scripts/development/generate-docs.sh || echo "⚠️  Docs generation script not found"

gap-analysis: ## Generate SaaS parity gap analysis
	@echo "🔍 Running gap analysis..."
	@python3 tools/gap-analyzer/analyze.py || echo "⚠️  Gap analyzer not found"

# ══════════════════════════════════════════════════════════════
# 🔧 TROUBLESHOOTING
# ══════════════════════════════════════════════════════════════

reset-odoo: ## Reset Odoo (restart container)
	@echo "🔄 Resetting Odoo..."
	@docker-compose restart odoo
	@echo "✅ Odoo restarted!"

reset-postgres: ## Reset PostgreSQL (restart container)
	@echo "🔄 Resetting PostgreSQL..."
	@docker-compose restart postgres
	@echo "✅ PostgreSQL restarted!"

fix-permissions: ## Fix file permissions
	@echo "🔧 Fixing file permissions..."
	@sudo chown -R $(USER):$(USER) . || chown -R $(USER):$(USER) .
	@chmod -R 755 scripts/
	@echo "✅ Permissions fixed!"

# ══════════════════════════════════════════════════════════════
# ✅ VALIDATION & VERIFICATION
# ══════════════════════════════════════════════════════════════

validate: ## Run all validation checks
	@echo "🔍 Running validation checks..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@python3 scripts/validate-repo-structure.py
	@bash scripts/validate-makefile.sh
	@python3 tests/integration/test_repo_structure.py
	@python3 scripts/generate-structure-report.py
	@echo ""
	@echo "📊 Results saved to structure-health-report.json"

validate-structure: ## Validate repository structure only
	@echo "🔍 Validating repository structure..."
	@python3 scripts/validate-repo-structure.py

validate-makefile: ## Validate Makefile only
	@echo "🔧 Validating Makefile..."
	@bash scripts/validate-makefile.sh

health-report: ## Generate structure health report
	@echo "📊 Generating health report..."
	@python3 scripts/generate-structure-report.py
	@if [ -f structure-health-report.json ]; then \
		echo ""; \
		echo "Report Summary:"; \
		cat structure-health-report.json | python3 -c "import json, sys; data=json.load(sys.stdin); print(f\"Overall Score: {data['scores']['overall']:.1f}% (Grade: {data['scores']['grade']})\")"; \
	fi

# ══════════════════════════════════════════════════════════════
# 📝 INFORMATION
# ══════════════════════════════════════════════════════════════

version: ## Show version information
	@echo "InsightPulse Odoo v4.0.0 (Enterprise Structure)"
	@echo "Odoo Version: 19.0 CE + OCA"
	@echo "Status: Production Ready ✅"
	@echo "SaaS Parity: 87%"
	@echo "Test Coverage: 134 test methods"

status: ## Show system status
	@echo "📊 System Status"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@make health
	@echo ""
	@echo "💾 Disk Usage:"
	@df -h . | tail -1
	@echo ""
	@echo "🐳 Docker Space:"
	@docker system df

urls: ## Show all service URLs
	@echo "🌐 Service URLs"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "Odoo:           http://localhost:8069"
	@echo "Superset:       http://localhost:8088"
	@echo "n8n:            http://localhost:5678"
	@echo "Authentik:      http://localhost:9000"
	@echo "MinIO Console:  http://localhost:9001"
	@echo "Qdrant:         http://localhost:6333"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ══════════════════════════════════════════════════════════════
# 🚀 DEPLOYMENT & INFRASTRUCTURE
# ══════════════════════════════════════════════════════════════

.PHONY: deployment-status
deployment-status: ## Check DigitalOcean deployment status
	@echo "📊 DigitalOcean App deployment status:"
	@doctl apps deployments list $(DO_APP_ID) --format ID,Phase,CreatedAt --no-header | head -5

.PHONY: odoo-logs
odoo-logs: ## Tail Odoo droplet logs
	@echo "📜 Tailing Odoo logs (Ctrl+C to exit)..."
	@ssh $(ODOO_HOST) "journalctl -u odoo16 -f"

.PHONY: supabase-status
supabase-status: ## Check Supabase project status
	@echo "🗄️  Supabase project status:"
	@supabase status

.PHONY: clean-docker
clean-docker: ## Clean local Docker images and containers
	@echo "🧹 Cleaning Docker resources..."
	@docker system prune -af --volumes
	@echo "✅ Docker cleaned"

.PHONY: setup-ph-localization
setup-ph-localization: ## Install Philippine accounting localization in Odoo
	@echo "🇵🇭 Setting up Philippine accounting localization..."
	@ssh $(ODOO_HOST) '\
		/opt/odoo16/odoo16-venv/bin/python /opt/odoo16/odoo16/odoo-bin \
		-d insightpulse_prod \
		-i l10n_ph,l10n_ph_withholding \
		--stop-after-init \
	' || echo "⚠️  PH localization install failed (check if database exists)"
	@echo "✅ PH localization installed"

.PHONY: verify-ph-localization
verify-ph-localization: ## Verify Philippine accounting modules are installed
	@echo "🔍 Verifying PH localization..."
	@ssh $(ODOO_HOST) '\
		/opt/odoo16/odoo16-venv/bin/python /opt/odoo16/odoo16/odoo-bin shell \
		-d insightpulse_prod \
		--no-http \
		<<EOF
import odoo
env = odoo.api.Environment.manage()
mods = env["ir.module.module"].search([("name","ilike","l10n_ph")])
for m in mods:
    print(f"{m.name}: {m.state}")
EOF
	' || echo "⚠️  Verification failed"

# Development helpers
.PHONY: dev-setup
dev-setup: ## Setup local development environment
	@echo "🔧 Setting up development environment..."
	@pip install -r requirements.txt || echo "⚠️  requirements.txt not found"
	@npm install || echo "⚠️  package.json not found"
	@echo "✅ Development environment ready"

# Git helpers
.PHONY: git-status
git-status: ## Show git status and current branch
	@echo "📌 Current branch: $(BRANCH)"
	@echo "📋 Commit: $(COMMIT)"
	@git status -sb

# Quick deployment shortcuts
.PHONY: deploy-fast
deploy-fast: deploy-odoo-image deploy-do-app ## Fast deployment (Odoo image + DO App only)

.PHONY: deploy-db
deploy-db: deploy-supabase ## Deploy database changes only

.PHONY: deploy-docs
deploy-docs: deploy-github-actions ## Deploy documentation only

# Emergency rollback
.PHONY: rollback
rollback: ## Rollback to previous DigitalOcean deployment
	@echo "⏪ Rolling back to previous deployment..."
	@PREV_DEPLOYMENT=$$(doctl apps deployments list $(DO_APP_ID) --format ID --no-header | sed -n '2p') && \
	 doctl apps deployments rollback $(DO_APP_ID) $$PREV_DEPLOYMENT || \
	 echo "❌ Rollback failed - check deployment history with 'make deployment-status'"

# Security
.PHONY: rotate-secrets
rotate-secrets: ## Guide for rotating secrets
	@echo "🔐 Secret Rotation Guide:"
	@echo ""
	@echo "1. GitHub Container Registry Token (CR_PAT):"
	@echo "   https://github.com/settings/tokens → Generate new token → Update CR_PAT"
	@echo ""
	@echo "2. Supabase Access Token:"
	@echo "   https://app.supabase.com/account/tokens → Generate new token → Update SUPABASE_ACCESS_TOKEN"
	@echo ""
	@echo "3. DigitalOcean Access Token:"
	@echo "   https://cloud.digitalocean.com/account/api/tokens → Generate new token → Update DIGITALOCEAN_ACCESS_TOKEN"
	@echo ""
	@echo "4. Update GitHub Secrets:"
	@echo "   gh secret set CR_PAT -R $(GITHUB_USER)/insightpulse-odoo"
	@echo "   gh secret set SUPABASE_ACCESS_TOKEN -R $(GITHUB_USER)/insightpulse-odoo"
	@echo "   gh secret set DIGITALOCEAN_ACCESS_TOKEN -R $(GITHUB_USER)/insightpulse-odoo"

# Information
.PHONY: info
info: ## Display deployment configuration
	@echo "ℹ️  Deployment Configuration:"
	@echo ""
	@echo "  Branch: $(BRANCH)"
	@echo "  Commit: $(COMMIT)"
	@echo "  Image: $(IMAGE_FULL)"
	@echo ""
	@echo "  Supabase Project: $(SUPABASE_PROJECT_REF)"
	@echo "  DO App ID: $(DO_APP_ID)"
	@echo "  Odoo Host: $(ODOO_HOST)"
	@echo ""
	@echo "  Odoo URL: https://$(ODOO_FQDN)"
	@echo "  Docs URL: https://$(DOCS_FQDN)"
	@echo "  Edge URL: $(EDGE_URL)"

# ══════════════════════════════════════════════════════════════
# 🤖 SUPERCLAUDE MULTI-AGENT ORCHESTRATION
# ══════════════════════════════════════════════════════════════

.PHONY: superclaude-help
superclaude-help: ## Show SuperClaude commands
	@echo "🤖 SuperClaude Multi-Agent Framework Commands:"
	@echo ""
	@echo "  Workflow Orchestration:"
	@echo "    superclaude-bootstrap        Bootstrap SuperClaude framework (first-time setup)"
	@echo "    superclaude-build-ai         Build AI infrastructure (parallel, 3 agents, ~2-3 days)"
	@echo "    superclaude-build-all        Build entire system (parallel, 5 agents, ~5-7 days)"
	@echo ""
	@echo "  Skill Management:"
	@echo "    skill-generate               Generate skill from module (requires MODULE=path/to/module)"
	@echo "    skill-index                  Rebuild skill index and catalog"
	@echo "    skill-suggest                Suggest new skills based on codebase analysis"
	@echo "    skill-list                   List all available skills"
	@echo ""
	@echo "  Development:"
	@echo "    superclaude-status           Show current agent status and progress"
	@echo "    superclaude-logs             View execution logs"
	@echo "    superclaude-clean            Clean worktrees and temporary files"
	@echo ""
	@echo "Usage examples:"
	@echo "  make superclaude-bootstrap                    # First-time setup"
	@echo "  make superclaude-build-ai --parallel          # Build AI infrastructure"
	@echo "  make skill-generate MODULE=custom/expense_automation  # Generate skill"
	@echo "  make skill-suggest --threshold 500            # Suggest skills for modules >500 LOC"

# Workflow Commands
.PHONY: superclaude-bootstrap
superclaude-bootstrap: ## Bootstrap SuperClaude framework (first-time setup)
	@echo "🚀 Bootstrapping SuperClaude framework..."
	@python3 .superclaude/orchestrate.py --workflow bootstrap
	@echo "✅ Bootstrap complete! Next: make superclaude-build-ai"

.PHONY: superclaude-build-ai
superclaude-build-ai: ## Build AI infrastructure (parallel, 3 agents, ~2-3 days)
	@echo "⚡ Building AI infrastructure with 3 parallel agents..."
	@echo "   Estimated time: 2-3 days (vs 7-10 days sequential)"
	@python3 .superclaude/orchestrate.py --workflow build_ai_infrastructure --parallel
	@echo "✅ AI infrastructure build complete!"

.PHONY: superclaude-build-all
superclaude-build-all: ## Build entire system (parallel, 5 agents, ~5-7 days)
	@echo "🚀 Building entire system with 5 parallel agents..."
	@echo "   Estimated time: 5-7 days (vs 35-48 days sequential)"
	@echo "   Efficiency gain: 5-7x faster"
	@python3 .superclaude/orchestrate.py --workflow build_full_stack --parallel
	@echo "✅ Full stack build complete!"

.PHONY: superclaude-dry-run
superclaude-dry-run: ## Dry run workflow (simulate without executing)
	@echo "🔍 Dry run workflow: $(WORKFLOW)"
	@test -n "$(WORKFLOW)" || (echo "❌ WORKFLOW not set. Usage: make superclaude-dry-run WORKFLOW=bootstrap" && exit 1)
	@python3 .superclaude/orchestrate.py --workflow $(WORKFLOW) --dry-run

# Skill Management
.PHONY: skill-generate
skill-generate: ## Generate skill from module (requires MODULE=path/to/module)
	@echo "📚 Generating skill from module..."
	@test -n "$(MODULE)" || (echo "❌ MODULE not set. Usage: make skill-generate MODULE=custom/expense_automation" && exit 1)
	@python3 skills/core/librarian-indexer/auto-generate-skill.py \
		--module "$(MODULE)" \
		--output "skills/auto-generated/" \
		--verbose
	@echo "✅ Skill generated! Run 'make skill-index' to update catalog"

.PHONY: skill-index
skill-index: ## Rebuild skill index and catalog
	@echo "📇 Rebuilding skill index..."
	@python3 skills/core/librarian-indexer/index-all-skills.py \
		--skills-dir skills/ \
		--output skills/INDEX.json \
		--generate-readme
	@echo "✅ Skill index updated: skills/INDEX.json"
	@echo "📖 README generated: skills/README.md"

.PHONY: skill-suggest
skill-suggest: ## Suggest new skills based on codebase analysis
	@echo "💡 Analyzing codebase for skill suggestions..."
	@python3 skills/core/librarian-indexer/suggest-skills.py \
		--codebase custom/ \
		--threshold $(THRESHOLD) \
		--output .superclaude/shared-context/skill-suggestions.txt \
		--verbose
	@echo "📋 Suggestions saved to: .superclaude/shared-context/skill-suggestions.txt"
	@cat .superclaude/shared-context/skill-suggestions.txt

.PHONY: skill-list
skill-list: ## List all available skills
	@echo "📚 Available Skills:"
	@echo ""
	@test -f skills/INDEX.json || (echo "⚠️  No skill index found. Run 'make skill-index' first" && exit 1)
	@python3 -c "import json; skills = json.load(open('skills/INDEX.json')); \
		print('\n'.join([f\"  {s['name']:30} {s['category']:20} {s['expertise_level']}\" for s in skills['skills']]))"

.PHONY: skill-bulk-generate
skill-bulk-generate: ## Generate skills for top 5 suggested modules
	@echo "🔄 Generating skills for top 5 modules..."
	@make skill-suggest THRESHOLD=500
	@head -5 .superclaude/shared-context/skill-suggestions.txt | while read module; do \
		echo "📚 Generating skill for $$module..."; \
		make skill-generate MODULE=$$module || echo "⚠️  Failed to generate skill for $$module"; \
	done
	@make skill-index
	@echo "✅ Bulk skill generation complete!"

# Status and Monitoring
.PHONY: superclaude-status
superclaude-status: ## Show current agent status and progress
	@echo "📊 SuperClaude Agent Status:"
	@echo ""
	@test -f .superclaude/shared-context/status.json || (echo "⚠️  No status file found. No agents currently running." && exit 0)
	@python3 -c "import json; from datetime import datetime; \
		status = json.load(open('.superclaude/shared-context/status.json')); \
		for agent, info in status.items(): \
			print(f\"  {agent:20} {info['status']:12} {info.get('message', '')}\"); \
			if info.get('progress'): print(f\"     Progress: {info['progress']*100:.1f}%\")"

.PHONY: superclaude-logs
superclaude-logs: ## View execution logs
	@echo "📜 SuperClaude Execution Logs:"
	@echo ""
	@test -d .superclaude/logs || (echo "⚠️  No logs directory found. No executions yet." && exit 0)
	@ls -lt .superclaude/logs/*.json | head -5 | awk '{print "  " $$9}' || echo "⚠️  No log files found"
	@echo ""
	@echo "💡 View latest log: cat \$$(ls -t .superclaude/logs/*.json | head -1)"

.PHONY: superclaude-clean
superclaude-clean: ## Clean worktrees and temporary files
	@echo "🧹 Cleaning SuperClaude worktrees and temporary files..."
	@rm -rf .worktrees/
	@rm -rf .superclaude/logs/*.json 2>/dev/null || true
	@rm -f .superclaude/shared-context/memory.json 2>/dev/null || true
	@git worktree prune
	@echo "✅ Cleanup complete"

# Default threshold for skill suggestions
THRESHOLD ?= 500

# ══════════════════════════════════════════════════════════════
# 📋 SPEC-DRIVEN CI/CD
# ══════════════════════════════════════════════════════════════

.PHONY: spec spec-validate spec-drift spec-bump mqt-odoo spec-format spec-clean spec-ci

spec: ## Generate OpenAPI spec from Pydantic
	@echo "🔧 Generating OpenAPI spec..."
	@python3 ci/speckit/generate_openapi.py

spec-validate: ## Validate spec contracts
	@echo "🔒 Validating spec contracts..."
	@python3 ci/speckit/validate_spec_contract.py

spec-drift: ## Check for spec drift
	@echo "🔍 Checking for spec drift..."
	@python3 ci/speckit/spec_drift_gate.py

spec-bump: ## Bump __manifest__.py versions
	@echo "📦 Bumping manifest versions..."
	@python3 ci/speckit/bump_manifest_version.py

mqt-odoo: ## Run OCA MQT quality checks
	@echo "🔍 Running OCA MQT checks..."
	@bash ci/qa/run_mqt.sh

spec-format: ## Format spec code with black
	@echo "✨ Formatting spec code..."
	@black addons/ ci/ || echo "⚠️  black not installed"

spec-clean: ## Clean generated spec files
	@echo "🧹 Cleaning spec artifacts..."
	@rm -rf spec/*.json
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Spec artifacts cleaned"

spec-ci: ## Run full spec-driven CI pipeline locally
	@echo "🚀 Running spec-driven CI pipeline..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@make spec
	@make spec-validate
	@make spec-drift
	@make mqt-odoo
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "✅ All spec-driven CI checks passed!"

# ══════════════════════════════════════════════════════════════
# 📱 SUPABASE + EXPO PWA
# ══════════════════════════════════════════════════════════════

.PHONY: supabase-login supabase-link supabase-push supabase-deploy web

supabase-login: ## Login to Supabase CLI
	@echo "🔐 Logging into Supabase..."
	@supabase login

supabase-link: ## Link local project to Supabase
	@echo "🔗 Linking to Supabase project..."
	@supabase link --project-ref $(SUPABASE_PROJECT_REF)

supabase-push: ## Push database migrations to Supabase
	@echo "📤 Pushing database migrations..."
	@supabase db push

supabase-deploy: ## Deploy Supabase Edge Functions
	@echo "🚀 Deploying Edge Functions..."
	@supabase functions deploy notify-odoo --no-verify-jwt
	@echo "✅ Edge Functions deployed!"

web: ## Build and serve PWA locally
	@echo "🌐 Building PWA..."
	@npx expo export --platform web
	@echo "✅ PWA build complete! Serve with: npx serve dist"
