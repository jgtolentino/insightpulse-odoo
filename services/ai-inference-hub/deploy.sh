#!/bin/bash
set -euo pipefail

echo "🚀 AI Inference Hub Deployment Script"
echo "======================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root"
  exit 1
fi

# 1) Install prerequisites
echo "📦 Installing prerequisites..."
apt-get update
apt-get install -y \
  python3-pip \
  python3-venv \
  ffmpeg \
  libsndfile1 \
  espeak-ng \
  nginx \
  git \
  curl \
  jq

# 2) Create service user
echo "👤 Creating service user..."
id -u aihub &>/dev/null || useradd -m -s /bin/bash aihub

# 3) Setup application directory
echo "📁 Setting up application..."
mkdir -p /opt/ai-inference-hub
rsync -a --delete /root/ai-inference-hub/ /opt/ai-inference-hub/ 2>/dev/null || \
  rsync -a --delete $(dirname "$0")/ /opt/ai-inference-hub/
chown -R aihub:aihub /opt/ai-inference-hub

# 4) Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv /opt/ai-inference-hub/.venv
source /opt/ai-inference-hub/.venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r /opt/ai-inference-hub/requirements.txt

# 5) Create environment configuration
echo "⚙️  Creating environment configuration..."
cat >/etc/ai-inference-hub.env <<'EOV'
# Deployment Mode
MODE=dev
PROVIDER=anthropic
PROVIDER_ORDER=anthropic,ollama

# Server Configuration
BIND=127.0.0.1
PORT=8100

# API Keys (EDIT THESE!)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Model Configuration
MODEL_NAME=deepseek-ai/DeepSeek-OCR
WHISPER_MODEL=base
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
TORCH_DEVICE=cpu
IMAGE_SIZE=base

# Supabase (optional)
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=

# Ollama (for hybrid/self-hosted mode)
OLLAMA_BASE_URL=http://localhost:11434

# Budget & Limits
LLM_BUDGET_USD=200
MAX_REQUEST_SIZE_MB=25
RATE_LIMIT_PER_MINUTE=60

# Logging
LOG_LEVEL=INFO
EOV

chmod 600 /etc/ai-inference-hub.env
chown root:root /etc/ai-inference-hub.env

echo "⚠️  IMPORTANT: Edit /etc/ai-inference-hub.env and add your API keys!"
echo "   nano /etc/ai-inference-hub.env"

# 6) Create systemd service
echo "🔧 Creating systemd service..."
cat >/etc/systemd/system/ai-inference-hub.service <<'EOUNIT'
[Unit]
Description=AI Inference Hub (Multi-Modal AI Service)
Documentation=https://github.com/insightpulseai/ai-inference-hub
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=aihub
Group=aihub
WorkingDirectory=/opt/ai-inference-hub
EnvironmentFile=/etc/ai-inference-hub.env

# Activate venv and run uvicorn
ExecStart=/opt/ai-inference-hub/.venv/bin/uvicorn main:app \
  --host ${BIND:-127.0.0.1} \
  --port ${PORT:-8100} \
  --workers 2 \
  --log-level ${LOG_LEVEL:-info}

# Restart policy
Restart=always
RestartSec=3
RuntimeMaxSec=3d

# Resource limits
LimitNOFILE=65535
MemoryMax=4G
CPUQuota=200%

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/ai-inference-hub
ReadWritePaths=/tmp

[Install]
WantedBy=multi-user.target
EOUNIT

systemctl daemon-reload
systemctl enable ai-inference-hub

# 7) Setup Nginx reverse proxy
echo "🌐 Configuring Nginx reverse proxy..."
DOMAIN="${1:-ai.insightpulseai.net}"
cat >/etc/nginx/sites-available/ai-hub.conf <<NGINX
# AI Inference Hub Reverse Proxy
# Upstream
upstream ai_backend {
    server 127.0.0.1:8100 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# HTTP → HTTPS redirect (will be added by certbot)
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};

    # Let's Encrypt validation
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Proxy to backend
    location / {
        proxy_pass http://ai_backend;
        proxy_http_version 1.1;

        # Headers
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Connection "";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # Buffering
        proxy_buffering off;
        proxy_request_buffering off;

        # File upload size
        client_max_body_size 25m;
    }

    # Health check endpoint (bypass auth)
    location /health {
        proxy_pass http://ai_backend/health;
        access_log off;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/ai-hub.conf /etc/nginx/sites-enabled/ai-hub.conf
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl reload nginx

# 8) Setup UFW firewall
echo "🔒 Configuring firewall..."
ufw --force enable || true
ufw default deny incoming || true
ufw default allow outgoing || true
ufw allow 22/tcp comment 'SSH' || true
ufw allow 80/tcp comment 'HTTP' || true
ufw allow 443/tcp comment 'HTTPS' || true
ufw deny 8100/tcp comment 'Block direct AI Hub access' || true
ufw status

# 9) Start service
echo "▶️  Starting AI Inference Hub..."
systemctl start ai-inference-hub

# Wait for service to be ready
echo "⏳ Waiting for service to start..."
sleep 5

# 10) Health check
echo "🏥 Running health check..."
if curl -sf http://127.0.0.1:8100/health >/dev/null; then
  echo "✅ AI Inference Hub is running!"
  curl -s http://127.0.0.1:8100/health | jq .
else
  echo "❌ Health check failed. Check logs with: journalctl -u ai-inference-hub -f"
  exit 1
fi

# 11) Setup TLS (optional but recommended)
echo ""
read -p "Setup TLS with Let's Encrypt? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  apt-get install -y certbot python3-certbot-nginx
  read -p "Enter email for Let's Encrypt notifications: " EMAIL
  certbot --nginx -d ${DOMAIN} \
    --non-interactive \
    --agree-tos \
    -m "${EMAIL}" \
    --redirect
  echo "✅ TLS configured!"
fi

# 12) Show status
echo ""
echo "======================================"
echo "✅ Deployment Complete!"
echo "======================================"
echo ""
echo "Service Status:"
systemctl status ai-inference-hub --no-pager -l
echo ""
echo "Access URLs:"
echo "  - Internal: http://127.0.0.1:8100"
echo "  - External: http://${DOMAIN}"
if [[ -f /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ]]; then
  echo "  - HTTPS: https://${DOMAIN}"
fi
echo ""
echo "Next Steps:"
echo "  1. Edit API keys: nano /etc/ai-inference-hub.env"
echo "  2. Restart service: systemctl restart ai-inference-hub"
echo "  3. View logs: journalctl -u ai-inference-hub -f"
echo "  4. Test endpoints: curl https://${DOMAIN}/health"
echo ""
echo "Documentation:"
echo "  - Architecture: /opt/ai-inference-hub/ARCHITECTURE.md"
echo "  - Configuration: /opt/ai-inference-hub/CONFIG.md"
echo ""
