# InsightPulse AI Training Hub - MCP Integration

> **Replaces n8n** with MCP + Claude Max + CLI automation for training orchestration

**Architecture**: Claude Max (your subscription) → MCP Server → Training Stack (Axolotl/vLLM)

**Cost**: $0 API fees (uses your Claude Max subscription)

---

## 🎯 What This Replaces

| Before (PR #320 + n8n) | After (MCP + Claude Max) |
|-------------------------|--------------------------|
| n8n workflows ($20-50/month hosting) | CLI bash scripts + cron ($0) |
| Manual API orchestration | MCP tools (6 functions) |
| Limited AI capabilities | Full Claude Max reasoning |
| Complex GUI setup | Simple tool calls |

---

## 🏗️ Architecture

```
┌────────────────────┐
│  Claude Max        │ ← Your subscription (no API costs)
│  Web/Desktop       │
└──────┬─────────────┘
       │ MCP Protocol
       ▼
┌────────────────────────────────────┐
│  mcp.insightpulseai.net            │
│  Training Hub Tools:               │
│  1. prepare_bir_training_data      │
│  2. start_axolotl_training         │
│  3. deploy_vllm_model              │
│  4. run_model_evaluation           │
│  5. get_training_status            │
│  6. list_available_models          │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│  Training Infrastructure           │
│  - Axolotl (RTX 4090 fine-tuning) │
│  - vLLM (inference serving)        │
│  - LiteLLM (OpenAI gateway)        │
│  - TensorBoard (monitoring)        │
│  - Supabase (metrics/logs)         │
└────────────────────────────────────┘
```

---

## 📦 Components

### 1. MCP Server Tools (`server.py`)

**6 tools for training orchestration:**

| Tool | Purpose |
|------|---------|
| `prepare_bir_training_data` | Extract & validate BIR forms from OCR/validation queue |
| `start_axolotl_training` | Launch RTX 4090 optimized training jobs |
| `deploy_vllm_model` | Serve fine-tuned models via vLLM |
| `run_model_evaluation` | Validate against test sets (BIR compliance, expense accuracy) |
| `get_training_status` | Real-time job monitoring (progress, loss, ETA) |
| `list_available_models` | Show deployed models in vLLM + LiteLLM |

### 2. CLI Automation (`scripts/training/`)

**Bash scripts for cron jobs** (replaces n8n):

- `automate_bir_training.sh` - Daily BIR training pipeline
- Runs via cron: `0 2 * * *` (2 AM daily)
- Calls MCP tools sequentially
- Slack notifications
- Error handling & retries

### 3. Docker Compose (`docker-compose.training.yml`)

**Full training stack:**

```yaml
services:
  - axolotl          # Fine-tuning engine
  - vllm-*           # Model serving (per model)
  - litellm          # OpenAI-compatible gateway
  - tensorboard      # Training visualization
  - mcp-training-hub # MCP server extension
```

### 4. Supabase Schema (`migrations/005_training_infrastructure.sql`)

**5 tables for tracking:**

- `training_datasets` - Prepared training data
- `training_jobs` - Active/completed jobs
- `model_deployments` - Running vLLM containers
- `model_evaluations` - Test results & metrics
- `training_metrics` - Real-time progress (loss, LR, etc.)

---

## 🚀 Quick Start

### Step 1: Deploy Supabase Schema

```bash
cd /home/user/insightpulse-odoo

# Apply migration
psql "$POSTGRES_URL" -f supabase/migrations/005_training_infrastructure.sql

# Verify tables
psql "$POSTGRES_URL" -c "\dt public.training_*"
# Expected: training_datasets, training_jobs, model_deployments, etc.
```

### Step 2: Start Training Stack

```bash
# Set environment variables
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_SERVICE_ROLE="your-service-role-key"
export POSTGRES_URL="postgresql://..."
export HF_TOKEN="your-huggingface-token"
export WANDB_API_KEY="your-wandb-key"
export LITELLM_MASTER_KEY="sk-insightpulse"

# Start services
docker-compose -f docker-compose.training.yml up -d

# Verify services
docker-compose -f docker-compose.training.yml ps
# Expected: axolotl, litellm, tensorboard, mcp-training-hub (all running)
```

### Step 3: Configure Claude Desktop

**Copy MCP config** to Claude Desktop:

```bash
# Linux/Mac
cp mcp/training-hub/claude-desktop-config.json ~/.config/claude/mcp_servers.json

# Windows
cp mcp/training-hub/claude-desktop-config.json %APPDATA%/Claude/mcp_servers.json
```

**Or merge with existing config:**

```json
{
  "mcpServers": {
    "insightpulse-training": {
      "url": "http://localhost:8003",
      "transport": "sse",
      "env": {
        "SUPABASE_URL": "https://spdtwktxdalcfigzeqrz.supabase.co",
        "SUPABASE_SERVICE_ROLE": "..."
      }
    }
  }
}
```

Restart Claude Desktop to load MCP server.

### Step 4: Test MCP Tools (from Claude Max)

**In Claude Desktop/Web chat:**

```
You: "Start BIR training with forms from this week"

Claude will:
1. Call prepare_bir_training_data tool
2. Start axolotl_training job
3. Monitor progress
4. Deploy when ready
5. Run validation tests
```

**Or test via curl:**

```bash
# Test prepare_bir_training_data
curl -X POST http://localhost:8003/tools/prepare_bir_training_data \
  -H "Content-Type: application/json" \
  -d '{
    "form_types": ["1601C", "2550Q"],
    "source": "validation_queue",
    "min_confidence": 0.85
  }'

# Test start_axolotl_training
curl -X POST http://localhost:8003/tools/start_axolotl_training \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "/opt/insightpulse/training/datasets/bir_test.jsonl",
    "config_template": "bir-llama-lora",
    "model_output_name": "test-model"
  }'

# Monitor training
curl -X POST http://localhost:8003/tools/get_training_status \
  -H "Content-Type: application/json" \
  -d '{"job_id": "test-model-20250107-..."}'
```

### Step 5: Set Up Cron Automation

**Install cron job for daily BIR training:**

```bash
# Make script executable
chmod +x /home/user/insightpulse-odoo/scripts/training/automate_bir_training.sh

# Add to crontab
crontab -e

# Add line (runs daily at 2 AM):
0 2 * * * /home/user/insightpulse-odoo/scripts/training/automate_bir_training.sh >> /var/log/insightpulse/bir-training.log 2>&1
```

**Configure Slack webhook (optional):**

```bash
export SLACK_WEBHOOK_TRAINING="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

---

## 🎯 Usage Examples

### Example 1: Train BIR Compliance Model

**From Claude Max:**

```
You: "I need to train a BIR compliance model on the latest validated forms from the past week. Use Llama 3.3 70B with LoRA, 3 epochs, and deploy it when ready."

Claude will:
1. prepare_bir_training_data(form_types=["1601C", "2550Q", "1702RT", "2307"], source="validation_queue")
2. start_axolotl_training(dataset_path="...", config_template="bir-llama-lora", epochs=3)
3. Monitor via get_training_status every minute
4. When complete: deploy_vllm_model(model_name="bir-compliance-prod", port=8001)
5. run_model_evaluation(test_dataset="bir-test.jsonl", eval_type="bir_compliance")
6. Report final accuracy, F1 score, latency
```

### Example 2: Compare Model Performance

**From Claude Max:**

```
You: "Compare the performance of all deployed BIR models and show me which one has the best F1 score."

Claude will:
1. list_available_models()
2. For each model: run_model_evaluation(...)
3. Aggregate results
4. Present comparison table with F1 scores
```

### Example 3: Deploy Expense Classifier

**From CLI:**

```bash
# Prepare expense training data
curl -X POST http://localhost:8003/tools/prepare_bir_training_data \
  -d '{"form_types": ["expense_receipts"], "source": "production"}'

# Train Mistral 7B with QLoRA
curl -X POST http://localhost:8003/tools/start_axolotl_training \
  -d '{
    "dataset_path": "/opt/insightpulse/training/datasets/expense_receipts.jsonl",
    "config_template": "expense-mistral-qlora",
    "model_output_name": "expense-classifier-v2",
    "base_model": "mistralai/Mistral-7B-Instruct-v0.2"
  }'

# Wait for completion...

# Deploy to port 8002
curl -X POST http://localhost:8003/tools/deploy_vllm_model \
  -d '{
    "model_path": "/opt/insightpulse/training/models/expense-classifier-v2",
    "model_name": "expense-classifier-prod",
    "port": 8002
  }'
```

---

## 📊 Monitoring

### TensorBoard (Real-Time Training)

```bash
# Access at: http://localhost:6006
docker-compose -f docker-compose.training.yml logs tensorboard
```

### Supabase Dashboard (Job History)

```sql
-- Active training jobs
SELECT * FROM get_active_training_jobs();

-- Training dashboard
SELECT * FROM training_dashboard ORDER BY started_at DESC LIMIT 10;

-- Model leaderboard
SELECT * FROM model_leaderboard ORDER BY avg_f1_score DESC;

-- Latest evaluation for bir-compliance model
SELECT * FROM model_evaluations
WHERE model_name = 'bir-compliance-prod'
ORDER BY timestamp DESC LIMIT 1;
```

### Slack Notifications

**Automated alerts sent to Slack:**

- ✅ Training started
- ⏱️ Progress updates (every 25% completion)
- ✅ Training completed
- 📊 Evaluation results
- ❌ Errors/failures

---

## 🔧 Configuration Templates

### Axolotl Configs (`training/configs/templates/`)

Pre-configured templates:

1. **`bir-llama-lora.yml`** - Llama 3.3 70B LoRA for BIR forms
2. **`expense-mistral-qlora.yml`** - Mistral 7B QLoRA for expense classification
3. **`finance-ssc-full.yml`** - Full fine-tune for month-end closing
4. **`receipt-ocr-lora.yml`** - SmolLM2 LoRA for receipt extraction

**Example: `bir-llama-lora.yml`**

```yaml
base_model: meta-llama/Llama-3.3-70B-Instruct
adapter: lora
lora_r: 32
lora_alpha: 64
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - v_proj
  - k_proj
  - o_proj

sequence_len: 4096
bf16: true
flash_attention: true
sample_packing: true

# RTX 4090 optimizations
gradient_checkpointing: true
load_in_4bit: false  # Full precision on 4090
```

---

## 💰 Cost Comparison

### Before (n8n + API calls)

| Component | Cost/Month |
|-----------|------------|
| n8n Cloud | $20-50 |
| API calls (GPT-4 for orchestration) | $10-30 |
| **Total** | **$30-80/month** |

### After (MCP + Claude Max)

| Component | Cost/Month |
|-----------|------------|
| Claude Max subscription | $0 (already have) |
| MCP server (DigitalOcean) | $0 (uses existing infra) |
| CLI bash scripts | $0 |
| **Total** | **$0/month** |

**Savings: $30-80/month = $360-960/year**

---

## 🐛 Troubleshooting

### MCP Server Not Responding

```bash
# Check if container is running
docker ps | grep mcp-training-hub

# View logs
docker logs insightpulse-mcp-training

# Restart
docker-compose -f docker-compose.training.yml restart mcp-training-hub
```

### Training Job Stuck

```bash
# Check Axolotl logs
docker exec insightpulse-axolotl tail -f /workspace/logs/job_*.log

# Kill stuck job
docker exec insightpulse-axolotl pkill -f accelerate

# Check GPU usage
nvidia-smi
```

### vLLM Deployment Failed

```bash
# Check vLLM logs
docker logs insightpulse-vllm-bir

# Test endpoint
curl http://localhost:8001/v1/models

# Restart container
docker restart insightpulse-vllm-bir
```

### Supabase Connection Issues

```bash
# Test connection
psql "$POSTGRES_URL" -c "SELECT 1"

# Check MCP server env
docker exec insightpulse-mcp-training env | grep SUPABASE
```

---

## 📚 References

1. **PR #320**: Original training stack (Axolotl, vLLM, Unsloth, LiteLLM)
2. **Axolotl Docs**: https://github.com/OpenAccess-AI-Collective/axolotl
3. **vLLM Docs**: https://docs.vllm.ai
4. **MCP Protocol**: https://modelcontextprotocol.io

---

## ✅ Next Steps

After deploying:

1. ✅ **Test MCP tools** from Claude Desktop
2. ✅ **Run first training job** via `automate_bir_training.sh`
3. ✅ **Monitor in TensorBoard** at http://localhost:6006
4. ✅ **Deploy model to vLLM** and test inference
5. ✅ **Set up cron** for daily automated training
6. ✅ **Configure Slack webhooks** for notifications

---

## 🎉 Summary

**You've replaced:**
- ❌ n8n workflows
- ❌ API costs
- ❌ Complex GUI setup

**With:**
- ✅ MCP + Claude Max (your subscription)
- ✅ CLI bash scripts (cron)
- ✅ 6 training orchestration tools
- ✅ $0/month cost
- ✅ Full control via Claude Desktop

**The competitive edge is automation + private AI. You now have both! 🚀**
