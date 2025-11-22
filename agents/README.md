# InsightPulse AI - Agent Skills Architecture

**Version:** 1.0.0
**Created:** 2025-11-22
**Purpose:** Transform the InsightPulse Odoo CE stack into autonomous agent capabilities

---

## 🎯 What Is This?

This directory contains the **Agent Skills Architecture** - a framework that converts your Odoo CE + Supabase + n8n stack into **repeatable, autonomous agent capabilities**.

### The Core Concept

Instead of manually performing tasks over and over, we map them into:

- **Skills** → What agents can do (atomic actions)
- **Capabilities** → Composite workflows (multiple skills)
- **Knowledge** → Patterns, docs, best practices
- **Procedures** → Step-by-step execution playbooks

**Result:** Agents inherit knowledge and capabilities, building **compound intelligence** over time.

---

## 📁 Directory Structure

```
agents/
├── README.md                           # This file
├── ORCHESTRATOR.md                     # Master orchestration guide
├── AGENT_SKILLS_REGISTRY.yaml          # Skill & capability definitions
├── PRIORITIZED_ROADMAP.md              # Execution roadmap
├── capabilities/
│   └── CAPABILITY_MATRIX.yaml          # Composite workflows
├── knowledge/
│   └── KNOWLEDGE_BASE_INDEX.yaml       # Patterns, docs, references
├── procedures/
│   └── EXECUTION_PROCEDURES.yaml       # Step-by-step playbooks
└── skills/
    └── (Future: individual skill definitions)
```

---

## 📚 Core Documents

### 1. **ORCHESTRATOR.md** - Start Here
**Purpose:** Master guide for AI agents operating the platform

**What's inside:**
- Agent identity and principles
- How to execute tasks
- Skill execution patterns
- Error handling
- Quality standards

**When to use:** Every time you start working as an agent on this platform

---

### 2. **AGENT_SKILLS_REGISTRY.yaml** - What You Can Do
**Purpose:** Complete map of skills, capabilities, and knowledge sources

**What's inside:**
- **15+ atomic skills** (scaffold_odoo_module, test_ocr_quality, create_n8n_workflow, etc.)
- **6+ capabilities** (build_enterprise_module, improve_ocr_quality, automate_finance_closing, etc.)
- **5+ procedures** (build_new_feature, investigate_production_issue, etc.)
- **Execution rules** (CE/OCA compliance, quality standards, etc.)

**When to use:** When starting any task - find the right skill or capability

---

### 3. **CAPABILITY_MATRIX.yaml** - Composite Workflows
**Purpose:** Define complex workflows with preconditions and execution flows

**What's inside:**
- **Preconditions** (what must be true before execution)
- **Execution flows** (step-by-step with inputs/outputs)
- **Success criteria** (how to validate completion)
- **Validation templates** (CE/OCA compliance, OCR quality, deployment health)

**When to use:** When task requires multiple skills orchestrated together

---

### 4. **KNOWLEDGE_BASE_INDEX.yaml** - Where to Find Answers
**Purpose:** Map all documentation, patterns, and best practices

**What's inside:**
- **Documentation sources** (README, specs, PRDs, guides)
- **Code patterns** (Odoo manifest, OCR normalization, n8n workflows, Supabase RLS)
- **Best practices** (by domain: Odoo, OCR, n8n, security, deployment)
- **Troubleshooting guides** (common issues + solutions)
- **External references** (Odoo docs, OCA guidelines, Supabase docs, n8n docs)

**When to use:** Before starting work, to find existing patterns and avoid reinventing

---

### 5. **EXECUTION_PROCEDURES.yaml** - Step-by-Step Playbooks
**Purpose:** Detailed playbooks for common agent tasks

**What's inside:**
- **build_new_feature** (requirement → deploy)
- **investigate_production_issue** (debug → fix → validate)
- **improve_ocr_quality** (analyze → normalize → test → deploy)
- **onboard_new_n8n_automation** (spec → create → deploy)
- **deploy_to_digitalocean** (provision → deploy → validate)
- **Decision trees** (which skill to use, which deployment method)
- **Validation checklists** (before/after deployment, CE/OCA compliance)
- **Rollback procedures** (when things go wrong)

**When to use:** When executing a well-defined task type

---

### 6. **PRIORITIZED_ROADMAP.md** - What to Build Next
**Purpose:** 7-phase roadmap to full autonomy

**What's inside:**
- **Current state assessment** (what's working, what's partial, what's missing)
- **7 execution phases** (Foundation → n8n → MCP → OCR → Mobile → K8s → Mattermost → Superset)
- **Quick wins** (can do immediately)
- **Success metrics** (automation coverage, OCR quality, productivity)
- **Next 3 actions** (do today)

**When to use:** Weekly planning, understanding priorities

---

## 🚀 How to Use This Framework

### As a Human Developer

1. **Read `ORCHESTRATOR.md`** to understand the agent's operating model
2. **Check `PRIORITIZED_ROADMAP.md`** to see what phase you're in
3. **Use `AGENT_SKILLS_REGISTRY.yaml`** to find the right capability for your task
4. **Follow `EXECUTION_PROCEDURES.yaml`** for step-by-step guidance
5. **Reference `KNOWLEDGE_BASE_INDEX.yaml`** for patterns and docs

### As an AI Agent

1. **Load `ORCHESTRATOR.md`** as your core operating system
2. **For each task:**
   - Classify task type
   - Look up capability in `AGENT_SKILLS_REGISTRY.yaml`
   - Follow procedure from `EXECUTION_PROCEDURES.yaml`
   - Reference patterns from `KNOWLEDGE_BASE_INDEX.yaml`
   - Validate using criteria from `CAPABILITY_MATRIX.yaml`
3. **After completion:**
   - Update knowledge base if new learning
   - Report to user with clear summary

### As Claude Code CLI

When running in Claude Code CLI:

```bash
cd /home/user/odoo-ce

# Start Claude Code
claude

# In Claude Code session:
> I need you to act as the InsightPulse Platform Orchestrator.
> Read agents/ORCHESTRATOR.md and use the agent skills framework.
> Help me [specific task].
```

---

## 🎯 Quick Start Examples

### Example 1: Deploy a Module

**User request:** "Deploy the ipai_expense module to production"

**Agent execution:**
1. Look up capability: `cap_odoo_supabase_module`
2. Follow procedure: `build_new_feature` → deployment phase
3. Use skill: `deploy_odoo_module`
4. Validate: CI checks, health endpoint, no errors
5. Report: Deployment summary

### Example 2: Improve OCR Quality

**User request:** "OCR is failing for SM receipts, fix it"

**Agent execution:**
1. Look up capability: `cap_improve_ocr_quality`
2. Follow procedure: `improve_ocr_quality`
3. Use skills:
   - `analyze_odoo_logs` → identify failing vendors
   - `add_ocr_normalization` → add SM variants
   - `test_ocr_quality` → validate improvement
4. Deploy adapter update
5. Monitor for regressions

### Example 3: Create n8n Workflow

**User request:** "Automate BIR deadline alerts"

**Agent execution:**
1. Look up capability: `cap_n8n_finance_automation`
2. Follow procedure: `onboard_new_n8n_automation`
3. Use skills:
   - `create_n8n_workflow` → W002_OD_BIR_ALERTS.json
   - `deploy_n8n_workflow` → import to n8n
4. Validate: dry run successful
5. Register in workflows/index.yaml

---

## 🔧 Extending the Framework

### Adding a New Skill

**File:** `AGENT_SKILLS_REGISTRY.yaml`

```yaml
skills:
  - id: your_new_skill
    name: "Your New Skill"
    domain: odoo_ce | supabase | n8n | ocr_ml | deployment | finance_ops
    description: "What this skill does"
    inputs:
      - input1
      - input2
    outputs:
      - output1
    tools:
      - tool1
      - tool2
    knowledge_refs:
      - relevant_knowledge_id
```

### Adding a New Capability

**File:** `capabilities/CAPABILITY_MATRIX.yaml`

```yaml
capabilities:
  - name: "Your Capability Name"
    id: cap_your_capability
    description: "What this capability achieves"
    preconditions:
      - condition1
      - condition2
    skills_required:
      - skill1
      - skill2
    execution_flow:
      - step: 1
        action: "skill1"
        inputs: [...]
        outputs: [...]
    success_criteria:
      - criterion1
      - criterion2
```

### Adding a New Procedure

**File:** `procedures/EXECUTION_PROCEDURES.yaml`

```yaml
procedures:
  your_procedure:
    description: "What this procedure accomplishes"
    category: development | troubleshooting | quality_improvement | automation | infrastructure
    estimated_duration: "X hours"
    steps:
      - step: 1
        phase: "Phase Name"
        actions:
          - "Action 1"
          - "Action 2"
    success_criteria:
      - "Criterion 1"
```

### Adding to Knowledge Base

**File:** `knowledge/KNOWLEDGE_BASE_INDEX.yaml`

```yaml
documentation:
  - id: your_doc_id
    title: "Document Title"
    path: "/path/to/doc.md"
    domain: odoo_development | ocr_quality | automation | infrastructure | finance_operations
    type: overview | specification | runbook | howto | standards
    topics:
      - "Topic 1"
      - "Topic 2"
    agent_use: "When to reference this doc"

code_patterns:
  - id: your_pattern_id
    title: "Pattern Name"
    domain: odoo_development | ocr_quality | automation | security_compliance
    pattern: |
      # Your code pattern here
    agent_use: "When to use this pattern"

best_practices:
  domain_name:
    - "Practice 1"
    - "Practice 2"
```

---

## 📊 Success Metrics

### Platform Maturity

After 6 months, target:
- **Automation Coverage:** 80%+ (from 20%)
- **OCR Success Rate:** 90%+ (from 85%)
- **Deployed Workflows:** 20+ (from 2)
- **Agent Skills:** 50+ (from 15)
- **MCP Servers:** 3+ (from 0)

### Developer Productivity

- **Module Deployment Time:** 5 min (from 15 min)
- **OCR Quality Iteration:** 30 min (from 2 hours)
- **n8n Workflow Creation:** 15 min (from 1 hour)
- **Issue Resolution:** 30 min (from 2 hours)

---

## 🤝 Contributing

**When you use the agent framework:**

1. **Document learnings** - Update knowledge base after solving new problems
2. **Add patterns** - Extract reusable patterns from your work
3. **Improve procedures** - Suggest better workflows
4. **Expand skills** - Add new capabilities as needed

**Pull requests welcome for:**
- New skills or capabilities
- Improved procedures
- Additional knowledge base entries
- Better patterns or best practices

---

## 📞 Support

**Questions?**
- Check `KNOWLEDGE_BASE_INDEX.yaml` first
- Review troubleshooting guides
- Ask in project issues

**Bugs or improvements?**
- Update the relevant YAML file
- Document in git commit
- Share learnings

---

## 🌟 Why This Matters

**Traditional approach:**
- Manual work repeated infinitely
- Knowledge locked in people's heads
- No inheritance of expertise
- Each problem solved from scratch

**Agent Skills approach:**
- Work automated once → reusable forever
- Knowledge operationalized in code
- System-wide capability propagation
- Compound intelligence over time

**This is how you build a self-improving platform.**

---

**Status:** Phase 0 (Foundation) - Active
**Next Review:** 2025-12-06
**Owner:** InsightPulseAI Platform Team

---

🤖 **Ready to build autonomous capabilities. Let's transform manual work into agent intelligence.**
