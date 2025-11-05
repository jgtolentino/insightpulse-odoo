#!/bin/bash
#
# Superset Droplet Setup Script
# Automated installation of Apache Superset on DigitalOcean Droplet
#
# Usage: curl -fsSL https://raw.githubusercontent.com/your-repo/setup.sh | bash
# Or: chmod +x setup.sh && ./setup.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SUPERSET_VERSION="3.1.0"
POSTGRES_VERSION="15"
REDIS_VERSION="7"
INSTALL_DIR="/opt/superset"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
    fi
}

check_os() {
    if [[ ! -f /etc/os-release ]]; then
        log_error "Cannot detect OS. This script requires Ubuntu 22.04 or 24.04"
    fi
    
    source /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        log_error "This script requires Ubuntu. Detected: $ID"
    fi
    
    if [[ "$VERSION_ID" != "22.04" && "$VERSION_ID" != "24.04" ]]; then
        log_warn "Tested on Ubuntu 22.04/24.04. Current: $VERSION_ID. Proceeding anyway..."
    fi
    
    log_info "OS: Ubuntu $VERSION_ID"
}

update_system() {
    log_info "Updating system packages..."
    apt update
    apt upgrade -y
    apt autoremove -y
}

install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker already installed: $(docker --version)"
        return
    fi
    
    log_info "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Enable Docker to start on boot
    systemctl enable docker
    systemctl start docker
    
    log_info "Docker installed: $(docker --version)"
}

install_docker_compose() {
    if docker compose version &> /dev/null; then
        log_info "Docker Compose already installed: $(docker compose version)"
        return
    fi
    
    log_error "Docker Compose not found. Please install Docker 20.10+."
}

configure_firewall() {
    log_info "Configuring UFW firewall..."
    
    # Install UFW if not present
    apt install -y ufw
    
    # Default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH (port 22)
    ufw allow 22/tcp comment 'SSH'
    
    # Allow HTTP/HTTPS
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    
    # Enable firewall
    ufw --force enable
    
    log_info "Firewall configured"
}

create_install_dir() {
    log_info "Creating installation directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
}

generate_secrets() {
    log_info "Generating secure secrets..."
    
    POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d /=+)
    SUPERSET_SECRET_KEY=$(openssl rand -base64 42 | tr -d /=+)
    
    log_info "Secrets generated"
}

create_docker_compose() {
    log_info "Creating docker-compose.yml..."
    
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
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      DATABASE_DB: superset
      DATABASE_USER: superset
      DATABASE_PASSWORD: ${POSTGRES_PASSWORD}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      SUPERSET_SECRET_KEY: ${SUPERSET_SECRET_KEY}
      SUPERSET_ENV: production
      SUPERSET_LOAD_EXAMPLES: 'False'
      ENABLE_PROXY_FIX: 'True'
      WTF_CSRF_ENABLED: 'True'
      TALISMAN_ENABLED: 'False'
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

    log_info "docker-compose.yml created"
}

create_env_file() {
    log_info "Creating .env file..."
    
    cat > .env << EOF
# Generated on $(date)
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
SUPERSET_SECRET_KEY=$SUPERSET_SECRET_KEY
EOF

    chmod 600 .env
    log_info ".env file created and secured"
}

start_services() {
    log_info "Starting Docker services..."
    
    docker compose pull
    docker compose up -d
    
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Check if services are up
    if ! docker compose ps | grep -q "Up"; then
        log_error "Services failed to start. Check logs: docker compose logs"
    fi
    
    log_info "Services started successfully"
}

initialize_superset() {
    log_info "Initializing Superset database..."
    
    # Wait for DB to be ready
    sleep 10
    
    # Run migrations
    docker compose exec -T superset superset db upgrade
    
    # Get admin credentials
    echo
    echo -e "${YELLOW}================================================${NC}"
    echo -e "${YELLOW}    SUPERSET ADMIN CREDENTIALS${NC}"
    echo -e "${YELLOW}================================================${NC}"
    echo
    read -p "Admin username [admin]: " ADMIN_USER
    ADMIN_USER=${ADMIN_USER:-admin}
    
    read -p "Admin email: " ADMIN_EMAIL
    while [[ ! "$ADMIN_EMAIL" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; do
        echo -e "${RED}Invalid email format${NC}"
        read -p "Admin email: " ADMIN_EMAIL
    done
    
    read -sp "Admin password: " ADMIN_PASSWORD
    echo
    while [[ ${#ADMIN_PASSWORD} -lt 8 ]]; do
        echo -e "${RED}Password must be at least 8 characters${NC}"
        read -sp "Admin password: " ADMIN_PASSWORD
        echo
    done
    
    # Create admin user
    docker compose exec -T superset superset fab create-admin \
        --username "$ADMIN_USER" \
        --firstname "Admin" \
        --lastname "User" \
        --email "$ADMIN_EMAIL" \
        --password "$ADMIN_PASSWORD"
    
    # Initialize Superset
    docker compose exec -T superset superset init
    
    log_info "Superset initialized"
}

install_nginx() {
    if command -v nginx &> /dev/null; then
        log_info "Nginx already installed"
        return
    fi
    
    log_info "Installing Nginx..."
    apt install -y nginx
    systemctl enable nginx
    systemctl start nginx
}

configure_nginx() {
    log_info "Configuring Nginx reverse proxy..."
    
    # Get server IP
    SERVER_IP=$(curl -s ifconfig.me)
    
    cat > /etc/nginx/sites-available/superset << 'EOF'
upstream superset {
    server localhost:8088;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://superset;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/superset /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t
    
    # Reload Nginx
    systemctl reload nginx
    
    log_info "Nginx configured"
}

create_backup_script() {
    log_info "Creating backup script..."
    
    cat > "$INSTALL_DIR/backup.sh" << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/var/backups/superset"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "Starting backup: $DATE"

# Backup PostgreSQL
docker compose exec -T postgres pg_dump -U superset superset | \
  gzip > $BACKUP_DIR/superset_db_$DATE.sql.gz

# Backup Superset home
docker compose exec -T superset tar czf - /app/superset_home | \
  cat > $BACKUP_DIR/superset_home_$DATE.tar.gz

# Backup configuration
tar czf $BACKUP_DIR/superset_config_$DATE.tar.gz \
  docker-compose.yml .env

# Keep last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

    chmod +x "$INSTALL_DIR/backup.sh"
    
    # Add to crontab
    (crontab -l 2>/dev/null || echo "") | grep -v "superset/backup.sh" | \
        { cat; echo "0 2 * * * $INSTALL_DIR/backup.sh >> /var/log/superset-backup.log 2>&1"; } | \
        crontab -
    
    log_info "Backup script created and scheduled (daily 2 AM)"
}

print_summary() {
    SERVER_IP=$(curl -s ifconfig.me)
    
    echo
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}    SUPERSET INSTALLATION COMPLETE!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo
    echo -e "${YELLOW}Access Superset:${NC}"
    echo "  http://$SERVER_IP"
    echo
    echo -e "${YELLOW}Admin Credentials:${NC}"
    echo "  Username: $ADMIN_USER"
    echo "  Email: $ADMIN_EMAIL"
    echo "  Password: [the password you entered]"
    echo
    echo -e "${YELLOW}Installation Directory:${NC}"
    echo "  $INSTALL_DIR"
    echo
    echo -e "${YELLOW}Manage Services:${NC}"
    echo "  cd $INSTALL_DIR"
    echo "  docker compose ps         # Check status"
    echo "  docker compose logs -f    # View logs"
    echo "  docker compose restart    # Restart services"
    echo "  docker compose down       # Stop services"
    echo
    echo -e "${YELLOW}Backups:${NC}"
    echo "  Location: /var/backups/superset"
    echo "  Schedule: Daily at 2 AM"
    echo "  Manual: $INSTALL_DIR/backup.sh"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Set up DNS A record pointing to: $SERVER_IP"
    echo "  2. Install SSL: sudo certbot --nginx -d your-domain.com"
    echo "  3. Connect to Supabase or external database"
    echo "  4. Start building dashboards!"
    echo
    echo -e "${YELLOW}Documentation:${NC}"
    echo "  Superset: https://superset.apache.org/docs/intro"
    echo "  Docker Compose: https://docs.docker.com/compose/"
    echo
    echo -e "${GREEN}Happy dashboarding! 📊${NC}"
    echo
}

# Main execution
main() {
    echo
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}    Superset Automated Installation${NC}"
    echo -e "${GREEN}    DigitalOcean Droplet Edition${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo
    
    check_root
    check_os
    
    log_info "Starting installation..."
    
    update_system
    install_docker
    install_docker_compose
    configure_firewall
    create_install_dir
    generate_secrets
    create_docker_compose
    create_env_file
    start_services
    initialize_superset
    install_nginx
    configure_nginx
    create_backup_script
    
    print_summary
}

# Run main function
main
