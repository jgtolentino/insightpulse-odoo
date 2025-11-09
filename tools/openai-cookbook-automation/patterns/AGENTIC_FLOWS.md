# Agentic Flows Pattern

## Overview

YAML-defined multi-step workflows with triggers, steps, and outputs. Adapted from OpenAI Cookbook's "AgentKit / OpenAI Agents SDK" pattern for ipai-bot orchestration.

## Target Repo

`ipai-bot` (flows engine)

## Pattern

```
Trigger Event (GitHub, Odoo, cron)
    ↓
Load Flow Definition (YAML)
    ↓
Execute Steps Sequentially
    ├─ LLM Classify
    ├─ Code Search
    ├─ Generate Plan
    └─ Create PR
    ↓
Outputs Passed Between Steps
```

## Flow Definition Format

```yaml
# ipai-bot/flows/bir_issue_handler.yaml

name: BIR Issue Handler
description: Auto-handle BIR-related issues

trigger:
  type: github_issue
  repo: insightpulse-odoo
  labels: ["bir", "tax", "compliance"]
  conditions:
    - issue.state == "open"
    - not issue.assignee  # Only unassigned

steps:
  - name: classify_issue
    type: llm_classify
    prompt_template: classify_bir_issue.jinja2
    inputs:
      - trigger.issue.title
      - trigger.issue.body
    outputs:
      - issue_type      # bug / feature / docs
      - bir_form        # 1601-C / 2550Q / etc
      - urgency         # high / medium / low
      - affected_module # module name

  - name: gather_context
    type: code_search
    params:
      query: "{{ bir_form }} {{ affected_module }}"
      paths: ["odoo/addons/bir_*", "odoo/addons/{{ affected_module }}"]
      max_results: 10
    outputs:
      - relevant_files

  - name: search_regulations
    type: supabase_query
    params:
      table: bir_documents
      filters:
        bir_form: "{{ bir_form }}"
      limit: 5
    outputs:
      - regulations

  - name: draft_fix_plan
    type: llm_plan
    prompt_template: draft_bir_fix_plan.jinja2
    inputs:
      - trigger.issue.body
      - issue_type
      - relevant_files
      - regulations
    outputs:
      - fix_plan
      - estimated_effort

  - name: generate_compliance_notes
    type: llm_generate
    prompt_template: bir_compliance_notes.jinja2
    inputs:
      - fix_plan
      - bir_form
      - regulations
    outputs:
      - compliance_notes

  - name: create_pr_or_comment
    type: conditional
    condition: "{{ issue_type == 'bug' and urgency == 'high' }}"
    then:
      - name: create_pr
        type: github_pr
        params:
          repo: "{{ trigger.repo }}"
          branch: "fix/bir-{{ trigger.issue.number }}"
          title: "Fix: {{ trigger.issue.title }}"
          body: |
            ## Fix Plan
            {{ fix_plan }}

            ## Compliance Notes
            {{ compliance_notes }}

            ## Effort Estimate
            {{ estimated_effort }}

            Fixes #{{ trigger.issue.number }}
          labels: ["bir", "automated", "{{ urgency }}"]
    else:
      - name: comment_on_issue
        type: github_comment
        params:
          repo: "{{ trigger.repo }}"
          issue: "{{ trigger.issue.number }}"
          body: |
            ## Automated Analysis

            **Type**: {{ issue_type }}
            **Form**: {{ bir_form }}
            **Urgency**: {{ urgency }}

            ### Suggested Fix Plan
            {{ fix_plan }}

            ### Relevant Code
            {% for file in relevant_files %}
            - `{{ file.path }}`
            {% endfor %}

  - name: notify_team
    type: slack_notify
    params:
      channel: "#bir-automation"
      message: |
        🤖 Handled BIR issue #{{ trigger.issue.number }}
        Type: {{ issue_type }} | Form: {{ bir_form }} | Urgency: {{ urgency }}
        {% if pr_url %}PR created: {{ pr_url }}{% else %}Analysis posted as comment{% endif %}
```

## Flow Executor Implementation

```python
# ipai-bot/src/flows/executor.py

class FlowExecutor:
    """Execute YAML-defined flows"""

    def __init__(self):
        self.step_handlers = {
            "llm_classify": LLMClassifyHandler(),
            "llm_plan": LLMPlanHandler(),
            "llm_generate": LLMGenerateHandler(),
            "code_search": CodeSearchHandler(),
            "supabase_query": SupabaseQueryHandler(),
            "github_pr": GitHubPRHandler(),
            "github_comment": GitHubCommentHandler(),
            "slack_notify": SlackNotifyHandler(),
            "conditional": ConditionalHandler(),
        }

    def execute(self, flow_path: str, trigger_data: dict):
        """Execute a flow"""
        flow = self.load_flow(flow_path)

        # Check trigger matches
        if not self.trigger_matches(flow.trigger, trigger_data):
            logger.info(f"Trigger doesn't match for flow {flow.name}")
            return None

        # Initialize context
        context = {"trigger": trigger_data}

        # Execute steps
        for step in flow.steps:
            logger.info(f"Executing step: {step.name}")

            try:
                result = self.execute_step(step, context)

                # Add outputs to context
                for output_name, output_value in result.outputs.items():
                    context[output_name] = output_value

            except StepError as e:
                logger.error(f"Step {step.name} failed: {e}")

                # Handle error (retry, skip, or fail)
                if step.on_error == "retry":
                    result = self.retry_step(step, context)
                elif step.on_error == "skip":
                    continue
                else:
                    raise

        return context

    def execute_step(self, step: FlowStep, context: dict):
        """Execute a single step"""
        handler = self.step_handlers[step.type]

        # Render inputs with Jinja2
        rendered_inputs = self.render_inputs(step.inputs, context)
        rendered_params = self.render_params(step.params, context)

        # Execute
        result = handler.execute(rendered_inputs, rendered_params)

        return result

    def render_inputs(self, inputs: List[str], context: dict) -> dict:
        """Render input values using Jinja2"""
        env = Environment()
        rendered = {}

        for input_ref in inputs:
            template = env.from_string(input_ref)
            rendered[input_ref] = template.render(context)

        return rendered
```

## Step Handlers

```python
# ipai-bot/src/flows/step_handlers/llm.py

class LLMClassifyHandler(StepHandler):
    """LLM classification step"""

    def execute(self, inputs: dict, params: dict) -> StepResult:
        prompt_template = params["prompt_template"]
        prompt = render_template(prompt_template, **inputs)

        response = llm_client.complete(prompt, response_format="json")
        outputs = json.loads(response)

        return StepResult(outputs=outputs)


class LLMPlanHandler(StepHandler):
    """LLM planning step"""

    def execute(self, inputs: dict, params: dict) -> StepResult:
        prompt_template = params["prompt_template"]
        prompt = render_template(prompt_template, **inputs)

        plan = llm_client.complete(prompt)

        return StepResult(outputs={"plan": plan})
```

```python
# ipai-bot/src/flows/step_handlers/code_search.py

class CodeSearchHandler(StepHandler):
    """Code search step using pulser-copilot"""

    def execute(self, inputs: dict, params: dict) -> StepResult:
        query = params["query"]
        paths = params.get("paths", ["**/*"])
        max_results = params.get("max_results", 10)

        # Call pulser-copilot MCP tool
        results = mcp_client.call_tool(
            "search_code",
            {
                "query": query,
                "paths": paths,
                "max_results": max_results,
            }
        )

        return StepResult(outputs={"relevant_files": results})
```

```python
# ipai-bot/src/flows/step_handlers/github.py

class GitHubPRHandler(StepHandler):
    """Create GitHub PR"""

    def execute(self, inputs: dict, params: dict) -> StepResult:
        repo = params["repo"]
        branch = params["branch"]
        title = params["title"]
        body = params["body"]
        labels = params.get("labels", [])

        # Create branch
        github_api.create_branch(repo, branch)

        # Create PR
        pr = github_api.create_pull_request(
            repo=repo,
            head=branch,
            base="main",
            title=title,
            body=body,
        )

        # Add labels
        if labels:
            github_api.add_labels(repo, pr.number, labels)

        return StepResult(outputs={"pr_url": pr.html_url, "pr_number": pr.number})
```

## Trigger Types

| Type | Description | Data Available |
|------|-------------|----------------|
| `github_issue` | GitHub issue opened/labeled | issue.title, issue.body, issue.number, issue.labels |
| `github_pr` | Pull request events | pr.title, pr.body, pr.number, pr.files |
| `odoo_event` | Odoo webhook | event.model, event.res_id, event.action |
| `cron` | Scheduled | schedule.name, schedule.params |
| `manual` | API trigger | user.id, manual.params |

## Conditional Logic

```yaml
steps:
  - name: decide_action
    type: conditional
    condition: "{{ urgency == 'high' and issue_type == 'bug' }}"
    then:
      - name: create_immediate_pr
        type: github_pr
        # ...
    else:
      - name: schedule_review
        type: create_task
        # ...
```

## Parallel Execution

```yaml
steps:
  - name: gather_all_context
    type: parallel
    steps:
      - name: search_code
        type: code_search
        # ...
      - name: search_docs
        type: doc_search
        # ...
      - name: query_db
        type: supabase_query
        # ...
    aggregation: "merge_outputs"
```

## Error Handling

```yaml
steps:
  - name: risky_step
    type: llm_generate
    on_error: retry
    retry_config:
      max_attempts: 3
      backoff: exponential
      initial_delay: 2s
```

## Directory Structure

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
│       │   ├── code_search.py
│       │   ├── github.py
│       │   ├── supabase.py
│       │   └── notifications.py
│       └── prompts/
│           ├── classify_bir_issue.jinja2
│           ├── draft_bir_fix_plan.jinja2
│           └── bir_compliance_notes.jinja2
└── tests/
    └── flows/
        └── test_bir_issue_handler.py
```

## Usage

```python
# Trigger from webhook
@app.post("/webhooks/github/issues")
async def handle_github_issue(payload: dict):
    executor = FlowExecutor()

    # Find matching flows
    flows = find_flows_for_trigger("github_issue", payload)

    # Execute each flow
    for flow_path in flows:
        result = executor.execute(flow_path, payload)
        logger.info(f"Flow {flow_path} completed: {result}")

    return {"status": "ok"}
```

## Eval Criteria

```yaml
# ipai-bot/evals/flows.yaml

test_cases:
  - name: "BIR issue creates PR for high urgency bugs"
    flow: bir_issue_handler.yaml
    trigger:
      type: github_issue
      issue:
        title: "1601-C validation fails for negative amounts"
        body: "Critical bug affecting all users..."
        labels: ["bir", "bug"]
    expected:
      - step: classify_issue
        outputs:
          issue_type: "bug"
          urgency: "high"
      - step: create_pr
        executed: true
        outputs:
          pr_url: starts_with("https://github.com")

  - name: "Low urgency issues get comments, not PRs"
    flow: bir_issue_handler.yaml
    trigger:
      type: github_issue
      issue:
        title: "Add docs for 1702-RT"
        body: "We need documentation..."
        labels: ["bir", "docs"]
    expected:
      - step: classify_issue
        outputs:
          issue_type: "docs"
          urgency: "low"
      - step: create_pr
        executed: false
      - step: comment_on_issue
        executed: true
```

## Cost Estimate

Per flow execution:
- Classification: ~1000 tokens ($0.001)
- Planning: ~3000 tokens ($0.003)
- Generation: ~2000 tokens ($0.002)
- **Total**: ~$0.006

## Next Steps

1. Implement FlowExecutor base
2. Create 5 step handlers (LLM, code search, GitHub, Supabase, Slack)
3. Build first flow: `bir_issue_handler.yaml`
4. Add webhook endpoint
5. Create evals with 10+ test cases
