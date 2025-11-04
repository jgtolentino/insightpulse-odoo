-- Dataset: dim_employee
-- Description: Employee dimension table with department and role information
-- Schema: analytics
-- Refresh: Daily via CDC

SELECT
    employee_key,
    employee_id,
    employee_name,
    email,
    phone,
    department_name,
    department_id,
    job_title,
    manager_name,
    company_id,
    company_name,
    is_active,
    hire_date,
    created_date,
    updated_date
FROM analytics.dim_employee
WHERE is_active = true
ORDER BY employee_name;

-- Table reference for Superset dataset configuration:
-- Table name: analytics.dim_employee
-- Type: Dimension Table
-- Columns:
--   - employee_key (INTEGER): Employee surrogate key (Primary Key)
--   - employee_id (INTEGER): Employee ID from source system
--   - employee_name (VARCHAR): Employee name
--   - email (VARCHAR): Email address
--   - phone (VARCHAR): Phone number
--   - department_name (VARCHAR): Department name
--   - department_id (INTEGER): Department ID
--   - job_title (VARCHAR): Job title
--   - manager_name (VARCHAR): Manager name
--   - company_id (INTEGER): Company ID
--   - company_name (VARCHAR): Company name
--   - is_active (BOOLEAN): Active employee flag
--   - hire_date (DATE): Hire date
--   - created_date (DATE): Record creation date
--   - updated_date (DATE): Record update date
