# Installation Guide - Odoomation Skills Package

## 📦 What You're Installing

This package contains **19 specialized skills** that transform your ChatGPT into a complete Finance SSC automation assistant capable of building the Odoomation MVP.

**Total Package Size**: ~590KB  
**Number of Files**: 19 SKILL.md files + documentation  
**Estimated Setup Time**: 10-15 minutes

---

## 🚀 Step-by-Step Installation

### Step 1: Extract the ZIP File

1. Download `odoomation-skills.zip`
2. Extract to a folder on your computer
3. You should see this structure:
   ```
   odoomation-skills/
   ├── README.md
   ├── GPT-SYSTEM-PROMPT.md
   ├── MANIFEST.json
   ├── QUICK-REFERENCE.md
   ├── INSTALL.md (this file)
   └── skills/
       ├── odoo-agile-scrum-devops/
       ├── odoo-finance-automation/
       └── ... (17 more skills)
   ```

### Step 2: Access Your GPT Configuration

1. Go to [ChatGPT](https://chat.openai.com/)
2. Click your profile (bottom left)
3. Select **"My GPTs"**
4. Click **"Create a GPT"** or edit your existing "Skill Synthesizer" GPT
5. Switch to **"Configure"** tab

### Step 3: Set GPT Name and Description

**Name:**
```
Skill Synthesizer
```

**Description:**
```
Integrate Skills packs into DO starters; secure endpoints; generate OpenAPI+patches.
```

**Instructions:**
- Copy the ENTIRE contents of `GPT-SYSTEM-PROMPT.md`
- Paste into the "Instructions" field
- This is approximately 800 lines of detailed instructions

### Step 4: Upload Skills to Knowledge Base

1. Scroll down to the **"Knowledge"** section
2. Click **"Upload files"**
3. Navigate to `odoomation-skills/skills/`
4. **Select ALL 19 SKILL.md files** (use Ctrl+A or Cmd+A)

**Files to upload:**
```
✓ odoo-agile-scrum-devops/SKILL.md
✓ odoo-finance-automation/SKILL.md
✓ travel-expense-management/SKILL.md
✓ superset-dashboard-automation/SKILL.md
✓ notion-workflow-sync/SKILL.md
✓ multi-agency-orchestrator/SKILL.md
✓ supabase-rpc-manager/SKILL.md
✓ paddle-ocr-validation/SKILL.md
✓ procurement-sourcing/SKILL.md
✓ project-portfolio-management/SKILL.md
✓ odoo19-oca-devops/SKILL.md
✓ superset-chart-builder/SKILL.md
✓ superset-dashboard-designer/SKILL.md
✓ superset-sql-developer/SKILL.md
✓ pmbok-project-management/SKILL.md
✓ drawio-diagrams-enhanced/SKILL.md
✓ mcp-complete-guide/SKILL.md
✓ librarian-indexer/SKILL.md
✓ skill-creator/SKILL.md
```

5. Wait for uploads to complete (may take 2-3 minutes)
6. You should see all 19 files listed in the Knowledge section

### Step 5: Configure Conversation Starters

Add these 8 conversation starters to help users get started:

```
1. Add /skills and /skills/trigger to this starter.
```

```
2. Wire MCP_URL and secure endpoints with SKILLS_API_TOKEN.
```

```
3. Scan .claude/skills and build index.json.
```

```
4. Generate a Git OpenAPI 3.1 spec mapped to MCP tools.
```

```
5. Produce .do/app.yaml and minimal FastAPI endpoints.
```

```
6. Create a Finance SSC automation system for 8 agencies.
```

```
7. Generate Superset dashboard for BIR compliance.
```

```
8. Build Odoo 19 module with OCA dependencies.
```

### Step 6: Configure Capabilities

Enable these capabilities:

- ✅ **Web Browsing**: OFF (not needed for code generation)
- ✅ **DALL·E Image Generation**: OFF (not needed)
- ✅ **Code Interpreter**: ON (helpful for testing patterns)

### Step 7: Set GPT Settings

**Profile Picture**: (Optional) Upload an icon representing automation/ERP

**Category**: Select **"Programming"**

**Sharing**: 
- **Private** (only you can use) OR
- **Anyone with the link** (if sharing with team)

### Step 8: Save and Test

1. Click **"Save"** in the top-right
2. Click **"View GPT"** to test
3. Try a test prompt:
   ```
   Create a simple Odoo module for tracking expenses
   ```
4. GPT should:
   - Read the relevant skills
   - Generate a complete module structure
   - Include all OCA-compliant files
   - Provide proper documentation

---

## ✅ Verification Checklist

After installation, verify everything is working:

### ✓ Basic Tests

- [ ] GPT responds to conversation starters
- [ ] GPT mentions "reading skill" when generating code
- [ ] GPT produces OCA-compliant Odoo modules
- [ ] GPT generates proper docker-compose.yml files
- [ ] GPT creates Superset SQL queries

### ✓ Skill Loading Tests

Ask these questions and verify GPT reads the right skills:

1. **"Create month-end closing module"**
   - Should read: `odoo-finance-automation`
   
2. **"Build Superset dashboard"**
   - Should read: `superset-dashboard-automation`
   
3. **"Set up expense management"**
   - Should read: `travel-expense-management`
   
4. **"Deploy to DigitalOcean"**
   - Should read: `odoo19-oca-devops`

### ✓ Output Quality Tests

Generated code should have:

- [ ] Proper file structure
- [ ] License headers (LGPL-3 for Odoo)
- [ ] Complete documentation
- [ ] Unit tests (when applicable)
- [ ] BIR compliance notes (for finance modules)
- [ ] Agency codes (RIM, CKVC, etc.)

---

## 🔧 Troubleshooting

### Problem: GPT doesn't mention skills

**Solution**: 
1. Check that GPT-SYSTEM-PROMPT.md was fully copied to Instructions
2. Verify all 19 SKILL.md files are uploaded to Knowledge
3. Try rephrasing your request to be more specific

### Problem: GPT generates incomplete code

**Solution**:
1. Ask GPT to "read the [skill-name] skill first"
2. Request "complete implementation with all files"
3. Specify "OCA-compliant" for Odoo modules

### Problem: Upload fails

**Solution**:
1. Ensure SKILL.md files are under 20MB each
2. Try uploading in smaller batches (5 at a time)
3. Check your ChatGPT Plus subscription is active

### Problem: GPT ignores skill guidelines

**Solution**:
1. Re-upload the specific SKILL.md file
2. Explicitly mention the skill name in your prompt
3. Check Instructions field has complete system prompt

---

## 🎓 Learning the System

### Start with Simple Requests

Begin with basic requests to learn how the system works:

**Easy:**
```
Create a simple Odoo model for tracking tasks
```

**Medium:**
```
Build a month-end closing wizard with checklist
```

**Advanced:**
```
Create complete expense management system with OCR and dashboard
```

### Understand Multi-Skill Synthesis

For complex requests, GPT will:
1. Identify relevant skills (2-5 skills)
2. Read each SKILL.md file
3. Extract patterns from each
4. Synthesize a unified solution
5. Generate complete implementation

Example:
```
User: "Create expense system with Superset dashboard"

GPT Process:
1. Reads: travel-expense-management
2. Reads: paddle-ocr-validation
3. Reads: superset-dashboard-automation
4. Reads: odoo19-oca-devops
5. Synthesizes: Complete system with all components
```

### Review Generated Code

Always review GPT's output:
- Check OCA compliance
- Verify BIR requirements
- Test locally before deploying
- Validate security configurations

---

## 📚 Additional Resources

### Essential Documents

Keep these handy:
- **QUICK-REFERENCE.md** - Command cheat sheet
- **MANIFEST.json** - Skills catalog
- **README.md** - Complete documentation

### External Links

- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- [OCA Guidelines](https://github.com/OCA/maintainer-tools)
- [Superset Docs](https://superset.apache.org/docs/)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)

---

## 🆘 Getting Help

### If Something Goes Wrong

1. **Check Installation**: Verify all steps completed
2. **Review Logs**: Look at GPT's response for errors
3. **Test Individually**: Try each skill separately
4. **Re-upload**: Delete and re-upload problematic skill files
5. **Restart GPT**: Save and reload the GPT configuration

### Common Issues

**Issue**: "I can't find the skill file"  
**Fix**: Re-upload the specific SKILL.md to Knowledge

**Issue**: "Code doesn't follow OCA standards"  
**Fix**: Add "must be OCA-compliant" to your request

**Issue**: "Missing BIR compliance"  
**Fix**: Specify "include BIR Form [number]" in request

---

## 🎯 Next Steps

After successful installation:

1. **Print QUICK-REFERENCE.md** for easy access
2. **Bookmark this GPT** in your ChatGPT sidebar
3. **Try the conversation starters** to get familiar
4. **Start building** the Odoomation MVP!

### Your First Task

Try this to test the complete system:

```
Create a simple expense report module for Odoo 19 that:
1. Follows OCA standards
2. Includes receipt model
3. Has approval workflow
4. Supports RIM, CKVC, BOM agencies
5. Includes unit tests
6. Has proper documentation
```

GPT should generate a complete, production-ready module!

---

## ✨ Success!

You've successfully installed the Odoomation Skills Package! 

Your GPT can now:
✅ Generate OCA-compliant Odoo modules  
✅ Create Apache Superset dashboards  
✅ Build complete deployment configs  
✅ Implement BIR compliance automation  
✅ Integrate with Notion, Supabase, and more  
✅ Save $27,500/year in SaaS costs  

**Ready to build the Odoomation MVP!** 🚀

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-03  
**Support**: Check skill-specific SKILL.md files for detailed guidance
