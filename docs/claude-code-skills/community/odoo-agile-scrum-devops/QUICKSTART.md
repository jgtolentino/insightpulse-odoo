# Quick Start Guide: Odoo Agile Scrum DevOps Skill

Get started with your new skill in 5 minutes!

## ✨ What You Just Got

A complete Agile Scrum framework for Odoo development that includes:
- **34KB SKILL.md** - Comprehensive instructions for Claude
- **Sprint Planning Template** - Ready-to-use Finance SSC sprint template
- **Automation Scripts** - Python and Bash scripts for workflow automation
- **CI/CD Pipeline** - Production-ready GitHub Actions workflow

## 🚀 Immediate Next Steps

### Step 1: Install the Skill (Choose Your Method)

#### Method A: Claude.ai (Recommended for most users)
1. Zip this folder: `zip -r odoo-agile-scrum-devops.zip odoo-agile-scrum-devops/`
2. Go to Claude.ai → Settings → Skills
3. Click "Create Skill"
4. Upload the zip file
5. Enable the skill ✅

#### Method B: Claude Code (For developers)
```bash
# Copy to Claude Code skills directory
cp -r odoo-agile-scrum-devops ~/.claude/skills/

# Verify installation
ls ~/.claude/skills/odoo-agile-scrum-devops/
```

#### Method C: API Users
- Upload via Skills API endpoint
- See: https://docs.anthropic.com/en/docs/build-with-claude/agent-skills

### Step 2: Test the Skill

Try these prompts in Claude:

**Test 1: Sprint Planning**
```
Use the odoo-agile-scrum-devops skill to help me plan my next 
2-week sprint. We need to complete BIR Form 1601-C automation 
and October month-end closing for 8 agencies.
```

**Test 2: User Story Creation**
```
Create a user story for automating expense report OCR processing 
with PaddleOCR. Use the Finance SSC template from the skill.
```

**Test 3: CI/CD Setup**
```
Help me set up the GitHub Actions CI/CD pipeline from the skill 
for my Odoo 19 project deploying to DigitalOcean.
```

### Step 3: Customize for Your Environment

Edit these sections in `SKILL.md` to match your setup:

1. **Agency Codes** (lines ~800-900)
   - Update with your actual agency names and TINs
   
2. **DigitalOcean Project ID** (line ~150)
   - Replace with your actual DO project ID
   
3. **Supabase Project ID** (line ~151)
   - Replace with your actual Supabase project reference

4. **Team Capacity** (sprint-planning-template.md)
   - Adjust team size and velocity

## 📋 Your First Sprint (Right Now!)

Let's plan a real sprint together:

### 1. Define Your Sprint Goal
Example: "Automate BIR Form 1601-C generation for all agencies"

### 2. Use the Automation Script

```bash
# Create sprint in your Odoo instance
cd scripts/
python create_sprint.py \
  --url http://your-odoo-url:8069 \
  --db your_database \
  --username admin \
  --password YOUR_PASSWORD \
  --sprint-number 1 \
  --start-date 2025-11-01 \
  --end-date 2025-11-15 \
  --project-name "Your Project Name"
```

This creates:
- ✅ Project in Odoo
- ✅ Sprint milestone
- ✅ 5 default Finance SSC tasks
- ✅ Proper task descriptions with acceptance criteria

### 3. Create Your First Feature Branch

```bash
# Make script executable (first time only)
chmod +x scripts/git_branch.sh

# Create OCA-compliant feature branch
./scripts/git_branch.sh \
  --version 19.0 \
  --type feature \
  --module finance_bir_compliance
```

This creates branch: `19.0-feature-finance_bir_compliance`

### 4. Sync with Notion (Optional)

If you have Notion MCP enabled:

```
Use the odoo-agile-scrum-devops skill to help me sync my 
sprint tasks to Notion. Use the External ID upsert pattern 
to avoid duplicates.
```

Claude will guide you through:
- Fetching your Notion database structure
- Creating tasks with proper field mapping
- Setting up deduplication via External IDs

## 🎯 Common Use Cases

### Use Case 1: Month-End Closing Automation

```
I need to automate our month-end closing process for 8 agencies. 
Use the odoo-agile-scrum-devops skill to create a sprint plan 
with user stories for:
- Bank reconciliation automation
- Trial balance consolidation  
- BIR tax form generation
```

### Use Case 2: CI/CD Pipeline Setup

```
Use the skill to help me set up CI/CD for my odoboo-workspace 
project. Include:
- Pre-commit hooks for OCA standards
- Automated testing
- DigitalOcean deployment
- Sentry error tracking
```

### Use Case 3: OCA Module Development

```
I want to create a new OCA-compliant Odoo module for expense 
OCR processing. Use the skill to guide me through:
- Module structure
- Git workflow
- Testing requirements
- Documentation
```

## 🔧 Troubleshooting

**Skill not loading?**
- Check that SKILL.md has proper YAML frontmatter
- Ensure file is in correct directory
- Restart Claude or refresh session

**Scripts not executable?**
```bash
chmod +x scripts/*.sh
```

**Need more examples?**
- Check `sprint-planning-template.md` for detailed sprint example
- See `SKILL.md` sections 400-600 for code examples
- Review `README.md` for full documentation

## 📚 Next Steps After Setup

1. **Customize Templates**
   - Edit sprint-planning-template.md for your team
   - Adjust story point estimates based on velocity
   - Add your specific BIR compliance requirements

2. **Set Up Infrastructure**
   - Configure GitHub Actions secrets
   - Set up DigitalOcean project
   - Connect Supabase for pgvector

3. **Train Your Team**
   - Share the sprint planning template
   - Review OCA commit conventions
   - Practice with the automation scripts

4. **Start Your First Sprint**
   - Sprint Planning meeting (2 hours)
   - Create tasks using automation
   - Daily standups in Notion
   - Sprint review & retrospective

## 🎓 Learning Resources

**Odoo Development:**
- Official Docs: https://www.odoo.com/documentation/19.0/
- OCA Guidelines: https://github.com/OCA/odoo-community.org

**Agile Scrum:**
- Scrum Guide: https://scrumguides.org/
- Sprint Planning: https://www.scrum.org/resources/what-is-sprint-planning

**DevOps:**
- DORA Metrics: https://dora.dev/
- GitHub Actions: https://docs.github.com/en/actions

## 💡 Pro Tips

1. **Start Small**: Begin with one sprint, learn the workflow, then scale
2. **Use Notion MCP**: Makes task management seamless
3. **Track Metrics**: Monitor DORA metrics from day one
4. **Iterate**: Each retrospective should improve your process
5. **Automate Everything**: Use the scripts, they save hours

## 🆘 Need Help?

If you get stuck:
1. Re-read the relevant section in SKILL.md
2. Check the examples in sprint-planning-template.md
3. Ask Claude to use the skill to help you
4. Review OCA documentation for Odoo specifics

## ✅ Success Checklist

- [ ] Skill installed and tested
- [ ] First sprint created in Odoo
- [ ] Git workflow set up with OCA conventions
- [ ] CI/CD pipeline configured
- [ ] Team trained on Agile Scrum basics
- [ ] First user story written and estimated
- [ ] Sprint planning meeting scheduled
- [ ] Ready to start development! 🚀

---

**You're all set!** 🎉

Your skill is now ready to help you master Agile Scrum Odoo DevOps workflows. Start by planning your first sprint and let Claude guide you through the process using this skill.

**Remember:** The skill knows all about your Finance SSC workflows, 8 agencies, BIR compliance requirements, and OCA standards. Just ask Claude to use the skill whenever you need guidance!
