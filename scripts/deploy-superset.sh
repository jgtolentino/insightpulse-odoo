#!/bin/bash
# Deploy Superset 4.1.1 with example dashboards for InsightPulse Odoo

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying Superset 4.1.1 with InsightPulse Dashboards${NC}"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites satisfied${NC}"
echo ""

# Navigate to deploy directory
cd "$(dirname "$0")/../deploy" || exit 1

# Check if .env file exists
if [ ! -f superset.env ]; then
    echo -e "${YELLOW}⚠️  superset.env not found. Creating from example...${NC}"
    if [ -f superset.env.example ]; then
        cp superset.env.example superset.env
        echo -e "${GREEN}✅ Created superset.env from example${NC}"
        echo -e "${YELLOW}⚠️  Please review superset.env and update with your credentials${NC}"
        exit 0
    else
        echo -e "${RED}❌ superset.env.example not found${NC}"
        exit 1
    fi
fi

# Pull latest images
echo "📥 Pulling Superset 4.1.1 image..."
docker-compose -f superset.compose.yml pull

# Stop existing containers
echo "🛑 Stopping existing Superset containers..."
docker-compose -f superset.compose.yml down

# Start services
echo "🚀 Starting Superset services..."
docker-compose -f superset.compose.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check health
echo "🏥 Checking service health..."
if docker-compose -f superset.compose.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Superset is running${NC}"
else
    echo -e "${RED}❌ Superset failed to start${NC}"
    docker-compose -f superset.compose.yml logs superset
    exit 1
fi

# Initialize dashboards (if script exists)
if [ -f ../infra/superset/init-dashboards.py ]; then
    echo "📊 Initializing example dashboards..."
    docker-compose -f superset.compose.yml exec -T superset python3 /app/pythonpath/init-dashboards.py
    echo -e "${GREEN}✅ Dashboards initialized${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Superset 4.1.1 deployment complete!${NC}"
echo ""

# Prompt to reset admin password
echo -e "${YELLOW}⚠️  SECURITY: Default admin password is 'admin'${NC}"
read -p "Do you want to reset the admin password now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ../scripts/reset-superset-admin.sh
else
    echo -e "${YELLOW}⚠️  Remember to reset the admin password later using:${NC}"
    echo "   ./scripts/reset-superset-admin.sh"
fi

echo ""
echo "Access Superset at: http://localhost:8088"
echo "Default credentials (if not reset):"
echo "  Username: admin"
echo "  Password: admin"
echo ""
echo "View logs: docker-compose -f superset.compose.yml logs -f superset"
echo "Stop services: docker-compose -f superset.compose.yml down"
echo ""
