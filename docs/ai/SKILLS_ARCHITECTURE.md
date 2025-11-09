# InsightPulse AI Skills Architecture

**Version:** 1.0.0
**Last Updated:** 2025-11-09
**Status:** Active

## Executive Summary

This document defines the **consolidated AI skills architecture** for the InsightPulse AI ecosystem, following the Anthropic skills model. It serves as the authoritative reference for:

1. **Skills taxonomy and organization**
2. **Multi-agent coordination patterns**
3. **Governance and compliance frameworks**
4. **Integration with CI/CD and knowledge systems**

The architecture enables InsightPulse AI to compete with foundational LLM providers by building a robust "nervous system" that wields AI with reliability, security, and deep integration.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Skills Taxonomy](#skills-taxonomy)
4. [Directory Structure](#directory-structure)
5. [Skill Anatomy](#skill-anatomy)
6. [Multi-Agent Patterns](#multi-agent-patterns)
7. [Governance & Validation](#governance--validation)
8. [Knowledge Base Integration](#knowledge-base-integration)
9. [CI/CD Integration](#cicd-integration)
10. [Usage Guide](#usage-guide)
11. [References](#references)

---

## Overview

### What is a Skill?

Following the [Anthropic skills model](https://github.com/anthropics/skills), a **Skill** is:

> A folder of instructions, scripts, and resources that Claude loads dynamically to perform specialized tasks.

Each skill:
- Has a clear **role and purpose**
- Defines **inputs, outputs, and dependencies**
- Specifies **constraints and safety rules**
- Provides **step-by-step procedures**
- Includes **examples and integration patterns**

### Why This Architecture?

Traditional automation teams face a challenge: transitioning from **rule-based automation** to **agentic automation** (goal-oriented, autonomous, reasoning-driven). This architecture:

1. **Formalizes expertise** - Codifies DevOps, IaC, Finance SSC, and Odoo knowledge into reusable skills
2. **Enables multi-agent systems** - Coordinates specialized agents (planner, auditor, executor)
3. **Ensures safety** - Implements guardrails, human-in-the-loop gates, and audit trails
4. **Scales knowledge** - Uses RAG and knowledge graphs to ground AI in company-specific rules

### Key Differentiators

| Aspect | Traditional Automation | InsightPulse AI Skills |
|--------|------------------------|------------------------|
| **Trigger** | Event-driven (webhook, cron) | Goal-driven (natural language request) |
| **Logic** | Hardcoded rules (if-then) | Reasoning (LLM + tools) |
| **Adaptability** | Requires code changes | Self-adapting via prompt engineering |
| **Knowledge** | Embedded in code | Externalized in vector stores/knowledge graphs |
| **Audit** | Logs only | Full reasoning trace + citations |

---

## Architecture Principles

### 1. Modularity

Each skill is **self-contained** with:
- Clear boundaries (scope)
- Explicit dependencies
- Versioned definitions
- Independent testing

### 2. Composability

Skills **combine** to solve complex problems:
- `iac-planner` → `iac-security-auditor` → `iac-executor` (DevOps crew)
- `sre-cicd-gates-maintainer` → `sre-context-engineering` (SRE workflow)

### 3. Safety-First

Every skill:
- Declares prohibited actions
- Requires approvals for destructive operations
- Maintains audit trails
- Fails gracefully with actionable errors

### 4. Knowledge-Grounded

Skills retrieve context from:
- **Vector stores** (Pinecone, ChromaDB) - Unstructured docs, regulations
- **Knowledge graphs** (Neo4j) - Structured relationships (tax rules, accounting sequences)
- **Relational DBs** (PostgreSQL/Supabase) - Transactional data

### 5. CI/CD Native

All skills:
- Are version controlled in Git
- Pass validation in CI pipelines
- Are tested with evaluation suites
- Are deployed via GitOps

---

## Skills Taxonomy

Skills are organized into **three primary categories** based on the AI Agent Upskilling framework:

### Category A: Foundational Agentic Skills

**Purpose:** Underlying capabilities required for any agent to function

| Skill ID | Purpose | Key Techniques |
|----------|---------|----------------|
| `prompt-engineering` | Craft clear, context-rich, role-based prompts | Role definition, few-shot examples, chain-of-thought |
| `rag-retrieval` | Ground responses in proprietary data | Vector similarity search, semantic chunking, citation |
| `orchestration-tools` | Build chains of thought, manage memory | LangChain, LlamaIndex, state machines |
| `tool-use-function-calling` | Expose automation scripts as callable functions | OpenAPI specs, MCP servers, Agent Studio endpoints |

### Category B: Specialized DevOps Agent Skills

**Purpose:** Role-based modules for multi-agent DevOps workflows

| Skill ID | Role | Category | Safety |
|----------|------|----------|--------|
| `iac-planner` | Senior DevOps Engineer | `devops_agent` | `PLANNING_ONLY` |
| `iac-security-auditor` | QA Agent | `devops_agent` | `BLOCKS_ON_CRITICAL` |
| `iac-executor` | Automated Deployment Tool | `devops_agent` | `REQUIRES_DUAL_APPROVAL` |

**Workflow Pattern:**

```
User Request: "Deploy a new PostgreSQL database in production"
    ↓
[iac-planner]
    → Generates Terraform HCL + execution plan
    → Estimates cost: $47/month
    → Tags: owner=sre, env=production, project=insightpulse
    ↓
[iac-security-auditor]
    → Runs tfsec + checkov
    → Finds: CRITICAL - Database publicly accessible
    → Returns: AUDIT_RESULT: REJECTED
    ↓
[iac-planner] (retry)
    → Fixes: Adds security group restricting access
    → Regenerates plan
    ↓
[iac-security-auditor]
    → Re-runs scans
    → Returns: AUDIT_RESULT: APPROVED
    ↓
[Human] (approval gate)
    → Reviews plan
    → Approves: "Proceed with deployment"
    ↓
[iac-executor]
    → Verifies: auditor_approval ✓ + human_approval ✓
    → Executes: terraform apply
    → Returns: resource_ids, audit_log
```

### Category C: SRE Maintenance Skills

**Purpose:** Stabilize platform, reduce toil, improve observability

| Skill ID | Purpose | Category | Safety |
|----------|---------|----------|--------|
| `sre-cicd-gates-maintainer` | Keep core CI checks green, eliminate noise | `sre_maintenance` | `NEVER_DISABLE_CHECKS` |
| `sre-healthcheck-triage` | Diagnose healthcheck failures, harden probes | `sre_maintenance` | `NEVER_SILENCE_CRITICAL` |
| `sre-context-engineering` | Filter noise, summarize logs, structure data | `sre_maintenance` | `NEVER_LOSE_CRITICAL_INFO` |

---

## Directory Structure

```
insightpulse-odoo/
├── .claude/
│   ├── skills/                         # Symlinks exposing skills to Claude
│   │   ├── iac-planner -> ../../docs/claude-code-skills/community/iac-planner
│   │   ├── sre-cicd-gates-maintainer -> ../../docs/...
│   │   └── ...
│   └── commands/                       # Slash commands
│       ├── review-pr.md
│       └── check-compliance.md
│
├── docs/
│   ├── ai/
│   │   ├── AGENT_CONTRACT.md          # Foundational governance contract
│   │   ├── SKILLS_ARCHITECTURE.md     # This document
│   │   └── exceptions/                # Contract exception requests
│   │
│   └── claude-code-skills/            # Canonical skill definitions
│       ├── anthropic-official/        # Official Anthropic skills
│       │   ├── document-skills/
│       │   │   ├── docx/
│       │   │   ├── pdf/
│       │   │   ├── pptx/
│       │   │   └── xlsx/
│       │   ├── algorithmic-art/
│       │   ├── artifacts-builder/
│       │   └── mcp-builder/
│       │
│       ├── community/                 # InsightPulse custom skills
│       │   ├── iac-planner/
│       │   │   └── SKILL.md
│       │   ├── iac-security-auditor/
│       │   │   └── SKILL.md
│       │   ├── iac-executor/
│       │   │   └── SKILL.md
│       │   ├── sre-cicd-gates-maintainer/
│       │   │   └── SKILL.md
│       │   ├── sre-healthcheck-triage/
│       │   │   └── SKILL.md
│       │   ├── sre-context-engineering/
│       │   │   └── SKILL.md
│       │   ├── odoo-agile-scrum-devops/
│       │   ├── odoo-finance-automation/
│       │   ├── bir-tax-filing/
│       │   └── ...
│       │
│       ├── finance/                   # Finance-specific skills
│       │   ├── dcf-builder/
│       │   └── filings-edgar-ingest/
│       │
│       ├── notion/                    # Notion integration skills
│       │   ├── notion-meeting-intelligence/
│       │   ├── notion-research-documentation/
│       │   └── ...
│       │
│       └── odoo/                      # Odoo-specific skills
│           └── SKILL.md
│
├── skills/
│   ├── REGISTRY.yaml                  # Master skills catalog
│   ├── automation_executor/
│   ├── git_specialist/
│   └── ...
│
├── agents/
│   ├── REGISTRY.yaml                  # Multi-agent crew definitions
│   └── ...
│
└── .github/
    └── workflows/
        ├── skills-agents-check.yml    # Validates skills registry
        ├── claude-config.yml          # Validates skill paths
        └── spec-guard.yml             # Enforces platform spec
```

---

## Skill Anatomy

Every skill **MUST** include a `SKILL.md` file following this structure:

```markdown
# Skill Name

**Version:** X.Y.Z
**Category:** (devops_agent | sre_maintenance | finance | odoo | ...)
**Created:** YYYY-MM-DD

## Role

You are a **[specific role]**. [1-2 sentence role definition]

## Purpose

[What problem does this skill solve? What are the key capabilities?]

## Scope & Boundaries

**IN SCOPE:**
- [What this skill SHOULD do]

**OUT OF SCOPE:**
- [What this skill should NEVER do - delegate to other skills]

## Constraints & Safety Rules

### MANDATORY
1. [Required behaviors]

### PROHIBITED
1. [Forbidden actions]

## Inputs

1. [What data does this skill need?]

## Outputs

1. [What does this skill produce?]

## Procedure

### Step 1: [Phase Name] (Time estimate)

[Detailed instructions]

```bash
# Example commands
```

**Key Questions:**
- [Questions to guide decision-making]

### Step 2: [Next Phase]

...

## Examples

### Example 1: [Scenario]

**Scenario:** [Description]

**Diagnosis:**
```bash
# Commands run
```

**Fix:**
```bash
# Solution implemented
```

## Integration with Other Skills

- **skill-1:** [How they interact]
- **skill-2:** [Coordination pattern]

## Success Criteria

You have successfully completed this skill when:

1. ✅ [Success metric 1]
2. ✅ [Success metric 2]

## References

- [Relevant docs, contracts, APIs]

---

**Created by:** [Team]
**Maintained by:** [Team]
**Review Cycle:** [Frequency]
```

### Required Metadata

In `skills/REGISTRY.yaml`:

```yaml
- id: skill-unique-id
  path: docs/claude-code-skills/category/skill-name
  purpose: "One-line description"
  inputs: ["input1", "input2"]
  outputs: ["output1", "output2"]
  deps: ["ENV_VAR_1", "ENV_VAR_2"]
  category: "devops_agent | sre_maintenance | finance | ..."
  safety: "PLANNING_ONLY | BLOCKS_ON_CRITICAL | REQUIRES_DUAL_APPROVAL | ..."
```

---

## Multi-Agent Patterns

### Pattern 1: Sequential Pipeline (DevOps Crew)

**Use Case:** Infrastructure provisioning requiring planning, auditing, and execution

```
Request → Planner → Auditor → [Human Gate] → Executor → Result
```

**Implementation:**

```python
# Pseudocode
def provision_infrastructure(request):
    # Step 1: Planning
    plan = invoke_skill("iac-planner", inputs={"request": request})

    # Step 2: Security Audit
    audit = invoke_skill("iac-security-auditor", inputs={"plan": plan})

    if audit["status"] != "APPROVED":
        return {"error": "Security audit failed", "details": audit}

    # Step 3: Human Approval
    human_approval = request_approval(plan, audit)

    if not human_approval:
        return {"error": "Human approval denied"}

    # Step 4: Execution
    result = invoke_skill("iac-executor", inputs={
        "plan": plan,
        "auditor_approval": audit,
        "human_approval": human_approval
    })

    return result
```

### Pattern 2: Parallel Enrichment (SRE Diagnostics)

**Use Case:** Incident triage requiring multiple perspectives

```
Incident Alert
    ↓
    ├─→ [sre-healthcheck-triage]    → Diagnosis A
    ├─→ [sre-context-engineering]   → Filtered Logs
    └─→ [odoo-knowledge-agent]      → Historical Patterns
    ↓
Synthesized RCA
```

### Pattern 3: Iterative Refinement (Code Review)

**Use Case:** PR review with multiple feedback rounds

```
PR Submitted
    ↓
[code-reviewer] → Feedback
    ↓
Developer fixes
    ↓
[code-reviewer] → Approval ✓
    ↓
Merge
```

---

## Governance & Validation

### AI Agent Contract

**Location:** `docs/ai/AGENT_CONTRACT.md`

The contract defines:
1. **Technology stack constraints** (Odoo 18 CE only, Terraform for IaC, etc.)
2. **Security & safety rules** (no hardcoded secrets, TLS 1.2+, etc.)
3. **Destructive operation gates** (human approval required)
4. **Compliance requirements** (BIR regulations, OCA guidelines)
5. **Skill-specific contracts** (e.g., `iac-executor` MUST verify dual approval)

All skills **MUST** reference this contract in their `SKILL.md`.

### Skills Registry Validation

**Workflow:** `.github/workflows/skills-agents-check.yml`

**Validates:**
- YAML syntax is correct
- Required fields present (`id`, `path`, `purpose`)
- Paths are **relative** (not absolute)
- Symlinks resolve correctly
- No duplicate skill IDs

**Runs on:**
- Every PR modifying `skills/`, `agents/`, or `.claude/skills/`
- Push to `main` or `claude/**` branches

### Platform Specification Enforcement

**Workflow:** `.github/workflows/spec-guard.yml`

**Validates:**
- New workflows align with `spec/platform_spec.json`
- No introduction of prohibited dependencies
- Governance rules followed

---

## Knowledge Base Integration

### Three-Layer Knowledge Architecture

#### Layer 1: Vector Store (Unstructured Data)

**Purpose:** RAG for unstructured documents (regulations, manuals, forum posts)

**Technology:** Pinecone, ChromaDB, or Qdrant

**Examples:**
- BIR eFPS regulations (PDF → embeddings)
- OCA contribution guidelines (Markdown → embeddings)
- Odoo forum solutions (HTML → embeddings)

**Query Pattern:**
```python
# User asks: "What are the BIR requirements for 2550Q filing?"
relevant_chunks = vector_store.query(
    "BIR 2550Q filing requirements",
    top_k=5
)
# Returns: Top 5 most relevant chunks with citations
```

#### Layer 2: Knowledge Graph (Structured Relationships)

**Purpose:** Represent complex relationships (tax rules, accounting dependencies)

**Technology:** Neo4j or in-memory graph

**Examples:**
- Tax rules: `(TaxCode)-[:REQUIRES]->(Form)-[:DEPENDS_ON]->(TransactionType)`
- Accounting: `(JournalEntry)-[:POSTS_TO]->(Account)-[:BELONGS_TO]->(ChartOfAccounts)`

**Query Pattern:**
```cypher
// User asks: "What forms do I need for withholding tax?"
MATCH (form:BIRForm)-[:USED_FOR]->(tax:TaxType {name: 'Withholding Tax'})
RETURN form.code, form.name, form.frequency
```

#### Layer 3: Relational DB (Transactional Data)

**Purpose:** Operational data (invoices, payments, inventory)

**Technology:** PostgreSQL (Odoo database, Supabase)

**Query Pattern:**
```sql
-- User asks: "Show me unpaid invoices over 30 days old"
SELECT id, partner_id, invoice_date, amount_total
FROM account_move
WHERE state = 'posted'
  AND payment_state = 'not_paid'
  AND invoice_date < CURRENT_DATE - INTERVAL '30 days';
```

### Deep Researcher Knowledge Agent (Planned)

**Skill ID:** `stack-kg-knowledge-agent`

**Purpose:** Continuously mine repo, docs, and external sources to build lean knowledge graph

**Inputs:**
- Codebase (`git clone`, static analysis)
- External docs (Odoo docs, OCA docs, BIR site)
- Vendor documentation (Terraform, DigitalOcean)

**Outputs:**
- Knowledge graph (Neo4j or JSON-LD)
- Vector store (Pinecone/ChromaDB)
- Compliance rules (YAML or JSON)

**Maintenance:**
- **Incremental updates:** On new commits, reprocess changed files
- **Periodic refresh:** Weekly full rescan of external sources
- **Validation:** CI workflow checks graph consistency

---

## CI/CD Integration

### Skills Lifecycle

```
Skill Development (Local)
    ↓
Git Commit + Push
    ↓
CI Validation
    ├─ YAML syntax check
    ├─ Required fields check
    ├─ Symlink validation
    └─ Spec guard
    ↓
PR Review
    ↓
Merge to main
    ↓
Skills Registry Updated
    ↓
Claude Code Auto-Reloads Skills
```

### Key Workflows

#### 1. Skills & Agents Inventory Check

**File:** `.github/workflows/skills-agents-check.yml`

**Triggers:**
- PRs modifying `skills/**`, `agents/**`, `Makefile`
- Pushes to `main` or `claude/**`

**Steps:**
1. Validate `skills/REGISTRY.yaml` syntax
2. Validate `agents/REGISTRY.yaml` syntax
3. Check required fields
4. List skills and agents (for reporting)

#### 2. Claude Config Validation & Skills Sync

**File:** `.github/workflows/claude-config.yml`

**Triggers:**
- PRs modifying `claude.md`, `docs/claude-code-skills/**`, `mcp/**`

**Steps:**
1. Run `make claude:validate` (Python validator)
2. Skillsmith drift check (ensure skills sync with `claude.md`)
3. Optionally create PR to sync Section 19 (skills list)

#### 3. Auto-Fix on Failure

**File:** `.github/workflows/claude-autofix-bot.yml`

**Purpose:** When CI fails, Claude proposes fixes automatically

**Flow:**
1. CI failure detected
2. Claude analyzes logs
3. Claude proposes fix in new branch
4. Creates PR for human review

---

## Usage Guide

### For AI Agent Developers

#### Creating a New Skill

1. **Choose location:**
   ```bash
   mkdir -p docs/claude-code-skills/community/my-new-skill
   ```

2. **Create SKILL.md:**
   ```bash
   cp docs/claude-code-skills/community/iac-planner/SKILL.md \
      docs/claude-code-skills/community/my-new-skill/SKILL.md
   # Edit SKILL.md following the anatomy template
   ```

3. **Register in REGISTRY.yaml:**
   ```yaml
   - id: my-new-skill
     path: docs/claude-code-skills/community/my-new-skill
     purpose: "Brief description"
     inputs: ["input1"]
     outputs: ["output1"]
     deps: []
     category: "custom"
     safety: "SAFE"
   ```

4. **Create symlink:**
   ```bash
   ln -s ../../docs/claude-code-skills/community/my-new-skill \
         .claude/skills/my-new-skill
   ```

5. **Test locally:**
   ```bash
   # In Claude Code
   /skill my-new-skill
   ```

6. **Commit and push:**
   ```bash
   git add docs/claude-code-skills/community/my-new-skill
   git add .claude/skills/my-new-skill
   git add skills/REGISTRY.yaml
   git commit -m "feat(skills): add my-new-skill"
   git push
   ```

### For SREs

#### Using SRE Skills

**Scenario 1: CI Workflow Failing**

```bash
# Invoke skill via Claude Code
/skill sre-cicd-gates-maintainer

# Provide context
"CI Unified workflow is failing with pytest errors. Please diagnose and fix."

# Claude will:
# 1. Retrieve workflow logs
# 2. Diagnose root cause
# 3. Propose fix
# 4. Create PR with fix
```

**Scenario 2: Healthcheck Failures**

```bash
/skill sre-healthcheck-triage

"ERP healthcheck is failing with 'connection pool exhausted'. Please investigate."

# Claude will:
# 1. Retrieve healthcheck logs
# 2. Check database connections
# 3. Provide runbook
# 4. Suggest hardened configuration
```

### For DevOps Engineers

#### Provisioning Infrastructure

```bash
# Invoke DevOps crew
"Deploy a production PostgreSQL database in us-east-1 with 4GB RAM."

# Workflow:
# 1. iac-planner generates Terraform plan
# 2. iac-security-auditor audits plan
# 3. Human reviews and approves
# 4. iac-executor applies plan
```

---

## References

### Internal Documentation

- [AI Agent Contract](./AGENT_CONTRACT.md)
- [Platform Specification](/home/user/insightpulse-odoo/spec/platform_spec.json)
- [Skills Registry](/home/user/insightpulse-odoo/skills/REGISTRY.yaml)
- [Agents Registry](/home/user/insightpulse-odoo/agents/REGISTRY.yaml)

### External Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Anthropic Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [OCA Contribution Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/)
- [BIR eFPS Guidelines](https://www.bir.gov.ph/index.php/eservices/efps.html)
- [Google SRE Book](https://sre.google/sre-book/)

---

## Appendix

### Skill Categories Reference

| Category | Purpose | Examples |
|----------|---------|----------|
| `devops_agent` | Infrastructure automation | iac-planner, iac-executor |
| `sre_maintenance` | Site reliability, observability | sre-cicd-gates-maintainer, sre-healthcheck-triage |
| `finance` | Financial operations | dcf-builder, filings-edgar-ingest |
| `odoo` | Odoo ERP customization | odoo-finance-automation, odoo-agile-scrum-devops |
| `bir_compliance` | Philippine tax compliance | bir-tax-filing, paddle-ocr-validation |
| `knowledge_management` | Knowledge graph, RAG | stack-kg-knowledge-agent, odoo-knowledge-agent |
| `document_processing` | Document creation/editing | docx, pdf, pptx, xlsx |
| `integration` | External system integrations | notion-*, superset-*, firecrawl-* |

### Safety Levels Reference

| Safety Level | Meaning | Example |
|--------------|---------|---------|
| `SAFE` | No destructive actions | Context engineering, log filtering |
| `PLANNING_ONLY` | Generates plans, never executes | iac-planner |
| `BLOCKS_ON_CRITICAL` | Stops on critical issues | iac-security-auditor |
| `REQUIRES_APPROVAL` | Needs human approval | Deployment, deletion |
| `REQUIRES_DUAL_APPROVAL` | Needs auditor + human | iac-executor |
| `NEVER_DISABLE_CHECKS` | Cannot bypass safety gates | sre-cicd-gates-maintainer |
| `NEVER_SILENCE_CRITICAL` | Cannot mute critical alerts | sre-healthcheck-triage |

---

**Document Control:**
- **Author:** InsightPulse AI Engineering Team
- **Approvers:** Engineering Lead, Security Officer, Compliance Officer
- **Effective Date:** 2025-11-09
- **Next Review:** 2026-02-09 (Quarterly)
- **Version History:**
  - v1.0.0 (2025-11-09): Initial consolidated architecture
