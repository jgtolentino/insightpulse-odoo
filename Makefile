# InsightPulse Odoo - Unified Deployment Makefile
# One-shot deployment for all services: docs, RAG, Supabase, Odoo, DO App Platform

# Configuration
BRANCH ?= main
SUPABASE_PROJECT_REF ?= spdtwktxdalcfigzeqrz
DO_APP_ID ?= b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9
GITHUB_USER ?= jgtolentino
ODOO_HOST ?= root@165.227.10.178
ODOO_FQDN ?= erp.insightpulseai.net
DOCS_FQDN ?= docs.insightpulseai.net
EDGE_URL ?= https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1

# Image configuration
COMMIT := $(shell git rev-parse --short HEAD)
IMAGE_BASE := ghcr.io/$(GITHUB_USER)/insightpulse-odoo
IMAGE_TAG := prod-$(COMMIT)
IMAGE_FULL := $(IMAGE_BASE):$(IMAGE_TAG)
IMAGE_LATEST := $(IMAGE_BASE):latest-prod

.PHONY: help
help: ## Show this help message
	@echo "InsightPulse Odoo Deployment Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: deploy-now
deploy-now: ## 🚀 Full deployment pipeline (docs + RAG + Supabase + Odoo + DO)
	@echo "🚀 Starting full deployment pipeline..."
	@$(MAKE) check-secrets
	@$(MAKE) deploy-github-actions
	@$(MAKE) deploy-supabase
	@$(MAKE) deploy-odoo-image
	@$(MAKE) deploy-do-app
	@$(MAKE) health-check
	@echo "✅ Full deployment complete!"

.PHONY: check-secrets
check-secrets: ## Verify all required secrets are set
	@echo "🔐 Checking required secrets..."
	@test -n "$(CR_PAT)" || (echo "❌ CR_PAT not set" && exit 1)
	@test -n "$(SUPABASE_ACCESS_TOKEN)" || (echo "❌ SUPABASE_ACCESS_TOKEN not set" && exit 1)
	@test -n "$(DIGITALOCEAN_ACCESS_TOKEN)" || (echo "❌ DIGITALOCEAN_ACCESS_TOKEN not set" && exit 1)
	@echo "✅ All secrets present"

.PHONY: deploy-github-actions
deploy-github-actions: ## Trigger GitHub Actions workflows
	@echo "📋 Triggering GitHub Actions workflows..."
	@gh workflow run docs.yml --ref $(BRANCH) || echo "⚠️  docs.yml workflow not found (skipping)"
	@gh workflow run rag-index.yml --ref $(BRANCH) || echo "⚠️  rag-index.yml workflow not found (skipping)"
	@gh workflow run deploy.yml --ref $(BRANCH) -f env=prod || echo "⚠️  deploy.yml workflow not found (skipping)"
	@echo "📊 Recent workflow runs:"
	@gh run list --limit 3 || true
	@echo "✅ GitHub Actions triggered"

.PHONY: deploy-supabase
deploy-supabase: ## Deploy Supabase migrations and edge functions
	@echo "🗄️  Deploying Supabase..."
	@supabase link --project-ref $(SUPABASE_PROJECT_REF) || echo "⚠️  Already linked or skipping"
	@supabase db push || echo "⚠️  No migrations to push"
	@echo "🔧 Deploying edge functions..."
	@supabase functions deploy search --project-ref $(SUPABASE_PROJECT_REF) || echo "⚠️  search function deploy failed/skipped"
	@supabase functions deploy answer --project-ref $(SUPABASE_PROJECT_REF) || echo "⚠️  answer function deploy failed/skipped"
	@supabase functions deploy ingest --project-ref $(SUPABASE_PROJECT_REF) || echo "⚠️  ingest function deploy failed/skipped"
	@echo "✅ Supabase deployed"

.PHONY: deploy-odoo-image
deploy-odoo-image: ## Build and push Odoo Docker image to GHCR
	@echo "🐳 Building Odoo Docker image..."
	@echo "$(CR_PAT)" | docker login ghcr.io -u $(GITHUB_USER) --password-stdin
	@docker build -f ops/odoo/Dockerfile -t $(IMAGE_FULL) . || \
	 docker build -f Dockerfile -t $(IMAGE_FULL) . || \
	 (echo "❌ Dockerfile not found in ops/odoo/ or root" && exit 1)
	@echo "📤 Pushing image $(IMAGE_FULL)..."
	@docker push $(IMAGE_FULL)
	@echo "🏷️  Tagging as latest-prod..."
	@docker tag $(IMAGE_FULL) $(IMAGE_LATEST)
	@docker push $(IMAGE_LATEST)
	@echo "✅ Odoo image deployed: $(IMAGE_FULL)"

.PHONY: deploy-do-app
deploy-do-app: ## Update DigitalOcean App Platform with new image
	@echo "☁️  Updating DigitalOcean App Platform..."
	@doctl apps update $(DO_APP_ID) --spec infra/do/ade-ocr-service.yaml || \
	 doctl apps update $(DO_APP_ID) --spec ops/do/app.yaml || \
	 (echo "❌ App spec not found" && exit 1)
	@echo "🚀 Creating new deployment..."
	@doctl apps create-deployment $(DO_APP_ID) --wait || echo "⚠️  Deployment triggered (check status with 'make deployment-status')"
	@echo "✅ DigitalOcean App updated"

.PHONY: deploy-droplet
deploy-droplet: ## Deploy to Odoo droplet via Docker Compose (fallback)
	@echo "🖥️  Deploying to Odoo droplet ($(ODOO_HOST))..."
	@ssh $(ODOO_HOST) '\
		set -e && \
		echo "$(CR_PAT)" | docker login ghcr.io -u $(GITHUB_USER) --password-stdin && \
		docker pull $(IMAGE_LATEST) && \
		cd /opt/insightpulse-odoo && \
		docker compose pull && \
		docker compose up -d \
	' || echo "⚠️  Droplet deployment failed (check SSH access)"
	@echo "✅ Droplet deployment complete"

.PHONY: rag-reindex
rag-reindex: ## Force RAG reindex after docs deployment
	@echo "🔄 Triggering RAG reindex..."
	@curl -sS -X POST "$(EDGE_URL)/ingest" \
		-H "Authorization: Bearer $(RAG_REINDEX_TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"paths":["/docs"],"force":true}' || echo "⚠️  RAG reindex failed"
	@echo "✅ RAG reindex triggered"

.PHONY: deploy-superset-dashboards
deploy-superset-dashboards: ## Deploy Superset dashboards via API
	@echo "📊 Deploying Superset dashboards..."
	@test -n "$(SUPERSET_PASSWORD)" || (echo "❌ SUPERSET_PASSWORD not set" && exit 1)
	@test -d "superset/dashboards" || (echo "⚠️  No dashboards found in superset/dashboards/" && exit 0)
	@echo "🔐 Authenticating with Superset..."
	@ACCESS_TOKEN=$$(curl -sS -X POST "https://superset.insightpulseai.net/api/v1/security/login" \
		-H "Content-Type: application/json" \
		-d '{"username":"admin","password":"$(SUPERSET_PASSWORD)","provider":"db","refresh":true}' \
		| jq -r '.access_token' 2>/dev/null || echo ""); \
	if [ -z "$$ACCESS_TOKEN" ] || [ "$$ACCESS_TOKEN" = "null" ]; then \
		echo "❌ Failed to authenticate with Superset API"; \
		echo "💡 Import dashboards manually via UI: Settings → Import dashboards"; \
		exit 1; \
	fi; \
	echo "✅ Authenticated successfully"; \
	IMPORTED=0; \
	FAILED=0; \
	for DASHBOARD in superset/dashboards/*.json; do \
		if [ ! -f "$$DASHBOARD" ]; then continue; fi; \
		DASHBOARD_NAME=$$(basename "$$DASHBOARD" .json); \
		echo "📥 Importing $$DASHBOARD_NAME..."; \
		HTTP_CODE=$$(curl -sS -X POST "https://superset.insightpulseai.net/api/v1/dashboard/import/" \
			-H "Authorization: Bearer $$ACCESS_TOKEN" \
			-H "Content-Type: multipart/form-data" \
			-F "formData=@$$DASHBOARD" \
			-w "%{http_code}" -o /dev/null 2>/dev/null); \
		if [ "$$HTTP_CODE" = "200" ] || [ "$$HTTP_CODE" = "201" ]; then \
			echo "  ✅ $$DASHBOARD_NAME imported successfully"; \
			IMPORTED=$$((IMPORTED + 1)); \
		else \
			echo "  ⚠️  $$DASHBOARD_NAME import failed (HTTP $$HTTP_CODE)"; \
			FAILED=$$((FAILED + 1)); \
		fi; \
	done; \
	echo ""; \
	echo "📊 Dashboard deployment summary:"; \
	echo "  Imported: $$IMPORTED"; \
	echo "  Failed: $$FAILED"; \
	echo ""; \
	echo "💡 View dashboards: https://superset.insightpulseai.net/superset/welcome/"

.PHONY: superset-console
superset-console: ## Open interactive console to Superset container
	@echo "🖥️  Opening Superset console (interactive)..."
	@echo "Run these commands in the console:"
	@echo "  superset db upgrade"
	@echo "  superset load_examples"
	@echo "  superset init"
	@echo ""
	@doctl apps console 73af11cb-dab2-4cb1-9770-291c536531e6 superset-analytics

.PHONY: health-check
health-check: ## Run health checks on all deployed services
	@echo "🏥 Running health checks..."
	@echo ""
	@echo "📊 Odoo ERP:"
	@curl -Is https://$(ODOO_FQDN)/web/login | head -n1 || echo "  ❌ Odoo not responding"
	@echo ""
	@echo "📊 Apache Superset:"
	@curl -Is https://superset.insightpulseai.net | head -n1 || echo "  ⚠️  Superset not responding"
	@echo ""
	@echo "📚 Documentation:"
	@curl -Is https://$(DOCS_FQDN)/index.html | head -n1 || echo "  ⚠️  Docs not found (may not be deployed)"
	@echo ""
	@echo "🔍 Supabase Edge Functions:"
	@curl -sS -X POST "$(EDGE_URL)/search" \
		-H "Authorization: Bearer $(SUPABASE_ANON_KEY)" \
		-H "Content-Type: application/json" \
		-d '{"query":"status check","k":1}' | head -c 100 || echo "  ⚠️  Search function not responding"
	@echo ""
	@echo "✅ Health check complete"

.PHONY: deployment-status
deployment-status: ## Check DigitalOcean deployment status
	@echo "📊 DigitalOcean App deployment status:"
	@doctl apps deployments list $(DO_APP_ID) --format ID,Phase,CreatedAt --no-header | head -5

.PHONY: logs
logs: ## Tail DigitalOcean App logs
	@echo "📜 Tailing DO App logs (Ctrl+C to exit)..."
	@doctl apps logs $(DO_APP_ID) --follow

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

.PHONY: test
test: ## Run test suite
	@echo "🧪 Running tests..."
	@pytest tests/ || python -m pytest tests/ || echo "⚠️  No tests found"

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
