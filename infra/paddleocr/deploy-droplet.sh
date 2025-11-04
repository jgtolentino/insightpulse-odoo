#!/bin/bash

# PaddleOCR Service - DigitalOcean Droplet Deployment
# Author: InsightPulse DevOps Team
# Version: 1.0.0
# Date: 2025-11-02

set -euo pipefail

# Configuration
DROPLET_NAME="paddleocr-ollama-service"
REGION="sgp1"  # Singapore
SIZE="s-2vcpu-4gb"  # $24/month (needed for PaddleOCR + Ollama w/ Llama 3.2 3B)
IMAGE="ubuntu-22-04-x64"
SSH_KEY_NAME="insightpulse-deploy"
DOMAIN="ocr.insightpulseai.net"
OLLAMA_DOMAIN="llm.insightpulseai.net"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v doctl &> /dev/null; then
        log_error "doctl not installed. Please install: https://docs.digitalocean.com/reference/doctl/how-to/install/"
        exit 1
    fi

    if ! doctl auth list | grep -q "current"; then
        log_error "doctl not authenticated. Run: doctl auth init"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Create droplet
create_droplet() {
    log_info "Creating droplet: $DROPLET_NAME..."

    # Check if droplet already exists
    if doctl compute droplet list --format Name | grep -q "^$DROPLET_NAME$"; then
        log_warn "Droplet '$DROPLET_NAME' already exists"
        DROPLET_ID=$(doctl compute droplet list --format ID,Name --no-header | grep "$DROPLET_NAME" | awk '{print $1}')
        log_info "Using existing droplet ID: $DROPLET_ID"
    else
        # Get SSH key ID
        SSH_KEY_ID=$(doctl compute ssh-key list --format ID,Name --no-header | grep "$SSH_KEY_NAME" | awk '{print $1}')

        if [ -z "$SSH_KEY_ID" ]; then
            log_error "SSH key '$SSH_KEY_NAME' not found. Please add your SSH key first."
            log_info "Run: doctl compute ssh-key create $SSH_KEY_NAME --public-key-file ~/.ssh/id_rsa.pub"
            exit 1
        fi

        # Create droplet
        DROPLET_ID=$(doctl compute droplet create $DROPLET_NAME \
            --region $REGION \
            --size $SIZE \
            --image $IMAGE \
            --ssh-keys $SSH_KEY_ID \
            --tag-names paddleocr,ollama,ai,production \
            --enable-monitoring \
            --enable-ipv6 \
            --wait \
            --format ID \
            --no-header)

        log_info "Droplet created with ID: $DROPLET_ID"
    fi

    # Wait for droplet to be active
    log_info "Waiting for droplet to be active..."
    sleep 30

    # Get droplet IP
    DROPLET_IP=$(doctl compute droplet get $DROPLET_ID --format PublicIPv4 --no-header)
    log_info "Droplet IP: $DROPLET_IP"

    echo "$DROPLET_IP" > .droplet_ip
}

# Configure DNS
configure_dns() {
    log_info "Configuring DNS for $DOMAIN..."

    DROPLET_IP=$(cat .droplet_ip)

    # Create DNS A record
    if doctl compute domain records list insightpulseai.net --format Name | grep -q "^ocr$"; then
        log_warn "DNS record already exists"
        # Update existing record
        RECORD_ID=$(doctl compute domain records list insightpulseai.net --format ID,Name --no-header | grep "ocr" | awk '{print $1}')
        doctl compute domain records update insightpulseai.net \
            --record-id $RECORD_ID \
            --record-data $DROPLET_IP
        log_info "DNS record updated"
    else
        doctl compute domain records create insightpulseai.net \
            --record-type A \
            --record-name ocr \
            --record-data $DROPLET_IP \
            --record-ttl 3600
        log_info "DNS record created"
    fi

    log_info "DNS configured: $DOMAIN -> $DROPLET_IP"

    # Configure DNS for Ollama subdomain
    if doctl compute domain records list insightpulseai.net --format Name | grep -q "^llm$"; then
        log_warn "Ollama DNS record already exists"
        RECORD_ID=$(doctl compute domain records list insightpulseai.net --format ID,Name --no-header | grep "llm" | awk '{print $1}')
        doctl compute domain records update insightpulseai.net \
            --record-id $RECORD_ID \
            --record-data $DROPLET_IP
        log_info "Ollama DNS record updated"
    else
        doctl compute domain records create insightpulseai.net \
            --record-type A \
            --record-name llm \
            --record-data $DROPLET_IP \
            --record-ttl 3600
        log_info "Ollama DNS record created"
    fi

    log_info "Ollama DNS configured: $OLLAMA_DOMAIN -> $DROPLET_IP"
}

# Setup server
setup_server() {
    log_info "Setting up server..."

    DROPLET_IP=$(cat .droplet_ip)

    # Wait for SSH to be available
    log_info "Waiting for SSH to be available..."
    timeout 120 bash -c "until ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@$DROPLET_IP 'echo SSH is ready'; do sleep 5; done"

    # Copy setup script
    log_info "Copying setup script to droplet..."
    scp -o StrictHostKeyChecking=no infra/paddleocr/setup-server.sh root@$DROPLET_IP:/tmp/

    # Execute setup script
    log_info "Executing setup script on droplet..."
    ssh -o StrictHostKeyChecking=no root@$DROPLET_IP "bash /tmp/setup-server.sh"

    log_info "Server setup completed"
}

# Deploy application
deploy_application() {
    log_info "Deploying PaddleOCR application..."

    DROPLET_IP=$(cat .droplet_ip)

    # Copy application files
    log_info "Copying application files..."
    scp -o StrictHostKeyChecking=no -r infra/paddleocr/app root@$DROPLET_IP:/opt/paddleocr/

    # Copy docker-compose file
    scp -o StrictHostKeyChecking=no infra/paddleocr/docker-compose.yml root@$DROPLET_IP:/opt/paddleocr/

    # Copy environment variables
    scp -o StrictHostKeyChecking=no infra/paddleocr/.env.production root@$DROPLET_IP:/opt/paddleocr/.env

    # Start application
    log_info "Starting application..."
    ssh -o StrictHostKeyChecking=no root@$DROPLET_IP "cd /opt/paddleocr && docker-compose up -d"

    # Copy and execute Ollama initialization script
    log_info "Initializing Ollama..."
    scp -o StrictHostKeyChecking=no infra/paddleocr/init-ollama.sh root@$DROPLET_IP:/opt/paddleocr/
    ssh -o StrictHostKeyChecking=no root@$DROPLET_IP "cd /opt/paddleocr && bash init-ollama.sh"

    log_info "Application deployed"
}

# Configure firewall
configure_firewall() {
    log_info "Configuring firewall..."

    DROPLET_ID=$(doctl compute droplet list --format ID,Name --no-header | grep "$DROPLET_NAME" | awk '{print $1}')

    # Create firewall if it doesn't exist
    if ! doctl compute firewall list --format Name | grep -q "paddleocr-firewall"; then
        doctl compute firewall create \
            --name paddleocr-firewall \
            --inbound-rules "protocol:tcp,ports:22,sources:addresses:0.0.0.0/0 protocol:tcp,ports:80,sources:addresses:0.0.0.0/0 protocol:tcp,ports:443,sources:addresses:0.0.0.0/0" \
            --outbound-rules "protocol:tcp,ports:all,destinations:addresses:0.0.0.0/0 protocol:udp,ports:all,destinations:addresses:0.0.0.0/0" \
            --droplet-ids $DROPLET_ID
        log_info "Firewall created and applied"
    else
        log_warn "Firewall already exists"
    fi
}

# Health check
health_check() {
    log_info "Running health check..."

    DROPLET_IP=$(cat .droplet_ip)

    # Wait for application to start
    log_info "Waiting for application to start..."
    sleep 10

    # Check health endpoint
    MAX_RETRIES=12
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -f -s "http://$DROPLET_IP:8000/health" > /dev/null; then
            log_info "Health check passed!"
            curl -s "http://$DROPLET_IP:8000/health" | jq .
            return 0
        fi

        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_warn "Health check failed (attempt $RETRY_COUNT/$MAX_RETRIES). Retrying in 5 seconds..."
        sleep 5
    done

    log_error "Health check failed after $MAX_RETRIES attempts"
    return 1
}

# Main deployment flow
main() {
    log_info "Starting PaddleOCR service deployment..."
    log_info "Droplet: $DROPLET_NAME"
    log_info "Region: $REGION"
    log_info "Size: $SIZE"
    log_info "Domain: $DOMAIN"
    echo ""

    check_prerequisites
    create_droplet
    configure_dns
    setup_server
    deploy_application
    configure_firewall
    health_check

    log_info "================================"
    log_info "Deployment completed successfully!"
    log_info "================================"
    log_info "Service URL: http://$DOMAIN"
    log_info "API Endpoint: http://$DOMAIN/api/v1/ocr/scan"
    log_info "Health Check: http://$DOMAIN/health"
    log_info ""
    log_info "Next steps:"
    log_info "1. Configure SSL certificate with Let's Encrypt"
    log_info "2. Update Odoo configuration to use new OCR endpoint"
    log_info "3. Test OCR integration with mobile app"
    log_info ""
}

# Run main function
main "$@"
