#!/usr/bin/env bash
set -euo pipefail

# Monitoring Setup for Odoo SaaS Platform
# Creates Prometheus + Grafana monitoring stack

APP_ID="${1:-}"

if [ -z "$APP_ID" ]; then
  echo "Usage: $0 <app-id>"
  echo "Get app ID with: doctl apps list"
  exit 1
fi

echo "📊 Setting up monitoring for app: $APP_ID"
echo "=========================================="
echo ""

# Get app details
APP_NAME=$(doctl apps get "$APP_ID" --format Spec.Name --no-header)
APP_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)

echo "App Name: $APP_NAME"
echo "App URL: https://$APP_URL"
echo ""

# Create monitoring directory
MONITORING_DIR="infra/monitoring"
mkdir -p "$MONITORING_DIR"

echo "📝 Creating Prometheus configuration..."

cat > "$MONITORING_DIR/prometheus.yml" <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'digitalocean'
    app: '$APP_NAME'

scrape_configs:
  - job_name: 'odoo-saas-platform'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['$APP_URL:8069']
    scheme: https

  - job_name: 'digitalocean-app-platform'
    metrics_path: '/v2/monitoring/metrics/droplet/cpu'
    static_configs:
      - targets: ['api.digitalocean.com']
    scheme: https
    bearer_token: '${DO_ACCESS_TOKEN}'
EOF

echo "✅ Prometheus config created: $MONITORING_DIR/prometheus.yml"

echo ""
echo "📈 Creating Grafana dashboard..."

cat > "$MONITORING_DIR/grafana-dashboard.json" <<'EOF'
{
  "dashboard": {
    "title": "Odoo SaaS Platform",
    "tags": ["odoo", "saas", "digitalocean"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Latency P95",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95 Latency"
          }
        ],
        "alert": {
          "name": "High Latency Alert",
          "conditions": [
            {
              "evaluator": {
                "params": [0.5],
                "type": "gt"
              }
            }
          ],
          "notifications": []
        }
      },
      {
        "id": 2,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx Errors"
          }
        ],
        "alert": {
          "name": "High Error Rate Alert",
          "conditions": [
            {
              "evaluator": {
                "params": [0.001],
                "type": "gt"
              }
            }
          ]
        }
      },
      {
        "id": 3,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "id": 4,
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "odoo_active_users",
            "legendFormat": "Active Users"
          }
        ]
      },
      {
        "id": 5,
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_activity_count",
            "legendFormat": "DB Connections"
          }
        ]
      },
      {
        "id": 6,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes / 1024 / 1024",
            "legendFormat": "Memory (MB)"
          }
        ],
        "alert": {
          "name": "High Memory Usage Alert",
          "conditions": [
            {
              "evaluator": {
                "params": [400],
                "type": "gt"
              }
            }
          ]
        }
      }
    ]
  }
}
EOF

echo "✅ Grafana dashboard created: $MONITORING_DIR/grafana-dashboard.json"

echo ""
echo "🐳 Creating Docker Compose for monitoring stack..."

cat > "$MONITORING_DIR/docker-compose.yml" <<EOF
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana-dashboard.json:/etc/grafana/provisioning/dashboards/odoo.json
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=\${GRAFANA_ADMIN_PASSWORD:-admin}
      - GF_INSTALL_PLUGINS=
    restart: unless-stopped

volumes:
  prometheus-data:
  grafana-data:
EOF

echo "✅ Docker Compose created: $MONITORING_DIR/docker-compose.yml"

echo ""
echo "📧 Creating alert configuration..."

cat > "$MONITORING_DIR/alerts.yml" <<EOF
groups:
  - name: odoo_saas_platform
    interval: 30s
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High request latency detected"
          description: "P95 latency is {{ \$value }}s (threshold: 0.5s)"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.001
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ \$value }} (threshold: 0.1%)"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 > 400
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is {{ \$value }}MB (threshold: 400MB)"

      - alert: HealthCheckFailed
        expr: up{job="odoo-saas-platform"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Health check failing"
          description: "Odoo SaaS Platform health check has been failing for 2 minutes"
EOF

echo "✅ Alert config created: $MONITORING_DIR/alerts.yml"

echo ""
echo "✅ Monitoring setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start monitoring stack:"
echo "   cd $MONITORING_DIR"
echo "   docker-compose up -d"
echo ""
echo "2. Access dashboards:"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3000"
echo ""
echo "3. Configure Grafana:"
echo "   - Login with admin/admin"
echo "   - Add Prometheus data source: http://prometheus:9090"
echo "   - Import dashboard from grafana-dashboard.json"
echo ""
echo "4. Set up alerting:"
echo "   - Configure notification channels in Grafana"
echo "   - Add alert rules from alerts.yml to Prometheus"
