#!/bin/bash

echo "🐳 Testing Docker Setup for InsightPulse Odoo"
echo "=============================================="

# Test 1: Docker login
echo "1. Testing Docker Hub login..."
if docker info >/dev/null 2>&1; then
    echo "✅ Docker daemon is running"
else
    echo "❌ Docker daemon is not running"
    exit 1
fi

# Test 2: Check if we can pull a test image
echo "2. Testing image pull capability..."
if docker pull alpine:latest >/dev/null 2>&1; then
    echo "✅ Can pull images from Docker Hub"
else
    echo "❌ Cannot pull images from Docker Hub"
    exit 1
fi

# Test 3: Check if .env file exists
echo "3. Checking configuration files..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    echo "   DOCKER_USER: $(grep DOCKER_USER .env | cut -d'=' -f2)"
    echo "   ODOO_REF: $(grep ODOO_REF .env | cut -d'=' -f2)"
else
    echo "❌ .env file not found. Run: cp .env.example .env"
    exit 1
fi

# Test 4: Check if required files exist
echo "4. Checking required files..."
files=("Dockerfile" "docker-compose.yml" ".github/workflows/docker-build.yml")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Test 5: Validate docker-compose syntax
echo "5. Validating docker-compose.yml..."
if docker compose config >/dev/null 2>&1; then
    echo "✅ docker-compose.yml is valid"
else
    echo "❌ docker-compose.yml has syntax errors"
    exit 1
fi

echo ""
echo "🎉 All tests passed! Your Docker setup is ready."
echo ""
echo "Next steps:"
echo "1. Set up GitHub repository secrets:"
echo "   - REGISTRY_TOKEN: <docker-registry-token>"
echo "   - REGISTRY_USER: jgtolentino"
echo "2. Push to main branch to trigger CI/CD"
echo "3. Monitor the Actions tab for build status"
