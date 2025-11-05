# Gradient API Integration Setup

Complete setup guide for Gradient API fallback integration with InsightPulse AI Agent.

## Prerequisites

1. **Gradient API Account**
   - Sign up at https://gradient.ai
   - Generate an API key from the dashboard
   - Save the `MODEL_ACCESS_KEY` securely

2. **Python Dependencies**
   - Install Gradient SDK: `pip install gradient>=0.1.0`
   - Or use requirements.txt: `pip install -r requirements.txt`

## Installation Steps

### 1. Install Dependencies

```bash
cd /Users/tbwa/insightpulse-odoo
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add to `~/.zshrc` or Odoo service configuration:

```bash
# Gradient API Configuration
export MODEL_ACCESS_KEY="your_gradient_api_key_here"
```

Reload environment:
```bash
source ~/.zshrc
```

### 3. Configure Odoo Parameters

Login to Odoo and navigate to **Settings → Technical → Parameters → System Parameters**.

Add the following configuration parameters:

| Key | Value | Description |
|-----|-------|-------------|
| `ipai_agent.gradient_enabled` | `True` | Enable Gradient API fallback |
| `ipai_agent.gradient_model` | `openai-gpt-oss-120b` | Gradient model to use |
| `ipai_agent.gradient_max_tokens` | `500` | Maximum tokens per response |

**Available Gradient Models:**
- `openai-gpt-oss-120b` (120B parameters, recommended)
- `nous-hermes-2-mixtral-8x7b-dpo`
- `llama-3-70b-instruct`

### 4. Install/Update ipai_agent Module

```bash
# If module already installed, upgrade it
# Otherwise, install from Apps menu
```

In Odoo:
1. Navigate to **Apps**
2. Search for "InsightPulse AI Agent"
3. Click **Upgrade** (or **Install** if first time)

### 5. Test the Integration

#### Test via Odoo Discuss

1. Open any Discuss channel
2. Mention `@ipai-bot` with a test query:
   ```
   @ipai-bot What is the capital of France?
   ```
3. Bot should respond (using DO Agent Platform or Gradient fallback)

#### Test via Python Console

```python
# In Odoo shell (odoo-bin shell)
from odoo import api, SUPERUSER_ID

env = api.Environment(cr, SUPERUSER_ID, {})
agent_api = env['ipai.agent.api']

result = agent_api.call_agent(
    query="What is the capital of France?",
    context={
        'user_id': 1,
        'user_name': 'Administrator',
        'user_email': 'admin@example.com',
        'agencies': ['RIM', 'CKVC'],
        'channel': 'general',
        'permissions': {},
        'company_id': 1,
        'company_name': 'InsightPulse',
        'timestamp': '2025-11-04T00:00:00Z',
    }
)

print(result)
```

Expected output:
```python
{
    'success': True,
    'message': 'The capital of France is Paris.',
    'provider': 'gradient',  # or 'digitalocean'
    'model': 'openai-gpt-oss-120b',
    'fallback': True,  # if Gradient was used as fallback
}
```

## Architecture

### Fallback Priority

1. **Primary: DigitalOcean Agent Platform**
   - URL: `https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat`
   - Model: Claude 3.5 Sonnet
   - Features: Full action execution, tool use

2. **Fallback: Gradient API**
   - Model: OpenAI-GPT-OSS-120B (120B parameters)
   - Features: Text generation only (no actions)
   - Cost: Usage-based (~$0.001-0.002 per 1K tokens)

3. **Error Response**
   - When both providers fail
   - User-friendly error message

### LLM Router Flow

```
User Query → call_agent()
     ↓
Try DO Agent Platform
     ↓
   Success? → Return response
     ↓ No
Try Gradient API (via LLMRouter)
     ↓
   Success? → Return response
     ↓ No
Return error message
```

### Context Preservation

The LLM router preserves full user context:
- Company information
- User identity and email
- Agency associations
- Channel context
- User permissions

## Configuration Reference

### Odoo System Parameters

All parameters are optional with sensible defaults:

```python
{
    # DigitalOcean Agent Platform (Primary)
    'ipai_agent.api_url': 'https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat',
    'ipai_agent.api_key': '',  # Optional
    'ipai_agent.timeout': '30',  # seconds
    'ipai_agent.max_retries': '2',

    # Gradient API (Fallback)
    'ipai_agent.gradient_enabled': 'True',
    'ipai_agent.gradient_model': 'openai-gpt-oss-120b',
    'ipai_agent.gradient_max_tokens': '500',
}
```

### Environment Variables

Required:
- `MODEL_ACCESS_KEY` - Gradient API key (if gradient_enabled=True)

Optional:
- `IPAI_AGENT_URL` - Override DO Agent URL
- `IPAI_AGENT_KEY` - Override DO Agent API key

## Monitoring

### Check LLM Router Status

```python
# In Odoo shell
from odoo import api, SUPERUSER_ID

env = api.Environment(cr, SUPERUSER_ID, {})

from odoo.addons.ipai_agent.models.llm_router import LLMRouter

router = LLMRouter(env)
status = router.get_status()

print(status)
```

Expected output:
```python
{
    'digitalocean': {
        'configured': True,
        'available': True  # or False
    },
    'gradient': {
        'configured': True,
        'available': True  # or False
    }
}
```

### View Agent Logs

Navigate to **InsightPulse AI Agent → Agent Logs** in Odoo to see:
- All AI queries and responses
- Provider used (DO Agent or Gradient)
- Response times
- Error messages

## Cost Monitoring

### Gradient API Pricing

- **openai-gpt-oss-120b**: ~$0.001-0.002 per 1K tokens
- Typical query: 100-500 tokens
- Expected cost: ~$20-100/month (depending on usage)

### Example Usage Calculations

**Light Usage (50 queries/day):**
- Average 300 tokens per query
- 50 queries × 30 days = 1,500 queries/month
- 1,500 × 300 tokens = 450K tokens/month
- 450K × $0.0015 = **~$0.68/month**

**Moderate Usage (200 queries/day):**
- 200 queries × 30 days = 6,000 queries/month
- 6,000 × 300 tokens = 1.8M tokens/month
- 1.8M × $0.0015 = **~$2.70/month**

**Heavy Usage (1000 queries/day):**
- 1,000 queries × 30 days = 30,000 queries/month
- 30,000 × 300 tokens = 9M tokens/month
- 9M × $0.0015 = **~$13.50/month**

**Total Infrastructure Cost (with Gradient):**
- Baseline: $68/month (DO + Supabase)
- Gradient API: $2-20/month (typical usage)
- **Total: $70-88/month**

## Troubleshooting

### "MODULE_ACCESS_KEY not set"

**Symptom:** Warning in logs: "MODEL_ACCESS_KEY not set - Gradient API unavailable"

**Solution:**
```bash
# Add to ~/.zshrc
export MODEL_ACCESS_KEY="your_gradient_api_key_here"
source ~/.zshrc

# Restart Odoo service
sudo systemctl restart odoo
```

### "Gradient SDK not installed"

**Symptom:** Warning: "Gradient SDK not installed - run: pip install gradient"

**Solution:**
```bash
pip install gradient>=0.1.0
# or
pip install -r requirements.txt

# Restart Odoo service
sudo systemctl restart odoo
```

### "All AI services temporarily unavailable"

**Symptom:** Bot returns: "⚠️ All AI services temporarily unavailable."

**Causes:**
1. DO Agent Platform down + Gradient API unavailable
2. Network connectivity issues
3. Invalid API keys

**Debug Steps:**
```bash
# Check DO Agent Platform
curl -sf https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/health

# Check Gradient API
python3 -c "
import os
from gradient import Gradient
client = Gradient(model_access_key=os.environ.get('MODEL_ACCESS_KEY'))
print('Gradient API OK')
"

# Check Odoo logs
sudo journalctl -u odoo -f
```

### Gradient API Errors

**Symptom:** "Gradient API failed: [error message]"

**Common Errors:**
- `401 Unauthorized` → Invalid MODEL_ACCESS_KEY
- `429 Too Many Requests` → Rate limit exceeded
- `500 Internal Server Error` → Temporary Gradient service issue

**Solution:**
1. Verify API key is correct
2. Check Gradient dashboard for service status
3. Wait for rate limits to reset
4. Contact Gradient support if persistent

## Next Steps

After successful integration:

1. **Monitor Usage:**
   - Check Agent Logs regularly
   - Track Gradient API usage in dashboard
   - Monitor response quality

2. **Optimize Costs:**
   - Adjust `gradient_max_tokens` if needed
   - Consider switching models if quality/cost trade-off needed
   - Cache frequent responses

3. **Enable TLS on ERP Droplet:**
   - Run `scripts/deploy-core-stack.sh`
   - Obtain Let's Encrypt certificates
   - Test HTTPS endpoints

4. **Full Deployment:**
   - Install ipai_agent on production Odoo
   - Configure all agencies
   - Train users on @ipai-bot usage

## Support

**Documentation:**
- Gradient AI Docs: https://docs.gradient.ai
- InsightPulse Docs: `/Users/tbwa/insightpulse-odoo/docs/`

**Contact:**
- Jake Tolentino: jgtolentino_rn@yahoo.com
