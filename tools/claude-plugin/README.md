# Claude Plugin Bundle

This directory contains all Claude-related tooling, agents, skills, and commands for the InsightPulse Odoo platform.

## Structure

- `.claude-plugin/` - Claude plugin metadata
- `.superclaude/` - Super Claude orchestration system
  - `agents/` - Agent definitions and registry
  - `workflows/` - Workflow orchestrations
  - `shared-context/` - Shared context for multi-agent systems
- `agents/` - Individual agent implementations
  - `odoo-knowledge/` - Odoo knowledge agent
  - `mcp-servers/` - MCP server implementations
- `skills/` - Skills library
  - `core/` - Core skills
  - `integrations/` - Integration skills
  - `proposed/` - Proposed skills
- `commands/` - Claude command definitions
- `anthropic_skills/` - Anthropic-specific skills

## Purpose

This bundle is isolated from the core infrastructure to maintain clean governance:
- `supabase/` remains the canonical deploy surface for DB + Edge Functions
- `runtime/` contains execution scaffolding (Odoo, Supabase wrappers)
- `vendor/` contains external dependencies (Odoo source, OCA repos)
- `addons/` contains custom Odoo modules
- **This directory** (`tools/claude-plugin/`) contains all Claude-related tooling

## Usage

The Claude plugin bundle can be:
1. Used by Claude Code directly for agentic automation
2. Deployed as MCP servers for remote access
3. Integrated into CI/CD workflows via the agents

## Integration Points

- Supabase Edge Functions: via `supabase/functions/`
- Odoo XML-RPC/JSON-RPC: via runtime connectors
- MCP Servers: via `agents/mcp-servers/`
