#!/bin/bash
# Reset Superset admin password

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔐 Resetting Superset Admin Password${NC}"
echo ""

# Check if container is running
if ! docker ps | grep -q superset; then
    echo -e "${YELLOW}⚠️  Superset container is not running${NC}"
    echo "Starting Superset..."
    cd "$(dirname "$0")/../deploy" || exit 1
    docker-compose -f superset.compose.yml up -d superset
    sleep 30
fi

# Prompt for new password
read -sp "Enter new admin password: " NEW_PASSWORD
echo ""
read -sp "Confirm new password: " NEW_PASSWORD_CONFIRM
echo ""

if [ "$NEW_PASSWORD" != "$NEW_PASSWORD_CONFIRM" ]; then
    echo "Passwords do not match!"
    exit 1
fi

if [ ${#NEW_PASSWORD} -lt 8 ]; then
    echo "Password must be at least 8 characters long!"
    exit 1
fi

# Reset admin password
echo "Resetting admin password..."
docker exec -it superset bash -c "
superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@insightpulseai.net \
  --password '$NEW_PASSWORD' || \
superset fab reset-password --username admin --password '$NEW_PASSWORD'
"

echo ""
echo -e "${GREEN}✅ Admin password reset successfully${NC}"
echo ""
echo "You can now login with:"
echo "  Username: admin"
echo "  Password: <your-new-password>"
echo ""
