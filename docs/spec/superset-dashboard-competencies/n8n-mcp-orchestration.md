# Orchestration Options for Superset Hybrid Control Plane

> Workflow automation and AI agent integration for dashboard lifecycle management

## Orchestration Stack Decision

| Option | Use When | Your Fit |
|--------|----------|----------|
| **Supabase ETL (Rust)** | High-throughput CDC, real-time replication | ✅ Odoo → Analytics |
| **Python + Temporal** | AI agents, existing Python services | ✅ Best fit |
| **n8n** | Non-developers need visual workflows | ⚠️ Optional |

**Recommendation for fin-workspace**: Python + Supabase ETL hybrid

---

## Infrastructure Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  FIN-WORKSPACE (DigitalOcean)                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  APPS                                    DROPLETS                           │
│  ────                                    ────────                           │
│  superset.insightpulseai.net            odoo-erp-prod (159.223.75.148)     │
│  mcp.insightpulseai.net                 ocr-service (188.166.237.231)      │
│  bi-architect-bu9rc.ondigitalocean.app                                     │
│  finance-ssc-expert-3722k...                                               │
│  odoo-developer-agent-295j9...                                             │
│  multi-agent-orchestrator                                                  │
│  mattermost-rag                                                            │
│                                                                              │
│  AGENTS                                  AI SERVICES                        │
│  ──────                                  ───────────                        │
│  Kubernetes Genius                       Claude 3.5 Sonnet (13 tools)      │
│  Agent (wr2azp5d...)                     PaddleOCR-VL + OpenAI             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: n8n Workflows

### High-Value Workflows

| Workflow | Trigger | Action | Value |
|----------|---------|--------|-------|
| **OCR → Dashboard** | OCR service output | Create dataset + chart | Auto-visualize scanned docs |
| **Odoo → Superset Sync** | Odoo webhook | Update financial dashboards | Real-time ERP metrics |
| **Mattermost → Export** | Slash command | Export dashboard to Git | Chat-driven GitOps |
| **bi-architect → Deploy** | Agent output | Apply dashboard bundle | AI-generated dashboards |
| **Drift Alert → Mattermost** | Scheduled check | Post to channel | Team awareness |

### Workflow 1: OCR → Superset Dashboard

Automatically create dashboards from scanned financial documents:

```json
{
  "name": "OCR to Financial Dashboard",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "ocr-complete",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Parse OCR Output",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// OCR service sends extracted tables\nconst tables = $input.first().json.tables;\nconst invoices = tables.filter(t => t.type === 'invoice');\n\n// Transform to Superset-ready format\nreturn invoices.map(inv => ({\n  json: {\n    vendor: inv.vendor,\n    amount: parseFloat(inv.total),\n    date: inv.date,\n    line_items: inv.items\n  }\n}));"
      }
    },
    {
      "name": "Insert to Supabase",
      "type": "n8n-nodes-base.supabase",
      "parameters": {
        "operation": "insert",
        "table": "ocr_invoices",
        "options": {
          "returnAll": true
        }
      }
    },
    {
      "name": "Trigger Superset Refresh",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://superset.insightpulseai.net/api/v1/dataset/5/refresh",
        "method": "PUT",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth"
      }
    },
    {
      "name": "Notify Mattermost",
      "type": "n8n-nodes-base.mattermost",
      "parameters": {
        "channel": "finance-updates",
        "message": "📊 New invoice data processed: {{ $json.vendor }} - ${{ $json.amount }}\n[View Dashboard](https://superset.insightpulseai.net/superset/dashboard/invoices/)"
      }
    }
  ]
}
```

### Workflow 2: Odoo ERP → Superset Sync

Real-time financial metrics from Odoo:

```json
{
  "name": "Odoo to Superset Metrics",
  "nodes": [
    {
      "name": "Odoo Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "odoo-invoice",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Transform Invoice",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "const invoice = $input.first().json;\nreturn [{\n  json: {\n    invoice_id: invoice.id,\n    partner_name: invoice.partner_id.name,\n    amount_total: invoice.amount_total,\n    state: invoice.state,\n    invoice_date: invoice.invoice_date,\n    currency: invoice.currency_id.name,\n    company_id: invoice.company_id.id\n  }\n}];"
      }
    },
    {
      "name": "Upsert to Analytics DB",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "upsert",
        "table": "odoo_invoices",
        "columns": "invoice_id,partner_name,amount_total,state,invoice_date,currency,company_id",
        "conflictColumns": "invoice_id"
      },
      "credentials": {
        "postgres": "superset-analytics-db"
      }
    },
    {
      "name": "Check Threshold",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "number": [{
            "value1": "={{ $json.amount_total }}",
            "operation": "largerEqual",
            "value2": 10000
          }]
        }
      }
    },
    {
      "name": "Alert Large Invoice",
      "type": "n8n-nodes-base.mattermost",
      "parameters": {
        "channel": "finance-alerts",
        "message": "🚨 Large invoice detected!\nPartner: {{ $json.partner_name }}\nAmount: {{ $json.currency }} {{ $json.amount_total }}\n[View in Superset](https://superset.insightpulseai.net/superset/dashboard/ar-aging/)"
      }
    }
  ]
}
```

### Workflow 3: bi-architect → Dashboard Deploy

AI-generated dashboards from natural language:

```json
{
  "name": "AI Dashboard Generator",
  "nodes": [
    {
      "name": "Mattermost Trigger",
      "type": "n8n-nodes-base.mattermostTrigger",
      "parameters": {
        "events": ["slash_command"],
        "command": "/create-dashboard"
      }
    },
    {
      "name": "Call bi-architect",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://bi-architect-bu9rc.ondigitalocean.app/api/generate",
        "method": "POST",
        "body": {
          "prompt": "={{ $json.text }}",
          "data_source": "analytics_db",
          "viz_catalog": "echarts_first"
        }
      }
    },
    {
      "name": "Save to Git",
      "type": "n8n-nodes-base.git",
      "parameters": {
        "operation": "commit",
        "repository": "/app/superset-assets",
        "files": "={{ $json.assets }}",
        "message": "feat: AI-generated dashboard - {{ $json.title }}"
      }
    },
    {
      "name": "Run Hybrid Apply",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "hybrid compile --env dev && hybrid validate --env dev && hybrid apply --env dev"
      }
    },
    {
      "name": "Reply in Mattermost",
      "type": "n8n-nodes-base.mattermost",
      "parameters": {
        "channel": "={{ $json.channel_id }}",
        "message": "✅ Dashboard created!\n**{{ $json.title }}**\n[View Dashboard](https://superset.insightpulseai.net/superset/dashboard/{{ $json.slug }}/)"
      }
    }
  ]
}
```

### Workflow 4: Scheduled Drift Detection

```json
{
  "name": "Drift Detection & Alert",
  "nodes": [
    {
      "name": "Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{ "field": "hours", "hoursInterval": 6 }]
        }
      }
    },
    {
      "name": "Check Each Environment",
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 1,
        "options": {}
      }
    },
    {
      "name": "Run Drift Plan",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "hybrid drift-plan --env {{ $json.env }} --output json"
      }
    },
    {
      "name": "Parse Result",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "const output = JSON.parse($input.first().json.stdout);\nreturn [{\n  json: {\n    env: $input.first().json.env,\n    has_drift: output.status === 'DRIFT_FOUND',\n    changes: output.changes || [],\n    checked_at: new Date().toISOString()\n  }\n}];"
      }
    },
    {
      "name": "If Drift Found",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "boolean": [{
            "value1": "={{ $json.has_drift }}",
            "value2": true
          }]
        }
      }
    },
    {
      "name": "Log to Supabase",
      "type": "n8n-nodes-base.supabase",
      "parameters": {
        "operation": "insert",
        "table": "drift_logs"
      }
    },
    {
      "name": "Alert Team",
      "type": "n8n-nodes-base.mattermost",
      "parameters": {
        "channel": "superset-ops",
        "message": "⚠️ **Drift Detected** in `{{ $json.env }}`\n\nChanges:\n{{ $json.changes.map(c => '- ' + c.type + ': ' + c.name).join('\\n') }}\n\nRun `hybrid plan --env {{ $json.env }}` to review."
      }
    }
  ]
}
```

### Workflow 5: finance-ssc-expert → Report Generation

```json
{
  "name": "SSC Financial Report",
  "nodes": [
    {
      "name": "Schedule Monthly",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": { "interval": [{ "field": "months", "monthsInterval": 1 }] }
      }
    },
    {
      "name": "Query Superset",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://superset.insightpulseai.net/api/v1/chart/data",
        "method": "POST",
        "body": {
          "chart_id": 42,
          "queries": [{
            "time_range": "Last month",
            "granularity_sqla": "invoice_date"
          }]
        }
      }
    },
    {
      "name": "Call finance-ssc-expert",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://finance-ssc-expert-3722k.ondigitalocean.app/api/analyze",
        "method": "POST",
        "body": {
          "data": "={{ $json.result[0].data }}",
          "report_type": "monthly_summary",
          "include_recommendations": true
        }
      }
    },
    {
      "name": "Generate PDF",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://superset.insightpulseai.net/api/v1/report/42/pdf",
        "method": "GET",
        "responseFormat": "file"
      }
    },
    {
      "name": "Send to Mattermost",
      "type": "n8n-nodes-base.mattermost",
      "parameters": {
        "channel": "finance-reports",
        "message": "📈 **Monthly Financial Report**\n\n{{ $json.summary }}\n\n**Key Insights:**\n{{ $json.recommendations.join('\\n') }}",
        "attachments": [{ "file": "={{ $binary.file }}" }]
      }
    }
  ]
}
```

---

## Part 2: MCP Servers

### MCP Architecture for Dashboard Control

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  mcp.insightpulseai.net (MCP Coordinator)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  MCP Server Registry                                                     ││
│  │  ─────────────────                                                       ││
│  │  superset://     → Dashboard CRUD, Chart queries, Dataset management    ││
│  │  hybrid://       → Compile, validate, plan, apply, promote              ││
│  │  odoo://         → ERP data access, invoice queries                     ││
│  │  ocr://          → Document processing, table extraction                ││
│  │  supabase://     → Metadata store, real-time subscriptions              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Tool Definitions (13 tools for Claude 3.5 Sonnet)                       ││
│  │  ────────────────────────────────────────────────────────────────────────││
│  │  superset_query_chart      superset_list_dashboards                      ││
│  │  superset_export_assets    superset_apply_bundle                         ││
│  │  hybrid_compile            hybrid_validate                               ││
│  │  hybrid_plan               hybrid_apply                                  ││
│  │  hybrid_drift_detect       hybrid_promote                                ││
│  │  odoo_query_invoices       ocr_process_document                          ││
│  │  supabase_query            supabase_insert                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### MCP Server: superset://

```typescript
// mcp-servers/superset/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const SUPERSET_URL = process.env.SUPERSET_URL || "https://superset.insightpulseai.net";

const server = new Server({
  name: "superset",
  version: "1.0.0"
}, {
  capabilities: {
    tools: {}
  }
});

// Tool: List dashboards
server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "superset_list_dashboards",
      description: "List all dashboards in Superset",
      inputSchema: {
        type: "object",
        properties: {
          filter: { type: "string", description: "Optional filter by title" },
          limit: { type: "number", default: 100 }
        }
      }
    },
    {
      name: "superset_query_chart",
      description: "Execute a chart query and return data",
      inputSchema: {
        type: "object",
        properties: {
          chart_id: { type: "number", description: "Chart ID to query" },
          time_range: { type: "string", default: "Last 7 days" },
          filters: { type: "array", items: { type: "object" } }
        },
        required: ["chart_id"]
      }
    },
    {
      name: "superset_export_assets",
      description: "Export dashboards/charts as YAML bundle",
      inputSchema: {
        type: "object",
        properties: {
          dashboard_ids: { type: "array", items: { type: "number" } },
          output_dir: { type: "string", default: "./exports" }
        }
      }
    },
    {
      name: "superset_create_chart",
      description: "Create a new chart from specification",
      inputSchema: {
        type: "object",
        properties: {
          slice_name: { type: "string" },
          viz_type: { type: "string" },
          datasource_id: { type: "number" },
          params: { type: "object" }
        },
        required: ["slice_name", "viz_type", "datasource_id"]
      }
    }
  ]
}));

// Tool execution
server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;
  const token = await getAuthToken();

  switch (name) {
    case "superset_list_dashboards": {
      const response = await fetch(`${SUPERSET_URL}/api/v1/dashboard/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      return { content: [{ type: "text", text: JSON.stringify(data.result, null, 2) }] };
    }

    case "superset_query_chart": {
      const response = await fetch(`${SUPERSET_URL}/api/v1/chart/${args.chart_id}/data/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          queries: [{
            time_range: args.time_range,
            filters: args.filters || []
          }]
        })
      });
      const data = await response.json();
      return { content: [{ type: "text", text: JSON.stringify(data.result[0].data, null, 2) }] };
    }

    case "superset_export_assets": {
      const response = await fetch(`${SUPERSET_URL}/api/v1/dashboard/export/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ dashboards: args.dashboard_ids })
      });
      // Save to output_dir
      const zip = await response.blob();
      // Extract and save...
      return { content: [{ type: "text", text: `Exported ${args.dashboard_ids.length} dashboards` }] };
    }

    case "superset_create_chart": {
      const response = await fetch(`${SUPERSET_URL}/api/v1/chart/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          slice_name: args.slice_name,
          viz_type: args.viz_type,
          datasource_id: args.datasource_id,
          datasource_type: "table",
          params: JSON.stringify(args.params)
        })
      });
      const data = await response.json();
      return { content: [{ type: "text", text: `Created chart: ${data.id}` }] };
    }
  }
});

async function getAuthToken() {
  const response = await fetch(`${SUPERSET_URL}/api/v1/security/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: process.env.SUPERSET_USER,
      password: process.env.SUPERSET_PASS,
      provider: "db"
    })
  });
  const data = await response.json();
  return data.access_token;
}

const transport = new StdioServerTransport();
await server.connect(transport);
```

### MCP Server: hybrid://

```typescript
// mcp-servers/hybrid/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

const server = new Server({
  name: "hybrid",
  version: "1.0.0"
}, {
  capabilities: { tools: {} }
});

server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "hybrid_compile",
      description: "Compile Jinja2 templates to rendered YAML bundles",
      inputSchema: {
        type: "object",
        properties: {
          env: { type: "string", enum: ["dev", "staging", "prod"] },
          mapping: { type: "string", description: "Optional mapping file" }
        },
        required: ["env"]
      }
    },
    {
      name: "hybrid_validate",
      description: "Validate compiled bundle against schema",
      inputSchema: {
        type: "object",
        properties: {
          env: { type: "string", enum: ["dev", "staging", "prod"] }
        },
        required: ["env"]
      }
    },
    {
      name: "hybrid_plan",
      description: "Show what would be applied (dry-run)",
      inputSchema: {
        type: "object",
        properties: {
          env: { type: "string", enum: ["dev", "staging", "prod"] }
        },
        required: ["env"]
      }
    },
    {
      name: "hybrid_apply",
      description: "Apply bundle to Superset runtime",
      inputSchema: {
        type: "object",
        properties: {
          env: { type: "string", enum: ["dev", "staging", "prod"] },
          force: { type: "boolean", default: false }
        },
        required: ["env"]
      }
    },
    {
      name: "hybrid_drift_detect",
      description: "Compare compiled bundle vs runtime state",
      inputSchema: {
        type: "object",
        properties: {
          env: { type: "string", enum: ["dev", "staging", "prod"] }
        },
        required: ["env"]
      }
    },
    {
      name: "hybrid_promote",
      description: "Promote through environment chain",
      inputSchema: {
        type: "object",
        properties: {
          chain: { type: "string", default: "dev,staging,prod" },
          stop_on_drift: { type: "boolean", default: true }
        }
      }
    }
  ]
}));

server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;

  const commands: Record<string, string> = {
    hybrid_compile: `hybrid compile --env ${args.env}${args.mapping ? ` --mapping ${args.mapping}` : ''}`,
    hybrid_validate: `hybrid validate --env ${args.env}`,
    hybrid_plan: `hybrid plan --env ${args.env}`,
    hybrid_apply: `hybrid apply --env ${args.env}${args.force ? ' --force' : ''}`,
    hybrid_drift_detect: `hybrid drift-plan --env ${args.env}`,
    hybrid_promote: `hybrid promote --chain ${args.chain}${args.stop_on_drift ? ' --drift' : ''}`
  };

  try {
    const { stdout, stderr } = await execAsync(commands[name], {
      cwd: process.env.HYBRID_REPO_PATH || "/app/superset-assets"
    });
    return {
      content: [{
        type: "text",
        text: `✅ ${name} completed\n\n${stdout}${stderr ? `\nWarnings:\n${stderr}` : ''}`
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `❌ ${name} failed\n\n${error.message}\n${error.stderr || ''}`
      }],
      isError: true
    };
  }
});
```

### MCP Server: ocr://

```typescript
// mcp-servers/ocr/index.ts
const OCR_SERVICE = "http://188.166.237.231:8080";

server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "ocr_process_document",
      description: "Extract text and tables from document using PaddleOCR",
      inputSchema: {
        type: "object",
        properties: {
          file_url: { type: "string", description: "URL to document" },
          file_type: { type: "string", enum: ["pdf", "image", "invoice"] },
          extract_tables: { type: "boolean", default: true }
        },
        required: ["file_url"]
      }
    },
    {
      name: "ocr_extract_invoice",
      description: "Extract structured invoice data",
      inputSchema: {
        type: "object",
        properties: {
          file_url: { type: "string" }
        },
        required: ["file_url"]
      }
    }
  ]
}));

server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "ocr_process_document") {
    const response = await fetch(`${OCR_SERVICE}/api/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: args.file_url,
        type: args.file_type,
        extract_tables: args.extract_tables
      })
    });
    const result = await response.json();
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  }

  if (name === "ocr_extract_invoice") {
    const response = await fetch(`${OCR_SERVICE}/api/invoice`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: args.file_url })
    });
    const invoice = await response.json();
    return {
      content: [{
        type: "text",
        text: `Invoice extracted:\n- Vendor: ${invoice.vendor}\n- Amount: ${invoice.currency} ${invoice.total}\n- Date: ${invoice.date}\n- Items: ${invoice.line_items.length}`
      }]
    };
  }
});
```

### MCP Server: odoo://

```typescript
// mcp-servers/odoo/index.ts
const ODOO_URL = "http://159.223.75.148:8069";

server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "odoo_query_invoices",
      description: "Query invoices from Odoo ERP",
      inputSchema: {
        type: "object",
        properties: {
          state: { type: "string", enum: ["draft", "posted", "cancel"] },
          partner_id: { type: "number" },
          date_from: { type: "string", format: "date" },
          date_to: { type: "string", format: "date" },
          limit: { type: "number", default: 100 }
        }
      }
    },
    {
      name: "odoo_get_partner",
      description: "Get partner/customer details",
      inputSchema: {
        type: "object",
        properties: {
          partner_id: { type: "number" }
        },
        required: ["partner_id"]
      }
    },
    {
      name: "odoo_financial_summary",
      description: "Get financial summary for period",
      inputSchema: {
        type: "object",
        properties: {
          period: { type: "string", enum: ["this_month", "last_month", "this_quarter", "ytd"] }
        },
        required: ["period"]
      }
    }
  ]
}));
```

---

## Part 3: Agent Integration

### Claude Agent Configuration

```yaml
# agent-config.yaml
name: "Superset Dashboard Agent"
model: "claude-3-5-sonnet-20241022"
mcp_servers:
  - name: superset
    transport: stdio
    command: "node"
    args: ["mcp-servers/superset/index.js"]
    env:
      SUPERSET_URL: "https://superset.insightpulseai.net"
      SUPERSET_USER: "${SUPERSET_ADMIN_USER}"
      SUPERSET_PASS: "${SUPERSET_ADMIN_PASS}"

  - name: hybrid
    transport: stdio
    command: "node"
    args: ["mcp-servers/hybrid/index.js"]
    env:
      HYBRID_REPO_PATH: "/app/superset-assets"

  - name: ocr
    transport: stdio
    command: "node"
    args: ["mcp-servers/ocr/index.js"]
    env:
      OCR_SERVICE: "http://188.166.237.231:8080"

  - name: odoo
    transport: stdio
    command: "node"
    args: ["mcp-servers/odoo/index.js"]
    env:
      ODOO_URL: "http://159.223.75.148:8069"

  - name: supabase
    transport: stdio
    command: "npx"
    args: ["@anthropic/mcp-server-supabase"]
    env:
      SUPABASE_URL: "${SUPABASE_URL}"
      SUPABASE_KEY: "${SUPABASE_SERVICE_KEY}"

system_prompt: |
  You are a dashboard operations agent with access to:
  - Superset: Query and manage dashboards, charts, datasets
  - Hybrid: GitOps control plane for dashboard-as-code
  - OCR: Process financial documents and invoices
  - Odoo: Query ERP data for financial metrics
  - Supabase: Store metadata and logs

  When asked to create dashboards:
  1. First check existing assets with superset_list_dashboards
  2. Use hybrid_compile to render templates
  3. Validate with hybrid_validate
  4. Plan with hybrid_plan to show changes
  5. Apply with hybrid_apply only after confirmation

  For financial reporting:
  1. Query Odoo for raw data
  2. Create or update Superset charts
  3. Log actions to Supabase
```

### Example Agent Conversation

```
User: Create a dashboard showing invoice aging from Odoo

Agent: I'll create an invoice aging dashboard. Let me:

1. First, query Odoo for invoice data:
   [Calling odoo_query_invoices with state="posted", date_from="2024-01-01"]

2. Check existing dashboards:
   [Calling superset_list_dashboards with filter="aging"]
   → No existing aging dashboard found

3. I'll create the dashboard assets. Let me compile the template:
   [Calling hybrid_compile with env="dev"]
   ✅ Compiled 1 dashboard, 3 charts, 1 dataset

4. Validating the bundle:
   [Calling hybrid_validate with env="dev"]
   ✅ All assets valid

5. Here's the plan:
   [Calling hybrid_plan with env="dev"]

   CREATE dashboard "AR Aging Analysis"
   CREATE chart "Aging Buckets by Amount"
   CREATE chart "Top 10 Overdue Accounts"
   CREATE chart "Aging Trend"
   CREATE dataset "odoo_invoice_aging"

   Apply these changes? [Confirm to proceed]

User: Yes, apply it

Agent: [Calling hybrid_apply with env="dev"]
   ✅ Applied successfully

   Dashboard available at:
   https://superset.insightpulseai.net/superset/dashboard/ar-aging/

   [Calling supabase_insert to log deployment]
   ✅ Logged to deployment history
```

---

## Integration Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐     ┌────────────────┐     ┌────────────────┐          │
│  │  n8n           │     │  MCP Server    │     │  Claude Agent  │          │
│  │  (Workflows)   │────▶│  (Tools)       │◀────│  (Reasoning)   │          │
│  └───────┬────────┘     └───────┬────────┘     └───────┬────────┘          │
│          │                      │                      │                    │
└──────────┼──────────────────────┼──────────────────────┼────────────────────┘
           │                      │                      │
           ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SERVICE LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  superset.insightpulseai.net    odoo-erp-prod         ocr-service-droplet  │
│  ┌────────────────┐             ┌────────────────┐    ┌────────────────┐   │
│  │  Dashboards    │             │  Invoices      │    │  PaddleOCR     │   │
│  │  Charts        │             │  Partners      │    │  Tables        │   │
│  │  Datasets      │             │  GL Entries    │    │  Forms         │   │
│  └────────────────┘             └────────────────┘    └────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Deploy n8n

```bash
# Add n8n to docker-compose
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=$N8N_PASSWORD \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

### 2. Install MCP Servers

```bash
cd mcp-servers
npm install
npm run build

# Register with mcp-coordinator
curl -X POST https://mcp.insightpulseai.net/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "superset",
    "transport": "stdio",
    "command": "node",
    "args": ["dist/superset/index.js"]
  }'
```

### 3. Configure Agent

```bash
# Set environment variables
export SUPERSET_URL="https://superset.insightpulseai.net"
export SUPERSET_ADMIN_USER="admin"
export SUPERSET_ADMIN_PASS="$VAULT_SUPERSET_PASS"

# Start agent service
npm run start:agent
```

---

## Part 4: Python Orchestration (Alternative to n8n)

### Why Python for Your Stack?

Your existing services are Python-based:
- OCR Service (PaddleOCR-VL)
- AI Agents (Claude 3.5 Sonnet)
- bi-architect, finance-ssc-expert

Python orchestration provides:
- Native Claude SDK integration
- Consistent codebase
- Full control over AI reasoning
- Easy deployment to existing droplets

### Supabase ETL for CDC

```bash
# Install Supabase ETL
cargo install supabase-etl

# Configure CDC from Odoo Postgres
cat > etl-config.toml << 'EOF'
[source]
type = "postgres"
connection_string = "postgresql://odoo:$ODOO_DB_PASS@159.223.75.148:5432/odoo"
publication = "odoo_changes"
slot = "etl_slot"

[destination]
type = "postgres"
connection_string = "postgresql://postgres:$SUPABASE_DB_PASS@db.xxx.supabase.co:5432/postgres"
schema = "analytics"

[tables]
include = ["account_move", "account_move_line", "res_partner"]

[batching]
max_size = 1000
max_wait_ms = 100
EOF

# Run CDC
supabase-etl run --config etl-config.toml
```

### Python Workflow Engine (Temporal)

```python
# workflows/dashboard_workflows.py
from temporalio import workflow, activity
from datetime import timedelta
import httpx
from anthropic import Anthropic

# Activities
@activity.defn
async def query_odoo_invoices(state: str, date_from: str) -> list:
    """Query invoices from Odoo ERP."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://159.223.75.148:8069/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        "odoo", 2, os.environ["ODOO_PASSWORD"],
                        "account.move", "search_read",
                        [[["state", "=", state], ["invoice_date", ">=", date_from]]],
                        {"fields": ["name", "partner_id", "amount_total", "invoice_date"]}
                    ]
                }
            }
        )
        return response.json()["result"]


@activity.defn
async def process_ocr_document(file_url: str) -> dict:
    """Process document through OCR service."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://188.166.237.231:8080/api/invoice",
            json={"url": file_url}
        )
        return response.json()


@activity.defn
async def refresh_superset_dataset(dataset_id: int) -> bool:
    """Refresh Superset dataset."""
    token = await get_superset_token()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"https://superset.insightpulseai.net/api/v1/dataset/{dataset_id}/refresh",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.status_code == 200


@activity.defn
async def run_hybrid_command(command: str, env: str) -> str:
    """Run hybrid CLI command."""
    import subprocess
    result = subprocess.run(
        f"hybrid {command} --env {env}",
        shell=True,
        capture_output=True,
        text=True,
        cwd="/app/superset-assets"
    )
    return result.stdout


@activity.defn
async def call_claude_agent(prompt: str, tools: list) -> str:
    """Call Claude with MCP tools."""
    client = Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        tools=tools,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


@activity.defn
async def notify_mattermost(channel: str, message: str) -> None:
    """Send notification to Mattermost."""
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://mattermost-rag-egb6n.ondigitalocean.app/hooks/xxx",
            json={"channel": channel, "text": message}
        )


# Workflows
@workflow.defn
class OCRToDashboardWorkflow:
    """Process OCR output and update Superset dashboard."""

    @workflow.run
    async def run(self, file_url: str, dashboard_id: int) -> dict:
        # 1. Process document
        ocr_result = await workflow.execute_activity(
            process_ocr_document,
            file_url,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # 2. Insert to analytics DB (handled by Supabase ETL CDC)
        # Just trigger refresh
        await workflow.execute_activity(
            refresh_superset_dataset,
            dataset_id=5,  # ocr_invoices dataset
            start_to_close_timeout=timedelta(seconds=30)
        )

        # 3. Notify team
        await workflow.execute_activity(
            notify_mattermost,
            args=["finance-updates", f"📊 Invoice processed: {ocr_result['vendor']} - ${ocr_result['total']}"],
            start_to_close_timeout=timedelta(seconds=10)
        )

        return {"status": "success", "invoice": ocr_result}


@workflow.defn
class DriftDetectionWorkflow:
    """Scheduled drift detection across environments."""

    @workflow.run
    async def run(self, environments: list[str]) -> dict:
        results = {}
        for env in environments:
            output = await workflow.execute_activity(
                run_hybrid_command,
                args=["drift-plan", env],
                start_to_close_timeout=timedelta(minutes=2)
            )

            has_drift = "DRIFT_FOUND" in output
            results[env] = {"has_drift": has_drift, "output": output}

            if has_drift:
                await workflow.execute_activity(
                    notify_mattermost,
                    args=["superset-ops", f"⚠️ Drift detected in `{env}`\n```\n{output[:500]}\n```"],
                    start_to_close_timeout=timedelta(seconds=10)
                )

        return results


@workflow.defn
class AIGenerateDashboardWorkflow:
    """Use Claude to generate and deploy dashboard."""

    @workflow.run
    async def run(self, prompt: str, env: str = "dev") -> dict:
        # 1. Call bi-architect agent
        tools = [
            {"name": "superset_list_dashboards", ...},
            {"name": "hybrid_compile", ...},
            {"name": "hybrid_validate", ...},
            {"name": "hybrid_apply", ...},
        ]

        agent_response = await workflow.execute_activity(
            call_claude_agent,
            args=[f"Create a Superset dashboard: {prompt}", tools],
            start_to_close_timeout=timedelta(minutes=5)
        )

        # 2. Compile and validate
        compile_output = await workflow.execute_activity(
            run_hybrid_command,
            args=["compile", env],
            start_to_close_timeout=timedelta(minutes=1)
        )

        validate_output = await workflow.execute_activity(
            run_hybrid_command,
            args=["validate", env],
            start_to_close_timeout=timedelta(seconds=30)
        )

        # 3. Apply
        apply_output = await workflow.execute_activity(
            run_hybrid_command,
            args=["apply", env],
            start_to_close_timeout=timedelta(minutes=2)
        )

        return {
            "status": "success",
            "agent_response": agent_response,
            "deployed_to": env
        }
```

### FastAPI Webhook Server

```python
# api/webhooks.py
from fastapi import FastAPI, BackgroundTasks
from temporalio.client import Client
from workflows import OCRToDashboardWorkflow, DriftDetectionWorkflow

app = FastAPI()
temporal_client = None

@app.on_event("startup")
async def startup():
    global temporal_client
    temporal_client = await Client.connect("localhost:7233")

@app.post("/webhooks/ocr-complete")
async def ocr_complete(payload: dict, background_tasks: BackgroundTasks):
    """Handle OCR service completion webhook."""
    await temporal_client.start_workflow(
        OCRToDashboardWorkflow.run,
        args=[payload["file_url"], payload.get("dashboard_id", 1)],
        id=f"ocr-{payload['job_id']}",
        task_queue="superset-workflows"
    )
    return {"status": "workflow_started"}

@app.post("/webhooks/odoo-invoice")
async def odoo_invoice(payload: dict):
    """Handle Odoo invoice webhook (CDC handles data, this triggers refresh)."""
    # Supabase ETL handles the data sync via CDC
    # Just trigger Superset refresh
    async with httpx.AsyncClient() as client:
        await client.put(
            "https://superset.insightpulseai.net/api/v1/dataset/3/refresh",
            headers={"Authorization": f"Bearer {await get_superset_token()}"}
        )
    return {"status": "refresh_triggered"}

@app.post("/webhooks/mattermost-command")
async def mattermost_command(payload: dict):
    """Handle Mattermost slash commands."""
    command = payload.get("command", "")
    text = payload.get("text", "")

    if command == "/create-dashboard":
        await temporal_client.start_workflow(
            AIGenerateDashboardWorkflow.run,
            args=[text, "dev"],
            id=f"ai-dashboard-{uuid4()}",
            task_queue="superset-workflows"
        )
        return {"text": "🚀 Dashboard generation started..."}

    if command == "/drift-check":
        result = await temporal_client.execute_workflow(
            DriftDetectionWorkflow.run,
            args=[["dev", "staging", "prod"]],
            id=f"drift-{uuid4()}",
            task_queue="superset-workflows"
        )
        return {"text": f"Drift check complete: {result}"}

    return {"text": "Unknown command"}
```

### Deployment

```yaml
# docker-compose.yml
services:
  temporal:
    image: temporalio/auto-setup:latest
    ports:
      - "7233:7233"

  workflow-worker:
    build: .
    command: python -m workers.main
    environment:
      - TEMPORAL_HOST=temporal:7233
      - SUPERSET_URL=https://superset.insightpulseai.net
      - ODOO_URL=http://159.223.75.148:8069
      - OCR_URL=http://188.166.237.231:8080

  webhook-api:
    build: .
    command: uvicorn api.webhooks:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"

  supabase-etl:
    image: supabase/etl:latest
    volumes:
      - ./etl-config.toml:/config.toml
    command: run --config /config.toml
```

---

## Summary: Recommended Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DATA LAYER (Supabase ETL - Rust)                                           │
│  ────────────────────────────────                                           │
│  • Odoo Postgres CDC → Supabase Analytics                                   │
│  • Real-time, high-throughput                                               │
│  • Fault-tolerant with retries                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATION LAYER (Python + Temporal)                                    │
│  ─────────────────────────────────────                                      │
│  • Workflow engine with durability                                          │
│  • Native Claude SDK integration                                            │
│  • FastAPI webhooks                                                         │
│  • Consistent with existing Python services                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│  AI LAYER (MCP + Claude)                                                    │
│  ─────────────────────                                                      │
│  • MCP servers for tool execution                                           │
│  • Claude 3.5 Sonnet for reasoning                                          │
│  • bi-architect for dashboard generation                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Resources

- [Supabase ETL](https://github.com/supabase/etl) - Rust CDC framework
- [Temporal.io](https://temporal.io/) - Durable workflow engine
- [Claude SDK](https://github.com/anthropics/anthropic-sdk-python) - Python SDK
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [n8n Documentation](https://docs.n8n.io/) - Visual workflows (optional)
