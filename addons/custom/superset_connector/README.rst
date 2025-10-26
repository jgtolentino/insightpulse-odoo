====================
Superset Connector
====================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-InsightPulseAI%2Finsightpulse--odoo-lightgray.png?logo=github
    :target: https://github.com/InsightPulseAI/insightpulse-odoo/tree/main/addons/custom/superset_connector
    :alt: InsightPulseAI/insightpulse-odoo

|badge1| |badge2| |badge3|

This module integrates Apache Superset dashboards into Odoo with secure authentication, SSO, and embedded visualization capabilities.

**Table of contents**

.. contents::
   :local:

Features
========

* Embed Superset dashboards directly in Odoo views
* Guest token-based SSO authentication
* Content Security Policy (CSP) headers for secure embedding
* Automatic token lifecycle management
* Dashboard configuration and management interface
* Support for multiple Superset instances

Installation
============

Requirements
------------

* Apache Superset instance (v2.0+)
* Odoo 19.0+
* Python packages: No additional packages required
* PostgreSQL database for analytics views

Install Module
--------------

1. Copy this module to your Odoo addons directory
2. Update Apps List in Odoo
3. Search for "Superset Connector"
4. Click Install

Database Setup
--------------

After installation, you need to create the analytics views in your database:

.. code-block:: bash

   psql -U odoo_user -d odoo_database -f insightpulse_odoo/sql/views/erp_analytics_views.sql

Configuration
=============

Superset Instance Configuration
--------------------------------

1. Navigate to **Settings → Superset → Configurations**
2. Click **Create** to add a new Superset instance
3. Fill in the following fields:

   * **Configuration Name**: A descriptive name for this instance
   * **Superset Base URL**: URL of your Superset instance (e.g., https://superset.example.com)
   * **API Key**: Superset API key for authentication
   * **Allowed Origins**: Comma-separated list of allowed origins for CSP
   * **Token Expiry (Hours)**: Default token expiration time (default: 24 hours)

4. Click **Save**
5. Click **Test Connection** to verify the configuration

Dashboard Configuration
-----------------------

1. Navigate to **Settings → Superset → Dashboards**
2. Click **Create** to add a dashboard
3. Fill in the fields:

   * **Dashboard Name**: Display name in Odoo
   * **Superset Dashboard ID**: UUID from Superset dashboard URL
   * **Superset Configuration**: Select the configured instance
   * **Description**: Optional description
   * **Active**: Check to enable the dashboard

4. Click **Save**

Security Configuration
----------------------

Content Security Policy (CSP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module automatically adds CSP headers to embedded dashboard views. Configure allowed origins in the Superset Configuration.

Default CSP directives:

* ``default-src 'self'``
* ``frame-src 'self' <allowed-origins>``
* ``connect-src 'self' <allowed-origins>``
* ``script-src 'self' 'unsafe-inline' 'unsafe-eval'``
* ``style-src 'self' 'unsafe-inline'``

Token Management
~~~~~~~~~~~~~~~~

Guest tokens are automatically generated with the following security features:

* 256-bit cryptographically secure random tokens
* Configurable expiration time (default: 24 hours)
* Automatic cleanup of expired tokens
* Usage tracking and statistics
* IP address and user agent logging

Usage
=====

Embedding Dashboards
--------------------

Access embedded dashboards using these URLs:

**List all dashboards:**

.. code-block::

   https://your-odoo.example.com/superset/dashboards

**View specific dashboard:**

.. code-block::

   https://your-odoo.example.com/superset/dashboards?dashboard_id=<uuid>

**Direct embed:**

.. code-block::

   https://your-odoo.example.com/superset/embed/<dashboard-record-id>

Token Management
----------------

Tokens are automatically managed by the system:

* Created on first access
* Reused if valid token exists
* Auto-refreshed before expiry
* Cleaned up by scheduled cron job

**Manual token operations:**

Refresh token (JSON-RPC):

.. code-block:: python

   result = self.env['superset.token'].get_or_create_token(
       dashboard_id=dashboard.id,
       force_new=True
   )

View token statistics:

.. code-block:: python

   stats = self.env['superset.token'].get_token_stats()
   # Returns: total_tokens, active_tokens, expired_tokens, most_used_tokens

Scheduled Jobs
--------------

The module includes a cron job for token cleanup:

* **Name**: Cleanup Expired Superset Tokens
* **Frequency**: Daily at 2:00 AM
* **Actions**:
  * Deactivate expired tokens
  * Delete inactive tokens older than 30 days

Configure in **Settings → Technical → Automation → Scheduled Actions**.

Known issues / Roadmap
======================

Known Issues
------------

* Superset must be configured to allow guest tokens
* Cross-origin cookies may require SameSite configuration
* Some Superset features may not work in embedded mode

Roadmap
-------

* v19.0.2: Real-time dashboard refresh via websockets
* v19.0.3: Multi-dashboard comparison views
* v19.0.4: Custom filter integration from Odoo
* v19.0.5: Export dashboard as PDF/PNG
* v19.0.6: Dashboard template marketplace

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/InsightPulseAI/insightpulse-odoo/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* InsightPulseAI

Contributors
------------

* InsightPulseAI Team <team@insightpulseai.net>

Maintainers
-----------

This module is maintained by InsightPulseAI.

.. image:: https://insightpulseai.net/logo.png
   :alt: InsightPulseAI
   :target: https://insightpulseai.net

InsightPulseAI is a business intelligence and analytics platform for modern enterprises.

To contribute to this module, please visit https://github.com/InsightPulseAI/insightpulse-odoo.
