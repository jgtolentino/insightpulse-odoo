# SaaS Replication Playbook (Odoo CE + OCA + Custom Addons)

**Goal:** Systematically replicate SAP/SaaS app capabilities using Odoo Community + OCA modules + custom addons. This playbook gives you a repeatable, automation-first workflow: discovery → design → scaffold → build → integrate → test → deploy → observe.

---

## 0) Guiding Principles

* **80/20 Rule:** Prefer OCA modules for ~80% of needs; build the missing 20% as thin, well-tested custom addons.
* **API-first:** Document APIs early; treat external SaaS as first-class integrations.
* **Addons as units:** Each feature = one addon with its own tests, data, and docs.
* **Security & Compliance:** Enforce linting, licenses, and security scanning in CI.
* **Idempotence & Reproducibility:** Dockerized build; pinned Python/Odoo/OCA versions.
* **Observability:** Logs + metrics + traces; error budgets and SLOs for features.

---

## 1) Feature Analysis & OCA Mapping

Use this section to decompose the target SaaS/SAP domain into granular features and map to OCA.

### 1.1 Feature Inventory Template

```markdown
# Feature: <Name>
- Business goal:
- Actors & roles:
- Inputs:
- Outputs:
- KPIs/SLOs:
- Must-have vs Nice-to-have:

## Existing Odoo/OCA Coverage
- Candidate OCA repos: sale-workflow, account-financial-tools, hr, stock-logistics-*, server-tools, reporting-engine, queue, connector, vertical-*
- Known modules: <list>
- Gaps: <list>

## Data Contracts (ER model hints)
- Core models: <list>
- Relationships: <UML/ER hints>
- Constraints/invariants: <list>

## User Journeys
- Journey 1: <steps>
- Journey 2: <steps>

## Risks & Edge Cases
- Compliance, performance, data quality, migration, security
```

### 1.2 OCA Discovery (Automated)

* Use **`scripts/search-oca-modules.sh`** (below) to search across OCA repos by keyword and Odoo version.
* Export results to CSV and attach to the feature page.

---

## 2) Architecture & Design

### 2.1 Module Topology

* **Core** (domain models), **API** (controllers), **UI** (views/reports), **Integration** (connectors), **Ops** (monitoring hooks).
* Keep addons small and composable. Avoid cross-import cycles (only depend downward).

### 2.2 Data Modeling

* Normalize master data (partners, products, accounts, employees).
* Referential integrity in Python constraints + SQL constraints for invariants.
* Use **computed/stored fields** judiciously; prefer explicit writes in workflows.

### 2.3 API & Events

* REST endpoints under `/saas/<service>/<resource>` with token-based auth.
* Outgoing calls via `requests` with retries/backoff; enqueue with `queue_job` (OCA) for robust async.
* Domain events -> `bus`/`queue_job`/webhooks.

### 2.4 Non-Functional

* Performance: prefetch fields, batch writes, SQL indexes.
* Security: record rules, ACLs, OWASP input validation.
* Observability: structured logs, metrics (Prometheus), traces (OpenTelemetry exporters where relevant).

---

## 3) Automated Scaffolding (Addons & Files)

Use **`scripts/scaffold-odoo-module.sh`** to generate an OCA-compliant addon skeleton, including:

* `__manifest__.py` with metadata and dependencies
* `models/`, `views/`, `security/`, `data/`, `tests/`
* `README.rst`, `CHANGELOG.md`, `LICENSE`, badges
* CI hooks: `pre-commit`, `pylint-odoo`, `ruff` (optional), `black`

**Example:**

```bash
./scripts/scaffold-odoo-module.sh \
  --name expense_management \
  --summary "Unified expense submission and approvals" \
  --category "Human Resources" \
  --depends hr,account,mail \
  --models expense,expense_category,expense_report \
  --version 19.0 \
  --license LGPL-3 \
  --author "InsightPulse"
```

---

## 4) Development Workflow (TDD + OCA Standards)

1. **Create feature branch** from `main`.
2. **Generate addon** with scaffold script.
3. **Write tests first** (`tests/test_*.py`):

   * Business rules, workflows, access rules, API contracts.
4. **Implement models/views** incrementally; run tests locally in Docker.
5. **Lint & format**: `pre-commit run -a` enforces `pylint-odoo`, `black`, import order.
6. **Open PR**; CI runs: unit tests (with coverage ≥ 75%), XML/manifest lint, security scan, build image, run `odootest` matrix.
7. **Code review**: follow OCA guidelines on naming, manifests, dependencies.

**Coverage gate:** enforce 75% (config below). Exceptions require architectural justification.

---

## 5) Integration & Data Migration

### 5.1 Connectors

* Use **`component`** and **`connector`** OCA frameworks if doing complex sync.
* Model **binding records** for external IDs; queue jobs for push/pull; log job metadata.

### 5.2 Migration Plan Template

```markdown
# Migration <System → Odoo>
- Scope: objects, fields, volumes, historical depth
- Mapping tables: source → target
- Transform rules: Python functions with unit tests
- Loads: 1) master, 2) open txns, 3) histories (optional)
- Validation: count checks, hash totals, spot audits
- Cutover: blackout window, dry run → prod run, rollback plan
```

### 5.3 Validation Scripts

* CSV validators, referential checks, duplicate detection.
* Reconcile counts before/after; write fixtures for regression.

---

## 6) Testing, Deployment, Observability

### 6.1 Test Matrix

* **Unit tests (models, fields, constraints)** – ORM API, computed fields, onchange, SQL constraints.
* **Business workflow tests** – happy/edge paths, multi-step approvals, state transitions, accounting postings.
* **Security tests** – ACLs, record rules, sudo boundaries, group-based visibility; attempt privilege escalation and expect `AccessError`.
* **API contract tests** – controllers/routes, authentication, pagination, filtering, error payloads; schema-checked (OpenAPI) and backward-compat tests.
* **Integration tests** – external APIs with HTTP mocks (timeouts, 4xx/5xx, retries), queue jobs (`queue_job`) and idempotency.
* **Migration/data-load tests** – ETL transforms, referential integrity, deduplication, round-trip counts/hash totals.
* **Report/PDF tests** – wkhtmltopdf smoke (assets load, fonts glyphs), amounts/labels assertions.
* **Performance & scalability** – ORM batch ops, N+1 detection, heavy-report benchmarks, job queue throughput.
* **Concurrency & locking** – simulate parallel writes; verify transactional integrity and deadlock handling.
* **Multi-company/tenant isolation** – data leakage checks, cross-company rules, company-dependent fields.
* **I18n/L10n tests** – translations present, currency/rounding, timezone correctness.
* **Install/upgrade/uninstall** – module installability, `migrations/` pre/post scripts, upgrade path, uninstallation leaves DB clean.
* **Cron/mail/queue** – scheduled actions, mail gateways, bounce handling, retry/backoff semantics.
* **UI (Tours)** – headless browser tours for core flows, portal/mobile responsiveness smoke.
* **SRE/runbook tests** – health endpoints, readiness/liveness, backup/restore drill.

#### 6.1.A Sample pytest snippets

**Record rule should deny access to non-members**

```python
import pytest
from odoo.exceptions import AccessError

def test_record_rule_denies(env):
    Model = env["my_mod.secure_model"].with_user(env.ref("base.public_user"))
    rec = env["my_mod.secure_model"].create({"name": "X"})
    with pytest.raises(AccessError):
        Model.browse(rec.id).read(["name"])
```

**Workflow / posting assertions**

```python
def test_approval_flow(env):
    req = env["my_mod.request"].create({"name": "R1", "amount": 100})
    req.action_submit()
    assert req.state == "submitted"
    req.with_user(env.ref("my_mod.group_approver")).action_approve()
    assert req.state == "approved"
    move = req.account_move_id
    assert move.amount_total == 100
```

**API contract (JSON schema)**

```python
import jsonschema

def test_api_contract(http_client, token):
    res = http_client.get("/saas/service/items", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    schema = {"type": "object", "properties": {"data": {"type": "array"}}}
    jsonschema.validate(res.json(), schema)
```

**Idempotent queue job**

```python
def test_job_idempotent(env):
    job_model = env["queue.job"]
    payload = {"ext_id": "A1"}
    env["my_mod.job_service"].enqueue_sync(payload)  # creates record
    env["my_mod.job_service"].enqueue_sync(payload)  # should noop
    recs = env["my_mod.target"].search([("external_id", "=", "A1")])
    assert len(recs) == 1
```

**Concurrent write (advisory lock example)**

```python
from concurrent.futures import ThreadPoolExecutor

def test_concurrent_updates(env):
    rec = env["my_mod.counter"].create({"name": "C", "value": 0})
    def inc(uid):
        env_cr = env(cr=env.cr, uid=uid, context=dict(env.context))
        env_cr["my_mod.counter"].browse(rec.id).increment()
    users = [env.ref("base.user_admin").id, env.ref("base.user_root").id]
    with ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(inc, users))
    rec.refresh()
    assert rec.value == 2
```

#### 6.1.B Non-functional acceptance gates

* **P95 latency** for critical endpoints < *X* ms under *N* RPS.
* **Job success rate** ≥ 99.5% with retry policy proven.
* **PDF render success** ≥ 99.9% across top 5 templates.
* **Error budget** & alert thresholds defined per SLO.

#### 6.1.C Multi-tenant SaaS isolation checks

* Different companies cannot read/write each other's records.
* Cross-company many2one/many2many guarded by rules.
* Admin-only endpoints bypass isolation only with `sudo()` + audit log.

### 6.2 CI/CD (GitHub Actions example)

```yaml
name: odoo-ci
on:
  pull_request:
  push:
    branches: [ main ]
jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.10' }
      - name: Install system deps
        run: |
          sudo apt-get update
          sudo apt-get install -y libxml2-dev libxslt1-dev libpq-dev
      - name: Install python deps
        run: |
          python -m pip install --upgrade pip wheel
          pip install -r requirements.txt
      - name: Lint (pre-commit)
        run: |
          pip install pre-commit pylint-odoo black
          pre-commit install
          pre-commit run -a || (git diff && exit 1)
      - name: Tests
        env:
          ODOO_LOG_LEVEL: test
        run: |
          pip install coverage
          coverage run -m pytest -q
          coverage report --fail-under=75
      - name: Build Docker image
        run: |
          docker build -t ${{ github.repository }}:${{ github.sha }} .
```

### 6.3 Dockerfile (Debian trixie + wkhtmltopdf static)

```dockerfile
ARG DEBIAN_FRONTEND=noninteractive
FROM python:3.10-slim

# System deps & fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential git libxml2-dev libxslt1-dev libpq-dev \
    ca-certificates curl xz-utils fontconfig \
    libxrender1 libxext6 libx11-6 libxcb1 libx11-xcb1 libxcb-render0 libxcb-shm0 \
    libjpeg62-turbo libpng16-16 libfreetype6 xfonts-base xfonts-75dpi \
    fonts-dejavu fonts-liberation fonts-noto-cjk \
  && rm -rf /var/lib/apt/lists/*

# wkhtmltopdf 0.12.6 (Qt patched)
ARG WKHTML_VER=0.12.6-1
RUN curl -fsSL "https://github.com/wkhtmltopdf/packaging/releases/download/${WKHTML_VER}/wkhtmltox-${WKHTML_VER}.amd64.tar.xz" -o /tmp/wkhtmltox.tar.xz \
 && tar -xJf /tmp/wkhtmltox.tar.xz -C /tmp \
 && mv /tmp/wkhtmltox/bin/* /usr/local/bin/ \
 && rm -rf /tmp/wkhtmltox* /tmp/wkhtmltox.tar.xz \
 && wkhtmltopdf --version

# Odoo env
WORKDIR /opt/odoo
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["./entrypoint.sh"]
```

### 6.4 DigitalOcean App Platform / Droplet

* Build from Docker; enable **health checks** on `/web/health` (200 OK).
* Zero-downtime: blue/green via two apps behind Load Balancer or rolling deploy with readiness probe.
* Automated backups of Postgres; point-in-time if critical.

### 6.5 Observability

* **Prometheus** exporters for Postgres and Traefik; **Grafana** dashboards.
* **Loki** or **ELK** for logs; **Sentry** for Python exceptions (Odoo hook in `ir.logging`).

---

## 7) Security Hardening

* Least-privilege DB user; rotate DB/app secrets.
* Enforce HTTPS (HSTS), secure cookies, CSP for reports and portal.
* Validate all inbound payloads; rate-limit external APIs.
* Static analysis (`bandit`, `safety`/`pip-audit`), dependency pinning.
* Mandatory code owners for security-sensitive addons.

---

## 8) Rollback & Release Management

* **Semantic Versioning** per addon.
* Database migrations via `migrations/` with pre/post scripts.
* Rollback: revert image, restore DB snapshot, replay queues.
* Feature flags: gradual rollouts; dark launches for integrations.

---

## 9) Templates & Boilerplates

### 9.1 `__manifest__.py` template

```python
{
    "name": "<module_name>",
    "summary": "<one-line summary>",
    "version": "19.0.1.0.0",
    "author": "<Your Org>",
    "license": "LGPL-3",
    "website": "https://<your-site>",
    "category": "<Category>",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/<module_name>_menus.xml",
        "views/<module_name>_views.xml",
    ],
    "demo": [
        "demo/<module_name>_demo.xml"
    ],
    "installable": True,
    "application": False,
}
```

### 9.2 Pre-commit (OCA) minimal

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks: [{ id: black }]
  - repo: https://github.com/OCA/pylint-odoo
    rev: v9.0.0
    hooks: [{ id: pylint-odoo }]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
```

### 9.3 Coverage config (pytest + coverage)

```ini
# pyproject.toml or setup.cfg
[tool.pytest.ini_options]
addopts = "-q"

[tool.coverage.run]
source = ["addons", "odoo_addons"]
branch = true

[tool.coverage.report]
fail_under = 75
show_missing = true
```

### 9.4 Makefile helpers (optional)

```make
.PHONY: init lint test run shell
init:
	pre-commit install
lint:
	pre-commit run -a

test:
	coverage run -m pytest -q && coverage report --fail-under=75

run:
	docker compose up --build

shell:
	docker compose exec odoo bash
```

---

## 10) Automation Scripts

> Place these under `scripts/` and mark executable (`chmod +x`).

### 10.1 `scripts/scaffold-odoo-module.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# Defaults
ODOO_VERSION="19.0"
LICENSE="LGPL-3"
AUTHOR="Your Company"
CATEGORY="Tools"
SUMMARY=""
DEPENDS="base"
MODELS=""

usage() {
  cat <<EOF
Usage: $0 --name <module_name> [--version 19.0] [--license LGPL-3] \\
          [--author "Your Company"] [--category "Tools"] \\
          [--summary "One-liner"] [--depends a,b,c] [--models m1,m2]
EOF
}

# Parse args
NAME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME="$2"; shift 2;;
    --version) ODOO_VERSION="$2"; shift 2;;
    --license) LICENSE="$2"; shift 2;;
    --author) AUTHOR="$2"; shift 2;;
    --category) CATEGORY="$2"; shift 2;;
    --summary) SUMMARY="$2"; shift 2;;
    --depends) DEPENDS="$2"; shift 2;;
    --models) MODELS="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

[[ -z "$NAME" ]] && { echo "--name is required"; exit 1; }

MODULE_DIR="addons/${NAME}"
mkdir -p "$MODULE_DIR"/{models,views,security,data,demo,tests,migrations}

# __init__.py
cat > "$MODULE_DIR/__init__.py" <<PY
from . import models
PY

cat > "$MODULE_DIR/models/__init__.py" <<PY
# auto-generated
PY

# models
IFS=',' read -r -a MODEL_LIST <<< "${MODELS}"
for M in "${MODEL_LIST[@]}"; do
  [[ -z "$M" ]] && continue
  low="${M,,}"
  up="$(python3 - <<'PY'
import sys
s=sys.argv[1]
print(''.join([w.capitalize() for w in s.replace('_',' ').split()]))
PY
 "$M")"
  cat >> "$MODULE_DIR/models/__init__.py" <<PY
from . import ${low}
PY
  cat > "$MODULE_DIR/models/${low}.py" <<PY
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ${up}(models.Model):
    _name = "${NAME}.${low}"
    _description = "${up}"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    # TODO: add fields

    _sql_constraints = [
        ("name_unique", "unique(name)", "Name must be unique"),
    ]

    @api.constrains("name")
    def _check_name(self):
        for rec in self:
            if not rec.name:
                raise ValidationError(_("Name required"))
PY

  # Basic views per model
  cat >> "$MODULE_DIR/views/${NAME}_views.xml" <<XML
<!-- ${up} -->
<odoo>
  <record id="view_${low}_tree" model="ir.ui.view">
    <field name="name">${NAME}.${low}.tree</field>
    <field name="model">${NAME}.${low}</field>
    <field name="arch" type="xml">
      <tree>
        <field name="name"/>
        <field name="active"/>
      </tree>
    </field>
  </record>
  <record id="view_${low}_form" model="ir.ui.view">
    <field name="name">${NAME}.${low}.form</field>
    <field name="model">${NAME}.${low}</field>
    <field name="arch" type="xml">
      <form>
        <sheet>
          <group>
            <field name="name"/>
            <field name="active"/>
          </group>
        </sheet>
      </form>
    </field>
  </record>
  <record id="action_${low}" model="ir.actions.act_window">
    <field name="name">${up}</field>
    <field name="res_model">${NAME}.${low}</field>
    <field name="view_mode">tree,form</field>
  </record>
</odoo>
XML

  cat >> "$MODULE_DIR/views/${NAME}_menus.xml" <<XML
<odoo>
  <menuitem id="menu_${NAME}_root" name="${NAME^}"/>
  <menuitem id="menu_${low}" name="${up}" parent="menu_${NAME}_root" action="action_${low}"/>
</odoo>
XML

done

# access rules
cat > "$MODULE_DIR/security/ir.model.access.csv" <<CSV
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
# add groups as needed
CSV

# manifest - build depends array properly
DEPENDS_ARRAY=""
if [[ "$DEPENDS" == *","* ]]; then
  # Multiple dependencies
  IFS=',' read -r -a DEP_LIST <<< "$DEPENDS"
  DEPENDS_ARRAY="["
  for i in "${!DEP_LIST[@]}"; do
    DEPENDS_ARRAY+="\"${DEP_LIST[$i]}\""
    [[ $i -lt $((${#DEP_LIST[@]}-1)) ]] && DEPENDS_ARRAY+=", "
  done
  DEPENDS_ARRAY+="]"
else
  # Single dependency
  DEPENDS_ARRAY="[\"${DEPENDS}\"]"
fi

cat > "$MODULE_DIR/__manifest__.py" <<PY
{
    "name": "${NAME}",
    "summary": "${SUMMARY}",
    "version": "${ODOO_VERSION}.1.0.0",
    "author": "${AUTHOR}",
    "license": "${LICENSE}",
    "website": "",
    "category": "${CATEGORY}",
    "depends": ${DEPENDS_ARRAY},
    "data": [
        "security/ir.model.access.csv",
        "views/${NAME}_views.xml",
        "views/${NAME}_menus.xml"
    ],
    "demo": [
        "demo/${NAME}_demo.xml"
    ],
    "installable": True,
    "application": False
}
PY

# demo placeholder
cat > "$MODULE_DIR/demo/${NAME}_demo.xml" <<XML
<odoo>
  <!-- Demo data here -->
</odoo>
XML

# tests
cat > "$MODULE_DIR/tests/__init__.py" <<PY
# Test suite
PY

cat > "$MODULE_DIR/tests/test_${NAME}.py" <<PY
from odoo.tests.common import TransactionCase

class Test${NAME^}(TransactionCase):
    def setUp(self):
        super().setUp()
        # Setup test data

    def test_create_record(self):
        # Basic CRUD test placeholder
        record = self.env['${NAME}.${MODEL_LIST[0]:-model}'].create({
            'name': 'Test Record'
        })
        self.assertTrue(record)
        self.assertEqual(record.name, 'Test Record')
PY

# README
cat > "$MODULE_DIR/README.rst" <<RST
${NAME}
=====================

${SUMMARY}

* Version: ${ODOO_VERSION}
* License: ${LICENSE}
* Author: ${AUTHOR}

**Features**
- Scaffolding-generated module
- Add views, security, tests

**Installation**
- Add to addons path; update apps list; install.

**Usage**
- Navigate to menu '${NAME^}'.
RST

# Root-level quality configs (create if missing)
if [ ! -f .pre-commit-config.yaml ]; then
cat > .pre-commit-config.yaml <<YAML
repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
  - repo: https://github.com/OCA/pylint-odoo
    rev: v9.0.0
    hooks:
      - id: pylint-odoo
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
YAML
fi

printf "\n✅ Module scaffolded: %s\n" "$MODULE_DIR"
```

### 10.2 `scripts/search-oca-modules.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

FORMAT="table" # table|json|csv
VERSION="19.0"
KEYWORDS=""
TOKEN="${GITHUB_TOKEN:-}"

usage(){
  cat <<EOF
Usage: $0 --keywords "hr,expense,approval" [--version 19.0] [--format table|json|csv]
Env: GITHUB_TOKEN (optional, increases rate limits)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --keywords) KEYWORDS="$2"; shift 2;;
    --version) VERSION="$2"; shift 2;;
    --format) FORMAT="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

[[ -z "$KEYWORDS" ]] && { echo "--keywords required"; exit 1; }

OCA_REPOS=(
  account-financial-reporting account-financial-tools account-invoicing
  bank-payment connector hr l10n-spain l10n-brazil
  manufacturing mis-builder reporting-engine sale-workflow
  server-backend server-tools stock-logistics-workflow
)

hdr(){ echo "repo,module,name,summary,version,installable"; }
row(){ echo "$1,$2,$3,$4,$5,$6"; }

search_repo(){
  local repo="$1"
  local q
  q=$(printf "%s" "$KEYWORDS" | sed 's/,/|/g')
  local url="https://api.github.com/repos/OCA/${repo}/contents"
  local auth=()
  [[ -n "$TOKEN" ]] && auth=(-H "Authorization: Bearer $TOKEN") || auth=()
  # list top level dirs; filter addon dirs by manifest
  curl -sSL "${url}" "${auth[@]}" 2>/dev/null | jq -r \
    '.[] | select(.type=="dir") | .name' 2>/dev/null | while read -r addon; do
      [[ -z "$addon" ]] && continue
      murl="https://raw.githubusercontent.com/OCA/${repo}/${VERSION}/${addon}/__manifest__.py"
      man=$(curl -sSL "$murl" 2>/dev/null || true)
      [[ -z "$man" ]] && continue
      name=$(python3 - <<PY
import ast,sys
s=sys.stdin.read()
try:
 d=ast.literal_eval(s)
 print(d.get('name',''))
except Exception:
 pass
PY
 <<<"$man")
      summary=$(python3 - <<PY
import ast,sys
s=sys.stdin.read()
try:
 d=ast.literal_eval(s)
 print(d.get('summary','').replace(',', ';'))
except Exception:
 pass
PY
 <<<"$man")
      installable=$(python3 - <<PY
import ast,sys
s=sys.stdin.read()
try:
 d=ast.literal_eval(s)
 print(d.get('installable',True))
except Exception:
 print(True)
PY
 <<<"$man")
      if [[ "$name" =~ $(echo "$q") ]] || [[ "$summary" =~ $(echo "$q") ]]; then
        case "$FORMAT" in
          table) printf "%-28s %-32s %-40s %-6s %s\n" "$repo" "$addon" "$name" "$VERSION" "$summary";;
          csv) row "$repo" "$addon" "$name" "$summary" "$VERSION" "$installable";;
          json) jq -n --arg repo "$repo" --arg module "$addon" --arg name "$name" --arg summary "$summary" --arg version "$VERSION" --argjson installable "$installable" '{repo:$repo,module:$module,name:$name,summary:$summary,version:$version,installable:$installable}';;
        esac
      fi
    done
}

if [[ "$FORMAT" == "csv" ]]; then hdr; fi
for r in "${OCA_REPOS[@]}"; do
  search_repo "$r"
done
```

### 10.3 `scripts/README.md` (Suggested Outline)

```markdown
# scripts/

## scaffold-odoo-module.sh
- Generate OCA-compliant addon skeleton
- Usage examples (see playbook)

## search-oca-modules.sh
- Search OCA repos by keywords/version; outputs table/JSON/CSV
- Requires `jq`, `curl`, `python3`, and optional `GITHUB_TOKEN`

## Common prerequisites
- `jq`, `curl`, `python3`, `sed`, `awk`
- Run `chmod +x scripts/*.sh`
```

---

## 11) Quality Gates & Checklists

### 11.1 PR Checklist

* [ ] Manifest complete (summary, license, depends)
* [ ] Tests ≥ 75% coverage; new rules tested
* [ ] Security review (ACL, record rules, SQL injections)
* [ ] Docs updated (`README.rst`, usage, screenshots if UI)
* [ ] Changelog entry

### 11.2 Go-Live Checklist

* [ ] Migration dry-run validated; sign-off from business
* [ ] Monitoring dashboards ready; alerts configured
* [ ] Backups verified; PITR tested
* [ ] Rollback runbook validated
* [ ] Feature flags set for progressive rollout

---

## 12) Example Replication Paths

* **SuccessFactors → Odoo HR**: OCA `hr`, `hr-expense`, custom approval flows, SSO via OAuth.
* **SAP SD → Odoo Sales**: `sale-workflow`, custom pricing engines, EDI connectors.
* **SAP FI → Odoo Accounting**: `account-*` OCA, advanced reporting via `mis-builder`.

---

## 13) Next Steps

1. Run `search-oca-modules.sh` for your target SaaS domain keywords.
2. For each feature page, mark **Covered** / **Extend** / **Build**.
3. Scaffold first addon and push a PR with tests + CI.
4. Establish a fortnightly release train and keep the SLO dashboard visible.

---

## 14) Trusted AI with Docker + E2B (Agents, MCP, Model Runner)

**Objective:** Let agents assist (code changes, docs, data tasks) without ever granting them direct access to prod infra. All agent actions run in **isolated sandboxes**, use **curated tools via MCP Gateway**, and are gated by CI before merge/deploy.

### 14.1 Reference Architecture

* **Local Dev:** `docker compose` profile `ai` spins up `mcp-gateway`, `model-runner`, and your `agent` sidecar next to `odoo`/`postgres`.
* **CI:** Agent proposals arrive as PRs. CI enforces tests, coverage, lint, SBOM + vuln scan. No direct pushes.
* **Prod:** Agents live as separate services; any code execution happens in **E2B sandboxes** with read-only FS, network allowlists, short-lived creds. Odoo remains a stable app service.

### 14.2 Compose (AI profile)

Create `docker-compose.ai.yaml` and activate with `--profile ai`.

```yaml
services:
  mcp-gateway:
    image: <mcp-gateway-image>
    profiles: ["ai"]
    environment:
      MCP_ALLOWLIST: github,http,web-browsing
      MCP_CATALOG_URL: https://<your-org>/mcp-allowlist.json
      LOG_LEVEL: info
    ports: ["8089:8080"]

  model-runner:
    image: <model-runner-image>
    profiles: ["ai"]
    environment:
      MODEL_BACKENDS: openai:gpt-4o-mini,ollama:llama3
      # Provide keys via secrets manager or env
    depends_on: [mcp-gateway]

  agent:
    build: ./ai/agent
    profiles: ["ai"]
    environment:
      E2B_API_KEY: ${E2B_API_KEY}
      E2B_POLICY: /policy/policy.yaml
      MCP_SERVER_URL: http://mcp-gateway:8080
      MODEL_RUNNER_URL: http://model-runner:8080
    volumes:
      - ./ai/policy:/policy:ro
    depends_on: [model-runner]
```

### 14.3 MCP Gateway Allowlist

Only expose vetted tools to agents. Host this JSON and point `MCP_CATALOG_URL` to it.

```json
{
  "allow": [
    {"tool": "github", "version": ">=1.0.0"},
    {"tool": "http",   "version": ">=1.0.0"},
    {"tool": "browser", "version": ">=1.0.0"}
  ],
  "deny": [
    {"tool": "shell",   "reason": "No raw shell for agents"},
    {"tool": "ssh",     "reason": "Disallowed"}
  ]
}
```

### 14.4 E2B Sandbox Policy (example)

Keep execution locked down; only whitelisted egress and paths.

```yaml
fs:
  readOnly: true
  allowedPaths: ["/workspace", "/tmp"]
net:
  denyPrivateCIDRs: true
  allow:
    - "https://api.github.com"
    - "https://<your-api>"
secrets:
  mount: false
  envAllowlist: ["TOKEN_READONLY_*"]
timeout: 120s
cpu: "1"
memory: "1Gi"
```

### 14.5 Agent → PR Workflow (Guardrails)

1. Agent runs in E2B sandbox and calls MCP tools only.
2. Changes are sent as **PRs** with a run summary and sandbox run ID.
3. **Required checks** (branch protection):

   * Unit/Integration tests (≥75% coverage)
   * Lint (pylint-odoo, black), XML/manifest validations
   * SBOM + Vulnerability scan (block on High/Critical)
   * Policy: modified files under `addons/` must have matching tests

**GitHub Actions job (snippet):**

```yaml
jobs:
  ai-policy-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with: { path: '.', output-file: 'sbom.spdx.json' }
      - name: Vulnerability scan
        run: |
          pip install pip-audit
          pip-audit --strict
      - name: Verify tests changed with code
        run: |
          git diff --name-only origin/main...HEAD | grep '^addons/.\+\.py' && \
          git diff --name-only origin/main...HEAD | grep '^addons/.\+tests/.\+\.py' || \
          (echo 'Code changed without tests' && exit 1)
```

### 14.6 Observability & Audit

* Log every agent action with a correlation ID and sandbox run ID; ship to Loki/ELK.

```json
{ "ts": "2025-10-31T05:20:11Z", "agent_id": "ai-bot-1", "sandbox_run": "e2b_abc123", "tool": "github.pulls.create", "odoo_model": "saas.request", "res_id": 123, "result": "success", "latency_ms": 842 }
```

* Odoo linkage: add `sandbox_run_id` + `agent_id` fields on the job/request models; expose in chatter for traceability.
* Metrics: job success rate, tool error rates, P95 agent response latency.

### 14.7 Security Posture

* No prod secrets in agent containers; use read-only, least-privilege tokens.
* Deny private CIDRs; allow only needed public endpoints.
* Sign images; pin base images; block deploy on critical CVEs.
* Periodic red-team: try to exfiltrate secrets or bypass MCP allowlist as regression tests.

### 14.8 Developer UX

* `make ai-up` → brings up AI profile; `make ai-down` → stops it.
* Local model via Model Runner or point to your provider; switch with env.
* Scaffolder can generate an **agent stub** (`ai/agent/`) wired to MCP & E2B (optional enhancement).

### 14.9 Adding a New Tool (Runbook)

1. Propose tool in MCP allowlist PR with risk notes.
2. Add egress to E2B policy (if needed) and update tests.
3. Dry-run locally (`--profile ai`), then merge allowlist.
4. Observe agent runs; roll back by removing tool from allowlist if anomalies arise.

---

*Maintainers: keep this playbook in the repo root as `SAAS_REPLICATION_PLAYBOOK.md` and evolve per project retrospectives.*
