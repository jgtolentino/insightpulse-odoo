# Supabase Integrations for Superset Hybrid Control Plane

> Leveraging Supabase ecosystem to enhance dashboard infrastructure

## Overview

Supabase provides a powerful ecosystem that complements the Superset hybrid control plane:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPABASE (Infrastructure Layer)                                            │
│  ├── PostgreSQL (Metadata Store)     → Control plane state                  │
│  ├── Auth (Row-Level Security)       → Embedded dashboard tokens            │
│  ├── Realtime (WebSockets)           → Live drift notifications             │
│  ├── Edge Functions (Deno)           → Webhook handlers, token minting      │
│  └── Foreign Data Wrappers           → BigQuery, Stripe, Firebase sources   │
└─────────────────────────────────────────────────────────────────────────────┘
         │                    │                      │
         ▼                    ▼                      ▼
┌─────────────────┐  ┌─────────────────┐   ┌─────────────────┐
│  HYBRID CLI     │  │  SUPERSET       │   │  EXTERNAL DATA  │
│  compile/apply  │  │  Dashboards     │   │  Sources        │
└─────────────────┘  └─────────────────┘   └─────────────────┘
```

---

## Integration Categories

### 1. Data Platform Integrations

#### Foreign Data Wrappers (Query External Data in Superset)

| Wrapper | Use Case | Connection Pattern |
|---------|----------|-------------------|
| **BigQuery** | Analytics warehouse | `SELECT * FROM bq.dataset.table` |
| **Firebase** | Real-time app data | `SELECT * FROM firebase.users` |
| **Stripe** | Revenue dashboards | `SELECT * FROM stripe.charges` |

**Setup in Supabase:**
```sql
-- Enable wrappers extension
CREATE EXTENSION IF NOT EXISTS wrappers;

-- BigQuery wrapper
CREATE FOREIGN DATA WRAPPER bigquery_wrapper
  HANDLER big_query_fdw_handler
  VALIDATOR big_query_fdw_validator;

CREATE SERVER bigquery_server
  FOREIGN DATA WRAPPER bigquery_wrapper
  OPTIONS (
    sa_key_id 'key_id',
    sa_key 'base64_key',
    project_id 'your-gcp-project'
  );

CREATE FOREIGN TABLE bq_sales (
  order_date DATE,
  revenue NUMERIC,
  customer_id TEXT
)
SERVER bigquery_server
OPTIONS (table 'project.dataset.sales');
```

**Superset Dataset:**
```yaml
# datasets/bq_sales.yaml.j2
table_name: "bq_sales"
database: "supabase_{{ ENV }}"
schema: "public"
sql: |
  SELECT * FROM bq_sales
  WHERE order_date >= '{{ start_date | default("2024-01-01") }}'
```

#### Artie (Real-time CDC)

Stream changes from production databases to Supabase for Superset analytics:

```yaml
# artie-config.yaml
source:
  type: postgres
  host: "prod-db.example.com"
  database: "production"
  tables:
    - schema: public
      name: orders

destination:
  type: postgres
  host: "db.supabase.co"
  database: "postgres"
  schema: "analytics"
```

---

### 2. Auth Integrations (Embedded Dashboards)

#### Supabase Auth → Superset Guest Tokens

Use Supabase Auth to mint Superset embed tokens with tenant isolation:

```typescript
// supabase/functions/mint-superset-token/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const SUPERSET_URL = Deno.env.get('SUPERSET_URL')
const SUPERSET_SECRET = Deno.env.get('SUPERSET_SECRET')

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_ANON_KEY')!,
    { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
  )

  // Get authenticated user
  const { data: { user }, error } = await supabase.auth.getUser()
  if (error || !user) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401 })
  }

  // Get user's tenant from Supabase
  const { data: profile } = await supabase
    .from('profiles')
    .select('tenant_id, role')
    .eq('id', user.id)
    .single()

  // Mint Superset guest token with RLS
  const guestToken = await mintSupersetToken({
    user: {
      username: user.email,
      first_name: user.user_metadata.full_name?.split(' ')[0] || 'User',
      last_name: user.user_metadata.full_name?.split(' ')[1] || '',
    },
    resources: [{
      type: 'dashboard',
      id: req.body.dashboard_id,
    }],
    rls: [{
      clause: `tenant_id = '${profile.tenant_id}'`
    }]
  })

  return new Response(JSON.stringify({ guest_token: guestToken }))
})

async function mintSupersetToken(payload: any) {
  const response = await fetch(`${SUPERSET_URL}/api/v1/security/guest_token/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${SUPERSET_SECRET}`,
    },
    body: JSON.stringify(payload)
  })
  const data = await response.json()
  return data.token
}
```

#### Multi-Provider Auth (Clerk, Auth0, Kinde)

```typescript
// supabase/functions/oauth-to-superset/index.ts
// Works with any Supabase-compatible auth provider

const AUTH_PROVIDERS = {
  clerk: {
    verify: async (token: string) => {
      // Verify Clerk JWT
      const response = await fetch('https://api.clerk.dev/v1/tokens/verify', {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.json()
    }
  },
  auth0: {
    verify: async (token: string) => {
      // Verify Auth0 JWT
      const response = await fetch(`${AUTH0_DOMAIN}/userinfo`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      return response.json()
    }
  }
}
```

---

### 3. Workflow Automation

#### Trigger.dev (Background Jobs)

Schedule dashboard exports and drift detection:

```typescript
// trigger/superset-jobs.ts
import { cronTrigger, task } from "@trigger.dev/sdk/v3"
import { createClient } from '@supabase/supabase-js'

export const driftDetection = task({
  id: "superset-drift-detection",
  run: async (payload: { env: string }) => {
    const supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    )

    // Run drift detection
    const result = await execSync(`hybrid drift-plan --env ${payload.env}`)

    // Store result in Supabase
    await supabase.from('drift_logs').insert({
      environment: payload.env,
      status: result.includes('NO_DRIFT') ? 'clean' : 'drift_found',
      output: result,
      checked_at: new Date().toISOString()
    })

    // Alert if drift found
    if (result.includes('DRIFT_FOUND')) {
      await supabase.from('alerts').insert({
        type: 'drift',
        severity: 'warning',
        message: `Drift detected in ${payload.env}`,
        details: result
      })
    }

    return { status: 'completed', drift: result.includes('DRIFT_FOUND') }
  }
})

// Schedule: Run every 6 hours
export const scheduledDrift = cronTrigger({
  id: "scheduled-drift-check",
  cron: "0 */6 * * *",
  run: async () => {
    for (const env of ['dev', 'staging', 'prod']) {
      await driftDetection.trigger({ env })
    }
  }
})
```

#### n8n / Zapier (No-Code Workflows)

```json
{
  "name": "Superset Export to GitHub PR",
  "nodes": [
    {
      "type": "webhook",
      "name": "Trigger",
      "config": {
        "path": "/superset-export"
      }
    },
    {
      "type": "supabase",
      "name": "Log Export Request",
      "config": {
        "operation": "insert",
        "table": "export_logs"
      }
    },
    {
      "type": "ssh",
      "name": "Run Export",
      "config": {
        "command": "hybrid export --env {{ $json.env }} && hybrid translate --env {{ $json.env }}"
      }
    },
    {
      "type": "github",
      "name": "Create PR",
      "config": {
        "operation": "createPullRequest",
        "title": "Dashboard export from {{ $json.env }}"
      }
    }
  ]
}
```

#### Windmill (Internal Tools)

Build admin dashboards for the control plane:

```typescript
// windmill/hybrid-control-panel.ts
export async function main(
  action: "compile" | "validate" | "apply" | "drift",
  env: string,
  supabase_url: string,
  supabase_key: string
) {
  const supabase = createClient(supabase_url, supabase_key)

  // Run hybrid CLI command
  const result = await Deno.Command("hybrid", {
    args: [action, "--env", env]
  }).output()

  const output = new TextDecoder().decode(result.stdout)

  // Log to Supabase
  await supabase.from('control_plane_logs').insert({
    action,
    environment: env,
    status: result.code === 0 ? 'success' : 'failed',
    output,
    executed_at: new Date().toISOString()
  })

  return { success: result.code === 0, output }
}
```

---

### 4. Caching / Offline-First

#### PowerSync (Offline Dashboard State)

Sync dashboard filters and state for offline-capable embedded apps:

```yaml
# powersync-config.yaml
bucket_definitions:
  dashboard_state:
    data:
      - SELECT id, filters, created_at, user_id
        FROM dashboard_user_state
        WHERE user_id = token_parameters.user_id

  cached_charts:
    data:
      - SELECT chart_id, cached_data, expires_at
        FROM chart_cache
        WHERE tenant_id = token_parameters.tenant_id
```

```typescript
// React component with offline support
import { usePowerSync } from '@powersync/react'

function OfflineDashboard({ dashboardId }) {
  const { db } = usePowerSync()

  // State syncs automatically when online
  const [filters, setFilters] = useState({})

  useEffect(() => {
    // Load from local SQLite
    const state = await db.get(
      `SELECT filters FROM dashboard_state WHERE id = ?`,
      [dashboardId]
    )
    if (state) setFilters(JSON.parse(state.filters))
  }, [dashboardId])

  const saveFilters = async (newFilters) => {
    setFilters(newFilters)
    // Writes to local DB, syncs when online
    await db.execute(
      `INSERT OR REPLACE INTO dashboard_state (id, filters, updated_at)
       VALUES (?, ?, datetime('now'))`,
      [dashboardId, JSON.stringify(newFilters)]
    )
  }

  return <SupersetEmbed filters={filters} onFilterChange={saveFilters} />
}
```

---

### 5. Real-time Notifications

#### Supabase Realtime (Live Drift Alerts)

```typescript
// Dashboard admin with live drift notifications
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Subscribe to drift events
supabase
  .channel('drift-alerts')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'drift_logs',
      filter: 'status=eq.drift_found'
    },
    (payload) => {
      console.log('Drift detected:', payload.new)
      showNotification({
        title: `Drift in ${payload.new.environment}`,
        body: 'Dashboard configuration has drifted from Git',
        action: { label: 'View Diff', url: `/drift/${payload.new.id}` }
      })
    }
  )
  .subscribe()
```

---

### 6. Metadata Store Schema

Store hybrid control plane state in Supabase:

```sql
-- migrations/001_control_plane.sql

-- Dashboard assets registry
CREATE TABLE assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_type TEXT NOT NULL CHECK (asset_type IN ('dashboard', 'chart', 'dataset', 'database')),
  name TEXT NOT NULL,
  uuid TEXT UNIQUE NOT NULL,
  environment TEXT NOT NULL,
  git_sha TEXT,
  compiled_at TIMESTAMPTZ,
  applied_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deployment history
CREATE TABLE deployments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  environment TEXT NOT NULL,
  git_sha TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'success', 'failed')),
  assets JSONB NOT NULL DEFAULT '{}',
  started_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  error_message TEXT
);

-- Drift detection logs
CREATE TABLE drift_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  environment TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('clean', 'drift_found')),
  diff_output TEXT,
  checked_at TIMESTAMPTZ DEFAULT NOW()
);

-- Embed token audit
CREATE TABLE embed_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id),
  tenant_id TEXT NOT NULL,
  dashboard_id TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE deployments ENABLE ROW LEVEL SECURITY;
ALTER TABLE drift_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE embed_tokens ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their tenant's tokens
CREATE POLICY "Users see own embed tokens" ON embed_tokens
  FOR SELECT USING (user_id = auth.uid());
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SUPABASE PROJECT                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  PostgreSQL     │  │  Edge Functions │  │  Realtime       │             │
│  │  ───────────    │  │  ─────────────  │  │  ────────       │             │
│  │  • assets       │  │  • mint-token   │  │  • drift alerts │             │
│  │  • deployments  │  │  • webhook      │  │  • deploy notif │             │
│  │  • drift_logs   │  │  • export       │  │                 │             │
│  │  • embed_tokens │  │                 │  │                 │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│  ┌────────┴────────────────────┴────────────────────┴────────┐             │
│  │                    FOREIGN DATA WRAPPERS                   │             │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │             │
│  │  │ BigQuery │  │ Firebase │  │  Stripe  │  │ Gravatar │  │             │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │             │
│  └───────────────────────────────────────────────────────────┘             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
         │                           │                         │
         ▼                           ▼                         ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  HYBRID CLI     │      │  SUPERSET       │      │  TRIGGER.DEV    │
│  • compile      │─────▶│  • Dashboards   │◀─────│  • Scheduled    │
│  • apply        │      │  • Embeds       │      │  • Background   │
│  • drift-plan   │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

---

## Quick Start

### 1. Initialize Supabase Project

```bash
# Create new Supabase project
npx supabase init

# Link to existing project
npx supabase link --project-ref your-project-ref

# Apply migrations
npx supabase db push
```

### 2. Configure Foreign Data Wrappers

```bash
# Enable wrappers in Supabase dashboard
# Database → Extensions → Enable "wrappers"

# Or via SQL
CREATE EXTENSION wrappers;
```

### 3. Deploy Edge Functions

```bash
# Deploy token minting function
npx supabase functions deploy mint-superset-token

# Set secrets
npx supabase secrets set SUPERSET_URL=https://superset.example.com
npx supabase secrets set SUPERSET_SECRET=your-secret-key
```

### 4. Configure Hybrid CLI

```yaml
# hybrid.yaml
metadata_store:
  type: supabase
  url: "https://your-project.supabase.co"
  anon_key: "your-anon-key"
  service_key_env: "SUPABASE_SERVICE_KEY"

notifications:
  type: supabase_realtime
  channel: "control-plane-events"
```

---

## Integration Matrix

| Integration | Category | Use Case |
|-------------|----------|----------|
| **BigQuery Wrapper** | FDW | Query warehouse data in Superset |
| **Stripe Wrapper** | FDW | Revenue/billing dashboards |
| **Firebase Wrapper** | FDW | App analytics from Firestore |
| **PowerSync** | Offline | Embedded dashboards work offline |
| **Trigger.dev** | Jobs | Scheduled exports, drift checks |
| **n8n/Zapier** | Automation | No-code export → PR workflows |
| **Windmill** | Tools | Admin panel for control plane |
| **Clerk/Auth0** | Auth | SSO for embedded dashboards |
| **Vercel** | Deploy | Host embedded dashboard apps |
| **Resend** | Email | Drift alert notifications |

---

## Resources

- [Supabase Wrappers](https://supabase.com/docs/guides/database/extensions/wrappers/overview)
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)
- [PowerSync + Supabase](https://docs.powersync.com/integration-guides/supabase)
- [Trigger.dev](https://trigger.dev/docs)
