# Feature Inventory
Generated: 2025-11-04T04:54:27.784518+00:00Z

| Module | Source | Version | State | Summary | Depends | Path |
|---|---|---|---|---|---|---|
| apps_admin_enhancements | Custom | 19.0.251026.1 | unknown | Enhanced Apps management with source tracking and accessibility | base | addons/custom/apps_admin_enhancements |
| github_integration | Custom | 1.0.0 | unknown | GitHub webhook and OAuth integration via pulser-hub app | base,project,web | addons/insightpulse/ops/github_integration |
| insightpulse_app_sources | Custom | 19.0.1.0.0 | unknown | Display addon sources (OCA, Custom, Community) in Apps list | base | addons/insightpulse/insightpulse_app_sources |
| ipai_approvals | Custom | 19.0.1.0.0 | unknown | Unified Approvals Engine - Epic 1 (Clarity PPM Parity) | ipai_core,purchase,hr_expense,account,queue_job | addons/custom/ipai_approvals |
| ipai_ariba_cxml | Custom | 19.0.1.0.0 | unknown | SAP Ariba cXML (PO/Invoice) → purchase/account.move | base,purchase,account | odoo_addons/ipai_ariba_cxml |
| ipai_clarity_ppm_sync | Custom | 19.0.1.0.0 | unknown | Clarity PPM projects/tasks/timesheets → Odoo | base,project,hr_timesheet | odoo_addons/ipai_clarity_ppm_sync |
| ipai_concur_bridge | Custom | 19.0.1.0.0 | unknown | SAP Concur SAE → Odoo hr.expense & bank statements | base,hr_expense,account | odoo_addons/ipai_concur_bridge |
| ipai_consent_manager | Custom | 19.0.1.0.0 | unknown | GDPR email opt-in/out + policy logs | base,mail | odoo_addons/ipai_consent_manager |
| ipai_core | Custom | 19.0.1.0.0 | unknown | Core infrastructure for InsightPulse Enterprise SaaS Parity | base,mail,queue_job | addons/custom/ipai_core |
| ipai_doc_ai | Custom | 19.0.1.0.0 | unknown | OCR → entity map → Odoo drafts | base,mail | odoo_addons/ipai_doc_ai |
| ipai_expense | Custom | 19.0.20251026.1 | unknown | Cash advance lifecycle, expense policy, OCR audit | base,mail,hr,hr_expense,account,report_xlsx,queue_job,server_environment | addons/custom/ipai_expense |
| ipai_ppm | Custom | 19.0.1.0.0 | unknown | Program/Project/Budget/Risk Management | ipai_core,project,account | addons/insightpulse/finance/ipai_ppm |
| ipai_ppm_costsheet | Custom | 19.0.1.0.0 | unknown | Vendor-Privacy Cost Sheets - Epic 2 (Clarity PPM + SAP Ariba Parity) | ipai_core,project,hr,analytic,queue_job | addons/custom/ipai_ppm_costsheet |
| ipai_procure | Custom | 19.0.20251026.1 | unknown | PR → RFQ → PO → GRN → 3WM with approvals, catalogs, rounds | base,mail,purchase,stock,account,product,uom,queue_job,base_tier_validation,report_xlsx,server_environment | addons/custom/ipai_procure |
| ipai_rate_policy | Custom | 19.0.1.0.0 | unknown | Automated rate calculation with P60 + 25% markup | ipai_core,hr,account | addons/insightpulse/finance/ipai_rate_policy |
| ipai_saas_ops | Custom | 19.0.1.0.0 | unknown | Self-service tenant creation and automated backups | ipai_core,base | addons/insightpulse/ops/ipai_saas_ops |
| ipai_salesforce_sync | Custom | 19.0.1.0.0 | unknown | Salesforce Accounts/Contacts/Leads → Odoo CRM | base,crm | odoo_addons/ipai_salesforce_sync |
| ipai_statement_engine | Custom | 19.0.1.0.0 | unknown | Statements of Account + email dispatch | base,account,mail | odoo_addons/ipai_statement_engine |
| ipai_subscriptions | Custom | 19.0.20251026.1 | unknown | Recurring revenue management with MRR/ARR tracking | base,mail,account,product,uom,contract,contract_sale,contract_invoice,queue_job | addons/custom/ipai_subscriptions |
| ipai_visual_gate | Custom | 19.0.1.0.0 | unknown | Percy-style visual snapshot gating | base | odoo_addons/ipai_visual_gate |
| mcp_integration | Custom | 19.0.1.0.0 | unknown | Model Context Protocol integration for Odoo workflows | base,web | addons/mcp_integration |
| microservices_connector | Custom | 19.0.251027.1 | unknown | Integration with OCR, LLM, and Agent microservices | base,web | addons/custom/microservices_connector |
| odoo_knowledge_agent | Custom | 19.0.1.0.0 | unknown | Forum scraper and error prevention for Odoo custom modules | base | addons/custom/odoo_knowledge_agent |
| pulser_hub_sync | Custom | 19.0.1.0.0 | unknown | GitHub App integration for Pulser Hub webhook and OAuth | base,web,queue_job | addons/custom/pulser_hub_sync |
| pulser_webhook | Custom | 19.0.1.0.2 | unknown | Triggers GitHub repository_dispatch (git-ops) from Odoo | base,project,sale_management,account,hr_expense,purchase | custom_addons/pulser_webhook |
| security_hardening | Custom | 19.0.251026.1 | unknown | Security hardening features for Odoo deployment | base,web | addons/custom/security_hardening |
| superset_connector | Custom | 19.0.251027.1 | unknown | Apache Superset integration for Odoo | base,web | addons/custom/superset_connector |
| superset_menu | Custom | 19.0.1.0.0 | unknown | Replace native Odoo dashboards with Superset BI analytics | base,web | addons/custom/superset_menu |
| tableau_connector | Custom | 19.0.251026.1 | unknown | Tableau analytics integration for Odoo | base,web | addons/custom/tableau_connector |
