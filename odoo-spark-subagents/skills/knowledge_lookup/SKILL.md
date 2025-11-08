# knowledge_lookup

**Goal**: Provide unified access to the knowledge-first automation infrastructure for all agents.

**Progressive disclosure**: Load this skill when agents need to:
- Search for existing solutions, patterns, or skills
- Record execution outcomes for learning
- Trigger skill harvesting from successful runs
- Learn from error patterns

## Capabilities

### 1. Knowledge Search
Search the knowledge graph for relevant:
- **Skills**: Reusable capability patterns
- **Documentation**: Odoo docs, forum posts, GitHub issues
- **Error Resolutions**: Known errors and their guardrails

### 2. Observation Recording
Persist agent execution outcomes to feed:
- RL training dataset
- Skill harvesting pipeline
- Error learning system

### 3. Auto-Learning
Trigger on-demand:
- Skill harvesting from recent successes
- Error pattern extraction from failures
- Guardrail skill generation

## Usage

### Search for Skills

**Before starting a task**, query for existing solutions:

```python
# Find skills related to current task
results = knowledge_lookup.search(
    query="create odoo sales order with partner validation",
    limit=5
)

# Use top result if highly relevant
if results and results[0]['similarity'] > 0.85:
    skill = results[0]
    # Apply skill pattern
```

### Record Execution Outcomes

**After completing a task**, record the outcome:

```python
# On success
knowledge_lookup.record_outcome(
    run_id=trace_id,
    outcome="success",
    metadata={
        "agent": "automation_executor",
        "tools_used": ["create_sales_order"],
        "duration_ms": 1250,
        "plan": plan_dict
    }
)

# On failure
knowledge_lookup.record_outcome(
    run_id=trace_id,
    outcome="error",
    metadata={
        "agent": "automation_executor",
        "error": str(exception),
        "error_type": type(exception).__name__,
        "plan": plan_dict
    }
)
```

### Harvest New Skills

**Periodically** (e.g., nightly cron), harvest skills from successful runs:

```python
result = knowledge_lookup.harvest_skills(max_runs=100)
print(f"Harvested {result['harvested_count']} new skills:")
for skill_name in result['skill_names']:
    print(f"  - {skill_name}")
```

### Learn from Errors

**When error rates increase**, trigger error learning:

```python
result = knowledge_lookup.learn_from_errors(lookback_days=7)
print(f"Learned {result['patterns_learned']} error patterns")
print(f"Created {result['guardrails_created']} guardrail skills")
```

### Check Known Errors

**Before executing risky operations**, check if errors are known:

```python
try:
    # Risky operation
    result = create_sales_order(partner_id=123)
except Exception as e:
    # Check if this is a known error
    known = knowledge_lookup.check_error(
        error_message=str(e),
        error_type=type(e).__name__
    )

    if known['is_known'] and known['similarity'] > 0.85:
        print(f"Known error! Resolution: {known['resolution_skill']}")
        # Apply guardrail skill to prevent recurrence
    else:
        # New error - will be learned
        raise
```

## Examples

### Example 1: Create PR with Context

```python
# Agent: git_specialist
# Task: Create PR for bug fixes

# 1. Search for similar PR patterns
context = knowledge_lookup.search(
    query="create pull request with bug fixes",
    query_type="skills",
    category="git",
    limit=3
)

# 2. Execute task using learned patterns
pr = create_pr(
    title="fix: resolve partner validation errors",
    body=generate_pr_body(context),
    draft=True
)

# 3. Record success
knowledge_lookup.record_outcome(
    run_id=trace_id,
    outcome="success",
    metadata={
        "pr_url": pr.url,
        "context_used": [c['title'] for c in context['results']]
    }
)
```

### Example 2: Odoo Operation with Guardrails

```python
# Agent: automation_executor
# Task: Create sales order

# 1. Check for known validation errors
known_errors = knowledge_lookup.search(
    query="sales order partner validation",
    query_type="errors",
    limit=5
)

# 2. Apply guardrails from known errors
for error_pattern in known_errors:
    if error_pattern.get('resolution_skill'):
        apply_guardrail(error_pattern['resolution_skill'])

# 3. Execute with guardrails
try:
    order = create_sales_order(
        partner_id=partner_id,
        order_lines=lines
    )

    # Record success
    knowledge_lookup.record_outcome(
        run_id=trace_id,
        outcome="success",
        metadata={"order_id": order.id}
    )

except ValidationError as e:
    # Record failure (will trigger learning)
    knowledge_lookup.record_outcome(
        run_id=trace_id,
        outcome="error",
        metadata={
            "error": str(e),
            "error_type": "ValidationError",
            "partner_id": partner_id
        }
    )
    raise
```

### Example 3: Daily Automation Loop

```python
# Cron job: Daily knowledge maintenance

# 1. Harvest skills from yesterday's successes
harvest_result = knowledge_lookup.harvest_skills(hours=24)

# 2. Learn from yesterday's failures
learn_result = knowledge_lookup.learn_from_errors(lookback_days=1)

# 3. Log results
print(f"Daily automation complete:")
print(f"  - Skills harvested: {harvest_result['harvested_count']}")
print(f"  - Error patterns learned: {learn_result['patterns_learned']}")
print(f"  - Guardrails created: {learn_result['guardrails_created']}")
```

## Inputs

All operations use the `knowledge_lookup` skill interface:

### search(query, query_type="auto", category=None, threshold=0.7, limit=20)
- **query**: Natural language description
- **query_type**: "skills" | "knowledge" | "errors" | "auto"
- **category**: Optional filter ("odoo", "git", "automation", "conflict")
- **threshold**: Minimum similarity (0-1)
- **limit**: Max results

### record_outcome(run_id, outcome, metadata)
- **run_id**: Unique trace identifier
- **outcome**: "success" | "partial" | "error"
- **metadata**: Dict with execution details

### harvest_skills(max_runs=100, hours=24, min_confidence=0.75)
- **max_runs**: Max successful runs to analyze
- **hours**: Look back period
- **min_confidence**: Minimum confidence to harvest

### learn_from_errors(lookback_days=7, min_occurrences=2)
- **lookback_days**: Error history window
- **min_occurrences**: Min occurrences to trigger learning

### check_error(error_message, error_type=None)
- **error_message**: Error text to check
- **error_type**: Exception class name

## Outputs

### Search Results
```python
{
    "results": [
        {
            "id": "uuid",
            "type": "skill" | "knowledge" | "error",
            "title": "Skill/doc title",
            "content": "Full content",
            "similarity": 0.92,
            "metadata": {...}
        }
    ],
    "total_found": 5
}
```

### Harvest Results
```python
{
    "harvested_count": 3,
    "skill_names": ["skill_a", "skill_b", "skill_c"],
    "skipped_count": 2
}
```

### Learning Results
```python
{
    "patterns_learned": 5,
    "guardrails_created": 3,
    "error_signatures": ["sig1", "sig2", ...]
}
```

## Guardrails

- **Rate Limiting**: Max 60 queries/minute per agent
- **Timeout**: 10 second max per operation
- **Max Results**: 100 results per query
- **Secret Protection**: Never store credentials in metadata
- **Schema Validation**: All inputs validated against JSON schemas

## Checkpoints

- Observations are persisted immediately after recording
- Harvesting runs can be interrupted and resumed
- Error learning is idempotent (safe to re-run)

## Dependencies

- Supabase connection (pgvector enabled)
- OpenAI API (for embeddings)
- `knowledge_client` agent

## Tags

knowledge, search, learning, skills, errors, automation, rl-training
