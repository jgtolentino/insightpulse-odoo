# dbt Staging Models

This directory contains staging models that clean and standardize raw Odoo data from the `odoo_raw` schema.

## Purpose

Staging models serve as the foundation layer for all downstream transformations. They:
- Rename columns to business-friendly names
- Cast data types appropriately
- Filter out inactive/cancelled records (by default)
- Add computed flags for common business logic
- Preserve raw data as JSONB for flexibility

## Available Models

### stg_partners.sql
**Source**: `odoo_raw.res_partner`  
**Purpose**: Customer, vendor, and contact master data

**Key transformations**:
- Standardized naming (partner_id, partner_name, etc.)
- Separate contact methods (email, phone, mobile)
- Address fields normalized
- Tax ID extraction from VAT field
- Active/inactive filtering

**Usage**:
```sql
SELECT * FROM staging.stg_partners
WHERE is_company = true
  AND customer_rank > 0;
```

### stg_invoices.sql
**Source**: `odoo_raw.account_move`  
**Purpose**: Customer invoices and vendor bills

**Key transformations**:
- Move type categorization (customer/vendor/other)
- Amount fields with consistent naming
- Payment state tracking
- Overdue flag calculation
- Origin tracking (SO/PO reference)

**Usage**:
```sql
SELECT * FROM staging.stg_invoices
WHERE move_category = 'customer'
  AND is_overdue = true;
```

### stg_sales_orders.sql
**Source**: `odoo_raw.sale_order`  
**Purpose**: Sales order data

**Key transformations**:
- Order/quote differentiation
- Date standardization
- Invoice status tracking
- Salesperson/team attribution

**Usage**:
```sql
SELECT * FROM staging.stg_sales_orders
WHERE is_confirmed = true
  AND is_fully_invoiced = false;
```

## Configuration

All staging models use:
- **Materialization**: `table` (for fast queries)
- **Schema**: `staging`
- **Refresh**: Daily (via dbt Cloud or cron)
- **Tags**: `staging`, `daily`, plus specific tags

## Data Quality Tests

Each model should have:
- Primary key uniqueness test
- Not null tests for critical fields
- Referential integrity tests (where applicable)
- Custom business logic tests

Example test (add to `schema.yml`):
```yaml
models:
  - name: stg_partners
    columns:
      - name: partner_id
        tests:
          - unique
          - not_null
      - name: partner_name
        tests:
          - not_null
```

## Dependencies

These models depend on:
- Source tables in `odoo_raw` schema
- Airbyte sync completing successfully
- Source configuration in `sources.yml`

## Next Steps

After staging models are stable:
1. Create intermediate models (business logic aggregations)
2. Create semantic models (wide tables for BI tools)
3. Create metrics models (KPIs and calculated fields)

## Maintenance

- Review and update quarterly as Odoo schema changes
- Add new fields as business needs evolve
- Document breaking changes in CHANGELOG
