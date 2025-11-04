# Prompt Library & Context Engineering

Reusable prompts, contexts, and LLM rules for InsightPulse AI agents.

## Quick Start

```bash
# Use a template
cat prompts/templates/code-generation/odoo-model.hbs

# Load context
cat prompts/contexts/odoo/model-context.md

# Apply rules
cat prompts/rules/odoo-development.md
```

## Directory Structure

- **contexts/** - Reusable context snippets for specific domains
- **templates/** - Handlebars templates for code generation, reviews, docs
- **rules/** - LLM behavior rules and coding standards
- **examples/** - Working examples of complete implementations

## Usage

See `/docs/PROMPT_LIBRARY_SYSTEM.md` for complete documentation.

## Global LLM Rules

The `.llmrules` file at project root contains global rules that apply to all AI interactions.
