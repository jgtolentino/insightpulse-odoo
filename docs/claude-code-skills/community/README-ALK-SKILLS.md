# ALK (AI Learning & Knowledge) Skills

This directory contains skills extracted from an AI/ML and DevOps upskilling conversation focused on building AI agent capabilities for automation, infrastructure, and CI/CD operations.

## Overview

These skills represent a comprehensive framework for transforming traditional DevOps/IaC teams into AI Agent Engineers, with practical skills for multi-agent systems, infrastructure automation, and CI/CD optimization.

## Skills Included

### 1. Infrastructure as Code (IaC) Multi-Agent System

A complete three-agent system for safe, audited infrastructure deployment:

#### `iac-planner`
**Purpose**: Takes user infrastructure requests and generates Terraform plans

**Key Features**:
- Clarifies vague infrastructure requests with intelligent questioning
- Generates production-quality Terraform HCL code
- Runs `terraform plan` and presents summary for approval
- **Never executes** - only plans and presents

**Use Case**: "I need a new production web server"
- Agent asks clarifying questions (region, size, ports, tags)
- Generates complete Terraform configuration
- Runs plan and presents for security audit

#### `iac-security-auditor`
**Purpose**: Audits Terraform plans for security vulnerabilities and compliance

**Key Features**:
- Runs automated security scanning (tfsec, checkov)
- Enforces compliance policies (tagging, encryption, networking)
- Generates detailed audit reports with severity levels
- Returns APPROVED or REJECTED verdict

**Security Checks**:
- No public security group rules on sensitive ports
- S3 buckets have block public access enabled
- Required tags present (owner, cost-center, environment)
- Encryption at rest for all data stores
- IAM principle of least privilege
- Approved regions only

**Output Format**:
```
AUDIT_RESULT: APPROVED
```
or
```
AUDIT_RESULT: REJECTED
[Detailed findings with remediation steps]
```

#### `iac-executor`
**Purpose**: Safely executes approved Terraform plans

**Key Features**:
- **Dual approval required**: Security audit + human confirmation
- Streams real-time apply output
- Runs post-deployment smoke tests
- Comprehensive error handling and rollback procedures

**Safety Mechanisms**:
- Pre-execution checklist (workspace, credentials, state backend)
- Real-time monitoring during apply
- Automatic smoke tests (HTTP checks, database connectivity, load balancer health)
- Detailed status reporting

**Example Workflow**:
```
User Request → Planner → Security Auditor → User Approval → Executor → Smoke Tests → Report
```

### 2. CI/CD Audit & Optimization

#### `cicd-audit-optimizer`
**Purpose**: Comprehensive audit framework for CI/CD pipelines and automation

**Four-Phase Process**:

**Phase 1: Full Inventory**
- Catalog all CI/CD pipelines across repositories
- Document tools, triggers, artifacts, and dependencies
- Create complete automation inventory

**Phase 2: Operational Health Check**
- Assess success/failure rates (last 30 days)
- Identify monitoring gaps
- Categorize pipelines (healthy, at-risk, failing, disabled)

**Phase 3: Gap Analysis**
- Identify manual processes that should be automated
- Find pipeline bottlenecks
- Discover missing automations (security scanning, testing, observability)

**Phase 4: Error Cataloging & Root Cause Analysis**
- Structured failure logging
- Root cause analysis framework (5 Whys, Fishbone)
- Categorization: Skills, Infrastructure, Tools, or Process

**Deliverables**:
- Executive summary with health scores
- Complete pipeline inventory
- Prioritized recommendations (Impact × Urgency / Complexity)
- DORA metrics baseline (Deployment Frequency, Lead Time, Change Failure Rate, MTTR)

**Root Cause Framework**:
```
Step 1: Can you reproduce? → Intermittent (Infra) vs Consistent (Skill/Tools)
Step 2: Works manually? → Yes (Skill/Infra) vs No (Tools)
Step 3: Infrastructure error? → Yes (Infra) vs No (Skill)
```

**Categories**:
- **Skills & Capabilities**: Vague instructions, poor error handling, wrong parameters
- **Infrastructure**: OOM, network timeouts, permissions, resource limits
- **Tools & Technology**: Tool bugs, flaky tests, dependency conflicts, API downtime
- **Process & People**: Manual drift, bad merges, outdated docs

### 3. AI Agent Engineer Upskilling

#### `ai-agent-upskilling`
**Purpose**: L&D framework for upskilling DevOps teams to become AI Agent Engineers

**Strategic Goal**: Transform teams from traditional automation (rule-based, deterministic) to agentic automation (goal-oriented, autonomous, reasoning-driven)

**Four-Phase Curriculum**:

**Phase 1: Foundation - AI Literacy** (Weeks 1-2)
- LLMs as a new "runtime" (probabilistic, non-deterministic)
- Prompt engineering (the new command line)
- RAG (Retrieval-Augmented Generation) concepts
- Vector databases (semantic search vs exact match)
- **Milestone**: Working documentation chatbot with RAG

**Phase 2: Agent Frameworks** (Weeks 3-4)
- LangChain (chains, agents, memory)
- LlamaIndex (advanced RAG)
- Function calling / tool use
- Integrating existing APIs as LLM tools
- **Milestone**: Chatbot can execute read-only operations

**Phase 3: Multi-Agent Systems** (Weeks 5-6)
- CrewAI and AutoGen frameworks
- Building specialized agent teams
- Agent roles, backstories, and tools
- Integrating with existing "Agent Studio"
- **Milestone**: Full DevOps Crew (planner → auditor → executor)

**Phase 4: LLMOps - Production Readiness** (Weeks 7-8)
- Evaluation frameworks (DeepEval, Ragas)
- CI/CD for AI agents
- Monitoring and observability (OpenTelemetry)
- Security (prompt injection prevention, guardrails)
- Model serving with IaC (Terraform for LLM infrastructure)
- **Milestone**: Production-ready agent with full monitoring

**Competitive Advantage**:
> "While OpenAI and Anthropic build the 'brains' (LLMs), your advantage is building the 'nervous system'—robust, scalable, secure systems that connect AI to real infrastructure."

**Capstone Project**:
Build a complete multi-agent DevOps system that:
1. Takes infrastructure requests
2. Generates Terraform code
3. Runs security scans
4. Executes if approved
5. Performs smoke tests
6. Includes full observability

**Assessment Criteria**:
- [ ] Handles 10+ infrastructure request types
- [ ] 95%+ evaluation score on test suite
- [ ] Passes security audit (no prompt injection)
- [ ] Full monitoring dashboard
- [ ] Team wiki documentation
- [ ] Peer review approved

## Integration Patterns

### Using the IaC Multi-Agent System

```python
from crewai import Agent, Task, Crew

# Initialize agents with the three skills
planner = Agent(
    role='IaC Planner',
    goal='Generate infrastructure plans from user requests',
    skill='iac-planner',
    tools=[terraform_plan]
)

auditor = Agent(
    role='Security Auditor',
    goal='Audit plans for security and compliance',
    skill='iac-security-auditor',
    tools=[run_tfsec, check_compliance]
)

executor = Agent(
    role='Safe Executor',
    goal='Execute approved plans safely',
    skill='iac-executor',
    tools=[terraform_apply, smoke_test]
)

# Create workflow
deploy_crew = Crew(
    agents=[planner, auditor, executor],
    tasks=[plan_task, audit_task, execute_task],
    process='sequential'  # Each step must complete before next
)

# Execute
result = deploy_crew.kickoff(inputs={
    "request": "Deploy a production web server in us-east-1"
})
```

### Using CI/CD Audit Skill

```bash
# Invoke the cicd-audit-optimizer skill
claude --skill cicd-audit-optimizer

# Or programmatically
from claude_code import invoke_skill

audit_result = invoke_skill(
    skill_name='cicd-audit-optimizer',
    parameters={
        'scope': 'all-repositories',
        'timeframe': 'last-30-days',
        'include_recommendations': True
    }
)

print(audit_result['executive_summary'])
print(audit_result['prioritized_recommendations'])
```

### Using Upskilling Framework

```python
# Create personalized learning path
from skills import ai_agent_upskilling

learning_plan = ai_agent_upskilling.create_learning_path(
    team_profile={
        'current_skills': ['Terraform', 'Ansible', 'Jenkins', 'Docker'],
        'team_size': 8,
        'experience_level': 'Senior DevOps',
        'time_commitment': '10 hours/week'
    }
)

# Track progress
learning_plan.track_milestone('Phase 1: Foundation', completed=True)
learning_plan.next_assignment()  # Returns Phase 2 first task
```

## Key Concepts from the Source Material

### M&E Equivalent in DevOps

The conversation identified that traditional M&E (Monitoring and Evaluation) evolves into:

**Monitoring → Observability**
- Logs (event records)
- Metrics (time-series data)
- Traces (request journey)

**Evaluation → DORA Metrics**
- **Deployment Frequency**: How often do you deploy?
- **Lead Time for Changes**: Commit to production time
- **Change Failure Rate**: % of deployments requiring hotfix/rollback
- **Mean Time to Recovery (MTTR)**: Time to restore service after failure

**Elite Team Benchmarks**:
- Deploy multiple times per day
- Lead time < 1 day
- Change failure rate 0-15%
- MTTR < 1 hour

### Agent vs. Traditional Automation

**Traditional Automation**:
- Pre-defined workflows
- Deterministic (always same result for same input)
- Rule-based decision making
- Requires exact specifications

**Agentic Automation**:
- Goal-oriented (given objective, figures out steps)
- Probabilistic (reasons about best approach)
- Adaptive decision making
- Works with high-level requirements

**Example**:
- Traditional: "Run this exact sequence: terraform plan → wait → terraform apply"
- Agentic: "Deploy a secure web server" → Agent determines: region, size, security groups, monitoring, tags, runs plan, audits, executes

## File Structure

```
docs/claude-code-skills/community/
├── iac-planner/
│   └── SKILL.md
├── iac-security-auditor/
│   └── SKILL.md
├── iac-executor/
│   └── SKILL.md
├── cicd-audit-optimizer/
│   └── SKILL.md
├── ai-agent-upskilling/
│   └── SKILL.md
└── README-ALK-SKILLS.md (this file)
```

## Installation

These skills are already linked in `.claude/skills/` via symlinks:

```bash
ls -la .claude/skills/ | grep -E "(iac-|cicd-|ai-agent)"
```

To use in Claude Code:
```bash
claude --skill iac-planner
claude --skill iac-security-auditor
claude --skill iac-executor
claude --skill cicd-audit-optimizer
claude --skill ai-agent-upskilling
```

## Real-World Use Cases

### Use Case 1: Safe Infrastructure Deployment
**Scenario**: Developer needs to deploy new RDS database for production

**Flow**:
1. Developer: "I need a PostgreSQL database for production"
2. `iac-planner`: Asks questions (size? backup retention? multi-AZ?)
3. `iac-planner`: Generates Terraform, runs plan
4. `iac-security-auditor`: Scans plan, checks:
   - Encryption at rest enabled?
   - Not publicly accessible?
   - Backup configured?
   - Tags present?
5. `iac-security-auditor`: Returns APPROVED
6. Developer: "Execute"
7. `iac-executor`: Verifies approvals, runs apply, tests connection
8. `iac-executor`: Reports success + connection string

**Value**: Zero manual Terraform, zero security misconfigurations, full audit trail

### Use Case 2: CI/CD Performance Optimization
**Scenario**: Build times increasing, deployment reliability decreasing

**Flow**:
1. Team lead: Invoke `cicd-audit-optimizer`
2. Phase 1: Discovers 47 workflows across 12 repositories
3. Phase 2: Finds:
   - 3 workflows failing >50% of time
   - 8 workflows with no monitoring
   - Average build time increased 200% in 30 days
4. Phase 3: Identifies gaps:
   - No dependency caching (quick win)
   - Sequential jobs that could be parallel (medium)
   - Integration tests timing out (investigate)
5. Phase 4: Root cause analysis:
   - Bottleneck: npm install taking 8 minutes (was 2 minutes)
   - RCA: package-lock.json was deleted, versions drifting
   - Fix: Restore lock file, enable caching
6. Deliverable: Prioritized list of 15 recommendations with ROI

**Value**: Data-driven optimization, identified root causes, clear action plan

### Use Case 3: Team Upskilling to AI Agents
**Scenario**: DevOps team of 8 needs to adopt AI agent automation

**Flow**:
1. L&D manager: Uses `ai-agent-upskilling` skill
2. Week 1-2: Team builds RAG chatbot for internal docs
3. Week 3-4: Team adds function calling to chatbot (can query monitoring)
4. Week 5-6: Team builds 3-agent system (plan → audit → execute)
5. Week 7-8: Team adds evaluation suite, monitoring, CI/CD
6. Capstone: Team demonstrates full IaC agent system
7. Certification: Peer review + production deployment

**Value**: Systematic skill transformation, practical deliverables, production-ready AI agents

## Contributing

These skills were extracted from a comprehensive conversation about AI/ML upskilling for DevOps teams. To contribute:

1. Add new skills in `docs/claude-code-skills/community/[skill-name]/SKILL.md`
2. Create symlink in `.claude/skills/`
3. Document in this README
4. Test with Claude Code
5. Submit PR

## References

- Source: Gemini conversation on AI Agent upskilling for DevOps
- Frameworks: CrewAI, LangChain, LlamaIndex
- Tools: Terraform, tfsec, checkov, GitHub Actions
- Concepts: DORA metrics, RAG, Multi-agent systems, LLMOps

## License

These skills are part of the InsightPulse AI ecosystem and follow the same license as the parent repository.

---

**Last Updated**: 2025-11-09
**Skills Version**: 1.0.0
**Extracted By**: Claude Code with ALK extraction prompt
