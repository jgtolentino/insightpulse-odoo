#!/bin/bash

# Ollama Initialization Script
# Pulls Llama 3.2 3B model after deployment

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_info "Initializing Ollama with Llama 3.2 3B model..."

# Wait for Ollama service to be ready
log_info "Waiting for Ollama service to start..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker exec ollama-service ollama list &> /dev/null; then
        log_info "Ollama service is ready!"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    log_warn "Waiting for Ollama (attempt $RETRY_COUNT/$MAX_RETRIES)..."
    sleep 5
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "Error: Ollama service did not start in time"
    exit 1
fi

# Pull Llama 3.2 3B model
log_info "Pulling Llama 3.2 3B model (this will take a few minutes)..."
docker exec ollama-service ollama pull llama3.2:3b

# Verify model is available
log_info "Verifying model installation..."
docker exec ollama-service ollama list

# Test model with a simple prompt
log_info "Testing model with a simple prompt..."
docker exec ollama-service ollama run llama3.2:3b "Say hello in one sentence" --verbose false

log_info "================================"
log_info "Ollama initialized successfully!"
log_info "================================"
log_info ""
log_info "Model: llama3.2:3b"
log_info "API Endpoint: http://localhost:11434"
log_info "Public URL: https://llm.insightpulseai.net (after SSL setup)"
log_info ""
log_info "Test API:"
log_info 'curl -X POST http://localhost:11434/api/generate -d'"'"'{"model":"llama3.2:3b","prompt":"Hello","stream":false}'"'"''
log_info ""
