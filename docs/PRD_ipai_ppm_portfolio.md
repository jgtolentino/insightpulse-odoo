# Product Requirements Document: ipai_ppm_portfolio

**Module**: ipai_ppm_portfolio
**Version**: 1.0.0
**Status**: Draft
**Author**: Agent Skills Architecture / Odoo Reverse Mapper
**Created**: 2025-11-23
**SaaS Equivalent**: Clarity PPM – Portfolio & Project Management

---

## 1. Problem Statement

### Current State

Organizations using Odoo CE 18 have excellent **project** management capabilities (`project.project`, `project.task`) but **lack enterprise-grade portfolio management**:

- **No Portfolio → Program → Project hierarchy** for organizing related initiatives
- **No strategic prioritization** with weighted scoring models
- **No resource capacity planning** across the portfolio
- **No stage-gate governance** for investment decisions
- **No consolidated reporting** at portfolio/program levels

### Pain Points

1. **Flat Project Structure**: All projects treated equally regardless of strategic importance
2. **Resource Blindness**: No visibility into capacity constraints and allocation conflicts
3. **Governance Gap**: No structured decision points (gates) for approving/canceling initiatives
4. **Reporting Silos**: Manual aggregation required for executive dashboards

### Target Users

- **Portfolio Managers**: Oversee multiple programs and ensure strategic alignment
- **Program Managers**: Coordinate related projects and manage dependencies
- **Resource Managers**: Allocate talent across initiatives based on skills and availability
- **Executives**: Review portfolio performance and approve stage-gate decisions

---

## 2. Goals and Non-Goals

### Goals

✅ **Provide Portfolio → Program → Project hierarchy** for strategic organization
✅ **Enable portfolio scoring and prioritization** with customizable criteria
✅ **Aggregate budget, timeline, and resource data** from child projects
✅ **Implement stage-gate workflow** for governance (Gates 0-5)
✅ **Maintain 95% parity** with Clarity PPM core portfolio features
✅ **Remain 100% Odoo CE compatible** (no Enterprise dependencies)
✅ **Integrate with existing** `project.project` and `project.task` modules

### Non-Goals

❌ **Advanced resource optimization** (automated skill-based matching → ipai_ppm_capacity)
❌ **Roadmap visualization** (Gantt with dependencies → ipai_ppm_roadmap)
❌ **Financial forecasting** (NPV, IRR calculations → future enhancement)
❌ **PPM mobile app** (use existing Odoo mobile app for tasks)

---

## 3. Personas and Use Cases

### Persona 1: Portfolio Manager (Sarah)

**Background**: Oversees $5M portfolio with 3 programs and 15 projects

**Use Cases**:
1. **UC-1.1**: Create portfolio "Digital Transformation 2026" with strategic objectives
2. **UC-1.2**: Assign 3 programs (Customer Experience, Operations, IT Modernization)
3. **UC-1.3**: View consolidated budget: $5M planned vs $3.2M actual across all projects
4. **UC-1.4**: Score and prioritize projects using weighted criteria (strategic fit: 40%, ROI: 30%, risk: 30%)
5. **UC-1.5**: Review Gate 2 submissions and approve/reject project continuation

### Persona 2: Program Manager (Michael)

**Background**: Manages "Customer Experience" program with 5 related projects

**Use Cases**:
2. **UC-2.1**: Create program "Customer Experience Modernization" under Digital Transformation portfolio
3. **UC-2.2**: Link 5 projects (Mobile App, CRM Upgrade, Chatbot, Self-Service Portal, NPS Dashboard)
4. **UC-2.3**: View program-level aggregates: 15 FTE allocated, 8 months avg duration
5. **UC-2.4**: Identify cross-project dependencies and resource conflicts
6. **UC-2.5**: Prepare Gate 3 review package with business case and milestone status

### Persona 3: Resource Manager (Lisa)

**Background**: Allocates 50 consultants across portfolio initiatives

**Use Cases**:
3. **UC-3.1**: View resource utilization heatmap across all programs
4. **UC-3.2**: Identify overallocation conflicts (e.g., John Doe assigned 120% capacity)
5. **UC-3.3**: Search for available resources with specific skills (Java, React, SAP)
6. **UC-3.4**: Forecast resource needs for upcoming project phases
7. **UC-3.5**: Generate capacity planning report for executive review

---

## 4. High-Level Design

### Data Model

#### 4.1 Portfolio Model (`ppm.portfolio`)

```python
class PpmPortfolio(models.Model):
    _name = 'ppm.portfolio'
    _description = 'Portfolio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # Basic Information
    name = fields.Char(required=True, tracking=True)
    code = fields.Char(unique=True, required=True, tracking=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Html()

    # Ownership
    owner_id = fields.Many2one('res.users', string='Portfolio Owner', tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    # Hierarchy
    program_ids = fields.One2many('ppm.program', 'portfolio_id', string='Programs')
    program_count = fields.Integer(compute='_compute_counts', store=True)

    # Strategic Objectives
    strategic_objective_ids = fields.Many2many('ppm.strategic.objective')

    # Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('closed', 'Closed')
    ], default='draft', required=True, tracking=True)

    # Scoring
    score_strategic_fit = fields.Float(digits=(5, 2))
    score_roi = fields.Float(digits=(5, 2))
    score_risk = fields.Float(digits=(5, 2))
    score_total = fields.Float(compute='_compute_score_total', store=True)

    # Aggregations (computed from programs → projects)
    budget_planned = fields.Monetary(compute='_compute_aggregates', store=True)
    budget_actual = fields.Monetary(compute='_compute_aggregates', store=True)
    budget_variance = fields.Monetary(compute='_compute_aggregates', store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    # Dates
    date_start = fields.Date(tracking=True)
    date_end = fields.Date(tracking=True)
    date_approved = fields.Date(tracking=True)
    date_closed = fields.Date(tracking=True)

    @api.depends('program_ids')
    def _compute_counts(self):
        for portfolio in self:
            portfolio.program_count = len(portfolio.program_ids)

    @api.depends('score_strategic_fit', 'score_roi', 'score_risk')
    def _compute_score_total(self):
        for portfolio in self:
            # Weighted scoring: strategic_fit (40%), ROI (30%), risk (30%)
            portfolio.score_total = (
                portfolio.score_strategic_fit * 0.4 +
                portfolio.score_roi * 0.3 +
                portfolio.score_risk * 0.3
            )

    @api.depends('program_ids.budget_planned', 'program_ids.budget_actual')
    def _compute_aggregates(self):
        for portfolio in self:
            portfolio.budget_planned = sum(portfolio.program_ids.mapped('budget_planned'))
            portfolio.budget_actual = sum(portfolio.program_ids.mapped('budget_actual'))
            portfolio.budget_variance = portfolio.budget_planned - portfolio.budget_actual
```

#### 4.2 Program Model (`ppm.program`)

```python
class PpmProgram(models.Model):
    _name = 'ppm.program'
    _description = 'Program'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # Basic Information
    name = fields.Char(required=True, tracking=True)
    code = fields.Char(unique=True, required=True, tracking=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Html()

    # Ownership
    manager_id = fields.Many2one('res.users', string='Program Manager', tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    # Hierarchy
    portfolio_id = fields.Many2one('ppm.portfolio', string='Portfolio', required=True, ondelete='cascade', tracking=True)
    project_ids = fields.One2many('project.project', 'program_id', string='Projects')
    project_count = fields.Integer(compute='_compute_counts', store=True)

    # Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planning', 'Planning'),
        ('execution', 'Execution'),
        ('closing', 'Closing'),
        ('closed', 'Closed')
    ], default='draft', required=True, tracking=True)

    # Aggregations (computed from projects)
    budget_planned = fields.Monetary(compute='_compute_aggregates', store=True)
    budget_actual = fields.Monetary(compute='_compute_aggregates', store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    task_count = fields.Integer(compute='_compute_aggregates', store=True)
    task_done_count = fields.Integer(compute='_compute_aggregates', store=True)

    # Dates
    date_start = fields.Date(tracking=True)
    date_end = fields.Date(tracking=True)

    @api.depends('project_ids')
    def _compute_counts(self):
        for program in self:
            program.project_count = len(program.project_ids)

    @api.depends('project_ids.allocated_hours', 'project_ids.subtask_effective_hours')
    def _compute_aggregates(self):
        for program in self:
            program.budget_planned = sum(program.project_ids.mapped('allocated_hours')) * 100  # Placeholder
            program.budget_actual = sum(program.project_ids.mapped('subtask_effective_hours')) * 100
            program.task_count = sum(program.project_ids.mapped('task_count'))
            program.task_done_count = sum(
                program.project_ids.mapped('task_ids').filtered(lambda t: t.stage_id.fold).mapped('id')
            )
```

#### 4.3 Gate Model (`ppm.gate`)

```python
class PpmGate(models.Model):
    _name = 'ppm.gate'
    _description = 'Stage-Gate Decision Point'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'gate_number, date_scheduled'

    # Gate Definition
    name = fields.Char(compute='_compute_name', store=True)
    gate_number = fields.Selection([
        ('0', 'Gate 0: Ideation'),
        ('1', 'Gate 1: Scoping'),
        ('2', 'Gate 2: Business Case'),
        ('3', 'Gate 3: Development'),
        ('4', 'Gate 4: Testing'),
        ('5', 'Gate 5: Launch')
    ], required=True, tracking=True)

    # Linkage
    project_id = fields.Many2one('project.project', required=True, ondelete='cascade', tracking=True)
    program_id = fields.Many2one('ppm.program', related='project_id.program_id', store=True)
    portfolio_id = fields.Many2one('ppm.portfolio', related='program_id.portfolio_id', store=True)

    # Scheduling
    date_scheduled = fields.Date(required=True, tracking=True)
    date_actual = fields.Date(tracking=True)

    # Decision
    decision = fields.Selection([
        ('pending', 'Pending Review'),
        ('go', 'GO – Approved'),
        ('kill', 'KILL – Rejected'),
        ('hold', 'HOLD – Deferred'),
        ('recycle', 'RECYCLE – Rework Required')
    ], default='pending', required=True, tracking=True)

    # Review
    reviewer_ids = fields.Many2many('res.users', string='Gate Reviewers')
    review_notes = fields.Html()
    attachment_ids = fields.Many2many('ir.attachment', string='Deliverables')

    @api.depends('gate_number', 'project_id.name')
    def _compute_name(self):
        for gate in self:
            gate_labels = dict(gate._fields['gate_number'].selection)
            gate.name = f"{gate.project_id.name} – {gate_labels.get(gate.gate_number, '')}"
```

### Architecture Diagram

```
ppm.portfolio (Digital Transformation 2026)
  ├── ppm.program (Customer Experience)
  │     ├── project.project (Mobile App)
  │     │     ├── ppm.gate (Gate 2: Business Case)
  │     │     └── project.task (x15)
  │     ├── project.project (CRM Upgrade)
  │     └── project.project (Chatbot)
  ├── ppm.program (Operations Excellence)
  └── ppm.program (IT Modernization)
```

---

## 5. Functional Requirements

### FR-1: Portfolio Management

**FR-1.1**: Users can create portfolios with name, code, owner, strategic objectives
**FR-1.2**: Portfolios aggregate budget, timeline, and resource data from child programs
**FR-1.3**: Portfolios support weighted scoring (strategic fit, ROI, risk) for prioritization
**FR-1.4**: Portfolios have workflow states (draft → in_review → approved → active → closed)
**FR-1.5**: Portfolio dashboard shows KPIs: budget variance, task completion %, gate pass rate

### FR-2: Program Management

**FR-2.1**: Users can create programs under portfolios with name, code, manager
**FR-2.2**: Programs link to multiple projects via `project.program_id` field
**FR-2.3**: Programs aggregate data from child projects (budget, tasks, hours)
**FR-2.4**: Programs have workflow states (draft → planning → execution → closing → closed)
**FR-2.5**: Program view shows dependency map of linked projects

### FR-3: Stage-Gate Workflow

**FR-3.1**: Projects have configurable gates (0-5) with scheduled review dates
**FR-3.2**: Gates require deliverables (attachments) and reviewer approval
**FR-3.3**: Gate decisions: GO, KILL, HOLD, RECYCLE
**FR-3.4**: Projects cannot proceed to next phase without passing current gate
**FR-3.5**: Gate dashboard shows upcoming reviews and overdue decisions

### FR-4: Reporting & Analytics

**FR-4.1**: Portfolio view: pivot table of programs by budget, timeline, resource allocation
**FR-4.2**: Program view: Gantt chart of linked projects with milestones
**FR-4.3**: Gate view: funnel chart showing pass/fail rate by gate number
**FR-4.4**: Resource view: heatmap of allocation across portfolio (requires ipai_ppm_capacity)
**FR-4.5**: Export portfolio summary to PDF for executive reviews

---

## 6. Implementation Plan

### Phase 1: Core Models & Views (Week 1-2)

**Deliverables**:
- `ppm.portfolio` model with fields, constraints, and computed aggregations
- `ppm.program` model with project linkage
- `ppm.gate` model with decision workflow
- Tree, form, kanban views for all 3 models
- Security: `ir.model.access.csv` with Portfolio Manager, Program Manager, Executive roles

**Acceptance Criteria**:
- Portfolio owner can create portfolio with 3 programs
- Program manager can link 5 projects to a program
- Budget aggregations show correct totals from project.allocated_hours

### Phase 2: Scoring & Aggregations (Week 3)

**Deliverables**:
- Weighted scoring system (`_compute_score_total`)
- Budget aggregation logic (`_compute_aggregates`)
- Task completion percentage calculation
- Portfolio prioritization pivot view

**Acceptance Criteria**:
- Scoring formula matches: (strategic_fit * 0.4) + (ROI * 0.3) + (risk * 0.3)
- Budget variance = budget_planned - budget_actual
- Task completion % = task_done_count / task_count * 100

### Phase 3: Reporting & UX Polish (Week 4)

**Deliverables**:
- Portfolio dashboard with graph views (budget, timeline, gate funnel)
- Stage-gate approval workflow (activities + notifications)
- Kanban view for portfolios by state
- Graph view for program budget trends

**Acceptance Criteria**:
- Dashboard loads in <2 seconds with 100+ projects
- Gate reviewers receive email notification 7 days before scheduled date
- Kanban drag-and-drop updates portfolio state

### Phase 4: Testing & Documentation (Week 5)

**Deliverables**:
- Regression tests: `addons/ipai_ppm_portfolio/tests/test_portfolio_aggregations.py`
- UAT script: 6 scenarios covering portfolio creation → gate review
- Feature parity docs: `docs/FEATURE_CLARITY_PPM_PARITY.md`
- CI/CD integration: `.github/workflows/odoo-parity-tests.yml` update

**Acceptance Criteria**:
- Test coverage ≥80% for models, ≥70% for workflows
- All 6 UAT scenarios pass without errors
- CI workflow green on pull request

---

## 7. Acceptance Criteria

### AC-1: Portfolio Hierarchy

✅ **GIVEN** a portfolio "Digital Transformation 2026"
✅ **WHEN** user creates 3 programs and links 15 projects across them
✅ **THEN** portfolio shows budget_planned = sum of all 15 projects
✅ **AND** program_count = 3, project_count = 15 aggregated correctly

### AC-2: Weighted Scoring

✅ **GIVEN** a portfolio with score_strategic_fit=80, score_roi=70, score_risk=60
✅ **WHEN** system computes score_total
✅ **THEN** score_total = (80*0.4) + (70*0.3) + (60*0.3) = 71.0

### AC-3: Stage-Gate Workflow

✅ **GIVEN** a project at Gate 2 (Business Case)
✅ **WHEN** reviewer sets decision = 'go' and date_actual = today
✅ **THEN** project state advances to Gate 3 (Development)
✅ **AND** notification sent to project manager

### AC-4: Reporting

✅ **GIVEN** 100 projects across 5 portfolios
✅ **WHEN** user opens portfolio pivot view
✅ **THEN** page loads in <2 seconds
✅ **AND** shows budget variance, task completion %, gate pass rate

### AC-5: Integration

✅ **GIVEN** existing `project.project` records
✅ **WHEN** user upgrades ipai_ppm_portfolio module
✅ **THEN** no data loss or constraint violations
✅ **AND** `program_id` field added to all projects without breaking views

---

## 8. Dependencies

### Odoo CE Core Modules

- `project` (required): Provides project.project and project.task models
- `hr` (optional): Links program.manager_id to hr.employee for org chart
- `mail` (required): Chatter integration for portfolio discussions

### OCA Modules

- None required (100% CE compatible)

### External Services

- None required

---

## 9. Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| Performance degradation with >1000 projects | Medium | High | Index `program_id`, `portfolio_id` fields; optimize `_compute_aggregates` with SQL |
| User resistance to new hierarchy | Medium | Medium | Provide migration guide showing how to organize existing projects into programs |
| Gate workflow too rigid for agile teams | Low | Medium | Make gates optional per project; provide "Fast Track" mode skipping gates 1-4 |
| Budget aggregation logic errors | Medium | High | Comprehensive unit tests; validate against manual Excel calculations |

---

## 10. Success Metrics

- **Adoption Rate**: ≥70% of projects linked to programs within 3 months
- **Time Savings**: 50% reduction in manual portfolio reporting time
- **Decision Speed**: Gate review cycle time reduced from 14 days to 7 days
- **Data Accuracy**: <5% variance between aggregated vs actual budget figures
- **User Satisfaction**: ≥4.0/5.0 rating from portfolio managers in UAT survey

---

## 11. Future Enhancements (Out of Scope)

- **ipai_ppm_capacity**: Resource capacity planning with skill-based matching
- **ipai_ppm_roadmap**: Strategic roadmap visualization (Gantt with dependencies)
- **ipai_ppm_scoring**: Advanced multi-criteria decision analysis (MCDA)
- **Financial Forecasting**: NPV, IRR, payback period calculations
- **AI-Powered Recommendations**: Machine learning for project prioritization

---

## 12. References

- **Clarity PPM Documentation**: Enterprise PPM best practices
- **Odoo Project Module**: https://www.odoo.com/documentation/18.0/applications/services/project.html
- **ENTERPRISE_FEATURE_GAP.yaml**: Line 122-174 (Clarity PPM section)
- **Agent Skills Registry**: `saas_parity_reverse_mapper` capability

---

**Status**: Ready for implementation (PRD approved by reverse mapping agent)
**Next Steps**: Scaffold module, implement Phase 1, write regression tests
