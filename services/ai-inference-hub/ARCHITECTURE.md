# AI Inference Hub Architecture

## 🎯 Design Philosophy

**Self-Hosted First**: All AI inference runs on your own infrastructure - no external API dependencies for production workloads.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   AI Inference Hub (Port 8100)               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  Document        │  │  Speech          │                 │
│  │  Processing      │  │  Processing      │                 │
│  ├──────────────────┤  ├──────────────────┤                 │
│  │ DeepSeek-OCR 3B  │  │ Whisper (STT)    │                 │
│  │ LangChain        │  │ Coqui TTS        │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                               │
│  ┌────────────────────────────────────────┐                 │
│  │         AI Coding Agents                │                 │
│  ├────────────────────────────────────────┤                 │
│  │ Local LLM Inference (vLLM)              │                 │
│  │ - DeepSeek-V3 (671B/37B MoE)            │                 │
│  │ - CodeLlama (7B-34B)                    │                 │
│  │ - Qwen2.5-Coder (7B-32B)                │                 │
│  │                                          │                 │
│  │ Capabilities:                            │                 │
│  │ • Code Review                            │                 │
│  │ • Code Completion                        │                 │
│  │ • Code Explanation                       │                 │
│  │ • Code Refactoring                       │                 │
│  │ • Code Generation                        │                 │
│  │ • Debugging                              │                 │
│  └────────────────────────────────────────┘                 │
│                                                               │
│  ┌────────────────────────────────────────┐                 │
│  │         Optimization Layer              │                 │
│  ├────────────────────────────────────────┤                 │
│  │ vLLM: High-throughput inference         │                 │
│  │ bitsandbytes: 8-bit/4-bit quantization  │                 │
│  │ accelerate: Multi-GPU support           │                 │
│  │ Model caching: 100GB volume             │                 │
│  └────────────────────────────────────────┘                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
              ┌──────────────────────┐
              │  Supabase (Optional)  │
              ├──────────────────────┤
              │ • Result storage      │
              │ • Usage analytics     │
              │ • Audit logs          │
              └──────────────────────┘
```

## 🤖 Local LLM Options

### Option 1: DeepSeek-V3 (Recommended for Coding)
- **Model**: `deepseek-ai/DeepSeek-V3`
- **Size**: 671B total parameters (37B active MoE)
- **Memory**: ~20GB VRAM (with quantization)
- **Strengths**: State-of-the-art coding, reasoning, math
- **Deployment**: vLLM with 8-bit quantization

### Option 2: CodeLlama
- **Model**: `codellama/CodeLlama-34b-Instruct-hf`
- **Size**: 7B-34B parameters
- **Memory**: 7GB-20GB VRAM
- **Strengths**: Code completion, infilling, debugging
- **Deployment**: vLLM or transformers

### Option 3: Qwen2.5-Coder
- **Model**: `Qwen/Qwen2.5-Coder-32B-Instruct`
- **Size**: 7B-32B parameters
- **Memory**: 7GB-18GB VRAM
- **Strengths**: Multi-language coding, long context
- **Deployment**: vLLM with PagedAttention

## 📊 Deployment Strategies

### Strategy 1: CPU-Only (Current)
- **Hardware**: Standard droplet with 4-8 CPU cores
- **Models**: DeepSeek-OCR, Whisper-base, Coqui TTS
- **Inference**: Slow but cost-effective
- **Best For**: Low-volume workloads, testing

### Strategy 2: Single GPU
- **Hardware**: NVIDIA RTX 4090 (24GB VRAM) or A10 (24GB)
- **Models**: All models including DeepSeek-V3 (quantized)
- **Inference**: ~50 tokens/sec
- **Best For**: Medium-volume production workloads

### Strategy 3: Multi-GPU
- **Hardware**: 2x NVIDIA A100 (80GB each)
- **Models**: DeepSeek-V3 (full precision), all other models
- **Inference**: ~200 tokens/sec
- **Best For**: High-volume enterprise workloads

### Strategy 4: DigitalOcean GPU Droplets (Future)
- **Hardware**: gpu-h100x1-80gb droplet ($4.49/hr)
- **Models**: Any model up to 80GB
- **Inference**: ~300 tokens/sec
- **Best For**: On-demand scaling

## 🚀 Current Deployment

**Location**: OCR Droplet (188.166.237.231)
**Port**: 8100
**Hardware**: 4 CPU cores, 8GB RAM, 100GB model cache volume
**Status**: CPU-only inference for OCR/STT/TTS

## 🔄 Migration Path to GPU

### Phase 1: Add GPU Droplet (Immediate)
```bash
# Create GPU droplet
doctl compute droplet create ai-gpu-inference \
  --size gpu-h100x1-80gb \
  --image ubuntu-24-04-x64 \
  --region nyc3 \
  --ssh-keys 51525133

# Deploy AI Inference Hub with vLLM
docker run -p 8100:8000 \
  --gpus all \
  -v /mnt/models:/models \
  -e LLM_MODEL=deepseek-ai/DeepSeek-V3 \
  -e QUANTIZATION=8bit \
  ai-inference-hub:latest
```

### Phase 2: Load Balancing (Scale)
```
           ┌─────────────┐
           │  Traefik    │
           │  (Port 80)  │
           └──────┬──────┘
                  │
      ┌───────────┴───────────┐
      │                       │
┌─────▼────┐           ┌─────▼────┐
│ CPU Node │           │ GPU Node │
│ (OCR/STT)│           │ (Coding) │
└──────────┘           └──────────┘
```

### Phase 3: Auto-Scaling (Peak Loads)
- Monitor GPU utilization
- Spawn additional GPU nodes when >80% utilized
- Terminate idle nodes after 10 minutes

## 💰 Cost Analysis

### Current (CPU-Only)
- **Droplet**: $24/month (c-4 size)
- **Volume**: $10/month (100GB)
- **Total**: **$34/month**

### GPU Single Node
- **GPU Droplet**: ~$3,200/month (gpu-h100x1-80gb 24/7)
- **OR On-Demand**: $4.49/hr × hours used
- **Volume**: $10/month
- **Total**: **$3,210/month** (24/7) or **$100-500/month** (on-demand)

### Hybrid (Recommended)
- **CPU Node**: $34/month (OCR/STT/TTS)
- **GPU Node**: $4.49/hr × 40hrs/month = $180/month (on-demand coding)
- **Total**: **$214/month** (saves 93% vs 24/7 GPU)

## 🎛️ Configuration

### Environment Variables

```bash
# Model Selection
LLM_MODEL=deepseek-ai/DeepSeek-V3
# Options: deepseek-ai/DeepSeek-V3
#          codellama/CodeLlama-34b-Instruct-hf
#          Qwen/Qwen2.5-Coder-32B-Instruct

# Optimization
QUANTIZATION=8bit
# Options: none, 8bit, 4bit
MAX_MODEL_LEN=8192
GPU_MEMORY_UTILIZATION=0.9

# vLLM Settings
VLLM_ENGINE=true
TENSOR_PARALLEL_SIZE=1
# Set to number of GPUs for multi-GPU

# Existing Settings
MODEL_NAME=deepseek-ai/DeepSeek-OCR
WHISPER_MODEL=base
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
```

## 📈 Performance Benchmarks

### OCR (DeepSeek-OCR 3B)
- **CPU**: ~5s per image
- **GPU**: ~0.5s per image

### STT (Whisper)
- **CPU**: 2x real-time
- **GPU**: 10x real-time

### TTS (Coqui TTS)
- **CPU**: ~3s per sentence
- **GPU**: ~0.3s per sentence

### Coding Agent (DeepSeek-V3 37B active)
- **CPU**: Not practical (>60s per response)
- **GPU (8-bit)**: ~2s per response (50 tokens/sec)
- **GPU (full)**: ~0.5s per response (200 tokens/sec)

## 🔐 Security Considerations

1. **No External APIs**: All inference happens on your infrastructure
2. **Code Isolation**: Sandbox untrusted code execution
3. **Rate Limiting**: Prevent abuse of inference endpoints
4. **Authentication**: Add API keys for production
5. **Audit Logging**: Track all inference requests in Supabase

## 🛠️ Development Roadmap

- [x] **Phase 1**: CPU-based OCR/STT/TTS (Current)
- [ ] **Phase 2**: Add local LLM inference (vLLM integration)
- [ ] **Phase 3**: GPU droplet deployment
- [ ] **Phase 4**: Load balancing and auto-scaling
- [ ] **Phase 5**: Fine-tuning for domain-specific tasks

## 📚 References

- [vLLM Documentation](https://docs.vllm.ai/)
- [DeepSeek-V3 Paper](https://github.com/deepseek-ai/DeepSeek-V3)
- [DigitalOcean GPU Droplets](https://www.digitalocean.com/products/droplets/gpu)
