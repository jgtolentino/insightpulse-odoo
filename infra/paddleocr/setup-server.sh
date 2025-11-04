#!/bin/bash

# PaddleOCR Server Setup Script
# Runs on Ubuntu 22.04 droplet
# Installs Docker, Docker Compose, and configures the server

set -euo pipefail

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_info "Starting server setup..."

# Update system
log_info "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
log_info "Installing dependencies..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    git \
    htop \
    ufw \
    fail2ban \
    jq

# Install Docker
log_info "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker root
    systemctl enable docker
    systemctl start docker
    log_info "Docker installed"
else
    log_info "Docker already installed"
fi

# Install Docker Compose
log_info "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_VERSION="2.23.0"
    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    log_info "Docker Compose installed"
else
    log_info "Docker Compose already installed"
fi

# Configure firewall
log_info "Configuring UFW firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # PaddleOCR API
ufw allow 11434/tcp # Ollama API
echo "y" | ufw enable

# Configure fail2ban
log_info "Configuring fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Create application directory
log_info "Creating application directory..."
mkdir -p /opt/paddleocr
chown -R root:root /opt/paddleocr

# Configure swap (helps with Ollama model loading)
log_info "Configuring swap..."
if [ ! -f /swapfile ]; then
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    log_info "Swap configured (4GB)"
else
    log_info "Swap already configured"
fi

# Set timezone
log_info "Setting timezone to UTC..."
timedatectl set-timezone UTC

# Configure system limits
log_info "Configuring system limits..."
cat >> /etc/security/limits.conf <<EOF
* soft nofile 65536
* hard nofile 65536
* soft nproc 65536
* hard nproc 65536
EOF

# Configure sysctl
log_info "Configuring sysctl..."
cat >> /etc/sysctl.conf <<EOF
# Network performance tuning
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq
vm.swappiness = 10
vm.vfs_cache_pressure = 50
EOF
sysctl -p

# Install monitoring tools
log_info "Installing monitoring tools..."
apt-get install -y \
    netdata \
    prometheus-node-exporter

systemctl enable netdata
systemctl start netdata

# Create log directory
log_info "Creating log directory..."
mkdir -p /var/log/paddleocr
chmod 755 /var/log/paddleocr

# Configure log rotation
log_info "Configuring log rotation..."
cat > /etc/logrotate.d/paddleocr <<EOF
/var/log/paddleocr/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 root root
    sharedscripts
    postrotate
        docker-compose -f /opt/paddleocr/docker-compose.yml restart web
    endscript
}
EOF

# Install Nginx (for reverse proxy and SSL termination)
log_info "Installing Nginx..."
apt-get install -y nginx
systemctl enable nginx
systemctl start nginx

# Configure Nginx
log_info "Configuring Nginx..."
cat > /etc/nginx/sites-available/paddleocr <<'EOF'
server {
    listen 80;
    server_name ocr.insightpulseai.net;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=ocr_limit:10m rate=10r/s;
    limit_req zone=ocr_limit burst=20 nodelay;

    # Client body size limit (for image uploads)
    client_max_body_size 10M;

    # Proxy to PaddleOCR service
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts (OCR can take time)
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }

    # Metrics endpoint (protected)
    location /metrics {
        proxy_pass http://localhost:8000/metrics;
        allow 10.0.0.0/8;  # Allow internal IPs only
        deny all;
    }
}
EOF

ln -sf /etc/nginx/sites-available/paddleocr /etc/nginx/sites-enabled/

# Configure Nginx for Ollama
log_info "Configuring Nginx for Ollama..."
cat > /etc/nginx/sites-available/ollama <<'EOF'
server {
    listen 80;
    server_name llm.insightpulseai.net;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=ollama_limit:10m rate=5r/s;
    limit_req zone=ollama_limit burst=10 nodelay;

    # Client body size limit
    client_max_body_size 10M;

    # Proxy to Ollama service
    location / {
        proxy_pass http://localhost:11434;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts (LLM inference can take time)
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;

        # Streaming support
        proxy_buffering off;
        proxy_http_version 1.1;
        chunked_transfer_encoding on;
    }

    # Health check endpoint
    location /api/tags {
        proxy_pass http://localhost:11434/api/tags;
        access_log off;
    }
}
EOF

ln -sf /etc/nginx/sites-available/ollama /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# Install Certbot for SSL
log_info "Installing Certbot..."
apt-get install -y certbot python3-certbot-nginx

log_info "Server setup completed successfully!"
log_info ""
log_info "Next steps:"
log_info "1. Deploy application files to /opt/paddleocr/"
log_info "2. Run: cd /opt/paddleocr && docker-compose up -d"
log_info "3. Pull Ollama model: docker exec ollama-service ollama pull llama3.2:3b"
log_info "4. Configure SSL: certbot --nginx -d ocr.insightpulseai.net -d llm.insightpulseai.net"
log_info ""
