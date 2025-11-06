# AI Inference Hub

Production-ready FastAPI service for OCR using PaddleOCR with non-blocking startup and comprehensive health probes.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
export AI_ENABLE_STT=0
export AI_ENABLE_TTS=0
uvicorn main:app --host 0.0.0.0 --port 8100
```

## Features

- ✅ **Non-blocking startup**: Models load in background, service starts immediately
- ✅ **Health probes**: `/live`, `/health`, `/ready` for orchestration
- ✅ **PaddleOCR**: 88% memory reduction vs DeepSeek (900MB vs 7-8GB)
- ✅ **Production-ready**: Systemd service, proper error handling, logging
- ✅ **Fast**: 1-3s per receipt, 96.97% avg confidence

## Endpoints

- `GET /live` - Liveness probe (instant)
- `GET /health` - Health check with metrics
- `GET /ready` - Readiness probe (true when models loaded)
- `POST /v1/ocr/receipt` - Upload receipt, get structured OCR results
- `POST /v1/ocr` - Legacy endpoint (alias)
- `POST /v1/parse` - Alias for document parsing

## Documentation

- [Architecture Guide](./ARCHITECTURE.md) - System design, health probes, performance
- [Configuration Guide](./CONFIG.md) - Environment variables, systemd setup

## Performance

- **Memory**: 900 MB RSS (idle), 1.1 GB peak
- **Startup**: <1s (FastAPI), 20-30s (models in background)
- **OCR**: 1-3s per receipt, 96.97% avg confidence
- **Cost**: $18/month (2GB droplet) vs $42/month (8GB for DeepSeek)

## Deployment

**Service URL**: `http://188.166.237.231:8100`

```bash
# Systemd service
sudo systemctl status ai-inference-hub
sudo journalctl -u ai-inference-hub -f

# Health check
curl http://127.0.0.1:8100/health

# Test OCR
curl -X POST http://127.0.0.1:8100/v1/ocr/receipt \
  -F "file=@receipt.jpg"
```

## Integration

### Odoo (ip_expense_mvp)

```python
# Settings → AI OCR URL
http://127.0.0.1:8100/v1/ocr/receipt

# Upload endpoint
POST /ip/mobile/receipt (multipart file)
```

### Supabase Analytics

```sql
-- View daily stats
SELECT * FROM analytics.v_ip_ocr_receipts_daily
ORDER BY day DESC LIMIT 14;
```

---

**Version**: 1.0.0 | **Python**: 3.11+ | **License**: LGPL-3
