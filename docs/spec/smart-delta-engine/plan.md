# PLAN — Smart Delta Engine

## Overview

This plan outlines the implementation strategy for building the Smart Delta Engine, a system that maps enterprise SaaS capabilities to Odoo CE/OCA 18 with deterministic, machine-readable outputs.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Smart Delta Engine                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Docs Crawler │───▶│ Capability   │───▶│ Parity       │      │
│  │              │    │ Normalizer   │    │ Mapper       │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Raw Crawl    │    │ Capability   │    │ Parity Map   │      │
│  │ Output (JSON)│    │ Tree (JSON)  │    │ (YAML)       │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                 │               │
│                                                 ▼               │
│                                          ┌──────────────┐      │
│                                          │ Spec-Kit     │      │
│                                          │ Generator    │      │
│                                          └──────────────┘      │
│                                                 │               │
│                                                 ▼               │
│                                          ┌──────────────┐      │
│                                          │ constitution │      │
│                                          │ prd.md       │      │
│                                          │ plan.md      │      │
│                                          │ tasks.md     │      │
│                                          └──────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Models

### CapabilityNode

```yaml
CapabilityNode:
  id: string              # Stable hash-based ID
  name: string            # Human-readable name
  domain: enum            # Finance | PPM | HR | Ops | Analytics
  source_url: string      # Canonical URL
  source_hash: string     # Content hash for change detection
  parent_id: string?      # Parent capability (null for root)
  children: string[]      # Child capability IDs
  raw_content: string     # Extracted text content
  metadata:
    last_crawled: datetime
    version: string
```

### ParityMapping

```yaml
ParityMapping:
  capability_id: string           # Reference to CapabilityNode
  capability_name: string         # Denormalized for readability
  enterprise_refs: string[]       # Source doc references
  odoo_core: string[]             # Core module names
  oca_modules:
    - repo: string                # e.g., OCA/account-budgeting
      module: string              # e.g., account_budget
  alt_stack: string[]             # External components
  gap_level: int                  # 0-3
  smart_delta: enum               # Config | OCA | Custom | External
  implementation_notes: string[]  # Ordered steps
  validation:
    deterministic_hash: string
    last_validated: datetime
```

### OCAFeatureRequest

```yaml
OCAFeatureRequest:
  id: string
  title: string
  problem: string
  proposed_solution: string
  justification: string
  references: string[]
  gap_level: int
  preferred_resolution: string    # OCA | Custom
  status: enum                    # Draft | Submitted | Accepted | Rejected
  created_at: datetime
  submitted_at: datetime?
```

---

## Implementation Phases

### Phase 0: Foundation (Week 1)

**Objective**: Establish repo structure and guardrails

**Deliverables**:
- Repository structure with Spec-Kit
- CI pipeline for validation
- Schema definitions (JSON Schema)
- Smart Delta rule validator

**Acceptance Criteria**:
- [ ] CI blocks invalid parity mappings
- [ ] Schema validation passes for all artifacts
- [ ] Deterministic hash check implemented

---

### Phase 1: Docs Crawler (Week 2)

**Objective**: Build recursive documentation crawler

**Deliverables**:
- Recursive crawler with canonical URL handling
- Stable node ID generator (content hash based)
- Deduplication logic
- Raw output persistence (JSON)

**Acceptance Criteria**:
- [ ] Crawler handles SAP Help Portal structure
- [ ] Same content produces same node ID
- [ ] Duplicates are eliminated
- [ ] Output is valid JSON

---

### Phase 2: Capability Normalization (Week 3)

**Objective**: Map raw docs to normalized capabilities

**Deliverables**:
- Enterprise capability taxonomy definition
- Leaf page → capability mapper
- Domain tagging (Finance, PPM, HR, Ops, Analytics)

**Acceptance Criteria**:
- [ ] All leaf pages have capability assignment
- [ ] Taxonomy covers all supported domains
- [ ] Domain tags are consistent

---

### Phase 3: Parity Mapping Engine (Week 4-5)

**Objective**: Build the core parity mapping logic

**Deliverables**:
- Odoo core module resolver
- OCA module resolver (repo + module lookup)
- Alt-stack resolver (Supabase, n8n, etc.)
- Gap level calculator
- Smart Delta choice enforcer

**Acceptance Criteria**:
- [ ] Every capability resolves to at least one solution
- [ ] Gap levels are calculated correctly
- [ ] Smart Delta rules are enforced
- [ ] OCA references are validated

---

### Phase 4: Spec-Kit Generator (Week 6)

**Objective**: Auto-generate Spec-Kit artifacts

**Deliverables**:
- constitution.md generator
- prd.md generator
- plan.md generator
- tasks.md generator
- Machine-readability validator

**Acceptance Criteria**:
- [ ] Generated artifacts pass linting
- [ ] Artifacts are parseable by agents
- [ ] Output is deterministic

---

### Phase 5: Automation (Week 7)

**Objective**: Set up automated workflows

**Deliverables**:
- n8n scheduled crawl workflow
- Parity diff detection workflow
- OCA feature request auto-drafter
- Slack/Mattermost notification hooks

**Acceptance Criteria**:
- [ ] Crawl runs on schedule
- [ ] Diffs are detected and reported
- [ ] Feature requests are drafted correctly
- [ ] Notifications are sent

---

### Phase 6: CI/CD Hardening (Week 8)

**Objective**: Enforce all rules via CI/CD

**Deliverables**:
- Custom module rejection (gap < 2)
- OCA reference validation
- Deterministic output hash enforcement
- Full test coverage

**Acceptance Criteria**:
- [ ] Invalid PRs are blocked
- [ ] All rules have CI checks
- [ ] 100% test coverage on critical paths

---

## RLS (Row-Level Security) Strategy

For Supabase analytics layer (gap level 3 external):

```sql
-- Enable RLS on analytics tables
ALTER TABLE analytics.capability_coverage ENABLE ROW LEVEL SECURITY;

-- Policy: Users see only their tenant's data
CREATE POLICY "tenant_isolation" ON analytics.capability_coverage
  FOR ALL
  USING (tenant_id = current_setting('app.current_tenant')::uuid);

-- Policy: Read-only from Odoo replication
CREATE POLICY "read_only_replication" ON analytics.odoo_snapshot
  FOR SELECT
  USING (true);

-- No INSERT/UPDATE/DELETE allowed on replicated data
REVOKE INSERT, UPDATE, DELETE ON analytics.odoo_snapshot FROM PUBLIC;
```

---

## Dependencies

### External Services

| Service   | Purpose                      | Gap Level |
|-----------|------------------------------|-----------|
| Supabase  | Read-only analytics DB       | 3         |
| n8n       | Workflow automation          | 3         |
| Superset  | BI dashboards                | 3         |

### Odoo Modules (Core)

| Module    | Purpose                      |
|-----------|------------------------------|
| account   | Core accounting              |
| analytic  | Analytic accounting          |
| project   | Project management           |
| hr        | Human resources              |
| mail      | Messaging/chatter            |
| approval  | Approval workflows           |

### OCA Modules

| Repo                    | Module          | Purpose                    |
|-------------------------|-----------------|----------------------------|
| OCA/account-budgeting   | account_budget  | Budget management          |
| OCA/project             | project_budget  | Project budgets            |
| OCA/server-ux           | base_approval   | Multi-level approvals      |

---

## Risk Mitigation

| Risk                     | Mitigation                           | Owner     |
|--------------------------|--------------------------------------|-----------|
| Doc structure changes    | Hash-based change detection          | Crawler   |
| OCA module deprecation   | Quarterly OCA health check           | Parity    |
| Over-customization       | CI gates on gap level                | CI/CD     |
| Determinism failures     | Hash verification on every run       | CI/CD     |

---

## Success Metrics

| Metric                    | Target | Tracking                    |
|---------------------------|--------|-----------------------------|
| Capability coverage       | 100%   | Parity map completeness     |
| Config-only (gap 0)       | > 60%  | Gap level distribution      |
| OCA (gap 1)               | > 30%  | Gap level distribution      |
| Custom (gap 2)            | < 10%  | Gap level distribution      |
| External (gap 3)          | < 5%   | Gap level distribution      |
| CI pass rate              | > 95%  | CI metrics                  |
| Hash consistency          | 100%   | Determinism checks          |
