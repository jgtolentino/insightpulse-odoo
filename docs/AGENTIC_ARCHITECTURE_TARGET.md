# InsightPulse Odoo – Agentic Target Architecture

> This document describes the **Target State** architecture for `insightpulse-odoo`:
> a production-grade, agentic Finance Shared Service Center (SSC) built on
> Odoo 19 CE + OCA modules + custom automation, with strong DevOps, IaC, and AI.

Items are labeled as:

- **(Existing)** – inferred from current repo / deployment.
- **(Proposed)** – required to reach Level 4/5 agentic maturity (AI-assisted with strong automation and guardrails).

---

## 1. Target Project Structure (Top-Level Tree)

```text
insightpulse-odoo/
├── .github/
│   └── workflows/
│       ├── continuous-integration.yml      (Existing: CI/CD automation)
│       └── production-deployment.yml       (Proposed: CI/CD with security/rollback)
│
├── agents/                                 (Proposed: Autonomous Agent Runtime)
│   ├── __init__.py
│   ├── base_agent.py                       (Proposed: AgentState, BaseAgent, MemoryEnhancedAgent)
│   ├── bir_compliance_agent.py             (Proposed: Handles BIR forms 1601-C, 2550Q)
│   ├── reconciliation_agent.py             (Proposed: Bank/GL reconciliation with ML matching)
│   ├── expense_validation_agent.py         (Proposed: Policy check, fraud detection)
│   ├── ocr_extraction_agent.py             (Proposed: PaddleOCR wrapper for documents)
│   ├── financial_reporting_agent.py        (Proposed: Generates P&L, BS, CF)
│   └── memory_enhanced_agent.py            (Proposed: Optional shim if separate from base_agent)
│
├── workflows/                              (Proposed: Multi-Agent Orchestration)
│   ├── __init__.py
│   ├── orchestrator.py                     (Proposed: AgentOrchestrator class, routing patterns)
│   ├── month_end_close_orchestrator.py     (Proposed: Level 4 autonomous workflow, HITL-approved)
│   ├── bir_compliance_orchestrator.py      (Proposed: Manages all tax filing deadlines & tasks)
│   └── expense_approval_workflow.py        (Proposed: Sequential/Handoff pattern for approvals)
│
├── memory/                                 (Proposed: Vector, Graph, Context Layer)
│   ├── __init__.py
│   ├── vector_store.py                     (Proposed: AgentMemory class, Qdrant/pgvector integration)
│   ├── knowledge_graph.py                  (Proposed: COA hierarchy, policy graph)
│   └── hybrid_knowledge_base.py            (Proposed: Combines Vector, Graph, and SQL access)
│
├── automation/                             (Proposed: Intelligent Automation Engine)
│   ├── workflow_engine.py                  (Proposed: Intelligent retries, rollback, state persistence)
│   ├── cron_jobs.py                        (Proposed: P0/P1 scheduled tasks: backup, SSL renewal, DB optimize)
│   └── self_healing.py                     (Proposed: Auto-cleanup, memory leak detection, restart logic)
│
├── rpa/                                    (Proposed: Robotic Process Automation Layer)
│   ├── __init__.py
│   └── bir_portal_automation.py            (Proposed: Playwright bot for BIR eServices portal)
│
├── terraform/                              (Proposed: Infrastructure as Code - IaC)
│   ├── main.tf                             (Proposed: Load balancer, VPC, droplets, DBs)
│   ├── variables.tf                        (Proposed: Environment variables and types)
│   ├── outputs.tf                          (Proposed: IP addresses, DB hosts, LB endpoints)
│   ├── cloud-init.yml                      (Proposed: Droplet bootstrapping script)
│   └── minimum_viable.tf                   (Proposed: Minimal IaC to stand up staging)
│
├── ansible/                                (Proposed: Configuration Management)
│   ├── playbook.yml                        (Proposed: Global entrypoint)
│   └── inventory/
│       ├── hosts.ini
│       └── playbooks/
│           ├── odoo.yml                    (Proposed: Odoo server configuration)
│           └── monitoring.yml              (Proposed: Prometheus/Grafana/Alertmanager config)
│
├── monitoring/                             (Proposed: Observability Stack)
│   ├── prometheus.yml                      (Proposed: Scrape configs for agents, Odoo, Postgres, OCR)
│   ├── alerts.yml                          (Proposed: P0/P1 alerts for Alertmanager)
│   ├── grafana_dashboards/
│   │   ├── overview.json                   (Proposed: System Status, Error Rate, Latency)
│   │   └── agents.json                     (Proposed: Agent Cost, Confidence, Latency)
│   └── agent_telemetry.py                  (Proposed: Prometheus metrics for agents)
│
├── tests/
│   ├── unit/                               (Existing: Unit tests for business logic)
│   ├── integration/                        (Proposed: Tests for Agent ↔ MCP ↔ Odoo flows)
│   ├── performance/                        (Proposed: Load tests, e.g., k6 / locust harnesses)
│   └── minimum_test_suite.py               (Proposed: Smoke tests — login, basic agent run)
│
├── docs/
│   ├── AGENT.md                            (Existing: Agent definition/usage patterns)
│   ├── SKILLS.md                           (Existing: Skills/capabilities definitions)
│   ├── KNOWLEDGE.md                        (Existing: Knowledge and RAG definitions)
│   ├── AGENTIC_ARCHITECTURE.md             (Proposed: This file)
│   └── DISASTER_RECOVERY.md                (Proposed: Backup, restore, failover procedures)
│
├── datasets/                               (Proposed: Training/Evaluation Data)
│   ├── bir_regulations/                    (Proposed: Source docs for RAG)
│   ├── golden_prompts.yml                  (Proposed: Agent evaluation suite)
│   └── reconciliation_data/                (Proposed: Data for ML matching / eval)
│
├── odoo/                                   (Existing: Odoo application core)
│   ├── custom_addons/                      (Existing: Custom modules)
│   ├── vendor_oca/                         (Existing: Vendored OCA modules)
│   └── odoo_config/                        (Existing: Nginx/SSL configuration, env templates)
│
├── scripts/
│   ├── appsrc.py                           (Existing: Custom module building script)
│   └── vendor_oca.py                       (Existing: OCA module management/vendoring)
│
├── docker-compose.yml                      (Existing: Odoo, Postgres, Superset, etc.)
├── Dockerfile                              (Existing: Odoo application image)
├── requirements.txt                        (Existing: Python dependencies)
└── README.md                               (Existing: Project overview)
```

## 2. Conceptual Layers

### 2.1 Agent Runtime (agents/)

**Purpose:** Encapsulate domain-specific autonomy:

- BIR compliance (1601-C, 2550Q, etc.).
- Bank/GL reconciliation.
- Expense validation and fraud detection.
- OCR extraction and financial reporting.

**Contract:** All agents inherit from BaseAgent (see agents/base_agent.py) and receive:

- A shared AgentState (context, environment, run metadata).
- Optional AgentMemory access for RAG (via memory/).
- Tooling to log telemetry to monitoring/agent_telemetry.py.

### 2.2 Orchestration (workflows/)

**Purpose:** Compose agents into end-to-end flows:

- Month-end close (Level 4: highly automated, human approval gates).
- BIR filing schedule orchestration.
- Expense approval flow across teams.

**Contract:**

- AgentOrchestrator orchestrates stateful runs, steps, approvals.
- Orchestrators do not embed business rules directly; they delegate to agents and memory/.

### 2.3 Memory & Knowledge (memory/ + datasets/)

**Purpose:** Provide consistent, testable knowledge:

- Vector RAG over datasets (BIR regulations, SOPs, policies).
- Knowledge graph for Chart of Accounts, entities, and rules.
- Hybrid access to SQL (Odoo DB, analytics DB) when needed.

**Contract:**

- AgentMemory in vector_store.py is the primary interface.
- Agents never query raw DBs directly; they call memory or explicit data access helpers.
- datasets/ is the canonical source of truth for training and evaluation data.

### 2.4 Automation & RPA (automation/ + rpa/)

**automation/** – Python-driven automation:

- Workflow engine with retries, idempotency, and rollback.
- Cron-like scheduling for backups, SSL renewal, and maintenance.
- Self-healing scripts that restart services or clean up resources.

**rpa/** – Browser-level / portal-level automation:

- BIR portal automation (Playwright) to submit forms using agent-prepared payloads.
- RPA actions always triggered via orchestrators; never free-floating.

### 2.5 Infra & Observability (terraform/, ansible/, monitoring/)

**Terraform:**

- Declarative provisioning of droplets, DBs, networking.
- minimum_viable.tf stands up a minimal staging environment.

**Ansible:**

- Idempotent configuration for Odoo servers and observability stack.

**Monitoring:**

- Prometheus + Alertmanager + Grafana dashboards.
- Agent-specific dashboards (cost, token usage, latency, error rates).

### 2.6 Testing & Docs (tests/, docs/)

**Tests:**

- unit/ – logic inside agents, memory, and automation.
- integration/ – agent ↔ Odoo ↔ DB ↔ RPA flows.
- performance/ – load tests for month-end and BIR spikes.
- minimum_test_suite.py – smoke tests to gate deploys.

**Docs:**

- AGENT.md – how to write/extend agents.
- SKILLS.md – list of capabilities and prerequisites.
- KNOWLEDGE.md – what the system "knows" and where it lives.
- AGENTIC_ARCHITECTURE.md – this architecture overview.
- DISASTER_RECOVERY.md – backup/restore/failover runbooks.

## 3. Autonomy & Guardrails

We explicitly target:

- **Level 4 Agentic Maturity** (high automation with human approvals).
- Optional selective Level 5 behavior only for low-risk, reversible operations.

**Guardrails:**

Agents never directly:

- Post irreversible accounting entries.
- File official BIR returns.
- Change roles, permissions, or infra.

High-risk operations always:

- Produce a plan and diff.
- Require human approval (with clear logs and links).
- Are executed via audited backends (Odoo APIs, RPA, IaC).

## 4. Implementation Order (High-Level)

1. **Create backbone modules:**
   - agents/base_agent.py
   - workflows/orchestrator.py
   - memory/vector_store.py

2. **Wire at least one real use case:**
   - reconciliation_agent.py + month_end_close_orchestrator.py with HITL.

3. **Add BIR-specific agents and RPA:**
   - bir_compliance_agent.py + bir_portal_automation.py.

4. **Flesh out IaC and observability:**
   - Minimal Terraform (staging), Prometheus scraping, Grafana dashboards.

5. **Gradually bring more existing automation under this unified structure.**
