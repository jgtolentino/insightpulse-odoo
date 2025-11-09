# Product Requirements Document (PRD)
**Pulser v4.0.0 – Multi-Agent Orchestration Runtime**

**Last Updated**: 2025-11-09
**Version**: 4.0.0
**Status**: Development (Sprint 5, Nov 9-15, 2025)
**Product Owner**: InsightPulse AI Team
**Target Release**: 2025-11-15 (Wave 4 completion)

---

## 0. Executive Summary

### Product Vision
Build a **production-grade multi-agent orchestration runtime** that coordinates 7 specialized AI agents (Dash, Maya, Echo, Data Fabcon, Arkie, LearnBot, Pulser) to automate enterprise operations, documentation, quality assurance, and deployment workflows for the InsightPulse Odoo platform.

### Value Proposition
- **24/7 Orchestration**: Continuous agent coordination and task routing
- **Specialist Agents**: 7 domain experts with clear responsibilities (BI, Docs, QA, Data, Architecture, Knowledge, Orchestration)
- **MCP Integration**: 98 tools across 7 MCP servers for comprehensive automation
- **Context Bus**: Supabase (pgvector + RLS) for persistent agent memory and coordination
- **Production Ready**: FastAPI + Celery + Redis for reliable asynchronous execution
- **Telemetry & Monitoring**: Real-time agent health, task queue metrics, performance tracking

### Success Criteria
- Deploy Pulser runtime to DigitalOcean App Platform by 2025-11-15
- Achieve 99.5%+ uptime for orchestration service
- Agent task completion rate >95%
- Task queue latency P95 <5 seconds
- Complete Pulser documentation suite (5 files)

---

## 1. Product Overview

### What is Pulser?

Pulser is a **multi-agent orchestration runtime** that acts as the "nervous system" of the InsightPulse Odoo platform, coordinating specialized AI agents to handle:

1. **Documentation Automation** (Maya agent)
2. **BI & Analytics** (Dash agent)
3. **Quality Assurance** (Echo agent)
4. **Data Operations** (Data Fabcon agent)
5. **Architecture & Deployment** (Arkie agent)
6. **Knowledge Management** (LearnBot agent)
7. **Agent Coordination** (Pulser orchestrator)

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Pulser Orchestrator (24/7)                    │
│         FastAPI + Celery + Redis + MCP Coordinator             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Task Router  │  Agent Manager  │  MCP Coordinator       │  │
│  │  (Priority)   │  (Health check) │  (7 servers)           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Celery Workers (4 workers)                              │  │
│  │  - Agent task execution                                  │  │
│  │  - Async job processing                                  │  │
│  │  - Retry logic (exponential backoff)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└───┬───┬───┬───┬───┬───┬──────────────────────────────────────┘
    │   │   │   │   │   │
    ▼   ▼   ▼   ▼   ▼   ▼
  Dash Maya Echo Data Arkie Learn
        Fabcon         Bot

              ↓ Context Bus ↓
┌─────────────────────────────────────────────────────────────────┐
│            Supabase (pgvector + RLS) Context Bus                │
│  ┌──────────────────┬──────────────────┬──────────────────┐    │
│  │  Agent Memory    │  Task Queue      │  Telemetry       │    │
│  │  (pgvector)      │  (task_queue)    │  (metrics)       │    │
│  └──────────────────┴──────────────────┴──────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Web Framework** | FastAPI | 0.104+ | REST API + WebSocket |
| **Task Queue** | Celery | 5.3+ | Async job processing |
| **Message Broker** | Redis | 7.0+ | Task queue + caching |
| **Data Layer** | Supabase (PostgreSQL 15.6) | - | Agent memory + context bus |
| **Vector DB** | pgvector | 0.5+ | Semantic search + embeddings |
| **MCP Integration** | 7 MCP servers | - | 98 tools for agents |
| **Deployment** | DigitalOcean App Platform | - | Container deployment |
| **Monitoring** | Prometheus + Grafana | - | Metrics + alerting |

---

## 2. Agent Specifications

### 2.1 Dash (BI Architect)

**Role**: BI dashboard creation, SQL optimization, analytics automation

**Responsibilities**:
- Create and maintain Superset dashboards (5 key dashboards: Finance, PPM, Procurement, Expenses, Retainers)
- Optimize SQL queries for performance (P95 <5 seconds dashboard load time)
- Design analytics data models (materialized views, aggregations)
- Implement RLS policies for multi-company isolation
- Generate analytics reports (scheduled email reports)

**MCP Servers**:
- `superset` (primary) - Dashboard creation, chart builder, SQL execution
- `github` - Version control for SQL queries and dashboard configs
- `supabase` - Direct database access for optimization

**Capacity**: 40 hours/week

**Success Metrics**:
- Dashboard creation time: <2 hours per dashboard
- SQL query optimization: P95 <5 seconds
- Dashboard uptime: >99.5%

---

### 2.2 Maya (Documentation Specialist)

**Role**: Technical writing, API documentation, user guides

**Responsibilities**:
- Create and maintain Spec-Kit compliant documentation (CLAUDE.md, TASKS.md, PLANNING.md, CHANGELOG.md, PRD.md)
- Generate API documentation (OpenAPI specs, endpoint docs)
- Write user guides and tutorials (admin guides, user manuals)
- Maintain documentation freshness (<7 days old)
- Create architectural diagrams (draw.io, mermaid)

**MCP Servers**:
- `github` (primary) - Repository management, PR creation
- `superset` - Analytics documentation
- `supabase` - Database schema documentation

**Capacity**: 40 hours/week

**Success Metrics**:
- Documentation freshness: <7 days
- Spec-Kit compliance: 100%
- Documentation completeness: >90%

---

### 2.3 Echo (QA Engineer)

**Role**: Test automation, quality gates, CI/CD validation

**Responsibilities**:
- Create and maintain test suites (unit, integration, E2E)
- Implement quality gates (test coverage >80%, lint score >8.0)
- Automate CI/CD workflows (GitHub Actions)
- Monitor test results and failure rates
- Perform security audits (OWASP Top 10 compliance)

**MCP Servers**:
- `github` (primary) - CI/CD workflows, PR checks
- `docker` - Container testing
- `kubernetes` - Deployment validation

**Capacity**: 40 hours/week

**Success Metrics**:
- Test coverage: >80%
- CI/CD success rate: >95%
- Security audit: No Critical/High vulnerabilities

---

### 2.4 Data Fabcon (Data Engineer)

**Role**: ETL pipelines, Supabase migrations, data quality

**Responsibilities**:
- Design and maintain ETL pipelines (Scout data → Odoo → Superset)
- Create and apply Supabase database migrations
- Implement data quality checks (completeness, accuracy, consistency)
- Optimize database queries and indexes
- Manage RLS policies for multi-tenant data

**MCP Servers**:
- `supabase` (primary) - Database operations, migrations
- `github` - Version control for SQL migrations
- `superset` - Analytics data models

**Capacity**: 40 hours/week

**Success Metrics**:
- Migration success rate: 100%
- Data quality score: >95%
- Query performance: P95 <200ms

---

### 2.5 Arkie (Solutions Architect)

**Role**: System design, infrastructure, deployment automation

**Responsibilities**:
- Design system architecture (Odoo + Supabase + Superset + Pulser)
- Manage infrastructure as code (DigitalOcean App Platform specs)
- Implement deployment automation (CI/CD workflows)
- Monitor system health (uptime, performance, errors)
- Capacity planning and scaling strategies

**MCP Servers**:
- `digitalocean` (primary) - App Platform management
- `kubernetes` - Cluster operations
- `docker` - Container management
- `github` - Infrastructure code version control

**Capacity**: 40 hours/week

**Success Metrics**:
- System uptime: >99.5%
- Deployment frequency: Daily
- Deployment success rate: >95%

---

### 2.6 LearnBot (Knowledge Manager)

**Role**: Skills mining, error analysis, continuous improvement

**Responsibilities**:
- Mine errors from logs for skill generation (Skillsmith integration)
- Analyze agent performance and identify improvement areas
- Create and maintain agent skills library (46 skills)
- Document common issues and solutions (knowledge base)
- Train agents on new capabilities (skill onboarding)

**MCP Servers**:
- `github` (primary) - Skills repository management
- `supabase` - Error log analysis
- `superset` - Performance analytics

**Capacity**: 20 hours/week

**Success Metrics**:
- Skills generated: ≥1 skill/week
- Error reduction rate: >10%/month
- Knowledge base completeness: >90%

---

### 2.7 Pulser (Orchestrator)

**Role**: Agent coordination, task routing, 24/7 runtime

**Responsibilities**:
- Route tasks to appropriate agents based on expertise
- Monitor agent health and task completion
- Coordinate multi-agent workflows (complex tasks requiring multiple agents)
- Manage task queue priorities (critical, high, medium, low)
- Collect telemetry and performance metrics
- Handle agent failures and retries (exponential backoff)

**MCP Servers**:
- ALL (7 servers) - Full access to coordinate all tools

**Capacity**: 24/7 runtime

**Success Metrics**:
- Orchestrator uptime: >99.5%
- Task routing accuracy: >95%
- Agent coordination latency: P95 <5 seconds

---

## 3. Functional Requirements

### 3.1 Task Routing & Orchestration

**REQ-001: Intelligent Task Routing** (Priority: Critical)
- System MUST route tasks to correct agents based on task type
- Routing decision MUST be made within <1 second
- Task routing accuracy MUST be >95%

**Acceptance Criteria**:
- Documentation tasks → Maya
- BI/analytics tasks → Dash
- QA/testing tasks → Echo
- Data operations → Data Fabcon
- Infrastructure → Arkie
- Knowledge management → LearnBot
- Multi-agent tasks → Pulser coordination

**REQ-002: Multi-Agent Coordination** (Priority: High)
- System MUST coordinate complex tasks requiring multiple agents
- Agent dependencies MUST be resolved automatically
- Task completion MUST be tracked end-to-end

**Acceptance Criteria**:
- Complex tasks decomposed into sub-tasks
- Sub-tasks assigned to appropriate agents
- Agent dependencies resolved via DAG (Directed Acyclic Graph)
- Progress tracked in Supabase context bus

### 3.2 Agent Health & Monitoring

**REQ-003: Agent Health Checks** (Priority: Critical)
- System MUST monitor agent health every 60 seconds
- Unhealthy agents MUST be flagged and restarted
- Health metrics MUST be stored in Supabase

**Acceptance Criteria**:
- Health check endpoint: `/health` per agent
- Health status: healthy, degraded, unhealthy
- Automatic restart on unhealthy status (max 3 retries)
- Alerting via Slack/email on persistent failures

**REQ-004: Telemetry & Metrics** (Priority: High)
- System MUST collect task execution metrics
- Metrics MUST be exposed via Prometheus endpoint
- Dashboards MUST be available in Grafana

**Acceptance Criteria**:
- Task completion time (P50, P95, P99)
- Task success rate per agent
- Agent utilization rate
- Queue depth and latency

### 3.3 Task Queue Management

**REQ-005: Priority Queue** (Priority: High)
- System MUST support task priorities (critical, high, medium, low)
- Critical tasks MUST be executed before lower priority tasks
- Task queue depth MUST be monitored

**Acceptance Criteria**:
- Priority levels: critical (P0), high (P1), medium (P2), low (P3)
- Critical tasks executed within 60 seconds
- Queue depth <100 tasks (alert if exceeded)

**REQ-006: Retry Logic** (Priority: High)
- System MUST retry failed tasks with exponential backoff
- Max retries: 3 attempts
- Failed tasks MUST be logged for analysis

**Acceptance Criteria**:
- Retry delays: 5s, 25s, 125s (exponential backoff)
- Failed tasks stored in `task_queue` with failure reason
- LearnBot analyzes failures for skill generation

### 3.4 Context Bus & Agent Memory

**REQ-007: Persistent Agent Memory** (Priority: High)
- System MUST store agent context in Supabase (pgvector)
- Agents MUST access shared context across sessions
- Context MUST be isolated per company (RLS policies)

**Acceptance Criteria**:
- Agent memory stored in `agent_memory` table
- Vector embeddings for semantic search
- RLS policies enforce company isolation

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-001: Task Routing Latency** (Priority: Critical)
- Task routing decision: <1 second
- Task queue latency: P95 <5 seconds
- Agent response time: P95 <30 seconds

**NFR-002: Throughput** (Priority: High)
- Support 1,000 tasks/hour
- Support 100 concurrent agents
- Queue depth <100 tasks

### 4.2 Reliability

**NFR-003: Uptime** (Priority: Critical)
- Pulser orchestrator uptime: >99.5% (43 hours downtime/year max)
- Agent availability: >95% per agent
- Task completion rate: >95%

**NFR-004: Fault Tolerance** (Priority: High)
- Graceful degradation on agent failures
- Automatic agent restart on crashes (max 3 retries)
- Task retry with exponential backoff

### 4.3 Security

**NFR-005: Access Control** (Priority: Critical)
- Agent authentication via API keys
- RLS policies on all Supabase tables
- Secrets in environment variables only

**NFR-006: Audit Trail** (Priority: High)
- All task executions logged
- Agent actions auditable
- Security events tracked

### 4.4 Scalability

**NFR-007: Horizontal Scaling** (Priority: Medium)
- Support 1-10 Celery workers (dynamic scaling)
- Support 1-100 agents (agent pool)
- Redis cluster for high availability

---

## 5. MCP Server Integration

### 5.1 MCP Server Registry (7 servers, 98 tools)

**pulser-hub** (Odoo & Ecosystem Integration)
- **Command**: `docker run -i --rm pulser-hub-mcp:latest`
- **Tools**: 5 tools (odoo, deployment, ecosystem)
- **DO App ID**: 60a13dec-1b31-4daf-b4c3-bfe8ca0dbfc8
- **Status**: ✅ Deployed

**digitalocean** (App Platform Management)
- **Command**: `npx -y @modelcontextprotocol/server-digitalocean`
- **Tools**: 3 tools (infrastructure, kubernetes, database)
- **Purpose**: App deployment, log monitoring, metrics

**kubernetes** (Cluster Operations)
- **Command**: `npx -y @modelcontextprotocol/server-kubernetes`
- **Tools**: 22 tools (cluster, deployment, monitoring, networking)
- **Cluster**: do-nyc3-superset-ai-cluster (nyc3 region)

**docker** (Container Management)
- **Command**: `npx -y @modelcontextprotocol/server-docker`
- **Tools**: 1 tool (container operations)
- **Registry**: docker.io

**github** (Repository Management)
- **Command**: `npx -y @modelcontextprotocol/server-github`
- **Tools**: 40 tools (repository, ci_cd, issues, actions)

**superset** (Apache Superset Analytics)
- **Command**: `npx -y @modelcontextprotocol/server-superset`
- **URL**: https://insightpulseai.net/odoo/superset
- **Tools**: 3+ tools (analytics, dashboard, chart)
- **App ID**: bc1764a5-b48e-4bec-aa72-8a22cab141bc

---

## 6. API Specification

### 6.1 Task Submission API

**POST /api/v1/tasks**

Submit a task to Pulser for routing and execution.

**Request**:
```json
{
  "task_type": "documentation",
  "priority": "high",
  "payload": {
    "file": "CLAUDE.md",
    "action": "update",
    "description": "Add Section 25: Agent Telemetry"
  },
  "requester": "user@insightpulseai.net"
}
```

**Response**:
```json
{
  "task_id": "tsk_abc123def456",
  "status": "queued",
  "assigned_agent": "maya",
  "priority": "high",
  "estimated_completion": "2025-11-09T15:30:00Z"
}
```

### 6.2 Task Status API

**GET /api/v1/tasks/{task_id}**

Get the status of a submitted task.

**Response**:
```json
{
  "task_id": "tsk_abc123def456",
  "status": "completed",
  "assigned_agent": "maya",
  "started_at": "2025-11-09T15:00:00Z",
  "completed_at": "2025-11-09T15:25:00Z",
  "result": {
    "success": true,
    "output": "Section 25 added to CLAUDE.md",
    "file_path": "/Users/tbwa/insightpulse-odoo/CLAUDE.md"
  }
}
```

### 6.3 Agent Health API

**GET /api/v1/agents/health**

Get health status of all agents.

**Response**:
```json
{
  "timestamp": "2025-11-09T15:00:00Z",
  "agents": [
    {
      "name": "dash",
      "status": "healthy",
      "last_heartbeat": "2025-11-09T14:59:30Z",
      "tasks_completed": 127,
      "tasks_failed": 3
    },
    {
      "name": "maya",
      "status": "healthy",
      "last_heartbeat": "2025-11-09T14:59:45Z",
      "tasks_completed": 215,
      "tasks_failed": 1
    }
  ]
}
```

---

## 7. Deployment Strategy

### 7.1 DigitalOcean App Platform Deployment

**Service Configuration**:
```yaml
name: pulser-v4
services:
  - name: pulser-api
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    source_dir: /services/pulser
    http_port: 8000
    instance_count: 2
    instance_size_slug: basic-xxs
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${SUPABASE_DATABASE_URL}
      - key: REDIS_URL
        scope: RUN_TIME
        value: ${REDIS_URL}

  - name: pulser-worker
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
    source_dir: /services/pulser
    run_command: celery -A pulser.celery worker --loglevel=info
    instance_count: 4
    instance_size_slug: basic-xxs
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${SUPABASE_DATABASE_URL}
      - key: REDIS_URL
        scope: RUN_TIME
        value: ${REDIS_URL}
```

**Cost**: $5/month (basic-xxs x 6 instances)

### 7.2 Monitoring & Alerting

**Prometheus Metrics**:
- `pulser_tasks_total` - Total tasks submitted
- `pulser_tasks_completed` - Tasks completed successfully
- `pulser_tasks_failed` - Tasks failed
- `pulser_task_duration_seconds` - Task execution time (histogram)
- `pulser_queue_depth` - Current queue depth
- `pulser_agent_health` - Agent health status (1=healthy, 0=unhealthy)

**Grafana Dashboards**:
- Pulser Overview (task throughput, success rate, queue depth)
- Agent Performance (per-agent completion rate, latency)
- System Health (uptime, errors, resource usage)

---

## 8. Success Metrics

### Business Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Agent Task Completion Rate** | >95% | TBD | 🔴 |
| **Documentation Freshness** | <7 days | 1 day | 🟢 |
| **CI/CD Success Rate** | >95% | TBD | 🔴 |
| **Dashboard Creation Time** | <2 hours | TBD | 🔴 |
| **Migration Success Rate** | 100% | TBD | 🔴 |

### Technical Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Orchestrator Uptime** | >99.5% | TBD | 🔴 |
| **Task Routing Latency** | <1 second | TBD | 🔴 |
| **Queue Latency P95** | <5 seconds | TBD | 🔴 |
| **Agent Response Time P95** | <30 seconds | TBD | 🔴 |
| **Task Retry Rate** | <5% | TBD | 🔴 |

---

## 9. Related Documents

- **CLAUDE.md**: [/Users/tbwa/insightpulse-odoo/CLAUDE.md](../../CLAUDE.md) (Section 24: Pulser Integration)
- **PLANNING.md**: [/Users/tbwa/insightpulse-odoo/PLANNING.md](../../PLANNING.md) (Resource Allocation)
- **TASKS.md**: [/Users/tbwa/insightpulse-odoo/TASKS.md](../../TASKS.md) (TSK-007: Pulser docs)
- **CHANGELOG.md**: [/Users/tbwa/insightpulse-odoo/CHANGELOG.md](../../CHANGELOG.md) (v4.0.0: Pulser integration)
- **PRD.md**: [/Users/tbwa/insightpulse-odoo/PRD.md](../../PRD.md) (Main project PRD)

---

**Maintainer**: InsightPulse AI Team
**Repository**: https://github.com/jgtolentino/insightpulse-odoo
**License**: AGPL-3.0
**Last Updated**: 2025-11-09 (Wave 4, Sprint 5)
**Document Version**: 4.0.0
