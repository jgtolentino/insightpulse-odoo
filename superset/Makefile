# Superset Dashboard Management Makefile
# For Travel & Expense (T&E) and other dashboard operations

.PHONY: help te-import te-reload te-clean te-views te-status

help:
	@echo "Superset Dashboard Management"
	@echo "=============================="
	@echo ""
	@echo "T&E Dashboard Commands:"
	@echo "  make te-views        Create database views for T&E analytics"
	@echo "  make te-import       Import T&E datasets, charts, and dashboards"
	@echo "  make te-reload       Clean and re-import T&E dashboards"
	@echo "  make te-clean        Remove T&E assets (manual via UI)"
	@echo "  make te-status       Check T&E dashboard status"
	@echo ""
	@echo "Environment Variables:"
	@echo "  POSTGRES_URL         PostgreSQL connection string"
	@echo "  SUPERSET_BASE_URL    Superset instance URL (default: http://localhost:8088)"
	@echo ""

te-views:
	@echo "Creating T&E analytics views in database..."
	@if [ -z "$$POSTGRES_URL" ]; then \
		echo "ERROR: POSTGRES_URL not set. Example:"; \
		echo "  export POSTGRES_URL='postgresql://user:pass@host:5432/dbname'"; \
		exit 1; \
	fi
	@psql "$$POSTGRES_URL" -f superset/te/sql/00_views.sql
	@echo "✓ Views created successfully"

te-import:
	@echo "Importing T&E dashboards..."
	@bash superset/te/import.sh

te-reload:
	@echo "WARNING: This will require manual cleanup of existing T&E dashboards."
	@echo "Please delete existing dashboards via Superset UI (filter by 'T&E')."
	@echo "Then run: make te-import"

te-clean:
	@echo "To clean T&E assets:"
	@echo "1. Open Superset UI"
	@echo "2. Go to Dashboards"
	@echo "3. Filter by title containing 'T&E'"
	@echo "4. Delete: T&E Overview, T&E Manager, T&E Audit"
	@echo "5. Go to Charts and delete charts starting with 'te_'"
	@echo "6. Go to Data → Datasets and delete: te_expenses_v, te_cash_advances_v, te_approvals_v, te_receipts_ocr_v"

te-status:
	@echo "Checking T&E dashboard status..."
	@echo ""
	@echo "Views (check in database):"
	@if [ -z "$$POSTGRES_URL" ]; then \
		echo "  Set POSTGRES_URL to check view status"; \
	else \
		psql "$$POSTGRES_URL" -c "SELECT viewname FROM pg_views WHERE viewname LIKE 'te_%_v';" || true; \
	fi
	@echo ""
	@echo "Check Superset UI for:"
	@echo "  - Datasets: te_expenses_v, te_cash_advances_v, te_approvals_v, te_receipts_ocr_v"
	@echo "  - Charts: 12 charts starting with 'te_'"
	@echo "  - Dashboards: T&E Overview, T&E Manager, T&E Audit"
	@echo ""
	@echo "Access dashboards at: $${SUPERSET_BASE_URL:-http://localhost:8088}"
