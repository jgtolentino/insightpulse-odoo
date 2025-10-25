#!/bin/bash

# Multi-architecture Docker build script
# Follows DigitalOcean best practices for Odoo deployment

set -e

# Configuration
DOCKER_USER=${DOCKER_USER:-jgtolentino}
ODOO_REF=${ODOO_REF:-19.0}
IMAGE_NAME="${DOCKER_USER}/insightpulse-odoo"
TAG=${1:-${ODOO_REF}}

echo "🐳 Building multi-architecture Odoo image"
echo "========================================"
echo "Image: ${IMAGE_NAME}:${TAG}"
echo "Odoo version: ${ODOO_REF}"
echo "Platforms: linux/amd64, linux/arm64/v8"
echo ""

# Create buildx builder if it doesn't exist
if ! docker buildx ls | grep -q "odoboo"; then
    echo "Creating buildx builder 'odoboo'..."
    docker buildx create --name odoboo --driver cloud --use
else
    echo "Using existing buildx builder 'odoboo'..."
    docker buildx use odoboo
fi

# Build and push multi-architecture image
echo "Building and pushing multi-architecture image..."
docker buildx build \
    --platform linux/amd64,linux/arm64/v8 \
    --build-arg ODOO_REF=${ODOO_REF} \
    -t ${IMAGE_NAME}:${TAG} \
    -t ${IMAGE_NAME}:latest \
    --push \
    .

echo ""
echo "✅ Multi-architecture build complete!"
echo "Image: ${IMAGE_NAME}:${TAG}"
echo "Image: ${IMAGE_NAME}:latest"
echo ""
echo "To verify the manifest:"
echo "docker buildx imagetools inspect ${IMAGE_NAME}:${TAG}"
