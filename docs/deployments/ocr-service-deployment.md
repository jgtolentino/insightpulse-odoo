# OCR Service Deployment Guide

## Droplet Information

- **Name**: `ocr-service-droplet`
- **Workspace**: `fin-workspace`
- **Region**: SGP1 (Singapore)
- **Resources**: 4 GB Memory / 80 GB Disk + 100 GB
- **OS**: Docker on Ubuntu 22.04
- **IPv4**: `188.166.237.231`
- **Private IP**: `10.104.0.2`
- **Domain**: `ocr.insightpulseai.net`

## DNS Configuration

```
ocr.insightpulseai.net → Cloudflare Proxy (162.159.140.98) → Origin (188.166.237.231)
```

The domain is behind Cloudflare for:
- SSL/TLS termination
- DDoS protection
- WAF (Web Application Firewall)
- Caching and CDN

## Initial Droplet Setup

### 1. Connect via SSH

```bash
ssh root@188.166.237.231
```

### 2. Install Docker

```bash
# Update package index
apt update

# Install prerequisites
apt install -y ca-certificates curl gnupg

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
apt update
apt install -y docker-ce docker-ce-cli containerd.io \
               docker-buildx-plugin docker-compose-plugin

# Verify installation
docker run --rm hello-world
```

### 3. Configure Firewall

```bash
# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp  # SSH (if not already allowed)

# Reload firewall
ufw reload
ufw status
```

## OCR Service Deployment Options

### Option 1: PaddleOCR (Recommended)

PaddleOCR provides excellent multi-language support with good accuracy.

```bash
# Pull and run PaddleOCR service
docker run -d \
  --name paddleocr-service \
  -p 80:8000 \
  --restart unless-stopped \
  -e LANG=en,fil \
  paddlepaddle/paddleocr:latest-cpu

# Or with GPU support (if available)
docker run -d \
  --name paddleocr-service \
  -p 80:8000 \
  --gpus all \
  --restart unless-stopped \
  -e LANG=en,fil \
  paddlepaddle/paddleocr:latest-gpu
```

### Option 2: Tesseract OCR

```bash
# Create Dockerfile
cat > /opt/ocr/Dockerfile <<'EOF'
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pytesseract pillow fastapi uvicorn python-multipart

WORKDIR /app
COPY app.py .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create FastAPI app
cat > /opt/ocr/app.py <<'EOF'
from fastapi import FastAPI, File, UploadFile
from PIL import Image
import pytesseract
import io

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/ocr")
async def perform_ocr(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    text = pytesseract.image_to_string(image)
    return {"text": text}
EOF

# Build and run
cd /opt/ocr
docker build -t ocr-service .
docker run -d \
  --name ocr-service \
  -p 80:8000 \
  --restart unless-stopped \
  ocr-service
```

### Option 3: Custom OCR with Multiple Engines

For BIR form processing and receipt validation:

```bash
# Clone InsightPulse OCR service
git clone https://github.com/jgtolentino/insightpulse-ocr.git /opt/ocr-service
cd /opt/ocr-service

# Build from existing Dockerfile
docker build -t insightpulse-ocr .

# Run with environment variables
docker run -d \
  --name ocr-service \
  -p 80:8000 \
  --restart unless-stopped \
  -e SUPABASE_URL="${SUPABASE_URL}" \
  -e SUPABASE_KEY="${SUPABASE_KEY}" \
  -e OCR_ENGINE=paddleocr \
  insightpulse-ocr
```

## Nginx Reverse Proxy (Optional)

If you want to add an Nginx layer for advanced routing:

```bash
# Install Nginx
apt install -y nginx

# Configure OCR service proxy
cat > /etc/nginx/sites-available/ocr <<'EOF'
server {
    listen 80;
    server_name ocr.insightpulseai.net;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/ocr /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## Cloudflare Configuration

### DNS Settings

Ensure Cloudflare DNS is configured:

```
Type: A
Name: ocr
Content: 188.166.237.231
Proxy status: Proxied (orange cloud)
TTL: Auto
```

### SSL/TLS Settings

- **SSL/TLS encryption mode**: Full (strict)
- **Always Use HTTPS**: Enabled
- **Minimum TLS Version**: TLS 1.2
- **Opportunistic Encryption**: Enabled
- **TLS 1.3**: Enabled

### Firewall Rules (Optional)

Add rate limiting for OCR endpoint:

```
Rule: OCR Rate Limit
Expression: (http.host eq "ocr.insightpulseai.net")
Action: Rate Limit (100 requests per minute)
```

## Health Check

```bash
# From the droplet
curl http://localhost/health

# From external
curl https://ocr.insightpulseai.net/health
```

## Monitoring

### Container Logs

```bash
# View real-time logs
docker logs -f ocr-service

# View last 100 lines
docker logs --tail 100 ocr-service
```

### Container Status

```bash
# Check running containers
docker ps

# Check resource usage
docker stats ocr-service
```

## Troubleshooting

### Service Not Responding

```bash
# Check if container is running
docker ps -a | grep ocr-service

# Restart container
docker restart ocr-service

# Check logs for errors
docker logs ocr-service
```

### High Memory Usage

```bash
# Check memory usage
docker stats ocr-service

# Restart with memory limit
docker stop ocr-service
docker rm ocr-service
docker run -d \
  --name ocr-service \
  -p 80:8000 \
  --memory="3g" \
  --restart unless-stopped \
  ocr-service
```

### Cloudflare 403 Errors

If legitimate requests are blocked:

1. Go to Cloudflare Dashboard → Security → WAF
2. Check Security Events for blocked requests
3. Add firewall rule to allow your IP or specific user agents
4. Consider adding rate limiting instead of blocking

## Backup and Updates

### Backup Configuration

```bash
# Backup Docker volumes
docker run --rm \
  -v ocr-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/ocr-data-backup.tar.gz -C /data .
```

### Update Service

```bash
# Pull latest image
docker pull your-registry/ocr-service:latest

# Stop and remove old container
docker stop ocr-service
docker rm ocr-service

# Run new container
docker run -d \
  --name ocr-service \
  -p 80:8000 \
  --restart unless-stopped \
  your-registry/ocr-service:latest
```

## Integration with InsightPulse

The OCR service integrates with:

- **Odoo ERP** (`erp.insightpulseai.net`) - Invoice/receipt processing
- **MCP Skill Hub** (`mcp.insightpulseai.net`) - OCR skill endpoint
- **Supabase** - Logging and result storage

### Environment Variables

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
OCR_ENGINE=paddleocr
LOG_LEVEL=info
MAX_FILE_SIZE_MB=10
```

## Cost Optimization

Current droplet: **$24/month** (4 GB / 2 vCPUs)

Consider:
- Add Redis cache to reduce repeated OCR processing
- Implement result caching in Supabase
- Use App Platform with autoscaling if traffic is variable

## Next Steps

1. ✅ DNS configured (ocr.insightpulseai.net → 188.166.237.231)
2. ☐ SSH into droplet and verify Docker installation
3. ☐ Deploy OCR service (choose Option 1, 2, or 3)
4. ☐ Configure Cloudflare SSL (Full/Strict mode)
5. ☐ Test health endpoint
6. ☐ Integrate with Odoo and MCP Skill Hub
7. ☐ Set up monitoring and alerting
