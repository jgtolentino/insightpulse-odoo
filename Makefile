# Odoo Development Makefile
# Provides convenient shortcuts for common development tasks

.PHONY: help init lint test run shell build clean coverage scaffold search

help:
	@echo "Odoo Development Commands"
	@echo "========================="
	@echo ""
	@echo "Setup:"
	@echo "  make init         - Initialize pre-commit hooks and dev environment"
	@echo ""
	@echo "Development:"
	@echo "  make lint         - Run linting (pre-commit, pylint-odoo, ruff)"
	@echo "  make test         - Run tests with coverage"
	@echo "  make coverage     - Generate coverage report (must run after test)"
	@echo "  make run          - Start Docker Compose development environment"
	@echo "  make shell        - Open shell in Odoo container"
	@echo "  make build        - Build Docker images"
	@echo ""
	@echo "Module Management:"
	@echo "  make scaffold     - Generate new module (requires: NAME, MODELS, etc.)"
	@echo "  make search       - Search OCA modules (requires: KEYWORDS)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Clean temporary files and caches"
	@echo ""
	@echo "Examples:"
	@echo "  make scaffold NAME=hr_training CATEGORY=\"Human Resources\" MODELS=training,session"
	@echo "  make search KEYWORDS=expense,approval"

init:
	@echo "🔧 Installing pre-commit hooks..."
	pre-commit install || { echo "Installing pre-commit..."; pip install pre-commit && pre-commit install; }
	@echo "📦 Installing development dependencies..."
	pip install -r requirements-dev.txt 2>/dev/null || echo "⚠️  requirements-dev.txt not found"
	@echo "✅ Development environment initialized"

lint:
	@echo "🔍 Running linting checks..."
	pre-commit run -a

test:
	@echo "🧪 Running tests with coverage..."
	coverage run -m pytest -q
	@echo ""
	@echo "📊 Generating coverage report..."
	coverage report --fail-under=75

coverage:
	@echo "📊 Generating detailed coverage report..."
	coverage report --show-missing
	@echo ""
	@echo "📈 Generating HTML coverage report..."
	coverage html
	@echo "✅ Coverage report generated in htmlcov/index.html"

run:
	@echo "🚀 Starting Docker Compose environment..."
	docker compose up --build

shell:
	@echo "🐚 Opening shell in Odoo container..."
	docker compose exec odoo bash

build:
	@echo "🏗️  Building Docker images..."
	docker compose build

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov/ .ruff_cache/
	@echo "✅ Cleanup complete"

scaffold:
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Error: NAME is required"; \
		echo "Usage: make scaffold NAME=module_name [CATEGORY=\"Category\"] [MODELS=model1,model2]"; \
		exit 1; \
	fi
	@echo "🏗️  Scaffolding module: $(NAME)"
	@ARGS="--name $(NAME)"; \
	[ -n "$(SUMMARY)" ] && ARGS="$$ARGS --summary \"$(SUMMARY)\""; \
	[ -n "$(CATEGORY)" ] && ARGS="$$ARGS --category \"$(CATEGORY)\""; \
	[ -n "$(DEPENDS)" ] && ARGS="$$ARGS --depends $(DEPENDS)"; \
	[ -n "$(MODELS)" ] && ARGS="$$ARGS --models $(MODELS)"; \
	[ -n "$(LICENSE)" ] && ARGS="$$ARGS --license $(LICENSE)"; \
	[ -n "$(AUTHOR)" ] && ARGS="$$ARGS --author \"$(AUTHOR)\""; \
	./scripts/scaffold-odoo-module.sh $$ARGS

search:
	@if [ -z "$(KEYWORDS)" ]; then \
		echo "❌ Error: KEYWORDS is required"; \
		echo "Usage: make search KEYWORDS=expense,approval [VERSION=19.0] [FORMAT=table]"; \
		exit 1; \
	fi
	@echo "🔍 Searching OCA modules..."
	@ARGS="--keywords $(KEYWORDS)"; \
	[ -n "$(VERSION)" ] && ARGS="$$ARGS --version $(VERSION)"; \
	[ -n "$(FORMAT)" ] && ARGS="$$ARGS --format $(FORMAT)"; \
	./scripts/search-oca-modules.sh $$ARGS
