# Claude Code Web Skills Setup

## Problem

Custom agent Skills were available in local Claude Code, claude.ai web chat, and Claude desktop app, but were **not accessible** in Claude Code web sessions (https://claude.ai/code). This created an inconsistent experience where the same Skills worked in some environments but not in the cloud-based code editor.

## Root Cause

Claude Code discovers Skills by looking for `SKILL.md` files in the `.claude/skills/` directory. In this repository:

- Skills were defined in `docs/claude-code-skills/` for documentation purposes
- The `.claude/skills/` directory didn't exist
- Claude Code web sessions couldn't discover the Skills

## Solution

Create a symlink-based infrastructure that:

1. Links all Skills from `docs/claude-code-skills/` to `.claude/skills/`
2. Commits the symlinks to Git (Git tracks symlinks natively)
3. Adds a SessionStart hook as redundancy to recreate symlinks if needed

### Implementation

#### 1. Created `.claude/skills/` Directory Structure

```bash
mkdir -p .claude/skills
```

#### 2. Created Symlink Script (`link_skills.sh`)

```bash
#!/bin/bash

# Create symlinks for all Skills in .claude/skills/
find docs/claude-code-skills -name "SKILL.md" -exec dirname {} \; | while read skill_dir; do
  skill_name=$(basename "$skill_dir")
  ln -sf "../../$skill_dir" ".claude/skills/$skill_name"
  echo "Linked: $skill_name"
done

echo "Done! All skills linked to .claude/skills/"
```

#### 3. Created `.claude/settings.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR\"/link_skills.sh"
          }
        ]
      }
    ]
  }
}
```

This ensures that when a new Claude Code web session starts, the symlinks are automatically created if they're missing.

#### 4. Updated `.gitignore`

```gitignore
# Claude Code
.claude/settings.local.json
```

This excludes local-only settings while committing the shared `settings.json`.

## Skills Enabled

### Total: 43 Skills (20 Original + 23 Community)

#### Custom Odoo Skills (6)
- **odoo19-oca-devops**: Odoo 19 ERP development with OCA modules, DevOps deployment
- **odoo-agile-scrum-devops**: Agile/Scrum workflows for Odoo development
- **odoo-app-automator-final**: Automated Odoo app scaffolding
- **odoo-finance-automation**: Financial process automation
- **odoo-knowledge-agent**: AI-powered knowledge management
- **bir-tax-filing**: BIR tax compliance for Philippines

#### Document Processing Skills (4)
- **pdf**: PDF document processing
- **docx**: Word document processing
- **xlsx**: Excel spreadsheet processing
- **pptx**: PowerPoint presentation processing

#### Superset BI Skills (4)
- **superset-chart-builder**: Interactive chart creation
- **superset-dashboard-automation**: Automated dashboard generation
- **superset-dashboard-designer**: Dashboard design patterns
- **superset-sql-developer**: SQL dataset development

#### Project Management Skills (3)
- **pmbok-project-management**: PMBOK-compliant PM practices
- **procurement-sourcing**: Strategic sourcing workflows
- **project-portfolio-management**: Multi-project portfolio management

#### Integration & Automation Skills (5)
- **firecrawl-data-extraction**: Web scraping with Firecrawl
- **insightpulse_connection_manager**: Connection management for InsightPulse
- **mcp-complete-guide**: Complete MCP server development guide
- **multi-agency-orchestrator**: Multi-agent workflow orchestration
- **supabase-rpc-manager**: Supabase RPC function management

#### Utilities & Tools (6)
- **drawio-diagrams-enhanced**: Enhanced diagram generation
- **librarian-indexer**: Code/doc indexing and search
- **notion-workflow-sync**: Notion workspace synchronization
- **paddle-ocr-validation**: PaddleOCR receipt validation
- **reddit-product-viability**: Product validation via Reddit
- **travel-expense-management**: Travel/expense tracking

#### Notion Integration Skills (4)
- **notion-meeting-intelligence**: Meeting notes and action item extraction
- **notion-knowledge-capture**: Knowledge base creation from conversations
- **notion-research-documentation**: Research documentation workflows
- **notion-spec-to-implementation**: Convert specifications to implementation

#### Anthropic Official Skills (11)
- **algorithmic-art**: Generate algorithmic art and visualizations
- **artifacts-builder**: Build interactive artifacts
- **brand-guidelines**: Apply brand guidelines to designs
- **canvas-design**: Design canvas layouts
- **internal-comms**: Internal communications templates
- **mcp-builder**: Model Context Protocol server builder
- **skill-creator**: Create new Skills
- **slack-gif-creator**: Create GIFs for Slack
- **template-skill**: Template for new Skills
- **theme-factory**: Generate UI themes
- **webapp-testing**: Web application testing patterns

## How It Works

### On Repository Clone

1. Git clones the repository including all symlinks in `.claude/skills/`
2. Claude Code discovers the Skills immediately
3. SessionStart hook runs `link_skills.sh` as redundancy (recreates symlinks)
4. Skills are loaded and available for use

### Symlink Structure

```
.claude/skills/
├── odoo -> ../../docs/claude-code-skills/odoo
├── pdf -> ../../docs/claude-code-skills/anthropic-official/document-skills/pdf
├── docx -> ../../docs/claude-code-skills/anthropic-official/document-skills/docx
├── xlsx -> ../../docs/claude-code-skills/anthropic-official/document-skills/xlsx
├── pptx -> ../../docs/claude-code-skills/anthropic-official/document-skills/pptx
├── notion-meeting-intelligence -> ../../docs/claude-code-skills/notion/notion-meeting-intelligence
├── notion-knowledge-capture -> ../../docs/claude-code-skills/notion/notion-knowledge-capture
├── notion-research-documentation -> ../../docs/claude-code-skills/notion/notion-research-documentation
├── notion-spec-to-implementation -> ../../docs/claude-code-skills/notion/notion-spec-to-implementation
├── algorithmic-art -> ../../docs/claude-code-skills/anthropic-official/algorithmic-art
├── artifacts-builder -> ../../docs/claude-code-skills/anthropic-official/artifacts-builder
├── brand-guidelines -> ../../docs/claude-code-skills/anthropic-official/brand-guidelines
├── canvas-design -> ../../docs/claude-code-skills/anthropic-official/canvas-design
├── internal-comms -> ../../docs/claude-code-skills/anthropic-official/internal-comms
├── mcp-builder -> ../../docs/claude-code-skills/anthropic-official/mcp-builder
├── skill-creator -> ../../docs/claude-code-skills/anthropic-official/skill-creator
├── slack-gif-creator -> ../../docs/claude-code-skills/anthropic-official/slack-gif-creator
├── template-skill -> ../../docs/claude-code-skills/anthropic-official/template-skill
├── theme-factory -> ../../docs/claude-code-skills/anthropic-official/theme-factory
└── webapp-testing -> ../../docs/claude-code-skills/anthropic-official/webapp-testing
```

## Benefits

### 1. **Single Source of Truth**
- Skills are defined once in `docs/claude-code-skills/`
- Symlinks point to the canonical definitions
- No duplication or sync issues

### 2. **Works Across Environments**
- Local Claude Code: ✅ Discovers Skills in `.claude/skills/`
- claude.ai web: ✅ (already had Skills access)
- Claude desktop: ✅ (already had Skills access)
- **Claude Code web**: ✅ **Now works!**

### 3. **Automatic on Fresh Clones**
- Git tracks symlinks natively
- No manual setup required
- SessionStart hook provides redundancy

### 4. **Easy to Add New Skills**

```bash
# 1. Create skill in docs/claude-code-skills/
mkdir -p docs/claude-code-skills/my-new-skill
cat > docs/claude-code-skills/my-new-skill/SKILL.md <<EOF
---
name: my-new-skill
description: Description of what this skill does
---

# Instructions for the skill
EOF

# 2. Run link script
./link_skills.sh

# 3. Commit
git add docs/claude-code-skills/my-new-skill .claude/skills/my-new-skill
git commit -m "feat: add my-new-skill"
git push
```

## Verification

### Check Skills Are Available

In a new Claude Code web session:

```bash
# List available skills
ls -la .claude/skills/

# Count skills
ls .claude/skills/ | wc -l
# Expected output: 43

# Verify symlinks are valid
for skill in .claude/skills/*; do
  if [ -f "$skill/SKILL.md" ]; then
    echo "✅ $(basename $skill)"
  else
    echo "❌ $(basename $skill) - broken symlink"
  fi
done
```

### Invoke a Skill

In the Claude Code chat, you can now invoke Skills:

```
/skill odoo19-oca-devops
/skill pdf
/skill notion-meeting-intelligence
```

Or Claude will automatically suggest Skills when relevant to your task.

## Troubleshooting

### Problem: Skills Not Available in New Session

**Solution**: Run the symlink script manually:
```bash
./link_skills.sh
```

### Problem: Broken Symlinks

**Cause**: Skill definitions were moved or deleted from `docs/claude-code-skills/`

**Solution**:
1. Restore the skill definition, or
2. Remove the broken symlink:
   ```bash
   rm .claude/skills/broken-skill-name
   ```

### Problem: SessionStart Hook Not Running

**Cause**: `settings.json` might not be loaded properly

**Solution**:
1. Check `.claude/settings.json` exists
2. Verify JSON syntax is valid
3. Manually run the script: `./link_skills.sh`

### Problem: Permission Denied on `link_skills.sh`

**Solution**: Make the script executable:
```bash
chmod +x link_skills.sh
```

## Technical Details

### Git Symlink Handling

Git stores symlinks as a special file type (mode `120000`). When you clone the repository:
- Git recreates the symlinks pointing to their targets
- Symlinks work on Linux, macOS, and Windows (with Developer Mode enabled)

### SessionStart Hook

The hook in `settings.json` runs when Claude Code web session initializes:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR\"/link_skills.sh"
          }
        ]
      }
    ]
  }
}
```

`$CLAUDE_PROJECT_DIR` is an environment variable set by Claude Code pointing to the repository root.

### Why Symlinks Instead of Copying?

**Symlinks**:
- ✅ Single source of truth
- ✅ Changes propagate automatically
- ✅ No duplication
- ✅ Smaller repository size

**Copying**:
- ❌ Risk of files getting out of sync
- ❌ Duplication increases repository size
- ❌ Need to remember to copy after edits

## References

- [Agent Skills Spec](../docs/claude-code-skills/anthropic-official/agent_skills_spec.md)
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Claude Code on the Web](https://docs.claude.com/en/docs/claude-code/claude-code-on-the-web)

## Version History

- **2025-11-03**:
  - Initial setup enabling 20 Skills for Claude Code web sessions (commit `431a54bf`)
  - Integrated 23 community Skills from odoomation package (commit `385bcb4a`)
  - **Total**: 43 Skills now available
- **Branch**: `claude/claude-code-web-skills-011CUkaUKPzzjEb5uyLr1tD9`

## Maintainers

- InsightPulse Team
- GitHub: jgtolentino/insightpulse-odoo

---

**Status**: ✅ **SOLVED** - Skills now work in Claude Code web sessions!
