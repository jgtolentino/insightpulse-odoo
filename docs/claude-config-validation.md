# Claude Configuration Validation Report

**Generated**: Sun Nov  9 10:02:02 UTC 2025
**Repository**: InsightPulse Odoo
**Canonical Source**: /claude.md

---

## Summary

- **Total Errors**: 0
- **Total Warnings**: 3
- **Model Version**: claude-sonnet-4-5-20250929

---

## Validation Results

### Section Structure

✅ No issues found

### MCP Servers

**Warnings:**
- ⚠️  MCP servers in config but NOT in claude.md: {'pulser-hub', 'kubernetes', 'superset', 'docker', 'github', 'digitalocean'}

### Agent Definitions

**Warnings:**
- ⚠️  Agent directory not found: /root/.claude/superclaude/agents/domain

### Skills Inventory

**Warnings:**
- ⚠️  Skill directories exist but not documented in claude.md: {'odoo', 'audit-skill'}

### Interface Hierarchy

✅ No issues found

---

## Recommendations

⚠️  **Warnings detected** - Consider addressing these for better configuration consistency:

1. **Document MCP Servers**: Add missing MCP servers to claude.md Section 17
2. **Document Skills**: Add missing skills to claude.md Section 19
3. **Update Agents**: Sync agent definitions with actual files
