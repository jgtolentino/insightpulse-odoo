#!/bin/bash

# Traefik Reverse Proxy Deployment Script
# Deploy Traefik on DigitalOcean droplet

set -euo pipefail

# Configuration
DROPLET_NAME="traefik-proxy"
REGION="sgp1"
SIZE="s-1vcpu-1gb"  # $6/month
IMAGE="docker-20-04"
SSH_KEY_NAME="insightpulse-deploy"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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
        log_error "doctl not installed"
        exit 1
    fi

    if ! command -v htpasswd &> /dev/null; then
        log_warn "htpasswd not found. Install apache2-utils for password generation"
    fi

    log_info "Prerequisites check passed"
}

# Create droplet
create_droplet() {
    log_info "Creating Traefik droplet..."

    if doctl compute droplet list --format Name | grep -q "^$DROPLET_NAME$"; then
        log_warn "Droplet already exists"
        DROPLET_ID=$(doctl compute droplet list --format ID,Name --no-header | grep "$DROPLET_NAME" | awk '{print $1}')
    else
        SSH_KEY_ID=$(doctl compute ssh-key list --format ID,Name --no-header | grep "$SSH_KEY_NAME" | awk '{print $1}')

        DROPLET_ID=$(doctl compute droplet create $DROPLET_NAME \
            --region $REGION \
            --size $SIZE \
            --image $IMAGE \
            --ssh-keys $SSH_KEY_ID \
            --tag-names traefik,proxy,production \
            --enable-monitoring \
            --wait \
            --format ID \
            --no-header)
    fi

    log_info "Droplet ID: $DROPLET_ID"

    # Get IP
    sleep 20
    DROPLET_IP=$(doctl compute droplet get $DROPLET_ID --format PublicIPv4 --no-header)
    echo "$DROPLET_IP" > .droplet_ip

    log_info "Droplet IP: $DROPLET_IP"
}

# Configure DNS
configure_dns() {
    log_info "Configuring DNS..."

    DROPLET_IP=$(cat .droplet_ip)

    # Main domain A record
    doctl compute domain records create insightpulseai.net \
        --record-type A \
        --record-name "@" \
        --record-data $DROPLET_IP \
        --record-ttl 3600 || log_warn "Main A record may already exist"

    # Wildcard CNAME (optional)
    # doctl compute domain records create insightpulseai.net \
    #     --record-type CNAME \
    #     --record-name "*" \
    #     --record-data "insightpulseai.net." \
    #     --record-ttl 3600 || log_warn "Wildcard CNAME may already exist"

    log_info "DNS configured"
}

# Deploy Traefik
deploy_traefik() {
    log_info "Deploying Traefik..."

    DROPLET_IP=$(cat .droplet_ip)

    # Wait for SSH
    timeout 120 bash -c "until ssh -o StrictHostKeyChecking=no root@$DROPLET_IP 'echo ready'; do sleep 5; done"

    # Create directory
    ssh -o StrictHostKeyChecking=no root@$DROPLET_IP "mkdir -p /opt/traefik"

    # Copy files
    scp -o StrictHostKeyChecking=no traefik.yml dynamic.yml docker-compose.yml root@$DROPLET_IP:/opt/traefik/

    # Start Traefik
    ssh -o StrictHostKeyChecking=no root@$DROPLET_IP "cd /opt/traefik && docker-compose up -d"

    log_info "Traefik deployed"
}

# Main
main() {
    log_info "Deploying Traefik reverse proxy..."

    check_prerequisites
    create_droplet
    configure_dns
    deploy_traefik

    log_info "Deployment complete!"
    log_info "Traefik dashboard: https://traefik.insightpulseai.net"
}

main "$@"
