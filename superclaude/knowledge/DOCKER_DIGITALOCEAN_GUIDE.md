# Docker & Digital Ocean Infrastructure Guide

## Docker Infrastructure for Odoo

### Docker Architecture Patterns

#### Multi-container Odoo Stack
```yaml
# docker-compose.yml - Complete Odoo Stack
version: '3.8'
services:
  # Database Layer
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - odoo_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Cache Layer
  redis:
    image: redis:6-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - odoo_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Application Layer
  odoo:
    image: odoo:19.0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      HOST: postgres
      USER: ${POSTGRES_USER}
      PASSWORD: ${POSTGRES_PASSWORD}
      REDIS_HOST: redis
      ADDONS_PATH: /mnt/extra-addons
    volumes:
      - odoo_data:/var/lib/odoo
      - ./addons:/mnt/extra-addons
      - ./odoo/odoo.conf:/etc/odoo/odoo.conf
    networks:
      - odoo_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - odoo
    networks:
      - odoo_network

volumes:
  postgres_data:
  redis_data:
  odoo_data:

networks:
  odoo_network:
    driver: bridge
```

### Production Docker Configuration

#### Multi-stage Docker Build
```dockerfile
# Dockerfile for Production Odoo
FROM odoo:19.0 as builder

# Install build dependencies
USER root
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Clone OCA modules
RUN git clone --depth 1 --branch 19.0 https://github.com/OCA/web.git /mnt/oca-web
RUN git clone --depth 1 --branch 19.0 https://github.com/OCA/server-tools.git /mnt/oca-server-tools

FROM odoo:19.0

# Copy OCA modules
COPY --from=builder /mnt/oca-web /mnt/extra-addons/oca-web
COPY --from=builder /mnt/oca-server-tools /mnt/extra-addons/oca-server-tools

# Copy custom addons
COPY ./addons /mnt/extra-addons/custom

# Copy Python dependencies
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Set proper permissions
USER root
RUN chown -R odoo:odoo /mnt/extra-addons
USER odoo

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=300s \
  CMD curl -f http://localhost:8069/web/health || exit 1

# Default command
CMD ["odoo", "-c", "/etc/odoo/odoo.conf"]
```

#### Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - odoo_network
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  redis:
    image: redis:6-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - odoo_network
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  odoo:
    image: ${DOCKER_REGISTRY}/odoo:${ODOO_VERSION}
    depends_on:
      - postgres
      - redis
    environment:
      HOST: postgres
      USER: ${POSTGRES_USER}
      PASSWORD: ${POSTGRES_PASSWORD}
      REDIS_HOST: redis
      ADDONS_PATH: /mnt/extra-addons
      WORKERS: 4
      MAX_CRON_THREADS: 2
    volumes:
      - odoo_data:/var/lib/odoo
      - ./addons:/mnt/extra-addons
    networks:
      - odoo_network
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - odoo
    networks:
      - odoo_network
    deploy:
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  odoo_data:
    driver: local

networks:
  odoo_network:
    driver: bridge
```

## Digital Ocean Infrastructure

### Digital Ocean CLI Setup

#### Installation and Configuration
```bash
#!/bin/bash
# setup-digitalocean-cli.sh

# Install Digital Ocean CLI
curl -sL https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz | tar -xzv
sudo mv doctl /usr/local/bin/

# Authenticate with Digital Ocean
doctl auth init --context production

# Create SSH key for droplets
ssh-keygen -t rsa -b 4096 -C "odoo@insightpulseai.net" -f ~/.ssh/odoo_production -N ""
doctl compute ssh-key import odoo-production --public-key-file ~/.ssh/odoo_production.pub

# List available regions and sizes
doctl compute region list
doctl compute size list
```

### Infrastructure as Code with Terraform

#### Terraform Configuration
```hcl
# terraform/main.tf
terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

# Odoo Droplet
resource "digitalocean_droplet" "odoo" {
  image    = "ubuntu-22-04-x64"
  name     = "odoo-production"
  region   = var.region
  size     = "s-2vcpu-4gb"
  ssh_keys = [digitalocean_ssh_key.odoo.fingerprint]
  tags     = ["odoo", "production"]

  connection {
    type        = "ssh"
    user        = "root"
    private_key = file(var.pvt_key)
    host        = self.ipv4_address
  }

  provisioner "remote-exec" {
    inline = [
      "curl -fsSL https://get.docker.com -o get-docker.sh",
      "sh get-docker.sh",
      "systemctl enable docker",
      "systemctl start docker",
      "docker plugin install --grant-all-permissions vieux/sshfs"
    ]
  }
}

# Load Balancer
resource "digitalocean_loadbalancer" "odoo" {
  name   = "odoo-lb"
  region = var.region
  tags   = ["odoo", "production"]

  forwarding_rule {
    entry_port     = 80
    entry_protocol = "http"

    target_port     = 8069
    target_protocol = "http"
  }

  forwarding_rule {
    entry_port     = 443
    entry_protocol = "https"

    target_port     = 8069
    target_protocol = "http"

    certificate_name = digitalocean_certificate.odoo.name
  }

  healthcheck {
    port     = 8069
    protocol = "http"
    path     = "/web/health"
  }

  droplet_ids = [digitalocean_droplet.odoo.id]
}

# Database Cluster
resource "digitalocean_database_cluster" "postgresql" {
  name       = "odoo-postgresql"
  engine     = "pg"
  version    = "14"
  size       = "db-s-1vcpu-1gb"
  region     = var.region
  node_count = 1
  tags       = ["odoo", "production"]

  connection_pool {
    name = "odoo-pool"
    mode = "transaction"
    size = 20
  }
}

# Firewall
resource "digitalocean_firewall" "odoo" {
  name = "odoo-firewall"

  droplet_ids = [digitalocean_droplet.odoo.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# SSL Certificate
resource "digitalocean_certificate" "odoo" {
  name    = "odoo-certificate"
  type    = "lets_encrypt"
  domains = ["insightpulseai.net"]
}
```

### Automated Deployment Scripts

#### Complete Deployment Pipeline
```bash
#!/bin/bash
# digitalocean-deploy.sh

set -e

# Configuration
DROPLET_NAME="odoo-production"
REGION="nyc3"
SIZE="s-2vcpu-4gb"
IMAGE="ubuntu-22-04-x64"

echo "Starting Digital Ocean deployment..."

# Get SSH key fingerprint
SSH_KEY_FINGERPRINT=$(doctl compute ssh-key list --format FingerPrint --no-header | head -1)

if [ -z "$SSH_KEY_FINGERPRINT" ]; then
  echo "No SSH keys found. Please add an SSH key to Digital Ocean."
  exit 1
fi

# Create droplet
echo "Creating droplet..."
DROPLET_ID=$(doctl compute droplet create $DROPLET_NAME \
  --image $IMAGE \
  --size $SIZE \
  --region $REGION \
  --ssh-keys $SSH_KEY_FINGERPRINT \
  --tag-name odoo \
  --format ID \
  --no-header \
  --wait)

if [ -z "$DROPLET_ID" ]; then
  echo "Failed to create droplet"
  exit 1
fi

# Get droplet IP
DROPLET_IP=$(doctl compute droplet get $DROPLET_ID --format PublicIPv4 --no-header)

echo "Droplet created with IP: $DROPLET_IP"

# Wait for droplet to be ready
echo "Waiting for droplet to be ready..."
sleep 30

# Deploy application
echo "Deploying Odoo application..."
scp -o StrictHostKeyChecking=no \
  docker-compose.prod.yml \
  .env.production \
  scripts/droplet-setup.sh \
  root@$DROPLET_IP:/tmp/

ssh -o StrictHostKeyChecking=no root@$DROPLET_IP << 'EOF'
  # Run setup script
  chmod +x /tmp/droplet-setup.sh
  /tmp/droplet-setup.sh

  # Create application directory
  mkdir -p /opt/odoo19
  mv /tmp/docker-compose.prod.yml /opt/odoo19/
  mv /tmp/.env.production /opt/odoo19/.env

  # Start application
  cd /opt/odoo19
  docker-compose -f docker-compose.prod.yml up -d

  # Setup monitoring
  docker run -d \
    --name=cadvisor \
    --volume=/:/rootfs:ro \
    --volume=/var/run:/var/run:ro \
    --volume=/sys:/sys:ro \
    --volume=/var/lib/docker/:/var/lib/docker:ro \
    --volume=/dev/disk/:/dev/disk:ro \
    --publish=8080:8080 \
    --detach=true \
    gcr.io/cadvisor/cadvisor:v0.47.0
EOF

echo "Deployment completed successfully!"
echo "Odoo is available at: http://$DROPLET_IP"
echo "cAdvisor monitoring at: http://$DROPLET_IP:8080"
```

## Monitoring and Logging

### Docker Monitoring Setup
```bash
#!/bin/bash
# setup-monitoring.sh

# Install Prometheus
docker run -d \
  --name=prometheus \
  --net=host \
  -v /opt/odoo19/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Install Grafana
docker run -d \
  --name=grafana \
  --net=host \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana

# Install cAdvisor for container metrics
docker run -d \
  --name=cadvisor \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --volume=/dev/disk/:/dev/disk:ro \
  --publish=8080:8080 \
  gcr.io/cadvisor/cadvisor:v0.47.0
```

### Log Management
```bash
#!/bin/bash
# setup-logging.sh

# Install ELK stack for log management
docker run -d \
  --name=elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  docker.elastic.co/elasticsearch/elasticsearch:7.17.0

docker run -d \
  --name=logstash \
  --link elasticsearch:elasticsearch \
  -v /opt/odoo19/logstash.conf:/usr/share/logstash/pipeline/logstash.conf \
  docker.elastic.co/logstash/logstash:7.17.0

docker run -d \
  --name=kibana \
  --link elasticsearch:elasticsearch \
  -p 5601:5601 \
  docker.elastic.co/kibana/kibana:7.17.0
```

## Backup and Recovery

### Automated Backup Script
```bash
#!/bin/bash
# backup-odoo.sh

set -e

BACKUP_DIR="/opt/odoo19/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="odoo_backup_${DATE}.tar.gz"

echo "Starting Odoo backup..."

# Stop Odoo containers
docker-compose -f /opt/odoo19/docker-compose.prod.yml stop odoo

# Backup database
docker exec postgres pg_dump -U odoo -d odoo_prod > ${BACKUP_DIR}/database_${DATE}.sql

# Backup filestore
tar -czf ${BACKUP_DIR}/filestore_${DATE}.tar.gz /opt/odoo19/odoo_data/filestore

# Create complete backup
tar -czf ${BACKUP_DIR}/${BACKUP_FILE} \
  ${BACKUP_DIR
