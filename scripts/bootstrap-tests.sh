#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Bootstrapping InsightPulse test plan..."

# 1) Core test directories
mkdir -p \
  addons/custom/finance_ssc_closing/tests \
  addons/custom/ipai_expense/tests \
  addons/custom/ipai_approvals/tests \
  services/ai-training-hub/tests \
  services/ipai-agent/tests \
  services/mcp-hub/tests \
  tests/fixtures \
  tests/unit \
  tests/integration \
  ci/qa

# 2) Finance SSC Closing tests
cat > addons/custom/finance_ssc_closing/tests/test_closing.py << 'EOF'
import pytest

pytestmark = pytest.mark.financial

def test_month_end_closing_process():
    """End-to-end month-end closing for one agency."""
    # TODO: implement
    pass

def test_journal_entry_validation():
    """Journal entries must balance and respect chart of accounts."""
    pass

def test_account_reconciliation():
    """Bank and ledger reconciliation rules."""
    pass

def test_trial_balance_generation():
    """Trial balance output is consistent with posted entries."""
    pass

def test_multi_agency_consolidation():
    """Consolidated reporting across 8 agencies with isolation."""
    pass

def test_immutable_posted_entries():
    """Posted entries cannot be edited, only reversed."""
    pass
EOF

# 3) Expense Management tests
cat > addons/custom/ipai_expense/tests/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
EOF

cat > addons/custom/ipai_expense/tests/test_expense_policy.py << 'EOF'
import pytest

pytestmark = pytest.mark.expense

def test_policy_rule_evaluation():
    """Policies are evaluated correctly per employee/agency."""
    pass

def test_expense_amount_limits():
    """Hard and soft limits enforced on expense amounts."""
    pass

def test_category_restrictions():
    """Disallowed categories are rejected."""
    pass

def test_approval_thresholds():
    """Escalation thresholds behave as configured."""
    pass
EOF

cat > addons/custom/ipai_expense/tests/test_expense_advance.py << 'EOF'
import pytest

pytestmark = pytest.mark.expense_advance

def test_advance_request_creation():
    """Advance requests create correct accounting stub."""
    pass

def test_advance_liquidation():
    """Liquidation reconciles advance vs actual spend."""
    pass

def test_advance_balance_tracking():
    """Remaining advance balance tracked per employee."""
    pass
EOF

cat > addons/custom/ipai_expense/tests/test_expense_ocr_audit.py << 'EOF'
import pytest

pytestmark = pytest.mark.ocr_audit

def test_ocr_data_extraction():
    """OCR payload mapped correctly into expense fields."""
    pass

def test_receipt_validation():
    """Receipt date/amount/vendor validated against policy."""
    pass

def test_duplicate_detection():
    """Duplicate receipts detected using hash/fingerprint."""
    pass

def test_audit_trail_creation():
    """Audit trail entries created for OCR-assisted expenses."""
    pass
EOF

# 4) Approval Routing tests
cat > addons/custom/ipai_approvals/tests/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
EOF

cat > addons/custom/ipai_approvals/tests/test_approval_routing.py << 'EOF'
import pytest

pytestmark = pytest.mark.approvals

def test_approval_chain_construction():
    """Approval chain built from configuration (roles, levels)."""
    pass

def test_escalation_logic():
    """Overdue items escalate to next approver."""
    pass

def test_delegation_handling():
    """Delegated approvers can act within delegated scope."""
    pass

def test_approval_timeout_handling():
    """Timeout rules applied and logged."""
    pass

def test_parallel_approval_paths():
    """Parallel approvals (e.g. Finance + HR) supported."""
    pass

def test_approval_cancellation():
    """Cancelled requests leave consistent state."""
    pass
EOF

# 5) AI Training Hub tests (skeletons)
cat > services/ai-training-hub/tests/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
EOF

cat > services/ai-training-hub/tests/test_semantic_layer.py << 'EOF'
import pytest

pytestmark = pytest.mark.ai_semantic

def test_metric_definition_parsing():
    """Metric definitions loaded and validated from config."""
    pass

def test_dimension_resolution():
    """Dimension references resolve against warehouse schema."""
    pass

def test_semantic_query_generation():
    """Natural language to semantic query mapping."""
    pass
EOF

cat > services/ai-training-hub/tests/test_text_to_sql_agent.py << 'EOF'
import pytest

pytestmark = pytest.mark.text_to_sql

def test_natural_language_parsing():
    """Free text query parsed into intent + constraints."""
    pass

def test_sql_generation():
    """Generated SQL matches expected pattern and tables."""
    pass

def test_query_safety_validation():
    """Dangerous queries (DROP/TRUNCATE/etc.) rejected."""
    pass

def test_parameter_injection_prevention():
    """User params are always bound, never interpolated."""
    pass
EOF

cat > services/ai-training-hub/tests/test_vision_agent.py << 'EOF'
import pytest

pytestmark = pytest.mark.vision_agent

def test_document_classification():
    """Documents classified into correct types (invoice, receipt, etc.)."""
    pass

def test_layout_detection():
    """Layout engine finds lines/boxes/regions correctly."""
    pass

def test_field_extraction():
    """Key fields (amount, date, vendor) extracted reliably."""
    pass
EOF

cat > services/ai-training-hub/tests/test_paddleocr_finetune.py << 'EOF'
import pytest

pytestmark = pytest.mark.ocr_training

def test_training_data_preparation():
    """Training dataset assembled with correct labels/paths."""
    pass

def test_model_fine_tuning():
    """Fine-tune job runs end-to-end with no errors."""
    pass

def test_accuracy_metrics():
    """Reported accuracy metrics computed correctly."""
    pass
EOF

# 6) IPAI Agent Services tests
cat > services/ipai-agent/tests/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
EOF

cat > services/ipai-agent/tests/test_bir_batch_generator_agent.py << 'EOF'
import pytest

pytestmark = pytest.mark.bir_agent

def test_batch_generation_logic():
    """BIR batch split by form, period, and agency correctly."""
    pass

def test_form_population_accuracy():
    """Numeric fields match source ledger values."""
    pass

def test_validation_rule_compliance():
    """Run BIR validation rules and capture all failures."""
    pass
EOF

cat > services/ipai-agent/tests/test_tools_odoo_client.py << 'EOF'
import pytest

pytestmark = pytest.mark.tools_odoo

def test_record_creation(mocker):
    """Client creates records with correct payloads."""
    pass

def test_record_search(mocker):
    """Search filters and domains built correctly."""
    pass

def test_error_handling(mocker):
    """Odoo errors converted into safe, typed exceptions."""
    pass
EOF

cat > services/ipai-agent/tests/test_tools_supabase_client.py << 'EOF'
import pytest

pytestmark = pytest.mark.tools_supabase

def test_query_execution(mocker):
    """Supabase queries executed with expected SQL/RPC names."""
    pass

def test_connection_pooling(mocker):
    """Client reuses connections/pools appropriately."""
    pass

def test_retry_logic(mocker):
    """Transient errors trigger backoff + retry."""
    pass
EOF

cat > services/ipai-agent/tests/test_memory_kv_store.py << 'EOF'
import pytest

pytestmark = pytest.mark.memory

def test_key_value_storage():
    """Values are persisted and retrieved by key."""
    pass

def test_cache_eviction():
    """Eviction policy respected when capacity exceeded."""
    pass

def test_concurrent_access():
    """Concurrent reads/writes behave predictably."""
    pass
EOF

# 7) MCP Coordinator tests
cat > services/mcp-hub/tests/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
EOF

cat > services/mcp-hub/tests/test_mcp_coordinator.py << 'EOF'
import pytest

pytestmark = pytest.mark.mcp

def test_service_registration():
    """Services can register and are discoverable."""
    pass

def test_health_check_aggregation():
    """Health endpoints aggregated into a single status view."""
    pass

def test_request_routing():
    """Requests routed to the correct backend service."""
    pass

def test_failover_handling():
    """Failed services trigger failover to backups."""
    pass

def test_circuit_breaker_logic():
    """Unhealthy services are tripped and not called repeatedly."""
    pass

def test_multi_service_coordination():
    """Coordinator can orchestrate 8+ services in a flow."""
    pass
EOF

# 8) Fixtures
cat > tests/fixtures/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
EOF

cat > tests/fixtures/odoo_records.py << 'EOF'
import pytest

@pytest.fixture
def sample_expense():
    return {
        "name": "Test Expense",
        "total_amount": 1000.00,
        "employee_id": 1,
        "product_id": 1,
        "company_id": 1,
    }

@pytest.fixture
def sample_warehouse_data():
    return {
        "agency": "RIM",
        "period": "2025-10",
        "total_expense": 123456.78,
    }
EOF

cat > tests/PATTERNS.md << 'EOF'
# Test Patterns for InsightPulse Odoo + Services

## Odoo Addons (addons/custom/*)

- Use pytest functions, no unittest classes.
- Tag tests with `pytestmark` (e.g. `pytest.mark.financial`).
- Prefer model-level tests over UI tests.
- Use fixtures from `tests/fixtures` instead of hitting real DB where possible.

## Services (services/*)

- Always mock external calls (Odoo XML-RPC, Supabase, HTTP APIs).
- Test:
  - happy path
  - validation errors
  - transient failure with retry
  - permanent failure with clear error

## Agents

- Test decision logic with small, deterministic inputs.
- Do not call real models; mock tool clients.
EOF

# 9) Update pytest.ini with new markers
cat > ci/qa/pytest.ini << 'EOF'
[pytest]
testpaths = tests ci/qa ci/otel addons services agents
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=addons
    --cov=services
    --cov=agents
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
    --cov-fail-under=20
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    otel: OpenTelemetry tests
    spec: Spec validation tests
    financial: Finance SSC and accounting logic
    expense: Expense policy and workflow
    expense_advance: Cash advances and liquidation
    ocr_audit: OCR and audit trail
    approvals: Approval routing and escalation
    ai_semantic: Semantic layer tests
    text_to_sql: Text-to-SQL agent tests
    vision_agent: Vision/Doc AI tests
    ocr_training: OCR fine-tuning tests
    bir_agent: BIR batch generator agent
    tools_odoo: Odoo client tools
    tools_supabase: Supabase client tools
    memory: Agent memory KV store
    mcp: MCP coordinator tests
EOF

# 10) Pre-commit hook (append if file exists)
if [ -f .pre-commit-config.yaml ]; then
  if ! grep -q "pytest-check" .pre-commit-config.yaml; then
    cat >> .pre-commit-config.yaml << 'EOF'

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit -q --maxfail=1
        language: system
        pass_filenames: false
        always_run: true
EOF
  fi
else
  cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit -q --maxfail=1
        language: system
        pass_filenames: false
        always_run: true
EOF
fi

echo "✅ Test bootstrap complete."
echo "Next: run 'pytest -c ci/qa/pytest.ini' and then 'pre-commit install'."
