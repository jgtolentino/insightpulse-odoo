# Prompt Library & Context Engineering System

## Executive Summary

A curated system for maintaining reusable prompts, context templates, and LLM rules that enhance AI agent performance across InsightPulse projects.

## Why Prompt Libraries?

### Benefits
1. **Consistency** - Standardized approaches across all AI interactions
2. **Quality** - Tested, refined prompts that produce better results
3. **Efficiency** - Reusable components reduce development time
4. **Knowledge Transfer** - Documented best practices for the team
5. **Version Control** - Track prompt improvements over time
6. **Context Management** - Efficient use of token budgets

### Use Cases
- Odoo module development
- BIR tax form generation
- SQL query optimization
- Code reviews and refactoring
- Documentation generation
- Superset dashboard automation

## Directory Structure

```
insightpulse-odoo/
├── prompts/
│   ├── README.md                          # Prompt library documentation
│   ├── contexts/                          # Reusable context snippets
│   │   ├── odoo/
│   │   │   ├── model-context.md          # Odoo model context
│   │   │   ├── security-context.md       # Security rules context
│   │   │   ├── view-context.md           # XML views context
│   │   │   └── oca-standards.md          # OCA coding standards
│   │   ├── finance/
│   │   │   ├── trial-balance.md          # Trial balance context
│   │   │   ├── journal-entry.md          # Journal entry rules
│   │   │   └── bir-forms.md              # BIR compliance context
│   │   ├── supabase/
│   │   │   ├── rls-policies.md           # Row Level Security patterns
│   │   │   ├── edge-functions.md         # Edge function templates
│   │   │   └── migrations.md             # Migration best practices
│   │   └── superset/
│   │       ├── chart-types.md            # Chart selection guide
│   │       ├── sql-lab.md                # SQL optimization
│   │       └── dashboard-design.md       # Dashboard UX patterns
│   │
│   ├── templates/                         # Prompt templates
│   │   ├── code-generation/
│   │   │   ├── odoo-model.hbs            # Generate Odoo models
│   │   │   ├── odoo-wizard.hbs           # Generate wizards
│   │   │   ├── edge-function.hbs         # Supabase edge functions
│   │   │   └── rpc-function.hbs          # PostgreSQL RPC functions
│   │   ├── code-review/
│   │   │   ├── security-audit.hbs        # Security review
│   │   │   ├── performance-audit.hbs     # Performance review
│   │   │   └── oca-compliance.hbs        # OCA standards check
│   │   ├── documentation/
│   │   │   ├── module-readme.hbs         # Module documentation
│   │   │   ├── api-docs.hbs              # API documentation
│   │   │   └── user-guide.hbs            # User guide generation
│   │   └── analysis/
│   │       ├── error-diagnosis.hbs       # Error analysis
│   │       ├── query-optimization.hbs    # SQL optimization
│   │       └── dependency-analysis.hbs   # Dependency graph
│   │
│   ├── rules/                             # LLM behavior rules
│   │   ├── odoo-development.md           # Odoo dev best practices
│   │   ├── supabase-patterns.md          # Supabase patterns
│   │   ├── bir-compliance.md             # BIR regulatory rules
│   │   ├── security-standards.md         # Security requirements
│   │   └── code-style.md                 # Code formatting rules
│   │
│   └── examples/                          # Working examples
│       ├── odoo-module-complete/         # Full module example
│       ├── edge-function-auth/           # Auth edge function
│       ├── bir-1601c-wizard/             # BIR form wizard
│       └── superset-dashboard/           # Dashboard automation
│
└── .llmrules                              # Global LLM rules file
```

## Context Engineering Strategies

### 1. Hierarchical Context Loading

Load only the context needed for the current task:

```markdown
# Context Layers (Priority Order)

## Layer 1: Core System Context (Always Loaded)
- Project structure
- Tech stack overview
- Critical constraints

## Layer 2: Domain Context (Load on Demand)
- Odoo models and relationships
- BIR form requirements
- Finance rules

## Layer 3: Task-Specific Context (Minimal)
- Specific file contents
- Related code snippets
- Recent changes
```

### 2. Token Budget Management

```python
# scripts/optimize-context.py
"""
Optimize context usage to fit within token budgets.
"""

MAX_TOKENS = 200_000  # Claude Sonnet 4.5
RESERVE_TOKENS = 50_000  # Reserve for response

def calculate_context_size(contexts: list[str]) -> int:
    """Estimate token count for contexts."""
    return sum(len(c.split()) * 1.3 for c in contexts)  # ~1.3 tokens per word

def optimize_context_loading(task: str) -> list[str]:
    """Load minimal context for task."""
    contexts = []

    # Always include core context
    contexts.append(load_context('core/project-structure.md'))

    # Domain-specific
    if 'odoo' in task.lower():
        contexts.append(load_context('odoo/model-context.md'))
    if 'bir' in task.lower():
        contexts.append(load_context('finance/bir-forms.md'))

    # Validate size
    if calculate_context_size(contexts) > (MAX_TOKENS - RESERVE_TOKENS):
        raise ValueError('Context too large, optimize further')

    return contexts
```

### 3. Progressive Context Refinement

Start broad, then narrow down:

```markdown
# Step 1: High-level context
"I need to generate a BIR 1601C form"

# Step 2: Load specific context
→ Load: prompts/contexts/finance/bir-forms.md
→ Load: prompts/templates/code-generation/odoo-wizard.hbs

# Step 3: Inject working examples
→ Load: prompts/examples/bir-1601c-wizard/

# Step 4: Generate with full context
```

## Prompt Template System

### Handlebars Templates

```handlebars
{{!-- prompts/templates/code-generation/odoo-model.hbs --}}
---
Task: Generate Odoo Model
Framework: Odoo 19 / OCA Standards
---

# Requirements

Generate a new Odoo model with the following specifications:

**Model Name:** `{{model_name}}`
**Table Name:** `{{table_name}}`
**Description:** {{description}}
**Inherits From:** {{#if inherits}}{{inherits}}{{else}}models.Model{{/if}}

## Fields

{{#each fields}}
- **{{this.name}}** ({{this.type}}): {{this.description}}
  {{#if this.required}}- Required: Yes{{/if}}
  {{#if this.help}}- Help: {{this.help}}{{/if}}
{{/each}}

## Business Logic

{{#if compute_methods}}
### Computed Fields
{{#each compute_methods}}
- `{{this.field}}` computed by `{{this.method}}`
{{/each}}
{{/if}}

{{#if constraints}}
### Constraints
{{#each constraints}}
- `{{this.name}}`: {{this.description}}
{{/each}}
{{/if}}

## Security Requirements

- Enable Row Level Security (RLS)
- Multi-company support: {{multi_company}}
- Access groups: {{access_groups}}

## OCA Compliance

✅ Follow OCA module structure
✅ Include proper docstrings
✅ Add type hints (Python 3.10+)
✅ Use OCA code formatting (black, isort, pylint)
✅ Include tests with >80% coverage

---

# Context

{{> odoo/model-context}}
{{> odoo/security-context}}
{{> odoo/oca-standards}}

---

# Example Structure

```python
# File: models/{{model_name}}.py
from odoo import models, fields, api

class {{pascal_case model_name}}(models.Model):
    _name = '{{table_name}}'
    _description = '{{description}}'
    {{#if inherits}}_inherit = ['{{inherits}}']{{/if}}

    # Fields
    {{#each fields}}
    {{this.name}} = fields.{{title_case this.type}}(
        string='{{this.label}}',
        {{#if this.required}}required=True,{{/if}}
        {{#if this.help}}help='{{this.help}}',{{/if}}
    )
    {{/each}}
```

---

# Generate the model following all requirements above.
```

### Using Templates Programmatically

```typescript
// scripts/generate-from-template.ts
import Handlebars from 'handlebars'
import { readFileSync } from 'fs'

// Load template
const template = Handlebars.compile(
  readFileSync('prompts/templates/code-generation/odoo-model.hbs', 'utf8')
)

// Load context partials
Handlebars.registerPartial(
  'odoo/model-context',
  readFileSync('prompts/contexts/odoo/model-context.md', 'utf8')
)

// Generate prompt
const prompt = template({
  model_name: 'account_trial_balance',
  table_name: 'account.trial.balance',
  description: 'Trial Balance Report for Multi-Company',
  multi_company: true,
  access_groups: 'account.group_account_manager',
  fields: [
    {
      name: 'period_start',
      type: 'Date',
      label: 'Period Start',
      required: true,
      help: 'Start date for trial balance calculation'
    }
  ]
})
```

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Create directory structure
- [ ] Write global .llmrules file
- [ ] Document 5 core contexts (Odoo, Supabase, Finance, BIR, Superset)
- [ ] Create 3 essential templates (model generation, edge function, dashboard)

### Phase 2: Templates (Week 2)
- [ ] Code generation templates (10+ templates)
- [ ] Code review templates (5+ templates)
- [ ] Documentation templates (5+ templates)
- [ ] Add Handlebars helper functions

### Phase 3: Examples (Week 3)
- [ ] Complete Odoo module example
- [ ] Complete edge function example
- [ ] Complete BIR wizard example
- [ ] Complete Superset dashboard example

### Phase 4: Integration (Week 4)
- [ ] CI/CD integration (automated prompts in GitHub Actions)
- [ ] Claude Code skill integration
- [ ] VS Code snippets integration
- [ ] Cursor IDE integration

## Integration with Claude Code Skills

```yaml
# .claude/settings.json
{
  "prompt_library": {
    "enabled": true,
    "path": "prompts/",
    "auto_load_contexts": true,
    "template_engine": "handlebars"
  },
  "context_engineering": {
    "max_tokens": 150000,
    "reserve_tokens": 50000,
    "auto_optimize": true
  }
}
```

## Cursor IDE Integration

```json
// .cursorrules
{
  "rules": [
    {
      "name": "Odoo Development",
      "file": "prompts/rules/odoo-development.md",
      "applies_to": ["**/*.py", "**/models/*.py", "**/views/*.xml"]
    },
    {
      "name": "Supabase Edge Functions",
      "file": "prompts/rules/supabase-patterns.md",
      "applies_to": ["**/supabase/functions/**/*.ts"]
    },
    {
      "name": "BIR Compliance",
      "file": "prompts/rules/bir-compliance.md",
      "applies_to": ["**/bir_tax_filing/**/*"]
    }
  ]
}
```

## Context Engineering Best Practices

### 1. Lazy Loading
Only load context when needed:

```typescript
class ContextManager {
  private cache = new Map<string, string>()

  async getContext(task: string): Promise<string> {
    const contextKey = this.determineContextKey(task)

    if (!this.cache.has(contextKey)) {
      this.cache.set(contextKey, await this.loadContext(contextKey))
    }

    return this.cache.get(contextKey)!
  }

  private determineContextKey(task: string): string {
    if (task.includes('odoo') && task.includes('model')) {
      return 'odoo/model-context'
    }
    if (task.includes('bir') && task.includes('1601')) {
      return 'finance/bir-1601c'
    }
    return 'core/basic-context'
  }
}
```

### 2. Context Compression
Summarize large contexts:

```typescript
async function compressContext(context: string): Promise<string> {
  // Use LLM to summarize long contexts
  const summary = await llm.summarize(context, {
    max_length: 500,
    preserve_code_examples: true
  })
  return summary
}
```

### 3. Incremental Context Building
Start small, expand as needed:

```markdown
# Iteration 1: Minimal context
Task: "Generate Odoo model"
Context: Basic Odoo model structure (500 tokens)

# Iteration 2: Add domain context
Error: "Field type not recognized"
Context: + Odoo field types reference (1000 tokens)

# Iteration 3: Add specific example
Error: "Compute method syntax unclear"
Context: + Working compute method example (500 tokens)

Total: 2000 tokens (optimized)
```

## Measuring Effectiveness

### Metrics to Track

```python
# scripts/measure-prompt-effectiveness.py
class PromptMetrics:
    def __init__(self):
        self.metrics = {
            'success_rate': 0.0,      # % of prompts that work first try
            'token_usage': 0,          # Average tokens per prompt
            'iteration_count': 0,      # Average iterations to success
            'time_to_solution': 0.0,   # Average seconds to solution
        }

    def record_prompt_execution(
        self,
        prompt_template: str,
        success: bool,
        tokens_used: int,
        iterations: int,
        time_elapsed: float
    ):
        """Record metrics for prompt execution."""
        self.metrics['success_rate'] = (
            self.metrics['success_rate'] * 0.9 + (1.0 if success else 0.0) * 0.1
        )
        self.metrics['token_usage'] = tokens_used
        self.metrics['iteration_count'] = iterations
        self.metrics['time_to_solution'] = time_elapsed

        # Store in database for analysis
        self.store_metrics(prompt_template, self.metrics)
```

## Conclusion

A well-maintained prompt library with context engineering provides:

✅ **Faster Development** - Reusable, tested prompts
✅ **Better Quality** - Consistent, standards-compliant code
✅ **Knowledge Preservation** - Institutional knowledge in version control
✅ **Cost Optimization** - Efficient token usage
✅ **Team Collaboration** - Shared best practices

**Next Steps:**
1. Start with Phase 1 (Foundation) - create core structure
2. Document top 10 most common tasks
3. Create templates for those tasks
4. Measure and iterate based on effectiveness metrics

---

**Related Documentation:**
- `/docs/HYBRID_STACK_ARCHITECTURE.md` - Architecture patterns
- `/docs/claude-code-skills/` - Claude Code skills library
- `.llmrules` - Global LLM rules
