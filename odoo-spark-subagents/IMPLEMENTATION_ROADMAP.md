# Implementation Roadmap: Knowledge-First Automation

> **Goal**: Deploy exponential automation system in 4 weeks

This roadmap takes the odoo-spark-subagents project from **blueprint** (current state: 15-20% implemented) to **production-ready knowledge-first automation system**.

---

## 📋 Executive Summary

**Current State**: Well-architected design specification with placeholder implementations

**Target State**: Functional knowledge-first automation that learns and improves daily

**Timeline**: 4 weeks (1 FTE) or 2 weeks (2 FTEs)

**Cost**: ~$100/month recurring (OpenAI + Supabase)

**ROI**: $4,000/month saved developer time (conservative estimate)

---

## 🎯 Sprint Breakdown

### Sprint 1: Knowledge Foundation (Week 1)
**Goal**: Deploy the knowledge graph and start harvesting Odoo knowledge

#### Day 1-2: Infrastructure Setup
- [ ] **Supabase Setup**
  ```bash
  # Create production Supabase project
  # Enable pgvector extension
  # Run schema migration
  psql $POSTGRES_URL -f supabase/schema/knowledge_graph.sql

  # Verify tables created
  psql $POSTGRES_URL -c "\dt"
  ```

- [ ] **Environment Configuration**
  ```bash
  # Move secrets to vault (not .env)
  # Required secrets:
  - SUPABASE_URL
  - SUPABASE_SERVICE_ROLE (NOT anon key)
  - OPENAI_API_KEY
  - GITHUB_TOKEN (for OCA scraping)
  ```

- [ ] **Dependencies Installation**
  ```bash
  pip install httpx beautifulsoup4 supabase-py openai pydantic pytest-cov
  ```

#### Day 3-4: Initial Knowledge Harvest
- [ ] **Run Odoo Scraper**
  ```bash
  # Initial scrape (expect 1-2 hours, ~$3 OpenAI cost)
  make knowledge_scrape

  # Verify indexing
  psql $POSTGRES_URL -c "SELECT source_type, COUNT(*) FROM odoo_knowledge GROUP BY source_type;"

  # Expected results:
  # docs        | 1000+
  # forum       | 2000+
  # github_issue| 500+
  ```

- [ ] **Test Knowledge Search**
  ```bash
  make knowledge_demo

  # Should return relevant results for:
  # - "create sales order validation"
  # - "migrate from version 18 to 19"
  ```

#### Day 5: Integration Tests
- [ ] **Create Integration Test Suite**
  ```bash
  # tests/integration/test_knowledge_system.py
  pytest tests/integration/ -v
  ```

  Tests:
  - Scrape → Index → Search end-to-end
  - Embedding generation performance
  - Semantic search accuracy
  - Duplicate detection

**Sprint 1 Deliverable**:
✅ Knowledge graph with 3,000+ Odoo documents searchable via semantic search

---

### Sprint 2: Self-Improving Skills (Week 2)
**Goal**: Enable automatic skill generation from successful runs

#### Day 6-7: Agent Runtime Integration
- [ ] **Implement Minimal Agent Runtime**
  ```python
  # agents/runtime/executor.py
  class AgentExecutor:
      def __init__(self):
          self.knowledge = KnowledgeClient.from_env()
          self.harvester = SkillHarvester.from_env()
          self.learner = ErrorLearner.from_env()

      def execute(self, agent_name: str, input: Dict) -> Result:
          # 1. Get context from knowledge
          context = self.knowledge.get_context_for_task(
              task_description=input.get("task"),
              agent_name=agent_name
          )

          # 2. Execute agent (placeholder for now)
          try:
              result = self._execute_agent(agent_name, input, context)

              # 3. On success: harvest skill
              if result.status == "success" and result.human_approved:
                  self.harvester.maybe_harvest(result.trace_id, "success", True)

              return result

          except Exception as e:
              # 4. On failure: learn error
              self.learner.on_failure(result.trace_id, e, context)
              raise
  ```

- [ ] **Create Test Agent Runs**
  ```bash
  # Simulate 10 successful agent runs with dummy data
  # Verify skill harvesting triggers
  make knowledge_harvest

  # Expected: 2-3 new skills auto-generated
  psql $POSTGRES_URL -c "SELECT name, category FROM skills WHERE created_from_trace_id IS NOT NULL;"
  ```

#### Day 8-9: Skill Quality Validation
- [ ] **Review Auto-Generated Skills**
  - Check SKILL.md formatting
  - Validate examples are concrete
  - Ensure dependencies are correct

- [ ] **A/B Test Skill Usage**
  ```python
  # Implement skill versioning
  # Test: agents with auto-generated skills vs. without
  # Measure: success rate, confidence score
  ```

#### Day 10: Error Learning Pipeline
- [ ] **Implement Error Learner Integration**
  ```python
  # In agent exception handler
  try:
      result = agent.execute(input)
  except ValidationError as e:
      learner.on_failure(trace_id, e, {
          "agent_name": "automation_executor",
          "input": input,
          "plan": plan
      })
      # Auto-generates guardrail skill
  ```

- [ ] **Test Error → Guardrail Flow**
  1. Simulate agent failure
  2. Verify root cause analysis
  3. Check guardrail skill generated
  4. Confirm error doesn't repeat

**Sprint 2 Deliverable**:
✅ Skill library growing automatically (5+ auto-generated skills)
✅ Error learning pipeline active

---

### Sprint 3: Daily Automation Loop (Week 3)
**Goal**: Deploy continuous learning system

#### Day 11-12: Cron Job Setup
- [ ] **Configure Daily Automation**
  ```bash
  # Add to crontab
  crontab -e

  # Add line:
  0 2 * * * cd /path/to/odoo-spark-subagents && make knowledge_daily >> /var/log/knowledge-automation.log 2>&1
  ```

- [ ] **Monitoring Setup**
  ```bash
  # Create Grafana dashboard
  # Metrics to track:
  - Skills added per day
  - Knowledge docs indexed per day
  - Error resolution rate
  - Agent success rate trend
  ```

#### Day 13-14: Observability Integration
- [ ] **OpenTelemetry Setup**
  ```python
  # Export to your OTEL collector
  from opentelemetry import trace
  from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

  tracer = trace.get_tracer(__name__)

  # In knowledge client:
  with tracer.start_as_current_span("knowledge.search_skills") as span:
      results = self.search_skills(query)
      span.set_attribute("results.count", len(results))
  ```

- [ ] **Prometheus Metrics**
  ```python
  from prometheus_client import Counter, Histogram, Gauge

  skill_growth = Gauge("skill_library_total", "Total skills in library")
  knowledge_docs = Gauge("knowledge_docs_total", "Total knowledge documents")
  error_resolution_time = Histogram("error_resolution_seconds", "Time to resolve errors")
  ```

#### Day 15: Analytics Dashboards
- [ ] **Create Superset Dashboards**
  - Skill growth chart (weekly trend)
  - Agent performance over time
  - Knowledge coverage by topic
  - Error reduction curve

**Sprint 3 Deliverable**:
✅ Automated daily knowledge loop running
✅ Metrics dashboards live
✅ System learning without human intervention

---

### Sprint 4: Production Hardening (Week 4)
**Goal**: Security, reliability, and scale

#### Day 16-17: Security Audit
- [ ] **Secrets Management**
  ```bash
  # Move all secrets to HashiCorp Vault or AWS Secrets Manager
  # Rotate all API keys
  # Enable secret scanning in CI
  ```

- [ ] **Input Validation**
  ```python
  # Add JSON Schema validation for all agent YAML configs
  from jsonschema import validate

  AGENT_SCHEMA = {...}
  validate(instance=agent_config, schema=AGENT_SCHEMA)
  ```

- [ ] **Rate Limiting**
  ```python
  # scripts/knowledge/odoo_scraper.py
  from ratelimit import limits, sleep_and_retry

  @sleep_and_retry
  @limits(calls=100, period=60)  # 100 calls per minute
  def scrape_page(url):
      ...
  ```

#### Day 18-19: Reliability Improvements
- [ ] **Retry Logic**
  ```python
  from tenacity import retry, stop_after_attempt, wait_exponential

  @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
  def create_embedding(text):
      return self.openai.embeddings.create(...)
  ```

- [ ] **Circuit Breaker**
  ```python
  from pybreaker import CircuitBreaker

  breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

  @breaker
  def call_external_api():
      ...
  ```

- [ ] **Graceful Degradation**
  ```python
  # If knowledge search fails, fall back to basic mode
  try:
      context = knowledge.get_context_for_task(task, agent)
  except Exception:
      context = {"relevant_skills": [], "knowledge_docs": []}
      # Agent still works, just without enhanced context
  ```

#### Day 19-20: Performance Optimization
- [ ] **Connection Pooling**
  ```python
  # Use connection pool for Supabase
  from supabase import create_client

  supabase = create_client(url, key, options={
      "pool_max_size": 10,
      "pool_timeout": 30
  })
  ```

- [ ] **Embedding Caching**
  ```python
  # Cache embeddings to avoid re-computing
  from functools import lru_cache

  @lru_cache(maxsize=1000)
  def get_embedding(text_hash: str) -> List[float]:
      # Check Redis cache first
      # Fall back to OpenAI if not found
  ```

- [ ] **Batch Processing**
  ```python
  # Process skills in batches for efficiency
  def index_batch(docs: List[KnowledgeDocument], batch_size=50):
      for i in range(0, len(docs), batch_size):
          batch = docs[i:i+batch_size]
          embeddings = self.openai.embeddings.create(input=[d.content for d in batch])
          # Bulk insert to Supabase
  ```

**Sprint 4 Deliverable**:
✅ Production-ready security posture
✅ Reliable error handling and retries
✅ Performance optimized for scale

---

## 🚀 Launch Checklist

Before going live:

### Infrastructure
- [ ] Supabase production instance configured
- [ ] PostgreSQL backups enabled (daily)
- [ ] Secrets in vault (not environment variables)
- [ ] HTTPS enforced for all endpoints
- [ ] Rate limiting configured

### Testing
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass
- [ ] E2E smoke test passes
- [ ] Load testing completed (1000 searches/hour)

### Monitoring
- [ ] Grafana dashboards deployed
- [ ] Alerting rules configured:
  - Knowledge scrape failures
  - Skill harvesting errors
  - Search latency > 2s
  - Daily automation job failures
- [ ] On-call rotation configured

### Documentation
- [ ] Runbook created (what to do when alerts fire)
- [ ] Architecture diagrams updated
- [ ] API documentation generated
- [ ] User guide written

### Rollout
- [ ] Staged rollout plan:
  - Week 1: 10% of agents use knowledge system
  - Week 2: 50% of agents
  - Week 3: 100% of agents
- [ ] Rollback plan documented
- [ ] Incident response plan

---

## 📊 Success Criteria (4 Weeks)

### Week 1
- ✅ 3,000+ Odoo documents indexed
- ✅ Semantic search working
- ✅ <500ms search latency (p95)

### Week 2
- ✅ 5+ auto-generated skills
- ✅ Skill harvesting working on successful runs
- ✅ Error learning pipeline functional

### Week 3
- ✅ Daily automation running reliably
- ✅ Metrics dashboards live
- ✅ 10+ skills auto-generated (cumulative)

### Week 4
- ✅ Security audit passed
- ✅ Production deployment complete
- ✅ 20+ skills total (growing daily)

---

## 💰 Budget

### One-Time Costs
| Item | Cost |
|------|------|
| Developer time (4 weeks) | $16,000 |
| Initial Odoo scrape (OpenAI) | $5 |
| Supabase setup | $0 (free tier) |
| **Total** | **$16,005** |

### Recurring Monthly Costs
| Item | Cost |
|------|------|
| Supabase Pro | $25 |
| OpenAI embeddings | $30 |
| OpenAI GPT-4 (skill/error gen) | $20 |
| Monitoring (Grafana Cloud) | $0 (free tier) |
| **Total** | **$75/month** |

### ROI Calculation
| Item | Value |
|------|-------|
| Developer time saved | $4,000/month |
| Recurring costs | -$75/month |
| **Net savings** | **$3,925/month** |
| **Payback period** | **4.1 months** |
| **Annual ROI** | **293%** |

---

## 🎯 Key Milestones & Metrics

### Milestone 1: Knowledge Bootstrap (Day 4)
- **Metric**: 3,000+ documents indexed
- **Validation**: `make knowledge_demo` returns relevant results

### Milestone 2: First Auto-Generated Skill (Day 10)
- **Metric**: 1+ skill with `created_from_trace_id` not null
- **Validation**: Skill is human-readable and reusable

### Milestone 3: Continuous Learning Loop (Day 15)
- **Metric**: Cron job running without failures for 3 consecutive days
- **Validation**: Daily logs show new skills/docs added

### Milestone 4: Production Launch (Day 28)
- **Metric**: 100% of agents using knowledge system
- **Validation**: Agent success rate improved by 15%+

---

## 🚧 Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OpenAI rate limits | Medium | High | Implement retry logic + fallback to cached embeddings |
| Supabase downtime | Low | High | Deploy read replicas + local cache |
| Poor skill quality | Medium | Medium | Human review queue for auto-generated skills |
| Scraper blocked | Medium | Low | Rotate IPs + respect robots.txt + backoff |
| Cost overrun | Low | Medium | Set monthly budget alerts + use embedding cache |

---

## 📞 Support & Escalation

### During Implementation
- **Technical issues**: Slack #odoo-spark-dev
- **Blocker escalation**: Project lead (2-hour SLA)

### Post-Launch
- **P0 (system down)**: On-call rotation (15-min SLA)
- **P1 (degraded)**: Async via Slack (4-hour SLA)
- **P2 (enhancement)**: GitHub issues (48-hour SLA)

---

## 🎓 Team Enablement

### Week 1: Knowledge Session
- **Topic**: "How the Knowledge System Works"
- **Audience**: All developers
- **Duration**: 1 hour
- **Outcome**: Team understands architecture

### Week 2: Hands-On Workshop
- **Topic**: "Building Your First Auto-Generated Skill"
- **Audience**: Agent developers
- **Duration**: 2 hours
- **Outcome**: Developers can integrate knowledge client

### Week 3: Metrics Deep Dive
- **Topic**: "Reading the Knowledge Growth Dashboards"
- **Audience**: Product + Engineering
- **Duration**: 1 hour
- **Outcome**: Team tracks exponential growth

### Week 4: Runbook Training
- **Topic**: "Operating the Knowledge System"
- **Audience**: On-call engineers
- **Duration**: 1 hour
- **Outcome**: Team can respond to incidents

---

## ✅ Next Actions (Right Now)

### For Project Lead
1. **Allocate Budget**: Approve $16K + $75/month
2. **Assign Team**: 1-2 FTEs for 4 weeks
3. **Create Kickoff**: Schedule Sprint 1 kickoff meeting

### For Engineering
1. **Environment Setup**: Create Supabase project
2. **Run First Command**: `make knowledge_setup`
3. **Review This Doc**: Understand the 4-week plan

### For Product
1. **Define Success Metrics**: What's "exponential growth" for your use case?
2. **Stakeholder Buy-In**: Get approval to deploy experimental system
3. **Communication Plan**: How to announce to users?

---

**Ready to start?**

```bash
make knowledge_setup
```

Then follow Sprint 1, Day 1-2 instructions above.

---

**Questions?** Open an issue or reach out on Slack.

**Let's build exponential automation! 🚀**
