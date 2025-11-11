#!/bin/bash
# deploy.sh

set -euo pipefail

echo "🚀 Deploying InsightPulse AI to production..."
echo "📦 Environment: PROD"

# Optional: Build containers
if [ -f "docker-compose.prod.yml" ]; then
  echo "Building production containers..."
  docker-compose -f docker-compose.prod.yml build

  echo "Pushing to registry..."
  docker-compose -f docker-compose.prod.yml push
fi

# Optional: Deploy to DigitalOcean
if [ -n "${DIGITALOCEAN_APP_ID:-}" ]; then
  echo "Deploying to DigitalOcean App Platform..."
  doctl apps update "$DIGITALOCEAN_APP_ID" --spec .do/app.yaml
fi

# Optional: Deploy via rsync (if configured)
if [ -n "${PROD_SERVER:-}" ] && [ -n "${PROD_PATH:-}" ]; then
  echo "Deploying via rsync to $PROD_SERVER:$PROD_PATH..."
  rsync -avz --exclude .git --exclude node_modules --exclude __pycache__ ./ "$PROD_SERVER:$PROD_PATH/"
fi

echo "✅ Deployment completed at $(date)"
