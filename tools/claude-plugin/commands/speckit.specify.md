# Spec-Kit: Create Specification

Create a new specification using the template at `docs/spec-kit/templates/specification-template.md`.

## Process

1. **Identify**: What feature/system needs to be specified?
2. **Research**: Review existing patterns, OCA modules, BIR requirements
3. **Define Requirements**:
   - Functional requirements (what the system does)
   - Non-functional requirements (performance, security, compliance)
   - BIR compliance needs (if applicable)
4. **Specify Acceptance Criteria**: Make them testable and measurable
5. **Document Dependencies**: Technical, team, timeline dependencies
6. **Identify Risks**: What could go wrong? How to mitigate?
7. **Save**: Save to `docs/spec-kit/specs/[ID]-[name].md`

## Quality Checklist

Before considering spec complete:
- ☐ Business value clearly articulated
- ☐ Problem statement describes current vs. desired state
- ☐ User stories capture who, what, why
- ☐ Functional requirements are specific and complete
- ☐ Non-functional requirements include targets and measurement
- ☐ Acceptance criteria are testable (avoid "should work well")
- ☐ BIR compliance addressed (if financial feature)
- ☐ OCA standards referenced (if Odoo module)
- ☐ Data model designed (if database changes)
- ☐ Security and privacy requirements defined
- ☐ Dependencies identified (technical, team, timeline)
- ☐ Risks documented with mitigation strategies
- ☐ Success metrics defined (KPIs, business impact)

## Examples of Good Acceptance Criteria

✅ **Good**: "Page loads in < 2 seconds with 1000 journal entries"
❌ **Bad**: "System should be fast"

✅ **Good**: "BIR Form 2550Q generates PDF with all required fields populated from account.move.line"
❌ **Bad**: "BIR form should work correctly"

✅ **Good**: "User can create journal entry only if balance = 0 and user has 'Accountant' role"
❌ **Bad**: "Journal entries should be balanced"

## Template Location
`docs/spec-kit/templates/specification-template.md`

## Example Spec
`docs/spec-kit/specs/001-finserv-skills-parity.md`

Validate spec completeness before proceeding to planning phase.
