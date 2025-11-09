# CI Autofix Pipeline Pattern

## Overview

Automatically detect, diagnose, and fix CI failures using LLM. Adapted from OpenAI Cookbook's "Codex CLI for CI autofix" pattern.

## Target Repos

- `ipai-bot` (autofix task)
- `insightpulse-odoo` (trigger workflow)

## Pattern

```
CI Workflow Fails
    ↓
Webhook to ipai-bot
    ↓
Fetch Failing Logs
    ↓
Extract Error Context
    ↓
Get Relevant Code
    ↓
LLM Generate Fix
    ↓
Create Draft PR
```

## Implementation

### ipai-bot Task

```python
# ipai-bot/src/tasks/ci_autofix.py

@celery_app.task(name="autofix_ci_failure")
def autofix_ci_failure(repo: str, workflow_name: str, run_id: int):
    """Auto-generate fix for failing CI"""

    # 1. Fetch logs
    logs = github_api.get_workflow_run_logs(repo, run_id)
    errors = extract_errors(logs)

    if not errors:
        return {"status": "no_errors_found"}

    # 2. Get code context
    code_context = get_code_context(repo, errors)

    # 3. Generate fix
    fix_prompt = render_template(
        "ci_autofix.jinja2",
        workflow=workflow_name,
        errors=errors,
        code=code_context,
    )

    patch = llm_client.generate_patch(fix_prompt)

    # 4. Validate patch (syntax check, test locally)
    if not validate_patch(patch, repo):
        return {"status": "patch_validation_failed", "patch": patch}

    # 5. Create PR
    pr = create_autofix_pr(
        repo=repo,
        run_id=run_id,
        patch=patch,
        branch=f"ci/autofix-{run_id}",
    )

    return {
        "status": "success",
        "pr_url": pr.html_url,
        "patch_preview": patch[:500],
    }


def extract_errors(logs: str) -> List[Error]:
    """Parse logs to extract errors"""
    errors = []

    # Common patterns
    patterns = [
        r"ERROR:(.+?)(?=\n|$)",
        r"FAILED (.+?) - (.+)",
        r"AssertionError:(.+)",
        r"ModuleNotFoundError:(.+)",
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, logs, re.MULTILINE)
        for match in matches:
            errors.append(Error(
                type="test_failure",
                message=match.group(0),
                file=extract_file_from_error(match.group(0)),
                line=extract_line_from_error(match.group(0)),
            ))

    return errors


def get_code_context(repo: str, errors: List[Error]) -> str:
    """Get relevant code for each error"""
    context_parts = []

    for error in errors:
        if error.file:
            # Get file content around error line
            content = github_api.get_file_content(
                repo,
                error.file,
                line_start=max(1, error.line - 20),
                line_end=error.line + 20,
            )
            context_parts.append(f"# {error.file}:{error.line}\n{content}")

    return "\n\n".join(context_parts)
```

### Prompt Template

```jinja2
{# prompts/ci_autofix.jinja2 #}

# CI Failure Autofix

**Workflow**: {{ workflow }}
**Repository**: {{ repo }}

## Errors

{% for error in errors %}
### Error {{ loop.index }}

```
{{ error.message }}
```

**File**: `{{ error.file }}`
**Line**: {{ error.line }}

{% endfor %}

## Relevant Code

{{ code }}

## Task

Generate a **minimal patch** to fix these errors.

**Requirements**:
- Fix only the immediate cause
- Don't refactor unrelated code
- Preserve existing functionality
- Add comments explaining the fix
- Include test updates if needed

**Output Format**:

```diff
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -line,count +line,count @@
 context
-old line
+new line
 context
```
```

### GitHub Workflow Trigger

```yaml
# .github/workflows/ci-autofix-trigger.yml

name: Trigger CI Autofix

on:
  workflow_run:
    workflows:
      - "CI/CD"
      - "Notebook CI"
      - "Quality Checks"
    types: [completed]

jobs:
  trigger-autofix:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest

    steps:
      - name: Check if autofix is enabled
        id: check
        run: |
          # Only autofix on test failures, not build/deploy
          if [[ "${{ github.event.workflow_run.name }}" == "CI/CD" ]]; then
            echo "enabled=true" >> $GITHUB_OUTPUT
          fi

      - name: Trigger ipai-bot
        if: steps.check.outputs.enabled == 'true'
        run: |
          curl -X POST https://ipai-bot.insightpulseai.net/api/autofix \
            -H "Authorization: Bearer ${{ secrets.IPAI_BOT_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{
              "repo": "${{ github.repository }}",
              "workflow_name": "${{ github.event.workflow_run.name }}",
              "run_id": ${{ github.event.workflow_run.id }},
              "head_sha": "${{ github.event.workflow_run.head_sha }}"
            }'
```

## Behavior Contract

1. **Only test failures**: Don't autofix build/deploy failures
2. **Draft PRs**: Never auto-merge
3. **Label**: Add `ci/autofix` label
4. **Explanation**: Include comment with reasoning
5. **Validation**: Syntax check before creating PR

## Safety Rails

```python
def validate_patch(patch: str, repo: str) -> bool:
    """Validate patch before creating PR"""

    # 1. Syntax check
    if not syntax_check(patch):
        logger.error("Patch has syntax errors")
        return False

    # 2. Test locally (optional)
    if ENABLE_LOCAL_TEST:
        result = test_patch_locally(patch, repo)
        if not result.success:
            logger.error(f"Local test failed: {result.error}")
            return False

    # 3. Size check
    if count_changed_lines(patch) > 100:
        logger.error("Patch too large (>100 lines)")
        return False

    return True
```

## Eval Criteria

```yaml
# ipai-bot/evals/ci_autofix.yaml

test_cases:
  - name: "Fix import error"
    input:
      error: "ModuleNotFoundError: No module named 'pandas'"
      file: "tests/test_analytics.py"
    expected_fix:
      contains: "import pandas"
      or_contains: "requirements.txt"

  - name: "Fix assertion failure"
    input:
      error: "AssertionError: Expected 5, got 3"
      file: "tests/test_consolidation.py"
      line: 42
    expected_fix:
      modifies_file: "tests/test_consolidation.py"
      or_modifies: "src/consolidation.py"

behavioral_requirements:
  - "Must not change unrelated files"
  - "Must include explanation comment"
  - "Must preserve test intent"
```

## Cost Estimate

- Log parsing: Free
- Fix generation: ~4000 tokens ($0.004)
- **Total per autofix**: ~$0.004

## Success Metrics

- **Autofix success rate**: 70% target
- **False positive rate**: <10%
- **Average time to fix**: <5 minutes

## Next Steps

1. Implement error extraction patterns
2. Build PR creation logic
3. Add validation checks
4. Create 20+ eval test cases
5. Monitor success rate in Superset
