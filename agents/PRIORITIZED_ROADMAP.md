# InsightPulse AI - Prioritized Execution Roadmap
**Version:** 1.0.0
**Created:** 2025-11-22
**Purpose:** Transform InsightPulse stack into fully autonomous agent-driven platform

---

## 🎯 Vision

Convert the InsightPulse Odoo CE + Supabase + n8n stack into a **self-improving, agent-orchestrated system** where:

- **Skills** = atomic capabilities agents can execute
- **Capabilities** = composite workflows combining skills
- **Knowledge** = continuously learning from patterns, docs, and outcomes
- **Procedures** = autonomous execution playbooks
- **Automation** = reduces manual work by 80%+

---

## 📊 Current State Assessment

### ✅ What's Working (Keep Building On)

| Component | Status | Quality | Notes |
|-----------|--------|---------|-------|
| **Odoo CE 18** | 🟢 Production | High | 5 custom modules deployed |
| **OCR Pipeline** | 🟢 Production | Good | 85%+ accuracy, needs iteration |
| **Flutter Mobile** | 🟡 Built | Medium | Not yet deployed to devices |
| **M1 Deploy Script** | 🟢 Production | High | One-shot deployment works |
| **CI/CD Guardrails** | 🟢 Active | High | CE/OCA checks enforced |
| **Docker Compose** | 🟢 Production | Medium | Works, but not K8s yet |

### ⚠️ What's Partially Implemented (Complete These First)

| Component | Status | Gap | Priority |
|-----------|--------|-----|----------|
| **n8n Workflows** | 🟡 Partial | Only 5-10% of planned workflows exist | HIGH |
| **Supabase Integration** | 🟡 Partial | Used for OCR, not for Odoo sync | MEDIUM |
| **Knowledge Base** | 🟡 Partial | Docs exist, not indexed for agents | HIGH |
| **Agent Framework** | 🔴 Missing | Just created, not operational | HIGH |

### ❌ What's Missing (Build These Next)

| Component | Status | Impact | Priority |
|-----------|--------|--------|----------|
| **MCP Servers** | 🔴 Missing | Can't expose Odoo/Supabase to agents | HIGH |
| **Mattermost Integration** | 🔴 Missing | No chat-based agent interface | MEDIUM |
| **Superset Dashboards** | 🔴 Missing | No analytics visibility | LOW |
| **Kubernetes Manifests** | 🔴 Missing | Stuck on Docker Compose | MEDIUM |
| **Auto-healing Automation** | 🔴 Missing | No self-recovery from failures | MEDIUM |

---

## 🗺️ Execution Phases

### **Phase 0: Foundation (Week 1-2)** ⏳ CURRENT

**Goal:** Make the agent skills framework operational

#### Tasks:
- [x] Create agent skills registry (`AGENT_SKILLS_REGISTRY.yaml`)
- [x] Define capability matrix (`CAPABILITY_MATRIX.yaml`)
- [x] Build knowledge base index (`KNOWLEDGE_BASE_INDEX.yaml`)
- [x] Document execution procedures (`EXECUTION_PROCEDURES.yaml`)
- [ ] Create master orchestrator prompt (`ORCHESTRATOR.md`)
- [ ] Test agent skills with real tasks
- [ ] Document how to invoke skills from Claude Code CLI

#### Success Criteria:
- Agent can execute at least 3 skills autonomously
- Knowledge base searchable and referenced
- Procedures followed successfully in practice

#### Estimated Duration: **1-2 weeks**

---

### **Phase 1: Complete n8n Automation Library (Week 3-4)**

**Goal:** Deploy all planned n8n workflows for finance ops

#### Priority Workflows:

**High Priority (Week 3):**
1. `W001_OD_MNTH_CLOSE_SYNC` - Daily closing digest
2. `W002_OD_BIR_ALERTS` - BIR deadline alerts
3. `W101_SB_CLOSE_SNAPSHOT` - Monthly close data snapshot
4. `W401_CC_EXPENSE_IMPORT` - Email → expense creation

**Medium Priority (Week 4):**
5. `W402_CC_TRAVEL_APPROVAL` - Travel approval workflow
6. `W501_EQ_BOOKING_SYNC` - Equipment booking calendar sync
7. `W502_EQ_OVERDUE_ALERTS` - Overdue equipment alerts
8. `W301_NO_CLOSE_MIRROR` - Notion closing board mirror

#### Agent Skills to Use:
- `create_n8n_workflow`
- `deploy_n8n_workflow`
- `send_bir_alerts`

#### Success Criteria:
- 8+ workflows deployed and active
- All workflows follow conventions (WNNN_DD_DESCRIPTION)
- Registered in `workflows/index.yaml`
- Daily execution logs show success

#### Estimated Duration: **2 weeks**

---

### **Phase 2: MCP Server Infrastructure (Week 5-6)**

**Goal:** Expose Odoo, Supabase, n8n to agent ecosystem via MCP

#### MCP Servers to Build:

1. **odoo-mcp-server**
   - Expose Odoo JSON-RPC via MCP protocol
   - Skills: create records, search, update, execute workflows
   - Auth: API key from Odoo admin user

2. **supabase-mcp-server**
   - Expose Supabase REST API + PostgreSQL
   - Skills: query tables, create records, upload to storage
   - Auth: Service role key

3. **n8n-mcp-server**
   - Expose n8n workflow execution API
   - Skills: trigger workflows, get execution status
   - Auth: n8n API key

#### Agent Skills to Create:
- `build_mcp_server`
- `deploy_mcp_server`
- `test_mcp_integration`

#### Success Criteria:
- 3 MCP servers deployed and accessible
- Agents can query Odoo, Supabase, n8n via MCP
- Authentication and rate limiting working

#### Estimated Duration: **2 weeks**

---

### **Phase 3: Improve OCR to 90%+ Quality (Week 7-8)**

**Goal:** Achieve 90%+ OCR success rate through iteration

#### Iteration Plan:

**Week 7: Data Collection**
- Collect 100+ real PH receipts (SM, 7-Eleven, Jollibee, Max's, etc.)
- Create ground_truth.csv for all receipts
- Run test harness baseline: measure current accuracy

**Week 8: Normalization & Testing**
- Add 20+ vendor normalization rules
- Add 5+ date format patterns
- Add currency defaulting for PH vendors
- Run test harness after each change
- Deploy adapter updates incrementally

#### Agent Skills to Use:
- `test_ocr_quality`
- `add_ocr_normalization`
- `analyze_odoo_logs`

#### Success Criteria:
- OCR success rate >= 90% (target: 85% baseline → 90%+)
- P95 latency < 30 seconds
- Date accuracy >= 95%
- Total accuracy >= 95% (±1 peso)
- Vendor accuracy >= 90%

#### Estimated Duration: **2 weeks**

---

### **Phase 4: Deploy Mobile OCR Client (Week 9-10)**

**Goal:** Get Flutter app on iOS/Android test devices

#### Tasks:

**Week 9: Mobile Testing**
- Build APK for Android: `flutter build apk --release`
- Build IPA for iOS: `flutter build ios --release`
- Deploy to test devices (3-5 testers)
- Test with 20+ real receipts
- Measure: upload time, OCR time, cache retrieval

**Week 10: Integration**
- Implement Odoo integration (webhook or cron)
- Auto-create `hr.expense` records from `parsed_receipts`
- Test approval workflows
- Deploy to production

#### Agent Skills to Use:
- `build_flutter_module`
- `test_flutter_integration`
- `deploy_mobile_ocr`

#### Success Criteria:
- App runs on Android and iOS
- Upload time < 2 seconds
- Cache retrieval < 500ms
- Auto-expense creation works
- 10+ users successfully scanning receipts

#### Estimated Duration: **2 weeks**

---

### **Phase 5: Kubernetes + Auto-Scaling (Week 11-12)**

**Goal:** Migrate from Docker Compose to Kubernetes for scalability

#### Migration Plan:

**Week 11: K8s Manifests**
- Create Kubernetes manifests for:
  - Odoo CE deployment + service
  - PostgreSQL StatefulSet
  - Nginx ingress controller
  - OCR adapter deployment
- Test on local Minikube or DigitalOcean DOKS

**Week 12: Production Migration**
- Provision DigitalOcean Kubernetes cluster
- Deploy to K8s staging
- Migrate production (with rollback plan)
- Configure auto-scaling rules

#### Agent Skills to Create:
- `scaffold_k8s_manifests`
- `deploy_to_kubernetes`
- `configure_autoscaling`

#### Success Criteria:
- Odoo running on K8s
- Auto-scaling based on CPU/memory
- Zero downtime during migration
- Rollback plan tested

#### Estimated Duration: **2 weeks**

---

### **Phase 6: Mattermost + Chat Agent (Week 13-14)**

**Goal:** Deploy Mattermost with Claude-based chat agent

#### Components:

1. **Mattermost Deployment**
   - Deploy Mattermost on DigitalOcean
   - Integrate with Odoo SSO (optional)
   - Create channels: #ops, #finance, #alerts

2. **Chat Agent**
   - Claude Code CLI bot in Mattermost
   - Skills: query Odoo, trigger n8n, check OCR logs
   - Triggered by: @agent or /command

3. **Alert Integration**
   - n8n workflows send alerts to Mattermost
   - BIR deadlines, overdue tasks, OCR failures

#### Agent Skills to Create:
- `deploy_mattermost`
- `create_chat_agent`
- `integrate_mattermost_n8n`

#### Success Criteria:
- Mattermost accessible at chat.insightpulseai.net
- Chat agent responds to queries
- n8n alerts appear in #alerts channel

#### Estimated Duration: **2 weeks**

---

### **Phase 7: Superset Analytics (Week 15-16)**

**Goal:** Deploy Superset dashboards for visibility

#### Dashboards to Build:

1. **Expense Analytics**
   - Monthly expense trends
   - By vendor, category, employee
   - Budget vs actual

2. **Equipment Utilization**
   - Booking frequency
   - Overdue incidents
   - Asset condition tracking

3. **OCR Quality Metrics**
   - Success rate over time
   - P95 latency trends
   - Vendor-wise accuracy

4. **Finance Closing SLA**
   - Task completion rate
   - Days to close
   - BIR filing compliance

#### Agent Skills to Create:
- `deploy_superset`
- `create_superset_dashboard`
- `connect_superset_postgres`

#### Success Criteria:
- Superset accessible at superset.insightpulseai.net
- 4 dashboards live and updating
- Read-only PostgreSQL connection secure

#### Estimated Duration: **2 weeks**

---

## 🚀 Quick Wins (Can Do Immediately)

These tasks can be done **in parallel** with phases above:

### Quick Win 1: Complete Odoo Module Deployment
- **Task:** Finish deploying `ipai_expense`, `ipai_equipment`, `ipai_finance_monthly_closing`
- **Duration:** 2-3 hours
- **Skills:** `deploy_odoo_module`

### Quick Win 2: Add 10 OCR Normalization Rules
- **Task:** Add top 10 failing PH vendors to normalization
- **Duration:** 1-2 hours
- **Skills:** `add_ocr_normalization`, `test_ocr_quality`

### Quick Win 3: Create 5 n8n Workflows
- **Task:** Build W001, W002, W101, W401, W501
- **Duration:** 3-4 hours
- **Skills:** `create_n8n_workflow`, `deploy_n8n_workflow`

### Quick Win 4: Setup Health Monitoring
- **Task:** Add UptimeRobot or similar for health checks
- **Duration:** 30 minutes
- **No agent skills needed (manual)**

---

## 📈 Success Metrics

### Platform Maturity

| Metric | Baseline | Target (6 months) |
|--------|----------|-------------------|
| **Automation Coverage** | 20% | 80%+ |
| **OCR Success Rate** | 85% | 90%+ |
| **Deployed n8n Workflows** | 2 | 20+ |
| **Agent Skills Available** | 15 | 50+ |
| **MCP Servers** | 0 | 3+ |
| **Uptime** | 99.0% | 99.5%+ |

### Developer Productivity

| Metric | Baseline | Target |
|--------|----------|--------|
| **Module Deployment Time** | 15 min | 5 min |
| **OCR Quality Iteration** | 2 hours | 30 min |
| **n8n Workflow Creation** | 1 hour | 15 min |
| **Issue Resolution Time** | 2 hours | 30 min |

### Business Impact

| Metric | Baseline | Target |
|--------|----------|--------|
| **Manual Expense Entry Time** | 10 min/expense | 2 min/expense |
| **Finance Closing Duration** | 10 days | 5 days |
| **Equipment Booking Conflicts** | 20%/month | <5%/month |
| **BIR Filing On-Time Rate** | 90% | 100% |

---

## 🎯 Next 3 Actions (Do Today)

1. **Test Agent Skills Framework**
   - Pick 1 simple task (e.g., "deploy ipai_expense module")
   - Use agent skills to execute
   - Document what works, what needs fixing

2. **Create W001_OD_MNTH_CLOSE_SYNC Workflow**
   - Use `create_n8n_workflow` skill
   - Follow WORKFLOW_CONVENTIONS.md
   - Deploy to n8n staging

3. **Add 5 OCR Normalization Rules**
   - Check ocr.expense.log for top 5 failing vendors
   - Add to VENDOR_NORMALIZATION in ocr-adapter/main.py
   - Run test harness
   - Deploy adapter update

---

## 📋 Tracking Progress

**How to use this roadmap:**

1. **Daily:** Pick 1-2 tasks from current phase
2. **Weekly:** Review progress, adjust priorities
3. **Monthly:** Measure success metrics, update roadmap

**Tools:**
- Use `TodoWrite` to track daily tasks
- Update this roadmap when phase completes
- Document learnings in knowledge base

---

## 🔄 Feedback Loop

**After each phase:**
1. What worked well?
2. What was harder than expected?
3. What new capabilities emerged?
4. Update AGENT_SKILLS_REGISTRY with new skills
5. Update KNOWLEDGE_BASE_INDEX with new patterns

---

**Status:** Phase 0 in progress
**Next Review:** 2025-12-06
**Owner:** InsightPulseAI Platform Team
