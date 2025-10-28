-- Superset DSN Seeder
-- This script seeds the Superset database with initial Odoo data source configuration

-- Create extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create a table to track seeded data sources
CREATE TABLE IF NOT EXISTS seeded_datasources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    datasource_name VARCHAR(255) NOT NULL,
    connection_string TEXT NOT NULL,
    seeded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(datasource_name)
);

-- Insert Odoo database connection information
-- Note: This is informational only. Actual datasource creation happens through Superset UI or API
INSERT INTO seeded_datasources (datasource_name, connection_string)
VALUES (
    'odoo_production',
    'postgresql://odoo:changeme@odoo-db:5432/odoo'
)
ON CONFLICT (datasource_name) DO UPDATE
SET connection_string = EXCLUDED.connection_string,
    seeded_at = CURRENT_TIMESTAMP;

-- Create views for common Odoo analytics queries
-- Note: These would need to be created in the Odoo database, not Superset database
-- This is provided as reference SQL

COMMENT ON TABLE seeded_datasources IS 'Tracks data sources that have been seeded into Superset';

-- Log successful execution
DO $$
BEGIN
    RAISE NOTICE 'Superset DSN seeder completed successfully';
END $$;
