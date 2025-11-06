# AI Inference Hub - Configuration Guide

## Environment Variables

### Core Settings

#### `PORT`
- **Default**: `8100`
- **Description**: HTTP server port
- **Example**: `PORT=8080`

#### `HOST`
- **Default**: `0.0.0.0`
- **Description**: Bind address (0.0.0.0 = all interfaces)
- **Example**: `HOST=127.0.0.1` (localhost only)

#### `LOG_LEVEL`
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Example**: `LOG_LEVEL=DEBUG`

### Feature Flags

#### `AI_ENABLE_STT`
- **Default**: `0`
- **Description**: Enable Speech-To-Text models
- **Values**: `0` (disabled), `1` (enabled)
- **Impact**: +2GB memory, +60s startup time
- **Use Case**: Audio transcription (not needed for receipt OCR)

#### `AI_ENABLE_TTS`
- **Default**: `0`
- **Description**: Enable Text-To-Speech models
- **Values**: `0` (disabled), `1` (enabled)
- **Impact**: +1.5GB memory, +45s startup time
- **Use Case**: Voice synthesis (not needed for receipt OCR)

#### `AI_ENABLE_OCR`
- **Default**: `1`
- **Description**: Enable OCR models (PaddleOCR)
- **Values**: `0` (disabled), `1` (enabled)
- **Impact**: +900MB memory, +20s startup time
- **Use Case**: Receipt/document text extraction

### PaddleOCR Settings

#### `PADDLEOCR_LANG`
- **Default**: `en`
- **Options**: `en`, `ch`, `fr`, `german`, `korean`, `japan`
- **Description**: OCR language pack
- **Example**: `PADDLEOCR_LANG=ch` (Chinese)

#### `PADDLEOCR_USE_GPU`
- **Default**: `false`
- **Options**: `true`, `false`
- **Description**: Enable CUDA GPU acceleration
- **Requirements**: NVIDIA GPU, CUDA 11.x, cuDNN
- **Performance**: 5-10x faster inference

#### `PADDLEOCR_DET_MODEL`
- **Default**: `ch_PP-OCRv4_det`
- **Description**: Text detection model
- **Options**: See [PaddleOCR Models](https://github.com/PaddlePaddle/PaddleOCR)

#### `PADDLEOCR_REC_MODEL`
- **Default**: `ch_PP-OCRv4_rec`
- **Description**: Text recognition model

#### `PADDLEOCR_SHOW_LOG`
- **Default**: `false`
- **Options**: `true`, `false`
- **Description**: Enable verbose PaddleOCR logs

### Supabase Integration

#### `SUPABASE_URL`
- **Required**: No (optional analytics sink)
- **Description**: Supabase project URL
- **Example**: `https://xxx.supabase.co`
- **Use Case**: OCR result storage for analytics

#### `SUPABASE_SERVICE_ROLE_KEY`
- **Required**: No (if `SUPABASE_URL` is set)
- **Description**: Service role key (server-side only)
- **Example**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **Security**: Never expose to client; use environment variables

### Performance Tuning

#### `UVICORN_WORKERS`
- **Default**: `1`
- **Description**: Number of Uvicorn worker processes
- **Recommendation**: `1` (models loaded per-worker, high memory cost)
- **Formula**: `workers * 1GB = total memory`

#### `UVICORN_TIMEOUT_KEEP_ALIVE`
- **Default**: `5`
- **Description**: Keep-alive timeout (seconds)
- **Use Case**: Load balancer connection pooling

#### `MAX_UPLOAD_SIZE_MB`
- **Default**: `10`
- **Description**: Maximum file upload size (MB)
- **Example**: `MAX_UPLOAD_SIZE_MB=20`

#### `OCR_TIMEOUT_SECONDS`
- **Default**: `30`
- **Description**: OCR processing timeout per request
- **Example**: `OCR_TIMEOUT_SECONDS=60` (large images)

### Resource Limits (Systemd)

#### `MemoryMax`
- **Recommended**: `2G`
- **Description**: Hard memory limit (OOM if exceeded)
- **Config File**: `/etc/systemd/system/ai-inference-hub.service`
- **Example**:
  ```ini
  [Service]
  MemoryMax=2G
  ```

#### `TimeoutStartSec`
- **Recommended**: `900` (15 minutes)
- **Description**: Grace period for first-time model downloads
- **After First Boot**: Models cached, startup <30s
- **Example**:
  ```ini
  [Service]
  TimeoutStartSec=900
  ```

## Configuration Files

### Systemd Service (`/etc/systemd/system/ai-inference-hub.service`)

**Production Configuration**:
```ini
[Unit]
Description=AI Inference Hub (PaddleOCR)
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/root/ai-inference-hub
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8100

# Feature flags (disable unused models)
Environment="AI_ENABLE_STT=0"
Environment="AI_ENABLE_TTS=0"
Environment="AI_ENABLE_OCR=1"

# PaddleOCR settings
Environment="PADDLEOCR_LANG=en"
Environment="PADDLEOCR_USE_GPU=false"
Environment="PADDLEOCR_SHOW_LOG=false"

# Performance
Environment="LOG_LEVEL=INFO"
Environment="MAX_UPLOAD_SIZE_MB=10"

# Resource limits
MemoryMax=2G
TimeoutStartSec=900

# Restart policy
Restart=on-failure
RestartSec=10
StartLimitInterval=300
StartLimitBurst=5

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ai-inference-hub

[Install]
WantedBy=multi-user.target
```

**Enable and Start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-inference-hub
sudo systemctl start ai-inference-hub
sudo systemctl status ai-inference-hub
```

### Docker Compose (`docker-compose.yml`)

**Production Configuration**:
```yaml
version: '3.8'

services:
  ai-inference-hub:
    build: .
    ports:
      - "8100:8100"
    environment:
      - AI_ENABLE_STT=0
      - AI_ENABLE_TTS=0
      - AI_ENABLE_OCR=1
      - PADDLEOCR_LANG=en
      - PADDLEOCR_USE_GPU=false
      - LOG_LEVEL=INFO
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
    volumes:
      - ./models:/root/.paddleocr  # Cache models
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8100/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped
```

**Run**:
```bash
docker-compose up -d
docker-compose logs -f
```

## Configuration Examples

### Development (Local)

**Scenario**: Fast startup, verbose logging, localhost only

```bash
export PORT=8100
export HOST=127.0.0.1
export LOG_LEVEL=DEBUG
export AI_ENABLE_STT=0
export AI_ENABLE_TTS=0
export PADDLEOCR_SHOW_LOG=true

uvicorn main:app --reload
```

### Production (Cloud)

**Scenario**: Optimized for 2GB RAM droplet, minimal logs

```bash
export PORT=8100
export HOST=0.0.0.0
export LOG_LEVEL=INFO
export AI_ENABLE_STT=0
export AI_ENABLE_TTS=0
export PADDLEOCR_LANG=en
export PADDLEOCR_USE_GPU=false
export PADDLEOCR_SHOW_LOG=false
export MAX_UPLOAD_SIZE_MB=10
export OCR_TIMEOUT_SECONDS=30

uvicorn main:app --host 0.0.0.0 --port 8100
```

### High-Performance (GPU)

**Scenario**: GPU-accelerated, high throughput

```bash
export PORT=8100
export AI_ENABLE_OCR=1
export PADDLEOCR_USE_GPU=true
export PADDLEOCR_LANG=en
export UVICORN_WORKERS=4  # Multiple workers
export MAX_UPLOAD_SIZE_MB=20
export OCR_TIMEOUT_SECONDS=60

# Requires: NVIDIA GPU, CUDA 11.x, cuDNN
uvicorn main:app --host 0.0.0.0 --port 8100 --workers 4
```

### Multi-Language (Asian Markets)

**Scenario**: Support English + Chinese receipts

```bash
export PADDLEOCR_LANG=ch  # Chinese + English
export AI_ENABLE_OCR=1
export MAX_UPLOAD_SIZE_MB=15
export OCR_TIMEOUT_SECONDS=45

uvicorn main:app --host 0.0.0.0 --port 8100
```

## Configuration Validation

### Health Check

Verify configuration is working:

```bash
curl http://127.0.0.1:8100/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "available_endpoints": ["/v1/ocr/receipt", "/v1/ocr", "/v1/parse"],
  "memory_mb": 939,
  "uptime_seconds": 120,
  "config": {
    "ocr_enabled": true,
    "stt_enabled": false,
    "tts_enabled": false,
    "paddleocr_lang": "en",
    "use_gpu": false
  }
}
```

### Test OCR

Upload test receipt:

```bash
curl -X POST http://127.0.0.1:8100/v1/ocr/receipt \
  -F "file=@test_receipt.jpg"
```

**Expected Response**:
```json
{
  "lines": [
    {
      "text": "GROCERY STORE",
      "confidence": 0.98,
      "bbox": [[10,20], [200,20], [200,40], [10,40]]
    }
  ],
  "line_count": 15,
  "avg_confidence": 0.9697,
  "processing_time_ms": 1234
}
```

## Troubleshooting Configuration

### Models Not Loading

**Symptom**: `/ready` returns `{"ready": false}`

**Check**:
```bash
journalctl -u ai-inference-hub -n 50
# Look for "Loading PaddleOCR models..."
# Check for download errors
```

**Fix**:
- Verify internet connectivity
- Check disk space (`df -h`)
- Increase `TimeoutStartSec` if slow network

### Out of Memory

**Symptom**: Service crashes with OOM error

**Check**:
```bash
dmesg | grep -i "out of memory"
journalctl -u ai-inference-hub | grep -i "memory"
```

**Fix**:
- Disable unused features (`AI_ENABLE_STT=0`)
- Reduce workers (`UVICORN_WORKERS=1`)
- Increase `MemoryMax` or upgrade droplet

### Port Already in Use

**Symptom**: `Address already in use` error

**Check**:
```bash
sudo lsof -i :8100
```

**Fix**:
```bash
# Kill existing process
sudo kill -9 $(sudo lsof -t -i:8100)

# Or change port
export PORT=8101
```

### Slow OCR Processing

**Symptom**: Requests timeout or take >30 seconds

**Check**:
- Image size (resize to <2MB)
- CPU usage (`top`)
- Memory available (`free -h`)

**Fix**:
- Enable GPU: `PADDLEOCR_USE_GPU=true`
- Increase timeout: `OCR_TIMEOUT_SECONDS=60`
- Reduce image quality before upload

## Security Considerations

### Environment Variables

**Never expose in code**:
```python
# ❌ BAD
supabase_key = "eyJhbGci..."

# ✅ GOOD
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
```

**Store in systemd service**:
```ini
[Service]
Environment="SUPABASE_SERVICE_ROLE_KEY=eyJhbGci..."
```

### Network Security

**Firewall Rules** (UFW):
```bash
# Allow only from Odoo server
sudo ufw allow from 192.168.1.100 to any port 8100

# Or allow all (behind nginx)
sudo ufw allow 8100/tcp
```

**Nginx Reverse Proxy** (recommended):
```nginx
server {
    listen 80;
    server_name ocr.insightpulseai.net;

    location / {
        proxy_pass http://127.0.0.1:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # Rate limiting
        limit_req zone=ocr_limit burst=10;
    }
}
```

### Input Validation

**File Size Limit**:
```python
@app.post("/v1/ocr/receipt")
async def ocr_receipt(file: UploadFile):
    # Validate size
    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(413, "File too large")
```

**Content-Type Validation**:
```python
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
if file.content_type not in ALLOWED_TYPES:
    raise HTTPException(400, "Invalid file type")
```

## Related Documentation

- [Architecture Guide](./ARCHITECTURE.md) - System design and architecture
- [API Reference](./API.md) - Full endpoint documentation (TODO)
- [Deployment Guide](./DEPLOYMENT.md) - Production deployment (TODO)

---

**Last Updated**: 2025-11-06
**Service Version**: 1.0.0
