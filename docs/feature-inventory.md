# Feature Inventory
Generated: 2025-11-14T13:37:58.101584+00:00Z

| Module | Source | Version | State | Summary | Depends | Path |
|---|---|---|---|---|---|---|
| apps_admin_enhancements | Custom | 18.0.251026.1 | unknown | Enhanced Apps management with source tracking and accessibility | base | addons/custom/apps_admin_enhancements |
| finance_ssc_closing | Custom | 18.0.1.0.0 | unknown | Month-end closing checklist and BIR compliance tracking for Finance Shared Service Center | base,account,account_accountant,project,mail,hr,web | addons/custom/finance_ssc_closing |
| github_integration | Custom | 1.0.0 | unknown | GitHub webhook and OAuth integration via pulser-hub app | base,project,web | addons/insightpulse/ops/github_integration |
| hr_offboarding_clearance | Custom | 18.0.1.0.0 | unknown | Employee offboarding clearance workflow with BIR compliance | hr,hr_contract,mail,portal | custom_addons/hr_offboarding_clearance |
| insightpulse_app_sources | Custom | 18.0.1.0.0 | unknown | Display addon sources (OCA, Custom, Community) in Apps list | base | addons/insightpulse/insightpulse_app_sources |
| ip_expense_mvp | Custom | 18.0.1.0.0 | unknown | Expense management minimum viable product | base,account | addons/ip_expense_mvp |
| ip_expense_mvp | Custom | 0.1.0 | unknown | Mobile receipt capture + OCR, cash advance/liquidation scaffolds, admin dashboard | base,web,hr,hr_expense | custom_addons/ip_expense_mvp |
| ip_superset_integration | Custom | 18.0.1.0.0 | unknown | Apache Superset BI dashboards integration - Tableau alternative | base,web | custom_addons/ip_superset_integration |
| ipai_agent | Custom | 1.0.0 | unknown | AI-powered chatbot for Odoo Discuss with automation capabilities | base,mail,hr_expense,account | addons/ipai_agent |
| ipai_agent_hybrid | Custom | 18.0.1.0.0 | unknown | Odoo Studio × Notion Agent - Hybrid no-code + AI orchestration | base,web,mail,project,calendar | addons/ipai_agent_hybrid |
| ipai_approvals | Custom | 18.0.1.0.0 | unknown | Unified Approvals Engine - Epic 1 (Clarity PPM Parity) | ipai_core,purchase,hr_expense,account,queue_job | addons/custom/ipai_approvals |
| ipai_ariba_cxml | Custom | 19.0.1.0.0 | unknown | SAP Ariba cXML (PO/Invoice) → purchase/account.move | base,purchase,account | odoo_addons/ipai_ariba_cxml |
| ipai_audit_discovery | Custom | 19.0.1.0.0 | unknown | Immutable audit trail, legal hold, eDiscovery export | ipai_chat_core,auditlog | odoo_addons/ipai_audit_discovery |
| ipai_bir_compliance | Custom | 18.0.1.0.0 | unknown | Philippine BIR Tax Forms Automation (1601-C, 2550Q, 1702-RT) | base,account,account_accountant,l10n_ph | odoo_addons/ipai_bir_compliance |
| ipai_bir_compliance | Custom | 18.0.1.0.0 | unknown | Philippine BIR compliance (Forms 2307, 2316, 1601-C, 1702-RT) | base,account | addons/ipai_bir_compliance |
| ipai_branding | Custom | 18.0.1.0.0 | unknown | InsightPulse AI branding and customizations | base,web | addons/ipai_branding |
| ipai_chat_core | Custom | 19.0.1.0.0 | unknown | Enterprise-grade chat foundation - RBAC, channel policies, thread UX | mail,base,web | odoo_addons/ipai_chat_core |
| ipai_clarity_ppm_sync | Custom | 19.0.1.0.0 | unknown | Clarity PPM projects/tasks/timesheets → Odoo | base,project,hr_timesheet | odoo_addons/ipai_clarity_ppm_sync |
| ipai_concur_bridge | Custom | 19.0.1.0.0 | unknown | SAP Concur SAE → Odoo hr.expense & bank statements | base,hr_expense,account | odoo_addons/ipai_concur_bridge |
| ipai_connect_external | Custom | 19.0.1.0.0 | unknown | Guest/partner collaboration spaces (Slack Connect equivalent) | ipai_chat_core,portal | odoo_addons/ipai_connect_external |
| ipai_consent_manager | Custom | 19.0.1.0.0 | unknown | GDPR email opt-in/out + policy logs | base,mail | odoo_addons/ipai_consent_manager |
| ipai_core | Custom | 18.0.1.0.0 | unknown | Core infrastructure for InsightPulse Enterprise SaaS Parity | base,mail,queue_job | addons/custom/ipai_core |
| ipai_dlp_guard | Custom | 19.0.1.0.0 | unknown | Data Loss Prevention - pattern detection, quarantine, review | ipai_chat_core | odoo_addons/ipai_dlp_guard |
| ipai_doc_ai | Custom | 19.0.1.0.0 | unknown | OCR → entity map → Odoo drafts | base,mail | odoo_addons/ipai_doc_ai |
| ipai_expense | Custom | 18.0.20251026.1 | unknown | Cash advance lifecycle, expense policy, OCR audit | base,mail,hr,hr_expense,account,report_xlsx,queue_job,server_environment | addons/custom/ipai_expense |
| ipai_files_spaces | Custom | 19.0.1.0.0 | unknown | S3/DigitalOcean Spaces integration for large files | base | odoo_addons/ipai_files_spaces |
| ipai_huddles_webrtc | Custom | 19.0.1.0.0 | unknown | Jitsi integration for audio/video calls and huddles | ipai_chat_core | odoo_addons/ipai_huddles_webrtc |
| ipai_mattermost_bridge | Custom | 1.0.0 | unknown | Webhook ingestion for GitHub/Jira/ServiceNow into Odoo | base | custom_addons/ipai_mattermost_bridge |
| ipai_ppm | Custom | 18.0.1.0.0 | unknown | Program/Project/Budget/Risk Management | ipai_core,project,account | addons/insightpulse/finance/ipai_ppm |
| ipai_ppm_costsheet | Custom | 18.0.1.0.0 | unknown | Vendor-Privacy Cost Sheets - Epic 2 (Clarity PPM + SAP Ariba Parity) | ipai_core,project,hr,analytic,queue_job | addons/custom/ipai_ppm_costsheet |
| ipai_procure | Custom | 18.0.20251026.1 | unknown | PR → RFQ → PO → GRN → 3WM with approvals, catalogs, rounds | base,mail,purchase,stock,account,product,uom,queue_job,base_tier_validation,report_xlsx,server_environment | addons/custom/ipai_procure |
| ipai_rate_policy | Custom | 18.0.1.0.0 | unknown | Automated rate calculation with P60 + 25% markup | ipai_core,hr,account | addons/insightpulse/finance/ipai_rate_policy |
| ipai_retention_policies | Custom | 19.0.1.0.0 | unknown | Data retention, auto-purge, legal hold exceptions | ipai_chat_core,ipai_audit_discovery | odoo_addons/ipai_retention_policies |
| ipai_saas_ops | Custom | 18.0.1.0.0 | unknown | Self-service tenant creation and automated backups | ipai_core,base | addons/insightpulse/ops/ipai_saas_ops |
| ipai_salesforce_sync | Custom | 19.0.1.0.0 | unknown | Salesforce Accounts/Contacts/Leads → Odoo CRM | base,crm | odoo_addons/ipai_salesforce_sync |
| ipai_scim_provisioner | Custom | 19.0.1.0.0 | unknown | SCIM 2.0 user lifecycle management - provision, deprovision, sync | base,base_rest,base_rest_auth_jwt | odoo_addons/ipai_scim_provisioner |
| ipai_search_vector | Custom | 19.0.1.0.0 | unknown | pgvector-based semantic search for messages and files | ipai_chat_core | odoo_addons/ipai_search_vector |
| ipai_slack_bridge | Custom | 19.0.1.0.0 | unknown | Bidirectional Slack integration - OAuth, Events API, message sync | ipai_chat_core,base_rest | odoo_addons/ipai_slack_bridge |
| ipai_statement_engine | Custom | 19.0.1.0.0 | unknown | Statements of Account + email dispatch | base,account,mail | odoo_addons/ipai_statement_engine |
| ipai_subscriptions | Custom | 18.0.20251026.1 | unknown | Recurring revenue management with MRR/ARR tracking | base,mail,account,product,uom,contract,contract_sale,contract_invoice,queue_job | addons/custom/ipai_subscriptions |
| ipai_te_seed | Custom | 1.0.0 | unknown | IPAI seed: T&E accounts, journals, categories, MIS KPIs | account,hr_expense,mis_builder | custom_addons/ipai_te_seed |
| ipai_visual_gate | Custom | 19.0.1.0.0 | unknown | Percy-style visual snapshot gating | base | odoo_addons/ipai_visual_gate |
| ipai_workflow_bot | Custom | 19.0.1.0.0 | unknown | Slash commands, interactive dialogs, workflow automation | ipai_chat_core,base_automation | odoo_addons/ipai_workflow_bot |
| mcp_integration | Custom | 18.0.1.0.0 | unknown | Model Context Protocol integration for Odoo workflows | base,web | addons/mcp_integration |
| microservices_connector | Custom | 18.0.251027.1 | unknown | Integration with OCR, LLM, and Agent microservices | base,web | addons/custom/microservices_connector |
| odoo_knowledge_agent | Custom | 18.0.1.0.0 | unknown | Forum scraper and error prevention for Odoo custom modules | base | addons/custom/odoo_knowledge_agent |
| pulser_hub_sync | Custom | 18.0.1.0.0 | unknown | GitHub App integration for Pulser Hub webhook and OAuth | base,web,queue_job | addons/custom/pulser_hub_sync |
| pulser_webhook | Custom | 19.0.1.0.2 | unknown | Triggers GitHub repository_dispatch (git-ops) from Odoo | base,project,sale_management,account,hr_expense,purchase | custom_addons/pulser_webhook |
| security_hardening | Custom | 18.0.251026.1 | unknown | Security hardening features for Odoo deployment | base,web | addons/custom/security_hardening |
| slack_bridge | Custom | 18.0.1.0.0 | unknown | Slack integration for InsightPulse AI agencies | base,mail | addons/slack_bridge |
| superset_connector | Custom | 18.0.251027.1 | unknown | Apache Superset integration for Odoo | base,web | addons/custom/superset_connector |
| superset_menu | Custom | 18.0.1.0.0 | unknown | Replace native Odoo dashboards with Superset BI analytics | base,web | addons/custom/superset_menu |
| tableau_connector | Custom | 18.0.251026.1 | unknown | Tableau analytics integration for Odoo | base,web | addons/custom/tableau_connector |
