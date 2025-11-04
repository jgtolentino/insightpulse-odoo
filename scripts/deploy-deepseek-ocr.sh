#!/bin/bash
# Deploy DeepSeek-OCR Service to Existing OCR Droplet
# Adds experimental DeepSeek-OCR endpoint at ocr.insightpulseai.net/dsocr/

set -euo pipefail

# Configuration
OCR_DROPLET_IP="188.166.237.231"
OCR_DROPLET_USER="root"
OCR_DOMAIN="ocr.insightpulseai.net"
DSOCR_PORT="7010"  # Local port for DeepSeek-OCR service

echo "🚀 Deploying DeepSeek-OCR Service"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   Target: $OCR_DROPLET_IP"
echo "   Domain: https://${OCR_DOMAIN}/dsocr/"
echo "   Port: $DSOCR_PORT (localhost)"
echo ""

# Step 1: Create Python venv and install dependencies
echo "📦 Setting up Python environment..."

ssh ${OCR_DROPLET_USER}@${OCR_DROPLET_IP} <<'REMOTE_SCRIPT'
# Create directory for DeepSeek-OCR
mkdir -p ~/dsocr
cd ~/dsocr

# Create Python virtual environment
python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn python-multipart pillow pydantic

echo "✅ Python environment ready"
REMOTE_SCRIPT

# Step 2: Create FastAPI placeholder service
echo ""
echo "🔧 Creating DeepSeek-OCR service..."

ssh ${OCR_DROPLET_USER}@${OCR_DROPLET_IP} <<'REMOTE_SCRIPT'
cat > ~/dsocr/main.py <<'PYTHON_CODE'
#!/usr/bin/env python3
"""
DeepSeek-OCR Service (Placeholder Implementation)
Endpoint: POST /ocr
Future: Integrate actual DeepSeek-OCR-7B model
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DeepSeek-OCR Service",
    description="Document OCR using DeepSeek-OCR-7B (Placeholder)",
    version="0.1.0-placeholder"
)

class OCRResult(BaseModel):
    text: str
    confidence: float
    fields: Dict[str, str]
    metadata: Dict[str, any]

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "deepseek-ocr",
        "version": "0.1.0-placeholder",
        "model": "pending-integration",
        "implementation": "placeholder"
    }

@app.post("/ocr", response_model=OCRResult)
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text from uploaded image using DeepSeek-OCR

    Future: Replace with actual DeepSeek-OCR-7B model inference
    """

    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read file
        contents = await file.read()
        logger.info(f"Received image: {file.filename}, size: {len(contents)} bytes")

        # PLACEHOLDER: Return mock OCR result
        # TODO: Integrate actual DeepSeek-OCR-7B model
        result = OCRResult(
            text="[PLACEHOLDER] This is a mock OCR result. Actual DeepSeek-OCR-7B integration pending.",
            confidence=0.99,
            fields={
                "vendor": "[PLACEHOLDER]",
                "date": "[PLACEHOLDER]",
                "total": "[PLACEHOLDER]",
                "status": "mock-extraction"
            },
            metadata={
                "filename": file.filename,
                "content_type": file.content_type,
                "size_bytes": len(contents),
                "implementation": "placeholder",
                "note": "Replace with actual DeepSeek-OCR-7B inference"
            }
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@app.get("/models")
async def list_models():
    """List available OCR models"""
    return {
        "models": [
            {
                "id": "deepseek-ocr-7b",
                "name": "DeepSeek-OCR-7B",
                "status": "pending-integration",
                "capabilities": ["document-understanding", "structured-output"],
                "languages": ["en", "zh", "multilingual"]
            }
        ],
        "default": "deepseek-ocr-7b"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7010, log_level="info")
PYTHON_CODE

chmod +x ~/dsocr/main.py

echo "✅ DeepSeek-OCR service created"
REMOTE_SCRIPT

# Step 3: Create systemd service for auto-start
echo ""
echo "⚙️ Creating systemd service..."

ssh ${OCR_DROPLET_USER}@${OCR_DROPLET_IP} <<'REMOTE_SCRIPT'
cat > /etc/systemd/system/deepseek-ocr.service <<'SYSTEMD_UNIT'
[Unit]
Description=DeepSeek-OCR Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/dsocr
Environment="PATH=/root/dsocr/venv/bin"
ExecStart=/root/dsocr/venv/bin/uvicorn main:app --host 0.0.0.0 --port 7010 --log-level info
Restart=on-failure
RestartSec=10s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SYSTEMD_UNIT

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable deepseek-ocr.service
systemctl start deepseek-ocr.service

# Check status
systemctl status deepseek-ocr.service --no-pager

echo "✅ Systemd service created and started"
REMOTE_SCRIPT

# Step 4: Update Nginx configuration
echo ""
echo "🌐 Updating Nginx configuration..."

ssh ${OCR_DROPLET_USER}@${OCR_DROPLET_IP} <<'REMOTE_SCRIPT'
# Backup existing Nginx config
cp /etc/nginx/sites-available/ocr.insightpulseai.net.conf /etc/nginx/sites-available/ocr.insightpulseai.net.conf.backup

# Update Nginx config to add /dsocr/ route
cat > /etc/nginx/sites-available/ocr.insightpulseai.net.conf <<'NGINX_CONF'
server {
    listen 80;
    server_name ocr.insightpulseai.net;

    # PaddleOCR endpoint (existing)
    location /paddle/ {
        rewrite ^/paddle/(.*) /$1 break;
        proxy_pass http://172.22.0.2:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 10M;
    }

    # DeepSeek-OCR endpoint (new)
    location /dsocr/ {
        rewrite ^/dsocr/(.*) /$1 break;
        proxy_pass http://localhost:7010;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 10M;
    }

    # Health check endpoint
    location /health {
        return 200 '{"status":"ok","services":["paddle","dsocr"]}';
        add_header Content-Type application/json;
    }

    # Root redirect to health
    location = / {
        return 301 /health;
    }
}
NGINX_CONF

# Test and reload Nginx
nginx -t
systemctl reload nginx

echo "✅ Nginx configuration updated"
REMOTE_SCRIPT

# Step 5: Verify deployment
echo ""
echo "🔍 Verifying DeepSeek-OCR deployment..."

ssh ${OCR_DROPLET_USER}@${OCR_DROPLET_IP} <<'REMOTE_SCRIPT'
# Check service status
echo "Service status:"
systemctl is-active deepseek-ocr.service && echo "✅ DeepSeek-OCR service is running" || echo "❌ Service not running"

# Check port listening
echo ""
echo "Port listening:"
netstat -tuln | grep 7010 && echo "✅ Port 7010 is listening" || echo "❌ Port 7010 not listening"

# Test health endpoint
echo ""
echo "Health check:"
curl -s http://localhost:7010/health | jq || echo "❌ Health check failed"

echo ""
echo "✅ Verification complete"
REMOTE_SCRIPT

# Final validation
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DeepSeek-OCR Service Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Deployment Summary:"
echo "   Domain: https://${OCR_DOMAIN}/dsocr/"
echo "   Local Port: $DSOCR_PORT"
echo "   Service: deepseek-ocr.service"
echo "   Status: Placeholder implementation (ready for model integration)"
echo ""
echo "🔍 Validation Commands:"
echo ""
echo "# Health check"
echo "curl -s http://${OCR_DOMAIN}/dsocr/health | jq"
echo ""
echo "# List models"
echo "curl -s http://${OCR_DOMAIN}/dsocr/models | jq"
echo ""
echo "# Test OCR (placeholder)"
echo "curl -s -F file=@sample.jpg http://${OCR_DOMAIN}/dsocr/ocr | jq"
echo ""
echo "# Service status"
echo "ssh ${OCR_DROPLET_USER}@${OCR_DROPLET_IP} 'systemctl status deepseek-ocr.service'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo "1. Integrate actual DeepSeek-OCR-7B model in ~/dsocr/main.py"
echo "2. Test with real receipt images"
echo "3. Compare accuracy with PaddleOCR-VL"
echo "4. Update Pulse Hub to include /dsocr/ endpoint"
echo ""
