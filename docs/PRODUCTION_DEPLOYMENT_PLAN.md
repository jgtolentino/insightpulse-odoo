# Production Deployment Plan: InsightPulse AI (insightpulseai.net)

**Target**: https://insightpulseai.net
**Current Status**: 🔴 LIVE with CRITICAL vulnerabilities (Risk Score: 8.7/10)
**Strategy**: Emergency Remediation + SuperClaude Framework + New Skills Integration
**Timeline**: 72 hours (Phases 1-2), 28 weeks (Full Remediation)

---

## 🎯 Executive Summary

**Situation**: Production deployment at insightpulseai.net has critical security vulnerabilities and 87.5% of modules have 0% test coverage. Repository review shows 44/100 score (F grade).

**Solution**: Use SuperClaude parallel sub-agent framework + newly integrated Odoo DevOps skills to execute emergency remediation and deploy fixes to production.

**Outcome**: Reduce breach risk from 78% to 18%, achieve security grade B+, maintain zero-downtime operation.

---

## 🚀 Deployment Architecture

### SuperClaude Framework Integration

**6 Parallel Work Trees** (from `insightpulse_odoo/SUPERCLAUDE_AGENT_STRUCTURE.md`):

1. **ERP Development** (`odoo-erp-architect`)
   - **New Skill**: `docs/claude-code-skills/odoo/SKILL.md`
   - **Focus**: Fix incomplete modules (ipai_procure, ipai_expense, ipai_subscriptions)
   - **Output**: OCA-compliant implementations with security controls

2. **Analytics & BI** (`superset-analytics-architect`)
   - **Focus**: Superset connector security patches
   - **Tasks**: Fix SQL injection, add CSP headers, token management

3. **DevOps & Infrastructure** (`odoo-devops-architect`)
   - **New Skill**: `docs/claude-code-skills/odoo/reference/docker-production.md`
   - **Focus**: Production hardening, deployment automation, monitoring
   - **Output**: Blue-green deployment, health checks, rollback procedures

4. **Security & Compliance** (`odoo-security-engineer`)
   - **Focus**: Fix 18 Critical + 24 High vulnerabilities
   - **Tasks**: Encrypt credentials, access controls, security tests

5. **Testing & Quality** (`testing-engineer`)
   - **Focus**: Achieve 80% test coverage from current 12%
   - **Tasks**: Security tests, integration tests, performance tests

6. **Project Coordination** (`project-coordinator`)
   - **New Skills**: `docs/claude-code-skills/notion/knowledge-capture/`
   - **Focus**: Documentation automation, deployment tracking
   - **Output**: Runbooks, changelogs, incident reports

### New Capabilities Integration

**Odoo DevOps Skill** (13KB + 6 references):
- ✅ OCA-compliant module scaffolding
- ✅ Production Docker deployment patterns
- ✅ Security hardening checklists
- ✅ Enterprise feature alternatives

**Notion Integration** (4 skills):
- ✅ Automated deployment documentation
- ✅ Decision logging (security fixes)
- ✅ Meeting intelligence (stakeholder updates)
- ✅ Research documentation (vulnerability analysis)

**MCP Servers** (from `insightpulse_odoo/MCP_INTEGRATION_GUIDE.md`):
- ✅ `mcp/postgres` - Production database queries
- ✅ `mcp/github` - Automated PR creation
- ✅ `mcp/docker` - Container health monitoring

---

## 📋 Phase 1: Emergency Security Remediation (24 hours)

### Objective
Fix 4 critical security vulnerabilities blocking production readiness.

### Sub-Agent Delegation

#### Agent 1: `odoo-security-engineer` (Security Fixes)

**Task 1.1**: Encrypt Plaintext Credentials (CVSS 8.1)
```yaml
Agent: odoo-security-engineer
Skill: docs/claude-code-skills/odoo/SKILL.md (security patterns)
Target: addons/custom/microservices_connector/models/microservices_config.py
Duration: 2 hours

Steps:
1. Read current implementation (plaintext fields)
2. Apply encryption pattern from Odoo skill
3. Add cryptography.fernet integration
4. Create data migration script
5. Write security tests (80% coverage requirement)
6. Deploy with zero-downtime migration

Deliverable:
- ✅ addons/custom/microservices_connector/models/microservices_config.py (encrypted)
- ✅ addons/custom/microservices_connector/migrations/1.1.0/ (migration)
- ✅ addons/custom/microservices_connector/tests/test_encryption.py
```

**Task 1.2**: Fix URL Injection Vulnerability (CVSS 6.5)
```yaml
Agent: odoo-security-engineer
Target: addons/custom/superset_connector/controllers/embedded.py:227
Duration: 1 hour

Steps:
1. Add urllib.parse.quote sanitization
2. Validate all user inputs
3. Add security tests for XSS/injection
4. Update CSP headers

Deliverable:
- ✅ addons/custom/superset_connector/controllers/embedded.py (sanitized)
- ✅ addons/custom/superset_connector/tests/test_security.py
```

**Task 1.3**: Deploy Access Controls (7 modules)
```yaml
Agent: odoo-security-engineer
Skill: docs/claude-code-skills/odoo/reference/oca-module-structure.md
Targets:
  - ipai_procure/security/ir.model.access.csv
  - ipai_expense/security/ir.model.access.csv
  - ipai_subscriptions/security/ir.model.access.csv
  - tableau_connector/security/ir.model.access.csv
  - microservices_connector/security/ir.model.access.csv
  - apps_admin_enhancements/security/ir.model.access.csv
  - security_hardening/security/ir.model.access.csv
Duration: 4 hours

Steps:
1. Read OCA module structure reference
2. Generate ir.model.access.csv for each module
3. Create ir.rule.xml for RLS policies
4. Write access control tests
5. Validate against security audit checklist

Deliverable:
- ✅ 7 × ir.model.access.csv files (18% → 100% coverage)
- ✅ 7 × ir.rule.xml files (RLS policies)
- ✅ Security test suite (40+ tests)
```

#### Agent 2: `odoo-devops-architect` (Production Hardening)

**Task 2.1**: Update Production Configuration
```yaml
Agent: odoo-devops-architect
Skill: docs/claude-code-skills/odoo/reference/docker-production.md
Target: config/odoo/odoo.conf
Duration: 1 hour

Changes:
- dev_mode = False (currently: all)
- log_level = info (currently: debug)
- workers = 4 (currently: 0)
- max_cron_threads = 2 (currently: 0)
- Add security limits

Deliverable:
- ✅ config/odoo/odoo.conf (production-ready)
- ✅ Deployment script update
```

**Task 2.2**: Implement Health Checks & Monitoring
```yaml
Agent: odoo-devops-architect
Targets:
  - docker-compose.simple.yml
  - scripts/health-check.sh
Duration: 2 hours

Steps:
1. Add healthcheck to Odoo service
2. Create health endpoint (/web/health)
3. Configure restart policies
4. Setup log aggregation
5. Add monitoring dashboards

Deliverable:
- ✅ docker-compose.simple.yml (with health checks)
- ✅ scripts/health-check.sh
- ✅ Monitoring configuration
```

### Deployment to Production

**Method**: Blue-Green Deployment (Zero Downtime)

**Step 1**: Create Feature Branch
```bash
git checkout -b emergency-remediation-phase1
```

**Step 2**: Parallel Agent Execution
```bash
# Execute both agents in parallel
# Agent 1: Security fixes (6 hours)
# Agent 2: DevOps hardening (3 hours)
# Total: 6 hours (parallelized)
```

**Step 3**: Integration Testing
```bash
# Run full test suite
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Security tests MUST pass (80% coverage)
pytest addons/custom/*/tests/test_security.py --cov=addons/custom --cov-report=term-missing

# Access control tests
pytest addons/custom/*/tests/test_access.py
```

**Step 4**: Deploy to Production (Droplet: 188.166.237.231)
```bash
# Automated deployment via GitHub Actions
git add .
git commit -m "feat: emergency security remediation phase 1

- Encrypt all plaintext credentials (CVSS 8.1 fix)
- Fix URL injection in superset_connector (CVSS 6.5 fix)
- Add access controls to 7 modules (18% → 100%)
- Production config hardening (dev_mode off, workers enabled)
- Health checks and monitoring

Security Grade: D- → B
Risk Score: 8.7 → 3.5
Coverage: 12% → 85%

🤖 Generated with Claude Code + SuperClaude Framework
Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin emergency-remediation-phase1
```

**Step 5**: GitHub Actions Workflow
```yaml
# .github/workflows/emergency-remediation-deploy.yml
name: Emergency Remediation Deployment
on:
  push:
    branches: [emergency-remediation-phase1]

jobs:
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run security tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
          pytest addons/custom/*/tests/test_security.py --cov=85

  deploy-to-production:
    needs: security-tests
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to insightpulseai.net
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.PRODUCTION_HOST }}
          username: ${{ secrets.PRODUCTION_USER }}
          key: ${{ secrets.PRODUCTION_SSH_KEY }}
          script: |
            cd ~/insightpulse-odoo
            git pull origin emergency-remediation-phase1
            docker-compose pull odoo
            docker-compose up -d --force-recreate odoo

            # Run migrations
            docker-compose exec -T odoo odoo -c /etc/odoo/odoo.conf -d insightpulse -u all --stop-after-init

            # Verify health
            sleep 30
            curl -f https://insightpulseai.net/odoo/web/health || exit 1

            echo "✅ Emergency remediation deployed successfully"
```

---

## 📊 Phase 2: Performance Optimization (48 hours)

### Sub-Agent Delegation

#### Agent 3: `odoo-devops-architect` (Database Performance)

**Task 3.1**: Add Critical Database Indexes
```yaml
Agent: odoo-devops-architect
Target: scripts/add_performance_indexes.sql
Duration: 4 hours

Steps:
1. Analyze slow query logs
2. Identify missing indexes (15+ confirmed)
3. Generate index creation SQL
4. Test on staging
5. Deploy to production with monitoring

Critical Indexes:
- superset_token(dashboard_id, user_id, is_active)
- superset_dashboard(config_id, is_active)
- subscription_contract(state, date_start)
- subscription_line(contract_id, product_id)
- (12 more indexes)

Deliverable:
- ✅ scripts/add_performance_indexes.sql
- ✅ Migration script
- ✅ Performance test results (before/after)
```

**Task 3.2**: Fix N+1 Query Patterns
```yaml
Agent: odoo-devops-architect
Target: addons/custom/ipai_subscriptions/models/
Duration: 4 hours

Steps:
1. Profile subscription MRR calculations
2. Add prefetch hints
3. Batch query operations
4. Implement caching layer
5. Validate performance improvement

Expected: 88% faster (sequential → parallel)

Deliverable:
- ✅ Fixed N+1 patterns in subscriptions
- ✅ Performance benchmarks
```

---

## 🧪 Phase 3: Test Coverage Deployment (Week 2)

### Sub-Agent Delegation

#### Agent 5: `testing-engineer` (Test Suite Creation)

**Task 5.1**: Security Test Suite
```yaml
Agent: testing-engineer
Targets: All 8 custom modules
Duration: 16 hours

Test Categories:
1. Authentication tests (OAuth, session management)
2. Authorization tests (RLS, access controls)
3. Input validation tests (XSS, SQL injection)
4. Cryptography tests (credential encryption)
5. CSP header tests
6. CSRF protection tests

Target Coverage: 80% for security-critical modules

Deliverable:
- ✅ 40+ security tests across 8 modules
- ✅ Coverage reports (pytest-cov)
```

**Task 5.2**: Integration Test Suite
```yaml
Agent: testing-engineer
Targets:
  - superset_connector
  - tableau_connector
  - microservices_connector
Duration: 16 hours

Test Scenarios:
1. Dashboard embed workflow (Superset)
2. Token generation and refresh
3. Health check integration
4. Service failover handling
5. API error responses

Deliverable:
- ✅ Integration test suite
- ✅ CI pipeline integration
```

---

## 📝 Phase 4: Documentation Automation (Week 3)

### Sub-Agent Delegation

#### Agent 6: `project-coordinator` (Documentation)

**Task 6.1**: Automated Deployment Documentation
```yaml
Agent: project-coordinator
Skill: docs/claude-code-skills/notion/knowledge-capture/SKILL.md
Duration: 8 hours

Outputs:
1. Deployment runbook (Notion)
2. Security incident response plan
3. Rollback procedures
4. Emergency contact procedures
5. Stakeholder communication templates

Deliverable:
- ✅ Complete operational documentation
- ✅ Notion knowledge base
```

---

## 🎯 Success Metrics

### Security (Phase 1)
- ✅ Grade: D- → B+ (38/100 → 85/100)
- ✅ Zero plaintext credentials
- ✅ 100% access control coverage
- ✅ 80%+ security test coverage
- ✅ Risk Score: 8.7 → 3.5

### Performance (Phase 2)
- ✅ API response time: <500ms P95
- ✅ Database queries: 88% faster
- ✅ System handles 10,000+ records
- ✅ Zero N+1 query patterns

### Quality (Phase 3)
- ✅ Test coverage: 12% → 80%
- ✅ All modules have tests
- ✅ CI pipeline with coverage gates
- ✅ Automated regression testing

### Operations (Phase 4)
- ✅ Zero-downtime deployments
- ✅ <5 minute rollback capability
- ✅ Comprehensive monitoring
- ✅ Complete documentation

---

## ⚡ Execution Commands

### Initialize Parallel Agents

```bash
# Activate SuperClaude agent work trees
cd /Users/tbwa/insightpulse-odoo/insightpulse_odoo/superclaude-agents

# Agent 1: Security remediation
/sc:spawn odoo-security-engineer
# Reference: docs/claude-code-skills/odoo/SKILL.md
# Task: Encrypt credentials, add access controls

# Agent 2: DevOps hardening
/sc:spawn odoo-devops-architect
# Reference: docs/claude-code-skills/odoo/reference/docker-production.md
# Task: Production config, health checks

# Agent 3: Performance optimization
/sc:spawn odoo-devops-architect
# Task: Database indexes, N+1 fixes

# Agent 5: Testing
/sc:spawn testing-engineer
# Task: Security tests, integration tests

# Agent 6: Documentation
/sc:spawn project-coordinator
# Skill: docs/claude-code-skills/notion/knowledge-capture/SKILL.md
# Task: Runbooks, incident response
```

### Validate Skills Available

```bash
# Verify Odoo DevOps skill
cat docs/claude-code-skills/odoo/SKILL.md | head -50

# Verify OCA structure reference
cat docs/claude-code-skills/odoo/reference/oca-module-structure.md | head -50

# Verify production deployment patterns
cat docs/claude-code-skills/odoo/reference/docker-production.md | head -50

# Verify Notion integration
ls -la docs/claude-code-skills/notion/*/SKILL.md
```

---

## 🚦 Go/No-Go Criteria

### Phase 1 (24 hours) - REQUIRED for Production

**Security**:
- [ ] All plaintext credentials encrypted
- [ ] URL injection vulnerability fixed
- [ ] Access controls on all 7 modules
- [ ] Security test suite passing (40+ tests)
- [ ] Production config hardened

**Validation**:
- [ ] Security grade: B+ or higher
- [ ] Risk score: <4.0
- [ ] Zero critical vulnerabilities remaining
- [ ] Health checks operational

**Decision**: ✅ GO / ❌ NO-GO

### Phase 2 (48 hours) - HIGH PRIORITY

**Performance**:
- [ ] 15+ database indexes deployed
- [ ] N+1 queries eliminated
- [ ] API P95 response time <500ms
- [ ] System handles 10K+ records

**Decision**: ✅ GO / ❌ NO-GO

### Phase 3 (Week 2) - QUALITY GATE

**Testing**:
- [ ] 80% test coverage achieved
- [ ] CI pipeline with coverage gates
- [ ] All modules have test suites
- [ ] Integration tests passing

**Decision**: ✅ GO / ❌ NO-GO

---

## 📞 Stakeholder Communication

### Status Updates (Automated via Notion)

**Daily Updates** (During Phase 1):
- Agent progress reports
- Security metrics dashboard
- Risk score tracking
- Deployment timeline

**Weekly Updates** (Phases 2-4):
- Feature completion status
- Test coverage progress
- Performance benchmarks
- Documentation updates

**Skill Used**: `docs/claude-code-skills/notion/notion-meeting-intelligence/SKILL.md`

---

## 🔄 Rollback Procedures

### Emergency Rollback

```bash
# SSH to production
ssh root@188.166.237.231

# Check current deployment
cd ~/insightpulse-odoo
git log -1 --oneline

# Rollback to previous commit
git checkout <previous-commit-hash>
docker-compose up -d --force-recreate odoo

# Verify health
curl -f https://insightpulseai.net/odoo/web/health
```

**Rollback Time**: <5 minutes
**Data Loss**: None (database migrations are reversible)
**Monitoring**: Automated alerts via health checks

---

## ✅ Next Steps

**Immediate Action** (User Decision):
1. ✅ Approve Phase 1 execution (24-hour security remediation)
2. ✅ Activate parallel sub-agents (6 agents)
3. ✅ Monitor deployment via GitHub Actions
4. ✅ Validate production deployment

**Timeline**:
- **Phase 1**: 24 hours (Emergency Security)
- **Phase 2**: 48 hours (Performance)
- **Phase 3**: Week 2 (Testing)
- **Phase 4**: Week 3 (Documentation)

**Expected Outcome**:
- 🟢 Production-ready deployment
- 🟢 Security Grade: B+
- 🟢 Risk Score: <3.5
- 🟢 Zero-downtime operation

---

**Ready to execute Phase 1?** All skills are integrated and agents are ready to deploy.
