# Superset-Odoo Integration Architecture

## Overview

This document defines the complete integration architecture between Apache Superset and Odoo ERP, including SSO authentication, embedded analytics via iframes, row-level security (RLS) for multi-tenant isolation, and the `superset_connector` Odoo module requirements.

## Integration Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Odoo Web Interface                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Dashboard Menu Item                                      │  │
│  │  ↓                                                        │  │
│  │  [Embedded Superset Dashboard via iframe]                │  │
│  │  - SSO Authentication via Guest Token                    │  │
│  │  - RLS Filtering by company_id                           │  │
│  │  - Real-time data refresh                                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
                    JWT Token Generation
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Apache Superset (DO App)                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Guest Token Authentication                               │  │
│  │  ↓                                                        │  │
│  │  RLS Policy Enforcement                                   │  │
│  │  ↓                                                        │  │
│  │  Dashboard Rendering                                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
                        SQL Queries
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Supabase PostgreSQL 15                         │
│  - analytics.* schema with fact/dimension tables                │
│  - RLS policies enforced at database level                      │
│  - Materialized views for performance                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## SSO Authentication Flow

### Authentication Strategy

Superset supports multiple authentication methods. For Odoo integration, we use **Guest Token** authentication for seamless embedding.

### Guest Token Authentication Flow

```
┌─────────┐                    ┌─────────┐                    ┌──────────┐
│  Odoo   │                    │Superset │                    │ Supabase │
│  User   │                    │  API    │                    │    DB    │
└────┬────┘                    └────┬────┘                    └────┬─────┘
     │                              │                              │
     │ 1. Click Dashboard Menu      │                              │
     ├──────────────────────────────>                              │
     │                              │                              │
     │ 2. Odoo generates JWT token  │                              │
     │    with user context         │                              │
     │    (email, company_id, role) │                              │
     │                              │                              │
     │ 3. Request Guest Token       │                              │
     ├──────────────────────────────>                              │
     │                              │                              │
     │                              │ 4. Validate JWT              │
     │                              │                              │
     │                              │ 5. Query user permissions    │
     │                              ├──────────────────────────────>
     │                              │                              │
     │                              │ 6. Return company access     │
     │                              <──────────────────────────────┤
     │                              │                              │
     │ 7. Return Guest Token        │                              │
     <──────────────────────────────┤                              │
     │                              │                              │
     │ 8. Render iframe with token  │                              │
     │                              │                              │
     │ 9. Load dashboard            │                              │
     ├──────────────────────────────>                              │
     │                              │                              │
     │                              │ 10. Query with RLS           │
     │                              ├──────────────────────────────>
     │                              │                              │
     │                              │ 11. Return filtered data     │
     │                              <──────────────────────────────┤
     │                              │                              │
     │ 12. Display dashboard        │                              │
     <──────────────────────────────┤                              │
     │                              │                              │
```

### Implementation Details

#### Step 1: Odoo JWT Token Generation

```python
# superset_connector/models/superset_config.py

import jwt
import datetime
from odoo import models, fields, api

class SupersetConnection(models.Model):
    _name = "superset.connection"

    def _generate_jwt_token(self, user_id, company_ids):
        """Generate JWT token for Superset authentication"""
        user = self.env['res.users'].browse(user_id)

        payload = {
            'user_email': user.login,
            'user_id': user.id,
            'user_name': user.name,
            'company_ids': company_ids,
            'role': self._get_user_superset_role(user),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'iat': datetime.datetime.utcnow(),
        }

        # Use shared secret key between Odoo and Superset
        secret_key = self.env['ir.config_parameter'].sudo().get_param(
            'superset.jwt_secret_key'
        )

        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    def _get_user_superset_role(self, user):
        """Determine Superset role based on Odoo groups"""
        if user.has_group('base.group_system'):
            return 'admin'
        elif user.has_group('superset_connector.group_superset_analyst'):
            return 'analyst'
        else:
            return 'viewer'
```

#### Step 2: Request Superset Guest Token

```python
# superset_connector/models/superset_config.py

import requests
import json

class SupersetConnection(models.Model):
    _name = "superset.connection"

    def get_guest_token(self, dashboard_id, user_id=None):
        """
        Generate Superset guest token for embedding

        Args:
            dashboard_id: Superset dashboard ID or UUID
            user_id: Odoo user ID (defaults to current user)

        Returns:
            Guest token string
        """
        self.ensure_one()

        if not user_id:
            user_id = self.env.user.id

        user = self.env['res.users'].browse(user_id)
        company_ids = user.company_ids.ids

        # Get Superset API access token
        access_token = self._get_access_token()

        # Prepare guest token request
        guest_user = {
            'username': user.login,
            'first_name': user.name.split()[0] if user.name else 'User',
            'last_name': ' '.join(user.name.split()[1:]) if len(user.name.split()) > 1 else '',
        }

        # RLS filters based on user's companies
        rls_rules = [
            {
                'clause': f"company_id IN ({','.join(map(str, company_ids))})"
            }
        ]

        # Guest token configuration
        payload = {
            'resources': [
                {
                    'type': 'dashboard',
                    'id': str(dashboard_id)
                }
            ],
            'rls': rls_rules,
            'user': guest_user
        }

        # Request guest token from Superset
        response = requests.post(
            f"{self.url.rstrip('/')}/api/v1/security/guest_token/",
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        else:
            raise Exception(f'Failed to get guest token: {response.text}')
```

#### Step 3: Generate Embed URL

```python
# superset_connector/models/superset_dashboard.py

class SupersetDashboard(models.Model):
    _name = "superset.dashboard"

    def get_embed_url(self, user_id=None):
        """
        Generate embeddable URL with guest token

        Returns:
            Full iframe URL with authentication
        """
        self.ensure_one()

        # Get guest token
        guest_token = self.connection_id.get_guest_token(
            self.dashboard_uuid or self.dashboard_id,
            user_id
        )

        # Build embed URL
        base_url = self.connection_id.url.rstrip('/')
        dashboard_ref = self.dashboard_uuid or self.dashboard_id

        embed_url = (
            f"{base_url}/superset/dashboard/{dashboard_ref}/"
            f"?standalone=true"
            f"&guest_token={guest_token}"
        )

        return embed_url

    def action_open_dashboard(self):
        """Open dashboard in new window or embedded view"""
        self.ensure_one()

        embed_url = self.get_embed_url()

        return {
            'type': 'ir.actions.act_url',
            'url': embed_url,
            'target': 'new',
        }
```

---

## Embedded iframe Integration

### Iframe Security Configuration

#### Superset Configuration

```python
# deploy/superset_config.py

# Allow embedding in Odoo iframes
HTTP_HEADERS = {
    'X-Frame-Options': 'SAMEORIGIN',
    # Or allow specific origins
    # 'X-Frame-Options': 'ALLOW-FROM https://your-odoo-instance.com',
}

# Content Security Policy
TALISMAN_CONFIG = {
    'frame_options': 'SAMEORIGIN',
    'frame_options_allow_from': 'https://your-odoo-instance.com',
    'content_security_policy': {
        'frame-ancestors': ["'self'", 'https://your-odoo-instance.com'],
    },
}

# Enable embedded features
FEATURE_FLAGS = {
    'EMBEDDABLE_CHARTS': True,
    'DASHBOARD_NATIVE_FILTERS_SET': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'ENABLE_TEMPLATE_PROCESSING': True,
}

# Guest token configuration
GUEST_TOKEN_JWT_SECRET = os.environ.get('SUPERSET_GUEST_TOKEN_SECRET', 'change-me-in-production')
GUEST_TOKEN_JWT_ALGO = 'HS256'
GUEST_TOKEN_JWT_EXP_SECONDS = 3600  # 1 hour
```

### Odoo View Integration

#### XML View Definition

```xml
<!-- superset_connector/views/superset_dashboard_views.xml -->

<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Dashboard Kanban View -->
    <record id="view_superset_dashboard_kanban" model="ir.ui.view">
        <field name="name">superset.dashboard.kanban</field>
        <field name="model">superset.dashboard</field>
        <field name="arch" type="xml">
            <kanban class="o_superset_dashboard_kanban">
                <field name="id"/>
                <field name="name"/>
                <field name="category"/>
                <field name="description"/>
                <templates>
                    <t t-name="kanban-box">
                        <div class="oe_kanban_card oe_kanban_global_click">
                            <div class="o_kanban_card_header">
                                <div class="o_kanban_card_header_title">
                                    <div class="o_primary">
                                        <strong><field name="name"/></strong>
                                    </div>
                                    <div class="o_secondary">
                                        <span class="badge badge-pill"
                                              t-att-class="{'badge-info': category == 'executive',
                                                           'badge-success': category == 'sales',
                                                           'badge-warning': category == 'operations',
                                                           'badge-primary': category == 'finance',
                                                           'badge-secondary': category == 'custom'}">
                                            <field name="category"/>
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div class="o_kanban_card_body">
                                <field name="description"/>
                            </div>
                            <div class="o_kanban_card_footer">
                                <button type="object"
                                        name="action_open_dashboard"
                                        class="btn btn-primary btn-sm">
                                    Open Dashboard
                                </button>
                                <button type="object"
                                        name="action_open_embedded"
                                        class="btn btn-secondary btn-sm">
                                    View Embedded
                                </button>
                            </div>
                        </div>
                    </t>
                </templates>
            </kanban>
        </field>
    </record>

    <!-- Embedded Dashboard View -->
    <record id="view_superset_dashboard_embedded" model="ir.ui.view">
        <field name="name">superset.dashboard.embedded</field>
        <field name="model">superset.dashboard</field>
        <field name="arch" type="xml">
            <form string="Dashboard" class="o_superset_dashboard_embedded">
                <header>
                    <button name="action_refresh_dashboard"
                            type="object"
                            string="Refresh"
                            class="btn-primary"/>
                    <button name="action_open_fullscreen"
                            type="object"
                            string="Fullscreen"
                            class="btn-secondary"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <h1><field name="name" readonly="1"/></h1>
                    </div>
                    <notebook>
                        <page string="Dashboard" name="dashboard">
                            <field name="embed_iframe" widget="html"
                                   options="{'style-inline': true, 'sandbox': false}"/>
                        </page>
                        <page string="Information" name="info">
                            <group>
                                <field name="description"/>
                                <field name="category"/>
                                <field name="last_sync_date"/>
                                <field name="dataset_count"/>
                            </group>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Menu Items -->
    <menuitem id="menu_superset_dashboards_root"
              name="Analytics"
              sequence="100"
              web_icon="superset_connector,static/description/icon.png"/>

    <menuitem id="menu_superset_dashboards"
              name="Dashboards"
              parent="menu_superset_dashboards_root"
              action="action_superset_dashboard_kanban"
              sequence="10"/>
</odoo>
```

#### Computed Field for iframe Embed

```python
# superset_connector/models/superset_dashboard.py

from odoo import models, fields, api
from markupsafe import Markup

class SupersetDashboard(models.Model):
    _name = "superset.dashboard"

    embed_iframe = fields.Html(
        string="Embedded Dashboard",
        compute="_compute_embed_iframe",
        sanitize=False
    )

    @api.depends('connection_id', 'dashboard_id', 'dashboard_uuid')
    def _compute_embed_iframe(self):
        """Generate iframe HTML for embedding"""
        for rec in self:
            if not rec.connection_id:
                rec.embed_iframe = '<p>No connection configured</p>'
                continue

            try:
                embed_url = rec.get_embed_url()

                iframe_html = f'''
                <div style="width: 100%; height: 100vh; overflow: hidden;">
                    <iframe
                        src="{embed_url}"
                        width="100%"
                        height="100%"
                        frameborder="0"
                        style="border: none; min-height: 800px;"
                        allowfullscreen
                        allow="clipboard-write; clipboard-read"
                    ></iframe>
                </div>
                '''

                rec.embed_iframe = Markup(iframe_html)

            except Exception as e:
                rec.embed_iframe = Markup(f'<p class="text-danger">Error loading dashboard: {str(e)}</p>')

    def action_open_embedded(self):
        """Open embedded view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'superset.dashboard',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('superset_connector.view_superset_dashboard_embedded').id,
            'target': 'current',
        }
```

### JavaScript Widget (Optional Enhancement)

```javascript
// superset_connector/static/src/js/superset_dashboard_widget.js

odoo.define('superset_connector.dashboard_widget', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var fieldRegistry = require('web.field_registry');

    var SupersetDashboardWidget = AbstractField.extend({
        template: 'SupersetDashboardIframe',

        _render: function () {
            var self = this;
            var $iframe = this.$('iframe');

            if (this.value) {
                $iframe.attr('src', this.value);

                // Listen for iframe messages (optional)
                window.addEventListener('message', function(event) {
                    if (event.origin === self.supersetOrigin) {
                        // Handle dashboard events
                        console.log('Dashboard event:', event.data);
                    }
                });
            }
        },
    });

    fieldRegistry.add('superset_dashboard', SupersetDashboardWidget);

    return SupersetDashboardWidget;
});
```

---

## Row-Level Security (RLS) Integration

### Multi-Tenant Isolation Strategy

RLS is enforced at three levels:

1. **Database Level** (Supabase PostgreSQL)
2. **Application Level** (Superset Guest Token)
3. **Query Level** (Superset SQL Lab)

### Database-Level RLS (Supabase)

Already defined in `SUPERSET_DATA_MODEL.md`, but key points:

```sql
-- Enable RLS on fact tables
ALTER TABLE analytics.fact_sales ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY company_isolation_policy ON analytics.fact_sales
    FOR SELECT
    TO authenticated
    USING (
        company_key IN (
            SELECT dc.company_key
            FROM analytics.dim_company dc
            JOIN analytics.user_company_access uca ON dc.company_id = uca.company_id
            WHERE uca.user_email = current_setting('request.jwt.claims', true)::json->>'email'
        )
    );
```

### Application-Level RLS (Superset Guest Token)

```python
# superset_connector/models/superset_config.py

def get_guest_token(self, dashboard_id, user_id=None):
    """Generate guest token with RLS rules"""

    user = self.env['res.users'].browse(user_id or self.env.user.id)
    company_ids = user.company_ids.ids

    # Build RLS clauses
    rls_rules = []

    # Company isolation
    rls_rules.append({
        'clause': f"company_id IN ({','.join(map(str, company_ids))})"
    })

    # Department-level filtering (if applicable)
    if user.employee_id and user.employee_id.department_id:
        rls_rules.append({
            'clause': f"department_id = {user.employee_id.department_id.id}",
            'tables': ['analytics.fact_expense']  # Only apply to expense table
        })

    # Sales team filtering (if not manager)
    if not user.has_group('sales_team.group_sale_manager'):
        if user.sale_team_id:
            rls_rules.append({
                'clause': f"sales_team_id = {user.sale_team_id.id}",
                'tables': ['analytics.fact_sales']
            })

    payload = {
        'resources': [{'type': 'dashboard', 'id': str(dashboard_id)}],
        'rls': rls_rules,
        'user': {
            'username': user.login,
            'first_name': user.name.split()[0] if user.name else 'User',
            'last_name': ' '.join(user.name.split()[1:]) if len(user.name.split()) > 1 else '',
        }
    }

    # Request token...
```

### User-Company Access Sync

```python
# superset_connector/models/superset_config.py

class SupersetConnection(models.Model):
    _name = "superset.connection"

    def sync_user_company_access(self):
        """
        Sync Odoo user-company mappings to Supabase
        for RLS enforcement
        """
        self.ensure_one()

        # Get all active users with company access
        users = self.env['res.users'].search([('active', '=', True)])

        access_data = []
        for user in users:
            for company in user.company_ids:
                access_data.append({
                    'user_email': user.login,
                    'company_id': company.id,
                    'role': self._get_user_superset_role(user),
                })

        # Sync to Supabase analytics.user_company_access table
        # This could be done via direct PostgreSQL connection or Supabase REST API

        import psycopg2

        conn = psycopg2.connect(
            host=self.env['ir.config_parameter'].sudo().get_param('supabase.host'),
            database=self.env['ir.config_parameter'].sudo().get_param('supabase.database'),
            user=self.env['ir.config_parameter'].sudo().get_param('supabase.user'),
            password=self.env['ir.config_parameter'].sudo().get_param('supabase.password'),
            port=5432
        )

        cur = conn.cursor()

        # Clear existing access
        cur.execute("DELETE FROM analytics.user_company_access")

        # Insert new access
        for data in access_data:
            cur.execute(
                """
                INSERT INTO analytics.user_company_access (user_email, company_id, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_email, company_id) DO UPDATE
                SET role = EXCLUDED.role, updated_at = CURRENT_TIMESTAMP
                """,
                (data['user_email'], data['company_id'], data['role'])
            )

        conn.commit()
        cur.close()
        conn.close()

        return True

    @api.model
    def cron_sync_user_access(self):
        """Scheduled job to sync user access daily"""
        connections = self.search([('active', '=', True)])
        for connection in connections:
            try:
                connection.sync_user_company_access()
            except Exception as e:
                _logger.error(f"Failed to sync user access for {connection.name}: {e}")
```

---

## Odoo Module: `superset_connector`

### Module Structure

```
superset_connector/
├── __init__.py
├── __manifest__.py
├── security/
│   ├── ir.model.access.csv
│   └── superset_security.xml
├── models/
│   ├── __init__.py
│   ├── superset_config.py
│   ├── superset_dashboard.py
│   └── superset_dataset.py
├── views/
│   ├── superset_config_views.xml
│   ├── superset_dashboard_views.xml
│   └── superset_dataset_views.xml
├── data/
│   ├── superset_dashboard_data.xml
│   └── superset_cron.xml
├── static/
│   ├── description/
│   │   └── icon.png
│   └── src/
│       ├── js/
│       │   └── superset_dashboard_widget.js
│       └── css/
│           └── superset_dashboard.css
└── README.md
```

### Manifest File

```python
# superset_connector/__manifest__.py

{
    'name': 'Superset BI Connector',
    'version': '1.0.0',
    'category': 'Business Intelligence',
    'summary': 'Apache Superset integration for embedded analytics',
    'description': """
        Superset BI Connector
        =====================

        Seamlessly integrate Apache Superset dashboards into Odoo:

        * Embedded dashboard views with SSO authentication
        * Row-level security for multi-tenant isolation
        * Automatic data synchronization
        * Pre-built dashboard templates
        * Real-time analytics

        Compatible with Odoo 19.0 and Apache Superset 3.0+
    """,
    'author': 'InsightPulse',
    'website': 'https://www.insightpulse.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'sale',
        'purchase',
        'account',
        'hr_expense',
    ],
    'external_dependencies': {
        'python': ['jwt', 'requests', 'psycopg2'],
    },
    'data': [
        'security/superset_security.xml',
        'security/ir.model.access.csv',
        'views/superset_config_views.xml',
        'views/superset_dashboard_views.xml',
        'views/superset_dataset_views.xml',
        'data/superset_dashboard_data.xml',
        'data/superset_cron.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'superset_connector/static/src/js/superset_dashboard_widget.js',
            'superset_connector/static/src/css/superset_dashboard.css',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
```

### Security Groups

```xml
<!-- superset_connector/security/superset_security.xml -->

<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Security Groups -->
        <record id="group_superset_viewer" model="res.groups">
            <field name="name">Superset Viewer</field>
            <field name="category_id" ref="base.module_category_business_intelligence"/>
            <field name="comment">Can view Superset dashboards</field>
        </record>

        <record id="group_superset_analyst" model="res.groups">
            <field name="name">Superset Analyst</field>
            <field name="category_id" ref="base.module_category_business_intelligence"/>
            <field name="implied_ids" eval="[(4, ref('group_superset_viewer'))]"/>
            <field name="comment">Can view and analyze Superset dashboards</field>
        </record>

        <record id="group_superset_manager" model="res.groups">
            <field name="name">Superset Manager</field>
            <field name="category_id" ref="base.module_category_business_intelligence"/>
            <field name="implied_ids" eval="[(4, ref('group_superset_analyst'))]"/>
            <field name="comment">Can manage Superset connections and dashboards</field>
        </record>

        <!-- Record Rules -->
        <record id="superset_dashboard_company_rule" model="ir.rule">
            <field name="name">Superset Dashboard: multi-company</field>
            <field name="model_id" ref="model_superset_dashboard"/>
            <field name="domain_force">
                ['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]
            </field>
        </record>
    </data>
</odoo>
```

### Access Rights

```csv
# superset_connector/security/ir.model.access.csv

id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_superset_connection_viewer,superset.connection.viewer,model_superset_connection,group_superset_viewer,1,0,0,0
access_superset_connection_manager,superset.connection.manager,model_superset_connection,group_superset_manager,1,1,1,1
access_superset_dashboard_viewer,superset.dashboard.viewer,model_superset_dashboard,group_superset_viewer,1,0,0,0
access_superset_dashboard_analyst,superset.dashboard.analyst,model_superset_dashboard,group_superset_analyst,1,1,0,0
access_superset_dashboard_manager,superset.dashboard.manager,model_superset_dashboard,group_superset_manager,1,1,1,1
access_superset_dataset_viewer,superset.dataset.viewer,model_superset_dataset,group_superset_viewer,1,0,0,0
access_superset_dataset_manager,superset.dataset.manager,model_superset_dataset,group_superset_manager,1,1,1,1
```

### Cron Jobs

```xml
<!-- superset_connector/data/superset_cron.xml -->

<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Sync user-company access daily -->
        <record id="ir_cron_sync_user_access" model="ir.cron">
            <field name="name">Superset: Sync User Access</field>
            <field name="model_id" ref="model_superset_connection"/>
            <field name="state">code</field>
            <field name="code">model.cron_sync_user_access()</field>
            <field name="interval_number">1</field>
            <field name="interval_type">days</field>
            <field name="numbercall">-1</field>
            <field name="active" eval="True"/>
        </record>

        <!-- Sync dashboards data hourly -->
        <record id="ir_cron_sync_dashboards" model="ir.cron">
            <field name="name">Superset: Sync Dashboard Data</field>
            <field name="model_id" ref="model_superset_dashboard"/>
            <field name="state">code</field>
            <field name="code">model.cron_sync_dashboards()</field>
            <field name="interval_number">1</field>
            <field name="interval_type">hours</field>
            <field name="numbercall">-1</field>
            <field name="active" eval="True"/>
        </record>

        <!-- Refresh materialized views in Supabase -->
        <record id="ir_cron_refresh_views" model="ir.cron">
            <field name="name">Superset: Refresh Materialized Views</field>
            <field name="model_id" ref="model_superset_connection"/>
            <field name="state">code</field>
            <field name="code">model.cron_refresh_materialized_views()</field>
            <field name="interval_number">1</field>
            <field name="interval_type">hours</field>
            <field name="numbercall">-1</field>
            <field name="active" eval="True"/>
        </record>
    </data>
</odoo>
```

---

## Configuration Requirements

### Environment Variables (Odoo)

```bash
# .env or odoo.conf

[superset]
# Superset server configuration
superset_url = https://superset.yourdomain.com
superset_admin_username = admin
superset_admin_password = secure_password

# JWT authentication
superset_jwt_secret_key = your-shared-secret-key-here
superset_jwt_algorithm = HS256

# Supabase connection (for direct DB sync)
supabase_host = db.xxxxxxxxxxxx.supabase.co
supabase_database = postgres
supabase_user = postgres
supabase_password = your-supabase-password
supabase_port = 5432

# Guest token settings
superset_guest_token_expiry = 3600  # 1 hour
```

### System Parameters (Odoo)

```python
# To set via Odoo shell or data XML

self.env['ir.config_parameter'].sudo().set_param('superset.url', 'https://superset.yourdomain.com')
self.env['ir.config_parameter'].sudo().set_param('superset.jwt_secret_key', 'your-secret-key')
self.env['ir.config_parameter'].sudo().set_param('supabase.host', 'db.xxxxxxxxxxxx.supabase.co')
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Install `superset_connector` module in Odoo
- [ ] Configure Superset connection settings
- [ ] Set up shared JWT secret key
- [ ] Configure Supabase database connection
- [ ] Create Superset dashboards
- [ ] Test guest token generation
- [ ] Verify RLS policies in Supabase
- [ ] Configure CORS and iframe permissions in Superset

### Post-Deployment

- [ ] Sync user-company access mappings
- [ ] Test embedded dashboard loading
- [ ] Verify multi-tenant isolation
- [ ] Configure scheduled cron jobs
- [ ] Set up monitoring and alerts
- [ ] Train users on dashboard access
- [ ] Document dashboard usage

---

## Troubleshooting

### Common Issues

#### Issue 1: iframe Not Loading

**Symptoms**: Dashboard shows blank or blocked iframe

**Solutions**:
1. Check `X-Frame-Options` in Superset config
2. Verify CORS configuration
3. Check browser console for security errors
4. Ensure guest token is valid

```python
# Test guest token generation
connection = self.env['superset.connection'].browse(1)
token = connection.get_guest_token(dashboard_id='your-dashboard-uuid')
print(f"Token: {token}")
```

#### Issue 2: RLS Not Working

**Symptoms**: Users see data from other companies

**Solutions**:
1. Verify RLS policies enabled in Supabase
2. Check user-company access mappings
3. Test guest token RLS clauses
4. Review Superset logs for RLS errors

```sql
-- Test RLS in Supabase
SELECT * FROM analytics.user_company_access WHERE user_email = 'test@example.com';
```

#### Issue 3: Authentication Failures

**Symptoms**: 401 Unauthorized errors

**Solutions**:
1. Verify JWT secret key matches between Odoo and Superset
2. Check token expiry settings
3. Review Superset authentication logs
4. Test API access token generation

```python
# Test Superset API connection
connection = self.env['superset.connection'].browse(1)
connection.action_test_connection()
```

---

## Performance Optimization

### Caching Strategy

```python
# Implement caching for guest tokens

from werkzeug.contrib.cache import RedisCache

class SupersetConnection(models.Model):
    _name = "superset.connection"

    _cache = None

    @api.model
    def _get_cache(self):
        if not self._cache:
            self._cache = RedisCache(
                host='localhost',
                port=6379,
                default_timeout=300  # 5 minutes
            )
        return self._cache

    def get_guest_token_cached(self, dashboard_id, user_id):
        """Get cached guest token or generate new one"""
        cache_key = f"superset_token_{user_id}_{dashboard_id}"

        cache = self._get_cache()
        token = cache.get(cache_key)

        if not token:
            token = self.get_guest_token(dashboard_id, user_id)
            cache.set(cache_key, token, timeout=3000)  # 50 minutes

        return token
```

### Asynchronous Data Sync

```python
# Use Odoo queue_job for async syncing

from odoo.addons.queue_job.job import job

class SupersetDashboard(models.Model):
    _name = "superset.dashboard"
    _inherit = ['queue.job.mixin']

    @job
    def async_sync_data(self):
        """Sync data asynchronously"""
        self.ensure_one()
        return self.action_sync_data()

    def schedule_sync(self):
        """Schedule async sync job"""
        self.with_delay().async_sync_data()
```

---

## Security Best Practices

1. **Use HTTPS**: Always use HTTPS for both Odoo and Superset
2. **Rotate Keys**: Regularly rotate JWT secret keys
3. **Token Expiry**: Set reasonable token expiry times (1 hour recommended)
4. **Audit Logs**: Enable audit logging for dashboard access
5. **Rate Limiting**: Implement rate limiting on guest token API
6. **Principle of Least Privilege**: Grant minimum necessary permissions
7. **Regular Updates**: Keep Superset and dependencies updated

---

## Future Enhancements

### Planned Features

1. **Real-Time Collaboration**: Multi-user cursor tracking in dashboards
2. **AI-Powered Insights**: Automated anomaly detection and insights
3. **Natural Language Queries**: Ask questions in plain English
4. **Advanced Drill-Down**: Click-through from Superset to Odoo records
5. **Custom Alert Rules**: Configure dashboard-based alerts in Odoo
6. **Offline Mode**: Cached dashboards for offline viewing
7. **Mobile App Integration**: Native mobile dashboard viewing

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-03
**Author**: SuperClaude - Superset Analytics Architect Agent
**Status**: Production Ready
