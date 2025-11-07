# InsightPulse AI - Monitoring & Observability Stack

Complete monitoring solution using Prometheus, Grafana, and Alertmanager for InsightPulse AI platform.

## 🎯 Overview

This monitoring stack provides:
- **Prometheus**: Metrics collection and time-series database
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notification management
- **Node Exporter**: System-level metrics
- **cAdvisor**: Container metrics
- **Blackbox Exporter**: Endpoint health checks
- **Postgres Exporter**: Database metrics

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Access to your infrastructure endpoints
- SMTP credentials for email alerts (optional)

### Installation

1. **Clone and navigate to monitoring directory**
   ```bash
   cd /path/to/insightpulse-odoo/monitoring
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   vim .env  # Edit with your credentials
   ```

3. **Start the monitoring stack**
   ```bash
   docker-compose up -d
   ```

4. **Verify services are running**
   ```bash
   docker-compose ps
   ```

5. **Access dashboards**
   - Grafana: http://localhost:3000 (admin / insightpulse2025)
   - Prometheus: http://localhost:9090
   - Alertmanager: http://localhost:9093

## 📊 Services & Ports

| Service | Port | Purpose |
|---------|------|---------|
| Grafana | 3000 | Visualization dashboards |
| Prometheus | 9090 | Metrics database & queries |
| Alertmanager | 9093 | Alert management |
| Node Exporter | 9100 | System metrics |
| cAdvisor | 8080 | Container metrics |
| Blackbox Exporter | 9115 | HTTP/SSL probes |
| Postgres Exporter | 9187 | Database metrics |

## 🎨 Grafana Dashboards

### Pre-configured Dashboards

Access Grafana at http://localhost:3000 with default credentials:
- **Username**: `admin`
- **Password**: `insightpulse2025`

**Change the password immediately after first login!**

### Available Dashboards

1. **System Overview**
   - CPU, Memory, Disk, Network metrics
   - System load and uptime
   - Resource utilization trends

2. **Application Performance**
   - HTTP request rates
   - Response time percentiles
   - Error rates by service
   - Throughput metrics

3. **Database Monitoring**
   - Connection pool status
   - Query performance
   - Transaction rates
   - Slow query detection

4. **Container Health**
   - Container CPU/memory usage
   - Container restart counts
   - Network I/O per container
   - Storage usage

5. **Endpoint Monitoring**
   - HTTP health check status
   - SSL certificate expiry
   - DNS resolution times
   - Uptime percentage

6. **Business Metrics** (Odoo-specific)
   - Active user sessions
   - Sales orders per hour
   - Invoice generation rate
   - Module usage statistics

## 🔔 Alert Configuration

### Alert Severity Levels

**Critical** (Immediate action required):
- Service down (>2 minutes)
- HTTP endpoint unreachable
- Critical CPU usage (>95%)
- Critical memory usage (>95%)
- Disk space critical (<5%)
- Database connection failure

**Warning** (Investigation needed):
- High CPU usage (>80% for 5 min)
- High memory usage (>85% for 5 min)
- Low disk space (<15%)
- SSL certificate expires in <30 days
- High response times (>2s)
- High error rate (>5%)

### Notification Channels

Edit `alertmanager/alertmanager.yml` to configure:

**Email Notifications**:
```yaml
email_configs:
  - to: 'admin@insightpulseai.net'
    from: 'alerts@insightpulseai.net'
    smarthost: 'smtp.gmail.com:587'
    auth_username: 'alerts@insightpulseai.net'
    auth_password: '${SMTP_PASSWORD}'
```

**Slack Notifications** (optional):
```yaml
webhook_configs:
  - url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    send_resolved: true
```

**PagerDuty** (optional):
```yaml
pagerduty_configs:
  - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
```

## 📈 Metrics Collection

### System Metrics (Node Exporter)

Collected every 15 seconds:
- CPU usage per core
- Memory (total, available, cached, buffered)
- Disk I/O (read/write ops, bytes)
- Network I/O (bytes in/out, packets)
- Filesystem usage per mount point
- System load (1m, 5m, 15m)

### Application Metrics

**Odoo ERP**:
- HTTP request count and duration
- Active sessions
- Database query counts
- Cron job execution times
- Module load times

**Superset**:
- Dashboard load times
- Query execution duration
- Cache hit rates
- Active users

**MCP Server**:
- API request rates
- GitHub webhook processing time
- Queue depth

### Database Metrics (Postgres Exporter)

- Active connections
- Connection pool utilization
- Transaction rate (commits, rollbacks)
- Query duration percentiles
- Table/index sizes
- Cache hit ratios
- Replication lag (if applicable)

### Container Metrics (cAdvisor)

- Per-container CPU usage
- Per-container memory usage
- Network I/O per container
- Filesystem I/O per container
- Container restart counts

### Endpoint Health (Blackbox Exporter)

- HTTP status codes
- Response times
- SSL certificate validity
- Certificate expiry dates
- DNS resolution times
- TCP connection times

## 🔧 Configuration

### Adding New Scrape Targets

Edit `prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'new_service'
    static_configs:
      - targets: ['new-service.example.com:9090']
        labels:
          service: 'new_service'
          environment: 'production'
```

Reload Prometheus configuration:
```bash
curl -X POST http://localhost:9090/-/reload
```

### Adding New Alerts

Edit `prometheus/alerts.yml`:

```yaml
- alert: NewAlertName
  expr: metric_expression > threshold
  for: 5m
  labels:
    severity: warning
    category: performance
  annotations:
    summary: "Alert summary"
    description: "Detailed description"
    runbook: "https://docs.insightpulseai.net/runbooks/alert-name"
```

### Creating Custom Dashboards

1. Create dashboard in Grafana UI
2. Export JSON via Dashboard Settings → JSON Model
3. Save to `grafana/dashboards/custom-dashboard.json`
4. Restart Grafana or wait for auto-reload

## 🔍 Querying Metrics

### Prometheus Query Examples

**CPU Usage**:
```promql
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Memory Usage**:
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

**HTTP Request Rate**:
```promql
rate(http_requests_total[5m])
```

**95th Percentile Response Time**:
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Database Connections**:
```promql
pg_stat_activity_count
```

**Container Memory Usage**:
```promql
container_memory_usage_bytes{name!=""}
```

## 🛠️ Operations

### Starting the Stack

```bash
docker-compose up -d
```

### Stopping the Stack

```bash
docker-compose down
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f alertmanager
```

### Restarting Services

```bash
docker-compose restart prometheus
docker-compose restart grafana
```

### Updating Images

```bash
docker-compose pull
docker-compose up -d
```

### Backup & Restore

**Backup Prometheus data**:
```bash
docker run --rm -v monitoring_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup-$(date +%Y%m%d).tar.gz -C /data .
```

**Backup Grafana data**:
```bash
docker run --rm -v monitoring_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup-$(date +%Y%m%d).tar.gz -C /data .
```

**Restore Prometheus data**:
```bash
docker-compose down
docker run --rm -v monitoring_prometheus_data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/prometheus-backup-YYYYMMDD.tar.gz"
docker-compose up -d
```

## 📊 Performance Tuning

### Prometheus Retention

Default retention: 30 days

To change retention in `docker-compose.yml`:
```yaml
command:
  - '--storage.tsdb.retention.time=90d'
  - '--storage.tsdb.retention.size=50GB'
```

### Scrape Interval

Default: 15 seconds

To change globally in `prometheus/prometheus.yml`:
```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 30s
```

### Grafana Performance

For large dashboards:
- Increase query timeout: `GF_DATAPROXY_TIMEOUT=120`
- Increase dashboard refresh interval
- Use recording rules for complex queries

## 🔐 Security

### Change Default Passwords

**Grafana**:
```bash
docker exec -it grafana grafana-cli admin reset-admin-password NEW_PASSWORD
```

**Prometheus Basic Auth** (via reverse proxy):
Use Caddy, Nginx, or Traefik with basic authentication

### Restrict Access

Use firewall rules or reverse proxy to restrict access:
```bash
# Allow only specific IPs
iptables -A INPUT -p tcp --dport 9090 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 9090 -j DROP
```

### Enable HTTPS

Use Caddy as reverse proxy (automatic SSL):
```
monitoring.insightpulseai.net {
    reverse_proxy localhost:3000
}

prometheus.insightpulseai.net {
    reverse_proxy localhost:9090
    basicauth {
        admin JDJhJDE0JFhrPUVYeEpQNUs4WTlLM1lRWDNhT20=
    }
}
```

## 🐛 Troubleshooting

### Prometheus Not Scraping Targets

**Check target status**:
- Go to http://localhost:9090/targets
- Look for errors in target status

**Common issues**:
- Firewall blocking connections
- Incorrect target address
- Service not exposing metrics endpoint

**Solution**:
```bash
# Test connectivity
curl http://target-host:9100/metrics

# Check Prometheus logs
docker-compose logs prometheus
```

### Grafana Dashboards Not Loading

**Check Prometheus datasource**:
- Go to Configuration → Data Sources
- Test Prometheus connection
- Verify URL: `http://prometheus:9090`

**Check logs**:
```bash
docker-compose logs grafana
```

### Alerts Not Firing

**Check alert status**:
- Go to http://localhost:9090/alerts
- Verify alert expressions

**Check Alertmanager**:
- Go to http://localhost:9093
- Check alert routing configuration
- Verify SMTP credentials in `.env`

### High Memory Usage

**Prometheus memory**:
```bash
# Reduce retention period
--storage.tsdb.retention.time=15d

# Limit memory usage
--storage.tsdb.max-block-duration=2h
```

**Grafana memory**:
```yaml
environment:
  - GF_DATABASE_WAL=false
```

## 📚 Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [PromQL Query Examples](https://prometheus.io/docs/prometheus/latest/querying/examples/)
- [Grafana Dashboard Gallery](https://grafana.com/grafana/dashboards/)

## 📄 License

Part of InsightPulse AI platform. See main repository LICENSE.
