# InsightPulse AI - Agent Skills System

## Quick Start

```bash
# List all skills
python3 -m agents.run_skill --list

# Run a skill
python3 -m agents.run_skill odoo.manifest.validate --repo-path .

# Run a profile
python3 -m agents.run_skill --profile fast_check --repo-path .
```

## What's Inside

This directory contains the InsightPulse AI agent skills system:

### Core Components

- **skill_registry.py** - Unified skill loader (native + Anthropic skills)
- **run_skill.py** - CLI executor for skills and profiles
- **skills.yaml** - Native skills registry with RAG configuration
- **mcp_skill_server.py** - MCP server integration for Claude

### Docker & CI

- **Dockerfile.skills** - Docker image for skills runner
- **docker-compose.skills.yml** - Compose services for local testing and CI
- **mcp_config.example.json** - Example MCP configuration

### Integration

The skills system is integrated with:

- ✅ **GitHub Actions** - 3 workflows (fast-check, full-compliance, rag-compliance)
- ✅ **Docker** - Containerized runner for CI/CD
- ✅ **MCP** - Model Context Protocol server for Claude integration
- ✅ **Anthropic Skills** - External skills from anthropics/skills repo

## Architecture

```
┌─────────────────────────────────────────────────┐
│          InsightPulse AI Skills System          │
└─────────────────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
   ┌────▼────┐              ┌──────▼──────┐
   │ Native  │              │ Anthropic   │
   │ Skills  │              │   Skills    │
   │ (YAML)  │              │ (SKILL.md)  │
   └────┬────┘              └──────┬──────┘
        │                           │
        └─────────────┬─────────────┘
                      │
              ┌───────▼────────┐
              │ Skill Registry │
              │  (Unified)     │
              └───────┬────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
   │   CLI   │  │   CI    │  │   MCP   │
   │ Runner  │  │ Pipelines│ │ Server  │
   └─────────┘  └─────────┘  └─────────┘
```

## Skills Count

- **Native Skills**: 11 (OCA compliance, RAG-enhanced validators)
- **Anthropic Skills**: 11 (document creation, design, development)
- **Total Skills**: 22
- **Profiles**: 8

## Documentation

Full documentation available at: [docs/AGENT_SKILLS.md](../docs/AGENT_SKILLS.md)

## Quick Links

- 📖 [Full Documentation](../docs/AGENT_SKILLS.md)
- 🐳 [Docker Setup](./docker-compose.skills.yml)
- 🔧 [MCP Configuration](./mcp_config.example.json)
- 🔄 [GitHub Actions](../.github/workflows/)
- 🧠 [Anthropic Skills](../anthropic_skills/)

---

**Maintained by:** InsightPulse AI Team
**Version:** 1.0.0
**Last Updated:** 2025-11-11
