# Spec Governance

**Contract-First API Development** for InsightPulse Odoo

## Overview

This directory contains OpenAPI 3.1 specifications generated from Pydantic models in `addons/*/models/spec_registry.py`.

## Workflow

1. **Define API Contract** - Create Pydantic models in `spec_registry.py`:
   ```python
   # addons/expense_automation/models/spec_registry.py
   from pydantic import BaseModel

   class ExpenseCreateRequest(BaseModel):
       receipt_id: str
       amount: float
       currency: str = "PHP"

   class ExpenseCreateResponse(BaseModel):
       expense_id: int
       status: str

   SPEC_REGISTRY = {
       "expense_create": {
           "path": "/api/v1/expenses",
           "method": "post",
           "summary": "Create expense from receipt",
           "request_schema": ExpenseCreateRequest.model_json_schema(),
           "response_schema": ExpenseCreateResponse.model_json_schema(),
           "x-atomic": True,
           "x-idempotency": "key-based",
           "x-role-scopes": ["expense_user:create", "admin:all"]
       }
   }
   ```

2. **Generate OpenAPI Spec**:
   ```bash
   make spec
   # or
   python ci/speckit/generate_openapi.py
   ```

3. **Validate Contract Metadata**:
   ```bash
   make spec-validate
   # Checks: x-atomic, x-idempotency, x-role-scopes
   ```

4. **Detect Breaking Changes**:
   ```bash
   make spec-drift
   # Fails if tracked spec differs from generated
   ```

5. **Auto-Bump Versions**:
   ```bash
   make spec-bump
   # Updates __manifest__.py patch versions
   ```

## Contract Metadata

### `x-atomic`
**Boolean** - Indicates if operation is atomic (all-or-nothing)
- `true`: Database transaction required, failures rollback completely
- `false`: Partial success possible

### `x-idempotency`
**Enum** - Indicates idempotency guarantee:
- `none`: Multiple calls have different effects (e.g., create resources)
- `key-based`: Requires `Idempotency-Key` header for safe retries
- `natural`: Naturally idempotent (GET, PUT, DELETE)

### `x-role-scopes`
**List[str]** - Required role:permission combinations:
- Format: `"{role}:{permission}"`
- Examples: `["expense_user:create", "admin:all"]`
- Validated via RLS policies in Supabase

## CI/CD Integration

### GitHub Actions
`.github/workflows/ci-spec.yml` runs:
1. **Spec Generation** - Generate OpenAPI from Pydantic
2. **Contract Validation** - Ensure metadata complete
3. **Drift Detection** - Fail on breaking changes
4. **Version Bumping** - Auto-bump `__manifest__.py` on main
5. **OCA MQT** - Quality checks on all modules
6. **OTel Tests** - Trace context propagation validation

### Quality Gates
- ❌ **Spec Drift** - Breaking changes require version bump
- ❌ **Missing Metadata** - All endpoints need contract metadata
- ❌ **Invalid Scopes** - Role scopes must follow `role:permission` format
- ❌ **Atomic Non-Idempotent** - Atomic operations should be idempotent

## Local Development

```bash
# Install dependencies
pip install pydantic pyyaml click

# Full CI pipeline
make spec-ci

# Individual operations
make spec              # Generate spec
make spec-validate     # Validate metadata
make spec-drift        # Check drift
make spec-bump         # Bump versions
make mqt-odoo          # OCA quality checks
```

## Best Practices

1. **Contract-First**: Define Pydantic models before implementation
2. **Atomic + Idempotent**: Use `x-atomic: true` with `x-idempotency: key-based`
3. **Clear Scopes**: Define granular role:permission combinations
4. **Version Discipline**: Bump major/minor for breaking changes, patch for fixes
5. **Test Contracts**: Validate schemas in unit tests

## Troubleshooting

### Spec Drift Detected
```bash
# View differences
git diff spec/openapi.json

# If intentional breaking change:
1. Bump major/minor version in affected __manifest__.py
2. Update spec: make spec
3. Commit both changes together
```

### Missing Contract Metadata
```bash
# Add to SPEC_REGISTRY
"x-atomic": True,
"x-idempotency": "key-based",
"x-role-scopes": ["user:read", "admin:all"]
```

### Invalid Role Scopes
```bash
# Wrong: "admin" (no permission)
# Right: "admin:all"

# Wrong: "user:read:write" (too many colons)
# Right: ["user:read", "user:write"]
```

## References

- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OCA Module Structure](https://github.com/OCA/maintainer-tools)
