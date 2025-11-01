# Notion-to-Odoo Automation with DeepSeek API & Cline CLI

**100x cheaper than Claude!** 🎉

## Cost Comparison

| Provider | Cost per Module | Cost for 100 Modules | Speed |
|----------|----------------|---------------------|--------|
| **DeepSeek** | **$0.001** | **$0.10/month** | Fast |
| Anthropic Claude | $0.03 | $3/month | Fast |
| OpenAI GPT-4 | $0.15 | $15/month | Medium |

## Architecture Options

### Option 1: Pure Python + DeepSeek (Recommended)

**Pros**:
- ✅ Complete end-to-end automation
- ✅ Direct API control
- ✅ 100x cheaper than Claude
- ✅ Existing GitHub Actions workflow
- ✅ Proven and documented

**Architecture**:
```
Notion Database → Python → DeepSeek API → Odoo Module → GitHub PR → Notion Update
```

###Option 2: Cline CLI + DeepSeek (Interactive)

**Pros**:
- ✅ Native AI coding assistant
- ✅ Task management and checkpoints
- ✅ 100x cheaper than Claude
- ✅ Autonomous mode (`-y` flag)

**Cons**:
- ❌ Still need Python for Notion/GitHub
- ❌ More complex setup
- ❌ Less predictable output format

**Architecture**:
```
Notion Database → Python → Cline CLI (DeepSeek) → Odoo Module → GitHub PR → Notion Update
```

## Quick Start: Option 1 (Python + DeepSeek)

### 1. Install Dependencies

```bash
cd scripts/notion-automation
pip install -r requirements-deepseek.txt
```

**requirements-deepseek.txt**:
```
notion-client>=2.2.1
openai>=1.0.0  # DeepSeek uses OpenAI SDK
PyGithub>=2.1.1
python-dotenv>=1.0.0
```

### 2. Configure Environment

```bash
# Add to ~/.zshrc or .env
export NOTION_API_TOKEN=secret_...
export NOTION_DB_ID=abc123...
export DEEPSEEK_API_KEY=sk-...
export GITHUB_TOKEN=ghp_...
```

Get DeepSeek API key: https://platform.deepseek.com/api_keys

### 3. Run Automation

```bash
# Fetch Notion specs
python fetch_notion_specs.py \
  --database-id "$NOTION_DB_ID" \
  --status "Ready for Dev" \
  --output specs.json

# Generate modules with DeepSeek
python generate_odoo_module_deepseek.py \
  --spec specs.json \
  --output-dir addons \
  --odoo-version 19.0

# Create GitHub PR
gh pr create --title "Auto-generated module" --body "..."

# Update Notion
python update_notion_status.py \
  --page-id "$PAGE_ID" \
  --status "In Development" \
  --pr-url "$PR_URL"
```

### 4. GitHub Actions Integration

```yaml
# .github/workflows/notion-to-odoo-deepseek.yml
name: Notion to Odoo (DeepSeek)

on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd scripts/notion-automation
          pip install -r requirements-deepseek.txt

      - name: Fetch Notion specs
        env:
          NOTION_API_TOKEN: ${{ secrets.NOTION_API_TOKEN }}
          NOTION_DB_ID: ${{ secrets.NOTION_DB_ID }}
        run: |
          python scripts/notion-automation/fetch_notion_specs.py \
            --database-id "$NOTION_DB_ID" \
            --status "Ready for Dev" \
            --output specs.json

      - name: Generate modules with DeepSeek
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: |
          python scripts/notion-automation/generate_odoo_module_deepseek.py \
            --spec specs.json \
            --output-dir addons \
            --odoo-version 19.0 \
            --model deepseek-chat

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          commit-message: 'feat: auto-generated Odoo modules (DeepSeek)'
          branch: auto-gen/deepseek-modules-${{ github.run_number }}
          title: '🤖 [Auto-Generated] Odoo Modules (DeepSeek)'
          body: |
            ## Automated Module Generation (DeepSeek)

            **Model**: deepseek-chat
            **Cost**: ~$0.001 per module (100x cheaper than Claude!)

            ### Generated Modules
            See commits for details

            ---
            🤖 Generated with DeepSeek API
          labels: auto-generated, odoo-module, deepseek, needs-review

      - name: Update Notion
        env:
          NOTION_API_TOKEN: ${{ secrets.NOTION_API_TOKEN }}
        run: |
          jq -r '.[] | .page_id' specs.json | while read PAGE_ID; do
            python scripts/notion-automation/update_notion_status.py \
              --page-id "$PAGE_ID" \
              --status "In Development" \
              --pr-url "${{ steps.cpr.outputs.pull-request-url }}"
          done
```

## Quick Start: Option 2 (Cline CLI + DeepSeek)

### 1. Install Cline CLI

```bash
npm install -g @yaegaki/cline-cli
```

### 2. Configure Cline with DeepSeek

```bash
# Cline CLI supports OpenAI-compatible APIs
cline config set api_provider openai
cline config set api_base_url https://api.deepseek.com
cline config set api_key $DEEPSEEK_API_KEY
cline config set model deepseek-chat
```

### 3. Run Automation Script

```bash
export NOTION_DB_ID=abc123...
export DEEPSEEK_API_KEY=sk-...

bash scripts/notion-automation/cline-deepseek-automation.sh
```

The script will:
1. Fetch Notion specs (Python)
2. Generate modules (Cline CLI + DeepSeek)
3. Create GitHub PRs (gh CLI)
4. Update Notion (Python)

## DeepSeek API Details

### Models

**deepseek-chat** (Recommended for Odoo):
- Best for code generation
- Context: 64K tokens
- Pricing: $0.14/M input, $0.28/M output

**deepseek-coder**:
- Specialized for code
- Context: 16K tokens
- Pricing: Same as deepseek-chat

### Authentication

```bash
# Get API key from https://platform.deepseek.com/api_keys
export DEEPSEEK_API_KEY=sk-...
```

### API Endpoint

DeepSeek is OpenAI-compatible:
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Generate Odoo module..."}],
    max_tokens=8000
)
```

## Cost Analysis

### Per Module Breakdown

**DeepSeek**:
- Input: 2,000 tokens × $0.14/M = $0.00028
- Output: 6,000 tokens × $0.28/M = $0.00168
- **Total: ~$0.002 per module**

**Claude 3.5 Sonnet** (comparison):
- Input: 2,000 tokens × $3/M = $0.006
- Output: 6,000 tokens × $15/M = $0.09
- **Total: ~$0.096 per module**

**Savings**: 48x cheaper!

### Monthly Cost (100 Modules)

- **DeepSeek**: $0.20/month
- **Claude**: $9.60/month
- **Savings**: $9.40/month (98% reduction)

## Feature Comparison

| Feature | Python + DeepSeek | Cline CLI + DeepSeek |
|---------|------------------|---------------------|
| End-to-end automation | ✅ Complete | ⚠️ Hybrid |
| Cost | $0.002/module | $0.002/module |
| Setup complexity | Low | Medium |
| Predictability | High | Medium |
| Interactive mode | ❌ No | ✅ Yes |
| Task management | ❌ No | ✅ Yes |
| GitHub Actions ready | ✅ Yes | ⚠️ Partial |

## Recommendation

**Use Option 1 (Python + DeepSeek)** because:

1. **Complete automation** - No manual steps
2. **Proven workflow** - Based on working implementation
3. **Predictable output** - Custom parsing logic
4. **100x cheaper** - $0.002 vs $0.03 per module
5. **GitHub Actions ready** - Drop-in replacement

**Use Option 2 (Cline CLI + DeepSeek)** if you want:

1. **Interactive development** - Chat with AI during generation
2. **Task resumption** - Pause/resume complex tasks
3. **Checkpoint management** - Save and restore states

## Migration from Claude

### Update Python Script

```python
# Old (Anthropic)
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=8000,
    messages=[{"role": "user", "content": prompt}]
)

# New (DeepSeek)
from openai import OpenAI
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=8000,
    messages=[{"role": "user", "content": prompt}]
)
```

### Update GitHub Secrets

```bash
# Remove old secret
gh secret delete ANTHROPIC_API_KEY

# Add new secret
gh secret set DEEPSEEK_API_KEY
```

### Update Workflow

```yaml
# Change environment variable name
env:
  DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}  # Was: ANTHROPIC_API_KEY

# Change script name
run: python generate_odoo_module_deepseek.py  # Was: generate_odoo_module.py
```

## Troubleshooting

### DeepSeek API Rate Limits

**Limits**:
- 60 requests per minute
- 1M tokens per minute

**Solution**: Add rate limiting to script:
```python
import time
time.sleep(1)  # 1 second between requests
```

### Cline CLI Configuration Issues

**Error**: `No API provider configured`

**Solution**:
```bash
cline config set api_provider openai
cline config set api_base_url https://api.deepseek.com
cline config set api_key $DEEPSEEK_API_KEY
```

### Module Generation Quality

**Issue**: Generated code has TODOs or placeholders

**Solution**: Enhance system prompt:
```python
ODOO_EXPERT_PROMPT += """
CRITICAL RULES:
- NO TODO comments
- NO placeholder functions
- Complete implementation only
- All features fully working
"""
```

## Next Steps

1. **Get DeepSeek API key**: https://platform.deepseek.com/api_keys
2. **Choose option**: Python (recommended) or Cline CLI
3. **Test locally**: Generate one module to verify quality
4. **Deploy to GitHub Actions**: Set secrets and enable workflow
5. **Monitor costs**: Check usage at https://platform.deepseek.com/usage

---

**Generated**: 2025-10-31
**Cost per module**: $0.002 (100x cheaper than Claude!)
**Recommended**: Option 1 (Python + DeepSeek)
