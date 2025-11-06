# AI Inference Hub - Architecture

## Overview

The AI Inference Hub is a production-ready FastAPI service providing OCR capabilities using PaddleOCR. It features non-blocking startup, comprehensive health probes, and optimized memory usage for cloud deployment.

**Service URL**: `http://188.166.237.231:8100`

## Key Features

### 1. Non-Blocking Startup with Background Model Loading

**Problem Solved**: Previously, model loading blocked the entire application startup, causing health check failures and deployment timeouts in orchestration platforms (Kubernetes, DigitalOcean App Platform).

**Solution**: Models load in a separate background thread while the FastAPI server starts immediately and responds to health checks.

```python
# Main application
app = FastAPI(
    title="AI Inference Hub",
    version="1.0.0",
    lifespan=lifespan
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - start model loading in background."""
    # Start background model loading
    thread = threading.Thread(target=load_models_background, daemon=True)
    thread.start()

    yield  # Application runs

    # Cleanup on shutdown (if needed)
```

**Benefits**:
- FastAPI server starts in <1 second
- Health probes respond immediately during model loading
- No orchestration timeouts (900s grace period no longer needed in production)
- Graceful degradation: Service is "alive" but "not ready" until models load

### 2. Comprehensive Health Probes

Three distinct endpoints for different monitoring purposes:

#### `/live` - Liveness Probe
- **Purpose**: Kubernetes/DO liveness check
- **Response Time**: Instant (always returns immediately)
- **Use Case**: Determines if the service should be restarted
- **Example**:
  ```bash
  curl http://127.0.0.1:8100/live
  # {"status":"alive"}
  ```

#### `/health` - General Health Check
- **Purpose**: Overall service health including model loading state
- **Response Time**: Instant (non-blocking)
- **Returns**: Service status, model loading progress, memory usage
- **Example**:
  ```bash
  curl http://127.0.0.1:8100/health
  {
    "status": "healthy",
    "models_loaded": true,
    "available_endpoints": ["/v1/ocr/receipt", "/v1/ocr", "/v1/parse"],
    "memory_mb": 939,
    "uptime_seconds": 3600
  }
  ```

#### `/ready` - Readiness Probe
- **Purpose**: Kubernetes/DO readiness check
- **Response Time**: Instant
- **Use Case**: Determines if the service should receive traffic
- **Returns**: `true` only when OCR models are fully loaded
- **Example**:
  ```bash
  curl http://127.0.0.1:8100/ready
  {"ready":true,"models_loaded":true}
  ```

**Orchestration Integration**:
```yaml
# Kubernetes/DigitalOcean App Platform config
livenessProbe:
  httpGet:
    path: /live
    port: 8100
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8100
  initialDelaySeconds: 30
  periodSeconds: 5
```

### 3. OCR Endpoints

#### `/v1/ocr/receipt` - Production OCR Endpoint
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Input**: Image file (JPEG, PNG, etc.)
- **Output**: Structured `OCRResponse` with line-by-line extraction
- **Response Schema**:
  ```json
  {
    "lines": [
      {
        "text": "TOTAL AMOUNT",
        "confidence": 0.9697,
        "bbox": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
      }
    ],
    "line_count": 22,
    "avg_confidence": 0.9697,
    "processing_time_ms": 1234
  }
  ```

#### `/v1/ocr` - Legacy Compatibility
- Maintained for backward compatibility with existing clients
- Same functionality as `/v1/ocr/receipt`

#### `/v1/parse` - Alias
- Convenience alias for document parsing workflows

**Example Usage**:
```bash
curl -X POST http://127.0.0.1:8100/v1/ocr/receipt \
  -F "file=@receipt.jpg"
```

## Architecture Decisions

### Why PaddleOCR?

**Before (DeepSeek-OCR)**:
- Memory: 7-8 GB RSS
- Model size: ~6 GB download
- Startup time: 120-180 seconds
- Cloud cost: Requires 8GB+ RAM droplets

**After (PaddleOCR)**:
- Memory: 0.9-1.1 GB RSS (**88% reduction**)
- Model size: ~100 MB download
- Startup time: 20-30 seconds (background, non-blocking)
- Cloud cost: Works on 2GB RAM droplets ($18/month vs $42/month)

**Cost Savings**: ~$288/year per service instance

### Feature Flags

Environment variables to disable unused features:

```bash
AI_ENABLE_STT=0  # Disable speech-to-text (not needed for receipt OCR)
AI_ENABLE_TTS=0  # Disable text-to-speech (not needed)
```

**Benefits**:
- Faster startup (no unused model downloads)
- Lower memory footprint
- Simpler debugging (fewer moving parts)

### Threading Model

- **Main Thread**: FastAPI/Uvicorn HTTP server
- **Background Thread**: Model loading (runs once at startup)
- **Worker Threads**: PaddleOCR inference (thread-safe)

**Why Threading over Async**:
- PaddleOCR is CPU-bound, not I/O-bound
- Global Interpreter Lock (GIL) doesn't hurt CPU inference
- Simpler code vs multiprocessing
- Models shared in memory across requests

## Performance Metrics

### Memory Usage
- **Idle**: ~900 MB RSS
- **During OCR**: ~1.0 GB RSS peak
- **Available**: 1.2 GB (on 2GB droplet)
- **Swap**: Disabled (not needed)

### OCR Performance
- **Average Confidence**: 96.97%
- **Lines Extracted**: 20-30 per receipt
- **Processing Time**: 1-3 seconds per image
- **Throughput**: ~20-30 receipts/minute (single instance)

### Startup Performance
- **FastAPI Start**: <1 second
- **Model Loading**: 20-30 seconds (background)
- **First Request Ready**: 20-30 seconds (readiness probe)

## Deployment

### Systemd Service

**Service File**: `/etc/systemd/system/ai-inference-hub.service`

Key configurations:
```ini
[Service]
Type=notify       # FastAPI notifies systemd when ready
TimeoutStartSec=900   # 15min grace period for model downloads (first boot)
Restart=on-failure    # Only restart on crashes, not on success exit
MemoryMax=2G      # Limit to 2GB (prevents OOM on shared droplet)

# Feature flags
Environment="AI_ENABLE_STT=0"
Environment="AI_ENABLE_TTS=0"
```

**Why `TimeoutStartSec=900`?**
- First-time model download can take 5-10 minutes
- After first boot, models are cached (startup <30s)
- Prevents systemd from killing during legitimate initialization

**Why `Restart=on-failure`?**
- Prevents restart loops during intentional shutdowns
- Only restarts on crashes (exit code != 0)
- Allows graceful admin shutdowns

### Container Deployment (Optional)

```dockerfile
FROM python:3.11-slim

# Install PaddleOCR dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV AI_ENABLE_STT=0 AI_ENABLE_TTS=0

EXPOSE 8100
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]
```

## Security

### Network Security
- Service binds to `0.0.0.0:8100` (accepts external traffic)
- **Recommendation**: Place behind nginx reverse proxy with rate limiting
- **Firewall**: Only allow traffic from Odoo server IPs

### Input Validation
- File size limit: 10 MB (configurable)
- Allowed formats: JPEG, PNG, WEBP, BMP
- Content-Type validation
- Malicious file detection (via Pillow SafeImage)

### Secrets Management
- No API keys required (PaddleOCR is local)
- Supabase credentials stored as environment variables (not in code)
- Log sanitization (no PII in logs)

## Monitoring

### Health Check Monitoring

**Uptime Monitoring** (e.g., UptimeRobot, Pingdom):
```bash
# Check every 1 minute
GET http://188.166.237.231:8100/health
# Alert if status != "healthy" for 3 consecutive checks
```

**Readiness Monitoring** (for auto-scaling):
```bash
# Check every 30 seconds
GET http://188.166.237.231:8100/ready
# Scale up if ready==false for 2+ minutes (model reload)
```

### Application Logs

**Log Locations**:
- **Systemd**: `journalctl -u ai-inference-hub -f`
- **Container**: `docker logs ai-inference-hub`

**Key Log Events**:
- `Loading PaddleOCR models...` - Model loading started
- `Models loaded successfully` - Ready to serve traffic
- `OCR processing time: Xms` - Per-request performance
- `Memory usage: XMB` - Periodic memory checks

### Metrics Export (Future)

Consider adding Prometheus metrics:
```python
from prometheus_client import Counter, Histogram

ocr_requests_total = Counter('ocr_requests_total', 'Total OCR requests')
ocr_processing_time = Histogram('ocr_processing_seconds', 'OCR processing time')
```

## Troubleshooting

### Service Won't Start

**Check Logs**:
```bash
sudo journalctl -u ai-inference-hub -n 100 --no-pager
```

**Common Issues**:
1. **Port 8100 already in use**: Kill existing process or change port
2. **Out of memory**: Increase MemoryMax or upgrade droplet
3. **Model download fails**: Check internet connectivity, retry

### OCR Returns Empty Results

**Check Image**:
- Image is readable (not corrupted)
- Text is clear (not blurry/low-res)
- Image size <10 MB

**Check Logs**:
```bash
curl http://127.0.0.1:8100/health
# Verify models_loaded=true
```

### High Memory Usage

**Expected**: 900-1100 MB
**High**: >1500 MB (investigate memory leak)

**Debug**:
```bash
# Check memory per-process
ps aux | grep uvicorn

# Monitor real-time
watch -n 1 'ps aux | grep uvicorn'
```

## Future Enhancements

1. **Multi-Model Support**: Add Tesseract, EasyOCR options
2. **Batch Processing**: Process multiple receipts in single request
3. **Async Workers**: Celery/RQ for long-running jobs
4. **Result Caching**: Cache OCR results (hash-based)
5. **A/B Testing**: Compare PaddleOCR vs other engines
6. **GPU Support**: CUDA acceleration for higher throughput

## Related Documentation

- [Configuration Guide](./CONFIG.md) - Environment variables and settings
- [API Reference](./API.md) - Full endpoint documentation (TODO)
- [Deployment Guide](./DEPLOYMENT.md) - Production deployment steps (TODO)

---

**Last Updated**: 2025-11-06
**Service Version**: 1.0.0
**Python**: 3.11+
**FastAPI**: 0.104+
**PaddleOCR**: 2.7+
