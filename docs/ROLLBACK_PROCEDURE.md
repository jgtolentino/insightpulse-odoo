# Multi-Agent Orchestrator Rollback Procedure

## Overview

This document provides step-by-step procedures for rolling back the multi-agent orchestrator deployment if issues are detected.

**Recovery Time Objective (RTO)**: <5 minutes for emergency rollback, <1 hour for graceful rollback

**Recovery Point Objective (RPO)**: Zero data loss (no state stored in specialist services)

## Rollback Scenarios

### Scenario 1: Emergency Rollback (Critical Failures)

**Triggers**:
- Orchestrator completely unavailable (>5 minutes downtime)
- Error rate >10%
- Response time P95 >10 seconds
- Critical security vulnerability detected

**Procedure** (<5 minutes):

```bash
# Step 1: Revert DNS immediately
./scripts/setup-dns.sh wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run

# Step 2: Verify DNS propagation (may use cached DNS, wait 1-2 minutes)
dig agent.insightpulseai.net

# Step 3: Test old orchestrator is serving traffic
curl https://agent.insightpulseai.net/health

# Expected output:
# {
#   "status": "ok",
#   "agent": "orchestrator",
#   "version": "2.0.0"  # Old version
# }

# Step 4: Pause specialist services (don't delete - keep for debugging)
doctl apps list --format ID,Spec.Name | grep odoo-developer-agent | awk '{print $1}' | xargs -I {} doctl apps update {} --pause
doctl apps list --format ID,Spec.Name | grep finance-ssc-expert | awk '{print $1}' | xargs -I {} doctl apps update {} --pause
doctl apps list --format ID,Spec.Name | grep bi-architect | awk '{print $1}' | xargs -I {} doctl apps update {} --pause
doctl apps list --format ID,Spec.Name | grep devops-engineer | awk '{print $1}' | xargs -I {} doctl apps update {} --pause

# Step 5: Verify services paused
doctl apps list --format Spec.Name,ActiveDeployment.Phase

# Step 6: Document rollback reason
echo "$(date): Emergency rollback triggered - Reason: <YOUR_REASON>" >> docs/rollback_log.md
```

**Post-Rollback Actions**:
1. Notify team via Slack/email
2. Investigate root cause
3. Fix issues in staging environment
4. Test thoroughly before re-deployment
5. Document lessons learned

---

### Scenario 2: Graceful Rollback (Quality Gate Failures)

**Triggers**:
- Error rate 1-10% (sustained >1 hour)
- Response time P95 3-10 seconds
- Cost per query >$0.10 USD
- Routing accuracy <95%
- User feedback indicates poor quality

**Procedure** (<1 hour):

```bash
# Phase 1: Reduce traffic gradually (simulate canary in reverse)

# Week 4 → Week 3 (100% → 50%)
# Manual: Ask 50% of users to use old URL temporarily
echo "Reducing multi-agent usage to 50% of users"

# Monitor for 24 hours
# - Error rates
# - Response times
# - User feedback

# Week 3 → Week 2 (50% → 25%)
echo "Reducing multi-agent usage to 25% of users"

# Monitor for 24 hours

# Week 2 → Week 1 (25% → 0%)
echo "Reverting all users to old orchestrator"

# Phase 2: DNS cutover
./scripts/setup-dns.sh wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run

# Phase 3: Pause specialist services
doctl apps list --format ID,Spec.Name | grep -E "odoo-developer|finance-ssc|bi-architect|devops-engineer" | \
  awk '{print $1}' | \
  xargs -I {} doctl apps update {} --pause

# Phase 4: Document rollback
cat <<EOF >> docs/rollback_log.md
---
Date: $(date)
Type: Graceful Rollback
Reason: Quality gate failure
Metrics:
  - Error rate: <PERCENTAGE>
  - Response time P95: <SECONDS>
  - Cost per query: <USD>
  - Routing accuracy: <PERCENTAGE>
Actions Taken:
  - Reverted DNS
  - Paused specialist services
  - Notified team
---
EOF
```

---

### Scenario 3: Partial Rollback (Single Specialist Failure)

**Triggers**:
- One specialist service consistently failing (error rate >5%)
- One specialist service slow (response time >5s)
- Knowledge base issues for specific agent

**Procedure**:

```bash
# Example: finance_ssc_expert specialist failing

# Step 1: Identify failing specialist
FAILING_AGENT="finance-ssc-expert"
APP_ID=$(doctl apps list --format ID,Spec.Name | grep "$FAILING_AGENT" | awk '{print $1}')

# Step 2: Pause failing specialist
doctl apps update "$APP_ID" --pause

# Step 3: Update orchestrator to fallback to native capabilities
# (Via DO AI Agent Platform UI):
# - Comment out route_to_finance_ssc_expert tool temporarily
# - Or add fallback logic in system prompt

# Step 4: Verify orchestrator handles queries without specialist
curl -X POST https://agent.insightpulseai.net/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Generate BIR Form 1601-C for January 2025",
    "conversation_id": "fallback_test"
  }'

# Expected: Orchestrator handles with native BIR compliance tools

# Step 5: Debug and fix failing specialist
doctl apps logs "$APP_ID" --follow

# Step 6: Redeploy fixed specialist
./scripts/deploy-specialist.sh "$FAILING_AGENT"

# Step 7: Re-enable routing tool in orchestrator
```

---

### Scenario 4: Knowledge Base Rollback

**Triggers**:
- Low quality embeddings (retrieval accuracy <90%)
- Incorrect documents indexed
- Embedding model change required

**Procedure**:

```bash
# Step 1: Backup current embeddings
psql "$POSTGRES_URL" -c "
CREATE TABLE scout.agent_domain_embeddings_backup AS
SELECT * FROM scout.agent_domain_embeddings;
"

# Step 2: Delete problematic embeddings
# Option A: Delete specific agent's embeddings
psql "$POSTGRES_URL" -c "
DELETE FROM scout.agent_domain_embeddings
WHERE agent_domain = 'odoo_developer';
"

# Option B: Delete all embeddings (full reset)
psql "$POSTGRES_URL" -c "
TRUNCATE TABLE scout.agent_domain_embeddings;
"

# Step 3: Verify deletion
psql "$POSTGRES_URL" -c "SELECT * FROM scout.agent_knowledge_stats;"

# Step 4: Re-index with correct documents/model
./scripts/index_agent_knowledge.py \
  --source knowledge/odoo/ \
  --agent odoo_developer \
  --content-type oca_guideline \
  --embedding-model text-embedding-3-small

# Step 5: Verify new embeddings
psql "$POSTGRES_URL" -c "SELECT * FROM scout.agent_knowledge_stats;"

# Step 6: Test retrieval quality
python -c "
from supabase import create_client
import openai
import os

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
openai.api_key = os.getenv('OPENAI_API_KEY')

# Generate test query embedding
response = openai.embeddings.create(
    model='text-embedding-3-small',
    input='OCA module structure guidelines'
)
query_embedding = response.data[0].embedding

# Search knowledge base
result = supabase.rpc('search_agent_knowledge', {
    'p_agent_domain': 'odoo_developer',
    'p_query_embedding': query_embedding,
    'p_match_threshold': 0.7,
    'p_match_count': 5
}).execute()

print(f'Found {len(result.data)} results')
for doc in result.data:
    print(f'  - {doc[\"title\"]} (similarity: {doc[\"similarity\"]:.2f})')
"

# If retrieval quality still poor, restore backup:
psql "$POSTGRES_URL" -c "
TRUNCATE TABLE scout.agent_domain_embeddings;
INSERT INTO scout.agent_domain_embeddings
SELECT * FROM scout.agent_domain_embeddings_backup;
"
```

---

## Rollback Decision Matrix

| Issue | Severity | Rollback Type | Timeline | Approval Required |
|-------|----------|---------------|----------|-------------------|
| Orchestrator unavailable >5min | CRITICAL | Emergency | <5min | No (auto-execute) |
| Error rate >10% | CRITICAL | Emergency | <5min | No |
| Security vulnerability | CRITICAL | Emergency | <5min | No |
| Error rate 5-10% | HIGH | Graceful | <1 hour | Yes (Lead Engineer) |
| Response time P95 >5s | HIGH | Graceful | <1 hour | Yes |
| Cost per query >$0.20 | HIGH | Graceful | <1 hour | Yes |
| Error rate 1-5% | MEDIUM | Monitor 24h → Graceful if persists | 1-2 days | Yes |
| Single specialist failing | MEDIUM | Partial | <30min | No |
| Low routing accuracy (90-95%) | LOW | Monitor 7d → Optimize | 1 week | Yes |
| Knowledge base quality <90% | LOW | Knowledge Base | <2 hours | No |

---

## Post-Rollback Validation

After any rollback, verify:

```bash
# 1. Orchestrator health
curl https://agent.insightpulseai.net/health

# 2. No specialist services running (if full rollback)
doctl apps list --format Spec.Name,ActiveDeployment.Phase | grep -E "odoo-developer|finance-ssc|bi-architect|devops-engineer"
# Expected: All show "PAUSED" or "SUPERSEDED"

# 3. DNS pointing to correct URL
dig agent.insightpulseai.net
# Expected: CNAME to wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run

# 4. Old orchestrator serving traffic
curl -X POST https://agent.insightpulseai.net/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is your version?", "conversation_id": "rollback_test"}'
# Expected: Response from old orchestrator (version 2.0.0)

# 5. No errors in logs
doctl apps logs <ORCHESTRATOR_APP_ID> --type RUN | tail -n 50
```

---

## Root Cause Analysis Template

After rollback, complete this analysis:

```markdown
# Rollback Post-Mortem

**Date**: YYYY-MM-DD HH:MM UTC
**Duration**: X hours/minutes
**Triggered By**: [Auto / Manual]
**Rollback Type**: [Emergency / Graceful / Partial / Knowledge Base]

## Timeline

- HH:MM - Issue first detected
- HH:MM - Rollback decision made
- HH:MM - Rollback initiated
- HH:MM - Rollback completed
- HH:MM - Service restored

## Root Cause

[Detailed description of what went wrong]

## Impact

- Users affected: X
- Error rate: Y%
- Response time: Z seconds
- Revenue impact: $N
- Reputation impact: [High / Medium / Low]

## What Went Well

- [List things that worked well during rollback]

## What Didn't Go Well

- [List issues encountered during rollback]

## Action Items

- [ ] Fix root cause (Owner: NAME, Due: DATE)
- [ ] Update monitoring to detect earlier (Owner: NAME, Due: DATE)
- [ ] Improve rollback automation (Owner: NAME, Due: DATE)
- [ ] Update documentation (Owner: NAME, Due: DATE)

## Prevention

- [Steps to prevent similar issues in future]

## Re-Deployment Plan

- [ ] Root cause fixed in staging
- [ ] Additional tests added
- [ ] Monitoring improved
- [ ] Gradual rollout plan updated
- [ ] Rollback procedure tested
- [ ] Approval obtained for re-deployment
```

---

## Lessons Learned Database

Track all rollbacks in `docs/rollback_log.md`:

```markdown
# Rollback History

## 2025-11-16: Emergency Rollback - Orchestrator Timeout

**Reason**: Specialist services timeout after 30s
**Impact**: Error rate 15%, P95 response time 35s
**Resolution**: Increased specialist timeout to 60s
**Prevention**: Load testing before deployment
**Re-deployed**: 2025-11-18 (successful)

---

## 2025-11-20: Partial Rollback - finance_ssc_expert Memory Leak

**Reason**: Memory leak in BIR form generation
**Impact**: 1 specialist service crashed every 2 hours
**Resolution**: Fixed memory leak in PDF generation
**Prevention**: Memory profiling in staging
**Re-deployed**: 2025-11-21 (successful)

---
```

---

## Emergency Contacts

**Escalation Path**:
1. On-call Engineer (rollback execution)
2. Lead Engineer (rollback approval for HIGH severity)
3. Engineering Manager (post-mortem review)
4. CTO (communication for CRITICAL severity)

**Notification Channels**:
- Slack: #engineering-alerts
- Email: engineering@insightpulseai.net
- SMS: On-call engineer (CRITICAL only)

---

## Rollback Testing

**Test rollback procedure quarterly**:
```bash
# Schedule: Every 3 months on staging environment

# 1. Deploy multi-agent orchestrator to staging
# 2. Simulate failure (intentionally break specialist service)
# 3. Execute emergency rollback procedure
# 4. Measure RTO (should be <5 minutes)
# 5. Document any issues with rollback process
# 6. Update rollback procedure as needed
```
