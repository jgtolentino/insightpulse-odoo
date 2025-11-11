# Repository Archiving Strategy

## Overview

This document outlines the strategy for archiving old repositories that have been consolidated into the `insightpulse-odoo` monorepo.

## Benefits of Archiving

1. **Read-Only Protection**: Archived repositories are frozen - no new commits, PRs, or issues can be created
2. **Workspace Organization**: Archived repos are hidden from the main list, making your active projects clear
3. **History Preservation**: All code, commits, issues, and PRs remain accessible forever
4. **Reversible**: Archiving can be undone if needed

## Archiving Categories

### ✅ Keep Active

**Strategic Repositories**:
- `insightpulse-odoo` - Main Odoo 19.0 monorepo (consolidated)
- `superclaude-designer` - Active SuperClaude development
- `scout-analytics-prod` - Production Scout analytics

**Infrastructure & Tools**:
- `ai-aas-hardened-lakehouse` - Active infrastructure
- `render-mcp-bridge` - MCP bridge development
- `openai-ui` - Active UI project
- `Scout-Dashboard` - Active dashboard

### 🗂️ Archive Immediately

**Old Odoo Repositories** (consolidated into insightpulse-odoo):
- `ipai-odoo` - Old Odoo project
- `finance-automation` - Consolidated into monorepo
- `odoobo-fin-ops` - Old FinOps module
- `odoo-erp` - Old ERP fork
- `odoobo-backend-repo` - Old backend
- `odoobo-ocean` - Old DigitalOcean config
- `odoboo-workspace` - Old workspace
- `oca` - OCA fork (use official OCA repos)
- `odoo-spark-generator` - Old generator tool

**Old Notion Experiments**:
- `next-notion-supabase` - Notion integration experiment
- `react-notion-x` - Notion library fork
- `nextjs-notion-starter-kit` - Starter kit fork
- `notion-clone` - Notion clone experiment
- `notion` - Old Notion integration

**Old Rate Card Projects** (if consolidated):
- `rate-inquiry---approval-system` - Old rate system
- `rate-card` - Old rate card
- `rate-card-729` - Duplicate rate card

**Test/Duplicate Repositories**:
- `odoo-spark-generator` - If no longer used
- Any repositories with "test", "v1", "old" in the name

### 🤔 Review Before Archiving

**Scout-Related** (assess if still needed):
- `scout-agentic-analytics` - Last push Sep 29
- `apps-scout-dashboard` - Last push Sep 22
- `scout-dashboard-clean` - Last push Sep 17
- `scout-v7` - Last push Sep 12
- `scout-analytics-clean` - Last push Aug 5
- `tbwa-scout-dashboard` - Last push Aug 5

**Agency/Brand Projects** (if completed):
- `tbwa-agency-databank` - Last push Sep 23
- `tbwa-lions-palette-forge` - Last push Sep 8
- `amazing-awards` - Last push Sep 13

**Old Expense/SpendFlow** (if consolidated):
- `concur-ui-revive` - Last push Oct 9
- `app-expense` - Last push Oct 9
- `tbwa-concur-expense-app` - Last push Oct 9
- `ios-expense` - Last push Oct 9
- `SpendFlow-Web` - Last push Oct 9
- `spendflow-db` - Last push Oct 9
- `concur-buddy` - Last push Oct 7
- `mobile-expense---ca-app` - Last push Aug 21

**SUQI-Related** (assess consolidation):
- `suqi-agentic-ai` - Last push Oct 27
- `suqi-public` - Last push Sep 16
- `suqi-analytics` - Last push Sep 16
- `suqi-agentic-db` - Last push Sep 14
- `agentic-suqi` - Last push Sep 13
- `ai-agentic-analytics` - Last push Sep 13
- `suqi-ai` - Last push Sep 7
- Multiple older SUQI repositories

**Old Analytics/Dashboard Experiments**:
- `scout-suqi-ship` - Last push Aug 19
- `Scout-Analytics-Dashboard-Suqi` - Last push Aug 17
- `edge-suqi-pie` - Last push Aug 14
- `suqi-face` - Last push Aug 13
- `chartvision` - Last push Aug 11
- `Suqi-Supa-db` - Last push Aug 11
- `supa-love` - Last push Aug 10
- `supa-love-db` - Last push Aug 11
- `gen-bi-nw` - Last push Aug 7
- `tab-ai` - Last push Aug 6
- `suqi-gen-bi` - Last push Aug 5
- `tableau-insight-ai` - Last push Aug 5
- `pulser-ai-bi` - Last push Aug 5
- `suqi-ai-db` - Last push Aug 4
- `suqi-ai-dashboard-` - Last push Aug 4
- `geographic-dashboard` - Last push Aug 4

### 💼 Business Decision Required

**Agency Work** (check with stakeholders):
- `w9-studios-landing-page` - Last push Oct 3
- `w9-coming-soon` - Last push Oct 2
- `W9-landing` - Last push Oct 2
- `w9studio` - Last push Oct 2
- `ai-studios-landing-page` - Last push Oct 1
- `auto-brand` - Last push Oct 1

**Platform/Product Projects**:
- `pulser-ai-platform` - Last push Oct 27
- `agents-pulser` - Last push Oct 1
- `ask-ces` - Last push Oct 27
- `hris-fs-ai-central-hub` - Last push Oct 5
- `insightpulse-app` - Last push Oct 4

**Forks/External**:
- `ai-foundry-docs` - Microsoft fork, last push Oct 20
- `superset` - Superset fork, last push Nov 3
- `odoo` - Official Odoo fork, last push Nov 10
- `material-ui` - Material UI fork, last push Oct 9

## Execution Process

### Step 1: Dry Run
```bash
cd /Users/tbwa/Documents/GitHub/insightpulse-odoo
./scripts/archive-old-repos.sh
```

This will show you what would be archived without making changes.

### Step 2: Review Output
Review the list and verify you want to archive these repositories.

### Step 3: Execute
```bash
./scripts/archive-old-repos.sh --execute
```

This will actually archive the repositories.

### Step 4: Manual Archiving (if needed)
For repositories not in the script, manually archive via GitHub:

1. Go to repository settings
2. Scroll to "Danger Zone"
3. Click "Archive this repository"
4. Confirm the action

## Post-Archiving Checklist

- [ ] Update README in active repositories to note migration to monorepo
- [ ] Update any documentation referencing archived repos
- [ ] Notify team members about archived repositories
- [ ] Update CI/CD pipelines that reference archived repos
- [ ] Review and update local git remotes if needed

## Unarchiving (if needed)

To unarchive a repository:
```bash
gh repo unarchive <owner>/<repo>
```

Or via GitHub UI:
1. Go to archived repository
2. Settings → Danger Zone
3. Click "Unarchive this repository"

## Recommended Timeline

1. **Week 1**: Archive obvious old/duplicate repositories
2. **Week 2**: Review Scout-related repositories, consolidate if needed
3. **Week 3**: Review SUQI repositories, consolidate if needed
4. **Week 4**: Review agency/business repositories, get stakeholder approval
5. **Ongoing**: Archive any new experimental repos after 90 days of inactivity

## Archive Reason Matrix

| Repository Type | Reason | Safe to Archive |
|----------------|---------|-----------------|
| Duplicate | Multiple copies exist | ✅ Yes |
| Consolidated | Moved to monorepo | ✅ Yes |
| Experimental | Proof of concept done | ✅ Yes |
| Fork | Using official version | ✅ Yes |
| Old Version | Superseded by new | ✅ Yes |
| Active | Recent commits | ❌ No |
| Unknown | Unclear purpose | ⚠️ Review |

## Questions Before Archiving

For each repository, ask:

1. **Is this code used anywhere?** (Check CI/CD, documentation, dependencies)
2. **Does anyone else depend on this?** (Team members, external users)
3. **Is there unique code not backed up elsewhere?** (Not in monorepo)
4. **Could this be needed for reference?** (Historical patterns, decisions)
5. **Is this a fork with custom changes?** (Might need to preserve modifications)

If all answers are "No", it's safe to archive.

## Communication Template

When notifying about archiving:

> **Repository Archiving Notice**
>
> We are archiving the following repositories as part of our consolidation to the `insightpulse-odoo` monorepo:
>
> - [List repositories]
>
> **What this means:**
> - Repositories are now read-only (no new commits/PRs/issues)
> - All history remains accessible
> - Can be unarchived if needed
>
> **New primary repository:**
> - https://github.com/jgtolentino/insightpulse-odoo
>
> Questions? Contact [maintainer]

## Metrics & Success Criteria

- **Before**: 100+ active repositories (hard to navigate)
- **Target**: <20 active repositories (clear focus)
- **Success**: Team can easily find active projects
- **Validation**: No accidental work on archived repos

## References

- [GitHub Archiving Documentation](https://docs.github.com/en/repositories/archiving-a-github-repository)
- [insightpulse-odoo Consolidation Plan](./CONSOLIDATION.md)
- [Repository Organization Strategy](./REPOSITORY_STRATEGY.md)
