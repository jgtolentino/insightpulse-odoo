# Superset on DigitalOcean Droplets - Complete Guide

Deploy Apache Superset on a DigitalOcean Droplet with Docker Compose for maximum control and cost-effectiveness.

## When to Use Droplets vs App Platform

| Criteria | Droplets | App Platform |
|----------|----------|--------------|
| **Control** | Full root access, custom config | Managed, limited config |
| **Cost** | $12-24/month (1-2 droplets) | $27/month (service + Redis) |
| **Scaling** | Manual, but flexible | Automatic (horizontal) |
| **Maintenance** | You manage OS, security | DigitalOcean manages |
| **SSL** | Let's Encrypt (manual) | Automatic |
| **Backups** | Snapshots ($1.20/month) | Included |
| **Best for** | Cost optimization, full control | Ease of use, zero maintenance |

**Recommendation**: Use Droplets if you want to save 30-40% monthly costs and have DevOps experience.

## Prerequisites

- DigitalOcean account
- SSH key pair
- Domain name (optional, for SSL)
- Basic Linux knowledge

## Step 1: Create Droplet

### Via Control Panel

1. Go to https://cloud.digitalocean.com/droplets
2. Click **Create Droplet**
3. Select configuration:

```yaml
Image: Ubuntu 24.04 LTS x64
Droplet Type: Basic (Shared CPU)
CPU Options: Regular
Plan: 
  - Development/Testing: $12/month (2GB RAM, 1 vCPU, 50GB SSD)
  - Production (recommended): $24/month (4GB RAM, 2 vCPU, 80GB SSD)
  - Heavy usage: $48/month (8GB RAM, 4 vCPU, 160GB SSD)

Region: Singapore (SGP1) - or nearest to your users

VPC: Enable (default) ✓
IPv6: Enable ✓
Monitoring: Enable ✓
Backups: Enable ($1.20-4.80/month) ✓

SSH Key: Select your public key
Hostname: superset-prod
Tags: finance-ssc, superset, production
```

4. Click **Create Droplet**

### Via doctl CLI

```bash
# Create Droplet with recommended specs
doctl compute droplet create superset-prod \
  --image ubuntu-24-04-x64 \
  --size s-2vcpu-4gb \
  --region sgp1 \
  --enable-ipv6 \
  --enable-monitoring \
  --enable-backups \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header) \
  --tag-names finance-ssc,superset,production \
  --wait

# Get Droplet IP
DROPLET_IP=$(doctl compute droplet list superset-prod --format PublicIPv4 --no-header)
echo "Droplet IP: $DROPLET_IP"
```

## Step 2: Initial Server Setup

SSH into your Droplet:

```bash
ssh root@$DROPLET_IP
```

### 2.1 Create Non-Root User

```bash
# Create user
adduser superset
usermod -aG sudo superset

# Copy SSH keys
rsync --archive --chown=superset:superset ~/.ssh /home/superset

# Test login (in new terminal)
ssh superset@$DROPLET_IP
```

### 2.2 Configure Firewall

```bash
# SSH from local machine only
sudo ufw allow from YOUR_LOCAL_IP to any port 22

# HTTP/HTTPS for web access
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw --force enable
sudo ufw status
```

**Better approach**: Use DigitalOcean Cloud Firewall (free):

```bash
# Create firewall via doctl
doctl compute firewall create \
  --name superset-firewall \
  --inbound-rules "protocol:tcp,ports:22,sources:addresses:YOUR_IP protocol:tcp,ports:80,sources:addresses:0.0.0.0/0,::/0 protocol:tcp,ports:443,sources:addresses:0.0.0.0/0,::/0" \
  --droplet-ids $(doctl compute droplet list superset-prod --format ID --no-header)
```

### 2.3 Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
sudo reboot
```

## Step 3: Install Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version

# Enable Docker to start on boot
sudo systemctl enable docker
```

## Step 4: Deploy Superset with Docker Compose

### 4.1 Create Project Directory

```bash
mkdir -p ~/superset && cd ~/superset
```

### 4.2 Create docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: superset-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - superset-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  postgres:
    image: postgres:15-alpine
    container_name: superset-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: superset
      POSTGRES_USER: superset
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - superset-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U superset"]
      interval: 10s
      timeout: 5s
      retries: 5

  superset:
    image: apache/superset:3.1.0
    container_name: superset
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
    environment:
      # Database
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      DATABASE_DB: superset
      DATABASE_USER: superset
      DATABASE_PASSWORD: ${POSTGRES_PASSWORD}
      
      # Redis
      REDIS_HOST: redis
      REDIS_PORT: 6379
      
      # Superset config
      SUPERSET_SECRET_KEY: ${SUPERSET_SECRET_KEY}
      SUPERSET_ENV: production
      SUPERSET_LOAD_EXAMPLES: 'False'
      
      # Security
      ENABLE_PROXY_FIX: 'True'
      WTF_CSRF_ENABLED: 'True'
      TALISMAN_ENABLED: 'False'  # Behind Nginx
    ports:
      - "8088:8088"
    volumes:
      - superset-home:/app/superset_home
    networks:
      - superset-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8088/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  redis-data:
  postgres-data:
  superset-home:

networks:
  superset-network:
    driver: bridge
EOF
```

### 4.3 Create .env File

```bash
cat > .env << 'EOF'
# Generate secure password: openssl rand -base64 32
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD_HERE

# Generate secret key: openssl rand -base64 42
SUPERSET_SECRET_KEY=YOUR_SECRET_KEY_HERE
EOF

# Secure the .env file
chmod 600 .env
```

### 4.4 Start Services

```bash
# Pull images
docker compose pull

# Start services
docker compose up -d

# Check logs
docker compose logs -f superset
```

## Step 5: Initialize Superset

```bash
# Database migrations
docker compose exec superset superset db upgrade

# Create admin user
docker compose exec superset superset fab create-admin \
  --username admin \
  --firstname Jake \
  --lastname Tolentino \
  --email jgtolentino_rm@yahoo.com \
  --password SupersetAdmin2024!

# Initialize Superset
docker compose exec superset superset init

# Verify services
docker compose ps
```

Expected output:
```
NAME                COMMAND             STATUS        PORTS
superset            /app/docker/...     Up (healthy)  0.0.0.0:8088->8088/tcp
superset-postgres   docker-entryp...    Up (healthy)  5432/tcp
superset-redis      docker-entryp...    Up (healthy)  6379/tcp
```

## Step 6: Configure Nginx Reverse Proxy

### 6.1 Install Nginx

```bash
sudo apt install nginx -y
sudo systemctl enable nginx
```

### 6.2 Create Superset Config

```bash
sudo tee /etc/nginx/sites-available/superset << 'EOF'
upstream superset {
    server localhost:8088;
}

server {
    listen 80;
    server_name superset.insightpulseai.net;

    # Redirect to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://superset;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/superset /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6.3 Configure DNS

Add A record in your domain registrar:
```
Type: A
Name: superset
Value: YOUR_DROPLET_IP
TTL: 3600
```

Test: `http://superset.insightpulseai.net`

## Step 7: Enable SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d superset.insightpulseai.net \
  --non-interactive \
  --agree-tos \
  --email jgtolentino_rm@yahoo.com \
  --redirect

# Test auto-renewal
sudo certbot renew --dry-run

# Certificate auto-renews via systemd timer
sudo systemctl status certbot.timer
```

Access: `https://superset.insightpulseai.net` 🔒

## Step 8: Configure Backups

### 8.1 Automated Daily Backups

```bash
# Create backup script
cat > ~/superset/backup.sh << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/var/backups/superset"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker compose exec -T postgres pg_dump -U superset superset | \
  gzip > $BACKUP_DIR/superset_db_$DATE.sql.gz

# Backup Superset home directory
docker compose exec -T superset tar czf - /app/superset_home | \
  cat > $BACKUP_DIR/superset_home_$DATE.tar.gz

# Backup docker-compose config
tar czf $BACKUP_DIR/superset_config_$DATE.tar.gz \
  docker-compose.yml .env

# Keep last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x ~/superset/backup.sh
```

### 8.2 Schedule with Cron

```bash
# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /home/superset/superset/backup.sh >> /var/log/superset-backup.log 2>&1") | crontab -

# Verify
crontab -l
```

### 8.3 Off-site Backup to Spaces

```bash
# Install s3cmd
sudo apt install s3cmd -y

# Configure (use DO Spaces credentials)
s3cmd --configure

# Add to backup script
cat >> ~/superset/backup.sh << 'EOF'

# Upload to Spaces
s3cmd sync $BACKUP_DIR/ s3://your-space-name/superset-backups/
EOF
```

## Step 9: Monitoring & Maintenance

### 9.1 Enable DO Monitoring Agent

```bash
# Install agent (if not already)
curl -sSL https://repos.insights.digitalocean.com/install.sh | sudo bash
```

View metrics at: https://cloud.digitalocean.com/monitoring

### 9.2 Setup Log Rotation

```bash
sudo tee /etc/logrotate.d/superset << 'EOF'
/var/log/superset-backup.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

### 9.3 Health Check Script

```bash
cat > ~/superset/healthcheck.sh << 'EOF'
#!/bin/bash

# Check containers
if ! docker compose ps | grep -q "Up (healthy)"; then
    echo "ERROR: Unhealthy containers detected"
    docker compose ps
    exit 1
fi

# Check Superset endpoint
if ! curl -sf http://localhost:8088/health > /dev/null; then
    echo "ERROR: Superset health check failed"
    exit 1
fi

echo "OK: All services healthy"
EOF

chmod +x ~/superset/healthcheck.sh

# Add to cron (every 5 minutes)
(crontab -l; echo "*/5 * * * * /home/superset/superset/healthcheck.sh") | crontab -
```

## Step 10: Connect to Supabase

In Superset UI:

1. Go to **Settings** > **Database Connections**
2. Click **+ Database**
3. Fill in:

```
Database: Supabase Production
URI: postgresql://postgres:PASSWORD@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres?sslmode=require
```

4. Test Connection → **Connect**

## Cost Breakdown

**Monthly Costs (Production Setup):**
```
Droplet (4GB RAM):     $24.00
Backups (20%):         $ 4.80
Block Storage (optional): $ 1.00/10GB
Total:                 $29.80/month
```

**vs App Platform:**
```
Superset service:      $12.00
Managed Redis:         $15.00
Total:                 $27.00/month
```

**Trade-offs:**
- Droplets: +$2.80/month, but includes PostgreSQL
- App Platform: Easier, but external PostgreSQL needed

**With Supabase (both approaches):**
- Supabase Free Tier: $0
- **Total Droplet:** $29.80/month
- **Total App Platform:** $27/month

**Winner**: App Platform for simplicity, Droplet for control.

## Performance Tuning

### PostgreSQL Optimization

```bash
# Edit postgresql.conf
docker compose exec postgres bash
vi /var/lib/postgresql/data/postgresql.conf

# Add these settings:
shared_buffers = 1GB            # 25% of RAM
effective_cache_size = 3GB      # 75% of RAM
maintenance_work_mem = 256MB
work_mem = 16MB
max_connections = 100

# Restart
docker compose restart postgres
```

### Superset Caching

Edit `docker-compose.yml`:
```yaml
environment:
  CACHE_CONFIG: |
    {
      'CACHE_TYPE': 'RedisCache',
      'CACHE_DEFAULT_TIMEOUT': 3600,
      'CACHE_KEY_PREFIX': 'superset_',
      'CACHE_REDIS_URL': 'redis://redis:6379/0'
    }
```

Restart: `docker compose restart superset`

## Troubleshooting

### Issue: Containers won't start
```bash
# Check logs
docker compose logs superset
docker compose logs postgres

# Check disk space
df -h

# Check memory
free -h
```

### Issue: Database connection failed
```bash
# Verify PostgreSQL is running
docker compose exec postgres psql -U superset -c "SELECT version();"

# Check connection from Superset
docker compose exec superset python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://superset:PASSWORD@postgres:5432/superset')
print(engine.connect())
"
```

### Issue: Out of memory
```bash
# Check container memory
docker stats

# Upgrade Droplet size
doctl compute droplet-action resize DROPLET_ID --size s-4vcpu-8gb --wait

# Or enable swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue: SSL certificate renewal failed
```bash
# Manual renewal
sudo certbot renew --force-renewal

# Check timer
sudo systemctl status certbot.timer
sudo journalctl -u certbot.service
```

## Upgrading Superset

```bash
cd ~/superset

# Backup first!
./backup.sh

# Update docker-compose.yml
sed -i 's/superset:3.1.0/superset:3.1.1/' docker-compose.yml

# Pull new image
docker compose pull superset

# Restart
docker compose down
docker compose up -d

# Run migrations
docker compose exec superset superset db upgrade
```

## Security Checklist

- [ ] SSH key authentication only (no passwords)
- [ ] Cloud Firewall configured
- [ ] SSL/TLS enabled
- [ ] Non-root user for application
- [ ] .env file secured (chmod 600)
- [ ] Automated backups enabled
- [ ] Monitoring enabled
- [ ] Log rotation configured
- [ ] Regular security updates
- [ ] Strong database passwords

## Maintenance Schedule

**Daily:**
- Automated backups (2 AM)
- Health checks (every 5 minutes)

**Weekly:**
- Review logs
- Check disk space
- Review backup success

**Monthly:**
- Update system packages
- Review firewall rules
- Test backup restoration
- Check SSL certificate expiry

**Quarterly:**
- Upgrade Superset version
- Review and optimize queries
- Capacity planning

## Next Steps

1. ✅ Connect to Supabase
2. ✅ Create BIR compliance datasets
3. ✅ Build Finance SSC dashboards
4. ✅ Configure row-level security
5. ✅ Set up alerting

## Support

- **DigitalOcean Docs**: https://docs.digitalocean.com/products/droplets/
- **Docker Compose**: https://docs.docker.com/compose/
- **Superset Docs**: https://superset.apache.org/docs/intro

---

**Your self-hosted Superset is production-ready!** 🚀

Access: https://superset.insightpulseai.net
