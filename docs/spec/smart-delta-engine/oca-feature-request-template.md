# OCA Feature Request Template

Use this template when gap_level = 1 or 2 and OCA enhancement is needed.

---

## Template

```markdown
# OCA Feature Request — [FEATURE_NAME]

## Problem
[Describe the enterprise capability that is not fully covered by existing OCA modules]

## Proposed Solution
Extend existing OCA `[module_name]` module to support:
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Justification
- Eliminates need for custom module
- Widely applicable to [target users]
- Aligns with Odoo CE [related functionality]

## References
- [Enterprise source 1]
- [Enterprise source 2]
- [Odoo docs reference]

## Smart Delta Classification
Gap Level: [1 or 2]
Preferred Resolution: OCA

## Technical Approach
- [ ] Extend existing model `[model.name]`
- [ ] Add fields: [field_list]
- [ ] Add views: [view_list]
- [ ] Add security: [security_rules]
- [ ] No controllers (if possible)
- [ ] No JS (if possible)

## Backwards Compatibility
- [ ] No breaking changes to existing functionality
- [ ] Migration script provided (if needed)
- [ ] All existing tests pass

## Testing
- [ ] Unit tests for new functionality
- [ ] Integration tests with related modules
- [ ] Manual test scenarios documented
```

---

## Example: Budget Forecast Locking

```markdown
# OCA Feature Request — Budget Forecast Locking

## Problem
Enterprise ERP systems support forecast locking per budget period to prevent retroactive changes. Current OCA `account_budget` module does not support period-based locking of forecast values.

## Proposed Solution
Extend existing OCA `account_budget` module to support:
- Forecast snapshot locking per period
- Read-only historical periods
- Configurable unlock permissions (security group)
- Lock/unlock wizard for bulk operations

## Justification
- Eliminates need for custom module
- Widely applicable to finance teams using budget control
- Aligns with Odoo CE accounting periods concept

## References
- SAP Budget Control Docs: Budget Period Locking
- Odoo Accounting Periods documentation
- Current OCA account_budget implementation

## Smart Delta Classification
Gap Level: 1
Preferred Resolution: OCA

## Technical Approach
- [ ] Extend existing model `crossovered.budget`
- [ ] Add fields: `is_locked`, `locked_date`, `locked_by`
- [ ] Add views: Lock/unlock wizard, period lock indicator
- [ ] Add security: `group_budget_lock_manager`
- [ ] No controllers required
- [ ] No JS required (standard Odoo views)

## Backwards Compatibility
- [ ] Default `is_locked = False` for existing records
- [ ] No changes to existing budget line behavior
- [ ] All existing tests pass

## Testing
- [ ] Unit tests for lock/unlock operations
- [ ] Integration tests with budget workflow
- [ ] Test scenarios:
  - Lock budget period
  - Attempt modification of locked period (should fail)
  - Unlock with proper permissions
  - Bulk lock via wizard
```

---

## Submission Checklist

Before submitting to OCA:

- [ ] Feature request follows template
- [ ] Problem clearly stated
- [ ] Solution is minimal and focused
- [ ] No unnecessary dependencies
- [ ] Backwards compatible
- [ ] Test plan included
- [ ] Referenced in Smart Delta parity map
- [ ] Gap level documented
