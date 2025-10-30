# Continue CLI Configuration for InsightPulse Odoo

This directory contains Continue CLI configuration and prompts for automated Odoo module generation.

## 📁 Directory Structure

```
.continue/
├── README.md (this file)
├── config.example.json     # Example Continue CLI config (copy to ~/.continue/config.json)
└── prompts/                # Custom prompts for module generation
    ├── odoo-developer.md           # Main Odoo module developer prompt
    ├── travel-expense-generator.md # Travel expense module template
    └── finance-ssc-generator.md    # Finance SSC module template
```

## 🚀 Quick Setup

### 1. Install Continue CLI

```bash
npm i -g @continuedev/cli
```

### 2. Configure Continue CLI

```bash
# Create config directory
mkdir -p ~/.continue/prompts

# Copy example config
cp .continue/config.example.json ~/.continue/config.json

# Edit config and add your API keys
nano ~/.continue/config.json
```

**Required API Keys:**
- `NOTION_API_KEY` - Get from https://www.notion.so/my-integrations
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com

### 3. Copy Prompts

```bash
# Copy all prompts to Continue config
cp .continue/prompts/* ~/.continue/prompts/

# Verify
ls ~/.continue/prompts/
```

### 4. Test Connection

```bash
# Test Notion MCP
cn "List all databases I have access to in Notion"

# Should output your Notion databases
```

## 📝 Available Prompts

### 1. odoo-developer.md
**Main prompt for generating OCA-compliant Odoo modules**

**Use for:**
- General Odoo module development
- Following OCA guidelines
- Standard module structure

**Usage:**
```bash
cn -p "odoo-developer" "Create an expense tracking module with OCR support"
```

**Features:**
- ✅ OCA compliance
- ✅ Complete module structure
- ✅ Security rules
- ✅ Tests (80% coverage)
- ✅ Documentation

---

### 2. travel-expense-generator.md
**Specialized prompt for Travel & Expense Management (SAP Concur alternative)**

**Use for:**
- Travel request workflows
- Expense report submission
- Receipt OCR integration
- BIR compliance (Philippines)
- Policy validation

**Usage:**
```bash
cn -p "travel-expense-generator"
```

**Generated Module:** `ipai_travel_expense`

**Features:**
- Travel authorization workflow
- Multi-level approval matrix
- PaddleOCR integration for receipts
- Per diem calculation
- GL posting integration
- BIR Form 1604-CF generation

---

### 3. finance-ssc-generator.md
**Comprehensive prompt for Finance Shared Service Center automation**

**Use for:**
- Multi-agency operations (8 agencies)
- Month-end closing workflows
- BIR compliance (1601-C, 1702-RT, 2550Q)
- Inter-company eliminations
- Consolidated reporting

**Usage:**
```bash
cn -p "finance-ssc-generator"
```

**Generated Module:** `ipai_finance_ssc`

**Features:**
- 8-agency support (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- Automated month-end closing
- BIR form generation
- Bank reconciliation with OCR
- Trial balance validation
- ATP (Authorization to Print) tracking

---

## 🛠️ Configuration Details

### config.example.json

**MCP Servers:**
- **notion** - Connect to Notion databases
- **github** - (optional) GitHub integration

**Models:**
- Claude Sonnet 4.5 (claude-sonnet-4-20250514)
- Best for: Code generation, complex reasoning

**Environment Variables:**
```bash
# Required
export NOTION_API_KEY="secret_YOUR_KEY"
export ANTHROPIC_API_KEY="sk-ant-api03-YOUR_KEY"

# Optional (for integrations)
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your_key"
export PADDLEOCR_URL="https://ade-ocr-backend-d9dru.ondigitalocean.app"
```

---

## 📚 Usage Examples

### Example 1: Simple Module

```bash
cn -p "odoo-developer" << 'EOF'
Create a simple inventory tracking module with:
- Model: product.inventory
- Fields: product, quantity, location, date
- Views: form, tree, search
- Security: All users can read, only managers can write
EOF
```

### Example 2: Travel Expense Module

```bash
cn -p "travel-expense-generator"
# Uses the full template from travel-expense-generator.md
```

### Example 3: Finance SSC Module

```bash
cn -p "finance-ssc-generator"
# Generates complete multi-agency finance automation
```

### Example 4: Query Notion

```bash
# Get feature requests ready for development
cn << 'EOF'
Query my Notion Feature Requests database for all cards with:
- Status: "Ready for Development"
- Sort by: Priority descending

Output: title, description, priority
EOF
```

### Example 5: Update Notion

```bash
# Update card status after module generation
cn << 'EOF'
Update Notion card with ID "abc123" to:
- Status: "In Development"
- Add comment: "Module generated on $(date)"
EOF
```

---

## 🔐 Security Notes

### DO NOT Commit Secrets

**Never commit:**
- `~/.continue/config.json` (contains API keys)
- `.env` files
- Any file with API keys/tokens

**Safe to commit:**
- `.continue/config.example.json` (without real keys)
- `.continue/prompts/*.md` (no secrets)
- `.continue/README.md` (this file)

### GitHub Secrets

For CI/CD, use GitHub Secrets:
- `NOTION_API_KEY`
- `ANTHROPIC_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Never hardcode secrets in workflow files.

---

## 🧪 Testing

### Test MCP Connection

```bash
# Test Notion MCP server
npx @modelcontextprotocol/server-notion

# Test with Continue CLI
cn "List my Notion databases"
```

### Test Prompt Loading

```bash
# List available prompts
ls ~/.continue/prompts/

# Test a prompt
cn -p "odoo-developer" "What do you specialize in?"
```

### Validate Generated Module

```bash
# After generation, validate
find addons/new_module -name "*.py" -exec python3 -m py_compile {} \;

# Run tests
python -m pytest addons/new_module/tests/
```

---

## 🔧 Troubleshooting

### Issue: Prompts Not Found

**Solution:**
```bash
# Ensure prompts are copied
cp .continue/prompts/* ~/.continue/prompts/

# Check location
ls ~/.continue/prompts/
```

### Issue: MCP Server Failed

**Solution:**
```bash
# Test MCP directly
npx -y @modelcontextprotocol/server-notion

# Check API key
echo $NOTION_API_KEY
```

### Issue: Module Generation Failed

**Solution:**
```bash
# Check logs
tail -100 automation.log

# Run with debug
cn -p "odoo-developer" --verbose "Create module..."
```

---

## 📖 Additional Resources

### Continue.dev Documentation
- [Official Docs](https://docs.continue.dev)
- [MCP Servers](https://docs.continue.dev/walkthroughs/mcp-server)
- [Custom Prompts](https://docs.continue.dev/walkthroughs/prompt-files)

### Notion MCP
- [Notion MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/notion)
- [MCP Protocol Spec](https://spec.modelcontextprotocol.io)

### Odoo Development
- [OCA Guidelines](https://github.com/OCA/odoo-community.org)
- [Odoo 19 Docs](https://www.odoo.com/documentation/19.0/)

### InsightPulse AI Docs
- [Main Automation Guide](../docs/NOTION_ODOO_AUTOMATION.md)
- [Module Documentation](../MODULES.md)
- [Deployment Guide](../DEPLOYMENT_CHECKLIST.md)

---

## 🚀 Next Steps

1. ✅ Complete setup (install CLI, configure keys)
2. ✅ Test Notion connection
3. ✅ Generate test module
4. 📖 Read [NOTION_ODOO_AUTOMATION.md](../docs/NOTION_ODOO_AUTOMATION.md)
5. 🎯 Start automating!

---

**Questions?** See [docs/NOTION_ODOO_AUTOMATION.md](../docs/NOTION_ODOO_AUTOMATION.md) for comprehensive guide.

---

*Last Updated: 2025-10-30*
*Version: 1.0.0*
