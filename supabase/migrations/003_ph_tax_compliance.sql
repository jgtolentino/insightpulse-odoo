-- Philippine Tax Compliance Schema
-- RAG corpus + filing calendar with holiday rules

CREATE SCHEMA IF NOT EXISTS ph_tax;

-- Authoritative BIR documents (for RAG & citations)
CREATE TABLE IF NOT EXISTS ph_tax.docs (
    id BIGSERIAL PRIMARY KEY,
    source_url TEXT NOT NULL,
    title TEXT NOT NULL,
    doc_date DATE,
    doc_type TEXT NOT NULL, -- 'Form', 'RMC', 'RR', 'Guide', 'FAQ'
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(384), -- MiniLM-L6-v2 embeddings
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for vector search
CREATE INDEX IF NOT EXISTS docs_embedding_idx ON ph_tax.docs
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS docs_doc_type_idx ON ph_tax.docs(doc_type);
CREATE INDEX IF NOT EXISTS docs_doc_date_idx ON ph_tax.docs(doc_date DESC);
CREATE INDEX IF NOT EXISTS docs_metadata_idx ON ph_tax.docs USING GIN(metadata);

-- Filing calendar (entity-specific, with holiday adjustments)
CREATE TABLE IF NOT EXISTS ph_tax.calendar (
    id BIGSERIAL PRIMARY KEY,
    entity TEXT NOT NULL, -- 'ALL' for universal deadlines
    form_code TEXT NOT NULL, -- '2550Q', '1601-C', '1601-EQ', '2316', etc.
    form_name TEXT NOT NULL,
    period_type TEXT NOT NULL, -- 'monthly', 'quarterly', 'annual'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    due_date DATE NOT NULL,
    due_date_adjusted DATE, -- After holiday adjustments
    basis TEXT NOT NULL, -- Citation (e.g., 'RMC 5-2023, Form 2550Q Guidelines')
    source_url TEXT,
    notes TEXT,
    is_filed BOOLEAN DEFAULT FALSE,
    filed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS calendar_entity_idx ON ph_tax.calendar(entity);
CREATE INDEX IF NOT EXISTS calendar_form_idx ON ph_tax.calendar(form_code);
CREATE INDEX IF NOT EXISTS calendar_due_idx ON ph_tax.calendar(due_date_adjusted);
CREATE INDEX IF NOT EXISTS calendar_period_idx ON ph_tax.calendar(period_start, period_end);

-- Philippine holidays (for due date adjustments)
CREATE TABLE IF NOT EXISTS ph_tax.holidays (
    id BIGSERIAL PRIMARY KEY,
    holiday_date DATE NOT NULL UNIQUE,
    holiday_name TEXT NOT NULL,
    holiday_type TEXT NOT NULL, -- 'Regular', 'Special Non-Working', 'Special Working'
    proclamation TEXT, -- E.g., 'Proclamation No. 90, s. 2024'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS holidays_date_idx ON ph_tax.holidays(holiday_date);

-- Function to adjust due date for weekends and holidays
CREATE OR REPLACE FUNCTION ph_tax.adjust_due_date(input_date DATE)
RETURNS DATE AS $$
DECLARE
    adjusted_date DATE := input_date;
    max_iterations INT := 10;
    iteration INT := 0;
BEGIN
    -- Move forward if falls on weekend or holiday
    WHILE iteration < max_iterations LOOP
        -- Check if weekend
        IF EXTRACT(DOW FROM adjusted_date) IN (0, 6) THEN
            -- Sunday (0) or Saturday (6) - move to next Monday
            adjusted_date := adjusted_date + (1 + (7 - EXTRACT(DOW FROM adjusted_date)::INT))::INT;
        -- Check if holiday
        ELSIF EXISTS (
            SELECT 1 FROM ph_tax.holidays
            WHERE holiday_date = adjusted_date
            AND holiday_type IN ('Regular', 'Special Non-Working')
        ) THEN
            -- Move to next day
            adjusted_date := adjusted_date + 1;
        ELSE
            -- Valid business day
            EXIT;
        END IF;

        iteration := iteration + 1;
    END LOOP;

    RETURN adjusted_date;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to generate quarterly deadlines
CREATE OR REPLACE FUNCTION ph_tax.generate_quarterly_deadlines(
    p_year INT,
    p_form_code TEXT,
    p_form_name TEXT,
    p_basis TEXT,
    p_source_url TEXT DEFAULT NULL,
    p_days_after_quarter INT DEFAULT 25
)
RETURNS VOID AS $$
DECLARE
    quarters INT[] := ARRAY[1, 2, 3, 4];
    q INT;
    period_start DATE;
    period_end DATE;
    raw_due DATE;
BEGIN
    FOREACH q IN ARRAY quarters LOOP
        period_start := DATE(p_year || '-' || ((q-1)*3 + 1) || '-01');
        period_end := (period_start + INTERVAL '3 months' - INTERVAL '1 day')::DATE;
        raw_due := period_end + p_days_after_quarter;

        INSERT INTO ph_tax.calendar (
            entity, form_code, form_name, period_type,
            period_start, period_end, due_date, due_date_adjusted,
            basis, source_url
        ) VALUES (
            'ALL',
            p_form_code,
            p_form_name,
            'quarterly',
            period_start,
            period_end,
            raw_due,
            ph_tax.adjust_due_date(raw_due),
            p_basis,
            p_source_url
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function to generate monthly deadlines
CREATE OR REPLACE FUNCTION ph_tax.generate_monthly_deadlines(
    p_year INT,
    p_form_code TEXT,
    p_form_name TEXT,
    p_basis TEXT,
    p_source_url TEXT DEFAULT NULL,
    p_due_day INT DEFAULT 10 -- Day of following month
)
RETURNS VOID AS $$
DECLARE
    months INT[] := ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    m INT;
    period_start DATE;
    period_end DATE;
    raw_due DATE;
BEGIN
    FOREACH m IN ARRAY months LOOP
        period_start := DATE(p_year || '-' || m || '-01');
        period_end := (period_start + INTERVAL '1 month' - INTERVAL '1 day')::DATE;
        raw_due := (period_end + INTERVAL '1 month')::DATE;
        raw_due := DATE_TRUNC('month', raw_due)::DATE + (p_due_day - 1);

        INSERT INTO ph_tax.calendar (
            entity, form_code, form_name, period_type,
            period_start, period_end, due_date, due_date_adjusted,
            basis, source_url
        ) VALUES (
            'ALL',
            p_form_code,
            p_form_name,
            'monthly',
            period_start,
            period_end,
            raw_due,
            ph_tax.adjust_due_date(raw_due),
            p_basis,
            p_source_url
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- RLS Policies
ALTER TABLE ph_tax.docs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ph_tax.calendar ENABLE ROW LEVEL SECURITY;
ALTER TABLE ph_tax.holidays ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read
CREATE POLICY "Enable read for authenticated" ON ph_tax.docs
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read for authenticated" ON ph_tax.calendar
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read for authenticated" ON ph_tax.holidays
    FOR SELECT USING (auth.role() = 'authenticated');

-- Allow service role to insert/update
CREATE POLICY "Enable all for service role" ON ph_tax.docs
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Enable all for service role" ON ph_tax.calendar
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Enable all for service role" ON ph_tax.holidays
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Seed Philippine holidays for 2025
INSERT INTO ph_tax.holidays (holiday_date, holiday_name, holiday_type, proclamation) VALUES
('2025-01-01', 'New Year''s Day', 'Regular', 'R.A. 4166'),
('2025-01-25', 'Chinese New Year', 'Special Non-Working', 'Proclamation No. 90, s. 2024'),
('2025-02-25', 'EDSA People Power Revolution Anniversary', 'Special Non-Working', 'Proclamation No. 90, s. 2024'),
('2025-04-09', 'Araw ng Kagitingan (Day of Valor)', 'Regular', 'Proclamation No. 90, s. 2024'),
('2025-04-17', 'Maundy Thursday', 'Regular', 'Proclamation No. 90, s. 2024'),
('2025-04-18', 'Good Friday', 'Regular', 'Proclamation No. 90, s. 2024'),
('2025-04-19', 'Black Saturday', 'Special Non-Working', 'Proclamation No. 90, s. 2024'),
('2025-05-01', 'Labor Day', 'Regular', 'Presidential Decree No. 442'),
('2025-06-12', 'Independence Day', 'Regular', 'R.A. 4166'),
('2025-08-21', 'Ninoy Aquino Day', 'Special Non-Working', 'R.A. 9256'),
('2025-08-25', 'National Heroes Day', 'Regular', 'R.A. 9492'),
('2025-11-01', 'All Saints'' Day', 'Special Non-Working', 'Proclamation No. 90, s. 2024'),
('2025-11-30', 'Bonifacio Day', 'Regular', 'R.A. 9492'),
('2025-12-08', 'Feast of the Immaculate Conception', 'Special Non-Working', 'Proclamation No. 90, s. 2024'),
('2025-12-24', 'Christmas Eve', 'Special Non-Working', 'Proclamation No. 90, s. 2024'),
('2025-12-25', 'Christmas Day', 'Regular', 'Presidential Decree No. 1561'),
('2025-12-26', 'Additional Special Non-Working Day', 'Special Non-Working', 'Proclamation No. 90, s. 2024'),
('2025-12-30', 'Rizal Day', 'Regular', 'R.A. 9492'),
('2025-12-31', 'Last Day of the Year', 'Special Non-Working', 'Proclamation No. 90, s. 2024')
ON CONFLICT (holiday_date) DO NOTHING;

-- Seed 2025 BIR filing calendar
SELECT ph_tax.generate_quarterly_deadlines(
    2025,
    '2550Q',
    'Quarterly Value-Added Tax Return',
    'RMC 5-2023, Form 2550Q Guidelines (Apr 2024)',
    'https://bir-cdn.bir.gov.ph/BIR/pdf/2550Q%20guidelines%20April%202024_final.pdf',
    25 -- 25 days after quarter end
);

SELECT ph_tax.generate_monthly_deadlines(
    2025,
    '1601-C',
    'Monthly Remittance Return of Income Taxes Withheld on Compensation',
    'NIRC Sec. 58, RR 2-98',
    'https://bir-cdn.bir.gov.ph/local/pdf/1601C%20final%20Jan%202018%20with%20DPA.pdf',
    10 -- 10th day of following month
);

SELECT ph_tax.generate_quarterly_deadlines(
    2025,
    '1601-EQ',
    'Quarterly Remittance Return of Creditable Income Taxes Withheld (Expanded)',
    'NIRC Sec. 58, RR 2-98 as amended',
    'https://www.bir.gov.ph/bir-forms',
    25
);

-- Grant permissions
GRANT USAGE ON SCHEMA ph_tax TO authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA ph_tax TO service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA ph_tax TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA ph_tax TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ph_tax TO service_role, authenticated;

COMMENT ON SCHEMA ph_tax IS 'Philippine BIR tax compliance: RAG corpus, filing calendar, holiday rules';
COMMENT ON TABLE ph_tax.docs IS 'Authoritative BIR documents for RAG-based Q&A with citations';
COMMENT ON TABLE ph_tax.calendar IS 'BIR filing calendar with holiday-adjusted due dates';
COMMENT ON TABLE ph_tax.holidays IS 'Philippine regular and special non-working holidays';
COMMENT ON FUNCTION ph_tax.adjust_due_date IS 'Adjusts due date forward to next business day (skips weekends and holidays)';
