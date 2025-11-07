#!/bin/bash
# Cloud-init script for Prometheus + Grafana Monitoring Droplet
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

# Mount volumes
mkdir -p /mnt/prometheus_data
mkdir -p /mnt/grafana_data

# Format and mount volumes if not already mounted
if ! grep -q "/mnt/prometheus_data" /etc/fstab; then
    echo "UUID=$(blkid -s UUID -o value /dev/disk/by-id/scsi-0DO_Volume_prometheus-data) /mnt/prometheus_data ext4 defaults,nofail,discard 0 2" >> /etc/fstab
fi

if ! grep -q "/mnt/grafana_data" /etc/fstab; then
    echo "UUID=$(blkid -s UUID -o value /dev/disk/by-id/scsi-0DO_Volume_grafana-data) /mnt/grafana_data ext4 defaults,nofail,discard 0 2" >> /etc/fstab
fi

mount -a

# Create monitoring directory
mkdir -p /opt/monitoring
cd /opt/monitoring

# Create Prometheus configuration
cat > /opt/monitoring/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'insightpulse-ai'
    environment: 'production'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - 'localhost:9093'

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter (this droplet)
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']

  # OCR/LLM Droplet
  - job_name: 'ocr_llm_droplet'
    static_configs:
      - targets: ['ocr.insightpulseai.net:9100']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'ocr-llm-droplet'

  # DigitalOcean App Platform Apps
  - job_name: 'odoo'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['erp.insightpulseai.net:8069']

  - job_name: 'superset'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['superset.insightpulseai.net:8088']

  - job_name: 'mcp_server'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['mcp.insightpulseai.net:8000']

  # Blackbox exporter for uptime monitoring
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://erp.insightpulseai.net/web/health
        - https://superset.insightpulseai.net/health
        - https://mcp.insightpulseai.net/health
        - https://ocr.insightpulseai.net/health
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115
EOF

# Create Alertmanager configuration
cat > /opt/monitoring/alertmanager.yml <<'EOF'
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'email'

receivers:
  - name: 'email'
    email_configs:
      - to: 'admin@insightpulseai.net'
        from: 'alerts@insightpulseai.net'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@insightpulseai.net'
        auth_identity: 'alerts@insightpulseai.net'
        auth_password: '${SMTP_PASSWORD}'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster', 'service']
EOF

# Create Prometheus alerts
cat > /opt/monitoring/alerts.yml <<'EOF'
groups:
  - name: insightpulse_alerts
    interval: 30s
    rules:
      # Service Down Alerts
      - alert: ServiceDown
        expr: up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 2 minutes."

      # High CPU Usage
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for more than 5 minutes. Current value: {{ $value }}%"

      # High Memory Usage
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85%. Current value: {{ $value }}%"

      # Disk Space Low
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 15
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk space is below 15%. Current value: {{ $value }}%"

      # HTTP Endpoint Down
      - alert: HTTPEndpointDown
        expr: probe_success == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "HTTP endpoint {{ $labels.instance }} is down"
          description: "The endpoint has been unreachable for more than 2 minutes."

      # Database Connection Issues
      - alert: DatabaseConnectionFailure
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL database connection failed"
          description: "Cannot connect to PostgreSQL database {{ $labels.instance }}"
EOF

# Create Docker Compose for monitoring stack
cat > /opt/monitoring/docker-compose.yml <<'EOF'
version: '3.8'

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/prometheus_data
  grafana_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/grafana_data

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alerts.yml:/etc/prometheus/alerts.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - monitoring

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    restart: unless-stopped
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=insightpulse2025
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
      - GF_SERVER_ROOT_URL=https://monitoring.insightpulseai.net
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana-datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
    ports:
      - "3000:3000"
    networks:
      - monitoring
    depends_on:
      - prometheus

  node_exporter:
    image: quay.io/prometheus/node-exporter:latest
    container_name: node_exporter
    restart: unless-stopped
    command:
      - '--path.rootfs=/host'
    pid: host
    volumes:
      - '/:/host:ro,rslave'
    ports:
      - "9100:9100"
    networks:
      - monitoring

  blackbox_exporter:
    image: prom/blackbox-exporter:latest
    container_name: blackbox_exporter
    restart: unless-stopped
    ports:
      - "9115:9115"
    volumes:
      - ./blackbox.yml:/etc/blackbox_exporter/config.yml
    command:
      - '--config.file=/etc/blackbox_exporter/config.yml'
    networks:
      - monitoring
EOF

# Create Grafana datasource configuration
mkdir -p /opt/monitoring/grafana-dashboards
cat > /opt/monitoring/grafana-datasources.yml <<'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

# Create blackbox exporter configuration
cat > /opt/monitoring/blackbox.yml <<'EOF'
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: [200, 302]
      method: GET
      follow_redirects: true
      preferred_ip_protocol: "ip4"
EOF

# Setup Caddy reverse proxy for Grafana
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update
apt-get install -y caddy

# Configure Caddy
cat > /etc/caddy/Caddyfile <<'EOF'
monitoring.insightpulseai.net {
    reverse_proxy localhost:3000
}

prometheus.insightpulseai.net {
    reverse_proxy localhost:9090
    basicauth {
        admin $2a$14$Xkz3EXxJP5K8Y9K3YQX3aOm5Z5X3YQX3aOm5Z5X3YQX3aOm5Z5X3a
    }
}
EOF

systemctl restart caddy

# Start monitoring stack
cd /opt/monitoring
docker-compose up -d

# Wait for services to start
sleep 30

echo "Monitoring stack setup complete!"
echo "Grafana: https://monitoring.insightpulseai.net (admin / insightpulse2025)"
echo "Prometheus: https://prometheus.insightpulseai.net"
