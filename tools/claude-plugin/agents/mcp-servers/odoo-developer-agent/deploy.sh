#!/bin/bash
set -e

# Odoo Developer Agent - Production Deployment Script
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production

ENVIRONMENT=${1:-staging}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Deploying Odoo Developer Agent to: $ENVIRONMENT"
echo "================================================"

# Load environment variables
if [ -f ".env.$ENVIRONMENT" ]; then
    export $(cat ".env.$ENVIRONMENT" | xargs)
    echo "✅ Loaded .env.$ENVIRONMENT"
else
    echo "❌ Error: .env.$ENVIRONMENT not found"
    exit 1
fi

# Verify required environment variables
required_vars=(
    "ANTHROPIC_API_KEY"
    "SUPABASE_URL"
    "SUPABASE_KEY"
    "DB_PASSWORD"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var not set"
        exit 1
    fi
done

echo "✅ Environment variables verified"

# Build Docker image
echo ""
echo "📦 Building Docker image..."
docker build -t odoo-developer-agent:${ENVIRONMENT} .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"

# Run tests
echo ""
echo "🧪 Running tests..."
docker run --rm \
    -e ANTHROPIC_API_KEY=test-key \
    -e SUPABASE_URL=http://localhost:54321 \
    -e SUPABASE_KEY=test-key \
    odoo-developer-agent:${ENVIRONMENT} \
    pytest tests/ -v

if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

echo "✅ All tests passed"

# Initialize knowledge base (first deployment only)
if [ ! -f ".knowledge_base_initialized" ]; then
    echo ""
    echo "📚 Initializing knowledge base..."
    
    # Start database
    docker-compose up -d knowledge-db
    sleep 10
    
    # Run indexer
    docker run --rm \
        -e ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} \
        -e SUPABASE_URL=${SUPABASE_URL} \
        -e SUPABASE_KEY=${SUPABASE_KEY} \
        -v $(pwd)/knowledge-base:/data/knowledge-base \
        odoo-developer-agent:${ENVIRONMENT} \
        python scripts/index_knowledge_base.py
    
    if [ $? -eq 0 ]; then
        touch .knowledge_base_initialized
        echo "✅ Knowledge base initialized"
    else
        echo "⚠️  Knowledge base initialization failed (continuing anyway)"
    fi
fi

# Deploy based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    echo ""
    echo "🌐 Deploying to production..."
    
    # Stop existing containers
    docker-compose -f docker-compose.prod.yml down
    
    # Start new containers
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for health check
    echo "⏳ Waiting for health check..."
    sleep 10
    
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost:3001/health > /dev/null 2>&1; then
            echo "✅ Health check passed"
            break
        fi
        attempt=$((attempt + 1))
        echo "  Attempt $attempt/$max_attempts..."
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Health check failed"
        docker-compose -f docker-compose.prod.yml logs
        exit 1
    fi
    
    # Run smoke tests
    echo ""
    echo "🔥 Running smoke tests..."
    ./scripts/smoke_tests.sh
    
    if [ $? -ne 0 ]; then
        echo "❌ Smoke tests failed"
        echo "⚠️  Rolling back..."
        docker-compose -f docker-compose.prod.yml down
        # Restore previous version if available
        exit 1
    fi
    
    echo "✅ Smoke tests passed"
    
elif [ "$ENVIRONMENT" = "staging" ]; then
    echo ""
    echo "🧪 Deploying to staging..."
    
    docker-compose down
    docker-compose up -d
    
    echo "⏳ Waiting for services..."
    sleep 10
    
    echo "✅ Staging deployment complete"
else
    echo "❌ Unknown environment: $ENVIRONMENT"
    exit 1
fi

# Display deployment summary
echo ""
echo "================================================"
echo "✅ Deployment Complete!"
echo "================================================"
echo ""
echo "Environment: $ENVIRONMENT"
echo "Agent URL: http://localhost:3001"
echo "Grafana: http://localhost:3000 (admin/admin)"
echo "Prometheus: http://localhost:9090"
echo ""
echo "Next steps:"
echo "1. Verify metrics in Grafana"
echo "2. Test agent tools: ./scripts/test_tools.sh"
echo "3. Monitor logs: docker-compose logs -f odoo-developer-agent"
echo ""
echo "To rollback: docker-compose down && ./deploy.sh $ENVIRONMENT --rollback"
echo ""
