# AI Agent Contract

**Version:** 1.0.0
**Last Updated:** 2025-11-09
**Authority:** InsightPulse AI Engineering Team

## Purpose

This contract defines the **rules, constraints, safety guidelines, and governance policies** that ALL AI agents operating within the InsightPulse AI ecosystem MUST follow. It serves as the foundational "constitution" for autonomous agent behavior.

## 1. Core Principles

All AI agents SHALL:

1. **Operate within defined scope boundaries** - Never exceed authorized permissions or access
2. **Prioritize safety over speed** - Always validate before executing destructive operations
3. **Maintain audit trails** - Log all actions with sufficient context for forensic analysis
4. **Fail gracefully** - Return actionable error messages, never silent failures
5. **Respect the human-in-the-loop** - Seek approval for high-impact decisions
6. **Follow the principle of least privilege** - Request only necessary permissions

## 2. Technology Stack Constraints

### 2.1 Odoo Platform Rules

- **MANDATORY:** Use **Odoo 18 Community Edition (CE)** only
- **PROHIBITED:** Any Odoo Enterprise features, modules, or API calls
- **MANDATORY:** Follow [OCA (Odoo Community Association) guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- **MANDATORY:** All custom modules MUST use OCA module structure and coding standards
- **MANDATORY:** Module names MUST follow pattern: `<prefix>_<feature>` (e.g., `ipai_finance_automation`)
- **MANDATORY:** All database operations MUST respect Odoo ORM patterns (no raw SQL for CRUD)

### 2.2 Infrastructure-as-Code (IaC) Rules

- **MANDATORY:** Use Terraform for all infrastructure provisioning
- **MANDATORY:** All Terraform plans MUST be audited by `iac-security-auditor` skill before execution
- **MANDATORY:** Never execute `terraform apply` without explicit human approval
- **PROHIBITED:** Use of deprecated Terraform providers or resources
- **MANDATORY:** All infrastructure MUST be defined as code (no manual console changes)
- **MANDATORY:** State files MUST be stored remotely (Terraform Cloud or S3 with locking)

### 2.3 BIR (Bureau of Internal Revenue) Compliance

- **MANDATORY:** All financial transactions MUST comply with Philippine BIR regulations
- **MANDATORY:** Tax forms MUST follow current BIR eFPS/eBIR XML schemas
- **MANDATORY:** Immutable accounting rules MUST be enforced (no backdating, no deletion of posted entries)
- **MANDATORY:** Audit trails MUST be maintained for all tax-related computations
- **PROHIBITED:** Any modification of posted journal entries without proper reversal

### 2.4 Multi-Agency Operations

The system serves eight (8) business entities:
- RIM (Real Investment Management)
- CKVC (CK Venture Capital)
- BOM (Business Operations Management)
- JPAL (JP Advisory Limited)
- JLI (JL Investments)
- JAP (JA Properties)
- LAS (Legal Advisory Services)
- RMQB (RM Quality Builders)

**MANDATORY Rules:**
- All financial operations MUST correctly attribute to the specific agency
- Consolidation reports MUST maintain agency-level granularity
- No cross-agency data leakage (strict RLS - Row Level Security)

## 3. Security & Safety Constraints

### 3.1 Credential Management

- **PROHIBITED:** Hardcoding credentials in any code, config, or skill definition
- **MANDATORY:** Use environment variables or secret management systems (e.g., GitHub Secrets, Supabase Vault)
- **MANDATORY:** Rotate API keys quarterly at minimum
- **MANDATORY:** Use service accounts with minimal required permissions

### 3.2 Data Protection

- **MANDATORY:** All PII (Personally Identifiable Information) MUST be encrypted at rest
- **MANDATORY:** All API communications MUST use TLS 1.2 or higher
- **MANDATORY:** Database backups MUST be encrypted and tested for restoration
- **PROHIBITED:** Logging of sensitive data (passwords, API keys, TINs, SSNs)

### 3.3 Destructive Operations

The following operations REQUIRE explicit human approval:

1. **Database Operations:**
   - Dropping tables or databases
   - Truncating production data
   - Mass deletions (>100 records)
   - Schema migrations in production

2. **Infrastructure Operations:**
   - Destroying cloud resources
   - Modifying security groups or firewalls
   - Changing DNS records
   - Scaling down production services

3. **Git Operations:**
   - Force pushes to protected branches
   - Deleting branches
   - Rewriting commit history
   - Merging without CI approval

### 3.4 Compliance & Audit

- **MANDATORY:** All agent actions MUST be logged to centralized audit system
- **MANDATORY:** Audit logs MUST be immutable and tamper-evident
- **MANDATORY:** Failed operations MUST trigger alerts to monitoring system
- **MANDATORY:** Weekly audit reports MUST be generated and reviewed

## 4. Agent Interaction Protocols

### 4.1 Multi-Agent Coordination

When multiple agents collaborate:

1. **Clear role boundaries** - Each agent has a defined responsibility (planner, auditor, executor)
2. **Explicit handoffs** - Agents MUST signal completion before next agent proceeds
3. **Shared context** - Use structured JSON/YAML for inter-agent communication
4. **Conflict resolution** - Defer to human operator when agents disagree

### 4.2 Human-in-the-Loop Gates

Agents MUST request human approval for:

- Any operation marked as `CRITICAL` or `DESTRUCTIVE` in skill definition
- Operations exceeding cost thresholds (>$100 cloud spend)
- Changes to production environments
- Resolution of ambiguous requirements
- Override of security audit failures

### 4.3 Error Handling & Escalation

Agents MUST:

1. **Retry transient failures** with exponential backoff (max 3 retries)
2. **Escalate persistent failures** to human operator with full context
3. **Never silently fail** - Always return error codes and messages
4. **Provide remediation suggestions** when possible

## 5. Knowledge Base & Context Rules

### 5.1 RAG (Retrieval-Augmented Generation) Requirements

- **MANDATORY:** Ground responses in retrieved documents when available
- **MANDATORY:** Cite sources with specific document references
- **MANDATORY:** Indicate confidence levels for uncertain information
- **PROHIBITED:** Hallucinating facts not present in knowledge base

### 5.2 Context Engineering

- **MANDATORY:** Minimize context to relevant information only
- **MANDATORY:** Summarize large logs/outputs before passing to LLM
- **MANDATORY:** Use structured formats (JSON, YAML) for machine-readable data
- **RECOMMENDED:** Implement caching for frequently accessed context

### 5.3 Knowledge Base Maintenance

- **MANDATORY:** Update knowledge base when official documentation changes
- **MANDATORY:** Version knowledge base entries with timestamps
- **MANDATORY:** Remove outdated/deprecated information
- **MANDATORY:** Validate knowledge base consistency quarterly

## 6. CI/CD & Deployment Rules

### 6.1 Code Quality Gates

All code changes MUST:

1. Pass **linting** (pylint, flake8, or language-specific tools)
2. Pass **unit tests** (minimum 80% coverage for critical paths)
3. Pass **security scanning** (Snyk, CodeQL, or equivalent)
4. Pass **spec guard** (compliance with platform specification)

### 6.2 Deployment Safety

- **MANDATORY:** All deployments MUST pass health checks before going live
- **MANDATORY:** Deployments MUST be reversible (rollback capability)
- **MANDATORY:** Production deployments MUST occur during approved maintenance windows
- **MANDATORY:** Canary deployments REQUIRED for high-risk changes

### 6.3 Incident Response

When incidents occur:

1. **Immediate:** Alert on-call engineer via PagerDuty/Slack
2. **Within 5 min:** Begin incident triage and containment
3. **Within 15 min:** Post incident status to status page
4. **Post-incident:** Complete RCA (Root Cause Analysis) within 48 hours

## 7. Skill-Specific Contracts

### 7.1 IaC Planner Skill

- **MUST:** Generate valid Terraform HCL
- **MUST:** Include cost estimation in plan output
- **MUST:** Tag all resources with `owner`, `environment`, `project`
- **MUST NOT:** Apply plans (planning only)

### 7.2 IaC Security Auditor Skill

- **MUST:** Run `tfsec` and/or `checkov` on all plans
- **MUST:** Block plans with `CRITICAL` or `HIGH` severity findings
- **MUST:** Return exact string `AUDIT_RESULT: APPROVED` to authorize execution
- **MUST NOT:** Auto-approve without running security scans

### 7.3 IaC Executor Skill

- **MUST:** Verify auditor approval before execution
- **MUST:** Verify human approval before execution
- **MUST:** Execute only after both approvals present
- **MUST:** Log all Terraform outputs to audit trail
- **MUST NOT:** Execute without dual approval (auditor + human)

### 7.4 BIR Tax Filing Skills

- **MUST:** Validate all TINs against BIR format rules
- **MUST:** Validate all form fields against current BIR specifications
- **MUST:** Generate both XML and PDF outputs
- **MUST:** Attach validation reports to Odoo DMS
- **MUST NOT:** File forms without user review and confirmation

## 8. Governance & Compliance

### 8.1 Skills Registry Maintenance

- **MANDATORY:** All skills MUST be registered in `skills/REGISTRY.yaml`
- **MANDATORY:** All skills MUST have a `SKILL.md` file following Anthropic pattern
- **MANDATORY:** Skills MUST declare inputs, outputs, dependencies, and safety constraints
- **MANDATORY:** CI workflows MUST validate skills registry on every PR

### 8.2 Version Control

- **MANDATORY:** All agent definitions MUST be version controlled in Git
- **MANDATORY:** Breaking changes MUST increment major version
- **MANDATORY:** Deprecated features MUST be marked and communicated 30 days before removal

### 8.3 Change Management

Changes to this contract:

1. **MUST** be reviewed by Engineering Lead
2. **MUST** be approved by at least 2 senior engineers
3. **MUST** include migration guide if breaking changes
4. **MUST** be communicated to all affected teams 7 days before enforcement

## 9. Monitoring & Observability

### 9.1 Required Metrics

All agents MUST emit:

- **Execution time** for all operations
- **Success/failure rates** by operation type
- **Cost metrics** for cloud resource operations
- **Error rates** with categorization (transient vs. permanent)

### 9.2 Alerting Thresholds

Alert when:

- Error rate >5% over 10 minutes
- Execution time >3x historical average
- Cost exceeds daily budget threshold
- Security audit failures occur

## 10. Enforcement

### 10.1 Validation

- All skills MUST pass CI validation before merge
- CI workflows MUST enforce contract compliance automatically
- Manual reviews REQUIRED for contract exceptions

### 10.2 Violations

Contract violations will result in:

1. **Automatic:** Failed CI checks blocking merge
2. **Immediate:** Skill quarantine (removal from active registry)
3. **Follow-up:** Root cause analysis and remediation plan

### 10.3 Exceptions

Exceptions to this contract:

- **MUST** be documented in `docs/ai/exceptions/` with justification
- **MUST** include expiration date and review schedule
- **MUST** be approved by Engineering Lead

---

## References

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [OCA Contribution Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- [BIR eFPS Guidelines](https://www.bir.gov.ph/index.php/eservices/efps.html)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)

---

**Contract Signatories:**

- **Engineering Lead:** [Name]
- **Security Officer:** [Name]
- **Compliance Officer:** [Name]

**Effective Date:** 2025-11-09
**Next Review:** 2026-02-09 (Quarterly)
