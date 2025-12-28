-- Supabase Schema for HR Clearance & Final Pay Compliance
-- Supports: Employee offboarding, clearance tracking, SLA monitoring
-- RLS: Multi-tenant isolation by company_id

-- ============================================
-- 1. HR CLEARANCE REQUEST AUDIT
-- ============================================
CREATE TABLE IF NOT EXISTS hr_clearance_request_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    clearance_request_id INTEGER NOT NULL,  -- Odoo hr.clearance.request ID
    employee_id INTEGER NOT NULL,            -- Odoo hr.employee ID
    event_type VARCHAR(50) NOT NULL,         -- 'created', 'clearance_complete', 'final_pay_executed'
    actor_email VARCHAR(255),
    old_values JSONB DEFAULT '{}',
    new_values JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT valid_event_type CHECK (
        event_type IN ('created', 'submitted', 'department_cleared',
                       'finance_cleared', 'it_cleared', 'hr_cleared',
                       'clearance_complete', 'final_pay_calculated',
                       'final_pay_approved', 'final_pay_executed', 'cancelled')
    )
);

-- Enable RLS
ALTER TABLE hr_clearance_request_audit ENABLE ROW LEVEL SECURITY;

-- Policy: Users see only their company's clearance audits
CREATE POLICY "tenant_isolation_clearance_audit" ON hr_clearance_request_audit
    FOR ALL
    USING (company_id = current_setting('app.current_company_id', true)::uuid);

-- Indexes
CREATE INDEX idx_clearance_audit_request ON hr_clearance_request_audit(clearance_request_id);
CREATE INDEX idx_clearance_audit_employee ON hr_clearance_request_audit(employee_id);
CREATE INDEX idx_clearance_audit_event ON hr_clearance_request_audit(event_type);
CREATE INDEX idx_clearance_audit_date ON hr_clearance_request_audit(created_at DESC);

-- ============================================
-- 2. FINAL PAY SLA COMPLIANCE
-- ============================================
CREATE TABLE IF NOT EXISTS final_pay_sla_compliance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    clearance_request_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    employee_name VARCHAR(255),
    department VARCHAR(100),

    -- Key Dates
    resignation_date DATE,
    last_working_date DATE,
    clearance_date DATE,                      -- Date all clearances completed
    final_pay_due_date_internal DATE,         -- Internal SLA: clearance + 7 days
    final_pay_due_date_statutory DATE,        -- Statutory: last day + 30 days
    final_pay_executed_date DATE,

    -- SLA Metrics
    days_to_execute INTEGER GENERATED ALWAYS AS (
        CASE WHEN final_pay_executed_date IS NOT NULL AND clearance_date IS NOT NULL
             THEN final_pay_executed_date - clearance_date
             ELSE NULL
        END
    ) STORED,

    days_to_statutory INTEGER GENERATED ALWAYS AS (
        CASE WHEN final_pay_executed_date IS NOT NULL AND last_working_date IS NOT NULL
             THEN final_pay_executed_date - last_working_date
             ELSE NULL
        END
    ) STORED,

    -- SLA Status
    internal_sla_status VARCHAR(20) GENERATED ALWAYS AS (
        CASE
            WHEN final_pay_executed_date IS NULL AND CURRENT_DATE > final_pay_due_date_internal THEN 'breach'
            WHEN final_pay_executed_date IS NULL AND CURRENT_DATE > (final_pay_due_date_internal - INTERVAL '2 days') THEN 'at_risk'
            WHEN final_pay_executed_date IS NOT NULL AND final_pay_executed_date <= final_pay_due_date_internal THEN 'compliant'
            WHEN final_pay_executed_date IS NOT NULL AND final_pay_executed_date > final_pay_due_date_internal THEN 'breach'
            ELSE 'pending'
        END
    ) STORED,

    statutory_compliant BOOLEAN GENERATED ALWAYS AS (
        CASE
            WHEN final_pay_executed_date IS NOT NULL AND days_to_statutory <= 30 THEN true
            WHEN final_pay_executed_date IS NOT NULL AND days_to_statutory > 30 THEN false
            ELSE NULL
        END
    ) STORED,

    -- Financial Summary
    gross_final_pay NUMERIC(12,2),
    deductions_total NUMERIC(12,2),
    net_final_pay NUMERIC(12,2),
    currency_code VARCHAR(3) DEFAULT 'PHP',

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT unique_clearance_sla UNIQUE (company_id, clearance_request_id)
);

-- Enable RLS
ALTER TABLE final_pay_sla_compliance ENABLE ROW LEVEL SECURITY;

-- Policy: Users see only their company's SLA data
CREATE POLICY "tenant_isolation_sla" ON final_pay_sla_compliance
    FOR ALL
    USING (company_id = current_setting('app.current_company_id', true)::uuid);

-- Indexes
CREATE INDEX idx_sla_employee ON final_pay_sla_compliance(employee_id);
CREATE INDEX idx_sla_status ON final_pay_sla_compliance(internal_sla_status);
CREATE INDEX idx_sla_clearance_date ON final_pay_sla_compliance(clearance_date);

-- ============================================
-- 3. CLEARANCE CHECKLIST TRACKING
-- ============================================
CREATE TABLE IF NOT EXISTS hr_clearance_checklist (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    clearance_request_id INTEGER NOT NULL,
    department VARCHAR(50) NOT NULL,          -- 'IT', 'Finance', 'HR', 'Admin', 'Department'
    checklist_item VARCHAR(255) NOT NULL,
    is_cleared BOOLEAN DEFAULT FALSE,
    cleared_by_email VARCHAR(255),
    cleared_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT valid_department CHECK (
        department IN ('IT', 'Finance', 'HR', 'Admin', 'Department', 'Legal', 'Facilities')
    )
);

-- Enable RLS
ALTER TABLE hr_clearance_checklist ENABLE ROW LEVEL SECURITY;

-- Policy
CREATE POLICY "tenant_isolation_checklist" ON hr_clearance_checklist
    FOR ALL
    USING (company_id = current_setting('app.current_company_id', true)::uuid);

-- Indexes
CREATE INDEX idx_checklist_request ON hr_clearance_checklist(clearance_request_id);
CREATE INDEX idx_checklist_dept ON hr_clearance_checklist(department);

-- ============================================
-- 4. FUNCTIONS FOR SLA MANAGEMENT
-- ============================================

-- Function to initialize SLA record when clearance request is created
CREATE OR REPLACE FUNCTION init_clearance_sla(
    p_company_id UUID,
    p_clearance_request_id INTEGER,
    p_employee_id INTEGER,
    p_employee_name VARCHAR,
    p_department VARCHAR,
    p_resignation_date DATE,
    p_last_working_date DATE
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_result_id UUID;
BEGIN
    INSERT INTO final_pay_sla_compliance (
        company_id, clearance_request_id, employee_id,
        employee_name, department,
        resignation_date, last_working_date,
        final_pay_due_date_statutory
    )
    VALUES (
        p_company_id, p_clearance_request_id, p_employee_id,
        p_employee_name, p_department,
        p_resignation_date, p_last_working_date,
        p_last_working_date + INTERVAL '30 days'
    )
    ON CONFLICT (company_id, clearance_request_id)
    DO UPDATE SET
        updated_at = NOW()
    RETURNING id INTO v_result_id;

    -- Log audit event
    INSERT INTO hr_clearance_request_audit (
        company_id, clearance_request_id, employee_id,
        event_type, new_values
    )
    VALUES (
        p_company_id, p_clearance_request_id, p_employee_id,
        'created',
        jsonb_build_object(
            'resignation_date', p_resignation_date,
            'last_working_date', p_last_working_date
        )
    );

    RETURN v_result_id;
END;
$$;

-- Function to mark clearance complete and set internal SLA
CREATE OR REPLACE FUNCTION complete_clearance(
    p_company_id UUID,
    p_clearance_request_id INTEGER,
    p_actor_email VARCHAR
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_clearance_date DATE := CURRENT_DATE;
    v_employee_id INTEGER;
BEGIN
    -- Update SLA record
    UPDATE final_pay_sla_compliance
    SET
        clearance_date = v_clearance_date,
        final_pay_due_date_internal = v_clearance_date + INTERVAL '7 days',
        updated_at = NOW()
    WHERE company_id = p_company_id
      AND clearance_request_id = p_clearance_request_id
    RETURNING employee_id INTO v_employee_id;

    -- Log audit event
    INSERT INTO hr_clearance_request_audit (
        company_id, clearance_request_id, employee_id,
        event_type, actor_email,
        new_values
    )
    VALUES (
        p_company_id, p_clearance_request_id, v_employee_id,
        'clearance_complete', p_actor_email,
        jsonb_build_object('clearance_date', v_clearance_date)
    );
END;
$$;

-- Function to record final pay execution
CREATE OR REPLACE FUNCTION execute_final_pay(
    p_company_id UUID,
    p_clearance_request_id INTEGER,
    p_gross_pay NUMERIC,
    p_deductions NUMERIC,
    p_net_pay NUMERIC,
    p_actor_email VARCHAR
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_employee_id INTEGER;
BEGIN
    -- Update SLA record
    UPDATE final_pay_sla_compliance
    SET
        final_pay_executed_date = CURRENT_DATE,
        gross_final_pay = p_gross_pay,
        deductions_total = p_deductions,
        net_final_pay = p_net_pay,
        updated_at = NOW()
    WHERE company_id = p_company_id
      AND clearance_request_id = p_clearance_request_id
    RETURNING employee_id INTO v_employee_id;

    -- Log audit event
    INSERT INTO hr_clearance_request_audit (
        company_id, clearance_request_id, employee_id,
        event_type, actor_email,
        new_values
    )
    VALUES (
        p_company_id, p_clearance_request_id, v_employee_id,
        'final_pay_executed', p_actor_email,
        jsonb_build_object(
            'gross_pay', p_gross_pay,
            'deductions', p_deductions,
            'net_pay', p_net_pay
        )
    );
END;
$$;

-- ============================================
-- 5. VIEWS FOR REPORTING
-- ============================================

-- SLA Dashboard View
CREATE OR REPLACE VIEW v_final_pay_sla_dashboard AS
SELECT
    company_id,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE internal_sla_status = 'compliant') AS compliant_count,
    COUNT(*) FILTER (WHERE internal_sla_status = 'at_risk') AS at_risk_count,
    COUNT(*) FILTER (WHERE internal_sla_status = 'breach') AS breach_count,
    COUNT(*) FILTER (WHERE internal_sla_status = 'pending') AS pending_count,
    ROUND(
        COUNT(*) FILTER (WHERE internal_sla_status = 'compliant')::NUMERIC /
        NULLIF(COUNT(*) FILTER (WHERE internal_sla_status IN ('compliant', 'breach')), 0) * 100,
        2
    ) AS compliance_rate,
    AVG(days_to_execute) FILTER (WHERE days_to_execute IS NOT NULL) AS avg_days_to_execute,
    COUNT(*) FILTER (WHERE statutory_compliant = false) AS statutory_breach_count
FROM final_pay_sla_compliance
GROUP BY company_id;

-- Pending Clearances View
CREATE OR REPLACE VIEW v_pending_clearances AS
SELECT
    s.company_id,
    s.clearance_request_id,
    s.employee_id,
    s.employee_name,
    s.department,
    s.last_working_date,
    s.clearance_date,
    s.final_pay_due_date_internal,
    s.internal_sla_status,
    CURRENT_DATE - COALESCE(s.clearance_date, s.last_working_date) AS days_since_exit,
    s.final_pay_due_date_internal - CURRENT_DATE AS days_until_sla
FROM final_pay_sla_compliance s
WHERE s.final_pay_executed_date IS NULL;

-- Clearance Status by Department View
CREATE OR REPLACE VIEW v_clearance_by_department AS
SELECT
    c.company_id,
    c.clearance_request_id,
    c.department,
    COUNT(*) AS total_items,
    COUNT(*) FILTER (WHERE c.is_cleared = true) AS cleared_items,
    ROUND(
        COUNT(*) FILTER (WHERE c.is_cleared = true)::NUMERIC / COUNT(*) * 100,
        0
    ) AS completion_pct
FROM hr_clearance_checklist c
GROUP BY c.company_id, c.clearance_request_id, c.department;

-- ============================================
-- 6. TRIGGERS
-- ============================================

-- Auto-update timestamp
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_sla_updated
    BEFORE UPDATE ON final_pay_sla_compliance
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_timestamp();

-- ============================================
-- 7. GRANTS
-- ============================================

-- Grant access to authenticated users
GRANT SELECT ON hr_clearance_request_audit TO authenticated;
GRANT SELECT, INSERT, UPDATE ON final_pay_sla_compliance TO authenticated;
GRANT SELECT, INSERT, UPDATE ON hr_clearance_checklist TO authenticated;
GRANT SELECT ON v_final_pay_sla_dashboard TO authenticated;
GRANT SELECT ON v_pending_clearances TO authenticated;
GRANT SELECT ON v_clearance_by_department TO authenticated;

-- Grant access to service role (n8n, backend)
GRANT ALL ON hr_clearance_request_audit TO service_role;
GRANT ALL ON final_pay_sla_compliance TO service_role;
GRANT ALL ON hr_clearance_checklist TO service_role;
GRANT EXECUTE ON FUNCTION init_clearance_sla TO service_role;
GRANT EXECUTE ON FUNCTION complete_clearance TO service_role;
GRANT EXECUTE ON FUNCTION execute_final_pay TO service_role;
