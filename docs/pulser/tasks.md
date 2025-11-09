# 📋 Tasks – Pulser v4.0.0 Multi-Agent Orchestrator

**Last Updated**: 2025-11-09
**Current Sprint**: Sprint 5 - Pulser Runtime Development
**Duration**: Nov 9-15, 2025
**Status**: Development Phase (0% deployed, 60% planned)

---

## 🎯 Active Sprint Tasks (Pulser Development)

| ID | Title | Agent | Category | Status | Deadline |
|----|--------|--------|-----------|----------|----------|
| PLS-001 | Create FastAPI orchestrator skeleton | Arkie | Backend | ⏳ Pending | 2025-11-10 |
| PLS-002 | Implement Celery task queue with Redis | Arkie | Backend | ⏳ Pending | 2025-11-10 |
| PLS-003 | Create Supabase context bus schema | Data Fabcon | Database | ⏳ Pending | 2025-11-11 |
| PLS-004 | Implement agent health check system | Echo | Monitoring | ⏳ Pending | 2025-11-11 |
| PLS-005 | Create MCP coordinator service | Arkie | Integration | ⏳ Pending | 2025-11-12 |
| PLS-006 | Implement task routing logic | Pulser | Orchestration | ⏳ Pending | 2025-11-12 |
| PLS-007 | Create agent telemetry dashboard | Dash | Analytics | ⏳ Pending | 2025-11-13 |
| PLS-008 | Write integration tests (pytest) | Echo | Testing | ⏳ Pending | 2025-11-13 |
| PLS-009 | Create DigitalOcean App Platform spec | Arkie | DevOps | ⏳ Pending | 2025-11-14 |
| PLS-010 | Deploy Pulser v4.0.0 to production | Arkie | Deployment | ⏳ Pending | 2025-11-15 |

---

## 📊 Agent Workload Distribution

| Agent | Active Tasks | Capacity | Utilization |
|-------|--------------|----------|-------------|
| **Arkie** | 4 (PLS-001, PLS-002, PLS-005, PLS-009) | 40 hrs/week | 100% |
| **Data Fabcon** | 1 (PLS-003) | 40 hrs/week | 25% |
| **Echo** | 2 (PLS-004, PLS-008) | 40 hrs/week | 50% |
| **Dash** | 1 (PLS-007) | 40 hrs/week | 25% |
| **Pulser** | 1 (PLS-006) | 24/7 runtime | N/A |
| **Maya** | 0 (documentation complete) | 40 hrs/week | 0% |
| **LearnBot** | 0 (monitoring only) | 20 hrs/week | 0% |

**Total Workload**: 10 tasks across 5 agents

---

## 🔄 Task Dependencies

### Critical Path (Sequential)
```
PLS-001 (FastAPI skeleton)
   ↓
PLS-002 (Celery + Redis)
   ↓
PLS-003 (Supabase context bus)
   ↓
PLS-006 (Task routing logic)
   ↓
PLS-010 (Deployment)
```

### Parallel Tracks
```
Track 1 (Monitoring):
PLS-004 (Health checks) → PLS-007 (Telemetry dashboard)

Track 2 (Integration):
PLS-005 (MCP coordinator) → PLS-008 (Integration tests)

Track 3 (Deployment):
PLS-009 (DO App Platform spec) → PLS-010 (Production deploy)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| PLS-001 | None | PLS-002, PLS-005 |
| PLS-002 | PLS-001 | PLS-003, PLS-006 |
| PLS-003 | PLS-002 | PLS-006, PLS-008 |
| PLS-004 | None | PLS-007 |
| PLS-005 | PLS-001 | PLS-008 |
| PLS-006 | PLS-002, PLS-003 | PLS-010 |
| PLS-007 | PLS-004 | PLS-010 |
| PLS-008 | PLS-003, PLS-005 | PLS-010 |
| PLS-009 | None | PLS-010 |
| PLS-010 | PLS-006, PLS-007, PLS-008, PLS-009 | None |

---

## 🧩 Component Breakdown

### Core Components (PLS-001 through PLS-003)

#### PLS-001: FastAPI Orchestrator Skeleton
**Owner**: Arkie
**Description**: Create FastAPI application with basic routing, health endpoints, and OpenAPI documentation

**Deliverables**:
- `/pulser/main.py` - FastAPI app initialization
- `/pulser/routes/tasks.py` - Task submission endpoints
- `/pulser/routes/health.py` - Health check endpoints
- `/pulser/routes/status.py` - Status query endpoints
- `/pulser/config.py` - Configuration management
- `requirements.txt` - Python dependencies

**Acceptance Criteria**:
- [ ] FastAPI app starts on port 8000
- [ ] Health endpoint returns `{"ok": true}`
- [ ] OpenAPI docs accessible at `/docs`
- [ ] CORS enabled for frontend integration
- [ ] Environment variable configuration working

**Tech Stack**:
- FastAPI 0.104+
- Pydantic 2.0+ (data validation)
- Python 3.11+

---

#### PLS-002: Celery Task Queue with Redis
**Owner**: Arkie
**Description**: Implement async task queue using Celery with Redis broker for agent job distribution

**Deliverables**:
- `/pulser/celery_app.py` - Celery application
- `/pulser/tasks/agent_tasks.py` - Agent task definitions
- `/pulser/workers/` - Celery worker configuration
- `docker-compose.yml` - Redis service
- `/pulser/config/celery_config.py` - Celery settings

**Acceptance Criteria**:
- [ ] Redis broker running on port 6379
- [ ] Celery workers start successfully (4 workers)
- [ ] Task submission works (`delay()` method)
- [ ] Task status retrieval working
- [ ] Retry logic with exponential backoff
- [ ] Dead letter queue for failed tasks

**Tech Stack**:
- Celery 5.3+
- Redis 7.2+
- Kombu (messaging library)

---

#### PLS-003: Supabase Context Bus Schema
**Owner**: Data Fabcon
**Description**: Create PostgreSQL schema for agent memory, task queue, and telemetry

**Deliverables**:
- `supabase/migrations/001_context_bus.sql` - Schema migration
- `supabase/migrations/002_agent_memory.sql` - pgvector setup
- `supabase/migrations/003_task_queue.sql` - Task queue tables
- `supabase/migrations/004_telemetry.sql` - Metrics tables
- RLS policies for multi-tenant isolation

**Acceptance Criteria**:
- [ ] Tables created: `agent_memory`, `task_queue`, `agent_telemetry`
- [ ] pgvector extension enabled
- [ ] RLS policies active on all tables
- [ ] Indexes on `task_id`, `agent_id`, `status`
- [ ] Foreign key constraints enforced
- [ ] Migration rollback tested

**Schema Design**:
```sql
-- Task Queue Table
CREATE TABLE task_queue (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    assigned_agent VARCHAR(50),
    status VARCHAR(20) DEFAULT 'queued',
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT
);

-- Agent Memory Table (pgvector)
CREATE TABLE agent_memory (
    memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(50) NOT NULL,
    memory_type VARCHAR(50),
    content TEXT,
    embedding vector(1536), -- OpenAI ada-002 dimensions
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Agent Telemetry Table
CREATE TABLE agent_telemetry (
    telemetry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    unit VARCHAR(20),
    timestamp TIMESTAMPTZ DEFAULT now(),
    metadata JSONB
);
```

---

### Integration Components (PLS-004 through PLS-006)

#### PLS-004: Agent Health Check System
**Owner**: Echo
**Description**: Implement health monitoring for all 7 agents with automatic failover

**Deliverables**:
- `/pulser/health/agent_monitor.py` - Agent health checker
- `/pulser/health/failover.py` - Failover logic
- `/pulser/health/alerts.py` - Alert notifications
- Cron job for periodic health checks

**Acceptance Criteria**:
- [ ] Health checks run every 30 seconds
- [ ] Agent status: `healthy`, `degraded`, `unhealthy`
- [ ] Automatic failover to backup agent
- [ ] Slack/email alerts on agent failure
- [ ] Health history stored in Supabase

**Monitoring Metrics**:
- Response time (P50, P95, P99)
- Success rate (last 100 tasks)
- Error rate (last hour)
- Memory usage (MB)
- Task queue depth

---

#### PLS-005: MCP Coordinator Service
**Owner**: Arkie
**Description**: Create MCP server coordinator for managing 7 MCP server connections

**Deliverables**:
- `/pulser/mcp/coordinator.py` - MCP coordination logic
- `/pulser/mcp/server_manager.py` - Server lifecycle management
- `/pulser/mcp/tool_registry.py` - Tool catalog (98 tools)
- MCP health checks integration

**Acceptance Criteria**:
- [ ] All 7 MCP servers start successfully
- [ ] Tool registry populated (98 tools)
- [ ] MCP server health checks working
- [ ] Automatic reconnection on failure
- [ ] Tool call logging to Supabase

**MCP Servers**:
1. pulser-hub (Odoo integration)
2. digitalocean (App Platform)
3. kubernetes (Cluster ops)
4. docker (Container management)
5. github (Repository management)
6. superset (Analytics)
7. supabase (Database operations)

---

#### PLS-006: Task Routing Logic
**Owner**: Pulser
**Description**: Implement intelligent task routing to agents based on task type and priority

**Deliverables**:
- `/pulser/router/task_router.py` - Main routing logic
- `/pulser/router/priority_queue.py` - Priority-based queuing
- `/pulser/router/agent_selector.py` - Agent selection algorithm
- `/pulser/router/load_balancer.py` - Load distribution

**Acceptance Criteria**:
- [ ] Task types map to correct agents
- [ ] Priority queue respects high/medium/low
- [ ] Load balancing across multiple instances
- [ ] Automatic retry on agent failure (max 3 retries)
- [ ] Task routing metrics logged

**Routing Rules**:
```python
TASK_AGENT_MAPPING = {
    "analytics": "dash",
    "documentation": "maya",
    "testing": "echo",
    "data_pipeline": "data_fabcon",
    "infrastructure": "arkie",
    "skills_mining": "learnbot",
    "orchestration": "pulser"
}
```

---

### Deployment Components (PLS-007 through PLS-010)

#### PLS-007: Agent Telemetry Dashboard
**Owner**: Dash
**Description**: Create Superset dashboard for agent performance monitoring

**Deliverables**:
- Superset dashboard: "Pulser Agent Telemetry"
- 5 charts:
  1. Task throughput (tasks/hour by agent)
  2. Agent response time (P95 by agent)
  3. Error rate heatmap (by agent and hour)
  4. Task queue depth (real-time)
  5. Agent health status (traffic light)
- SQL views in Supabase for dashboard queries

**Acceptance Criteria**:
- [ ] Dashboard loads in <3 seconds
- [ ] Real-time data refresh (30 second intervals)
- [ ] RLS policies enforce company isolation
- [ ] Export to PDF/PNG working
- [ ] Email scheduled reports configured

**Dashboard URL**: `https://insightpulseai.net/odoo/superset/dashboard/pulser-telemetry`

---

#### PLS-008: Integration Tests (pytest)
**Owner**: Echo
**Description**: Write comprehensive integration tests for Pulser runtime

**Deliverables**:
- `/tests/integration/test_task_submission.py`
- `/tests/integration/test_agent_routing.py`
- `/tests/integration/test_mcp_integration.py`
- `/tests/integration/test_health_checks.py`
- `/tests/integration/test_failover.py`
- CI integration with GitHub Actions

**Acceptance Criteria**:
- [ ] >80% code coverage
- [ ] All critical paths tested
- [ ] MCP server mocks working
- [ ] Async task testing with pytest-asyncio
- [ ] Integration tests run in <5 minutes
- [ ] CI gate blocks PRs on test failures

**Test Categories**:
- Task submission API (POST /api/v1/tasks)
- Agent health monitoring
- MCP server coordination
- Failover scenarios
- Load balancing

---

#### PLS-009: DigitalOcean App Platform Spec
**Owner**: Arkie
**Description**: Create App Platform specification for Pulser deployment

**Deliverables**:
- `infra/do/pulser-orchestrator.yaml` - App spec
- Environment variable configuration
- Health check endpoints
- Auto-scaling rules (2-4 instances)

**Acceptance Criteria**:
- [ ] YAML spec validates with `doctl apps spec validate`
- [ ] Health check endpoint configured
- [ ] Environment variables set (Supabase, Redis)
- [ ] Auto-scaling triggers defined
- [ ] Build time <10 minutes

**App Spec Template**:
```yaml
name: pulser-orchestrator
region: sgp
services:
  - name: pulser-api
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    source_dir: pulser
    dockerfile_path: pulser/Dockerfile
    http_port: 8000
    instance_count: 2
    instance_size_slug: basic-xs
    routes:
      - path: /
    health_check:
      http_path: /health
      initial_delay_seconds: 30
      period_seconds: 10
      timeout_seconds: 5
      success_threshold: 1
      failure_threshold: 3
    envs:
      - key: SUPABASE_URL
        scope: RUN_TIME
        value: ${SUPABASE_URL}
      - key: REDIS_URL
        scope: RUN_TIME
        value: ${REDIS_URL}
      - key: CELERY_WORKERS
        scope: RUN_TIME
        value: "4"
```

---

#### PLS-010: Deploy Pulser v4.0.0 to Production
**Owner**: Arkie
**Description**: Deploy Pulser orchestrator to DigitalOcean App Platform

**Deliverables**:
- Production deployment to SGP region
- DNS configuration (pulser.insightpulseai.net)
- SSL certificate setup
- Monitoring dashboards live
- Rollback plan documented

**Acceptance Criteria**:
- [ ] App deployed and healthy
- [ ] Health endpoint returns 200 OK
- [ ] Task submission API working
- [ ] All 7 MCP servers connected
- [ ] Telemetry dashboard live
- [ ] Zero downtime deployment tested

**Deployment Commands**:
```bash
# Deploy to DigitalOcean
doctl apps create --spec infra/do/pulser-orchestrator.yaml

# Get app ID
export PULSER_APP_ID=$(doctl apps list | grep pulser-orchestrator | awk '{print $1}')

# Monitor deployment
doctl apps logs $PULSER_APP_ID --follow

# Verify health
curl -s https://pulser.insightpulseai.net/health | jq
```

---

## 🚧 Known Issues

### Critical ⚠️
- None at this time

### High 🔴
- [ ] **Issue-PLS-001**: Redis connection pooling limits
  - **Impact**: Task queue bottleneck at high volume (>1000 tasks/hour)
  - **Action**: Configure Redis connection pool (max 50 connections)
  - **Owner**: Arkie
  - **Deadline**: 2025-11-11

### Medium 🟡
- [ ] **Issue-PLS-002**: Celery task timeout defaults
  - **Impact**: Long-running tasks may timeout prematurely
  - **Action**: Set task-specific timeouts (analytics: 10min, deployment: 30min)
  - **Owner**: Arkie
  - **Deadline**: 2025-11-12

### Low 🟢
- [ ] **Issue-PLS-003**: Missing agent avatar images
  - **Impact**: Poor UX in telemetry dashboard
  - **Action**: Create 7 agent avatars (Dash, Maya, Echo, Data Fabcon, Arkie, LearnBot, Pulser)
  - **Owner**: Maya
  - **Deadline**: 2025-11-14

---

## ✅ Recently Completed (Last 7 Days)

- [x] **PRD_PULSER.md created** (600+ lines, comprehensive agent specs)
- [x] **Documentation suite planned** (5 files: PRD, tasks, planning, changelog, doc.yaml)
- [x] **Agent specifications finalized** (7 agents with clear responsibilities)
- [x] **MCP server inventory** (7 servers, 98 tools mapped to agents)
- [x] **API contract defined** (Task submission, status, health endpoints)

---

## 📊 Sprint Metrics (Sprint 5 - Pulser Development)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Tasks Completed** | 10/10 | 0/10 | 🔴 Not Started |
| **Code Coverage** | >80% | 0% | 🔴 Not Started |
| **Integration Tests** | 20 tests | 0 tests | 🔴 Not Started |
| **Documentation** | 5 files | 2/5 | 🟡 In Progress |
| **Deployment Ready** | Yes | No | 🔴 Not Started |
| **Agent Health** | >99.5% | N/A | ⏳ Pending |

**Sprint Velocity**: 0 tasks/day (target: 2 tasks/day)
**Sprint Progress**: 0% complete (0 of 10 tasks done)

---

## 📋 Backlog (Future Sprints)

### Sprint 6: Agent Enhancements (Nov 16-22, 2025)
- [ ] **PLS-011**: Implement agent memory persistence (pgvector)
- [ ] **PLS-012**: Add agent learning from telemetry
- [ ] **PLS-013**: Create agent performance benchmarks
- [ ] **PLS-014**: Implement agent workload prediction
- [ ] **PLS-015**: Add agent collaboration workflows

### Sprint 7: Scalability (Nov 23-29, 2025)
- [ ] **PLS-016**: Implement horizontal scaling (4-8 instances)
- [ ] **PLS-017**: Add task queue sharding
- [ ] **PLS-018**: Optimize Redis memory usage
- [ ] **PLS-019**: Implement agent autoscaling
- [ ] **PLS-020**: Add task prioritization ML model

### Sprint 8: Production Hardening (Nov 30 - Dec 6, 2025)
- [ ] **PLS-021**: Add comprehensive error handling
- [ ] **PLS-022**: Implement circuit breakers
- [ ] **PLS-023**: Add request rate limiting
- [ ] **PLS-024**: Implement audit logging
- [ ] **PLS-025**: Add security scanning (OWASP)

---

## 🔗 Related Documents

### Pulser Documentation
- **PRD**: `docs/pulser/PRD_PULSER.md` (product requirements, agent specs)
- **Tasks**: `docs/pulser/tasks.md` (this file - task manifest)
- **Planning**: `docs/pulser/planning.md` (sprint timeline, milestones)
- **Changelog**: `docs/pulser/CHANGELOG_PULSER.md` (version history)
- **Metadata**: `docs/pulser/doc.yaml` (Spec-Kit metadata)

### Main Project Documentation
- **Main PRD**: `PRD.md` (overall InsightPulse platform)
- **Main Tasks**: `TASKS.md` (project-wide task tracking)
- **Main Planning**: `PLANNING.md` (Wave 1-9 milestones)
- **Main Changelog**: `CHANGELOG.md` (semantic versioning)
- **Claude Context**: `CLAUDE.md` (AI assistant contract)

### Technical References
- **Architecture**: `docs/SUPERCLAUDE_ARCHITECTURE.md` (multi-agent system)
- **MCP Config**: `mcp/vscode-mcp-config.json` (7 server definitions)
- **API Spec**: `docs/pulser/PRD_PULSER.md#api-specification` (OpenAPI endpoints)
- **Deployment**: `infra/do/pulser-orchestrator.yaml` (App Platform spec)

---

## 📝 Task Conventions

### Status Labels
- `⏳ Pending` - Not started, dependencies may block
- `🚧 In Progress` - Currently active work
- `✅ Done` - Completed and validated
- `🚫 Blocked` - Cannot proceed due to dependency
- `⏸️ Paused` - Temporarily suspended
- `❌ Cancelled` - No longer needed

### Priority Levels
- **Critical**: Blocks deployment or violates SLA
- **High**: Required for Sprint 5 completion
- **Medium**: Important but can be deferred to Sprint 6
- **Low**: Nice-to-have, future optimization

### Task ID Format
- **PLS-XXX**: Pulser-specific tasks (001-099 = Sprint 5, 100-199 = Sprint 6+)
- **Issue-PLS-XXX**: Known issues requiring resolution

### Task Format (Markdown)
```markdown
| ID | Title | Agent | Category | Status | Deadline |
|----|--------|--------|-----------|----------|----------|
| PLS-XXX | Task description | Agent Name | Category | ⏳ Pending | YYYY-MM-DD |
```

---

**Maintainer**: InsightPulse AI Team (Pulser Orchestration Division)
**Repository**: https://github.com/jgtolentino/insightpulse-odoo
**License**: AGPL-3.0
**Pulser Version**: 4.0.0
**Last Updated**: 2025-11-09 (Sprint 5 task manifest created)
