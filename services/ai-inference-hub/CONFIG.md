# Configuration Guide

## 🎯 Deployment Modes

### Mode 1: Development (Anthropic API)
**Use Case**: Local development, testing, prototyping
**Provider**: Anthropic Max Subscription (Claude 3.5 Sonnet/Opus)
**Cost**: $20/month (unlimited for Max tier)
**Latency**: ~1-3s
**Setup**: Add ANTHROPIC_API_KEY to environment

### Mode 2: Hybrid (Anthropic + Local)
**Use Case**: Transition period, A/B testing
**Providers**: Anthropic API (dev) + vLLM (production)
**Cost**: $20/month (Anthropic) + GPU costs
**Setup**: Configure both API key and local model

### Mode 3: Production (Self-Hosted Only)
**Use Case**: Full control, data privacy, cost optimization at scale
**Provider**: vLLM with DeepSeek-V3 or CodeLlama
**Cost**: GPU infrastructure only (~$200-500/month on-demand)
**Latency**: ~0.5-2s (GPU)
**Setup**: Deploy to GPU droplet

## 🔧 Configuration

### Environment Variables

```bash
# ============ Development Mode (Anthropic) ============
# Use for: Local testing, rapid prototyping
ANTHROPIC_API_KEY=sk-ant-api03-...
DEFAULT_MODEL=claude-3-5-sonnet-20241022
# Options: claude-3-5-sonnet-20241022, claude-3-opus-20240229

# ============ Production Mode (Local LLM) ============
# Use for: Production inference, privacy requirements
LLM_MODEL=deepseek-ai/DeepSeek-V3
# Options:
#   - deepseek-ai/DeepSeek-V3 (best coding)
#   - codellama/CodeLlama-34b-Instruct-hf
#   - Qwen/Qwen2.5-Coder-32B-Instruct

VLLM_ENGINE=true
QUANTIZATION=8bit
# Options: none, 8bit, 4bit
MAX_MODEL_LEN=8192
GPU_MEMORY_UTILIZATION=0.9

# ============ Hybrid Mode (Both) ============
# Use for: Gradual migration, fallback support
ANTHROPIC_API_KEY=sk-ant-api03-...
LLM_MODEL=deepseek-ai/DeepSeek-V3
FALLBACK_TO_API=true  # Use Anthropic if local fails

# ============ Document & Speech (Always Local) ============
MODEL_NAME=deepseek-ai/DeepSeek-OCR
WHISPER_MODEL=base
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
TORCH_DEVICE=cpu
IMAGE_SIZE=base
```

## 📊 Cost Comparison

### Development Workflow (Anthropic Max)
```
Anthropic Max: $20/month (unlimited)
+ OCR/STT/TTS: $34/month (CPU droplet)
= Total: $54/month
```

**Pros**:
- Unlimited inference for development
- State-of-the-art Claude 3.5 Sonnet/Opus
- Zero infrastructure management
- Fast iteration

**Cons**:
- Data leaves your infrastructure
- Dependent on external service
- Rate limits on extended context

### Production Workflow (Self-Hosted)
```
GPU Droplet: $4.49/hr × 40hrs/month = $180/month (on-demand)
+ OCR/STT/TTS: $34/month (CPU droplet)
= Total: $214/month
```

**Pros**:
- Full data control
- No rate limits
- Customizable models
- Cost-effective at scale

**Cons**:
- Infrastructure management
- Startup time for cold start
- GPU availability

## 🚀 Recommended Setup

### Local Development
```bash
# .env.local
ANTHROPIC_API_KEY=sk-ant-api03-...
DEFAULT_MODEL=claude-3-5-sonnet-20241022
SUPABASE_URL=http://localhost:54321
SUPABASE_SERVICE_ROLE_KEY=...

# Use Anthropic for all coding agent requests
# Use local models for OCR/STT/TTS
```

### Staging Environment
```bash
# .env.staging
ANTHROPIC_API_KEY=sk-ant-api03-...
LLM_MODEL=deepseek-ai/DeepSeek-V3
FALLBACK_TO_API=true
VLLM_ENGINE=true
QUANTIZATION=8bit

# Hybrid mode: Try local first, fallback to Anthropic
```

### Production Environment
```bash
# .env.production
LLM_MODEL=deepseek-ai/DeepSeek-V3
VLLM_ENGINE=true
QUANTIZATION=8bit
GPU_MEMORY_UTILIZATION=0.9

# Self-hosted only, no external dependencies
```

## 🔄 Migration Strategy

### Phase 1: Pure Anthropic (Current)
All coding agent requests → Anthropic API

### Phase 2: Gradual Migration
- Simple tasks (code completion) → Local LLM
- Complex tasks (code review) → Anthropic API

### Phase 3: Full Self-Hosted
All requests → Local LLM (Anthropic API key removed)

## 📈 Model Selection Guide

### For Development (Anthropic)
| Task | Model | Reasoning |
|------|-------|-----------|
| Code Review | claude-3-opus-20240229 | Best reasoning |
| Code Generation | claude-3-5-sonnet-20241022 | Fast + accurate |
| Code Completion | claude-3-5-sonnet-20241022 | Low latency |
| Debugging | claude-3-opus-20240229 | Deep analysis |

### For Production (Self-Hosted)
| Task | Model | VRAM | Speed |
|------|-------|------|-------|
| All Coding | DeepSeek-V3 (8-bit) | 20GB | 50 tok/s |
| Code Completion | CodeLlama-7B | 7GB | 100 tok/s |
| Long Context | Qwen2.5-Coder-32B | 18GB | 40 tok/s |

## 🛡️ Security Considerations

### Development
- API keys in environment variables only
- Never commit API keys to git
- Use different keys for dev/prod

### Production
- No external API calls
- All data stays on your infrastructure
- Implement rate limiting
- Add authentication layer

## 🔍 Monitoring

### Key Metrics
```bash
# Anthropic API Usage (Development)
- Requests per day
- Token consumption
- Latency (p50, p95, p99)
- Error rate

# Local LLM (Production)
- GPU utilization
- Inference latency
- Throughput (tokens/sec)
- Queue depth
- Model load time
```

### Alerts
- GPU >90% for >5min → Scale up
- Latency p95 >5s → Investigate
- Error rate >1% → Page on-call

## 📚 Quick Start

### Development Mode
```bash
cd /Users/tbwa/Documents/GitHub/insightpulse-odoo/services/ai-inference-hub

# Add your Anthropic API key
export ANTHROPIC_API_KEY=sk-ant-api03-...

# Start service
docker compose up -d

# Test coding agent
curl -X POST http://localhost:8100/v1/agent/code-review \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello(): print(\"hi\")", "language": "python"}'
```

### Production Mode
```bash
# Deploy to GPU droplet
ssh root@gpu-droplet-ip

# Pull latest
cd /root/ai-inference-hub
git pull

# Configure for production
export LLM_MODEL=deepseek-ai/DeepSeek-V3
export VLLM_ENGINE=true
export QUANTIZATION=8bit

# Start with GPU support
docker compose -f docker-compose.gpu.yml up -d
```
