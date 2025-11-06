# Spec-Driven CI/CD Integration Guide

**Contract-First Development** with automated spec validation, drift detection, and version management.

## Quick Start

```bash
# 1. Install dependencies
pip install pydantic pyyaml click pytest opentelemetry-api black flake8

# 2. Generate initial spec
make spec

# 3. Run local CI pipeline
make spec-ci
```

## What's Included

### 1. Pydantic → OpenAPI Generation
**Tool**: `ci/speckit/generate_openapi.py`

Scans `addons/*/models/spec_registry.py` for Pydantic models and generates OpenAPI 3.1 spec.

```python
# Example spec_registry.py
from pydantic import BaseModel

class MyRequest(BaseModel):
    field1: str
    field2: int

SPEC_REGISTRY = {
    "my_endpoint": {
        "path": "/api/v1/endpoint",
        "method": "post",
        "request_schema": MyRequest.model_json_schema(),
        "x-atomic": True,
        "x-idempotency": "key-based",
        "x-role-scopes": ["user:create"]
    }
}
```

### 2. Spec Drift Detection
**Tool**: `ci/speckit/spec_drift_gate.py`

Compares tracked spec (`spec/openapi.json`) with generated spec to detect breaking changes.

**Fails CI if**:
- Endpoints removed
- HTTP methods changed
- Request/response schemas modified
- Role scopes changed

### 3. Contract Validation
**Tool**: `ci/speckit/validate_spec_contract.py`

Ensures all endpoints have required metadata:
- `x-atomic` (boolean)
- `x-idempotency` (none|key-based|natural)
- `x-role-scopes` (list of "role:permission")

### 4. Auto-Version Bumping
**Tool**: `ci/speckit/bump_manifest_version.py`

Automatically bumps patch versions in `__manifest__.py` when spec changes detected.

**Version Scheme**: `MAJOR.MINOR.PATCH`
- **MAJOR**: Breaking changes (manual bump)
- **MINOR**: New features (manual bump)
- **PATCH**: Bug fixes, spec updates (auto-bump)

### 5. OCA Maintainer Quality Tools
**Tool**: `ci/qa/run_mqt.sh`

Validates Odoo module structure:
- `__manifest__.py` exists and valid
- `__init__.py` present
- OCA compliance checks (if `odoo-analyse-module` installed)

### 6. OpenTelemetry Propagation Tests
**Tool**: `ci/otel/trace_probe_test.py`

Validates W3C Trace Context propagation:
- `traceparent` header format
- `tracestate` preservation
- Trace ID consistency across service boundaries

## CI/CD Workflow

### GitHub Actions (`.github/workflows/ci-spec.yml`)

**Triggers**:
- Push to `main`/`develop`
- Pull requests to `main`/`develop`
- Changes to `addons/**/*.py`, `spec/**/*.json`, CI files

**Jobs**:
1. **spec-regen**: Generate spec, detect drift, validate contracts, auto-bump versions
2. **otel-probe**: Run OTel header propagation tests
3. **oca-mqt**: Run OCA quality checks on all modules
4. **quality-gates**: Lint, test, coverage, final validation

**Quality Gates**:
- ❌ Spec drift detected → FAIL (breaking changes require version bump)
- ❌ Missing contract metadata → FAIL
- ❌ Invalid role scopes → FAIL
- ❌ Linting errors → FAIL
- ❌ Test coverage <80% → FAIL

## Local Development Workflow

### 1. Define API Contract
```python
# addons/my_module/models/spec_registry.py
SPEC_REGISTRY = {
    "my_endpoint": {
        "path": "/api/v1/my-endpoint",
        "method": "post",
        "summary": "My endpoint description",
        "request_schema": {...},
        "response_schema": {...},
        "x-atomic": True,
        "x-idempotency": "key-based",
        "x-role-scopes": ["user:create", "admin:all"]
    }
}
```

### 2. Generate & Validate
```bash
# Generate OpenAPI spec
make spec

# Validate contract metadata
make spec-validate

# Check for drift
make spec-drift
```

### 3. Implement Endpoint
```python
# addons/my_module/controllers/main.py
from odoo import http
from odoo.http import request

class MyController(http.Controller):
    @http.route('/api/v1/my-endpoint', type='json', auth='user', methods=['POST'])
    def my_endpoint(self, **kw):
        # Implementation matching SPEC_REGISTRY
        pass
```

### 4. Run Full CI Pipeline
```bash
# Run all checks locally before pushing
make spec-ci
```

### 5. Commit & Push
```bash
git add addons/my_module spec/openapi.json
git commit -m "feat: add my_endpoint API"
git push origin feature/my-endpoint
```

## Makefile Targets

```bash
make spec              # Generate OpenAPI spec from Pydantic
make spec-validate     # Validate contract metadata
make spec-drift        # Check for spec drift
make spec-bump         # Auto-bump __manifest__.py versions
make mqt-odoo          # Run OCA quality checks
make spec-format       # Format code with black
make spec-clean        # Clean generated artifacts
make spec-ci           # Run full CI pipeline locally
```

## Contract Metadata Reference

### `x-atomic` (boolean)
Indicates if operation is atomic (all-or-nothing transaction).

**Example**:
```python
"x-atomic": True  # Database transaction, rollback on failure
"x-atomic": False # Partial success possible
```

### `x-idempotency` (enum)
Indicates idempotency guarantee for safe retries.

**Values**:
- `none`: Not idempotent (e.g., POST create)
- `key-based`: Requires `Idempotency-Key` header
- `natural`: Naturally idempotent (GET, PUT, DELETE)

**Example**:
```python
"x-idempotency": "key-based"  # Requires Idempotency-Key header
"x-idempotency": "natural"    # GET endpoint
```

### `x-role-scopes` (list[str])
Required role:permission combinations for authorization.

**Format**: `"{role}:{permission}"`

**Example**:
```python
"x-role-scopes": [
    "expense_user:create",  # Expense users can create
    "admin:all"             # Admins have full access
]
```

## Troubleshooting

### Spec Drift Detected

**Problem**: CI fails with "Spec drift detected"

**Solution**:
```bash
# 1. Review changes
git diff spec/openapi.json

# 2. If intentional breaking change:
#    a. Bump major/minor version in __manifest__.py
#    b. Regenerate spec
make spec

# 3. Commit both changes
git add addons/*/\__manifest__.py spec/openapi.json
git commit -m "feat!: breaking API change (bump major version)"
```

### Missing Contract Metadata

**Problem**: CI fails with "missing x-atomic metadata"

**Solution**:
```python
# Add required metadata to SPEC_REGISTRY
SPEC_REGISTRY = {
    "my_endpoint": {
        # ... existing fields ...
        "x-atomic": True,
        "x-idempotency": "key-based",
        "x-role-scopes": ["user:create"]
    }
}
```

### Invalid Role Scopes

**Problem**: CI fails with "invalid role scope format"

**Solution**:
```python
# Wrong format
"x-role-scopes": ["admin"]  # Missing permission

# Correct format
"x-role-scopes": ["admin:all"]  # role:permission
```

### OCA MQT Failures

**Problem**: CI fails OCA quality checks

**Solution**:
```bash
# Run locally to see detailed errors
make mqt-odoo

# Common fixes:
# 1. Add __manifest__.py if missing
# 2. Add __init__.py if missing
# 3. Fix module structure to OCA standards
```

## Integration with Existing Workflows

### Adding Spec-Driven CI to Existing Modules

1. **Create `spec_registry.py`**:
   ```bash
   mkdir -p addons/my_existing_module/models
   touch addons/my_existing_module/models/spec_registry.py
   ```

2. **Define existing endpoints**:
   ```python
   # Document existing API contracts
   SPEC_REGISTRY = {
       "existing_endpoint_1": {...},
       "existing_endpoint_2": {...},
   }
   ```

3. **Generate initial spec**:
   ```bash
   make spec
   git add spec/openapi.json
   git commit -m "docs: add initial API spec"
   ```

4. **Enable drift detection**: Future changes will trigger drift checks

### Gradual Adoption Strategy

**Phase 1**: Document existing APIs
- Create `spec_registry.py` for each module
- Generate baseline spec
- No breaking change enforcement yet

**Phase 2**: Enable validation
- Add contract metadata (`x-atomic`, etc.)
- Enable `spec-validate` in CI

**Phase 3**: Enforce drift detection
- Enable `spec-drift` gate in CI
- Require version bumps for breaking changes

**Phase 4**: Full automation
- Auto-bump patch versions
- Require spec updates in PRs
- Enforce test coverage for spec changes

## Best Practices

1. **Contract-First**: Define `SPEC_REGISTRY` before implementing endpoints
2. **Atomic + Idempotent**: Use `x-atomic: true` with `x-idempotency: key-based`
3. **Granular Scopes**: Define specific `role:permission` combinations
4. **Version Discipline**: Major for breaking, minor for features, patch for fixes
5. **Test Contracts**: Validate Pydantic schemas in unit tests
6. **Local CI**: Run `make spec-ci` before pushing
7. **Document Changes**: Update `spec/README.md` when adding new patterns

## References

- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OCA Maintainer Tools](https://github.com/OCA/maintainer-tools)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [Semantic Versioning](https://semver.org/)
