# Odoo Knowledge Base Scraper - Automation Setup

This directory contains everything needed to run the Odoo forum scraper as an automated background job.

## 🎯 Quick Start

### Option 1: Cron Job (Simplest)

**1. Install the cron job:**
```bash
# Edit crontab
crontab -e

# Add this line (runs every Sunday at 2 AM):
0 2 * * 0 cd /home/user/insightpulse-odoo/agents/odoo-knowledge/crawler && ./run_scraper_cron.sh
```

**2. Verify it's installed:**
```bash
crontab -l
```

**3. Test manually:**
```bash
cd /home/user/insightpulse-odoo/agents/odoo-knowledge/crawler
./run_scraper_cron.sh
```

**4. Monitor logs:**
```bash
tail -f /home/user/insightpulse-odoo/logs/scraper/cron.log
```

---

### Option 2: Systemd Timer (Recommended for Servers)

**1. Copy service files:**
```bash
sudo cp odoo-scraper.service /etc/systemd/system/
sudo cp odoo-scraper.timer /etc/systemd/system/
```

**2. Enable and start timer:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable odoo-scraper.timer
sudo systemctl start odoo-scraper.timer
```

**3. Check status:**
```bash
# Check timer status
sudo systemctl status odoo-scraper.timer

# Check when it will run next
sudo systemctl list-timers odoo-scraper.timer

# View logs
sudo journalctl -u odoo-scraper.service -f
```

**4. Run manually (test):**
```bash
sudo systemctl start odoo-scraper.service
```

---

### Option 3: GitHub Actions (Zero Infrastructure)

**Already set up!** The workflow file is at:
`.github/workflows/odoo-knowledge-scraper.yml`

**Features:**
- ✅ Runs weekly (Sunday 2 AM UTC)
- ✅ Can trigger manually from GitHub UI
- ✅ Auto-commits results
- ✅ Email notifications on failure

**To trigger manually:**
1. Go to: https://github.com/jgtolentino/insightpulse-odoo/actions
2. Select "Weekly Odoo Knowledge Base Update"
3. Click "Run workflow"

---

## 📋 Files Overview

| File | Purpose |
|------|---------|
| `run_scraper_cron.sh` | Main automation script (handles everything) |
| `crontab.example` | Cron schedule examples |
| `odoo-scraper.service` | Systemd service definition |
| `odoo-scraper.timer` | Systemd timer schedule |
| `AUTOMATION_SETUP.md` | This file |

---

## 🔧 Configuration

### Change Schedule

**Cron:**
```bash
# Daily at 3 AM
0 3 * * * cd /path/to/crawler && ./run_scraper_cron.sh

# Twice weekly (Sun & Wed at 2 AM)
0 2 * * 0,3 cd /path/to/crawler && ./run_scraper_cron.sh

# Every 6 hours
0 */6 * * * cd /path/to/crawler && ./run_scraper_cron.sh
```

**Systemd Timer:**
Edit `odoo-scraper.timer`:
```ini
# Daily at 3 AM
OnCalendar=*-*-* 03:00:00

# Every 6 hours
OnCalendar=*-*-* 00,06,12,18:00:00
```

**GitHub Actions:**
Edit `.github/workflows/odoo-knowledge-scraper.yml`:
```yaml
on:
  schedule:
    # Daily at 3 AM UTC
    - cron: '0 3 * * *'
```

---

## 📊 Monitoring

### Check Logs

**Cron:**
```bash
# Latest log
tail -f /home/user/insightpulse-odoo/logs/scraper/cron.log

# All scraper logs
ls -lh /home/user/insightpulse-odoo/logs/scraper/
```

**Systemd:**
```bash
# Live logs
sudo journalctl -u odoo-scraper.service -f

# Last 100 lines
sudo journalctl -u odoo-scraper.service -n 100

# Logs since yesterday
sudo journalctl -u odoo-scraper.service --since yesterday
```

**GitHub Actions:**
- Go to: https://github.com/jgtolentino/insightpulse-odoo/actions
- View workflow runs and logs

### Verify It's Running

**Cron:**
```bash
# Check cron is running
ps aux | grep cron

# Check if scraper ran today
ls -lh /home/user/insightpulse-odoo/logs/scraper/ | grep $(date +%Y%m%d)

# Check last commit
git log -1 --grep="update Odoo knowledge"
```

**Systemd:**
```bash
# Timer status (shows next run time)
systemctl list-timers odoo-scraper.timer

# Service status
systemctl status odoo-scraper.service
```

---

## 🔔 Notifications (Optional)

### Slack Notifications

Add to `run_scraper_cron.sh` in `error_exit()` function:

```bash
error_exit() {
    log "ERROR: $1"

    # Slack webhook notification
    curl -X POST "$SLACK_WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d "{\"text\":\"❌ Odoo scraper failed: $1\nLog: $LOG_FILE\"}"

    exit 1
}
```

### Email Notifications

Add to crontab:
```bash
MAILTO=your-email@example.com
0 2 * * 0 cd /path/to/crawler && ./run_scraper_cron.sh
```

### Discord Webhook

```bash
curl -X POST "$DISCORD_WEBHOOK_URL" \
    -H 'Content-Type: application/json' \
    -d "{\"content\":\"❌ Odoo scraper failed: $1\"}"
```

---

## 🐛 Troubleshooting

### Cron Not Running

**1. Check cron service:**
```bash
sudo systemctl status cron
sudo systemctl start cron  # If stopped
```

**2. Check cron logs:**
```bash
grep CRON /var/log/syslog
```

**3. Check script permissions:**
```bash
ls -l /home/user/insightpulse-odoo/agents/odoo-knowledge/crawler/run_scraper_cron.sh
# Should show: -rwxr-xr-x (executable)

# Fix if needed:
chmod +x run_scraper_cron.sh
```

### Scraper Fails

**1. Test manually:**
```bash
cd /home/user/insightpulse-odoo/agents/odoo-knowledge/crawler
./run_scraper_cron.sh
```

**2. Check dependencies:**
```bash
pip3 install -r ../requirements.txt
playwright install chromium
```

**3. Check git permissions:**
```bash
cd /home/user/insightpulse-odoo
git status
git pull  # Should work without password
```

**4. Check network:**
```bash
curl -I https://www.odoo.com/forum/help-1
# Should return 200 OK
```

### Systemd Issues

**1. Check service logs:**
```bash
sudo journalctl -u odoo-scraper.service --no-pager
```

**2. Reload after changes:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart odoo-scraper.timer
```

**3. Check permissions:**
```bash
sudo systemctl cat odoo-scraper.service
# Verify User= and WorkingDirectory= are correct
```

---

## 📈 Performance

### Expected Runtime

- **100 pages**: ~30-60 minutes
- **With rate limiting**: ~45-90 minutes
- **Processing**: +5-10 minutes

### Resource Usage

- **CPU**: Low (mostly I/O bound)
- **Memory**: ~200-500 MB
- **Network**: ~50-100 MB download
- **Disk**: ~5-10 MB per run

### Optimization

To run faster (less polite):
```python
# In scrape_solved_threads.py, reduce sleep time:
time.sleep(random.uniform(0.5, 1.0))  # From (1.5, 3.0)
```

---

## ✅ Verification

After setup, verify everything works:

```bash
# 1. Run manually once
cd /home/user/insightpulse-odoo/agents/odoo-knowledge/crawler
./run_scraper_cron.sh

# 2. Check output
ls -lh /home/user/insightpulse-odoo/agents/odoo-knowledge/knowledge/

# 3. Check commit
git log -1

# 4. Verify schedule (cron)
crontab -l

# Or verify schedule (systemd)
systemctl list-timers odoo-scraper.timer
```

**Success indicators:**
- ✅ Script completes without errors
- ✅ New file: `knowledge/solved_threads_raw.json`
- ✅ Git commit created
- ✅ Changes pushed to remote
- ✅ Log file created in `logs/scraper/`

---

## 🎯 Summary

**Recommended Setup by Environment:**

| Environment | Best Option | Why |
|-------------|-------------|-----|
| **Production Server** | Systemd Timer | Monitoring, auto-restart, better logging |
| **Development Machine** | Cron | Simple, familiar, easy to debug |
| **No Infrastructure** | GitHub Actions | Zero setup, free, email notifications |
| **Docker/Kubernetes** | CronJob Resource | Native container orchestration |

**Current Status:** All three options are ready to use!

Pick one and activate it. The scraper will run automatically and keep your knowledge base up to date.
