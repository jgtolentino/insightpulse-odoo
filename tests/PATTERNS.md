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
