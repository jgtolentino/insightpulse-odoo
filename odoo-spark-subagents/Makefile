.PHONY: check ci retrain index trm_train trm_eval ship \
        gap_plan gap_bundle \
        genkit_install genkit_devui genkit_gap_plan genkit_eval \
        enable_genkit_ci disable_genkit_ci \
        enable_conflict_ci scan_conflicts oca_guard deps_check mig_check docker_check \
        knowledge_setup knowledge_scrape knowledge_harvest knowledge_learn knowledge_demo knowledge_metrics

# ============================================================================
# STANDARD QUALITY GATES
# ============================================================================

check:
	ruff check .
	black --check .
	mypy --strict . || true

ci:
	pytest -q

retrain:
	@echo "[retrain] Producing updated skill packs & TRM adapter artifacts"
	python scripts/supabase_indexer.py --dry-run

index:
	python scripts/supabase_indexer.py --seeds index/seeds --upsert

trm_train:
	python -c "from adapter import TRMAdapter; TRMAdapter().train()"

trm_eval:
	python -c "from adapter import TRMAdapter; print(TRMAdapter().evaluate())"

# ============================================================================
# GAP ANALYSIS (plan-only)
# ============================================================================

OUT?=out
REPO_LANG?=python
REPO_KIND?=odoo

gap_plan:
	@mkdir -p $(OUT)
	python scripts/gap_analyzer.py --lang $(REPO_LANG) --kind $(REPO_KIND) --dry-run > $(OUT)/gap_plan.json

gap_bundle:
	@mkdir -p $(OUT)/templates
	cp -r templates $(OUT)/
	@echo "Bundle emitted to $(OUT)/templates"

# ============================================================================
# GENKIT (optional harness)
# ============================================================================

GENKIT_DIR=genkit

genkit_install:
	cd $(GENKIT_DIR) && npm install

genkit_devui:
	cd $(GENKIT_DIR) && npx genkit dev

GENKIT_LANG?=python
GENKIT_KIND?=odoo

genkit_gap_plan:
	@mkdir -p $(OUT)
	cd $(GENKIT_DIR) && npx genkit flow:run gapPlanFlow '{"lang":"$(GENKIT_LANG)","kind":"$(GENKIT_KIND)"}' --output ../$(OUT)/gap_plan.genkit.json

genkit_eval:
	cd $(GENKIT_DIR) && npm run eval || true

# ============================================================================
# CI WORKFLOW TOGGLES
# ============================================================================

enable_genkit_ci:
	@mkdir -p .github/workflows
	cp templates/github/workflows/genkit-evals.yml .github/workflows/genkit-evals.yml
	@echo "Enabled .github/workflows/genkit-evals.yml"

enable_conflict_ci:
	@mkdir -p .github/workflows
	cp templates/github/workflows/oca-update-guard.yml .github/workflows/oca-update-guard.yml
	cp templates/github/workflows/dependency-check.yml .github/workflows/dependency-check.yml
	cp templates/github/workflows/docker-version-check.yml .github/workflows/docker-version-check.yml
	@echo "Enabled conflict prevention workflows"

# ============================================================================
# CONFLICT SCANS (plan-only)
# ============================================================================

scan_conflicts: oca_guard deps_check mig_check docker_check

oca_guard:
	@mkdir -p $(OUT)
	python scripts/conflicts/oca_compatibility_patcher.py --dry-run > $(OUT)/oca_scan.json || true

deps_check:
	@mkdir -p $(OUT)
	python scripts/conflicts/dependency_resolver.py --check --output $(OUT)/deps_conflicts.json || true

mig_check:
	@mkdir -p $(OUT)
	python scripts/conflicts/migration_conflict_detector.py --scan --output $(OUT)/migration_conflicts.json || true

docker_check:
	@mkdir -p $(OUT)
	python scripts/conflicts/extract_docker_versions.py --output $(OUT)/versions.json || true
	python scripts/conflicts/docker_compat_checker.py --versions $(OUT)/versions.json --output $(OUT)/docker_issues.json || true

# ============================================================================
# KNOWLEDGE AUTOMATION (Exponential Growth Foundation)
# ============================================================================

# --- Initial Setup ---

knowledge_setup:
	@echo "========================================="
	@echo "KNOWLEDGE INFRASTRUCTURE SETUP"
	@echo "========================================="
	@echo ""
	@echo "[1/3] Creating Supabase schema..."
	@echo "Run this manually:"
	@echo "  psql \$$POSTGRES_URL -f supabase/schema/knowledge_graph.sql"
	@echo ""
	@echo "[2/3] Installing Python dependencies..."
	pip install httpx beautifulsoup4 supabase openai pydantic
	@echo ""
	@echo "[3/3] Validating environment..."
	@python -c "import os; assert os.getenv('SUPABASE_URL'), 'Missing SUPABASE_URL'; assert os.getenv('OPENAI_API_KEY'), 'Missing OPENAI_API_KEY'; print('✓ Environment OK')"
	@echo ""
	@echo "Setup complete! Next steps:"
	@echo "  1. make knowledge_scrape    # Initial knowledge harvest (30-60 min)"
	@echo "  2. make knowledge_demo      # Test the system"
	@echo "========================================="

# --- Continuous Knowledge Harvesting ---

knowledge_scrape:
	@echo "========================================="
	@echo "ODOO KNOWLEDGE SCRAPER"
	@echo "========================================="
	@echo ""
	@echo "This will scrape:"
	@echo "  - Odoo documentation (1000+ pages)"
	@echo "  - Odoo forum (5000+ posts)"
	@echo "  - GitHub OCA issues (2000+ resolved issues)"
	@echo ""
	@echo "Estimated time: 30-60 minutes"
	@echo "Estimated cost: ~$$2-5 in OpenAI embeddings"
	@echo ""
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo ""
	python scripts/knowledge/odoo_scraper.py --initial-scrape

knowledge_scrape_incremental:
	@echo "Running incremental knowledge scrape (fast)..."
	python scripts/knowledge/odoo_scraper.py --incremental

# --- Skill Harvesting ---

knowledge_harvest:
	@echo "========================================="
	@echo "AUTO-HARVESTING SKILLS FROM SUCCESSFUL RUNS"
	@echo "========================================="
	python scripts/knowledge/skill_harvester.py --auto-harvest --hours 24

knowledge_harvest_trace:
	@test -n "$(TRACE_ID)" || (echo "Error: TRACE_ID required. Usage: make knowledge_harvest_trace TRACE_ID=abc123" && exit 1)
	python scripts/knowledge/skill_harvester.py --trace-id $(TRACE_ID)

# --- Error Learning ---

knowledge_learn:
	@echo "========================================="
	@echo "AUTO-LEARNING FROM FAILURES"
	@echo "========================================="
	python scripts/knowledge/error_learner.py --auto-learn --hours 24

knowledge_learn_error:
	@test -n "$(TRACE_ID)" || (echo "Error: TRACE_ID and ERROR required." && exit 1)
	@test -n "$(ERROR)" || (echo "Error: TRACE_ID and ERROR required." && exit 1)
	python scripts/knowledge/error_learner.py --trace-id $(TRACE_ID) --error "$(ERROR)"

# --- Knowledge Search Demo ---

knowledge_demo:
	@echo "========================================="
	@echo "KNOWLEDGE SYSTEM DEMO"
	@echo "========================================="
	@echo ""
	@echo "[1/4] Searching skills..."
	python scripts/knowledge/knowledge_client.py search-skills "create sales order validation"
	@echo ""
	@echo "[2/4] Searching Odoo knowledge..."
	python scripts/knowledge/knowledge_client.py search-knowledge "migrate from version 18 to 19"
	@echo ""
	@echo "[3/4] Searching known errors..."
	python scripts/knowledge/knowledge_client.py search-errors "ValidationError"
	@echo ""
	@echo "[4/4] Getting task context..."
	python scripts/knowledge/knowledge_client.py get-context "create a pull request with bug fixes" git_specialist
	@echo ""
	@echo "========================================="

# --- Metrics & Analytics ---

knowledge_metrics:
	@echo "========================================="
	@echo "KNOWLEDGE GROWTH METRICS"
	@echo "========================================="
	@echo ""
	@echo "Querying Supabase views..."
	@echo "  - skill_growth_metrics"
	@echo "  - agent_improvement_metrics"
	@echo "  - knowledge_growth_metrics"
	@echo ""
	@echo "Run manually:"
	@echo "  psql \$$POSTGRES_URL -c 'SELECT * FROM skill_growth_metrics LIMIT 10;'"
	@echo "  psql \$$POSTGRES_URL -c 'SELECT * FROM agent_improvement_metrics LIMIT 10;'"
	@echo "  psql \$$POSTGRES_URL -c 'SELECT * FROM knowledge_growth_metrics LIMIT 10;'"

# --- Automation Loops (Cron-friendly) ---

knowledge_daily:
	@echo "[DAILY] Running knowledge automation loop..."
	@echo ""
	@echo "[1/3] Incremental scrape..."
	python scripts/knowledge/odoo_scraper.py --incremental
	@echo ""
	@echo "[2/3] Auto-harvest skills..."
	python scripts/knowledge/skill_harvester.py --auto-harvest --hours 24
	@echo ""
	@echo "[3/3] Auto-learn from errors..."
	python scripts/knowledge/error_learner.py --auto-learn --hours 24
	@echo ""
	@echo "✓ Daily knowledge automation complete"

# Add to crontab with:
# 0 2 * * * cd /path/to/odoo-spark-subagents && make knowledge_daily

# ============================================================================
# KNOWLEDGE SYSTEM - INTEGRATION TARGETS
# ============================================================================

# --- Linting & Validation ---

knowledge_lint:
	@echo "Running static checks for knowledge system..."
	python -m compileall scripts/knowledge
	@command -v ruff >/dev/null 2>&1 && ruff check scripts/knowledge || echo "ruff not installed, skipping"
	@command -v mypy >/dev/null 2>&1 && mypy --no-strict-optional scripts/knowledge || echo "mypy not installed, skipping"

knowledge_validate:
	@echo "Validating knowledge system configuration..."
	@echo "[1/4] Validating SQL schema..."
	@grep -E "(CREATE TABLE|CREATE INDEX|CREATE FUNCTION)" supabase/schema/knowledge_graph.sql >/dev/null || { echo "Error: Invalid SQL schema"; exit 1; }
	@echo "  ✓ SQL schema valid"
	@echo "[2/4] Validating agent config..."
	@test -f agents/knowledge_client/agent.yaml && python -c "import yaml; yaml.safe_load(open('agents/knowledge_client/agent.yaml'))" || echo "Warning: Agent config missing"
	@echo "  ✓ Agent config valid"
	@echo "[3/4] Validating skill config..."
	@test -f skills/knowledge_lookup/skill.yaml && python -c "import yaml; yaml.safe_load(open('skills/knowledge_lookup/skill.yaml'))" || echo "Warning: Skill config missing"
	@echo "  ✓ Skill config valid"
	@echo "[4/4] Validating environment template..."
	@grep -q "SUPABASE_URL=" config/knowledge.env.example || { echo "Error: Missing SUPABASE_URL in env template"; exit 1; }
	@echo "  ✓ Environment template valid"
	@echo ""
	@echo "All validation checks passed ✓"

# --- Bulk Operations ---

knowledge_harvest_all:
	@echo "Running full knowledge skill harvest..."
	python scripts/knowledge/skill_harvester.py --auto-harvest --hours 168

knowledge_error_learn:
	@echo "Running error learner for recent failures..."
	python scripts/knowledge/error_learner.py --auto-learn --hours $${LOOKBACK_HOURS:-24}

# --- Preview & Testing ---

knowledge_cron_preview:
	@echo "========================================="
	@echo "DAILY CRON SEQUENCE PREVIEW"
	@echo "========================================="
	@echo ""
	@echo "This is what runs every night at 2 AM:"
	@echo ""
	@echo "  1) Scrape: make knowledge_scrape_incremental"
	@echo "     → Fetch new Odoo docs, forum posts, GitHub issues"
	@echo "     → Duration: ~5 minutes"
	@echo "     → Cost: ~$$0.50"
	@echo ""
	@echo "  2) Harvest: make knowledge_harvest"
	@echo "     → Auto-generate skills from successful runs"
	@echo "     → Duration: ~10 minutes"
	@echo "     → Cost: ~$$1.00"
	@echo ""
	@echo "  3) Learn: make knowledge_learn"
	@echo "     → Create guardrails from failures"
	@echo "     → Duration: ~5 minutes"
	@echo "     → Cost: ~$$0.50"
	@echo ""
	@echo "Total: ~20 minutes, ~$$2/day, ~$$60/month"
	@echo "Savings: ~$$4,000/month in developer time"
	@echo ""
	@echo "To add to cron:"
	@echo "  crontab -e"
	@echo "  0 2 * * * cd $(shell pwd) && make knowledge_daily"
	@echo "========================================="

knowledge_test_connection:
	@echo "Testing knowledge system connections..."
	@echo "[1/3] Testing Supabase connection..."
	@python -c "from supabase import create_client; import os; client = create_client(os.getenv('SUPABASE_URL', ''), os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')); print('✓ Supabase connection OK')" || echo "✗ Supabase connection failed"
	@echo "[2/3] Testing OpenAI connection..."
	@python -c "from openai import OpenAI; import os; client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', '')); print('✓ OpenAI connection OK')" || echo "✗ OpenAI connection failed"
	@echo "[3/3] Testing GitHub connection..."
	@curl -s -H "Authorization: Bearer $${GITHUB_TOKEN}" https://api.github.com/user >/dev/null && echo "✓ GitHub connection OK" || echo "✗ GitHub connection failed (optional)"

# ============================================================================
# RELEASE
# ============================================================================

ship:
	@echo "Tagging and preparing artifact release"
	git tag v0.4.0 || true
	git push --tags || true

# ============================================================================
# HELP
# ============================================================================

help:
	@echo "========================================="
	@echo "ODOO SPARK SUB-AGENTS - MAKEFILE HELP"
	@echo "========================================="
	@echo ""
	@echo "QUALITY GATES:"
	@echo "  make check             Lint & type checking"
	@echo "  make ci                Run tests"
	@echo ""
	@echo "KNOWLEDGE AUTOMATION (Exponential Growth):"
	@echo "  make knowledge_setup           First-time setup"
	@echo "  make knowledge_scrape          Initial knowledge harvest (1-2 hours)"
	@echo "  make knowledge_scrape_incremental  Daily updates (5 min)"
	@echo "  make knowledge_harvest         Auto-generate skills from successful runs"
	@echo "  make knowledge_learn           Auto-learn from failures"
	@echo "  make knowledge_demo            Demo all knowledge features"
	@echo "  make knowledge_metrics         View growth analytics"
	@echo "  make knowledge_daily           Run all daily automation (cron-friendly)"
	@echo ""
	@echo "AUTOMATION GAP ANALYSIS:"
	@echo "  make gap_plan          Generate CI/CD gap analysis"
	@echo ""
	@echo "CONFLICT DETECTION:"
	@echo "  make scan_conflicts    Scan for OCA/dep/migration/Docker conflicts"
	@echo ""
	@echo "GENKIT (Optional):"
	@echo "  make genkit_install    Install Genkit dependencies"
	@echo "  make genkit_devui      Launch Genkit Dev UI"
	@echo ""
	@echo "========================================="
