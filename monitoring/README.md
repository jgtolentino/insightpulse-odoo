# 📊 Monitoring - Observability & Metrics

This directory contains monitoring, metrics, and observability configurations for InsightPulse Odoo infrastructure.

## 📁 Directory Structure

```
monitoring/
├── prometheus/              # Prometheus configuration
│   ├── prometheus.yml       # Main Prometheus config
│   ├── alerts.yml           # Alert rules
│   └── rules/               # Recording rules
├── grafana/                 # Grafana dashboards
│   └── dashboards/          # Dashboard JSON definitions
├── alertmanager/            # Alert routing config
├── exporters/               # Custom metric exporters
└── logs/                    # Log aggregation config
```

## 🎯 Purpose

The monitoring stack provides:
- **Metrics Collection**: Time-series data from all services
- **Dashboards**: Visual insights into system health
- **Alerting**: Proactive notification of issues
- **Log Aggregation**: Centralized logging
- **Performance Tracking**: Resource usage and bottlenecks

## 🚀 Quick Start

### Start Monitoring Stack
```bash
# Start all monitoring services
docker-compose -f infrastructure/docker/docker-compose.yml up -d prometheus grafana

# Access dashboards
open http://localhost:9090  # Prometheus
open http://localhost:3000  # Grafana
```

### View Metrics
```bash
# Query Prometheus
curl 'http://localhost:9090/api/v1/query?query=up'

# View service health
make health
```

## 📊 Key Metrics

### System Metrics
- **CPU Usage**: `node_cpu_seconds_total`
- **Memory Usage**: `node_memory_MemAvailable_bytes`
- **Disk I/O**: `node_disk_io_time_seconds_total`
- **Network**: `node_network_receive_bytes_total`

### Application Metrics
- **Request Rate**: `http_requests_total`
- **Response Time**: `http_request_duration_seconds`
- **Error Rate**: `http_requests_total{status=~"5.."}`
- **Database Queries**: `postgres_queries_total`

### Business Metrics
- **Active Users**: `odoo_active_users`
- **Transactions**: `odoo_transactions_total`
- **Revenue**: `odoo_revenue_total`
- **API Calls**: `api_calls_total`

## 🚨 Alerting

### Alert Severity Levels
- **Critical**: Immediate action required (PagerDuty)
- **Warning**: Action needed soon (Email)
- **Info**: Informational (Dashboard only)

### Key Alerts
```yaml
# High CPU Usage
- alert: HighCPUUsage
  expr: node_cpu_usage > 80
  for: 5m
  severity: warning

# Service Down
- alert: ServiceDown
  expr: up{job="odoo"} == 0
  for: 1m
  severity: critical

# High Error Rate
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  severity: warning
```

## 📈 Grafana Dashboards

### Pre-built Dashboards
1. **System Overview** - Overall health and resource usage
2. **Odoo Performance** - Application-specific metrics
3. **Database Stats** - PostgreSQL performance
4. **Network Traffic** - Bandwidth and latency
5. **Business KPIs** - Revenue and user metrics

### Access Grafana
```bash
# Default credentials
URL: http://localhost:3000
User: admin
Password: admin
```

### Import Dashboard
```bash
# Import from JSON
cp monitoring/grafana/dashboards/system.json /var/lib/grafana/dashboards/
```

## 🔍 Log Aggregation

### Log Sources
- **Application Logs**: Odoo, Superset, n8n
- **System Logs**: Docker, OS events
- **Access Logs**: Nginx, Apache
- **Error Logs**: Application errors, stack traces

### Query Logs
```bash
# View Odoo logs
docker-compose logs odoo -f

# Search logs
docker-compose logs | grep ERROR

# Export logs
docker-compose logs > logs/export-$(date +%Y%m%d).log
```

## 📊 Performance Baselines

### Target SLAs
- **Uptime**: 99.9%
- **Response Time**: < 200ms (p95)
- **Error Rate**: < 0.1%
- **CPU Usage**: < 70% average
- **Memory Usage**: < 80% average

### Current Performance
- **Uptime**: 99.95%
- **Response Time**: 150ms (p95)
- **Error Rate**: 0.05%
- **CPU Usage**: 45% average
- **Memory Usage**: 60% average

## 🛠️ Maintenance

### Retention Policies
- **Metrics**: 30 days
- **Logs**: 7 days
- **Dashboards**: Versioned in Git

### Backup
```bash
# Backup Prometheus data
tar -czf prometheus-backup.tar.gz /var/lib/prometheus

# Backup Grafana dashboards
cp -r /var/lib/grafana/dashboards/ backups/grafana-$(date +%Y%m%d)/
```

## 🔗 Integration

### Slack Notifications
Configure Alertmanager to send alerts to Slack

### PagerDuty
Critical alerts trigger PagerDuty incidents

### Email
Warnings sent via SMTP

## 📝 Custom Metrics

### Export Custom Metrics
```python
from prometheus_client import Counter, Histogram

# Counter
requests_total = Counter('http_requests_total', 'Total HTTP requests')
requests_total.inc()

# Histogram
request_duration = Histogram('http_request_duration_seconds', 'HTTP request latency')
request_duration.observe(0.150)
```

### Scrape Custom Endpoint
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'custom-app'
    static_configs:
      - targets: ['localhost:8000']
```

## 🔗 Related Documentation

- [Infrastructure](../infrastructure/README.md)
- [Auto-Healing](../auto-healing/README.md)
- [Health Checks](../scripts/validate-repo-structure.py)

---

**For more information, see the main [README](../README.md)**
