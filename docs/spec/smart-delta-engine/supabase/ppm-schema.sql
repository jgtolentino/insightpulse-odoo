-- Supabase Schema for PPM Automation Pipeline
-- Supports: Audit logs, resource capacity, EVM calculations
-- RLS: Multi-tenant isolation by company_id

-- ============================================
-- 1. WORKFLOW AUDIT LOG
-- ============================================
CREATE TABLE IF NOT EXISTS project_workflow_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    workflow_type VARCHAR(50) NOT NULL,  -- 'portfolio_intake', 'resource_allocation', 'invoice_gen', 'variance_alert'
    source_system VARCHAR(20) NOT NULL,   -- 'notion', 'odoo', 'n8n', 'mattermost'
    source_record_id VARCHAR(100),
    action VARCHAR(50) NOT NULL,          -- 'created', 'approved', 'rejected', 'updated', 'alert_high'
    actor_email VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT valid_workflow_type CHECK (
        workflow_type IN ('portfolio_intake', 'resource_allocation', 'budget_sync',
                          'variance_alert', 'invoice_generation', 'demand_intake',
                          'evm_calculation', 'task_sync', 'capacity_sync')
    )
);

-- Enable RLS
ALTER TABLE project_workflow_audit ENABLE ROW LEVEL SECURITY;

-- Policy: Users see only their company's audit logs
CREATE POLICY "tenant_isolation_audit" ON project_workflow_audit
    FOR ALL
    USING (company_id = current_setting('app.current_company_id', true)::uuid);

-- Index for common queries
CREATE INDEX idx_audit_workflow_type ON project_workflow_audit(workflow_type);
CREATE INDEX idx_audit_created_at ON project_workflow_audit(created_at DESC);
CREATE INDEX idx_audit_company ON project_workflow_audit(company_id);

-- ============================================
-- 2. RESOURCE CAPACITY (Synced from Notion)
-- ============================================
CREATE TABLE IF NOT EXISTS resource_capacity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    resource_id VARCHAR(100) NOT NULL,      -- Notion resource ID or Odoo user ID
    resource_name VARCHAR(255),
    resource_email VARCHAR(255),
    week_of DATE NOT NULL,                   -- Monday of the week
    available_hours NUMERIC(6,2) DEFAULT 40,
    allocated_hours NUMERIC(6,2) DEFAULT 0,
    billable_hours NUMERIC(6,2) DEFAULT 0,
    non_billable_hours NUMERIC(6,2) DEFAULT 0,
    utilization_pct NUMERIC(5,2) GENERATED ALWAYS AS (
        CASE WHEN available_hours > 0
             THEN (allocated_hours / available_hours) * 100
             ELSE 0
        END
    ) STORED,
    synced_from VARCHAR(20) DEFAULT 'notion', -- 'notion', 'odoo'
    synced_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_resource_week UNIQUE (company_id, resource_id, week_of)
);

-- Enable RLS
ALTER TABLE resource_capacity ENABLE ROW LEVEL SECURITY;

-- Policy: Users see only their company's resources
CREATE POLICY "tenant_isolation_capacity" ON resource_capacity
    FOR ALL
    USING (company_id = current_setting('app.current_company_id', true)::uuid);

-- Index for capacity queries
CREATE INDEX idx_capacity_week ON resource_capacity(week_of);
CREATE INDEX idx_capacity_resource ON resource_capacity(resource_id);

-- ============================================
-- 3. PROJECT BUDGET SNAPSHOT (For variance analysis)
-- ============================================
CREATE TABLE IF NOT EXISTS project_budget_snapshot (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    project_id INTEGER NOT NULL,            -- Odoo project ID
    project_name VARCHAR(255),
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
    planned_amount NUMERIC(12,2) DEFAULT 0,
    actual_amount NUMERIC(12,2) DEFAULT 0,
    committed_amount NUMERIC(12,2) DEFAULT 0,
    forecast_amount NUMERIC(12,2) DEFAULT 0,
    variance_amount NUMERIC(12,2) GENERATED ALWAYS AS (actual_amount - planned_amount) STORED,
    variance_pct NUMERIC(6,2) GENERATED ALWAYS AS (
        CASE WHEN planned_amount > 0
             THEN ((actual_amount - planned_amount) / planned_amount) * 100
             ELSE 0
        END
    ) STORED,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_project_snapshot UNIQUE (company_id, project_id, snapshot_date)
);

-- Enable RLS
ALTER TABLE project_budget_snapshot ENABLE ROW LEVEL SECURITY;

-- Policy: Users see only their company's budgets
CREATE POLICY "tenant_isolation_budget" ON project_budget_snapshot
    FOR ALL
    USING (company_id = current_setting('app.current_company_id', true)::uuid);

-- Index for reporting
CREATE INDEX idx_budget_project ON project_budget_snapshot(project_id);
CREATE INDEX idx_budget_date ON project_budget_snapshot(snapshot_date DESC);

-- ============================================
-- 4. EARNED VALUE MANAGEMENT (EVM) METRICS
-- ============================================
CREATE TABLE IF NOT EXISTS project_evm_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    project_id INTEGER NOT NULL,
    project_name VARCHAR(255),
    calculation_date DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Earned Value Metrics
    bac NUMERIC(12,2) DEFAULT 0,            -- Budget at Completion
    pv NUMERIC(12,2) DEFAULT 0,             -- Planned Value
    ev NUMERIC(12,2) DEFAULT 0,             -- Earned Value
    ac NUMERIC(12,2) DEFAULT 0,             -- Actual Cost

    -- Performance Indices (computed)
    cpi NUMERIC(6,3) GENERATED ALWAYS AS (
        CASE WHEN ac > 0 THEN ev / ac ELSE 0 END
    ) STORED,
    spi NUMERIC(6,3) GENERATED ALWAYS AS (
        CASE WHEN pv > 0 THEN ev / pv ELSE 0 END
    ) STORED,

    -- Variances
    cv NUMERIC(12,2) GENERATED ALWAYS AS (ev - ac) STORED,   -- Cost Variance
    sv NUMERIC(12,2) GENERATED ALWAYS AS (ev - pv) STORED,   -- Schedule Variance

    -- Forecasts
    etc NUMERIC(12,2) DEFAULT 0,            -- Estimate to Complete
    eac NUMERIC(12,2) GENERATED ALWAYS AS (
        CASE WHEN cpi > 0 THEN bac / cpi ELSE bac END
    ) STORED,                               -- Estimate at Completion
    vac NUMERIC(12,2) GENERATED ALWAYS AS (bac - eac) STORED, -- Variance at Completion

    -- Percent Complete
    pct_complete NUMERIC(5,2) GENERATED ALWAYS AS (
        CASE WHEN bac > 0 THEN (ev / bac) * 100 ELSE 0 END
    ) STORED,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_evm_snapshot UNIQUE (company_id, project_id, calculation_date)
);

-- Enable RLS
ALTER TABLE project_evm_metrics ENABLE ROW LEVEL SECURITY;

-- Policy: Users see only their company's EVM data
CREATE POLICY "tenant_isolation_evm" ON project_evm_metrics
    FOR ALL
    USING (company_id = current_setting('app.current_company_id', true)::uuid);

-- Index for EVM queries
CREATE INDEX idx_evm_project ON project_evm_metrics(project_id);
CREATE INDEX idx_evm_date ON project_evm_metrics(calculation_date DESC);

-- ============================================
-- 5. FUNCTIONS FOR EVM CALCULATION
-- ============================================

-- Function to calculate and store EVM metrics for a project
CREATE OR REPLACE FUNCTION calculate_project_evm(
    p_company_id UUID,
    p_project_id INTEGER,
    p_project_name VARCHAR,
    p_bac NUMERIC,
    p_pv NUMERIC,
    p_ev NUMERIC,
    p_ac NUMERIC
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_result_id UUID;
BEGIN
    INSERT INTO project_evm_metrics (
        company_id, project_id, project_name,
        bac, pv, ev, ac,
        etc
    )
    VALUES (
        p_company_id, p_project_id, p_project_name,
        p_bac, p_pv, p_ev, p_ac,
        CASE WHEN (p_ev / NULLIF(p_ac, 0)) > 0
             THEN (p_bac - p_ev) / (p_ev / NULLIF(p_ac, 0))
             ELSE p_bac - p_ev
        END
    )
    ON CONFLICT (company_id, project_id, calculation_date)
    DO UPDATE SET
        bac = EXCLUDED.bac,
        pv = EXCLUDED.pv,
        ev = EXCLUDED.ev,
        ac = EXCLUDED.ac,
        etc = EXCLUDED.etc
    RETURNING id INTO v_result_id;

    RETURN v_result_id;
END;
$$;

-- ============================================
-- 6. VIEWS FOR REPORTING
-- ============================================

-- Resource utilization summary view
CREATE OR REPLACE VIEW v_resource_utilization AS
SELECT
    company_id,
    resource_name,
    resource_email,
    DATE_TRUNC('month', week_of) AS month,
    SUM(available_hours) AS total_available,
    SUM(allocated_hours) AS total_allocated,
    SUM(billable_hours) AS total_billable,
    AVG(utilization_pct) AS avg_utilization
FROM resource_capacity
GROUP BY company_id, resource_name, resource_email, DATE_TRUNC('month', week_of);

-- Project health dashboard view
CREATE OR REPLACE VIEW v_project_health AS
SELECT
    e.company_id,
    e.project_id,
    e.project_name,
    e.calculation_date,
    e.pct_complete,
    e.cpi,
    e.spi,
    b.variance_pct AS budget_variance_pct,
    CASE
        WHEN e.cpi >= 0.95 AND e.spi >= 0.95 THEN 'GREEN'
        WHEN e.cpi >= 0.85 AND e.spi >= 0.85 THEN 'YELLOW'
        ELSE 'RED'
    END AS health_status
FROM project_evm_metrics e
LEFT JOIN project_budget_snapshot b
    ON e.project_id = b.project_id
    AND e.calculation_date = b.snapshot_date
    AND e.company_id = b.company_id
WHERE e.calculation_date = (
    SELECT MAX(calculation_date)
    FROM project_evm_metrics
    WHERE project_id = e.project_id AND company_id = e.company_id
);

-- ============================================
-- 7. TRIGGERS FOR AUDIT LOGGING
-- ============================================

-- Function to log changes
CREATE OR REPLACE FUNCTION log_budget_change()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO project_workflow_audit (
        company_id, workflow_type, source_system,
        source_record_id, action, metadata
    )
    VALUES (
        NEW.company_id, 'budget_sync', 'supabase',
        NEW.project_id::text,
        CASE WHEN TG_OP = 'INSERT' THEN 'created' ELSE 'updated' END,
        jsonb_build_object(
            'planned', NEW.planned_amount,
            'actual', NEW.actual_amount,
            'variance_pct', NEW.variance_pct
        )
    );
    RETURN NEW;
END;
$$;

-- Create trigger
CREATE TRIGGER trg_budget_audit
    AFTER INSERT OR UPDATE ON project_budget_snapshot
    FOR EACH ROW
    EXECUTE FUNCTION log_budget_change();

-- ============================================
-- 8. GRANTS FOR API ACCESS
-- ============================================

-- Grant access to authenticated users (Supabase auth)
GRANT SELECT, INSERT ON project_workflow_audit TO authenticated;
GRANT SELECT, INSERT, UPDATE ON resource_capacity TO authenticated;
GRANT SELECT, INSERT ON project_budget_snapshot TO authenticated;
GRANT SELECT, INSERT ON project_evm_metrics TO authenticated;
GRANT SELECT ON v_resource_utilization TO authenticated;
GRANT SELECT ON v_project_health TO authenticated;
GRANT EXECUTE ON FUNCTION calculate_project_evm TO authenticated;

-- Grant access to service role (n8n, backend)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;
