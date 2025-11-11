# CLAUDE.md

## 🧠 InsightPulse AI - Claude Project Memory

This project is part of the InsightPulse AI enterprise automation stack.
It is structured as a multi-agent orchestration platform built over:
- Odoo CE 18+ with OCA modules
- Supabase (PostgreSQL + Vector Store)
- Apache Superset
- Claude-compatible agents, skills, and CI pipelines

### 📁 Memory Components
- Agent Registry: `agents/REGISTRY.yaml`
- Skills Index: `agents/skills.yaml`
- MCP Servers: `mcp/servers/*.json` (optional)
- Claude Skill Profiles: defined in `agents/skills.yaml` and callable via `run_skill.py`
- Vendor Skills: `vendor/anthropic_skills/` + others

### 🔐 Permission Model
Claude Code has write access only to:
- Agents and skills definitions
- `docs/`, `.claude/`, `CLAUDE.md`, and workflows
- PR suggestions and planning templates

Claude Code **cannot**:
- Push directly to `main`
- Access `.env` or secrets
- Execute system-level scripts (must go through MCP or executor agent)

### 🧭 Active Profiles
- `superclaude.dev` (Agent Editor)
- `mcp.coordinator` (runtime config planner)
- `skills.validator` (CI lint/review)

### 🧩 Projects Using This Memory
- Claude Code Desktop/CLI
- MCP Desktop Planner
- GitHub Action CI bots (`claude-code-pr-review.yml`)
