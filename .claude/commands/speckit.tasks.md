# Spec-Kit: Break Down Into Tasks

Break implementation plan into granular tasks.

## Process

1. **Review Implementation Plan**: Understand the technical approach
2. **Create Granular Tasks**:
   - Each task < 4 hours
   - Specific and actionable
   - Clear acceptance criteria
3. **Define Dependencies**: What must complete before each task?
4. **Assign Priorities**: P0 (must have), P1 (should have), P2 (nice to have)
5. **Estimate Effort**: Hours per task
6. **Group Into Sprints**: Logical groupings for iterations

## Task Structure

Each task should have:
```yaml
- id: TASK-001
  title: Clear, actionable title
  description: Detailed description of what to do
  component: [module/service name]
  priority: P0 | P1 | P2
  estimate: [hours]
  dependencies: [TASK-IDs that must complete first]
  acceptance_criteria:
    - Specific, testable criterion 1
    - Specific, testable criterion 2
    - All tests pass
    - Code review approved
```

## Quality Checklist

Before considering tasks complete:
- ☐ All plan components broken into tasks
- ☐ Each task is < 4 hours estimated effort
- ☐ Each task has clear acceptance criteria
- ☐ Dependencies identified (cannot start until X completes)
- ☐ Priorities assigned (P0, P1, P2)
- ☐ Effort estimated (hours)
- ☐ Tasks grouped into logical sprints/milestones
- ☐ Critical path identified

## Examples

### Good Task (Clear, Specific, Small)
```yaml
- id: TASK-BIR-001
  title: Create BIR Form 2550Q model extension
  description: |
    Extend account.move to add BIR Form 2550Q specific fields:
    - bir_form_type (Selection: 2550Q, 2550M)
    - bir_reference_number (Char, unique)
    - bir_filing_date (Date)
    - bir_rdo_code (Char, 3 digits)
  component: bir_tax_filing
  priority: P0
  estimate: 3h
  dependencies: []
  acceptance_criteria:
    - Fields added to account.move model
    - Migration script creates fields without data loss
    - TIN validation enforces 9 or 12 digit format
    - Unit tests validate constraints
    - pylint score ≥ 8.0
```

### Bad Task (Vague, Large, No Criteria)
```yaml
- id: TASK-BAD-001
  title: Implement BIR module
  description: Build the BIR tax filing system
  priority: P0
  estimate: 40h
  acceptance_criteria:
    - BIR module works
```
**Problems**: Too large (40h), vague criteria, no component, no dependencies

## Task Organization

Group tasks into milestones:
- **M1**: Core data model and basic CRUD (Week 1)
- **M2**: Business logic and validations (Week 2)
- **M3**: UI views and workflows (Week 3)
- **M4**: Integration and testing (Week 4)

## Dependencies

Identify dependency types:
- **Technical**: Task A must complete before Task B (e.g., model before view)
- **Team**: Waiting for another team/person
- **External**: Waiting for API access, approvals, etc.

## Critical Path

Identify the longest chain of dependent tasks (critical path):
- These tasks cannot be parallelized
- Delays here delay the entire project
- Focus effort on critical path items

## Save Location
`docs/spec-kit/tasks/[ID]-[name].yaml` or `.md`

Ensure tasks are granular and actionable before proceeding to implementation.
