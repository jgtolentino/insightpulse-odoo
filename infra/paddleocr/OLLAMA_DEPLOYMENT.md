# Ollama LLM Deployment on OCR Droplet

**Self-hosted Llama 3.2 3B on PaddleOCR droplet**

## Overview

Ollama has been integrated into the PaddleOCR droplet to provide self-hosted LLM capabilities at $0 API cost. This deployment runs Llama 3.2 3B (2GB model) alongside PaddleOCR on a shared 4GB droplet.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│          DigitalOcean Droplet (s-2vcpu-4gb, $24/mo)        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Nginx Reverse Proxy                                  │  │
│  │  - ocr.insightpulseai.net → :8000 (PaddleOCR)       │  │
│  │  - llm.insightpulseai.net → :11434 (Ollama)         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ PaddleOCR       │  │ Ollama       │  │ Redis        │  │
│  │ 768MB limit     │  │ 2GB limit    │  │ 128MB        │  │
│  │ Port: 8000      │  │ Port: 11434  │  │              │  │
│  │ CPU: 0.9        │  │ CPU: 0.8     │  │              │  │
│  └─────────────────┘  └──────────────┘  └──────────────┘  │
│                                                             │
│  Resources:                                                 │
│  - 4GB RAM (768MB + 2GB + 128MB + 1GB system)             │
│  - 2 vCPU (shared)                                          │
│  - 4GB Swap                                                 │
│  - ~5GB disk (models + system)                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ HTTPS
                          ▼
              ┌──────────────────────┐
              │ Odoo on App Platform │
              │ (uses ai.insightpulseai.net) │
              └──────────────────────┘
```

## Cost Breakdown

| Service | Tier | Monthly Cost | Details |
|---------|------|--------------|---------|
| **DigitalOcean Droplet** | s-2vcpu-4gb | **$24/month** | PaddleOCR + Ollama + Redis |
| **Supabase PostgreSQL** | Free | $0 | 500MB DB, 2GB bandwidth |
| **DigitalOcean App Platform** | basic-xxs | $5 | 512MB RAM, 1 vCPU |
| **Total** | | **$29/month** | |

**Previous cost**: $5/month (no LLM)
**New cost**: $29/month (self-hosted LLM)
**Savings vs OpenAI**: ~$15/month (assuming moderate usage)

## Deployment

### Prerequisites

1. DigitalOcean account with API token
2. `doctl` CLI installed and authenticated
3. SSH key added to DigitalOcean: `insightpulse-deploy`
4. Domain `insightpulseai.net` configured in DigitalOcean DNS

### Deploy Everything

```bash
cd /home/user/insightpulse-odoo

# Deploy droplet with PaddleOCR + Ollama
bash infra/paddleocr/deploy-droplet.sh
```

The script will:
1. Create 4GB droplet in Singapore ($24/month)
2. Configure DNS for `ocr.insightpulseai.net` and `llm.insightpulseai.net`
3. Install Docker, Docker Compose, Nginx
4. Configure firewall (ports 22, 80, 443, 8000, 11434)
5. Deploy PaddleOCR + Ollama services
6. Pull Llama 3.2 3B model (~2GB download)
7. Configure SSL with Certbot

### Manual Steps (if needed)

#### 1. Deploy Droplet

```bash
cd /home/user/insightpulse-odoo

# Deploy
bash infra/paddleocr/deploy-droplet.sh

# Get droplet IP
DROPLET_IP=$(cat infra/paddleocr/.droplet_ip)
echo "Droplet IP: $DROPLET_IP"
```

#### 2. Configure SSL

```bash
# SSH into droplet
ssh root@$DROPLET_IP

# Configure SSL for both domains
certbot --nginx -d ocr.insightpulseai.net -d llm.insightpulseai.net \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive
```

#### 3. Initialize Ollama (if not done automatically)

```bash
# SSH into droplet
ssh root@$DROPLET_IP

# Run initialization script
cd /opt/paddleocr
bash init-ollama.sh
```

## Testing

### Test PaddleOCR

```bash
curl -X POST https://ocr.insightpulseai.net/api/v1/ocr/scan \
  -H "Content-Type: multipart/form-data" \
  -F "image=@/path/to/image.jpg"
```

### Test Ollama

```bash
# List models
curl https://llm.insightpulseai.net/api/tags

# Generate completion
curl -X POST https://llm.insightpulseai.net/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "prompt": "Explain what Odoo ERP is in one sentence",
    "stream": false
  }'
```

### Test from Odoo

The Odoo instance is configured to use `https://ai.insightpulseai.net` via environment variables:

```yaml
# infra/do/odoo-saas-platform.yaml
- key: AI_PROVIDER
  value: "ollama"
- key: OLLAMA_BASE_URL
  value: "https://llm.insightpulseai.net"
- key: OLLAMA_MODEL
  value: "llama3.2:3b"
```

## Monitoring

### View Logs

```bash
# SSH into droplet
ssh root@$DROPLET_IP

# View all services
cd /opt/paddleocr
docker-compose logs -f

# View Ollama specifically
docker-compose logs -f ollama

# View PaddleOCR
docker-compose logs -f paddleocr
```

### Resource Usage

```bash
# Check memory usage
docker stats

# Check disk usage
df -h
du -sh /var/lib/docker/volumes/
```

### Health Checks

```bash
# PaddleOCR health
curl https://ocr.insightpulseai.net/health

# Ollama health
curl https://llm.insightpulseai.net/api/tags
```

## Performance

### Llama 3.2 3B Performance

- **Inference time**: 2-5 seconds for simple queries
- **Context window**: 4096 tokens
- **Memory usage**: ~1.5-2GB when model is loaded
- **Keep-alive**: 5 minutes (configurable)

### Resource Limits

- **PaddleOCR**: 768MB RAM, 0.9 CPU
- **Ollama**: 2048MB RAM, 0.8 CPU
- **Redis**: 128MB RAM
- **System**: ~1GB RAM

## Troubleshooting

### Ollama service not starting

```bash
# Check logs
docker logs ollama-service

# Check if port is available
netstat -tuln | grep 11434

# Restart service
docker-compose restart ollama
```

### Model download fails

```bash
# Pull model manually
docker exec ollama-service ollama pull llama3.2:3b

# Check disk space
df -h

# Check available models
docker exec ollama-service ollama list
```

### Out of memory

```bash
# Check memory usage
free -h

# Check swap
swapon --show

# Reduce resource limits in docker-compose.yml
# Or upgrade droplet to s-4vcpu-8gb ($48/month)
```

### Slow inference

This is expected on a 2-vCPU shared instance. Options:
1. Upgrade to CPU-optimized droplet (c-2 @ $42/month)
2. Use GPU droplet (g-2vcpu-8gb @ $90/month)
3. Keep current setup - 2-5s inference is acceptable for non-real-time tasks

## Maintenance

### Update Ollama

```bash
ssh root@$DROPLET_IP
cd /opt/paddleocr
docker-compose pull ollama
docker-compose up -d ollama
```

### Update Llama Model

```bash
# Pull latest model
docker exec ollama-service ollama pull llama3.2:3b

# Or switch to different model
docker exec ollama-service ollama pull llama3.2:1b  # Smaller, faster
docker exec ollama-service ollama pull codellama:7b  # Better for code
```

### Backup Configuration

```bash
# Backup docker-compose and configs
scp root@$DROPLET_IP:/opt/paddleocr/docker-compose.yml ./backup/
scp root@$DROPLET_IP:/opt/paddleocr/.env ./backup/

# Backup Nginx configs
scp root@$DROPLET_IP:/etc/nginx/sites-available/* ./backup/nginx/
```

## Scaling

### Current Limits

- **Concurrent requests**: 1-2 (single model instance)
- **Max queries/day**: ~10,000 (assuming 5s avg inference)
- **Cost**: $24/month fixed

### Upgrade Paths

**Phase 1: Optimize Current Setup** ($24/month)
- Fine-tune resource limits
- Implement request queuing
- Add Redis caching for common queries

**Phase 2: Upgrade Droplet** ($48/month)
- s-4vcpu-8gb (8GB RAM, 4 vCPU)
- Run multiple model instances
- Support 5-10 concurrent requests

**Phase 3: Dedicated GPU** ($90-180/month)
- GPU-enabled droplet
- 10x faster inference (200-500ms)
- Support real-time use cases

## Security

### Current Configuration

- ✅ Firewall enabled (UFW)
- ✅ Fail2ban active
- ✅ SSL/TLS with Let's Encrypt
- ✅ Rate limiting (Nginx)
- ✅ Non-root Docker containers
- ✅ Metrics endpoint protected (internal IPs only)

### Recommendations

- [ ] Add API authentication (API keys)
- [ ] Implement request logging and audit trail
- [ ] Set up monitoring alerts (Uptime Robot, etc.)
- [ ] Regular security updates (automated with unattended-upgrades)

## Next Steps

1. **Deploy**: Run `bash infra/paddleocr/deploy-droplet.sh`
2. **Test**: Verify both OCR and Ollama endpoints work
3. **Configure Odoo**: Update Odoo to use new Ollama endpoint (already done in `odoo-saas-platform.yaml`)
4. **Monitor**: Set up monitoring and alerts
5. **Optimize**: Fine-tune resource limits based on actual usage

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review Ollama docs: https://ollama.ai/docs
- Check Llama 3.2 docs: https://huggingface.co/meta-llama/Llama-3.2-3B

---

**Deployed**: 2025-11-04
**Version**: 1.0.0
**Model**: Llama 3.2 3B
**Cost**: $24/month (droplet) + $5/month (Odoo) = **$29/month total**
