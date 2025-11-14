# Multi-Agent Orchestrator: Routing Tools Setup

## Overview

This guide explains how to add routing tools to the DO AI Agent orchestrator (`https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run`) to enable delegation to the 4 specialist agents.

**Status**: ✅ Specialist services deployed and healthy
**Next Step**: Configure routing tools in DO AI Agent UI (manual step)

---

## Deployed Specialist Services

All 4 specialist FastAPI services are deployed and operational:

| Agent | URL | Status |
|-------|-----|--------|
| **odoo_developer** | https://odoo-developer-agent-295j9.ondigitalocean.app | ✅ Healthy |
| **finance_ssc_expert** | https://finance-ssc-expert-3722k.ondigitalocean.app | ✅ Healthy |
| **bi_architect** | https://bi-architect-bu9rc.ondigitalocean.app | ✅ Healthy |
| **devops_engineer** | https://devops-engineer-dzzf8.ondigitalocean.app | ✅ Healthy |

---

## Routing Tool Definitions

Navigate to: **DigitalOcean Control Panel → AI Platform → Your Agent → Tools**

### Tool 1: route_to_odoo_developer

**Name**: `route_to_odoo_developer`
**Description**: Route Odoo 18 CE development tasks to odoo_developer specialist
**URL**: `https://odoo-developer-agent-295j9.ondigitalocean.app/execute`
**Method**: `POST`
**Headers**:
```json
{
  "Content-Type": "application/json"
}
```

**Body Schema**:
```json
{
  "type": "object",
  "properties": {
    "task": {
      "type": "string",
      "description": "Description of the Odoo development task"
    },
    "context": {
      "type": "object",
      "description": "Additional context (files, requirements, agency info)"
    }
  },
  "required": ["task"]
}
```

**When to Use**: Odoo module scaffolding, OCA compliance, Python/XML development, manifest.py configuration

---

### Tool 2: route_to_finance_ssc_expert

**Name**: `route_to_finance_ssc_expert`
**Description**: Route Philippine BIR compliance and Finance SSC tasks to finance_ssc_expert specialist
**URL**: `https://finance-ssc-expert-3722k.ondigitalocean.app/execute`
**Method**: `POST`
**Headers**:
```json
{
  "Content-Type": "application/json"
}
```

**Body Schema**:
```json
{
  "type": "object",
  "properties": {
    "task": {
      "type": "string",
      "description": "Description of the BIR compliance or Finance SSC task"
    },
    "context": {
      "type": "object",
      "description": "Additional context (agency, tax form type, deadlines)"
    }
  },
  "required": ["task"]
}
```

**When to Use**: BIR Forms 1601-C, 1702-RT, 2550Q, 2550M, multi-agency finance operations, month-end closing

---

### Tool 3: route_to_bi_architect

**Name**: `route_to_bi_architect`
**Description**: Route Apache Superset dashboard and BI tasks to bi_architect specialist
**URL**: `https://bi-architect-bu9rc.ondigitalocean.app/execute`
**Method**: `POST`
**Headers**:
```json
{
  "Content-Type": "application/json"
}
```

**Body Schema**:
```json
{
  "type": "object",
  "properties": {
    "task": {
      "type": "string",
      "description": "Description of the BI/analytics task"
    },
    "context": {
      "type": "object",
      "description": "Additional context (dashboard type, data sources, metrics)"
    }
  },
  "required": ["task"]
}
```

**When to Use**: Superset dashboard creation, SQL view optimization, RLS policies, chart configuration

---

### Tool 4: route_to_devops_engineer

**Name**: `route_to_devops_engineer`
**Description**: Route DevOps and deployment tasks to devops_engineer specialist
**URL**: `https://devops-engineer-dzzf8.ondigitalocean.app/execute`
**Method**: `POST`
**Headers**:
```json
{
  "Content-Type": "application/json"
}
```

**Body Schema**:
```json
{
  "type": "object",
  "properties": {
    "task": {
      "type": "string",
      "description": "Description of the DevOps/deployment task"
    },
    "context": {
      "type": "object",
      "description": "Additional context (environment, deployment target, CI/CD)"
    }
  },
  "required": ["task"]
}
```

**When to Use**: DigitalOcean App Platform deployments, Docker containerization, CI/CD pipelines, GitHub Actions

---

## System Prompt Update (Recommended)

Update the orchestrator's system prompt to include routing logic:

```markdown
You are the Master Orchestrator for InsightPulse AI's Multi-Agent System.

You have access to 4 specialist agents via routing tools:
1. **odoo_developer**: Odoo 18 CE development, OCA compliance
2. **finance_ssc_expert**: Philippine BIR compliance, Finance SSC
3. **bi_architect**: Apache Superset, BI dashboards, SQL
4. **devops_engineer**: DevOps, deployment, CI/CD

**Routing Strategy**:
- **Simple tasks**: Handle directly
- **Specialist tasks**: Route to appropriate agent via tool
- **Complex tasks**: Coordinate multiple specialists

**User Context**:
- 8 agencies: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB
- Technology: Odoo 18 CE, Supabase, Apache Superset, DO App Platform
- Focus: BIR compliance, OCA standards, automation

When routing, provide task description and relevant context.
```

---

## Validation Tests

After adding tools, test each routing function:

### Test 1: odoo_developer
```bash
# Via DO AI Agent chat interface
"Create an Odoo 18 CE module for tracking travel requests"
```
**Expected**: Routes to odoo_developer, returns OCA-compliant module structure

### Test 2: finance_ssc_expert
```bash
"Generate BIR Form 1601-C for RIM agency for November 2025"
```
**Expected**: Routes to finance_ssc_expert, returns tax form with proper calculations

### Test 3: bi_architect
```bash
"Create a Superset dashboard showing expense trends by agency"
```
**Expected**: Routes to bi_architect, returns dashboard configuration

### Test 4: devops_engineer
```bash
"Deploy the odoo-developer-agent service to DigitalOcean App Platform"
```
**Expected**: Routes to devops_engineer, returns deployment workflow

---

## Cost Impact

**Total Monthly Cost**: $25-32
- Orchestrator (DO AI Agent): $5-10 (usage-based)
- odoo_developer: $5 (basic-xxs)
- finance_ssc_expert: $5 (basic-xxs)
- bi_architect: $5 (basic-xxs)
- devops_engineer: $5 (basic-xxs)

**ROI**: 80x ($2,000/month automation savings)

---

## Next Steps

1. ✅ Specialist services deployed
2. ⏳ **Add 4 routing tools** (via DO AI Agent UI - this guide)
3. ⏳ Update system prompt with routing logic
4. ⏳ Run integration tests (`scripts/test-orchestrator.py`)
5. ⏳ Execute staged rollout (25% → 50% → 100%)

---

## Troubleshooting

**Tool not appearing**:
- Verify URL is accessible: `curl -sf <URL>/health`
- Check HTTP method is POST
- Validate JSON schema syntax

**Routing failures**:
- Check agent health endpoints
- Review orchestrator logs for errors
- Verify tool names match function calls

**High latency**:
- Specialist services in `sfo` region for low latency
- Consider caching frequently accessed responses
- Monitor p95 response times (<3s target)

---

**Documentation**: README_MULTI_AGENT.md, MULTI_AGENT_ARCHITECTURE.md, DEPLOYMENT_GUIDE.md
**Support**: Check health endpoints, review deployment logs
**Last Updated**: 2025-11-14
