#!/bin/bash
# Cloud-init script for PaddleOCR + Ollama LLM Droplet
# InsightPulse AI Infrastructure

set -euo pipefail

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create directories
mkdir -p /opt/paddleocr
mkdir -p /opt/ollama

# Setup PaddleOCR
cat > /opt/paddleocr/docker-compose.yml <<'EOF'
version: '3.8'

services:
  paddleocr:
    image: paddlepaddle/paddleocr:latest
    container_name: paddleocr
    ports:
      - "8000:8000"
    environment:
      - USE_GPU=false
    restart: unless-stopped
    command: python3 /app/ocr_api.py
EOF

# Setup Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3.2 3B model
ollama pull llama3.2:3b

# Create systemd service for Ollama
cat > /etc/systemd/system/ollama.service <<'EOF'
[Unit]
Description=Ollama LLM Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/ollama serve
Restart=always
Environment="OLLAMA_HOST=0.0.0.0:11434"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ollama
systemctl start ollama

# Setup Caddy reverse proxy
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update
apt-get install -y caddy

# Configure Caddy
cat > /etc/caddy/Caddyfile <<'EOF'
ocr.insightpulseai.net {
    reverse_proxy localhost:8000
}

llm.insightpulseai.net {
    reverse_proxy localhost:11434
}
EOF

systemctl restart caddy

# Start PaddleOCR
cd /opt/paddleocr
docker-compose up -d

# Setup monitoring agent (node_exporter for Prometheus)
docker run -d \
  --name=node_exporter \
  --restart=unless-stopped \
  --net="host" \
  --pid="host" \
  -v "/:/host:ro,rslave" \
  quay.io/prometheus/node-exporter:latest \
  --path.rootfs=/host

echo "OCR + LLM Droplet setup complete!"
