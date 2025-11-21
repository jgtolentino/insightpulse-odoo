# InsightPulse ERP – Platform Matrix (Concur / Cheqroom / Notion)

## 1. Odoo Modules

| Module / Addon                  | Type      | SAP Concur (Expenses/Travel) | Cheqroom (Equipment) | Notion (Closing/BIR) | Notes / Scope                                                                 |
|---------------------------------|-----------|------------------------------|----------------------|----------------------|-------------------------------------------------------------------------------|
| base, web, mail                 | Core CE   | ✅                            | ✅                    | ✅                    | Core framework, UI, messaging, activities.                                    |
| contacts                        | Core CE   | ✅                            | ✅                    | ✅                    | Employees, vendors, counterparties.                                           |
| hr                              | Core CE   | ✅                            | ➖                    | ✅                    | Base HR model for employees.                                                  |
| hr_expense                      | Core CE   | ✅                            | ➖                    | ➖                    | Expense claims; Concur-parity backbone.                                       |
| hr_holidays (Time Off)         | Core CE   | ✅                            | ➖                    | ➖                    | Optional: link leaves to travel/expense.                                      |
| account, account_accountant     | Core CE   | ✅                            | ✅                    | ✅                    | Posting, journals, tax; used by all three domains.                            |
| project                         | Core CE   | ✅                            | ✅                    | ✅                    | Tasks, Kanban, deadlines; Notion-equivalent DB; booking contexts.            |
| stock, stock_account            | Core CE   | ➖                            | ✅                    | ➖                    | Equipment as stockable assets; valuations.                                    |
| maintenance                     | Core CE   | ➖                            | ✅                    | ➖                    | Maintenance requests / equipment registry.                                    |
| calendar                        | Core CE   | ✅                            | ✅                    | ✅                    | Travel calendars, booking windows, BIR deadlines.                             |
| knowledge                       | Core CE   | ➖                            | ➖                    | ✅                    | SOP / wiki pages for closing & BIR workflows (Notion-like).                  |
| fleet (optional)               | Core CE   | ➖                            | ⚪                    | ➖                    | Use if you want vehicles as bookable assets (shoot vans, etc.).             |
| ipai_ce_cleaner                 | Custom    | ✅                            | ✅                    | ✅                    | Hides Enterprise/IAP/odoo.com upsells; enforces InsightPulse/OCA-only UI.    |
| ipai_ocr_expense                | Custom    | ✅                            | ➖                    | ➖                    | OCR button + statusbar on expenses; logs; adapter integration.               |
| ipai_expense                    | Custom    | ✅                            | ➖                    | ⚪                    | PH-focused travel/expense workflows; approvals; extra fields.                |
| ipai_equipment                  | Custom    | ➖                            | ✅                    | ➖                    | Equipment catalog, bookings, conflicts, check-in/out, incidents.             |
| ipai_finance_monthly_closing    | Custom    | ⚪                            | ⚪                    | ✅                    | Extends project.task with Cluster, M±N, BIR fields, reviewer/approver, etc.  |
| ipai_ocr_expense (logs)         | Custom    | ✅                            | ➖                    | ⚪                    | `ocr.expense.log` model + views for quality & performance metrics.           |
| (Future) ipai_bir_filing        | Custom    | ➖                            | ➖                    | ✅                    | Optional dedicated `bir.filing` model with smart buttons to tasks.           |

Legend: ✅ Core for this product | ➖ Not used directly | ⚪ Optional / nice-to-have

---

## 2. External Services

| Service / Component                            | Layer          | SAP Concur Role                     | Cheqroom Role                       | Notion Role                                  | Notes                                                                 |
|-----------------------------------------------|----------------|-------------------------------------|-------------------------------------|----------------------------------------------|-----------------------------------------------------------------------|
| `ocr.insightpulseai.net` – OCR Adapter        | API Service    | ✅ Receipt OCR → `ipai_ocr_expense` | ➖                                   | ➖                                            | FastAPI adapter; maps OCR engine → Odoo JSON contract.               |
| PaddleOCR-VL + OpenAI engine                  | ML Engine      | ✅ Text extraction from receipts     | ⚪ Asset label OCR (future)         | ➖                                            | Lives behind adapter; swappable without Odoo changes.                |
| `odoo-erp-prod` droplet                       | Compute        | ✅ Main ERP                          | ✅ Main ERP                          | ✅ Main ERP                                   | Runs Odoo CE 18 + Postgres + nginx; single source of truth.          |
| `ocr-service-droplet`                         | Compute        | ✅ OCR backend                       | ⚪ Future vision/asset OCR          | ➖                                            | Hosts OCR engine + adapter.                                          |
| n8n (fin-workspace)                           | Automation     | ✅ Email → expense, reminders       | ✅ Booking → calendar sync          | ✅ Closing + BIR reminders / digests          | JSON-RPC into Odoo; runs CRON-style finance automation.              |
| Superset (`superset.insightpulseai.net`)      | Analytics/BI   | ⚪ Expense analytics                 | ⚪ Utilization / incident dashboards | ⚪ Closing SLA / tax calendar performance     | Optional but plugs into Postgres/Supabase for reporting.             |
| Mattermost / Chat agents (fin workspace)      | Agents / Chat  | ⚪ Expense Q&A, travel policies     | ⚪ Equipment policy Q&A             | ⚪ Closing/BIR assistant                       | Your Claude-based agents reading from Odoo & docs.                   |
| Supabase (optional mirror)                    | Data Hub       | ⚪ Long-term analytics store         | ⚪ Asset history / usage             | ⚪ Task performance / SLA store                | Only if you want decoupled lake from Odoo DB.                        |

---

## 3. Module Installation Sequence

### Phase 1: Core Foundation (Essential for all products)
```bash
# Core Odoo CE modules - already installed
base, web, mail, contacts, calendar
```

### Phase 2: Domain-Specific Core Modules

#### For SAP Concur (Expenses/Travel)
```bash
hr, hr_expense, hr_holidays, account, account_accountant, project
```

#### For Cheqroom (Equipment)
```bash
stock, stock_account, maintenance, project
```

#### For Notion (Finance Closing/BIR)
```bash
project, knowledge, account, account_accountant
```

### Phase 3: Custom InsightPulse Modules (Install Order)
```bash
1. ipai_ce_cleaner          # Install first - UI cleanup
2. ipai_ocr_expense         # OCR integration for expenses
3. ipai_expense             # PH expense/travel workflows
4. ipai_equipment           # Equipment booking system
5. ipai_finance_monthly_closing  # Finance closing + BIR tasks
```

### Phase 4: Optional OCA Addons (Future Enhancement)
```bash
# Install via git submodule under addons/oca/
account_invoice_import
hr_expense_advance_clearing
mail_activity_board
maintenance_equipment_hierarchy
stock_request
project_task_material
```

---

## 4. External Service Deployment Order

### Step 1: Database & Core ERP
1. ✅ PostgreSQL 15 on `odoo-erp-prod`
2. ✅ Odoo CE 18 on `erp.insightpulseai.net`
3. ✅ nginx reverse proxy with SSL

### Step 2: OCR Infrastructure
1. ✅ OCR Service droplet (`ocr-service-droplet`)
2. ✅ OCR Adapter at `ocr.insightpulseai.net`
3. ✅ PaddleOCR-VL + OpenAI engine

### Step 3: Automation & Integration
1. ⏳ n8n workflows (fin-workspace)
   - Email → expense creation
   - Daily reminder digests
   - BIR deadline alerts
2. ⏳ Calendar sync (optional)

### Step 4: Analytics & BI (Optional)
1. ⏳ Superset at `superset.insightpulseai.net`
2. ⏳ Supabase mirror (if needed)
3. ⏳ Mattermost / Chat agents

---

## 5. Integration Points

### Odoo ↔ OCR Adapter
```
Odoo ipai_ocr_expense → POST /api/expense/ocr
  ← JSON response with fields
→ Create/update hr.expense + ocr.expense.log
```

### Odoo ↔ n8n
```
n8n → JSON-RPC to Odoo
  - Create expense records
  - Update task stages
  - Query overdue tasks
← Odoo webhooks (optional)
```

### Odoo ↔ Superset
```
Superset → Direct PostgreSQL connection (read-only)
  - Query expense analytics
  - Equipment utilization
  - Closing task SLA
```

---

## 6. Current Status (v0.2.1-quality baseline)

### ✅ Completed
- [x] Core Odoo CE 18 installation
- [x] ipai_ce_cleaner (deployed, active)
- [x] ipai_ocr_expense (deployed, tested with OCR adapter)
- [x] OCR adapter at ocr.insightpulseai.net
- [x] PH normalization in OCR response
- [x] Enhanced OCR log views in Odoo
- [x] CE-only validation (169 modules, 0 Enterprise)
- [x] All odoo.com links removed from database
- [x] UI cleanup (hidden Website column, Enterprise badges)

### ⏳ In Progress
- [ ] ipai_expense (PH travel/expense workflows)
- [ ] ipai_equipment (equipment booking system)
- [ ] ipai_finance_monthly_closing (task import and templates)

### 📋 Planned
- [ ] n8n workflow deployment
- [ ] Superset dashboard creation
- [ ] OCA addon integration
- [ ] Chat agent integration (Mattermost)

---

## 7. v1 Scope Checklists

See [tasks.md](./tasks.md) for detailed v1 checklists by product.
