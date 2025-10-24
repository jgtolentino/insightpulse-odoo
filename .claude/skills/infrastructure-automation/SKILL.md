---
name: infrastructure-automation
description: Complete infrastructure automation for Docker, Digital Ocean, and cloud deployment with monitoring and scaling
version: 1.0.0
tags: [infrastructure, docker, digital-ocean, terraform, monitoring, scaling, automation]
requires:
  files:
    - superclaude/knowledge/DOCKER_DIGITALOCEAN_GUIDE.md
    - superclaude/knowledge/ODOO_19_REFERENCE.md
uses:
  skills:
    - cicd-pipeline-manager
    - odoo-sh-devops
---

# Infrastructure Automation Skill

## Purpose

Automate complete infrastructure lifecycle including Docker container orchestration, Digital Ocean provisioning, monitoring setup, and auto-scaling for Odoo deployments.

## When to use

- Provisioning and managing Digital Ocean infrastructure
- Setting up Docker container orchestration
- Implementing monitoring and alerting systems
- Configuring auto-scaling and load balancing
- Managing infrastructure as code with Terraform
- Implementing backup and disaster recovery

## Actions

1. **Infrastructure Provisioning**: Automate Digital Ocean droplet and resource creation
2. **Container Orchestration**: Set up Docker Swarm or Kubernetes for Odoo
3. **Monitoring Setup**: Implement comprehensive monitoring and alerting
4. **Auto-scaling Configuration**: Configure automatic scaling based on load
5. **Backup Management**: Implement automated backup and recovery procedures
6. **Security Hardening**: Apply security best practices to infrastructure

## Inputs

- `infrastructure_type`: Type of infrastructure (single-node, cluster, high-availability)
- `scaling_requirements`: Auto-scaling configuration and thresholds
- `monitoring_level`: Monitoring and alerting requirements
- `backup_strategy`: Backup frequency and retention policies
- `security_requirements`: Security and compliance requirements

## Outputs

- Terraform infrastructure configurations
- Docker orchestration setup
- Monitoring and alerting configurations
- Auto-scaling rules and policies
- Backup and recovery procedures
- Security hardening scripts

## Examples

### Example 1: High-Availability Cluster Setup
```
User: "Set up high-availability Odoo cluster on Digital Ocean with auto-scaling"

Agent:
1. Creates Terraform configuration for multi-node cluster
2. Sets up Docker Swarm with manager and worker nodes
3. Configures load balancer and auto-scaling rules
4. Implements monitoring with Prometheus and Grafana
5. Sets up automated backups and disaster recovery
6. Applies security hardening to all nodes
```

### Example 2: Production Monitoring Setup
```
User: "Implement comprehensive monitoring for Odoo production environment"

Agent:
1. Deploys Prometheus for metrics collection
2. Sets up Grafana dashboards for Odoo performance
3. Configures alerting for critical metrics
4. Implements log aggregation with ELK stack
5. Sets up application performance monitoring
6. Creates monitoring documentation and runbooks
```

### Example 3: Auto-scaling Configuration
```
User: "Configure auto-scaling for Odoo based on CPU and memory usage"

Agent:
1. Sets up horizontal pod auto-scaling for Odoo containers
2. Configures vertical scaling for database resources
3. Implements load-based scaling rules
4. Sets up cost optimization for scaling
5. Creates scaling policies and documentation
6. Tests scaling behavior under load
```

## Infrastructure as Code

### Complete Terraform Configuration
```hcl
# terraform/variables.tf
variable "do_token" {
  description = "Digital Ocean API token"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "Digital Ocean region"
  type        = string
  default     = "nyc3"
}

variable "cluster_size" {
  description = "Number of nodes in the cluster"
  type        = number
  default     = 3
}

# terraform/main.tf
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    # Configure remote state storage
  }
}

provider "digitalocean" {
  token = var.do_token
}

# SSH Key
resource "digitalocean_ssh_key" "odoo" {
  name       = "odoo-cluster"
  public_key = file("~/.ssh/odoo_production.pub")
}

# Odoo Cluster Nodes
resource "digitalocean_droplet" "odoo_nodes" {
  count  = var.cluster_size
  image  = "ubuntu-22-04-x64"
  name   = "odoo-node-${count.index + 1}"
  region = var.region
  size   = "s-2vcpu-4gb"
  ssh_keys = [digitalocean_ssh_key.odoo.fingerprint]
  tags   = ["odoo", "cluster"]

  connection {
    type        = "ssh"
    user        = "root"
    private_key = file("~/.ssh/odoo_production")
    host        = self.ipv4_address
  }

  provisioner "remote-exec" {
    inline = [
      "curl -fsSL https://get.docker.com -o get-docker.sh",
      "sh get-docker.sh",
      "systemctl enable docker",
      "systemctl start docker",
      "docker swarm init --advertise-addr ${self.ipv4_address_private}"
    ]
  }
}

# Load Balancer
resource "digitalocean_loadbalancer" "odoo" {
  name   = "odoo-cluster-lb"
  region = var.region

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

  droplet_ids = digitalocean_droplet.odoo_nodes[*].id
}

# Database Cluster
resource "digitalocean_database_cluster" "postgresql" {
  name       = "odoo-postgresql-cluster"
  engine     = "pg"
  version    = "14"
  size       = "db-s-2vcpu-4gb"
  region     = var.region
  node_count = 2
  tags       = ["odoo", "production"]

  connection_pool {
    name = "odoo-pool"
    mode = "transaction"
    size = 25
  }
}

# Redis Cluster
resource "digitalocean_database_cluster" "redis" {
  name       = "odoo-redis-cluster"
  engine     = "redis"
  version    = "6"
  size       = "db-s-1vcpu-1gb"
  region     = var.region
  node_count = 1
  tags       = ["odoo", "production"]
}

# Firewall
resource "digitalocean_firewall" "odoo_cluster" {
  name = "odoo-cluster-firewall"

  droplet_ids = digitalocean_droplet.odoo_nodes[*].id

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "2377"
    source_addresses = [digitalocean_droplet.odoo_nodes[0].ipv4_address_private]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "7946"
    source_addresses = digitalocean_droplet.odoo_nodes[*].ipv4_address_private
  }

  inbound_rule {
    protocol         = "udp"
    port_range       = "7946"
    source_addresses = digitalocean_droplet.odoo_nodes[*].ipv4_address_private
  }

  inbound_rule {
    protocol         = "udp"
    port_range       = "4789"
    source_addresses = digitalocean_droplet.odoo_nodes[*].ipv4_address_private
  }
}
```

## Docker Swarm Orchestration

### Docker Stack Configuration
```yaml
# docker-stack.yml
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
      placement:
        constraints:
          - node.role == manager
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
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      rollback_config:
        parallelism: 1
        delay: 5s
        order: stop-first
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
    networks:
      - odoo_network
    deploy:
      mode: global
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
    driver: overlay
    attachable: true
```

### Swarm Management Scripts
```bash
#!/bin/bash
# swarm-setup.sh

set -e

echo "Setting up Docker Swarm cluster..."

# Initialize swarm on first node
MANAGER_IP=$(doctl compute droplet list --tag-name odoo --format PublicIPv4 --no-header | head -1)

if [ -z "$MANAGER_IP" ]; then
  echo "No manager node found"
  exit 1
fi

# Get swarm join token
JOIN_TOKEN=$(ssh -o StrictHostKeyChecking=no root@$MANAGER_IP "docker swarm join-token -q worker")

# Join worker nodes
WORKER_IPS=$(doctl compute droplet list --tag-name odoo --format PublicIPv4 --no-header | tail -n +2)

for WORKER_IP in $WORKER_IPS; do
  echo "Joining worker node: $WORKER_IP"
  ssh -o StrictHostKeyChecking=no root@$WORKER_IP "docker swarm join --token $JOIN_TOKEN $MANAGER_IP:2377"
done

echo "Docker Swarm cluster setup complete!"
```

## Monitoring and Alerting

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'odoo'
    static_configs:
      - targets: ['odoo:8069']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 30s

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboards
```json
{
  "dashboard": {
    "title": "Odoo Production Dashboard",
    "panels": [
      {
        "title": "Odoo Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(odoo_request_duration_seconds_sum[5m]) / rate(odoo_request_duration_seconds_count[5m])",
            "legendFormat": "Average Response Time"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_activity_count{datname=\"odoo_prod\"}",
            "legendFormat": "Active Connections"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes{container_label_com_docker_swarm_service_name=\"odoo\"}",
            "legendFormat": "Odoo Memory"
          }
        ]
      }
    ]
  }
}
```

## Auto-scaling Configuration

### Horizontal Auto-scaling
```bash
#!/bin/bash
# setup-auto-scaling.sh

# Create auto-scaling rules for Odoo service
docker service update odoo \
  --replicas-max 10 \
  --replicas-min 2 \
  --update-parallelism 2 \
  --update-delay 10s

# Setup auto-scaling based on CPU
cat > /opt/odoo19/auto-scaling-rules.yml << EOF
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: odoo-autoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: odoo
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
EOF
```

### Load-based Scaling Script
```bash
#!/bin/bash
# auto-scale-odoo.sh

set -e

# Get current CPU usage
CPU_USAGE=$(docker stats odoo --no-stream --format "{{.CPUPerc}}" | sed 's/%//')

# Get current memory usage
MEMORY_USAGE=$(docker stats odoo --no-stream --format "{{.MemPerc}}" | sed 's/%//')

# Get current replica count
CURRENT_REPLICAS=$(docker service ls --filter name=odoo --format "{{.Replicas}}" | cut -d'/' -f2)

# Auto-scaling logic
if [ $(echo "$CPU_USAGE > 80" | bc) -eq 1 ] || [ $(echo "$MEMORY_USAGE > 80" | bc) -eq 1 ]; then
  if [ $CURRENT_REPLICAS -lt 10 ]; then
    NEW_REPLICAS=$((CURRENT_REPLICAS + 1))
    echo "Scaling up to $NEW_REPLICAS replicas"
    docker service scale odoo=$NEW_REPLICAS
  fi
elif [ $(echo "$CPU_USAGE < 30" | bc) -eq 1 ] && [ $(echo "$MEMORY_USAGE < 30" | bc) -eq 1 ]; then
  if [ $CURRENT_REPLICAS -gt 2 ]; then
    NEW_REPLICAS=$((CURRENT_REPLICAS - 1))
    echo "Scaling down to $NEW_REPLICAS replicas"
    docker service scale odoo=$NEW_REPLICAS
  fi
fi
```

## Backup and Disaster Recovery

### Automated Backup System
```bash
#!/bin/bash
# automated-backup.sh

set -e

BACKUP_DIR="/opt/odoo19/backups"
DATE=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="odoo-backups"

echo "Starting automated backup..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
echo "Backing up
