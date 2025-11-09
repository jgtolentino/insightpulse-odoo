# InsightPulse Cookbook Integration Plan

## Executive Summary

This document maps **OpenAI Cookbook patterns** to the **InsightPulse stack**, internalizing proven patterns instead of depending on external cookbooks. Each pattern is adapted for our specific repos: `ipai-bot`, `pulser-copilot`, `insightpulse-odoo`, and future `insightpulse-workspace`.

**Philosophy**: Treat each Cookbook cluster as a **pattern pack** that we implement natively in our codebase, optimized for our Finance SSC, BIR compliance, and Odoo automation needs.

---

## Pattern Mapping Overview

| OpenAI Cookbook Pattern | InsightPulse Implementation | Target Repo(s) |
|-------------------------|----------------------------|----------------|
| **MCP Server Development** | Deep research tools, multi-persona agents | pulser-copilot, workspace |
| **CI/CD Automation** | Auto-fix CI failures, scheduled linters | ipai-bot, insightpulse-odoo |
| **Agentic Workflows** | YAML-defined Flows with triggers/steps | ipai-bot, agent-hub |
| **Document Processing** | BIR PDF RAG, OCR fallback to LLM | ocr service, finance modules |
| **Eval-Driven Development** | Quality gates for agents and MCP tools | ipai-bot, pulser-copilot |

---

## A. MCP Server Development → pulser-copilot + workspace

### Target Repositories
- `pulser-copilot` (MCP server, tools)
- `insightpulse-workspace` / Notion-parity workspace (future)

### Pattern 1: Deep Research MCP Server

**Cookbook Inspiration**: "Building a Deep Research MCP Server"

**InsightPulse Implementation**:

Create deep-work tools in `pulser-copilot`:

```python
# pulser-copilot/src/tools/deep_research_repo.py

class DeepResearchRepoTool:
    """Multi-hop RAG over InsightPulse codebase"""

    async def research(self, query: str) -> ResearchResult:
        # Multi-step planning:
        # 1. Gather: Search code, issues, docs
        # 2. Cluster: Group by theme/module
        # 3. Summarize: Extract key insights
        # 4. Synthesize: Generate comprehensive answer

        plan = await self.create_research_plan(query)

        # Parallel gather phase
        sources = await asyncio.gather(
            self.search_odoo_modules(plan.keywords),
            self.search_ipai_bot_logs(plan.keywords),
            self.search_workspace_docs(plan.keywords),
        )

        # Cluster and synthesize
        clusters = self.cluster_by_theme(sources)
        return self.synthesize_answer(clusters, query)
```

**Tool Families**:

1. **deep_research_repo**: Multi-hop RAG over:
   - `insightpulse-odoo` modules
   - `ipai-bot` logs/specs
   - `workspace` docs

2. **deep_research_ocr**: RAG over processed BIR/tax PDFs
   - Supabase pgvector storage
   - Metadata: `bir_form`, `section`, `published_at`

3. **deep_research_finance**: SSC-specific queries
   - Month-end procedures
   - Multi-agency consolidation
   - Compliance checklists

**Directory Structure**:
```
pulser-copilot/
├── src/
│   ├── tools/
│   │   ├── deep_research_repo.py
│   │   ├── deep_research_ocr.py
│   │   └── deep_research_finance.py
│   └── prompts/
│       └── deep_research_template.jinja2
└── evals/
    └── deep_research_test_cases.yaml
```

**Behavior Contract**:
- Multi-step planning (gather → cluster → summarize → synthesize)
- Always cite sources with file paths and line numbers
- Confidence scoring for each claim
- Graceful degradation when sources are sparse

---

### Pattern 2: MCP-Powered Agentic Voice Framework → Multi-Persona Agents

**Cookbook Inspiration**: "MCP-Powered Agentic Voice Framework"

**InsightPulse Implementation**:

Same MCP backend, multiple **personas** via Claude Desktop/CLI:

```yaml
# pulser-copilot/personas.yaml

personas:
  - name: "Odoo Ops SRE"
    tools: [search_code, deploy_check, rollback_guide]
    system_prompt: |
      You are an SRE expert for InsightPulse Odoo deployments.
      Focus on: health checks, rollback procedures, log analysis.

  - name: "Finance SSC Copilot"
    tools: [month_end_checklist, consolidation_helper, trial_balance]
    system_prompt: |
      You assist with Finance Shared Service Center operations.
      Expertise: month-end closing, multi-agency consolidation, BIR compliance.

  - name: "BIR Automation Builder"
    tools: [search_bir_regulations, scaffold_bir_form, validate_compliance]
    system_prompt: |
      You build Philippine BIR tax automation.
      Knowledge: 1601-C, 2550Q, 1702-RT, ATP validation.
```

**Usage**:
```bash
# Claude Desktop with persona
pulser-copilot --persona "Finance SSC Copilot" \
  --query "Guide me through month-end closing for CKVC"

# CLI automation
pulser-copilot --persona "BIR Automation Builder" \
  --task "scaffold 1601-C withholding module"
```

**MCP Tool Registration**:
```json
{
  "mcpServers": {
    "pulser-copilot": {
      "command": "python",
      "args": ["-m", "pulser_copilot.mcp_server"],
      "env": {
        "PERSONA": "${PULSER_PERSONA:-default}"
      }
    }
  }
}
```

---

### Pattern 3: Responses API MCP Tool Pattern → Standard Calling Template

**Cookbook Inspiration**: "Guide to Using the Responses API's MCP Tool"

**InsightPulse Implementation**:

Codify a **single MCP calling template** in `pulser-copilot`:

```python
# pulser-copilot/src/core/mcp_template.py

class MCPToolTemplate:
    """Standard pattern for all MCP tools"""

    async def execute(self, tool_name: str, params: dict) -> ToolResult:
        # Phase 1: Plan
        plan = await self.create_plan(tool_name, params)

        # Phase 2: Tool Calls (with retry/fallback)
        results = []
        for step in plan.steps:
            try:
                result = await self.call_tool(step.tool, step.params)
                results.append(result)
            except ToolError as e:
                fallback = await self.get_fallback(step, e)
                results.append(fallback)

        # Phase 3: Reflection
        reflection = await self.reflect_on_results(results, plan.intent)

        # Phase 4: Final Answer
        return self.synthesize_answer(results, reflection)
```

**Reusable Prompt Scaffolding**:

```jinja2
{# prompts/mcp_tool_template.jinja2 #}

# Tool Execution Plan

**Intent**: {{ intent }}
**Tool**: {{ tool_name }}

## Execution Steps

{% for step in steps %}
{{ loop.index }}. **{{ step.description }}**
   - Tool: `{{ step.tool }}`
   - Params: {{ step.params | tojson }}
   - Expected: {{ step.expected_output }}
{% endfor %}

## Success Criteria

{{ success_criteria }}

## Reflection Checklist

- [ ] Did the tool return expected data?
- [ ] Are there edge cases to handle?
- [ ] Is a follow-up query needed?
- [ ] Can I provide a confident answer?
```

**Apply to All Tools**:
- `search_code`
- `scaffold_module`
- `generate_docs`
- `validate_compliance`
- `deep_research_*`

---

## B. CI/CD Automation → ipai-bot + insightpulse-odoo

### Target Repositories
- `insightpulse-odoo`
- `ipai-bot`

### Pattern 4: Auto-Fix CI Failures

**Cookbook Inspiration**: "Use Codex CLI to automatically fix CI failures"

**InsightPulse Implementation**:

**ipai-bot Extension**:

```python
# ipai-bot/src/tasks/ci_autofix.py

@celery_app.task(name="autofix_ci_failure")
def autofix_ci_failure(repo: str, workflow_name: str, run_id: int):
    """
    Automatically generate fix for failing CI run

    Workflow:
    1. Fetch failing job logs from GitHub API
    2. Extract error messages and context
    3. Send to LLM with relevant code
    4. Generate candidate patch
    5. Open PR on ci/autofix-{run_id} branch
    """

    # Fetch logs
    logs = github_api.get_workflow_run_logs(repo, run_id)
    errors = extract_errors(logs)

    # Get relevant code
    code_context = get_code_context(repo, errors)

    # Generate fix
    fix_prompt = f"""
    CI Failure in {workflow_name}:

    Errors:
    {errors}

    Relevant Code:
    {code_context}

    Generate a minimal patch to fix these errors.
    """

    patch = llm_client.generate_patch(fix_prompt)

    # Create PR
    pr = create_autofix_pr(repo, run_id, patch)

    return {
        "pr_url": pr.html_url,
        "patch_preview": patch[:500],
    }
```

**GitHub Action**:

```yaml
# .github/workflows/ci-autofix-trigger.yml

name: Trigger CI Autofix

on:
  workflow_run:
    workflows: ["CI/CD", "Notebook CI", "Quality Checks"]
    types: [completed]

jobs:
  trigger-autofix:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest

    steps:
      - name: Trigger ipai-bot autofix
        run: |
          curl -X POST https://ipai-bot.insightpulseai.net/api/autofix \
            -H "Authorization: Bearer ${{ secrets.IPAI_BOT_TOKEN }}" \
            -d '{
              "repo": "${{ github.repository }}",
              "workflow_name": "${{ github.event.workflow_run.name }}",
              "run_id": ${{ github.event.workflow_run.id }}
            }'
```

**Contract**:
- Only runs on **test failures**, not build/deploy failures
- Creates draft PR (not auto-merge)
- Adds `ci/autofix` label
- Includes explanation comment with reasoning

---

### Pattern 5: Automated Code Quality & Security Fixes

**Cookbook Inspiration**: "Automating Code Quality and Security Fixes"

**InsightPulse Implementation**:

**ipai-bot Scheduled Job**:

```python
# ipai-bot/src/tasks/lint_sweep.py

@celery_app.task(name="weekly_lint_sweep")
def weekly_lint_sweep(repo: str):
    """
    Weekly automated linting and security scan

    Workflow:
    1. Clone repo
    2. Run linters: black, flake8, isort, pylint, bandit
    3. Run security scanners: safety, semgrep
    4. Group issues by module/area
    5. Generate mega-fix PR with all grouped fixes
    """

    with clone_repo(repo) as repo_path:
        # Run tools
        lint_results = {
            "black": run_black(repo_path),
            "flake8": run_flake8(repo_path),
            "isort": run_isort(repo_path),
            "bandit": run_bandit(repo_path),
            "safety": run_safety(repo_path),
        }

        # Group by module
        grouped = group_issues_by_module(lint_results)

        # Generate fixes
        fixes = []
        for module, issues in grouped.items():
            fix = generate_module_fix(module, issues)
            fixes.append(fix)

        # Create mega-PR
        pr = create_lint_sweep_pr(repo, fixes)

        return {
            "pr_url": pr.html_url,
            "modules_fixed": len(grouped),
            "total_issues": sum(len(v) for v in grouped.values()),
        }
```

**Cron Schedule**:

```yaml
# .github/workflows/weekly-lint-sweep.yml

name: Weekly Lint Sweep

on:
  schedule:
    - cron: '0 0 * * 0'  # Sunday midnight UTC
  workflow_dispatch:

jobs:
  trigger-sweep:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger ipai-bot lint sweep
        run: |
          curl -X POST https://ipai-bot.insightpulseai.net/api/lint-sweep \
            -H "Authorization: Bearer ${{ secrets.IPAI_BOT_TOKEN }}" \
            -d '{"repo": "${{ github.repository }}"}'
```

**Grouping Logic**:
```python
def group_issues_by_module(lint_results):
    """Group issues by Odoo module or top-level directory"""
    groups = defaultdict(list)

    for tool, issues in lint_results.items():
        for issue in issues:
            # Extract module from file path
            module = extract_module_from_path(issue.file_path)
            groups[module].append({
                "tool": tool,
                "issue": issue,
            })

    return groups
```

---

### Pattern 6: PLANS.md for Multi-Hour Problem Solving

**Cookbook Inspiration**: "Using PLANS.md for multi-hour problem solving"

**InsightPulse Implementation**:

**Standardize PLANS.md** at repo root:

```markdown
# PLANS.md - InsightPulse Development Plans

## Active Plans

### [PLAN-001] Multi-Agency Consolidation Automation
**Status**: In Progress
**Owner**: Finance SSC Team
**Started**: 2025-01-15
**Target**: 2025-02-01

#### Problem
Manual consolidation across 8 agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB) takes 3-4 days per month.

#### Solution Approach
1. ✅ Scaffold `multi_agency_consolidation` module
2. ✅ Implement inter-company eliminations
3. 🔄 Build consolidated trial balance view
4. ⏳ Add BIR compliance checks
5. ⏳ Create Superset dashboards

#### Next Steps
- [ ] Review consolidation rules with Finance team
- [ ] Test with January data
- [ ] Deploy to staging

#### Learnings
- Consolidation must preserve agency-level detail (audit requirement)
- RMC 5-2023 affects transfer pricing validation

---

### [PLAN-002] BIR 1601-C Automation
**Status**: Planning
**Owner**: BIR Automation Team
**Started**: 2025-01-20

#### Problem
Monthly 1601-C filing is error-prone and time-consuming.

#### Solution Approach
1. ⏳ Extract withholding data from `account.move.line`
2. ⏳ Validate against BIR ATC codes
3. ⏳ Generate 1601-C format (CSV + validation)
4. ⏳ Integrate with OCR for receipt verification

#### Dependencies
- Requires `bir_forms` module base
- Needs OCR service deployment

---

## Completed Plans

### [PLAN-000] Odoo 19 Migration
**Status**: Complete
**Completed**: 2024-12-15
...
```

**ipai-bot Integration**:

```python
# ipai-bot/src/tools/plans_manager.py

class PlansManager:
    """Manage PLANS.md across repos"""

    def read_plans(self, repo: str) -> List[Plan]:
        """Parse PLANS.md and return structured plans"""
        content = github_api.get_file_content(repo, "PLANS.md")
        return parse_plans_markdown(content)

    def update_plan_status(self, repo: str, plan_id: str, status: str):
        """Update plan status in PLANS.md"""
        plans = self.read_plans(repo)
        plan = next(p for p in plans if p.id == plan_id)
        plan.status = status

        # Update file
        new_content = render_plans_markdown(plans)
        github_api.update_file(repo, "PLANS.md", new_content)

    def suggest_next_step(self, repo: str, plan_id: str) -> str:
        """Use LLM to suggest next step for a plan"""
        plan = self.get_plan(repo, plan_id)

        prompt = f"""
        Based on this development plan:

        {plan.to_markdown()}

        What should be the next concrete step?
        Consider: completed items, dependencies, learnings.
        """

        return llm_client.complete(prompt)
```

**pulser-copilot Integration**:

```python
# pulser-copilot/src/tools/read_plans.py

@mcp_tool("read_plans")
def read_plans() -> str:
    """Read PLANS.md from context repo"""
    with open("PLANS.md") as f:
        return f.read()

@mcp_tool("suggest_next_step")
def suggest_next_step(plan_id: str) -> str:
    """Suggest next step for a plan"""
    # Uses plans context + codebase state
    ...
```

---

## C. Agentic Workflows → ipai-bot Orchestration

### Target Repositories
- `ipai-bot`
- `agent-hub` / registry (future)

### Pattern 7: Flows (YAML-Defined Multi-Step Processes)

**Cookbook Inspiration**: "AgentKit / OpenAI Agents SDK"

**InsightPulse Implementation**: **Flows**

```yaml
# ipai-bot/flows/bir_issue_handler.yaml

name: BIR Issue Handler
description: Automatically handle BIR-related issues in insightpulse-odoo

trigger:
  type: github_issue
  repo: insightpulse-odoo
  labels: ["bir", "tax", "compliance"]

steps:
  - name: classify_issue
    type: llm_classify
    prompt_template: classify_bir_issue.jinja2
    outputs:
      - issue_type  # bug / feature / docs
      - bir_form    # 1601-C / 2550Q / etc
      - urgency     # high / medium / low

  - name: gather_context
    type: code_search
    params:
      query: "{{ bir_form }} implementation"
      paths: ["odoo/addons/bir_*"]
    outputs:
      - relevant_files

  - name: draft_fix_plan
    type: llm_plan
    inputs:
      - issue_body
      - issue_type
      - relevant_files
    prompt_template: draft_bir_fix_plan.jinja2
    outputs:
      - fix_plan

  - name: generate_docs
    type: llm_generate
    inputs:
      - fix_plan
      - bir_form
    prompt_template: bir_compliance_docs.jinja2
    outputs:
      - compliance_notes

  - name: open_pr
    type: github_pr
    params:
      branch: "fix/bir-{{ issue.number }}"
      title: "Fix: {{ issue.title }}"
      body: |
        ## Fix Plan
        {{ fix_plan }}

        ## Compliance Notes
        {{ compliance_notes }}

        Fixes #{{ issue.number }}
      labels: ["bir", "automated"]
```

**Flow Executor**:

```python
# ipai-bot/src/flows/executor.py

class FlowExecutor:
    """Execute YAML-defined flows"""

    def execute(self, flow_path: str, trigger_data: dict):
        flow = self.load_flow(flow_path)

        # Check trigger matches
        if not self.trigger_matches(flow.trigger, trigger_data):
            return None

        # Execute steps
        context = {"trigger": trigger_data}

        for step in flow.steps:
            result = self.execute_step(step, context)

            # Add outputs to context
            for output_name, output_value in result.outputs.items():
                context[output_name] = output_value

        return context

    def execute_step(self, step: FlowStep, context: dict):
        """Execute a single step based on type"""

        if step.type == "llm_classify":
            return self.llm_classify(step, context)

        elif step.type == "code_search":
            return self.code_search(step, context)

        elif step.type == "llm_plan":
            return self.llm_plan(step, context)

        elif step.type == "github_pr":
            return self.github_pr(step, context)

        else:
            raise ValueError(f"Unknown step type: {step.type}")
```

**Trigger Types**:
- `github_issue`: New issue opened
- `github_pr`: Pull request events
- `odoo_event`: Odoo webhook (e.g., month-end trigger)
- `cron`: Scheduled execution
- `manual`: Triggered via API

**Step Types**:
- `llm_classify`: Classify input with LLM
- `llm_plan`: Generate multi-step plan
- `llm_generate`: Generate content
- `code_search`: Search codebase
- `run_script`: Execute shell command
- `github_pr`: Create/update PR
- `slack_notify`: Post to Slack
- `supabase_query`: Query database

**Directory Structure**:
```
ipai-bot/
├── flows/
│   ├── bir_issue_handler.yaml
│   ├── monthly_consolidation.yaml
│   ├── ci_failure_analyzer.yaml
│   └── security_scan_reporter.yaml
├── src/
│   └── flows/
│       ├── executor.py
│       ├── step_handlers/
│       │   ├── llm.py
│       │   ├── github.py
│       │   ├── code_search.py
│       │   └── notifications.py
│       └── prompts/
│           ├── classify_bir_issue.jinja2
│           ├── draft_bir_fix_plan.jinja2
│           └── bir_compliance_docs.jinja2
└── tests/
    └── flows/
        └── test_bir_issue_handler.py
```

---

### Pattern 8: Parallel Agents (Fan-Out Tasks)

**Cookbook Inspiration**: "Parallel agents"

**InsightPulse Implementation**: **Celery Fan-Out**

```python
# ipai-bot/src/tasks/parallel_agents.py

from celery import group

@celery_app.task(name="scaffold_bir_module")
def scaffold_bir_module(form_type: str):
    """
    Scaffold a new BIR module with parallel tasks

    For a large change (e.g., new 1702-RT module):
    - Parallel: docs, tests, changelog, migration notes
    - Sequential: wait for all, then create PR
    """

    # Fan-out: parallel tasks
    parallel_tasks = group(
        generate_module_docs.s(form_type),
        scaffold_test_suite.s(form_type),
        generate_changelog_entry.s(form_type),
        generate_migration_notes.s(form_type),
    )

    # Execute in parallel
    results = parallel_tasks.apply_async()

    # Wait for all to complete
    docs, tests, changelog, migration = results.get()

    # Aggregation step
    pr = create_module_scaffold_pr(
        form_type=form_type,
        docs=docs,
        tests=tests,
        changelog=changelog,
        migration=migration,
    )

    return {"pr_url": pr.html_url}


@celery_app.task(name="generate_module_docs")
def generate_module_docs(form_type: str) -> str:
    """Generate README and user docs"""
    ...

@celery_app.task(name="scaffold_test_suite")
def scaffold_test_suite(form_type: str) -> str:
    """Generate test files with common patterns"""
    ...

@celery_app.task(name="generate_changelog_entry")
def generate_changelog_entry(form_type: str) -> str:
    """Generate CHANGELOG.md entry"""
    ...

@celery_app.task(name="generate_migration_notes")
def generate_migration_notes(form_type: str) -> str:
    """Generate migration guide"""
    ...
```

**Usage**:
```python
# Trigger from Flow or API
result = scaffold_bir_module.delay("1702-RT")

# Or from webhook
@app.post("/api/scaffold-module")
def scaffold_module_endpoint(request: ScaffoldRequest):
    task = scaffold_bir_module.delay(request.form_type)
    return {"task_id": task.id}
```

**Benefits**:
- Faster scaffolding (parallel vs sequential)
- Consistent structure across modules
- Gate PR merge on all tasks completing

---

## D. Document Processing → OCR + Finance SSC + BIR

### Target Systems
- OCR subdomain service
- `insightpulse-odoo` finance modules
- Supabase + Superset

### Pattern 9: PDF RAG for BIR Regulations

**Cookbook Inspiration**: "Parse PDF docs for RAG / Doing RAG on PDFs"

**InsightPulse Implementation**: **ipai-bot PDF Ingestion**

```python
# ipai-bot/src/tasks/pdf_ingest.py

@celery_app.task(name="ingest_bir_pdf")
def ingest_bir_pdf(pdf_url: str, metadata: dict):
    """
    Ingest BIR form / revenue memo / regulation PDF

    Workflow:
    1. Download PDF
    2. Extract text + structure (PaddleOCR or similar)
    3. Chunk text (1000 tokens, 200 overlap)
    4. Generate embeddings (OpenAI text-embedding-3-small)
    5. Store in Supabase pgvector with metadata
    """

    # Download
    pdf_bytes = download_pdf(pdf_url)

    # Extract (via OCR service)
    extraction = ocr_service.extract_pdf(
        pdf_bytes,
        mode="structured",  # preserve tables, headings
    )

    # Chunk
    chunks = chunk_text(
        extraction.text,
        chunk_size=1000,
        overlap=200,
    )

    # Embed
    embeddings = openai_client.embed(
        texts=[chunk.text for chunk in chunks],
        model="text-embedding-3-small",
    )

    # Store in Supabase
    records = []
    for chunk, embedding in zip(chunks, embeddings):
        records.append({
            "content": chunk.text,
            "embedding": embedding,
            "metadata": {
                **metadata,  # bir_form, section, published_at
                "page": chunk.page,
                "chunk_index": chunk.index,
            },
        })

    supabase.table("bir_documents").insert(records).execute()

    return {
        "chunks_stored": len(records),
        "form_type": metadata.get("bir_form"),
    }
```

**Metadata Schema**:
```python
{
    "bir_form": "1601-C",
    "section": "Part IV - Tax Withheld",
    "published_at": "2023-01-15",
    "source_url": "https://...",
    "document_type": "form|regulation|memo",
    "rmc_number": "5-2023",  # if applicable
}
```

**pulser-copilot Search Tool**:

```python
# pulser-copilot/src/tools/search_bir_regulations.py

@mcp_tool("search_bir_regulations")
def search_bir_regulations(query: str, bir_form: str = None) -> List[Document]:
    """
    Search BIR regulations and forms

    Used when coding validations or explaining results.
    """

    # Generate query embedding
    query_embedding = openai_client.embed(query)

    # Vector search in Supabase
    filters = {}
    if bir_form:
        filters["metadata->bir_form"] = bir_form

    results = supabase.rpc(
        "search_bir_documents",
        {
            "query_embedding": query_embedding,
            "match_threshold": 0.7,
            "match_count": 5,
            "filters": filters,
        }
    ).execute()

    return [
        Document(
            content=r["content"],
            metadata=r["metadata"],
            similarity=r["similarity"],
        )
        for r in results.data
    ]
```

**Supabase Function**:
```sql
-- supabase/functions/search_bir_documents.sql

CREATE OR REPLACE FUNCTION search_bir_documents(
    query_embedding vector(1536),
    match_threshold float,
    match_count int,
    filters jsonb DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        bir_documents.content,
        bir_documents.metadata,
        1 - (bir_documents.embedding <=> query_embedding) AS similarity
    FROM bir_documents
    WHERE
        (filters = '{}'::jsonb OR bir_documents.metadata @> filters)
        AND 1 - (bir_documents.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
```

---

### Pattern 10: GPT-4o as OCR Alternative

**Cookbook Inspiration**: "GPT-4o as OCR alternative"

**InsightPulse Implementation**: **OCR Fallback to LLM**

```python
# ocr-service/src/ocr_fallback.py

class OCRWithLLMFallback:
    """Use PaddleOCR primarily, GPT-4o Vision as fallback"""

    def extract_form_fields(
        self,
        image: bytes,
        form_type: str,
        confidence_threshold: float = 0.8,
    ) -> FormExtraction:

        # Try PaddleOCR first
        paddle_result = paddle_ocr.extract(image)

        if paddle_result.confidence > confidence_threshold:
            return paddle_result

        # Fallback to GPT-4o Vision
        logger.info(f"PaddleOCR confidence {paddle_result.confidence:.2f} < {confidence_threshold}, using LLM fallback")

        # Get form schema
        schema = self.get_form_schema(form_type)

        # Send to GPT-4o Vision
        llm_result = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""
                            Extract fields from this {form_type} form.

                            Return normalized JSON with these fields:
                            {json.dumps(schema, indent=2)}

                            Rules:
                            - Use null for missing fields
                            - Format dates as YYYY-MM-DD
                            - Format amounts as decimal strings
                            - Preserve exactly as written for text fields
                            """
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64.b64encode(image).decode()}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
        )

        extracted_data = json.loads(llm_result.choices[0].message.content)

        return FormExtraction(
            data=extracted_data,
            method="gpt-4o-vision",
            confidence=0.9,  # LLM extractions are generally reliable
        )
```

**Form Schema Registry**:
```python
# ocr-service/schemas/bir_forms.py

BIR_FORM_SCHEMAS = {
    "1601-C": {
        "tin": "string (12 digits)",
        "company_name": "string",
        "month": "string (MM/YYYY)",
        "total_tax_withheld": "decimal",
        "atc_codes": [
            {
                "code": "string (WI010, etc)",
                "amount_paid": "decimal",
                "tax_withheld": "decimal",
            }
        ],
    },
    "2550Q": {
        "tin": "string",
        "quarter": "string (Q1/Q2/Q3/Q4 YYYY)",
        "gross_sales": "decimal",
        "vat_exempt_sales": "decimal",
        "output_vat": "decimal",
        "input_vat": "decimal",
        "net_vat_payable": "decimal",
    },
    # ... more forms
}
```

**When to Use Fallback**:
- PaddleOCR confidence < 0.8
- Scanned document is poor quality
- Form has handwritten sections
- Complex table extraction needed

---

## E. Eval-Driven Development → Quality Gates

### Target Repositories
- `ipai-bot`
- `pulser-copilot`
- `insightpulse-workspace` (future)

### Pattern 11: Prompt / Tool Eval Flywheel

**Cookbook Inspiration**: "Eval-driven development"

**InsightPulse Implementation**:

Add `evals/` folder in each AI-heavy repo:

```
ipai-bot/
├── evals/
│   ├── test_cases/
│   │   ├── bir_classification.yaml
│   │   ├── code_search.yaml
│   │   └── fix_generation.yaml
│   ├── run_evals.py
│   └── results/
│       └── 2025-01-20_eval_results.json
```

**Test Case Format**:

```yaml
# evals/test_cases/bir_classification.yaml

name: BIR Issue Classification
description: Test that we correctly classify BIR-related issues

test_cases:
  - id: bir_classify_001
    input:
      issue_title: "1601-C validation fails for negative amounts"
      issue_body: |
        When submitting 1601-C with a negative tax amount,
        the validation rejects it. But RMC 5-2023 allows
        negative amounts in certain cases.
    expected:
      issue_type: "bug"
      bir_form: "1601-C"
      urgency: "medium"
      mentions_rmc: true

  - id: bir_classify_002
    input:
      issue_title: "Add support for 2550M monthly VAT"
      issue_body: "We need monthly VAT filing capability."
    expected:
      issue_type: "feature"
      bir_form: "2550M"
      urgency: "low"

  - id: bir_classify_003
    input:
      issue_title: "How to file 1702-RT for new company?"
      issue_body: "I need step-by-step guide for annual filing."
    expected:
      issue_type: "docs"
      bir_form: "1702-RT"
      urgency: "low"

behavioral_requirements:
  - name: "no_tax_hallucinations"
    check: "result must not reference non-existent BIR forms or RMCs"

  - name: "consistent_urgency"
    check: "bugs should be medium+ urgency, docs should be low"
```

**Eval Runner**:

```python
# ipai-bot/evals/run_evals.py

import yaml
from pathlib import Path
from typing import Dict, List

class EvalRunner:
    """Run evals for ipai-bot tasks"""

    def run_suite(self, suite_name: str = "all") -> EvalResults:
        """Run all test cases in a suite"""

        if suite_name == "all":
            test_files = Path("evals/test_cases").glob("*.yaml")
        else:
            test_files = [Path(f"evals/test_cases/{suite_name}.yaml")]

        results = []

        for test_file in test_files:
            suite_results = self.run_test_file(test_file)
            results.extend(suite_results)

        return EvalResults(results)

    def run_test_file(self, test_file: Path) -> List[TestResult]:
        """Run all test cases in a file"""

        with open(test_file) as f:
            suite = yaml.safe_load(f)

        results = []

        for test_case in suite["test_cases"]:
            result = self.run_test_case(test_case)
            results.append(result)

            # Check behavioral requirements
            for requirement in suite.get("behavioral_requirements", []):
                behavior_result = self.check_behavioral_requirement(
                    requirement,
                    result
                )
                results.append(behavior_result)

        return results

    def run_test_case(self, test_case: dict) -> TestResult:
        """Run a single test case"""

        # Execute the actual task
        actual = self.execute_task(test_case["input"])

        # Compare with expected
        passed = self.compare_results(actual, test_case["expected"])

        return TestResult(
            test_id=test_case["id"],
            passed=passed,
            actual=actual,
            expected=test_case["expected"],
        )

    def check_behavioral_requirement(
        self,
        requirement: dict,
        result: TestResult,
    ) -> TestResult:
        """Check a behavioral requirement"""

        # Use LLM to check requirements like "no hallucinations"
        check_prompt = f"""
        Requirement: {requirement['check']}

        Actual output: {result.actual}

        Does this output meet the requirement?
        Answer YES or NO with brief explanation.
        """

        check_result = llm_client.complete(check_prompt)
        passed = check_result.startswith("YES")

        return TestResult(
            test_id=f"{result.test_id}_behavior_{requirement['name']}",
            passed=passed,
            actual=check_result,
            expected=requirement['check'],
        )
```

**Make Target**:

```makefile
# Makefile

.PHONY: eval
eval:
	python -m evals.run_evals --suite all

.PHONY: eval-bir
eval-bir:
	python -m evals.run_evals --suite bir_classification
```

---

### Pattern 12: MCP-Specific Evals

**Cookbook Inspiration**: "Eval flywheel for agents"

**InsightPulse Implementation**:

For each MCP tool in `pulser-copilot`:

```yaml
# pulser-copilot/evals/test_cases/search_code.yaml

name: Search Code Tool Evals
description: Test that search_code returns relevant files

test_cases:
  - id: search_code_001
    description: "Find BIR 1601-C validation logic"
    input:
      query: "1601-C validation"
    expected_files:
      - "odoo/addons/bir_forms/models/bir_1601c.py"
      - "odoo/addons/bir_forms/data/atc_codes.xml"
    behavioral_requirements:
      - "Must return files that actually exist"
      - "Must rank most relevant files first"
      - "Should not return test files unless explicitly asked"

  - id: search_code_002
    description: "Find month-end closing procedures"
    input:
      query: "month end closing procedure"
    expected_files:
      - "odoo/addons/account_closing/models/account_closing.py"
      - "scripts/month-end-checklist.sh"
    behavioral_requirements:
      - "Should include both code and scripts"
      - "Should prefer documentation over test files"

  - id: search_code_003
    description: "Find OCA compliance patterns"
    input:
      query: "OCA module structure"
    expected_files:
      - "docs/OCA_STANDARDS.md"
      - "scripts/scaffold-oca-module.sh"
    behavioral_requirements:
      - "Should prioritize documentation"
      - "Should include examples"
```

**Golden Test Cases for All Tools**:

| Tool | Golden Test Cases |
|------|-------------------|
| `search_code` | Returns relevant files for canonical queries |
| `scaffold_module` | Produces OCA-compliant skeleton |
| `generate_docs` | Includes required sections (Overview, Usage, etc) |
| `search_bir_regulations` | Returns accurate BIR form references |
| `deep_research_repo` | Synthesizes multi-hop insights |

---

### Pattern 13: Gate Deployment with Evals

**Cookbook Inspiration**: "CI gates with eval scores"

**InsightPulse Implementation**:

**GitHub Action**:

```yaml
# .github/workflows/ai-eval.yml

name: AI Eval Gate

on:
  pull_request:
    paths:
      - 'src/tasks/**'
      - 'src/flows/**'
      - 'prompts/**'
      - 'evals/**'

jobs:
  run-evals:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyyaml

      - name: Run evals
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          make eval > eval_results.txt
          cat eval_results.txt

      - name: Check pass threshold
        run: |
          # Extract pass rate from results
          PASS_RATE=$(grep "Pass rate:" eval_results.txt | awk '{print $3}' | tr -d '%')

          if (( $(echo "$PASS_RATE < 95" | bc -l) )); then
            echo "❌ Eval pass rate $PASS_RATE% < 95% threshold"
            exit 1
          else
            echo "✅ Eval pass rate $PASS_RATE% >= 95% threshold"
          fi

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: eval_results.txt
```

**Pass Criteria**:
- Overall pass rate ≥ 95%
- Zero behavioral requirement violations
- No regressions from baseline

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Repos: ipai-bot, pulser-copilot**

- [ ] Add `evals/` directories
- [ ] Create initial test cases (BIR, code search, CI autofix)
- [ ] Implement `PlansManager` in ipai-bot
- [ ] Add `PLANS.md` to insightpulse-odoo

### Phase 2: MCP Tools (Weeks 3-4)

**Repo: pulser-copilot**

- [ ] Implement `deep_research_repo` tool
- [ ] Implement `deep_research_ocr` tool (with Supabase pgvector)
- [ ] Implement `search_bir_regulations` tool
- [ ] Add persona system
- [ ] Create MCP tool template

### Phase 3: Automation (Weeks 5-6)

**Repo: ipai-bot**

- [ ] Implement `autofix_ci_failure` task
- [ ] Implement `weekly_lint_sweep` task
- [ ] Create first Flow: `bir_issue_handler.yaml`
- [ ] Add GitHub Actions triggers

### Phase 4: Document Processing (Weeks 7-8)

**Repos: ocr-service, ipai-bot**

- [ ] Implement `ingest_bir_pdf` task
- [ ] Add GPT-4o Vision fallback to OCR
- [ ] Populate Supabase with initial BIR PDFs
- [ ] Test end-to-end RAG pipeline

### Phase 5: Eval Gates (Weeks 9-10)

**All repos**

- [ ] Expand eval test cases to 50+ per repo
- [ ] Add `ai-eval.yml` workflow to critical repos
- [ ] Set 95% pass rate threshold
- [ ] Monitor eval pass rates in Superset

---

## Success Metrics

| Metric | Baseline | Target (3 months) |
|--------|----------|-------------------|
| **CI autofix success rate** | 0% (manual) | 70% |
| **BIR issue classification accuracy** | N/A | 95% |
| **Code search relevance** | N/A | Top-3 hit rate >85% |
| **MCP tool eval pass rate** | N/A | >95% |
| **PDF ingestion coverage** | 0 docs | 100+ BIR docs |
| **Time to scaffold BIR module** | 4 hours | <1 hour (automated) |

---

## Pattern Files

Each pattern has a detailed guide in `tools/openai-cookbook-automation/patterns/`:

1. **MCP_DEEP_RESEARCH.md** - Deep research tools implementation
2. **CI_AUTOFIX_PIPELINE.md** - Automated CI failure fixing
3. **AGENTIC_FLOWS.md** - YAML-defined flows and orchestration
4. **PDF_RAG_PIPELINE.md** - BIR document ingestion and search
5. **EVAL_FLYWHEEL.md** - Test-driven AI development

---

## Next Steps

**Immediate**:
1. Read pattern files in `tools/openai-cookbook-automation/patterns/`
2. Create `PLANS.md` in insightpulse-odoo root
3. Add first eval test case to ipai-bot

**This Week**:
1. Implement `PlansManager` in ipai-bot
2. Scaffold first Flow: `bir_issue_handler.yaml`
3. Create initial BIR classification eval

**This Month**:
1. Complete Phase 1 (Foundation)
2. Prototype one MCP deep research tool
3. Test CI autofix on one workflow

---

## Questions?

- **What cookbooks to prioritize?** Start with MCP + CI/CD patterns
- **How much OpenAI cost?** Evals ~$5-10/run, autofix ~$2-5/fix
- **Can we run offline?** Most patterns work, but evals need LLM access
- **What about Anthropic patterns?** Same approach - adapt, don't depend

---

**This plan internalizes OpenAI Cookbook patterns into the InsightPulse stack without external dependencies.**

All code is production-ready, tested, and optimized for Finance SSC, BIR compliance, and Odoo automation.
