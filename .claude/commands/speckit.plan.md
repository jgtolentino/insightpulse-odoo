# Spec-Kit: Create Implementation Plan

Create implementation plan from specification using template at `docs/spec-kit/templates/plan-template.md`.

## Process

1. **Review Specification**: Read the spec thoroughly, understand all requirements
2. **Design Architecture**:
   - System components and data flow
   - Technology choices (justify each)
   - Integration patterns
3. **Plan OCA Module Structure** (if Odoo module):
   - Module dependencies
   - Models, views, security
   - Follows OCA guidelines
4. **Design Data Models**:
   - New models and modified models
   - Database schema changes
   - Migration strategy
5. **Define Integration Approach**:
   - APIs, MCP connectors, webhooks
   - Authentication and authorization
6. **Create Testing Strategy**:
   - Unit tests, integration tests, evals
   - Performance tests
   - Acceptance testing approach
7. **Identify Technical Risks**: And mitigation strategies
8. **Save**: Save to `docs/spec-kit/plans/[ID]-[name].md`

## Quality Checklist

Before considering plan complete:
- ☐ All spec requirements addressed in plan
- ☐ Architecture documented with diagrams
- ☐ OCA module structure planned (if applicable)
- ☐ Data model designed (new/modified models, migrations)
- ☐ Integration points defined (APIs, MCP, webhooks)
- ☐ Security implementation specified (access control, encryption)
- ☐ Testing strategy covers unit, integration, performance
- ☐ Deployment strategy documented (prerequisites, steps, rollback)
- ☐ Performance optimization considered (indexes, caching, queries)
- ☐ Documentation plan included
- ☐ Technical risks from spec addressed
- ☐ OCA standards validated
- ☐ BIR compliance requirements implemented (if applicable)

## Architecture Checklist

Ensure plan includes:
- [ ] Component diagram showing system parts
- [ ] Data flow from input to output
- [ ] Database schema (tables, indexes, constraints)
- [ ] API design (endpoints, request/response formats)
- [ ] Security model (roles, permissions, RLS)
- [ ] Performance considerations (caching, indexing)
- [ ] Monitoring and alerting strategy

## Common Pitfalls to Avoid

❌ **Don't**: Jump directly from spec to code
✅ **Do**: Create detailed technical plan first

❌ **Don't**: Ignore migration strategy
✅ **Do**: Plan data migration and rollback

❌ **Don't**: Skip testing strategy
✅ **Do**: Define test approach upfront

❌ **Don't**: Forget about monitoring
✅ **Do**: Plan health checks and metrics

## Template Location
`docs/spec-kit/templates/plan-template.md`

Ensure plan aligns with constitution and OCA standards before proceeding to task breakdown.
