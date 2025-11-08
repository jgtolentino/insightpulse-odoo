# InsightPulse Odoo – Sprint Planning & Milestones

**Last Updated**: 2025-11-08
**Planning Horizon**: 22 weeks (5 sprints)
**Methodology**: Agile Scrum with PMBOK guidance
**Current Status**: Wave 4 (80% complete)

---

## 🎯 Mission & Objectives

**Vision**: Build a complete, self-hosted enterprise SaaS replacement suite providing 95% feature parity at <5% of the cost.

**Target**: $60K+/year in SaaS replacements for <$300/year in infrastructure

**Key Objectives**:
1. Replace SAP Concur ($15K/yr) → Odoo Expense
2. Replace SAP Ariba ($12K/yr) → Odoo Procurement
3. Replace Tableau ($8.4K/yr) → Apache Superset
4. Replace Odoo Enterprise ($4.7K/yr) → Odoo CE + OCA
5. Achieve BIR compliance (Philippines)
6. Implement multi-tenant architecture

---

## 📅 Sprint Timeline (22 Weeks)

### Phase 0: Foundation (Weeks 0-2) ✅ COMPLETE
**Goal**: Establish `ipai_core` infrastructure foundation

**Deliverables**:
- [x] Core module structure (`ipai_core`)
- [x] Shared utilities (RLS templates, audit decorators, queue jobs)
- [x] Base models (approval.flow, rate.policy, ai.workspace, tenant.manager)
- [x] CI/CD pipeline setup (GitHub Actions)
- [x] Development environment (Docker compose)

**Status**: ✅ Complete

---

### Sprint 1: Unified Approvals + Cost Sheets (Weeks 1-4) 🔄 IN PROGRESS
**Duration**: 4 weeks (28 days)
**Team Capacity**: 160 hours
**Epic Coverage**: Epic 1 + Epic 2

#### Epic 1: Unified Approvals Engine
**Goal**: Generic multi-stage approval for Cost Sheets, RFQs, Expenses, Invoices, Docs

**Acceptance Criteria**:
- [ ] Any record type can define stages + actors + escalation
- [ ] Audit trail recorded via `mail.thread`
- [ ] Approval flow configurable per module
- [ ] Email notifications for pending approvals

**Tasks**:
- [ ] Create `ipai_approvals` module
- [ ] Implement `approval.flow` model
- [ ] Add state machine (Draft → Review → Approved → Rejected)
- [ ] Create approval wizard views
- [ ] Write unit tests (>80% coverage)
- [ ] Document API endpoints

**Module**: `addons/custom/ipai_approvals/`

#### Epic 2: Vendor-Privacy Cost Sheets
**Goal**: AM sees Role & Rate; FD sees Vendor & Cost

**Acceptance Criteria**:
- [ ] State flow: Draft → FD Review → Approved → Shared → Invoiced
- [ ] Vendor hidden via record rule (non-FD roles)
- [ ] Cost sheet lines link to projects
- [ ] Client portal view for shared cost sheets

**Tasks**:
- [ ] Create `ipai_ppm_costsheet` module
- [ ] Implement `job.costsheet` and `job.costsheet.line` models
- [ ] Add RLS rules for vendor privacy
- [ ] Create form/tree views with conditional fields
- [ ] Add client portal template
- [ ] Write HttpCase tests for RLS

**Module**: `addons/custom/ipai_ppm_costsheet/`

**Sprint 1 KPIs**:
- Test coverage: >80%
- Performance: <200ms CRUD operations
- Security: RLS rules validated

---

### Sprint 2: Rate Policy + PPM Core (Weeks 5-8) 📋 PLANNED
**Duration**: 4 weeks (28 days)
**Team Capacity**: 160 hours
**Epic Coverage**: Epic 3 + Epic 6

#### Epic 3: Rate Policy Automation
**Goal**: Compute Public Rate Bands automatically from vendor rate history

**Acceptance Criteria**:
- [ ] Nightly cron updates client rates
- [ ] Formula: P60 over 18 months + 25% markup + ₱100 rounding
- [ ] Rate card history tracked
- [ ] Public rate bands visible to AM, vendor rates to FD only

**Tasks**:
- [ ] Create `ipai_rate_policy` module
- [ ] Implement `vendor.rate.card` and `public.rate.band` models
- [ ] Add cron job for rate calculation
- [ ] Create rate policy settings page
- [ ] Write unit tests for rate calculations
- [ ] Document rate policy algorithm

**Module**: `addons/custom/ipai_rate_policy/`

#### Epic 6: PPM Core (Clarity parity)
**Goal**: Program / Project / Roadmap / Budget / Risk / Stage-Gate

**Acceptance Criteria**:
- [ ] Program → Project hierarchy established
- [ ] Budget vs actual dashboards operational
- [ ] FD gate approvals per phase
- [ ] Risk register integrated

**Tasks**:
- [ ] Create `ipai_ppm` module
- [ ] Implement `ppm.program`, `ppm.roadmap`, `ppm.budget` models
- [ ] Extend `project.project` with stage-gate workflow
- [ ] Add budget tracking views
- [ ] Integrate with `project_risk` OCA module
- [ ] Create PPM dashboards

**Module**: `addons/custom/ipai_ppm/`

**Sprint 2 KPIs**:
- Rate calculation accuracy: 100%
- Budget variance tracking: ±2%
- Dashboard load time: <3s

---

### Sprint 3: Procurement + Travel & Expense (Weeks 9-12) 📋 PLANNED
**Duration**: 4 weeks (28 days)
**Team Capacity**: 160 hours
**Epic Coverage**: Epic 4 + Epic 5

#### Epic 4: Procurement & SRM (Ariba parity)
**Goal**: Supplier onboarding, RFQs, bids, contracts, scorecards

**Acceptance Criteria**:
- [ ] Vendor lifecycle: onboarding → RFQ → PO → scorecard
- [ ] Multi-round bidding support
- [ ] 3-way match (PO → GRN → Invoice)
- [ ] Vendor scorecards (quality, delivery, pricing)

**Tasks**:
- [ ] Enhance `ipai_procure` module
- [ ] Extend OCA `purchase_requisition` and `purchase_contract`
- [ ] Implement vendor onboarding workflow
- [ ] Add RFQ bidding interface
- [ ] Create vendor scorecard model
- [ ] Write integration tests for 3-way match

**Module**: `addons/custom/ipai_procure/`

#### Epic 5: Travel & Expense (Concur parity)
**Goal**: Travel request → itinerary → expense → rebill

**Acceptance Criteria**:
- [ ] OCR receipts auto-fill expense lines
- [ ] Approved expenses rebill to project or offset retainer
- [ ] Travel request workflow with approvals
- [ ] Mileage calculation for vehicle expenses

**Tasks**:
- [ ] Enhance `ipai_expense` module
- [ ] Integrate OCA `account_invoice_ocr_google`
- [ ] Implement `travel.request` model
- [ ] Add expense rebilling logic
- [ ] Create mobile-friendly expense submission form
- [ ] Write HttpCase tests for OCR integration

**Module**: `addons/custom/ipai_expense/`

**Sprint 3 KPIs**:
- Vendor approval lead time: -40%
- OCR accuracy: >90%
- Expense processing time: <2 days

---

### Sprint 4: Retainers + Analytics (Weeks 13-16) 📋 PLANNED
**Duration**: 4 weeks (28 days)
**Team Capacity**: 160 hours
**Epic Coverage**: Epic 7 + Epic 9

#### Epic 7: Retainers & Subscriptions (SaaS Billing parity)
**Goal**: Recurring retainer contracts + auto-invoice + dunning

**Acceptance Criteria**:
- [ ] Monthly invoice cron runs successfully
- [ ] Overage detector alerts when usage exceeds limit (>95%)
- [ ] Client portal shows retainer balance
- [ ] Dunning workflow for overdue invoices

**Tasks**:
- [ ] Enhance `ipai_subscriptions` module
- [ ] Extend OCA `contract` and `subscription_oca`
- [ ] Implement overage detection logic
- [ ] Add dunning workflow (reminder emails)
- [ ] Create client portal retainer view
- [ ] Write unit tests for billing calculations

**Module**: `addons/custom/ipai_subscriptions/`

#### Epic 9: Analytics & Dashboards (Tableau parity)
**Goal**: MRR/ARR, job profitability, vendor spend, budget vs actual

**Acceptance Criteria**:
- [ ] Saved dashboards render <5s with filters per Program/Client
- [ ] Key metrics: MRR, ARR, job profitability, vendor spend
- [ ] Drill-down from summary to transaction level
- [ ] Export to PDF/Excel

**Tasks**:
- [ ] Enhance `superset_connector` module
- [ ] Create Superset datasets (SQL views)
- [ ] Build 5 key dashboards (Finance, PPM, Procurement, Expenses, Retainers)
- [ ] Configure RLS for multi-company isolation
- [ ] Add scheduled email reports
- [ ] Optimize query performance (<5s load time)

**Module**: `addons/custom/superset_connector/`

**Sprint 4 KPIs**:
- Retainer overage detection: ≥95%
- Dashboard load time: <5s
- MRR/ARR tracking accuracy: 100%

---

### Sprint 5: Knowledge Workspace + SaaS Ops (Weeks 17-20) 📋 PLANNED
**Duration**: 4 weeks (28 days)
**Team Capacity**: 160 hours
**Epic Coverage**: Epic 8 + Epic 10

#### Epic 8: Knowledge Workspace (Notion parity)
**Goal**: AI-assisted collaborative docs per Program/Project

**Acceptance Criteria**:
- [ ] Workspace pages linked to Programs/Projects
- [ ] Vector index for document search (pgvector)
- [ ] "/ask" queries answer from project context
- [ ] AI workspace answer precision ≥0.9 F1

**Tasks**:
- [ ] Create `ipai_knowledge_ai` module
- [ ] Extend `document_knowledge` OCA module
- [ ] Implement `ai.workspace` model with vector indexing
- [ ] Add AI query interface ("/ask" command)
- [ ] Integrate with OpenAI/Claude API
- [ ] Write accuracy tests (F1 score validation)

**Module**: `addons/custom/ipai_knowledge_ai/`

#### Epic 10: SaaS Ops & Multi-Tenancy
**Goal**: Self-service tenant create + backup + usage billing

**Acceptance Criteria**:
- [ ] New client DB spins via API
- [ ] Auto daily backup to DigitalOcean Spaces
- [ ] Tenant usage metrics tracked
- [ ] Billing based on usage (storage, API calls)

**Tasks**:
- [ ] Create `ipai_saas_ops` module
- [ ] Implement tenant provisioning API
- [ ] Integrate with `auto_backup` OCA module
- [ ] Add usage tracking (storage, API calls, users)
- [ ] Create tenant admin dashboard
- [ ] Write integration tests for provisioning

**Module**: `addons/custom/ipai_saas_ops/`

**Sprint 5 KPIs**:
- AI answer precision: ≥0.9 F1
- Tenant provisioning time: <5 minutes
- Backup success rate: 100%

---

## 📊 Key Performance Indicators (KPIs)

### Business KPIs
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Estimate → Invoice cycle** | ≤5 days | TBD | 🔴 |
| **Vendor approval lead time** | -40% | TBD | 🔴 |
| **Retainer overage detection** | ≥95% | TBD | 🔴 |
| **Margin variance** | ≤±2% | TBD | 🔴 |
| **AI workspace answer precision** | ≥0.9 F1 | TBD | 🔴 |

### Technical KPIs
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Response time P95** | <500ms | TBD | 🔴 |
| **Database query time P95** | <200ms | TBD | 🔴 |
| **Queue job success rate** | >99% | TBD | 🔴 |
| **API error rate** | <0.1% | TBD | 🔴 |
| **Test coverage** | >80% | 75% | 🟡 |
| **System uptime** | >99.5% | 99.8% | 🟢 |

---

## 🎯 Milestones & Go-Live Checklist

### Milestone 1: Sprint 1 Complete (Week 4)
- [ ] Unified Approvals Engine operational
- [ ] Cost sheets with vendor privacy implemented
- [ ] 80% test coverage achieved
- [ ] RLS rules validated

### Milestone 2: Sprint 2 Complete (Week 8)
- [ ] Rate policy automation functional
- [ ] PPM Core with budget tracking deployed
- [ ] Stage-gate workflow operational
- [ ] Budget vs actual dashboards live

### Milestone 3: Sprint 3 Complete (Week 12)
- [ ] Procurement module with 3-way match operational
- [ ] T&E with OCR integration deployed
- [ ] Vendor scorecards calculated
- [ ] Expense rebilling functional

### Milestone 4: Sprint 4 Complete (Week 16)
- [ ] Retainer billing automation operational
- [ ] Overage detection live
- [ ] 5 key Superset dashboards deployed
- [ ] Dashboard performance <5s

### Milestone 5: Sprint 5 Complete (Week 20)
- [ ] AI knowledge workspace operational
- [ ] SaaS tenant provisioning functional
- [ ] Auto-backup configured
- [ ] F1 score ≥0.9 achieved

### Go-Live Readiness (Week 22)
- [ ] All 10 epics acceptance criteria met
- [ ] Security audit passed (no Critical/High vulnerabilities)
- [ ] Performance benchmarks met (P95 <500ms)
- [ ] Test coverage ≥80% across all modules
- [ ] User training completed (AM, FD, Procurement Officer)
- [ ] Documentation complete (admin guide, user manuals, API specs)
- [ ] Production deployment successful (zero downtime)
- [ ] Monitoring dashboards operational (Prometheus, Grafana, Superset)
- [ ] Backup/restore tested successfully

---

## 🚨 Risk Register

### High Risk
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **OCA module compatibility issues** | Medium | High | Pin specific OCA versions; test in staging |
| **User adoption resistance** | Medium | High | Phased rollout; training; change management |
| **Scope creep beyond 22 weeks** | High | Medium | Sprint reviews; MVP focus; backlog prioritization |

### Medium Risk
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **AI workspace accuracy <0.9 F1** | Medium | Medium | Iterative prompt engineering; pgvector tuning |
| **Key developer departure** | Medium | High | Documentation; code reviews; knowledge transfer |

### Low Risk
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Performance degradation (>100 modules)** | Low | High | Database optimization; connection pooling; caching |
| **Multi-tenancy security breach** | Low | Critical | Rigorous RLS testing; security audit |

---

## 📝 Sprint Ceremonies

### Daily Standup (15 min)
- What did I complete yesterday?
- What am I working on today?
- Any blockers?

### Sprint Planning (Week 1, Day 1 – 2 hours)
- Review product backlog
- Select stories for sprint
- Estimate effort (story points)
- Commit to sprint goal

### Sprint Review (Week 4, Day 5 – 1 hour)
- Demo completed features
- Gather stakeholder feedback
- Update product backlog

### Sprint Retrospective (Week 4, Day 5 – 1 hour)
- What went well?
- What didn't go well?
- Action items for improvement

---

## 🔗 Related Documents

- **PRD**: `docs/PRD_ENTERPRISE_SAAS_PARITY.md` (Epic details)
- **Roadmap**: `docs/ROADMAP.md` (Waves 1-9 overview)
- **Tasks**: `TASKS.md` (Current sprint tasks)
- **Architecture**: `ARCHITECTURE.md` (System design)
- **Changelog**: `CHANGELOG.md` (Version history)

---

**Maintainer**: InsightPulse AI Team
**Repository**: https://github.com/jgtolentino/insightpulse-odoo
**License**: AGPL-3.0
**Odoo Version**: 18 CE
**Last Review**: 2025-11-08
