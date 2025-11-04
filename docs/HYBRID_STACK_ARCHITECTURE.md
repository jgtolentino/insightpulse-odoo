# Hybrid Stack Architecture: Next.js + OWL Best of Both Worlds

## Executive Summary

This architecture combines **Supabase UI (shadcn/ui) with Next.js** for modern web experiences and **Odoo OWL** for enterprise ERP functionality, creating a unified stack that leverages the strengths of both ecosystems.

## Technology Stack Comparison

### Supabase UI + Next.js
- **Framework**: React 18+ with Next.js 14+ App Router
- **UI Components**: shadcn/ui (Tailwind CSS + Radix UI primitives)
- **Auth**: Supabase Auth with pre-built components
- **Data**: Real-time subscriptions, PostgreSQL, Edge Functions
- **Best For**: Customer-facing apps, dashboards, analytics portals
- **Size**: ~50kb gzipped (with tree-shaking)

### Odoo OWL
- **Framework**: OWL (Odoo Web Library) - custom virtual DOM
- **Templates**: QWeb (XML-based templates)
- **Data**: Odoo ORM, JSON-RPC, XML-RPC
- **Best For**: ERP modules, complex business logic, multi-company workflows
- **Size**: ~20kb gzipped
- **Integration**: Direct access to Odoo models and business logic

## Recommended Hybrid Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    InsightPulse Platform                     │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼──────────┐                  ┌────────▼─────────┐
│   Next.js Apps   │                  │   Odoo 19 ERP    │
│  (Public Layer)  │                  │ (Business Layer) │
└──────────────────┘                  └──────────────────┘
        │                                       │
┌───────▼──────────────────────┐       ┌───────▼─────────────┐
│  Supabase UI Components:     │       │  OWL Components:    │
│  - Auth Forms                │       │  - Account Tree     │
│  - Dashboards                │       │  - Journal Entries  │
│  - Analytics                 │       │  - BIR Forms        │
│  - User Management           │       │  - Kanban Views     │
│  - File Upload               │       │  - List Views       │
│  - Real-time Chat            │       │  - Form Views       │
└──────────────────────────────┘       └─────────────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            │
                  ┌─────────▼──────────┐
                  │  Supabase Backend  │
                  │  - PostgreSQL      │
                  │  - Edge Functions  │
                  │  - Storage         │
                  │  - Real-time       │
                  └────────────────────┘
```

## Use Case Distribution

### Use Next.js + Supabase UI For:

#### 1. **Public Portal** (`app.insightpulseai.net`)
```typescript
// File: app/(public)/login/page.tsx
import { SupabaseAuthBlock } from '@/components/supabase-ui/auth-block'

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <SupabaseAuthBlock
        providers={['google', 'github']}
        redirectTo="/dashboard"
        appearance={{
          theme: 'default',
          variables: {
            default: {
              colors: {
                brand: '#3b82f6',
                brandAccent: '#2563eb'
              }
            }
          }
        }}
      />
    </div>
  )
}
```

**Components to Use:**
- **SupabaseAuthBlock** - Password auth, OAuth, magic links
- **StorageUpload** - File uploads with progress
- **RealtimeChat** - Customer support chat
- **Dashboard components** - Analytics, charts, KPIs

#### 2. **Finance Dashboard** (`finance.insightpulseai.net`)
```typescript
// File: app/(dashboard)/trial-balance/page.tsx
import { Card } from '@/components/ui/card'
import { Table } from '@/components/ui/table'
import { createServerClient } from '@/lib/supabase/server'

export default async function TrialBalancePage() {
  const supabase = createServerClient()

  // Real-time trial balance from Supabase
  const { data: accounts } = await supabase
    .from('account_account')
    .select('code, name, debit, credit, balance')
    .order('code')

  return (
    <Card>
      <Table>
        {/* shadcn/ui Table component */}
      </Table>
    </Card>
  )
}
```

**Components to Use:**
- **Table** (shadcn/ui) - Trial balance, ledgers
- **Charts** - Bar, line, pie charts for analytics
- **DateRangePicker** - Period selection
- **Command** - Quick search/navigation
- **Dialog** - Modals for quick actions

#### 3. **Superset Dashboards** (Embedded)
```typescript
// File: components/superset-embed.tsx
'use client'

import { useEffect } from 'react'
import { embedDashboard } from '@superset-ui/embedded-sdk'
import { createClient } from '@/lib/supabase/client'

export function SupersetDashboard({ dashboardId }: { dashboardId: string }) {
  const supabase = createClient()

  useEffect(() => {
    const fetchGuestToken = async () => {
      const { data: { session } } = await supabase.auth.getSession()

      // Get guest token from edge function
      const { data } = await supabase.functions.invoke('superset-guest-token', {
        body: { dashboard_id: dashboardId, user: session?.user }
      })

      embedDashboard({
        id: dashboardId,
        supersetDomain: 'https://superset.insightpulseai.net',
        mountPoint: document.getElementById('superset-dashboard')!,
        fetchGuestToken: () => data.token,
        dashboardUiConfig: {
          hideTitle: false,
          hideChartControls: false,
        }
      })
    }

    fetchGuestToken()
  }, [dashboardId])

  return <div id="superset-dashboard" className="w-full h-screen" />
}
```

### Use Odoo OWL For:

#### 1. **ERP Modules** (`odoo.insightpulseai.net`)
```xml
<!-- File: addons/custom/finance_dashboard/static/src/components/trial_balance/trial_balance.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
  <t t-name="finance_dashboard.TrialBalance" owl="1">
    <div class="o_trial_balance">
      <div class="o_control_panel">
        <div class="o_cp_buttons">
          <button class="btn btn-primary" t-on-click="exportPDF">
            <i class="fa fa-file-pdf-o"/> Export PDF
          </button>
          <button class="btn btn-secondary" t-on-click="exportXLSX">
            <i class="fa fa-file-excel-o"/> Export Excel
          </button>
        </div>
        <div class="o_cp_searchview">
          <DateRangePicker t-on-change="onPeriodChange"/>
        </div>
      </div>

      <table class="table table-striped o_list_view">
        <thead>
          <tr>
            <th>Account Code</th>
            <th>Account Name</th>
            <th class="text-end">Debit</th>
            <th class="text-end">Credit</th>
            <th class="text-end">Balance</th>
          </tr>
        </thead>
        <tbody>
          <t t-foreach="state.accounts" t-as="account" t-key="account.id">
            <tr>
              <td><t t-esc="account.code"/></td>
              <td><t t-esc="account.name"/></td>
              <td class="text-end"><t t-esc="formatCurrency(account.debit)"/></td>
              <td class="text-end"><t t-esc="formatCurrency(account.credit)"/></td>
              <td class="text-end"><t t-esc="formatCurrency(account.balance)"/></td>
            </tr>
          </t>
        </tbody>
      </table>
    </div>
  </t>
</templates>
```

```javascript
// File: addons/custom/finance_dashboard/static/src/components/trial_balance/trial_balance.js
/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class TrialBalance extends Component {
  static template = "finance_dashboard.TrialBalance";

  setup() {
    this.orm = useService("orm");
    this.state = useState({ accounts: [] });

    onWillStart(async () => {
      await this.loadTrialBalance();
    });
  }

  async loadTrialBalance() {
    const accounts = await this.orm.searchRead(
      "account.account",
      [],
      ["code", "name", "debit", "credit", "balance"],
      { order: "code" }
    );
    this.state.accounts = accounts;
  }

  async exportPDF() {
    const action = await this.orm.call(
      "account.report",
      "export_trial_balance_pdf",
      [this.state.period]
    );
    this.action.doAction(action);
  }

  formatCurrency(amount) {
    return new Intl.NumberFormat('en-PH', {
      style: 'currency',
      currency: 'PHP'
    }).format(amount);
  }
}
```

**Components to Use:**
- **Kanban Views** - Project management, CRM
- **List/Tree Views** - Journal entries, invoices
- **Form Views** - Detailed records
- **Gantt Charts** - Project timelines
- **Calendar** - Events, deadlines
- **Pivot Tables** - Multi-dimensional analysis

#### 2. **BIR Tax Filing Module**
```javascript
// File: addons/custom/bir_tax_filing/static/src/components/bir_1601c/bir_1601c.js
/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class BIR1601C extends Component {
  static template = "bir_tax_filing.BIR1601C";

  setup() {
    this.orm = useService("orm");
    this.notification = useService("notification");
    this.state = useState({
      form_data: {},
      validation_errors: [],
      status: 'draft'
    });
  }

  async validateForm() {
    // Call Odoo backend for BIR validation
    const result = await this.orm.call(
      "bir.form.1601c",
      "validate_form",
      [this.state.form_data]
    );

    if (result.errors.length === 0) {
      this.notification.add("Form validation successful", {
        type: "success"
      });
    }
  }

  async submitToBIR() {
    // Complex business logic handled by Odoo
    const result = await this.orm.call(
      "bir.form.1601c",
      "submit_to_bir",
      [this.state.form_data]
    );

    if (result.success) {
      this.state.status = 'submitted';
    }
  }
}
```

## Integration Patterns

### Pattern 1: SSO Between Next.js and Odoo

```typescript
// File: app/api/odoo/auth/route.ts
import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const supabase = createRouteHandlerClient({ cookies })

  // Get Supabase session
  const { data: { session } } = await supabase.auth.getSession()

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Authenticate with Odoo using Supabase JWT
  const odooResponse = await fetch(`${process.env.ODOO_URL}/web/session/authenticate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      params: {
        db: process.env.ODOO_DB,
        login: session.user.email,
        password: await getOdooSSOPassword(session.user.id) // Synced password
      }
    })
  })

  const odooSession = await odooResponse.json()

  return NextResponse.json({
    odoo_session_id: odooSession.result.session_id,
    redirect_url: `${process.env.ODOO_URL}/web`
  })
}
```

### Pattern 2: Embed Odoo Views in Next.js

```typescript
// File: components/odoo-iframe.tsx
'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'

export function OdooIframe({
  model,
  viewType = 'list'
}: {
  model: string
  viewType: 'list' | 'form' | 'kanban'
}) {
  const [iframeUrl, setIframeUrl] = useState<string | null>(null)
  const supabase = createClient()

  useEffect(() => {
    const authenticateOdoo = async () => {
      const { data } = await fetch('/api/odoo/auth', {
        method: 'POST'
      }).then(r => r.json())

      // Construct Odoo URL with session
      const url = new URL(`${process.env.NEXT_PUBLIC_ODOO_URL}/web`)
      url.searchParams.set('model', model)
      url.searchParams.set('view_type', viewType)
      url.searchParams.set('session_id', data.odoo_session_id)

      setIframeUrl(url.toString())
    }

    authenticateOdoo()
  }, [model, viewType])

  if (!iframeUrl) return <div>Loading...</div>

  return (
    <iframe
      src={iframeUrl}
      className="w-full h-screen border-0"
      sandbox="allow-same-origin allow-scripts allow-forms"
    />
  )
}
```

### Pattern 3: Shared Data via Supabase

```sql
-- Supabase Database Schema (shared between Next.js and Odoo)

-- Users table (synced from Supabase Auth)
CREATE TABLE public.users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  email TEXT UNIQUE NOT NULL,
  odoo_user_id INTEGER, -- FK to Odoo res.users
  company_id INTEGER, -- FK to Odoo res.company
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own data"
  ON public.users FOR SELECT
  USING (auth.uid() = id);

-- Real-time trial balance view (materialized)
CREATE MATERIALIZED VIEW public.trial_balance AS
SELECT
  aa.code,
  aa.name,
  SUM(CASE WHEN aml.debit > 0 THEN aml.debit ELSE 0 END) as debit,
  SUM(CASE WHEN aml.credit > 0 THEN aml.credit ELSE 0 END) as credit,
  SUM(aml.debit - aml.credit) as balance,
  aa.company_id
FROM account_account aa
LEFT JOIN account_move_line aml ON aml.account_id = aa.id
GROUP BY aa.id, aa.code, aa.name, aa.company_id
ORDER BY aa.code;

-- Refresh trigger for real-time updates
CREATE OR REPLACE FUNCTION refresh_trial_balance()
RETURNS TRIGGER AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY trial_balance;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trial_balance_refresh
AFTER INSERT OR UPDATE OR DELETE ON account_move_line
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_trial_balance();
```

### Pattern 4: Next.js API Routes Call Odoo RPC

```typescript
// File: app/api/odoo/rpc/route.ts
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const { model, method, args, kwargs } = await request.json()

  const response = await fetch(`${process.env.ODOO_URL}/jsonrpc`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'call',
      params: {
        service: 'object',
        method: 'execute_kw',
        args: [
          process.env.ODOO_DB,
          parseInt(process.env.ODOO_UID!),
          process.env.ODOO_PASSWORD,
          model,
          method,
          args,
          kwargs
        ]
      },
      id: Math.random()
    })
  })

  const data = await response.json()
  return NextResponse.json(data.result)
}
```

## Component Library Mapping

| Use Case | Next.js (Supabase UI) | Odoo (OWL) |
|----------|----------------------|------------|
| Authentication | ✅ SupabaseAuthBlock | ❌ Use Next.js |
| User Profile | ✅ shadcn/ui Forms | ⚠️ Odoo res.users |
| Analytics Dashboard | ✅ shadcn/ui + Recharts | ⚠️ Embedded Superset |
| File Upload | ✅ Supabase Storage UI | ⚠️ Odoo attachments |
| Real-time Chat | ✅ Supabase Realtime | ❌ Use Next.js |
| Trial Balance | ⚠️ Read-only view | ✅ OWL + Odoo ORM |
| Journal Entries | ❌ Too complex | ✅ OWL Form View |
| BIR Tax Forms | ❌ Too complex | ✅ OWL Custom Component |
| Invoice Generation | ❌ Business logic in Odoo | ✅ OWL + Odoo Report |
| Multi-company | ⚠️ Filter via RLS | ✅ Odoo built-in |
| Accounting Close | ❌ Complex workflow | ✅ Odoo Server Actions |

## Installation Guide

### 1. Install Supabase UI in Next.js

```bash
# Create Next.js app
npx create-next-app@latest insightpulse-portal --typescript --tailwind --app

cd insightpulse-portal

# Install Supabase
npm install @supabase/supabase-js @supabase/ssr

# Install shadcn/ui
npx shadcn@latest init

# Install Supabase UI components (via shadcn registry)
npx shadcn@latest add https://ui.supabase.com/registry/supabase-auth-block.json
npx shadcn@latest add https://ui.supabase.com/registry/supabase-storage-upload.json
npx shadcn@latest add https://ui.supabase.com/registry/supabase-realtime-chat.json

# Install additional shadcn components
npx shadcn@latest add button card table dialog dropdown-menu
npx shadcn@latest add form input label select checkbox
npx shadcn@latest add sheet tabs tooltip avatar badge
```

### 2. Install OWL in Odoo

```bash
# OWL is built into Odoo 19, but you can add custom components

# Create custom module
cd /home/user/insightpulse-odoo/addons/custom
mkdir -p finance_dashboard/static/src/components

# Install dependencies (if building standalone OWL)
npm install @odoo/owl
```

### 3. Configure Environment

```bash
# File: .env.local (Next.js)
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

ODOO_URL=https://odoo.insightpulseai.net
ODOO_DB=insightpulse
ODOO_UID=2
ODOO_PASSWORD=changeme

NEXT_PUBLIC_SUPERSET_URL=https://superset.insightpulseai.net
```

## Deployment Strategy

```yaml
# docker-compose.hybrid.yml
version: '3.8'

services:
  # Next.js Portal (Supabase UI)
  nextjs-portal:
    build: ./portal
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - ODOO_URL=http://odoo:8069
    depends_on:
      - odoo

  # Odoo ERP (OWL)
  odoo:
    image: odoo:19
    ports:
      - "8069:8069"
    environment:
      - HOST=postgres
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - ./addons/custom:/mnt/extra-addons
    depends_on:
      - postgres

  # PostgreSQL (Shared via Supabase)
  postgres:
    image: supabase/postgres:15.6.1.130
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_PASSWORD=your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - nextjs-portal
      - odoo

volumes:
  postgres_data:
```

## Best Practices

### When to Use Next.js + Supabase UI

✅ **DO USE for:**
- Public-facing websites
- Customer portals
- Read-heavy analytics dashboards
- Real-time collaboration features
- File uploads and storage
- Authentication and user management
- Mobile-responsive interfaces
- Server-side rendering (SEO)

❌ **DON'T USE for:**
- Complex multi-step wizards (Odoo is better)
- Heavy business logic (belongs in Odoo)
- Multi-company accounting rules
- BIR tax calculations
- Inventory management
- MRP workflows

### When to Use Odoo OWL

✅ **DO USE for:**
- ERP-specific workflows (accounting, inventory, HR)
- Complex business logic
- Multi-company, multi-currency
- Regulatory compliance (BIR)
- Backend admin interfaces
- Wizard-based processes
- Report generation (PDF, Excel)

❌ **DON'T USE for:**
- Public-facing marketing sites (Next.js is better)
- Real-time chat (Supabase is better)
- Mobile apps (React Native + Supabase better)
- Static content (Next.js SSG better)

## Performance Considerations

| Metric | Next.js + Supabase UI | Odoo OWL |
|--------|----------------------|----------|
| Initial Load | ~300-500ms (with edge) | ~800-1200ms |
| Time to Interactive | ~1s | ~2s |
| Bundle Size | ~150kb (tree-shaken) | ~400kb (full Odoo) |
| Real-time Updates | Native (Supabase) | Polling/WebSocket |
| SEO | Excellent (SSR/SSG) | Poor (SPA) |
| Mobile Performance | Excellent | Good |

## Cost Analysis

### Next.js + Supabase UI Stack
- **Hosting**: Vercel Free tier or DigitalOcean App Platform ($12/month)
- **Supabase**: Free tier (up to 500MB DB, 1GB file storage)
- **Total**: $0-12/month for small apps

### Odoo OWL Stack
- **Hosting**: DigitalOcean Droplet ($24/month for 4GB)
- **PostgreSQL**: Included with Supabase
- **Total**: $24/month

### Hybrid Stack (Recommended)
- **Next.js Portal**: Vercel Free tier
- **Odoo ERP**: DigitalOcean App Platform Professional-XS ($12/month)
- **Supabase**: Free tier
- **Total**: $12-24/month

**Savings vs Enterprise**: ~$4,728/year (no Odoo Enterprise license needed)

## Conclusion

The hybrid architecture gives you:

1. **Best UX**: Modern React components (shadcn/ui) for public-facing apps
2. **Best Business Logic**: Odoo OWL for complex ERP workflows
3. **Best Real-time**: Supabase for live updates and collaboration
4. **Best Cost**: Open-source stack, no licensing fees
5. **Best Integration**: Shared PostgreSQL database via Supabase

**Recommendation**: Use Next.js + Supabase UI for 70% of user-facing features, and Odoo OWL for 30% of backend/ERP-specific workflows.
