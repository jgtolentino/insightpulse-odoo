# Optimization Plan: Google Antigravity for Odoo CE

## Goal
Configure the Agent ("Antigravity") to autonomously enforce project standards and automate complex Odoo workflows, reducing user cognitive load and typing.

## Proposed Configuration

### 1. Project Rules (`.agent/rules.md`)
**Purpose:** Enforce the "IPAI Standard" and "No-Enterprise" policy at the system level.
**Content:**
- **Role:** Odoo 18 CE Expert (from `odoo_ce_expert_prompt.md`).
- **Constraints:**
    - NO Enterprise modules.
    - NO `x_` prefixes.
    - ALWAYS check OCA first.
    - ALWAYS use `ipai_` prefix for custom modules.
- **Style:** OWL 2.0, Python 3.10+, AGPL-3.

### 2. Workflows (`.agent/workflows/*.md`)
**Purpose:** Turn complex multi-step CLI commands into simple natural language requests.

#### A. Deploy & Update (`deploy.md`)
- **Trigger:** "Deploy", "Update modules"
- **Steps:**
    1.  Restart Odoo container.
    2.  Run `odoo -u ...` for all `ipai_*` modules.
    3.  Check logs for errors.

#### B. Scaffold New Module (`scaffold.md`)
- **Trigger:** "Create module X", "Scaffold X"
- **Steps:**
    1.  Create directory structure (`models`, `views`, `security`).
    2.  Generate compliant `__manifest__.py` (Author: InsightPulseAI).
    3.  Generate `__init__.py` files.
    4.  Add to `.gitignore` (if needed).

#### C. Run Tests (`test.md`)
- **Trigger:** "Test module X", "Run tests"
- **Steps:**
    1.  Run `odoo-bin --test-enable --stop-after-init -u <module>`.

### 3. Context Optimization
- **`.agentignore`**: Ensure `logs/`, `filestore/`, and `tmp/` are ignored to keep context window clean.

## Execution Steps
1.  Create `.agent` directory.
2.  Create `.agent/rules.md` with the content from `odoo_ce_expert_prompt.md` + `TBWA_IPAI_MODULE_STANDARD.md`.
3.  Create `.agent/workflows/deploy.md`.
4.  Create `.agent/workflows/scaffold.md`.
