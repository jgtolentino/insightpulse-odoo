# InsightPulse Odoo API Documentation

**Generated**: 2025-11-09 03:01:03
**Repository**: insightpulse-odoo
**Odoo Version**: 19.0

---

## 📊 Summary Statistics

| Metric | Count |
|--------|-------|
| Total Modules | 15 |
| Total Models | 45 |
| Total Fields | 393 |
| Total Views | 14 |
| BIR Modules | 0 |
| Finance Modules | 2 |

---

## 📦 Modules (15)


### Accounting/Expenses

#### IPAI Expense

**Version**: 19.0.20251026.1  
**Author**: InsightPulseAI  
**Summary**: Cash advance lifecycle, expense policy, OCR audit  
**Dependencies**: `base`, `mail`, `hr`, `hr_expense`, `account`, `report_xlsx`, `queue_job`, `server_environment`  
**Installable**: ✓  
**Application**: ✗  

> 
    OCR-powered expense automation with policy validation.

    Features:
    - Multi-provider OCR (PaddleOCR-VL, Azure, Google Vision)
    - Policy validation engine
    - Automated expense creation...

**Models** (3):

##### `ipai.expense.advance`

*File*: `addons/custom/ipai_expense/models/expense_advance.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char |  |  |  |
| `employee_id` | Many2one | ✓ |  | hr.employee |
| `amount` | Monetary | ✓ |  |  |
| `currency_id` | Many2one |  |  | res.currency |
| `purpose` | Char |  |  |  |
| `state` | Selection |  |  |  |
| `liquidation_sheet_id` | Many2one |  |  | hr.expense.sheet |

##### `ipai.expense.ocr.audit`

*File*: `addons/custom/ipai_expense/models/expense_ocr_audit.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `expense_id` | Many2one |  |  | hr.expense |
| `attachment_id` | Many2one | ✓ |  | ir.attachment |
| `ocr_payload` | Json |  |  |  |
| `confidence` | Float |  |  |  |

##### `ipai.expense.policy`

*File*: `addons/custom/ipai_expense/models/expense_policy.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `daily_limit` | Monetary |  |  |  |
| `currency_id` | Many2one |  |  | res.currency |
| `require_receipt` | Boolean |  |  |  |
| `notes` | Text |  |  |  |

**Security**: 1 ACL files  
**Data**: 1 data files  

---


### Accounting/Finance

#### Finance SSC Month-End Closing

**Version**: 19.0.1.0.0  
**Author**: InsightPulse AI  
**Summary**: Month-end closing checklist and BIR compliance tracking for Finance Shared Service Center  
**Dependencies**: `base`, `account`, `account_accountant`, `project`, `mail`, `hr`, `web`  
**Installable**: ✓  
**Application**: ✓  

> 
Finance SSC Month-End Closing Module
=====================================

This module provides comprehensive month-end closing workflow management for
Finance Shared Service Centers (SSC) handling ...

**Models** (4):

##### `finance.closing.period`


    Represents a month-end closing period for Finance SSC operations.
    This model manages the overall closing workflow for a specific period.
    

*File*: `addons/custom/finance_ssc_closing/models/closing_period.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `start_date` | Date | ✓ |  |  |
| `end_date` | Date | ✓ |  |  |
| `fiscal_year` | Char | ✓ |  |  |
| `state` | Selection | ✓ |  |  |
| `task_ids` | One2many |  |  | finance.closing.task |
| `task_count` | Integer |  |  |  |
| `task_completed_count` | Integer |  |  |  |
| `task_pending_count` | Integer |  |  |  |
| `completion_percentage` | Float |  |  |  |
| `bir_task_ids` | One2many |  |  | finance.bir.compliance.task |
| `bir_all_filed` | Boolean |  |  |  |
| `responsible_id` | Many2one |  |  | res.users |
| `reviewer_ids` | Many2many |  |  | res.users |
| `actual_close_date` | Date |  |  |  |
| `approved_date` | Date |  |  |  |
| `approved_by_id` | Many2one |  |  | res.users |
| `notes` | Html |  |  |  |

**Methods**: `action_open()`, `action_start_closing()`, `action_submit_for_review()`, `action_approve()`, `action_close()`, `action_reopen()`, `action_generate_tasks()`  

##### `finance.bir.compliance.task`


    BIR (Bureau of Internal Revenue) compliance task for Philippine tax filings.
    Tracks BIR form submissions for each agency.
    

*File*: `addons/custom/finance_ssc_closing/models/bir_compliance_task.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char |  |  |  |
| `period_id` | Many2one | ✓ |  | finance.closing.period |
| `company_id` | Many2one | ✓ |  | res.company |
| `bir_form` | Selection | ✓ |  |  |
| `filing_frequency` | Selection | ✓ |  |  |
| `due_date` | Date | ✓ |  |  |
| `filing_date` | Date |  |  |  |
| `state` | Selection | ✓ |  |  |
| `prepared_by` | Many2one |  |  | res.users |
| `reviewed_by` | Many2one |  |  | res.users |
| `filed_by` | Many2one |  |  | res.users |
| `tax_amount` | Monetary |  |  |  |
| `penalty_amount` | Monetary |  |  |  |
| `total_amount` | Monetary |  |  |  |
| `currency_id` | Many2one |  |  | res.currency |
| `reference_number` | Char |  |  |  |
| `payment_reference` | Char |  |  |  |
| `form_attachment_id` | Many2one |  |  | ir.attachment |
| `acknowledgment_attachment_id` | Many2one |  |  | ir.attachment |
| `payment_proof_attachment_id` | Many2one |  |  | ir.attachment |
| `notes` | Html |  |  |  |
| `is_overdue` | Boolean |  |  |  |
| `days_overdue` | Integer |  |  |  |

**Methods**: `action_prepare()`, `action_mark_ready()`, `action_file()`, `action_mark_paid()`, `action_upload_form()`  

##### `finance.closing.task`


    Individual month-end closing task.
    Notion equivalent: Database item/row in a closing checklist database.
    

*File*: `addons/custom/finance_ssc_closing/models/closing_task.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `sequence` | Integer |  |  |  |
| `description` | Html |  |  |  |
| `period_id` | Many2one | ✓ |  | finance.closing.period |
| `company_id` | Many2one | ✓ |  | res.company |
| `task_type` | Selection | ✓ |  |  |
| `assigned_to` | Many2one |  |  | res.users |
| `department_id` | Many2one |  |  | hr.department |
| `due_date` | Date | ✓ |  |  |
| `start_date` | Date |  |  |  |
| `completed_date` | Date |  |  |  |
| `state` | Selection | ✓ |  |  |
| `progress` | Integer |  |  |  |
| `priority` | Selection |  |  |  |
| `reviewer_id` | Many2one |  |  | res.users |
| `review_notes` | Html |  |  |  |
| `attachment_ids` | Many2many |  |  | ir.attachment |
| `attachment_count` | Integer |  |  |  |
| `depends_on_ids` | Many2many |  |  | finance.closing.task |
| `blocked_by_count` | Integer |  |  |  |
| `blocks_count` | Integer |  |  |  |
| `estimated_hours` | Float |  |  |  |
| `actual_hours` | Float |  |  |  |
| `active` | Boolean |  |  |  |
| `notes` | Html |  |  |  |

**Methods**: `action_start()`, `action_submit_for_review()`, `action_approve()`, `action_reject()`, `action_block()`, `action_unblock()`, `action_view_attachments()`  

##### `finance.closing.task.template`


    Templates for common month-end closing tasks.
    Allows quick task generation from predefined templates.
    

*File*: `addons/custom/finance_ssc_closing/models/task_template.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `sequence` | Integer |  |  |  |
| `description` | Html |  |  |  |
| `task_type` | Selection | ✓ |  |  |
| `estimated_hours` | Float |  |  |  |
| `priority` | Selection |  |  |  |
| `department_id` | Many2one |  |  | hr.department |
| `days_to_complete` | Integer |  |  |  |
| `active` | Boolean |  |  |  |

**Security**: 1 ACL files  

---


### Connectors

#### Superset Connector

**Version**: 19.0.251027.1  
**Author**: InsightPulseAI  
**Summary**: Apache Superset integration for Odoo  
**Dependencies**: `base`, `web`  
**Installable**: ✓  
**Application**: ✓  

> 
    Integrate Apache Superset dashboards and analytics into Odoo:
    - Embed Superset dashboards in Odoo views
    - Single Sign-On (SSO) integration
    - Dashboard management interface
    - Data ...

**Models** (4):

##### `superset.token`

Manage Superset guest tokens for SSO authentication

*File*: `addons/custom/superset_connector/models/superset_token.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char |  |  |  |
| `token` | Char | ✓ | ✓ |  |
| `user_id` | Many2one | ✓ |  | res.users |
| `dashboard_id` | Many2one | ✓ |  | superset.dashboard |
| `config_id` | Many2one | ✓ |  | superset.config |
| `created_at` | Datetime |  | ✓ |  |
| `expires_at` | Datetime | ✓ |  |  |
| `last_used_at` | Datetime |  |  |  |
| `is_active` | Boolean |  |  |  |
| `use_count` | Integer |  | ✓ |  |
| `user_ip` | Char |  |  |  |
| `user_agent` | Char |  |  |  |

**Methods**: `create()`, `write()`, `get_or_create_token()`, `invalidate_token()`, `cleanup_expired_tokens()`, `get_token_stats()`  

##### `superset.config`

Extend Superset Configuration with CSP settings

*Inherits*: `superset.config`  
*File*: `addons/custom/superset_connector/models/superset_token.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `allowed_origins` | Char |  |  |  |
| `token_expiry_hours` | Integer |  |  |  |
| `max_tokens_per_user` | Integer |  |  |  |

##### `superset.config`

*File*: `addons/custom/superset_connector/models/superset_config.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `base_url` | Char | ✓ |  |  |
| `username` | Char |  |  |  |
| `password` | Char |  |  |  |
| `api_key` | Char |  |  |  |
| `is_active` | Boolean |  |  |  |
| `connection_status` | Selection |  |  |  |
| `last_connection_test` | Datetime |  |  |  |

**Methods**: `test_connection()`  

##### `superset.dashboard`

*File*: `addons/custom/superset_connector/models/superset_config.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `dashboard_id` | Char | ✓ |  |  |
| `config_id` | Many2one | ✓ |  | superset.config |
| `embed_url` | Char |  |  |  |
| `description` | Text |  |  |  |
| `is_active` | Boolean |  |  |  |

**Views**: 2 XML files  
**Security**: 1 ACL files  
**Data**: 1 data files  

---

#### Tableau Connector

**Version**: 19.0.251026.1  
**Author**: InsightPulseAI  
**Summary**: Tableau analytics integration for Odoo  
**Dependencies**: `base`, `web`  
**Installable**: ✓  
**Application**: ✓  

> 
    Integrate Tableau dashboards and analytics into Odoo:
    - Embed Tableau dashboards in Odoo views
    - Data export from Odoo to Tableau
    - Authentication and security integration
    - Dashb...

**Models** (2):

##### `tableau.config`

*File*: `addons/custom/tableau_connector/models/tableau_config.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `server_url` | Char | ✓ |  |  |
| `site_name` | Char |  |  |  |
| `username` | Char |  |  |  |
| `password` | Char |  |  |  |
| `personal_access_token` | Char |  |  |  |
| `is_active` | Boolean |  |  |  |
| `connection_status` | Selection |  |  |  |
| `last_connection_test` | Datetime |  |  |  |

**Methods**: `test_connection()`  

##### `tableau.dashboard`

*File*: `addons/custom/tableau_connector/models/tableau_config.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `dashboard_id` | Char | ✓ |  |  |
| `workbook_id` | Char |  |  |  |
| `config_id` | Many2one | ✓ |  | tableau.config |
| `embed_url` | Char |  |  |  |
| `description` | Text |  |  |  |
| `is_active` | Boolean |  |  |  |

**Methods**: `export_data_to_tableau()`  

**Views**: 2 XML files  
**Security**: 1 ACL files  

---

#### Microservices Connector

**Version**: 19.0.251027.1  
**Author**: InsightPulseAI  
**Summary**: Integration with OCR, LLM, and Agent microservices  
**Dependencies**: `base`, `web`  
**Installable**: ✓  
**Application**: ✓  

> 
    Connect Odoo with your microservices ecosystem:
    - OCR Service integration for document processing
    - LLM Service integration for AI-powered features
    - Agent Service integration for wor...

**Models** (3):

##### `microservices.config`

*File*: `addons/custom/microservices_connector/models/microservices_config.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `ocr_service_url` | Char |  |  |  |
| `llm_service_url` | Char |  |  |  |
| `agent_service_url` | Char |  |  |  |
| `api_key_encrypted` | Binary |  | ✓ |  |
| `auth_token_encrypted` | Binary |  | ✓ |  |
| `api_key` | Char |  |  |  |
| `auth_token` | Char |  |  |  |
| `is_active` | Boolean |  |  |  |
| `connection_status` | Selection |  |  |  |
| `last_connection_test` | Datetime |  |  |  |
| `health_log_ids` | One2many |  |  | microservices.health.log |

**Methods**: `run_self_test()`  

##### `microservices.service`

*File*: `addons/custom/microservices_connector/models/microservices_config.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `service_type` | Selection | ✓ |  |  |
| `config_id` | Many2one | ✓ |  | microservices.config |
| `endpoint_url` | Char |  |  |  |
| `description` | Text |  |  |  |
| `is_active` | Boolean |  |  |  |

**Methods**: `test_service_connection()`  

##### `microservices.health.log`

*File*: `addons/custom/microservices_connector/models/health_log.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `config_id` | Many2one | ✓ |  | microservices.config |
| `component` | Selection | ✓ |  |  |
| `status` | Selection | ✓ |  |  |
| `response_time` | Float |  |  |  |
| `error_message` | Text |  |  |  |
| `total_check_time` | Float |  |  |  |
| `create_date` | Datetime |  |  |  |

**Methods**: `cleanup_old_logs()`  

**Views**: 2 XML files  
**Security**: 1 ACL files  
**Data**: 1 data files  

---


### Human Resources

#### IPAI Approvals

**Version**: 19.0.1.0.0  
**Author**: InsightPulse  
**Summary**: Unified Approvals Engine - Epic 1 (Clarity PPM Parity)  
**Dependencies**: `ipai_core`, `purchase`, `hr_expense`, `account`, `queue_job`  
**Installable**: ✓  
**Application**: ✗  

> 
Unified Approvals Engine
========================

Complete approval workflow system with:
- Purchase Order approvals
- Expense approvals
- Invoice approvals
- Custom approval rules
- Automated routi...

**Models** (4):

##### `account.move`

Extend Invoice with approval workflow integration.

*Inherits*: `account.move`  
*File*: `addons/custom/ipai_approvals/models/account_move.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `approval_request_id` | Many2one |  | ✓ | ipai.approval.request |
| `approval_state` | Selection |  |  |  |
| `requires_approval` | Boolean |  |  |  |

**Methods**: `action_submit_for_approval()`, `action_approve_invoice()`, `action_reject_invoice()`, `action_view_approval()`, `action_post()`  

##### `purchase.order`

Extend Purchase Order with approval workflow integration.

*Inherits*: `purchase.order`  
*File*: `addons/custom/ipai_approvals/models/purchase_order.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `approval_request_id` | Many2one |  | ✓ | ipai.approval.request |
| `approval_state` | Selection |  |  |  |
| `requires_approval` | Boolean |  |  |  |

**Methods**: `action_submit_for_approval()`, `action_approve_po()`, `action_reject_po()`, `action_view_approval()`, `button_confirm()`  

##### `hr.expense`

Extend Expense with approval workflow integration.

*Inherits*: `hr.expense`  
*File*: `addons/custom/ipai_approvals/models/hr_expense.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `approval_request_id` | Many2one |  | ✓ | ipai.approval.request |
| `approval_state` | Selection |  |  |  |

##### `hr.expense.sheet`

Extend Expense Sheet with approval workflow integration.

*Inherits*: `hr.expense.sheet`  
*File*: `addons/custom/ipai_approvals/models/hr_expense.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `approval_request_id` | Many2one |  | ✓ | ipai.approval.request |
| `approval_state` | Selection |  |  |  |
| `requires_approval` | Boolean |  |  |  |

**Methods**: `action_submit_for_approval()`, `action_approve_expense()`, `action_reject_expense()`, `action_view_approval()`, `approve_expense_sheets()`  

**Views**: 3 XML files  
**Security**: 1 ACL files  
**Data**: 1 data files  

---


### Inventory/Purchase

#### IPAI Procure

**Version**: 19.0.20251026.1  
**Author**: InsightPulseAI  
**Summary**: PR → RFQ → PO → GRN → 3WM with approvals, catalogs, rounds  
**Dependencies**: `base`, `mail`, `purchase`, `stock`, `account`, `product`, `uom`, `queue_job`, `base_tier_validation`, `report_xlsx`, `server_environment`  
**Installable**: ✓  
**Application**: ✗  

> 
    Strategic sourcing and supplier relationship management.

    Features:
    - Complete procurement cycle (PR → RFQ → PO → GRN → 3-way matching)
    - Multi-round RFQ support
    - Approval workfl...

**Models** (5):

##### `ipai.vendor.score`

*File*: `addons/custom/ipai_procure/models/vendor_score.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `vendor_id` | Many2one | ✓ |  | res.partner |
| `score_quality` | Integer |  |  |  |
| `score_on_time` | Integer |  |  |  |
| `score_cost` | Integer |  |  |  |
| `score_avg` | Float |  |  |  |

##### `ipai.rfq.round`

*File*: `addons/custom/ipai_procure/models/rfq_round.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `requisition_id` | Many2one | ✓ |  | ipai.purchase.requisition |
| `round_no` | Integer |  |  |  |
| `deadline` | Datetime |  |  |  |
| `vendor_ids` | Many2many |  |  | res.partner |
| `state` | Selection |  |  |  |

##### `ipai.purchase.requisition`

*File*: `addons/custom/ipai_procure/models/purchase_requisition.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char |  |  |  |
| `requester_id` | Many2one | ✓ |  | res.users |
| `date_requested` | Date |  |  |  |
| `state` | Selection |  |  |  |
| `line_ids` | One2many |  |  | ipai.purchase.req.line |
| `notes` | Text |  |  |  |
| `amount_total` | Monetary |  |  |  |
| `currency_id` | Many2one |  |  | res.currency |

##### `ipai.purchase.req.line`

*File*: `addons/custom/ipai_procure/models/purchase_req_line.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `requisition_id` | Many2one | ✓ |  | ipai.purchase.requisition |
| `product_id` | Many2one |  |  | product.product |
| `name` | Char |  |  |  |
| `qty` | Float |  |  |  |
| `uom_id` | Many2one |  |  | uom.uom |
| `price_unit` | Monetary |  |  |  |
| `currency_id` | Many2one |  |  | res.currency |
| `subtotal` | Monetary |  |  |  |
| `target_date` | Date |  |  |  |

##### `ipai.vendor.catalog`

*File*: `addons/custom/ipai_procure/models/vendor_catalog.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `vendor_id` | Many2one | ✓ |  | res.partner |
| `product_id` | Many2one | ✓ |  | product.product |
| `price` | Float | ✓ |  |  |
| `currency_id` | Many2one | ✓ |  | res.currency |
| `valid_from` | Date |  |  |  |
| `valid_to` | Date |  |  |  |
| `notes` | Char |  |  |  |

**Security**: 1 ACL files  
**Data**: 1 data files  

---


### Project Management

#### IPAI PPM Cost Sheets

**Version**: 19.0.1.0.0  
**Author**: InsightPulse  
**Summary**: Vendor-Privacy Cost Sheets - Epic 2 (Clarity PPM + SAP Ariba Parity)  
**Dependencies**: `ipai_core`, `project`, `hr`, `analytic`, `queue_job`  
**Installable**: ✓  
**Application**: ✗  

> 
Vendor-Privacy Cost Sheets
===========================

Project cost management with vendor privacy:
- Account Managers see: Role-based rates only
- Finance Directors see: Actual vendor costs + profi...

**Models** (1):

##### `ipai.cost.sheet`

Project cost sheet with vendor-privacy separation.

*File*: `addons/custom/ipai_ppm_costsheet/models/cost_sheet.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `code` | Char |  | ✓ |  |
| `active` | Boolean |  |  |  |
| `description` | Text |  |  |  |
| `project_id` | Many2one | ✓ |  | project.project |
| `analytic_account_id` | Many2one |  |  |  |
| `date_start` | Date | ✓ |  |  |
| `date_end` | Date |  |  |  |
| `state` | Selection | ✓ |  |  |
| `line_ids` | One2many |  |  | ipai.cost.sheet.line |
| `currency_id` | Many2one | ✓ |  | res.currency |
| `public_subtotal` | Monetary |  |  |  |
| `public_total` | Monetary |  |  |  |
| `vendor_subtotal` | Monetary |  |  |  |
| `vendor_total` | Monetary |  |  |  |
| `profit_amount` | Monetary |  |  |  |
| `profit_margin` | Float |  |  |  |
| `approval_request_id` | Many2one |  | ✓ | ipai.approval.request |
| `approval_state` | Selection |  |  |  |
| `line_count` | Integer |  |  |  |

**Methods**: `create()`, `action_activate()`, `action_complete()`, `action_cancel()`, `action_view_lines()`  


---


### Reporting

#### Superset BI Integration

**Version**: 19.0.1.0.0  
**Author**: InsightPulse AI  
**Summary**: Replace native Odoo dashboards with Superset BI analytics  
**Dependencies**: `base`, `web`  
**Installable**: ✓  
**Application**: ✗  

> 
Superset BI Integration
=======================

Replaces Odoo's built-in Dashboards module with Superset-powered analytics:

* Sales Dashboard - Real-time sales metrics and forecasting
* Finance Das...

**Data**: 1 data files  

---


### Sales/Subscriptions

#### IPAI Subscriptions

**Version**: 19.0.20251026.1  
**Author**: InsightPulseAI  
**Summary**: Recurring revenue management with MRR/ARR tracking  
**Dependencies**: `base`, `mail`, `account`, `product`, `uom`, `contract`, `contract_sale`, `contract_invoice`, `queue_job`  
**Installable**: ✓  
**Application**: ✗  

> 
    Subscription and recurring revenue management.

    Features:
    - Recurring revenue tracking (MRR/ARR)
    - Subscription lifecycle management
    - Automated invoice generation
    - Contract ...

**Models** (4):

##### `ipai.subscription.line`

*File*: `addons/custom/ipai_subscriptions/models/subscription_line.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `subscription_id` | Many2one | ✓ |  | ipai.subscription |
| `product_id` | Many2one | ✓ |  | product.product |
| `qty` | Float |  |  |  |
| `price_unit` | Monetary |  |  |  |
| `currency_id` | Many2one |  |  | res.currency |
| `billing_period` | Selection |  |  |  |
| `monthly_price` | Monetary |  |  |  |

##### `ipai.subscription`

*File*: `addons/custom/ipai_subscriptions/models/subscription.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `partner_id` | Many2one | ✓ |  | res.partner |
| `contract_id` | Many2one |  |  | contract.contract |
| `start_date` | Date | ✓ |  |  |
| `next_invoice_date` | Date |  |  |  |
| `state` | Selection |  |  |  |
| `line_ids` | One2many |  |  | ipai.subscription.line |
| `mrr` | Monetary |  |  |  |
| `currency_id` | Many2one |  |  | res.currency |

##### `ipai.usage.event`

*File*: `addons/custom/ipai_subscriptions/models/usage_event.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `subscription_id` | Many2one | ✓ |  | ipai.subscription |
| `metric` | Char | ✓ |  |  |
| `quantity` | Float | ✓ |  |  |
| `event_at` | Datetime | ✓ |  |  |

##### `ipai.dunning.step`

*File*: `addons/custom/ipai_subscriptions/models/dunning.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `day_offset` | Integer | ✓ |  |  |
| `action` | Selection |  |  |  |

**Security**: 1 ACL files  
**Data**: 2 data files  

---


### Security

#### Security Hardening

**Version**: 19.0.251026.1  
**Author**: InsightPulseAI  
**Summary**: Security hardening features for Odoo deployment  
**Dependencies**: `base`, `web`  
**Installable**: ✓  
**Application**: ✗  

> 
    Security hardening features:
    - Block database manager in production
    - Enhanced security headers
    - Audit trail enforcement
    - Security monitoring
    ...

**Views**: 1 XML files  
**Security**: 1 ACL files  

---


### Technical

#### IPAI Core

**Version**: 19.0.1.0.0  
**Author**: InsightPulseAI  
**Summary**: Core infrastructure for InsightPulse Enterprise SaaS Parity  
**Dependencies**: `base`, `mail`, `queue_job`  
**Installable**: ✓  
**Application**: ✗  

> 
IPAI Core Infrastructure
========================
Foundation module providing shared infrastructure for all IPAI enterprise modules.

Features:
* Unified approval workflow engine
* Rate policy calcul...

**Models** (10):

##### `ipai.tenant.manager`

Multi-tenancy manager for SaaS operations.

*File*: `addons/custom/ipai_core/models/tenant_manager.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `code` | Char | ✓ |  |  |
| `active` | Boolean |  |  |  |
| `description` | Text |  |  |  |
| `database_name` | Char |  |  |  |
| `database_created` | Boolean |  | ✓ |  |
| `database_size_mb` | Float |  | ✓ |  |
| `admin_user_id` | Many2one |  |  | res.users |
| `admin_email` | Char | ✓ |  |  |
| `admin_login` | Char | ✓ |  |  |
| `plan_id` | Many2one |  |  | ipai.tenant.plan |
| `state` | Selection | ✓ |  |  |
| `user_count` | Integer |  | ✓ |  |
| `storage_mb` | Float |  | ✓ |  |
| `api_calls_month` | Integer |  | ✓ |  |
| `provision_date` | Datetime |  | ✓ |  |
| `activation_date` | Datetime |  | ✓ |  |
| `termination_date` | Datetime |  | ✓ |  |
| `last_backup_date` | Datetime |  | ✓ |  |

**Methods**: `action_provision()`, `action_suspend()`, `action_reactivate()`, `action_terminate()`  

##### `ipai.tenant.plan`

Subscription plans for tenants.

*File*: `addons/custom/ipai_core/models/tenant_manager.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `sequence` | Integer |  |  |  |
| `active` | Boolean |  |  |  |
| `description` | Text |  |  |  |
| `price_monthly` | Float | ✓ |  |  |
| `currency_id` | Many2one |  |  | res.currency |
| `max_users` | Integer | ✓ |  |  |
| `max_storage_mb` | Integer | ✓ |  |  |
| `max_api_calls_month` | Integer | ✓ |  |  |
| `enable_ai_workspace` | Boolean |  |  |  |
| `enable_advanced_analytics` | Boolean |  |  |  |
| `enable_api_access` | Boolean |  |  |  |
| `tenant_count` | Integer |  |  |  |

##### `ipai.rate.policy`

Rate policy calculation framework for vendor rate bands.

*File*: `addons/custom/ipai_core/models/rate_policy.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `active` | Boolean |  |  |  |
| `description` | Text |  |  |  |
| `lookback_months` | Integer | ✓ |  |  |
| `markup_percentage` | Float | ✓ |  |  |
| `rounding_amount` | Float | ✓ |  |  |
| `percentile` | Selection | ✓ |  |  |
| `auto_update` | Boolean |  |  |  |
| `cron_id` | Many2one |  | ✓ | ir.cron |
| `last_update_date` | Datetime |  | ✓ |  |
| `last_update_user_id` | Many2one |  | ✓ | res.users |
| `update_count` | Integer |  | ✓ |  |

**Methods**: `create()`, `write()`, `unlink()`, `action_update_rates()`  

##### `ipai.rate.band`

Public rate bands calculated from vendor rates.

*File*: `addons/custom/ipai_core/models/rate_policy.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `role_id` | Many2one | ✓ |  | hr.job |
| `public_rate` | Float | ✓ |  |  |
| `vendor_rate_p50` | Float |  | ✓ |  |
| `vendor_rate_p60` | Float |  | ✓ |  |
| `vendor_rate_p75` | Float |  | ✓ |  |
| `sample_size` | Integer |  | ✓ |  |
| `last_update_date` | Datetime |  | ✓ |  |
| `last_update_policy_id` | Many2one |  | ✓ | ipai.rate.policy |
| `currency_id` | Many2one |  |  | res.currency |

##### `ipai.approval.flow`

Generic approval workflow template that can be attached to any model.

*File*: `addons/custom/ipai_core/models/approval_flow.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `model_id` | Many2one | ✓ |  | ir.model |
| `model_name` | Char |  |  |  |
| `active` | Boolean |  |  |  |
| `description` | Text |  |  |  |
| `stage_ids` | One2many |  |  | ipai.approval.stage |
| `request_ids` | One2many |  |  | ipai.approval.request |
| `parallel_execution` | Boolean |  |  |  |
| `auto_escalate` | Boolean |  |  |  |
| `default_timeout_hours` | Integer |  |  |  |
| `request_count` | Integer |  |  |  |
| `avg_approval_hours` | Float |  |  |  |

##### `ipai.approval.stage`

Individual stage in an approval workflow.

*File*: `addons/custom/ipai_core/models/approval_flow.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `flow_id` | Many2one | ✓ |  | ipai.approval.flow |
| `name` | Char | ✓ |  |  |
| `sequence` | Integer |  |  |  |
| `approver_ids` | Many2many |  |  | res.users |
| `approver_group_ids` | Many2many |  |  | res.groups |
| `timeout_hours` | Integer |  |  |  |
| `escalation_user_id` | Many2one |  |  | res.users |
| `escalation_action` | Selection | ✓ |  |  |
| `condition_field_id` | Many2one |  |  | ir.model.fields |
| `condition_operator` | Selection |  |  |  |
| `condition_value` | Char |  |  |  |

**Methods**: `get_approvers()`  

##### `ipai.approval.request`

Approval request instance for a specific record.

*File*: `addons/custom/ipai_core/models/approval_flow.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char |  |  |  |
| `flow_id` | Many2one | ✓ |  | ipai.approval.flow |
| `model_id` | Many2one |  |  |  |
| `model_name` | Char |  |  |  |
| `res_id` | Integer | ✓ |  |  |
| `res_model_id` | Many2one |  |  | ir.model |
| `state` | Selection | ✓ |  |  |
| `current_stage_id` | Many2one |  |  | ipai.approval.stage |
| `log_ids` | One2many |  |  | ipai.approval.log |
| `create_date` | Datetime |  | ✓ |  |
| `start_date` | Datetime |  | ✓ |  |
| `complete_date` | Datetime |  | ✓ |  |
| `duration_hours` | Float |  |  |  |

**Methods**: `action_submit()`, `action_approve()`, `action_reject()`, `action_cancel()`  

##### `ipai.approval.log`

Audit trail for approval actions.

*File*: `addons/custom/ipai_core/models/approval_flow.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `request_id` | Many2one | ✓ |  | ipai.approval.request |
| `stage_id` | Many2one | ✓ |  | ipai.approval.stage |
| `user_id` | Many2one | ✓ |  | res.users |
| `action` | Selection | ✓ |  |  |
| `notes` | Text |  |  |  |
| `create_date` | Datetime |  | ✓ |  |

##### `ipai.ai.workspace`

AI-powered workspace connector for knowledge management.

*File*: `addons/custom/ipai_core/models/ai_workspace.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `active` | Boolean |  |  |  |
| `description` | Text |  |  |  |
| `res_model` | Char |  |  |  |
| `res_id` | Integer |  |  |  |
| `enable_vector_search` | Boolean |  |  |  |
| `enable_llm_chat` | Boolean |  |  |  |
| `llm_provider` | Selection |  |  |  |
| `page_count` | Integer |  |  |  |
| `query_count` | Integer |  |  |  |
| `last_query_date` | Datetime |  | ✓ |  |

##### `ipai.ai.workspace.mixin`

Mixin to add AI workspace capability to any model.

*File*: `addons/custom/ipai_core/models/ai_workspace.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `ai_workspace_id` | Many2one |  |  | ipai.ai.workspace |

**Methods**: `action_create_workspace()`, `action_open_workspace()`  

**Views**: 1 XML files  
**Security**: 1 ACL files  
**Data**: 1 data files  

---


### Tools

#### Apps Admin Enhancements

**Version**: 19.0.251026.1  
**Author**: InsightPulseAI  
**Summary**: Enhanced Apps management with source tracking and accessibility  
**Dependencies**: `base`  
**Installable**: ✓  
**Application**: ✗  

> 
    Enhanced Apps interface with:
    - Module source tracking (Odoo/OCA/Custom)
    - Accessibility status (module present on disk)
    - Effective website URLs for your domain
    - Automatic modul...

**Models** (1):

##### `ir.module.module`

*Inherits*: `ir.module.module`  
*File*: `addons/custom/apps_admin_enhancements/models/ir_module.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `source` | Selection |  |  |  |
| `is_accessible` | Boolean |  |  |  |
| `website_effective` | Char |  |  |  |

**Views**: 1 XML files  
**Security**: 1 ACL files  
**Data**: 1 data files  

---

#### Pulser Hub Sync

**Version**: 19.0.1.0.0  
**Author**: InsightPulse AI  
**Summary**: GitHub App integration for Pulser Hub webhook and OAuth  
**Dependencies**: `base`, `web`, `queue_job`  
**Installable**: ✓  
**Application**: ✗  

> 
GitHub App Integration
======================
This module provides integration with GitHub App "pulser-hub" for:
* OAuth 2.0 authentication flow
* Webhook event processing
* Installation token manage...

**Models** (2):

##### `github.webhook.event`

*File*: `addons/custom/pulser_hub_sync/models/github_webhook_event.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char |  |  |  |
| `event_type` | Char | ✓ |  |  |
| `delivery_id` | Char | ✓ |  |  |
| `installation_id` | Char |  |  |  |
| `repository` | Char |  |  |  |
| `sender` | Char |  |  |  |
| `payload` | Text |  |  |  |
| `processed` | Boolean |  |  |  |
| `processing_error` | Text |  |  |  |
| `create_date` | Datetime |  | ✓ |  |

**Methods**: `action_reprocess()`, `action_view_payload()`, `process_webhook_async()`  

##### `github.integration`

*File*: `addons/custom/pulser_hub_sync/models/github_integration.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char |  |  |  |
| `app_id` | Char |  | ✓ |  |
| `installation_id` | Char | ✓ |  |  |
| `account_login` | Char | ✓ |  |  |
| `repository_selection` | Selection |  |  |  |
| `access_token` | Char |  |  |  |
| `installation_token` | Char |  |  |  |
| `token_expires_at` | Datetime |  |  |  |
| `webhook_secret` | Char |  |  |  |
| `last_sync` | Datetime |  |  |  |
| `active` | Boolean |  |  |  |
| `webhook_count` | Integer |  |  |  |

**Methods**: `refresh_installation_token()`, `action_view_webhooks()`, `create_issue()`, `commit_file()`, `get_integration_for_repo()`  

**Views**: 1 XML files  
**Security**: 1 ACL files  

---

#### Odoo Knowledge Agent

**Version**: 19.0.1.0.0  
**Author**: InsightPulse AI  
**Summary**: Forum scraper and error prevention for Odoo custom modules  
**Dependencies**: `base`  
**Installable**: ✓  
**Application**: ✗  

> 
Odoo Knowledge Agent
====================

Scrapes solved issues from Odoo forum to build:
- Error prevention guardrails
- Auto-fix patches
- Knowledge base for troubleshooting

Features:
- Automated...

**Models** (2):

##### `odoo.knowledge.agent`

Odoo Knowledge Agent - Forum scraper and error prevention

*File*: `addons/custom/odoo_knowledge_agent/models/knowledge_agent.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `name` | Char | ✓ |  |  |
| `state` | Selection |  |  |  |
| `scrape_date` | Datetime |  |  |  |
| `pages_scraped` | Integer |  |  |  |
| `issues_found` | Integer |  |  |  |
| `output_file` | Char |  |  |  |
| `error_message` | Text |  |  |  |
| `log_ids` | One2many |  |  | odoo.knowledge.agent.log |

**Methods**: `action_run_scraper()`, `cron_scrape_forum()`  

##### `odoo.knowledge.agent.log`

Log entries for knowledge agent scraping

*File*: `addons/custom/odoo_knowledge_agent/models/knowledge_agent.py`  

**Fields**:

| Name | Type | Required | Readonly | Relation |
|------|------|----------|----------|----------|
| `agent_id` | Many2one | ✓ |  | odoo.knowledge.agent |
| `message` | Text | ✓ |  |  |
| `level` | Selection |  |  |  |
| `create_date` | Datetime |  |  |  |

**Views**: 1 XML files  
**Security**: 1 ACL files  
**Data**: 1 data files  

---


## 🔍 Model Index

| Model | Module | Fields | Methods |
|-------|--------|--------|--------|
| `account.move` | IPAI Approvals | 3 | 5 |
| `finance.bir.compliance.task` | Finance SSC Month-End Closing | 23 | 5 |
| `finance.closing.period` | Finance SSC Month-End Closing | 18 | 7 |
| `finance.closing.task` | Finance SSC Month-End Closing | 25 | 7 |
| `finance.closing.task.template` | Finance SSC Month-End Closing | 9 | 0 |
| `github.integration` | Pulser Hub Sync | 12 | 5 |
| `github.webhook.event` | Pulser Hub Sync | 10 | 3 |
| `hr.expense` | IPAI Approvals | 2 | 0 |
| `hr.expense.sheet` | IPAI Approvals | 3 | 5 |
| `ipai.ai.workspace` | IPAI Core | 11 | 0 |
| `ipai.ai.workspace.mixin` | IPAI Core | 1 | 2 |
| `ipai.approval.flow` | IPAI Core | 12 | 0 |
| `ipai.approval.log` | IPAI Core | 6 | 0 |
| `ipai.approval.request` | IPAI Core | 13 | 4 |
| `ipai.approval.stage` | IPAI Core | 11 | 1 |
| `ipai.cost.sheet` | IPAI PPM Cost Sheets | 20 | 5 |
| `ipai.dunning.step` | IPAI Subscriptions | 3 | 0 |
| `ipai.expense.advance` | IPAI Expense | 7 | 0 |
| `ipai.expense.ocr.audit` | IPAI Expense | 4 | 0 |
| `ipai.expense.policy` | IPAI Expense | 5 | 0 |
| `ipai.purchase.req.line` | IPAI Procure | 9 | 0 |
| `ipai.purchase.requisition` | IPAI Procure | 8 | 0 |
| `ipai.rate.band` | IPAI Core | 9 | 0 |
| `ipai.rate.policy` | IPAI Core | 12 | 4 |
| `ipai.rfq.round` | IPAI Procure | 5 | 0 |
| `ipai.subscription` | IPAI Subscriptions | 9 | 0 |
| `ipai.subscription.line` | IPAI Subscriptions | 7 | 0 |
| `ipai.tenant.manager` | IPAI Core | 19 | 4 |
| `ipai.tenant.plan` | IPAI Core | 13 | 0 |
| `ipai.usage.event` | IPAI Subscriptions | 4 | 0 |
| `ipai.vendor.catalog` | IPAI Procure | 7 | 0 |
| `ipai.vendor.score` | IPAI Procure | 5 | 0 |
| `ir.module.module` | Apps Admin Enhancements | 3 | 0 |
| `microservices.config` | Microservices Connector | 12 | 1 |
| `microservices.health.log` | Microservices Connector | 7 | 1 |
| `microservices.service` | Microservices Connector | 6 | 1 |
| `odoo.knowledge.agent` | Odoo Knowledge Agent | 8 | 2 |
| `odoo.knowledge.agent.log` | Odoo Knowledge Agent | 4 | 0 |
| `purchase.order` | IPAI Approvals | 3 | 5 |
| `superset.config` | Superset Connector | 3 | 0 |
| `superset.config` | Superset Connector | 8 | 1 |
| `superset.dashboard` | Superset Connector | 6 | 0 |
| `superset.token` | Superset Connector | 12 | 6 |
| `tableau.config` | Tableau Connector | 9 | 1 |
| `tableau.dashboard` | Tableau Connector | 7 | 1 |

---

*Generated by InsightPulse Odoo Docs Generator*
