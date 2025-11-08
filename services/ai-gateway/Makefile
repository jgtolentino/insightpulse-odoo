.PHONY: help dev build up down logs test clean deploy

help: ## Show this help
\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.env: ## Create .env from template
\t@if [ ! -f .env ]; then \
\t\tcp .env.example .env; \
\t\techo "✅ Created .env from template. Please edit with your credentials."; \
\telse \
\t\techo "⚠️  .env already exists"; \
\tfi

dev: .env ## Run in development mode (with reload)
\t@echo "🚀 Starting AI Gateway in dev mode..."
\tuvicorn main:app --reload --host 0.0.0.0 --port 8080

build: ## Build Docker image
\t@echo "🔨 Building Docker image..."
\tdocker build -t ai-gateway:latest .

up: .env ## Start with Docker Compose
\t@echo "🚀 Starting AI Gateway..."
\tdocker compose up -d
\t@sleep 3
\t@make health

down: ## Stop Docker Compose
\t@echo "🛑 Stopping AI Gateway..."
\tdocker compose down

logs: ## View logs
\tdocker compose logs -f ai-gateway

restart: down up ## Restart service

health: ## Check health
\t@echo "🏥 Checking health..."
\t@curl -s http://localhost:8080/health | jq || echo "❌ Health check failed"

test: ## Run tests
\t@echo "🧪 Testing MCP endpoints..."
\t@echo "\n=== Testing /mcp/odoo ==="
\t@curl -s -X POST http://localhost:8080/mcp/odoo \
\t\t-H "Content-Type: application/json" \
\t\t-d '{"method": "tools/list", "params": {}}' | jq -r '.tools[] | "✓ " + .name'
\t@echo "\n=== Testing /mcp/close ==="
\t@curl -s -X POST http://localhost:8080/mcp/close \
\t\t-H "Content-Type: application/json" \
\t\t-d '{"method": "tools/list", "params": {}}' | jq -r '.tools[] | "✓ " + .name'
\t@echo "\n=== Testing /mcp/policy ==="
\t@curl -s -X POST http://localhost:8080/mcp/policy \
\t\t-H "Content-Type: application/json" \
\t\t-d '{"method": "tools/list", "params": {}}' | jq -r '.tools[] | "✓ " + .name'

test-rest: ## Test REST API endpoints
\t@echo "🧪 Testing REST API..."
\t@echo "\n=== Testing with API key ==="
\t@curl -s -H "X-API-Key: $${API_KEY_INTERNAL}" \
\t\thttp://localhost:8080/api/close/status | jq

test-openapi: ## Validate OpenAPI spec
\t@echo "🧪 Validating OpenAPI spec..."
\t@curl -s http://localhost:8080/.well-known/openapi.yaml | yq eval '.' - > /dev/null && echo "✅ OpenAPI spec valid" || echo "❌ OpenAPI spec invalid"

clean: down ## Clean up containers and volumes
\t@echo "🧹 Cleaning up..."
\tdocker compose down -v
\tdocker rmi ai-gateway:latest 2>/dev/null || true

install-claude: ## Install MCP config for Claude Desktop (macOS)
\t@echo "📦 Installing Claude Desktop MCP config..."
\t@mkdir -p ~/Library/Application\ Support/Claude
\t@if [ -f ~/Library/Application\ Support/Claude/claude_desktop_config.json ]; then \
\t\techo "⚠️  Backing up existing config..."; \
\t\tcp ~/Library/Application\ Support/Claude/claude_desktop_config.json \
\t\t   ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup; \
\tfi
\t@cp claude-desktop-config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
\t@echo "✅ Config installed. Restart Claude Desktop to apply."

deploy-do: ## Deploy to DigitalOcean App Platform
\t@echo "🚀 Deploying to DigitalOcean..."
\t@echo "⚠️  Make sure you've set secrets in DO dashboard:"
\t@echo "   - API_KEY_CHATGPT"
\t@echo "   - API_KEY_CLAUDE"
\t@echo "   - API_KEY_INTERNAL"
\t@echo "   - ODOO_API_KEY"
\t@echo "   - SUPABASE_SERVICE_KEY"
\t@read -p "Press Enter to continue..."
\tdoctl apps create --spec app.yaml

info: ## Show service info
\t@echo "=== AI Gateway Info ==="
\t@echo "Service: AI Gateway"
\t@echo "Version: 1.0.0"
\t@echo "Endpoints:"
\t@echo "  - Health: http://localhost:8080/health"
\t@echo "  - Docs: http://localhost:8080/docs"
\t@echo "  - OpenAPI: http://localhost:8080/.well-known/openapi.yaml"
\t@echo "\nMCP Endpoints (Claude Desktop):"
\t@echo "  - /mcp/odoo"
\t@echo "  - /mcp/close"
\t@echo "  - /mcp/policy"
\t@echo "\nREST API (ChatGPT/Claude Web):"
\t@echo "  - /api/close/*"
\t@echo "  - /api/policy/*"
\t@echo "  - /api/expenses/*"
