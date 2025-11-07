# SystemD Auto-Healing Services

This directory contains systemd service and timer units for auto-healing InsightPulse infrastructure.

## Services

### 1. DB Connection Healer (`ip-db-healer`)
- **What:** Monitors PostgreSQL connections and auto-remediates when threshold exceeded
- **Runs:** Every 5 minutes
- **Script:** `auto-healing/remediation/fix_db_connections.py`

### 2. Superset Health Check (`ip-superset-healer`)
- **What:** Monitors Superset health and auto-restarts if unresponsive
- **Runs:** Every 2 minutes
- **Script:** `auto-healing/remediation/superset_health_check.sh`

## Installation

### For System-Wide Services (requires root)

```bash
# Copy units to systemd
sudo cp auto-healing/systemd/ip-*.service /etc/systemd/system/
sudo cp auto-healing/systemd/ip-*.timer /etc/systemd/system/

# Replace %i with your username
sudo sed -i "s/%i/$USER/g" /etc/systemd/system/ip-*.service

# Start services
make healing:start
```

### For User Services (no root required)

```bash
# Copy units to user systemd
mkdir -p ~/.config/systemd/user/
cp auto-healing/systemd/ip-*.service ~/.config/systemd/user/
cp auto-healing/systemd/ip-*.timer ~/.config/systemd/user/

# Replace %i with your username
sed -i "s/%i/$USER/g" ~/.config/systemd/user/ip-*.service

# Enable user services
systemctl --user daemon-reload
systemctl --user enable --now ip-db-healer.service ip-db-healer.timer
systemctl --user enable --now ip-superset-healer.service ip-superset-healer.timer

# Check status
systemctl --user list-timers | grep ip-
```

## Usage

```bash
# Start healers
make healing:start

# Check status
make healing:status

# Stop healers
make healing:stop

# View logs
journalctl -u ip-db-healer.service -f
journalctl -u ip-superset-healer.service -f

# Manual trigger
sudo systemctl start ip-db-healer.service
sudo systemctl start ip-superset-healer.service
```

## Configuration

### Override Environment Variables

```bash
# Edit service environment
sudo systemctl edit ip-superset-healer.service

# Add:
[Service]
Environment="SUPERSET_URL=https://your-custom-url.com"
Environment="SUPERSET_APP_ID=your-app-id"
```

### Adjust Timer Intervals

```bash
# Edit timer
sudo systemctl edit ip-db-healer.timer

# Add:
[Timer]
OnUnitActiveSec=10min  # Change from 5min to 10min
```

## Monitoring

### View Timer Schedule
```bash
systemctl list-timers | grep ip-
```

### View Service Status
```bash
systemctl status ip-db-healer.service
systemctl status ip-superset-healer.service
```

### View Logs
```bash
# Last 50 lines
journalctl -u ip-db-healer.service -n 50

# Follow logs
journalctl -u ip-db-healer.service -f

# Filter by priority
journalctl -u ip-db-healer.service -p err
```

## Troubleshooting

### Service Fails to Start

```bash
# Check logs
journalctl -u ip-db-healer.service -xe

# Verify script permissions
ls -la auto-healing/remediation/fix_db_connections.py
chmod +x auto-healing/remediation/fix_db_connections.py

# Test manually
python3 auto-healing/remediation/fix_db_connections.py
```

### Timer Not Triggering

```bash
# Check timer status
systemctl status ip-db-healer.timer

# Verify timer is enabled
systemctl is-enabled ip-db-healer.timer

# Manually trigger
systemctl start ip-db-healer.service
```

### Permission Issues

```bash
# Ensure user has access
sudo usermod -aG docker $USER

# Create logs directory
mkdir -p auto-healing/logs
chmod 755 auto-healing/logs
```

## Uninstall

```bash
# Stop and disable
make healing:stop

# Remove units
sudo rm /etc/systemd/system/ip-*
sudo systemctl daemon-reload
```

## Production Recommendations

1. **Monitor logs regularly**: Set up log rotation and alerting
2. **Test in staging first**: Verify healers work correctly before production
3. **Adjust intervals**: Based on your infrastructure needs
4. **Set up alerting**: Notify ops team when healers trigger
5. **Review healing actions**: Audit what healers are fixing

## Security

- Services run with `NoNewPrivileges=true`
- Read-only home directory (except logs)
- Private `/tmp` directory
- Protected system paths

---

For more information, see:
- [Auto-Healing README](../README.md)
- [Comprehensive Troubleshooting Guide](../../docs/COMPREHENSIVE_ERROR_TROUBLESHOOTING_GUIDE_ODOO19.md)
