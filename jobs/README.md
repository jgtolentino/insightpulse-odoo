# Background Jobs

Scheduled background jobs for InsightPulse infrastructure.

## Forum Scraper

**Purpose**: Scrape Odoo community forum posts for MCP knowledge base

**Schedule**: Every 10 minutes via cron

**Configuration**:

### 1. Database Setup

Apply the schema:

```bash
psql "$POSTGRES_URL" -f infra/sql/mcp_forum_posts.sql
```

### 2. Environment Variables

Required environment variables:

```bash
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="<your-service-role-key>"
```

### 3. Install Dependencies

```bash
pip install supabase-py requests
```

### 4. Cron Setup

Add to crontab (`crontab -e`):

```cron
# Forum scraper - runs every 10 minutes
*/10 * * * * /usr/local/bin/python3 /opt/stack/jobs/forum_scrape.py >> /var/log/forum_scrape.log 2>&1
```

Or for DigitalOcean droplet:

```bash
# Create systemd timer
sudo tee /etc/systemd/system/forum-scraper.service <<EOF
[Unit]
Description=Odoo Forum Scraper
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/stack
Environment="SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co"
Environment="SUPABASE_SERVICE_ROLE_KEY=<your-key>"
ExecStart=/usr/local/bin/python3 /opt/stack/jobs/forum_scrape.py
StandardOutput=append:/var/log/forum_scrape.log
StandardError=append:/var/log/forum_scrape.log

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/forum-scraper.timer <<EOF
[Unit]
Description=Run Forum Scraper every 10 minutes
Requires=forum-scraper.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=10min
AccuracySec=1min

[Install]
WantedBy=timers.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable forum-scraper.timer
sudo systemctl start forum-scraper.timer

# Check status
sudo systemctl status forum-scraper.timer
sudo journalctl -u forum-scraper.service -f
```

### 5. Manual Run

Test the scraper manually:

```bash
python3 jobs/forum_scrape.py
```

### 6. Monitor Logs

```bash
# Cron logs
tail -f /var/log/forum_scrape.log

# Systemd logs
sudo journalctl -u forum-scraper.service -f
```

## Query Examples

```sql
-- Recent posts
SELECT id, topic, title, author, created_at, views, replies
FROM mcp.forum_posts
ORDER BY created_at DESC
LIMIT 20;

-- Most viewed posts by topic
SELECT topic, title, author, views, replies, url
FROM mcp.forum_posts
WHERE topic = 'odoo-19'
ORDER BY views DESC
LIMIT 10;

-- Full-text search
SELECT title, author, created_at, url
FROM mcp.forum_posts
WHERE to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(content, ''))
    @@ to_tsquery('english', 'accounting & invoice');

-- Posts by tag
SELECT title, author, tags, url
FROM mcp.forum_posts
WHERE tags && ARRAY['accounting', 'invoice']
ORDER BY created_at DESC;
```

## Troubleshooting

### Check if scraper is running

```bash
# Cron
ps aux | grep forum_scrape

# Systemd
sudo systemctl status forum-scraper.timer
```

### Verify database connection

```bash
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM mcp.forum_posts;"
```

### Test forum API

```bash
curl -s "https://www.odoo.com/forum/help-1?limit=5" | head -50
```

### Clear old posts (optional)

```sql
-- Delete posts older than 90 days
DELETE FROM mcp.forum_posts
WHERE created_at < NOW() - INTERVAL '90 days';
```
