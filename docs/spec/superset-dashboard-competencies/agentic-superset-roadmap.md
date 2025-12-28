# Agentic Superset Roadmap Alignment

> Aligning hybrid control plane with Apache Superset's official AI/MCP initiatives

## Official Superset Agentic SIPs

| SIP | Title | Status | Relevance |
|-----|-------|--------|-----------|
| **SIP-155** | Agentic Dashboard & Chart Summarization | Open | LLM-powered insights |
| **SIP-157** | Agentic Query in Dashboard | Open | Natural language querying |
| **SIP-166** | AI Assistant Extension Framework | Open | MCP tool integration |
| **SIP-189** | Context Engineering | Open | Structured AI context |

---

## Architecture Alignment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERSET CORE (Future State)                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  SIP-155: Dashboard Summarization    SIP-157: Agentic Query                 │
│  ┌────────────────────────────┐      ┌────────────────────────────┐        │
│  │ • Chart insight generation │      │ • Natural language search  │        │
│  │ • Anomaly detection        │      │ • Dashboard-wide questions │        │
│  │ • Automated KPI reports    │      │ • Chart-specific queries   │        │
│  └────────────────────────────┘      └────────────────────────────┘        │
│                                                                              │
│  SIP-166: AI Extension Framework     SIP-189: Context Engineering          │
│  ┌────────────────────────────┐      ┌────────────────────────────┐        │
│  │ • MCP server integration   │      │ • context/ directory       │        │
│  │ • Custom agent plugins     │      │ • Architectural docs       │        │
│  │ • RAG logic extension      │      │ • Tribal knowledge capture │        │
│  └────────────────────────────┘      └────────────────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERSET MCP SERVICE (FastMCP Protocol)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Tools:                              Resources:                             │
│  • list_dashboards                   • dashboards://{id}                    │
│  • get_chart_data                    • charts://{id}                        │
│  • create_chart                      • datasets://{id}                      │
│  • execute_query                     • databases://{id}                     │
│  • summarize_dashboard               • queries://{id}                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  HYBRID CONTROL PLANE (Our Extension)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  GitOps Layer:                       Orchestration:                         │
│  • compile / validate / apply        • Temporal workflows                   │
│  • drift-plan / promote              • MCP tool execution                   │
│  • translate (UI → Git)              • Multi-agent coordination             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## SIP-155: Agentic Dashboard Summarization

### Official Proposal

```yaml
# Feature flag
SHOW_DASHBOARD_SUMMARY: true

# Capabilities:
# - Textual insights for charts
# - Anomaly detection
# - Automated KPI reports
# - Non-technical user summaries
```

### Integration with Hybrid Control Plane

```python
# MCP tool wrapping SIP-155 summarization
@activity.defn
async def summarize_dashboard(dashboard_id: int) -> dict:
    """Call Superset's built-in LLM summarization (SIP-155)."""
    async with httpx.AsyncClient() as client:
        # Use native Superset endpoint when SIP-155 ships
        response = await client.post(
            f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}/summarize",
            headers={"Authorization": f"Bearer {token}"},
            json={"include_anomalies": True}
        )
        return response.json()

# Workflow: Scheduled insight generation
@workflow.defn
class DashboardInsightWorkflow:
    @workflow.run
    async def run(self, dashboard_ids: list[int]) -> dict:
        insights = {}
        for dash_id in dashboard_ids:
            summary = await workflow.execute_activity(
                summarize_dashboard,
                dash_id,
                start_to_close_timeout=timedelta(minutes=2)
            )
            insights[dash_id] = summary

            # Store insights in Supabase
            await workflow.execute_activity(
                store_insight,
                args=[dash_id, summary],
                start_to_close_timeout=timedelta(seconds=10)
            )

        return insights
```

---

## SIP-157: Agentic Query in Dashboard

### Official Proposal

```yaml
# Feature flag
SHOW_DASHBOARD_AGENT_QUERY: true

# Capabilities:
# - Search button in dashboard header
# - Natural language questions
# - Chart-specific queries
# - Dashboard-wide analysis
```

### Integration with Mattermost

```python
# Slack/Mattermost integration for dashboard queries
@app.post("/webhooks/mattermost-query")
async def mattermost_query(payload: dict):
    """Handle /query-dashboard command."""
    question = payload.get("text", "")
    dashboard_slug = payload.get("channel_name", "default")

    # Find dashboard by channel mapping
    dashboard_id = await get_dashboard_by_channel(dashboard_slug)

    # Call SIP-157 agent query endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}/query",
            headers={"Authorization": f"Bearer {token}"},
            json={"question": question}
        )
        answer = response.json()

    return {
        "text": f"**Answer**: {answer['response']}\n\n"
                f"*Based on charts: {', '.join(answer['source_charts'])}*"
    }
```

---

## SIP-166: AI Assistant Extension Framework

### Official Proposal

```yaml
# Extension architecture
# - Agents/RAG kept in extension framework
# - Not in core codebase
# - Rapidly evolving AI patterns

# MCP companion service
superset_mcp_service:
  protocol: FastMCP
  capabilities:
    - metadata_access
    - action_execution
    - context_bridging
```

### Our MCP Server Alignment

```typescript
// Our MCP server extends SIP-166 patterns
import { Server } from "@modelcontextprotocol/sdk/server/index.js";

const server = new Server({
  name: "superset-hybrid",
  version: "1.0.0"
}, {
  capabilities: {
    tools: {},
    resources: {}
  }
});

// Tools align with Superset MCP Service
server.setRequestHandler("tools/list", async () => ({
  tools: [
    // Core Superset operations (SIP-166)
    { name: "superset_list_dashboards", ... },
    { name: "superset_get_chart_data", ... },
    { name: "superset_execute_query", ... },

    // Agentic operations (SIP-155, SIP-157)
    { name: "superset_summarize_dashboard", ... },
    { name: "superset_query_natural_language", ... },

    // Hybrid control plane operations
    { name: "hybrid_compile", ... },
    { name: "hybrid_apply", ... },
    { name: "hybrid_drift_detect", ... },
  ]
}));

// Resources for context
server.setRequestHandler("resources/list", async () => ({
  resources: [
    { uri: "dashboards://list", name: "All Dashboards" },
    { uri: "charts://list", name: "All Charts" },
    { uri: "context://architecture", name: "Architecture Docs" },
  ]
}));
```

---

## SIP-189: Context Engineering

### Official Proposal

```
superset/
├── context/                    # NEW: AI context directory
│   ├── architecture/
│   │   ├── frontend.md
│   │   ├── backend.md
│   │   └── data-model.md
│   ├── workflows/
│   │   ├── chart-creation.md
│   │   └── dashboard-export.md
│   ├── decisions/
│   │   ├── adr-001-echarts.md
│   │   └── adr-002-mcp.md
│   └── tribal-knowledge/
│       ├── common-gotchas.md
│       └── performance-tips.md
```

### Our Context Structure

```
spec/superset-dashboard-competencies/
├── context/                           # AI context for hybrid control plane
│   ├── architecture/
│   │   ├── hybrid-control-plane.md    # System architecture
│   │   ├── mcp-servers.md             # MCP tool definitions
│   │   └── orchestration.md           # Workflow patterns
│   ├── workflows/
│   │   ├── compile-apply.md           # GitOps workflow
│   │   ├── drift-detection.md         # State reconciliation
│   │   └── ui-to-git.md               # Export roundtrip
│   ├── decisions/
│   │   ├── adr-001-echarts-first.md   # Viz type strategy
│   │   ├── adr-002-supabase-etl.md    # CDC choice
│   │   └── adr-003-temporal.md        # Workflow engine
│   └── tribal-knowledge/
│       ├── common-issues.md           # Known gotchas
│       └── performance.md             # Optimization tips
```

### Context Provider for Agents

```python
# context_provider.py
from pathlib import Path
import yaml

class ContextProvider:
    """Provide structured context to AI agents."""

    def __init__(self, context_dir: Path = Path("spec/superset-dashboard-competencies/context")):
        self.context_dir = context_dir

    def get_architecture_context(self) -> str:
        """Get architecture documentation for agent context."""
        docs = []
        for md_file in (self.context_dir / "architecture").glob("*.md"):
            docs.append(f"# {md_file.stem}\n\n{md_file.read_text()}")
        return "\n\n---\n\n".join(docs)

    def get_workflow_context(self, workflow_name: str) -> str:
        """Get specific workflow documentation."""
        workflow_file = self.context_dir / "workflows" / f"{workflow_name}.md"
        if workflow_file.exists():
            return workflow_file.read_text()
        return f"No documentation found for workflow: {workflow_name}"

    def get_decision_context(self, topic: str) -> str:
        """Get ADRs related to a topic."""
        adrs = []
        for adr_file in (self.context_dir / "decisions").glob("*.md"):
            content = adr_file.read_text()
            if topic.lower() in content.lower():
                adrs.append(f"# {adr_file.stem}\n\n{content}")
        return "\n\n---\n\n".join(adrs) if adrs else f"No ADRs found for: {topic}"

    def get_tribal_knowledge(self) -> str:
        """Get tribal knowledge for common issues."""
        docs = []
        for md_file in (self.context_dir / "tribal-knowledge").glob("*.md"):
            docs.append(f"# {md_file.stem}\n\n{md_file.read_text()}")
        return "\n\n---\n\n".join(docs)


# MCP resource for context
@server.setRequestHandler("resources/read")
async def read_resource(request):
    uri = request.params.uri
    provider = ContextProvider()

    if uri == "context://architecture":
        return {"contents": [{"text": provider.get_architecture_context()}]}
    if uri.startswith("context://workflow/"):
        workflow = uri.split("/")[-1]
        return {"contents": [{"text": provider.get_workflow_context(workflow)}]}
    if uri.startswith("context://decision/"):
        topic = uri.split("/")[-1]
        return {"contents": [{"text": provider.get_decision_context(topic)}]}
    if uri == "context://tribal-knowledge":
        return {"contents": [{"text": provider.get_tribal_knowledge()}]}
```

---

## Feature Flag Configuration

Align with Superset's feature flag pattern:

```python
# superset_config.py
FEATURE_FLAGS = {
    # Official Superset agentic features
    "SHOW_DASHBOARD_SUMMARY": True,           # SIP-155
    "SHOW_DASHBOARD_AGENT_QUERY": True,       # SIP-157
    "ENABLE_AI_ASSISTANT": True,              # SIP-166
    "ENABLE_CONTEXT_ENGINEERING": True,       # SIP-189

    # Hybrid control plane features
    "ENABLE_HYBRID_GITOPS": True,
    "ENABLE_DRIFT_DETECTION": True,
    "ENABLE_MCP_TOOLS": True,
}

# LLM Configuration (SIP-157)
AI_CONFIG = {
    "model": "claude-3-5-sonnet-20241022",
    "base_url": None,  # Use Anthropic API, or set for local LLM
    "api_key_env": "ANTHROPIC_API_KEY",
}
```

---

## Integration Matrix

| Component | SIP-155 | SIP-157 | SIP-166 | SIP-189 | Hybrid |
|-----------|---------|---------|---------|---------|--------|
| Dashboard summarization | ✅ Core | - | Tool | Context | Scheduled |
| Natural language query | - | ✅ Core | Tool | Context | Mattermost |
| MCP server | Insight | Query | ✅ Core | Context | GitOps |
| Context engineering | Docs | Docs | Docs | ✅ Core | ADRs |
| Drift detection | - | - | Tool | Context | ✅ Core |
| Multi-env promotion | - | - | Tool | Context | ✅ Core |

---

## Deployment Roadmap

### Phase 1: Current (Hybrid Control Plane)
```
✅ GitOps workflows (compile/apply/drift)
✅ MCP servers for Claude agents
✅ Python + Temporal orchestration
✅ Supabase ETL for CDC
```

### Phase 2: SIP Alignment (When Ships)
```
🔲 Integrate SIP-155 summarization API
🔲 Connect SIP-157 query to Mattermost
🔲 Adopt SIP-166 extension patterns
🔲 Migrate to SIP-189 context structure
```

### Phase 3: Full Agentic Analytics
```
🔲 Automated KPI report generation
🔲 Anomaly detection alerts
🔲 Self-healing dashboards
🔲 Multi-agent collaboration
```

---

## Resources

- [SIP-155: Dashboard Summarization](https://github.com/apache/superset/issues/SIP-155)
- [SIP-157: Agentic Query](https://github.com/apache/superset/issues/SIP-157)
- [SIP-166: AI Assistant](https://github.com/apache/superset/issues/SIP-166)
- [SIP-189: Context Engineering](https://github.com/apache/superset/issues/SIP-189)
- [Superset MCP Service](https://github.com/apache/superset-mcp-service)
- [FastMCP Protocol](https://fastmcp.io/)
