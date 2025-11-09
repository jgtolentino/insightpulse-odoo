# Claude Configuration Validation Report

**Generated**: Sun Nov  9 09:58:49 UTC 2025
**Repository**: InsightPulse Odoo
**Canonical Source**: /claude.md

---

## Summary

- **Total Errors**: 3
- **Model Version**: claude-sonnet-4-5-20250929

---

## Validation Results

### Section Structure

✅ No issues found

### MCP Servers

❌ MCP servers in config but NOT in claude.md: {'superset', 'kubernetes', 'github', 'digitalocean', 'pulser-hub', 'docker'}

### Agent Definitions

❌ Agent directory not found: /root/.claude/superclaude/agents/domain

### Skills Inventory

❌ Skill directories exist but not documented in claude.md: {'audit-skill', 'odoo'}

### Interface Hierarchy

✅ No issues found

---

## Recommendations

1. **Fix Configuration Drift**: Sync configurations across interface files
2. **Update Documentation**: Ensure all sections are documented in claude.md
3. **Validate Files**: Check that all referenced files exist
4. **Run Sync Script**: Execute `scripts/sync-claude-configs.sh`
