-- ============================================================================
-- SaaS Feature Matrix Seed Data
-- ============================================================================
-- Purpose: Initial seed data for SaaS products and feature mappings
-- Products: Cheqroom, SAP Concur, Notion, Clarity PPM
-- ============================================================================

-- 1. SaaS Products
-- ============================================================================
insert into saas_products (slug, name, homepage_url, active) values
  ('cheqroom', 'Cheqroom – Equipment Management', 'https://cheqroom.com', true),
  ('concur_expense', 'SAP Concur – Expense Management', 'https://www.concur.com', true),
  ('notion_business', 'Notion – Business Workspace', 'https://www.notion.so', true),
  ('clarity_ppm', 'Clarity PPM – Project & Portfolio Management', null, true)
on conflict (slug) do nothing;

-- 2. Cheqroom Feature Mappings
-- ============================================================================
insert into saas_feature_mappings (
  saas_product_id, feature_key, feature_name, category, status, criticality,
  odoo_core_modules, oca_modules, ipai_modules, enterprise_equiv, requires_ipai
) values
  -- Equipment Management
  (
    (select id from saas_products where slug = 'cheqroom'),
    'equipment_catalog',
    'Equipment catalog with categories, locations, and attributes',
    'equipment',
    'covered',
    5,
    array['stock', 'maintenance', 'project', 'mail'],
    array['web_responsive'],
    array['ipai_equipment'],
    array['maintenance_equipment'],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'cheqroom'),
    'booking_calendar',
    'Booking calendar with overlap prevention and conflict detection',
    'equipment',
    'covered',
    5,
    array['project', 'mail'],
    array[],
    array['ipai_equipment'],
    array['project_forecast'],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'cheqroom'),
    'overdue_alerts',
    'Automated overdue notifications and activity tracking',
    'equipment',
    'covered',
    4,
    array['mail'],
    array[],
    array['ipai_equipment'],
    array['helpdesk'],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'cheqroom'),
    'mobile_scanning',
    'Mobile barcode scanning for check-in/check-out',
    'equipment',
    'gap',
    3,
    array['stock'],
    array[],
    array[]::text[],
    array['stock_barcode'],
    array['ipai_equipment_mobile']
  ),
  (
    (select id from saas_products where slug = 'cheqroom'),
    'utilization_reports',
    'Equipment utilization and analytics dashboards',
    'equipment',
    'partial',
    3,
    array['maintenance'],
    array[],
    array['ipai_equipment'],
    array['maintenance_equipment'],
    array['ipai_equipment_analytics']
  )
on conflict (saas_product_id, feature_key) do nothing;

-- 3. SAP Concur Feature Mappings
-- ============================================================================
insert into saas_feature_mappings (
  saas_product_id, feature_key, feature_name, category, status, criticality,
  odoo_core_modules, oca_modules, ipai_modules, enterprise_equiv, requires_ipai
) values
  -- Expense Management
  (
    (select id from saas_products where slug = 'concur_expense'),
    'expense_submission',
    'Expense creation, approval workflows, and accounting posting',
    'expenses',
    'covered',
    5,
    array['hr_expense', 'account', 'mail'],
    array['hr_expense_invoice'],
    array['ipai_expense', 'ipai_cash_advance'],
    array['hr_expense_advanced'],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'concur_expense'),
    'ocr_receipt_capture',
    'OCR-powered receipt processing with vendor normalization',
    'expenses',
    'covered',
    5,
    array['hr_expense'],
    array[],
    array['ipai_ocr_expense'],
    array['documents_hr_expense'],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'concur_expense'),
    'cash_advance',
    'Cash advance request, disbursement, and settlement',
    'expenses',
    'covered',
    4,
    array['hr_expense', 'account'],
    array[],
    array['ipai_cash_advance'],
    array[],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'concur_expense'),
    'monthly_closing',
    'Monthly financial closing integration and BIR compliance',
    'expenses',
    'covered',
    5,
    array['account'],
    array[],
    array['ipai_finance_monthly_closing'],
    array['account_lock'],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'concur_expense'),
    'credit_card_sync',
    'Automated credit card feed import and reconciliation',
    'expenses',
    'gap',
    3,
    array['account'],
    array[],
    array[]::text[],
    array['account_bank_statement_import'],
    array['ipai_expense_bank_sync']
  ),
  (
    (select id from saas_products where slug = 'concur_expense'),
    'per_diem_automation',
    'Automated per diem calculation based on travel dates',
    'expenses',
    'gap',
    2,
    array['hr_expense'],
    array[],
    array[]::text[],
    array['hr_expense_advanced'],
    array['ipai_expense_per_diem']
  )
on conflict (saas_product_id, feature_key) do nothing;

-- 4. Notion Workspace Feature Mappings
-- ============================================================================
insert into saas_feature_mappings (
  saas_product_id, feature_key, feature_name, category, status, criticality,
  odoo_core_modules, oca_modules, ipai_modules, enterprise_equiv, requires_ipai
) values
  -- Document & Project Management
  (
    (select id from saas_products where slug = 'notion_business'),
    'document_management',
    'Rich text document creation, editing, and organization',
    'collaboration',
    'covered',
    5,
    array['note', 'mail'],
    array[],
    array['ipai_docs'],
    array['documents'],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'notion_business'),
    'project_doc_linkage',
    'Bi-directional linking between documents and projects',
    'collaboration',
    'covered',
    4,
    array['project', 'note'],
    array[],
    array['ipai_docs_project'],
    array['documents_project'],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'notion_business'),
    'task_templates',
    'Project templates with pre-defined task lists and workflows',
    'collaboration',
    'covered',
    4,
    array['project'],
    array[],
    array[]::text[],
    array['project_template'],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'notion_business'),
    'my_tasks_view',
    'Personal task dashboard with filters and quick actions',
    'collaboration',
    'covered',
    5,
    array['project', 'mail'],
    array[],
    array[]::text[],
    array['project_enterprise'],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'notion_business'),
    'mention_notifications',
    '@mention notifications via email and in-app',
    'collaboration',
    'covered',
    3,
    array['mail'],
    array[],
    array[]::text[],
    array[],
    array[]::text[]
  ),
  (
    (select id from saas_products where slug = 'notion_business'),
    'realtime_collaboration',
    'Multiple users editing same document simultaneously',
    'collaboration',
    'gap',
    2,
    array['note'],
    array[],
    array[]::text[],
    array['documents'],
    array['ipai_docs_realtime']
  )
on conflict (saas_product_id, feature_key) do nothing;

-- 5. Clarity PPM Feature Mappings
-- ============================================================================
insert into saas_feature_mappings (
  saas_product_id, feature_key, feature_name, category, status, criticality,
  odoo_core_modules, oca_modules, ipai_modules, enterprise_equiv, requires_ipai
) values
  -- Portfolio & Program Management
  (
    (select id from saas_products where slug = 'clarity_ppm'),
    'portfolio_hierarchy',
    'Portfolio → Program → Project hierarchy with aggregations',
    'ppm',
    'gap',
    5,
    array['project'],
    array[],
    array[]::text[],
    array['project_portfolio'],
    array['ipai_ppm_portfolio']
  ),
  (
    (select id from saas_products where slug = 'clarity_ppm'),
    'gate_workflows',
    'Stage-gate approval workflows (gate 0-5)',
    'ppm',
    'gap',
    4,
    array['project'],
    array[],
    array[]::text[],
    array['project_forecast'],
    array['ipai_ppm_gates']
  ),
  (
    (select id from saas_products where slug = 'clarity_ppm'),
    'resource_capacity',
    'Resource capacity planning and allocation tracking',
    'ppm',
    'gap',
    5,
    array['project'],
    array[],
    array[]::text[],
    array['planning', 'project_forecast'],
    array['ipai_ppm_capacity']
  ),
  (
    (select id from saas_products where slug = 'clarity_ppm'),
    'portfolio_scoring',
    'Portfolio prioritization with weighted scoring models',
    'ppm',
    'gap',
    3,
    array['project'],
    array[],
    array[]::text[],
    array['project_portfolio'],
    array['ipai_ppm_scoring']
  ),
  (
    (select id from saas_products where slug = 'clarity_ppm'),
    'roadmap_visualization',
    'Strategic roadmap and timeline visualization',
    'ppm',
    'gap',
    3,
    array['project'],
    array[],
    array[]::text[],
    array['project_forecast'],
    array['ipai_ppm_roadmap']
  )
on conflict (saas_product_id, feature_key) do nothing;

-- 6. Artifact Linkages (Existing Implementations)
-- ============================================================================

-- Cheqroom artifacts
insert into saas_feature_artifacts (feature_mapping_id, artifact_type, path, ref) values
  (
    (select id from saas_feature_mappings where feature_key = 'equipment_catalog'),
    'module',
    'addons/ipai_equipment',
    'v0.5.0-saas-parity'
  ),
  (
    (select id from saas_feature_mappings where feature_key = 'equipment_catalog'),
    'prd',
    'docs/FEATURE_CHEQROOM_PARITY.md',
    'v0.5.0-saas-parity'
  ),
  (
    (select id from saas_feature_mappings where feature_key = 'equipment_catalog'),
    'test',
    'addons/ipai_equipment/tests/test_booking_cron.py',
    'v0.5.0-saas-parity'
  )
on conflict (feature_mapping_id, artifact_type, path) do nothing;

-- Concur artifacts
insert into saas_feature_artifacts (feature_mapping_id, artifact_type, path, ref) values
  (
    (select id from saas_feature_mappings where feature_key = 'expense_submission'),
    'module',
    'addons/ipai_expense',
    'v0.5.0-saas-parity'
  ),
  (
    (select id from saas_feature_mappings where feature_key = 'ocr_receipt_capture'),
    'module',
    'addons/ipai_ocr_expense',
    'v0.5.0-saas-parity'
  ),
  (
    (select id from saas_feature_mappings where feature_key = 'cash_advance'),
    'module',
    'addons/ipai_cash_advance',
    'v0.5.0-saas-parity'
  ),
  (
    (select id from saas_feature_mappings where feature_key = 'expense_submission'),
    'prd',
    'docs/FEATURE_CONCUR_PARITY.md',
    'v0.5.0-saas-parity'
  ),
  (
    (select id from saas_feature_mappings where feature_key = 'expense_submission'),
    'test',
    'addons/ipai_expense/tests/test_expense_ocr.py',
    'v0.5.0-saas-parity'
  )
on conflict (feature_mapping_id, artifact_type, path) do nothing;

-- Notion artifacts
insert into saas_feature_artifacts (feature_mapping_id, artifact_type, path, ref) values
  (
    (select id from saas_feature_mappings where feature_key = 'document_management'),
    'module',
    'addons/ipai_docs',
    'v0.5.0-saas-parity'
  ),
  (
    (select id from saas_feature_mappings where feature_key = 'project_doc_linkage'),
    'module',
    'addons/ipai_docs_project',
    'v0.5.0-saas-parity'
  ),
  (
    (select id from saas_feature_mappings where feature_key = 'document_management'),
    'prd',
    'docs/FEATURE_WORKSPACE_PARITY.md',
    'v0.5.0-saas-parity'
  ),
  (
    (select id from saas_feature_mappings where feature_key = 'document_management'),
    'test',
    'addons/ipai_docs/tests/test_workspace_visibility.py',
    'v0.5.0-saas-parity'
  )
on conflict (feature_mapping_id, artifact_type, path) do nothing;
