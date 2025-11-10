# OCA Intelligence MCP Server

Model Context Protocol (MCP) server for automated OCA module discovery, documentation, and installation for Odoo 18.0 CE.

## Features

### 8 Tools

1. **search_oca_modules** - Search OCA repositories using gitsearchai.com
2. **generate_module_docs** - Generate documentation via gittodoc.com
3. **check_branch_status** - Monitor 18.0 branch availability
4. **analyze_dependencies** - Module dependency analysis
5. **suggest_alternatives** - Find OCA alternatives for Enterprise modules
6. **validate_compatibility** - Check Odoo 18.0 compatibility
7. **fetch_deepwiki** - Get interactive documentation from DeepWiki
8. **install_module** - Generate installation scripts

### 7 Resources

1. **oca://repositories/all** - Complete OCA repository list
2. **oca://modules/catalog** - Categorized module catalog
3. **oca://guides/installation** - Installation guides
4. **oca://compatibility/matrix** - Compatibility matrix
5. **oca://enterprise/alternatives** - Enterprise alternatives map
6. **oca://finance-ssc/stack** - InsightPulse Finance SSC stack
7. **oca://documentation/index** - Documentation index

### 5 Prompts

1. **module_discovery** - Discover modules for business requirements
2. **installation_workflow** - Generate installation workflows
3. **migration_planning** - Plan Enterprise → CE + OCA migration
4. **troubleshooting** - Debug installation issues
5. **best_practices** - OCA best practices guidance

## Installation

```bash
cd mcp/oca-intel
npm install
npm run build
```

## Usage

### With Claude Code

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "oca-intel": {
      "command": "node",
      "args": ["/Users/tbwa/insightpulse-odoo/mcp/oca-intel/dist/index.js"]
    }
  }
}
```

### Examples

**Search for modules**:
```typescript
use_mcp_tool("oca-intel", "search_oca_modules", {
  query: "accounting reports",
  version: "18.0",
  limit: 5
})
```

**Generate documentation**:
```typescript
use_mcp_tool("oca-intel", "generate_module_docs", {
  repo_url: "https://github.com/OCA/account-financial-reporting",
  branch: "18.0"
})
```

**Find Enterprise alternatives**:
```typescript
use_mcp_tool("oca-intel", "suggest_alternatives", {
  enterprise_module: "documents",
  version: "18.0"
})
```

**Generate installation script**:
```typescript
use_mcp_tool("oca-intel", "install_module", {
  module_names: ["dms", "dms_field", "helpdesk_mgmt"],
  database: "insightpulse",
  auto_deps: true
})
```

## Development

```bash
# Watch mode
npm run watch

# Development mode
npm run dev

# Run tests
npm test

# Lint
npm run lint
```

## Integration with Automation Tools

### gitsearchai.com
- Advanced GitHub repository search
- Semantic code search
- Natural language queries

### gittodoc.com
- Automated documentation generation
- Markdown output
- Repository-wide analysis

### DeepWiki
- Interactive documentation wikis
- Code navigation
- AI-powered explanations

## Project Context

**InsightPulse AI Finance SSC**
- Current Version: Odoo 18.0 CE
- Production: https://erp.insightpulseai.net
- Repository: https://github.com/jgtolentino/insightpulse-odoo

**Cost Savings**: $52.7k/year (Enterprise → CE + OCA)

## License

MIT License - InsightPulse AI Team
