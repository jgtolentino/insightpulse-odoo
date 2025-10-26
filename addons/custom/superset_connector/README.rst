====================
Superset Connector
====================

.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl-3.0.en.html
   :alt: License: LGPL-3

This module provides seamless integration between Odoo and Apache Superset for advanced Business Intelligence and data visualization.

**Table of contents**

.. contents::
   :local:

Overview
========

Apache Superset is a modern, enterprise-ready business intelligence web application. This connector module enables:

* **Secure Dashboard Embedding**: Embed Superset dashboards directly in Odoo with guest token authentication
* **Row-Level Security (RLS)**: Automatic data filtering based on Odoo user permissions and company access
* **Multi-Company Support**: Isolated data access for multi-company Odoo installations
* **SSO Integration**: Single sign-on with automatic token management
* **Content Security Policy**: Configurable CSP headers for secure iframe embedding
* **Analytics Views**: Pre-built SQL views for common Odoo analytics use cases

Features
========

Dashboard Embedding
-------------------

Embed Superset dashboards in Odoo using secure guest tokens:

* Automatic token generation and refresh
* Token expiry management
* User-specific access control
* Company-based data filtering

Row-Level Security
------------------

Enforce data access policies:

* Filter data by company_id automatically
* Custom RLS filter clauses
* Integration with Odoo security groups
* Multi-tenant data isolation

Analytics Views
---------------

Pre-built SQL views for:

* **Sales Analytics**: Daily KPIs, product performance, customer lifetime value
* **Inventory Analytics**: Stock levels, inventory turnover
* **Financial Analytics**: AR aging, monthly revenue
* **HR Analytics**: Employee headcount by department

Configuration
=============

Installation
------------

1. Install the module from Apps menu
2. Ensure ``requests`` Python library is installed: ``pip install requests``
3. Create analytics views in PostgreSQL (see SQL file in module)

Superset Configuration
----------------------

1. Navigate to **Settings > General Settings > Superset Integration**
2. Configure the following:

   * **Superset URL**: Base URL of your Superset instance (e.g., ``https://superset.example.com``)
   * **Username**: Superset admin username
   * **Password**: Superset admin password
   * **Database ID**: Superset database ID for Odoo connection
   * **Enable RLS**: Enable row-level security (recommended)
   * **Token Expiry**: Token lifetime in seconds (default: 3600)
   * **CSP Enabled**: Enable Content Security Policy headers (recommended)

Database Setup
--------------

1. Create a read-only PostgreSQL user for Superset::

    CREATE USER superset_readonly WITH PASSWORD 'secure_password';
    GRANT CONNECT ON DATABASE odoo TO superset_readonly;
    GRANT USAGE ON SCHEMA public TO superset_readonly;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_readonly;

2. Execute the analytics views SQL script::

    psql -U odoo -d your_db -f addons/custom/superset_connector/sql/erp_analytics_views.sql

3. Grant access to views::

    GRANT SELECT ON vw_sales_kpi_day TO superset_readonly;
    GRANT SELECT ON vw_product_performance TO superset_readonly;
    GRANT SELECT ON vw_customer_ltv TO superset_readonly;
    -- ... grant access to all analytics views

Superset Database Connection
-----------------------------

In Apache Superset:

1. Go to **Data > Databases**
2. Click **+ Database**
3. Configure PostgreSQL connection::

    postgresql://superset_readonly:password@host:5432/odoo

4. Test connection
5. Save database

Row-Level Security in Superset
-------------------------------

1. In Superset, go to **Data > Row Level Security**
2. Create a new RLS rule:

   * **Filter Name**: Multi-Company Filter
   * **Tables**: Select all analytics views
   * **Clause**::

       company_id IN (
           SELECT company_id 
           FROM user_company_access 
           WHERE user_email = '{{ current_username() }}'
       )

3. Save and test

Usage
=====

Embedding Dashboards
--------------------

**Method 1: Direct URL**

Access dashboards via URL::

    https://your-odoo.com/superset/dashboard/<dashboard-uuid>

**Method 2: Using Token Records**

1. Go to **Superset > Tokens**
2. Create a new token:

   * **Name**: Dashboard name
   * **Dashboard ID**: UUID from Superset
   * **RLS Filter**: Optional custom filter

3. Click **Generate Token**
4. Share the dashboard URL with users

**Method 3: Programmatic Access**

.. code-block:: python

   # In Odoo Python code
   token = self.env['superset.token'].get_or_create_token(
       dashboard_id='1234-5678-9abc-def0',
       rls_filter='department_id = 5'
   )
   dashboard_url = f'/superset/dashboard/1234-5678-9abc-def0'

Creating Analytics Views
-------------------------

Add custom analytics views:

1. Create SQL view in PostgreSQL
2. Grant SELECT to ``superset_readonly`` user
3. Add dataset in Superset
4. Create charts and dashboards

Example custom view::

    CREATE OR REPLACE VIEW vw_my_custom_metrics AS
    SELECT 
        date_trunc('day', create_date) as date,
        company_id,
        COUNT(*) as record_count
    FROM my_model
    GROUP BY date, company_id;

Security
========

Best Practices
--------------

* Use read-only database user for Superset
* Enable RLS in both Odoo and Superset
* Enable CSP headers
* Use HTTPS for all connections
* Rotate Superset credentials regularly
* Monitor token usage and expiry

Data Isolation
--------------

Multi-company data is automatically isolated:

* RLS filters enforce company_id restrictions
* Users only see data for their assigned companies
* Cross-company reports require explicit permissions

Known Issues / Roadmap
======================

Known Issues
------------

* Token refresh requires manual action (planned: automatic refresh)
* Dashboard list view is basic (planned: enhanced UI with thumbnails)

Roadmap
-------

* Automatic token refresh before expiry
* Dashboard preview thumbnails
* Superset dataset synchronization
* Scheduled cache warming
* Enhanced monitoring and logging

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/jgtolentino/insightpulse-odoo/issues>`_.

In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smash it by providing detailed and welcomed feedback.

Credits
=======

Authors
-------

* InsightPulseAI

Contributors
------------

* InsightPulseAI Team

Maintainers
-----------

This module is maintained by InsightPulseAI.

.. image:: https://avatars.githubusercontent.com/u/jgtolentino
   :alt: InsightPulseAI
   :target: https://github.com/jgtolentino

Further information
===================

* Documentation: `docs/SUPERSET_INTEGRATION.md <../../docs/SUPERSET_INTEGRATION.md>`_
* BI Architecture: `docs/BI_ARCHITECTURE.md <../../docs/BI_ARCHITECTURE.md>`_
* Dashboard Design: `docs/SUPERSET_DASHBOARDS.md <../../docs/SUPERSET_DASHBOARDS.md>`_

License
=======

This module is licensed under LGPL-3.

Please refer to the `LICENSE <https://www.gnu.org/licenses/lgpl-3.0.en.html>`_ file for details.
