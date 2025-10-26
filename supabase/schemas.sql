-- Supabase Schema Configuration for InsightPulse Odoo
-- Layered architecture: raw → silver → gold → ml → predictions

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Schema: odoo_raw - 1:1 mirror of Odoo tables
CREATE SCHEMA IF NOT EXISTS odoo_raw;
GRANT USAGE ON SCHEMA odoo_raw TO authenticated;
GRANT USAGE ON SCHEMA odoo_raw TO service_role;

-- Schema: odoo_silver - cleaned and denormalized views
CREATE SCHEMA IF NOT EXISTS odoo_silver;
GRANT USAGE ON SCHEMA odoo_silver TO authenticated;
GRANT USAGE ON SCHEMA odoo_silver TO service_role;

-- Schema: analytics_gold - materialized views for BI
CREATE SCHEMA IF NOT EXISTS analytics_gold;
GRANT USAGE ON SCHEMA analytics_gold TO authenticated;
GRANT USAGE ON SCHEMA analytics_gold TO service_role;

-- Schema: ml_features - feature tables for ML training
CREATE SCHEMA IF NOT EXISTS ml_features;
GRANT USAGE ON SCHEMA ml_features TO authenticated;
GRANT USAGE ON SCHEMA ml_features TO service_role;

-- Schema: predictions - model outputs
CREATE SCHEMA IF NOT EXISTS predictions;
GRANT USAGE ON SCHEMA predictions TO authenticated;
GRANT USAGE ON SCHEMA predictions TO service_role;

-- Schema: ops - CDC watermarks and job logs
CREATE SCHEMA IF NOT EXISTS ops;
GRANT USAGE ON SCHEMA ops TO authenticated;
GRANT USAGE ON SCHEMA ops TO service_role;

-- Ops tables for CDC tracking
CREATE TABLE IF NOT EXISTS ops.cdc_watermarks (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    last_synced_at TIMESTAMPTZ DEFAULT NOW(),
    last_synced_id INTEGER,
    sync_status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ops.job_logs (
    id SERIAL PRIMARY KEY,
    job_name TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    records_processed INTEGER,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Example ML feature table for subscription churn
CREATE TABLE IF NOT EXISTS ml_features.subscription_training (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL,
    partner_id INTEGER NOT NULL,
    mrr DECIMAL(10,2),
    subscription_age_days INTEGER,
    invoice_count INTEGER,
    late_payment_count INTEGER,
    support_ticket_count INTEGER,
    churn BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Example prediction table
CREATE TABLE IF NOT EXISTS predictions.subscription_churn (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL,
    prediction BOOLEAN,
    confidence DECIMAL(5,4),
    prediction_date TIMESTAMPTZ DEFAULT NOW(),
    model_version TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Set up Row Level Security (RLS)
ALTER TABLE ml_features.subscription_training ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions.subscription_churn ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.cdc_watermarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.job_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Service role can access everything
CREATE POLICY "service_role_full_access" ON ml_features.subscription_training
    FOR ALL TO service_role USING (true);

CREATE POLICY "service_role_full_access" ON predictions.subscription_churn
    FOR ALL TO service_role USING (true);

-- Authenticated users can only read
CREATE POLICY "authenticated_read_access" ON ml_features.subscription_training
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "authenticated_read_access" ON predictions.subscription_churn
    FOR SELECT TO authenticated USING (true);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_subscription_training_subscription_id 
    ON ml_features.subscription_training(subscription_id);
    
CREATE INDEX IF NOT EXISTS idx_subscription_churn_subscription_id 
    ON predictions.subscription_churn(subscription_id);
    
CREATE INDEX IF NOT EXISTS idx_subscription_churn_prediction_date 
    ON predictions.subscription_churn(prediction_date);

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for updated_at
CREATE TRIGGER update_cdc_watermarks_updated_at 
    BEFORE UPDATE ON ops.cdc_watermarks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
