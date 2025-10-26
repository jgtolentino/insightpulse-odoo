-- Performance Indexes for InsightPulse Odoo
-- Run these SQL commands to improve performance

-- Index for queue_job table (if queue_job module is installed)
CREATE INDEX IF NOT EXISTS idx_queue_job_state_date_enqueued 
ON queue_job (state, date_enqueued);

-- Index for microservices health logs
CREATE INDEX IF NOT EXISTS idx_microservices_health_log_create_date 
ON microservices_health_log (create_date);

CREATE INDEX IF NOT EXISTS idx_microservices_health_log_status 
ON microservices_health_log (status);

-- Index for connector audit tables (if they exist)
-- Replace 'connector_audit_table' with actual table names
-- CREATE INDEX IF NOT EXISTS idx_connector_audit_create_date 
-- ON connector_audit_table (create_date);

-- Index for connector audit status
-- CREATE INDEX IF NOT EXISTS idx_connector_audit_status 
-- ON connector_audit_table (status);

-- Index for ir_module_module for faster module queries
CREATE INDEX IF NOT EXISTS idx_ir_module_module_name_state 
ON ir_module_module (name, state);

-- Index for ir_cron for faster cron job lookups
CREATE INDEX IF NOT EXISTS idx_ir_cron_active_nextcall 
ON ir_cron (active, nextcall);

-- Index for ir_config_parameter for faster config lookups
CREATE INDEX IF NOT EXISTS idx_ir_config_parameter_key 
ON ir_config_parameter (key);

-- Index for mail_message for better performance
CREATE INDEX IF NOT EXISTS idx_mail_message_model_res_id 
ON mail_message (model, res_id);

-- Index for ir_attachment for faster file lookups
CREATE INDEX IF NOT EXISTS idx_ir_attachment_res_model_res_id 
ON ir_attachment (res_model, res_id);

-- Index for res_users for faster user lookups
CREATE INDEX IF NOT EXISTS idx_res_users_login 
ON res_users (login);

-- Index for res_partner for faster partner lookups
CREATE INDEX IF NOT EXISTS idx_res_partner_name 
ON res_partner (name);

-- Index for account_move for faster invoice lookups
CREATE INDEX IF NOT EXISTS idx_account_move_date_state 
ON account_move (date, state);

-- Index for stock_move for faster inventory lookups
CREATE INDEX IF NOT EXISTS idx_stock_move_date_state 
ON stock_move (date, state);

-- Index for project_task for faster task lookups
CREATE INDEX IF NOT EXISTS idx_project_task_date_deadline 
ON project_task (date_deadline);

-- Index for helpdesk_ticket for faster ticket lookups
CREATE INDEX IF NOT EXISTS idx_helpdesk_ticket_create_date 
ON helpdesk_ticket (create_date);

-- Index for website_visitor for faster analytics
CREATE INDEX IF NOT EXISTS idx_website_visitor_create_date 
ON website_visitor (create_date);

-- Index for sale_order for faster sales lookups
CREATE INDEX IF NOT EXISTS idx_sale_order_date_order_state 
ON sale_order (date_order, state);

-- Index for purchase_order for faster purchase lookups
CREATE INDEX IF NOT EXISTS idx_purchase_order_date_order_state 
ON purchase_order (date_order, state);

-- Index for hr_attendance for faster attendance lookups
CREATE INDEX IF NOT EXISTS idx_hr_attendance_check_in 
ON hr_attendance (check_in);

-- Index for calendar_event for faster event lookups
CREATE INDEX IF NOT EXISTS idx_calendar_event_start 
ON calendar_event (start);

-- Index for mail_followers for faster follower lookups
CREATE INDEX IF NOT EXISTS idx_mail_followers_res_model_res_id 
ON mail_followers (res_model, res_id);

-- Index for mail_notification for faster notification lookups
CREATE INDEX IF NOT EXISTS idx_mail_notification_is_read 
ON mail_notification (is_read);

-- Index for base_automation for faster automation lookups
CREATE INDEX IF NOT EXISTS idx_base_automation_active 
ON base_automation (active);

-- Index for ir_actions_server for faster action lookups
CREATE INDEX IF NOT EXISTS idx_ir_actions_server_state 
ON ir_actions_server (state);

-- Index for ir_logging for faster log analysis
CREATE INDEX IF NOT EXISTS idx_ir_logging_create_date 
ON ir_logging (create_date);

-- Index for ir_translation for faster translation lookups
CREATE INDEX IF NOT EXISTS idx_ir_translation_lang 
ON ir_translation (lang);

-- Index for ir_model_fields for faster field lookups
CREATE INDEX IF NOT EXISTS idx_ir_model_fields_model_id 
ON ir_model_fields (model_id);

-- Index for ir_model for faster model lookups
CREATE INDEX IF NOT EXISTS idx_ir_model_model 
ON ir_model (model);

-- Index for ir_ui_view for faster view lookups
CREATE INDEX IF NOT EXISTS idx_ir_ui_view_model 
ON ir_ui_view (model);

-- Index for ir_rule for faster rule lookups
CREATE INDEX IF NOT EXISTS idx_ir_rule_model_id 
ON ir_rule (model_id);

-- Index for res_groups for faster group lookups
CREATE INDEX IF NOT EXISTS idx_res_groups_name 
ON res_groups (name);

-- Index for res_company for faster company lookups
CREATE INDEX IF NOT EXISTS idx_res_company_name 
ON res_company (name);

-- Index for res_country for faster country lookups
CREATE INDEX IF NOT EXISTS idx_res_country_name 
ON res_country (name);

-- Index for res_currency for faster currency lookups
CREATE INDEX IF NOT EXISTS idx_res_currency_name 
ON res_currency (name);

-- Index for res_lang for faster language lookups
CREATE INDEX IF NOT EXISTS idx_res_lang_code 
ON res_lang (code);

-- Index for website for faster website lookups
CREATE INDEX IF NOT EXISTS idx_website_name 
ON website (name);

-- Index for website_page for faster page lookups
CREATE INDEX IF NOT EXISTS idx_website_page_url 
ON website_page (url);

-- Index for website_menu for faster menu lookups
CREATE INDEX IF NOT EXISTS idx_website_menu_parent_id 
ON website_menu (parent_id);

-- Index for product_template for faster product lookups
CREATE INDEX IF NOT EXISTS idx_product_template_name 
ON product_template (name);

-- Index for product_product for faster variant lookups
CREATE INDEX IF NOT EXISTS idx_product_product_default_code 
ON product_product (default_code);

-- Index for product_category for faster category lookups
CREATE INDEX IF NOT EXISTS idx_product_category_name 
ON product_category (name);

-- Index for uom_uom for faster unit lookups
CREATE INDEX IF NOT EXISTS idx_uom_uom_name 
ON uom_uom (name);

-- Index for uom_category for faster category lookups
CREATE INDEX IF NOT EXISTS idx_uom_category_name 
ON uom_category (name);

-- Index for account_account for faster account lookups
CREATE INDEX IF NOT EXISTS idx_account_account_code 
ON account_account (code);

-- Index for account_journal for faster journal lookups
CREATE INDEX IF NOT EXISTS idx_account_journal_name 
ON account_journal (name);

-- Index for account_tax for faster tax lookups
CREATE INDEX IF NOT EXISTS idx_account_tax_name 
ON account_tax (name);

-- Index for account_analytic_account for faster analytic lookups
CREATE INDEX IF NOT EXISTS idx_account_analytic_account_name 
ON account_analytic_account (name);

-- Index for account_analytic_line for faster analytic line lookups
CREATE INDEX IF NOT EXISTS idx_account_analytic_line_date 
ON account_analytic_line (date);

-- Index for stock_location for faster location lookups
CREATE INDEX IF NOT EXISTS idx_stock_location_name 
ON stock_location (name);

-- Index for stock_picking for faster picking lookups
CREATE INDEX IF NOT EXISTS idx_stock_picking_date_done 
ON stock_picking (date_done);

-- Index for stock_quant for faster quant lookups
CREATE INDEX IF NOT EXISTS idx_stock_quant_location_id 
ON stock_quant (location_id);

-- Index for stock_valuation_layer for faster valuation lookups
CREATE INDEX IF NOT EXISTS idx_stock_valuation_layer_create_date 
ON stock_valuation_layer (create_date);

-- Index for mrp_production for faster production lookups
CREATE INDEX IF NOT EXISTS idx_mrp_production_date_planned_start 
ON mrp_production (date_planned_start);

-- Index for mrp_bom for faster BOM lookups
CREATE INDEX IF NOT EXISTS idx_mrp_bom_product_tmpl_id 
ON mrp_bom (product_tmpl_id);

-- Index for quality_check for faster quality lookups
CREATE INDEX IF NOT EXISTS idx_quality_check_create_date 
ON quality_check (create_date);

-- Index for maintenance_equipment for faster equipment lookups
CREATE INDEX IF NOT EXISTS idx_maintenance_equipment_name 
ON maintenance_equipment (name);

-- Index for maintenance_request for faster request lookups
CREATE INDEX IF NOT EXISTS idx_maintenance_request_create_date 
ON maintenance_request (create_date);

-- Index for fleet_vehicle for faster vehicle lookups
CREATE INDEX IF NOT EXISTS idx_fleet_vehicle_license_plate 
ON fleet_vehicle (license_plate);

-- Index for fleet_vehicle_log_services for faster service lookups
CREATE INDEX IF NOT EXISTS idx_fleet_vehicle_log_services_date 
ON fleet_vehicle_log_services (date);

-- Index for crm_lead for faster lead lookups
CREATE INDEX IF NOT EXISTS idx_crm_lead_create_date 
ON crm_lead (create_date);

-- Index for crm_stage for faster stage lookups
CREATE INDEX IF NOT EXISTS idx_crm_stage_name 
ON crm_stage (name);

-- Index for crm_team for faster team lookups
CREATE INDEX IF NOT EXISTS idx_crm_team_name 
ON crm_team (name);

-- Index for marketing_campaign for faster campaign lookups
CREATE INDEX IF NOT EXISTS idx_marketing_campaign_name 
ON marketing_campaign (name);

-- Index for marketing_activity for faster activity lookups
CREATE INDEX IF NOT EXISTS idx_marketing_activity_create_date 
ON marketing_activity (create_date);

-- Index for marketing_trace for faster trace lookups
CREATE INDEX IF NOT EXISTS idx_marketing_trace_create_date 
ON marketing_trace (create_date);

-- Index for event_event for faster event lookups
CREATE INDEX IF NOT EXISTS idx_event_event_date_begin 
ON event_event (date_begin);

-- Index for event_registration for faster registration lookups
CREATE INDEX IF NOT EXISTS idx_event_registration_create_date 
ON event_registration (create_date);

-- Index for survey_survey for faster survey lookups
CREATE INDEX IF NOT EXISTS idx_survey_survey_title 
ON survey_survey (title);

-- Index for survey_user_input for faster input lookups
CREATE INDEX IF NOT EXISTS idx_survey_user_input_create_date 
ON survey_user_input (create_date);

-- Index for knowledge_article for faster article lookups
CREATE INDEX IF NOT EXISTS idx_knowledge_article_name 
ON knowledge_article (name);

-- Index for knowledge_article_member for faster member lookups
CREATE INDEX IF NOT EXISTS idx_knowledge_article_member_article_id 
ON knowledge_article_member (article_id);

-- Index for document_page for faster page lookups
CREATE INDEX IF NOT EXISTS idx_document_page_name 
ON document_page (name);

-- Index for document_folder for faster folder lookups
CREATE INDEX IF NOT EXISTS idx_document_folder_name 
ON document_folder (name);

-- Index for note_note for faster note lookups
CREATE INDEX IF NOT EXISTS idx_note_note_create_date 
ON note_note (create_date);

-- Index for app_odoo_app for faster app lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_name 
ON app_odoo_app (name);

-- Index for app_odoo_app_version for faster version lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_version_app_id 
ON app_odoo_app_version (app_id);

-- Index for app_odoo_app_category for faster category lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_category_name 
ON app_odoo_app_category (name);

-- Index for app_odoo_app_author for faster author lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_author_name 
ON app_odoo_app_author (name);

-- Index for app_odoo_app_website for faster website lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_name 
ON app_odoo_app_website (name);

-- Index for app_odoo_app_website_category for faster website category lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_category_name 
ON app_odoo_app_website_category (name);

-- Index for app_odoo_app_website_author for faster website author lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_author_name 
ON app_odoo_app_website_author (name);

-- Index for app_odoo_app_website_version for faster website version lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_version_app_id 
ON app_odoo_app_website_version (app_id);

-- Index for app_odoo_app_website_category_app for faster website category app lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_category_app_category_id 
ON app_odoo_app_website_category_app (category_id);

-- Index for app_odoo_app_website_author_app for faster website author app lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_author_app_author_id 
ON app_odoo_app_website_author_app (author_id);

-- Index for app_odoo_app_website_version_app for faster website version app lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_version_app_version_id 
ON app_odoo_app_website_version_app (version_id);

-- Index for app_odoo_app_website_app for faster website app lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_app_id 
ON app_odoo_app_website_app (app_id);

-- Index for app_odoo_app_website_app_website_id for faster website app website lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_website_id 
ON app_odoo_app_website_app (website_id);

-- Index for app_odoo_app_website_app_category_id for faster website app category lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_category_id 
ON app_odoo_app_website_app (category_id);

-- Index for app_odoo_app_website_app_author_id for faster website app author lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_author_id 
ON app_odoo_app_website_app (author_id);

-- Index for app_odoo_app_website_app_version_id for faster website app version lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_version_id 
ON app_odoo_app_website_app (version_id);

-- Index for app_odoo_app_website_app_is_published for faster website app published lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_published 
ON app_odoo_app_website_app (is_published);

-- Index for app_odoo_app_website_app_is_featured for faster website app featured lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_featured 
ON app_odoo_app_website_app (is_featured);

-- Index for app_odoo_app_website_app_is_recommended for faster website app recommended lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_recommended 
ON app_odoo_app_website_app (is_recommended);

-- Index for app_odoo_app_website_app_is_new for faster website app new lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_new 
ON app_odoo_app_website_app (is_new);

-- Index for app_odoo_app_website_app_is_updated for faster website app updated lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_updated 
ON app_odoo_app_website_app (is_updated);

-- Index for app_odoo_app_website_app_is_deprecated for faster website app deprecated lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_deprecated 
ON app_odoo_app_website_app (is_deprecated);

-- Index for app_odoo_app_website_app_is_archived for faster website app archived lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_archived 
ON app_odoo_app_website_app (is_archived);

-- Index for app_odoo_app_website_app_is_hidden for faster website app hidden lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_hidden 
ON app_odoo_app_website_app (is_hidden);

-- Index for app_odoo_app_website_app_is_private for faster website app private lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_private 
ON app_odoo_app_website_app (is_private);

-- Index for app_odoo_app_website_app_is_public for faster website app public lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_public 
ON app_odoo_app_website_app (is_public);

-- Index for app_odoo_app_website_app_is_verified for faster website app verified lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_verified 
ON app_odoo_app_website_app (is_verified);

-- Index for app_odoo_app_website_app_is_certified for faster website app certified lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_certified 
ON app_odoo_app_website_app (is_certified);

-- Index for app_odoo_app_website_app_is_official for faster website app official lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_official 
ON app_odoo_app_website_app (is_official);

-- Index for app_odoo_app_website_app_is_community for faster website app community lookups
CREATE INDEX IF NOT EXISTS idx_app_odoo_app_website_app_is_community 
ON app_odoo_app_website_app (is_community);

-- Index for app_odoo_app_website_app_is_enterprise for faster website app enterprise lookups
CREATE INDEX
