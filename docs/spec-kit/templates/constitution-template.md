# Project Constitution

## Purpose

This constitution defines the foundational principles, standards, and constraints that govern ALL development in this project. These are immutable rules that must be followed for every specification, plan, and implementation.

## Core Principles

### 1. Compliance First
- **BIR Compliance**: All tax calculations and reporting must comply with Philippine BIR regulations
- **Audit Trail**: Every financial transaction must maintain complete audit trail
- **Data Integrity**: Financial data must be immutable once posted
- **Regulatory Reporting**: All regulatory reports must be accurate and timely

### 2. OCA Standards
- **Module Structure**: All Odoo modules follow OCA guidelines
- **Code Quality**: All code passes OCA quality checks (pylint, flake8)
- **Documentation**: All modules include README.rst with OCA template
- **Versioning**: Semantic versioning for all modules
- **Dependencies**: Prefer OCA community modules over custom code

### 3. Security & Data Governance
- **Access Control**: Role-based access control (RBAC) for all features
- **Data Privacy**: PII must be encrypted at rest and in transit
- **Authentication**: Multi-factor authentication for privileged operations
- **Audit Logging**: All sensitive operations logged with user, timestamp, action
- **Separation of Duties**: Financial operations require segregation of duties

### 4. Quality & Testing
- **Test Coverage**: Minimum 80% test coverage for financial modules
- **Acceptance Testing**: All acceptance criteria must have automated tests
- **Code Review**: All code requires peer review before merge
- **Continuous Integration**: All tests must pass before deployment
- **Performance**: Page load < 2 seconds, API response < 500ms

### 5. Multi-Agency Coordination
- **Standardization**: Consistent chart of accounts across agencies
- **Consolidation**: Support for multi-agency financial consolidation
- **Isolation**: Data isolation between agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- **Reporting**: Consolidated and agency-specific reporting

## Technical Standards

### Architecture Constraints

#### Technology Stack
- **Backend**: Odoo 19 Community Edition
- **Database**: PostgreSQL 15+
- **Frontend**: Odoo Web Client (OWL framework)
- **Deployment**: Docker containers on DigitalOcean
- **CI/CD**: GitHub Actions
- **Monitoring**: Supabase + Apache Superset

#### Integration Patterns
- **APIs**: RESTful APIs for external integrations
- **MCP**: Model Context Protocol for AI agent access
- **Webhooks**: Event-driven integrations via webhooks
- **ETL**: Scheduled jobs for data synchronization
- **Real-time**: PostgreSQL triggers for real-time updates

#### Data Standards
- **Date Format**: ISO 8601 (YYYY-MM-DD)
- **Currency**: PHP (Philippine Peso) as base currency
- **Precision**: 2 decimal places for amounts, 4 for rates
- **Encoding**: UTF-8 for all text
- **Time Zone**: Asia/Manila (UTC+8)

### OCA Module Standards

#### Module Structure
```
module_name/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── *.py
├── views/
│   └── *.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   └── *.xml
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── static/
│   └── description/
│       ├── icon.png
│       └── index.html
└── README.rst
```

#### Naming Conventions
- **Module Name**: `{prefix}_{functional_area}` (e.g., `bir_tax_filing`)
- **Model Names**: `{module}.{object}` (e.g., `bir.form.2550q`)
- **Field Names**: `snake_case` (e.g., `bir_reference_number`)
- **XML IDs**: `{module}.{type}_{name}` (e.g., `bir_tax_filing.view_form_2550q`)

#### Code Quality
- **Linting**: pylint score ≥ 8.0/10
- **Style**: PEP 8 compliance via flake8
- **Complexity**: Max cyclomatic complexity 10
- **Docstrings**: All public methods documented
- **Type Hints**: Use type hints for all function signatures

### BIR Compliance Requirements

#### Immutable Fields
Once a BIR form is submitted:
- Taxable amounts cannot be modified
- Tax due amounts cannot be modified
- Filing dates cannot be modified
- Form type cannot be changed

#### Audit Requirements
- Complete audit trail of all BIR form changes
- User who created/modified each form
- Timestamp of all changes
- Previous values for modified fields
- Reason for amendments (if any)

#### Validation Rules
- TIN format: 9 or 12 digits
- RDO code: 3 digits
- Form series: Alphanumeric, max 20 chars
- Amounts: Non-negative, 2 decimal places
- Dates: Valid dates, not future dates

#### Filing Requirements
- Electronic filing capability
- PDF generation for printing
- BIR attachment uploads
- Filing deadline validation
- Penalty calculation for late filing

### Security Requirements

#### Authentication
- Session timeout: 30 minutes
- Password policy: Min 12 chars, complexity requirements
- MFA required for: Finance users, System admins
- API keys: Rotated every 90 days

#### Authorization
- **Accounting Manager**: Full access to financial modules
- **Accountant**: Can create/modify journal entries (draft)
- **Accounting Reviewer**: Can review and post entries
- **Auditor**: Read-only access to all financial data
- **Agency User**: Access only to their agency data

#### Data Protection
- **Encryption at Rest**: PostgreSQL transparent data encryption
- **Encryption in Transit**: TLS 1.3 for all connections
- **PII Masking**: Mask sensitive fields in logs
- **Backup Encryption**: All backups encrypted with AES-256

### Performance Requirements

#### Response Times
- Page Load: < 2 seconds (95th percentile)
- API Response: < 500ms (95th percentile)
- Report Generation: < 5 seconds for standard reports
- Search: < 1 second for typical queries

#### Scalability
- Support: 100 concurrent users
- Transactions: 10,000 journal entries per month
- Data Retention: 7 years of financial data
- Backup: Full backup within 4 hours

#### Monitoring
- Uptime: 99.5% availability
- Error Rate: < 0.1% of requests
- Alert Response: Critical alerts within 15 minutes
- Incident Resolution: P0 within 4 hours, P1 within 24 hours

## Development Workflow

### Spec-Driven Process
1. **Specify**: Write detailed specification BEFORE coding
2. **Plan**: Create implementation plan with architecture
3. **Task**: Break down into granular tasks (< 4 hours)
4. **Implement**: Code following spec and plan
5. **Test**: Validate all acceptance criteria
6. **Review**: Peer review before merge
7. **Deploy**: CI/CD pipeline to production

### Quality Gates

#### Before Planning
- ☐ Specification approved by stakeholders
- ☐ BIR compliance reviewed (if applicable)
- ☐ Security implications assessed
- ☐ Performance requirements defined

#### Before Implementation
- ☐ Implementation plan reviewed
- ☐ OCA standards validated
- ☐ Database design approved
- ☐ Test strategy defined

#### Before Merge
- ☐ All tests passing
- ☐ Code review approved
- ☐ Documentation updated
- ☐ No security vulnerabilities
- ☐ Performance benchmarks met

#### Before Production
- ☐ UAT completed successfully
- ☐ Rollback plan tested
- ☐ Monitoring configured
- ☐ Backup verified
- ☐ Stakeholder sign-off

## Prohibited Practices

### Code
- ❌ Direct database queries (use ORM)
- ❌ Hardcoded credentials
- ❌ SQL injection vulnerabilities
- ❌ Unvalidated user input
- ❌ Bypassing security checks

### Financial Data
- ❌ Modifying posted journal entries
- ❌ Deleting audit trail records
- ❌ Backdating financial transactions
- ❌ Manual tax calculations (must be automated)
- ❌ Unapproved chart of accounts changes

### Process
- ❌ Coding without specification
- ❌ Deploying without testing
- ❌ Skipping code review
- ❌ Ignoring linter warnings
- ❌ Breaking backward compatibility

## Exception Process

When deviation from constitution is required:

1. **Document**: Write exception request with justification
2. **Review**: Technical lead reviews technical exceptions
3. **Approve**: Stakeholders approve business exceptions
4. **Track**: Add to exception log with expiration date
5. **Remediate**: Plan to eliminate exception

Exception log location: `docs/spec-kit/exception-log.md`

## Maintenance

### Constitution Updates
- **Frequency**: Reviewed quarterly
- **Process**: Propose changes via PR, team review required
- **Approval**: Requires unanimous team approval
- **Communication**: All changes announced to team

### Version History
- **v1.0** (2025-11-08): Initial constitution for InsightPulse
- Future versions documented here

## References

- OCA Guidelines: https://github.com/OCA/odoo-community.org
- BIR Forms: https://www.bir.gov.ph/
- Odoo Development: https://www.odoo.com/documentation/
- PostgreSQL Best Practices: https://wiki.postgresql.org/wiki/Don%27t_Do_This
- OWASP Top 10: https://owasp.org/www-project-top-ten/

---

**This constitution is binding on all development. Violations must be justified and approved through the exception process.**
