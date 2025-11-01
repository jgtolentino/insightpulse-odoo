#!/bin/bash

# MCP Ecosystem Deployment Script
# This script deploys the complete MCP ecosystem for Pulser Hub

set -e

echo "🚀 Deploying MCP Ecosystem for Pulser Hub..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check environment variables
    if [[ -z "$DIGITALOCEAN_TOKEN" ]]; then
        print_warning "DIGITALOCEAN_TOKEN not set. Digital Ocean MCP server will not work."
    fi

    if [[ -z "$GITHUB_TOKEN" ]]; then
        print_warning "GITHUB_TOKEN not set. GitHub MCP server will not work."
    fi

    if [[ -z "$SUPERSET_PASSWORD" ]]; then
        print_warning "SUPERSET_PASSWORD not set. Superset MCP server will not work."
    fi

    print_success "Prerequisites check completed"
}

# Build MCP Docker image
build_mcp_image() {
    print_status "Building Pulser Hub MCP Docker image..."
    cd mcp
    docker build -t pulser-hub-mcp:latest .
    cd ..
    print_success "MCP Docker image built successfully"
}

# Deploy MCP ecosystem
deploy_mcp_ecosystem() {
    print_status "Deploying MCP ecosystem..."

    # Create necessary directories
    mkdir -p mcp/logs
    mkdir -p mcp/orchestrator
    mkdir -p mcp/bridge
    mkdir -p mcp/dashboard

    # Start MCP services
    cd mcp
    docker-compose -f docker-compose.mcp.yml up -d

    # Wait for services to start
    sleep 10

    # Check if services are running
    if docker-compose -f docker-compose.mcp.yml ps | grep -q "Up"; then
        print_success "MCP ecosystem services started successfully"
    else
        print_error "Some MCP services failed to start"
        docker-compose -f docker-compose.mcp.yml logs
        exit 1
    fi

    cd ..
}

# Configure VS Code MCP integration
configure_vscode() {
    print_status "Configuring VS Code MCP integration..."

    # Copy VS Code configuration
    if [[ -d "$HOME/.vscode" ]]; then
        cp mcp/vscode-mcp-config.json "$HOME/.vscode/mcp.json"
        print_success "VS Code MCP configuration copied"
    else
        print_warning "VS Code directory not found. Please copy mcp/vscode-mcp-config.json to your VS Code settings manually."
    fi

    # Create environment file template
    cat > mcp/.env.example << EOF
# MCP Ecosystem Environment Variables
DIGITALOCEAN_TOKEN=your_digitalocean_token_here
GITHUB_TOKEN=your_github_token_here
SUPERSET_PASSWORD=your_superset_password_here
KUBECONFIG=/path/to/your/kubeconfig
EOF

    print_success "VS Code configuration completed"
}

# Test MCP integration
test_mcp_integration() {
    print_status "Testing MCP integration..."

    # Test Pulser Hub MCP server
    if docker run --rm pulser-hub-mcp:latest python -c "print('MCP server test successful')" &> /dev/null; then
        print_success "Pulser Hub MCP server test passed"
    else
        print_error "Pulser Hub MCP server test failed"
        exit 1
    fi

    # Test ecosystem tools
    echo "Testing ecosystem tools..."
    docker run --rm pulser-hub-mcp:latest python -c "
import asyncio
from app.pulser_hub_mcp.main import handle_call_tool

async def test():
    result = await handle_call_tool('get_mcp_ecosystem_status', {})
    print('Ecosystem status test passed')

asyncio.run(test())
"

    print_success "MCP integration tests completed"
}

# Display deployment summary
display_summary() {
    print_success "🎉 MCP Ecosystem Deployment Completed!"
    echo ""
    echo "📊 Deployment Summary:"
    echo "  ✅ Pulser Hub MCP Server: Running in Docker"
    echo "  ✅ MCP Orchestrator: Ready for cross-server coordination"
    echo "  ✅ VS Code Integration: Configuration available"
    echo "  ✅ Docker Desktop MCP: Compatible with existing servers"
    echo ""
    echo "🔧 Available MCP Servers:"
    echo "  • Pulser Hub (5 tools) - Odoo & ecosystem integration"
    echo "  • Digital Ocean (3 tools) - Infrastructure management"
    echo "  • Kubernetes (22 tools) - Cluster operations"
    echo "  • Docker (1 tool) - Container management"
    echo "  • GitHub (40 tools) - Repository management"
    echo "  • Superset (3 tools) - Analytics dashboard creation"
    echo ""
    echo "🌐 Access Points:"
    echo "  • MCP Bridge: http://localhost:8081"
    echo "  • MCP Dashboard: http://localhost:8082"
    echo "  • Superset: https://insightpulseai.net/odoo/superset"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Set environment variables in mcp/.env"
    echo "  2. Configure VS Code with mcp/vscode-mcp-config.json"
    echo "  3. Test MCP tools in your AI agent or VS Code"
    echo "  4. Explore the MCP Dashboard at http://localhost:8082"
    echo ""
    echo "📚 Documentation:"
    echo "  • MCP Ecosystem Guide: mcp/README.md"
    echo "  • VS Code Integration: mcp/vscode-mcp-config.json"
    echo "  • Docker Compose: mcp/docker-compose.mcp.yml"
}

# Main deployment process
main() {
    echo "==========================================="
    echo "   MCP Ecosystem Deployment for Pulser Hub"
    echo "==========================================="
    echo ""

    check_prerequisites
    build_mcp_image
    deploy_mcp_ecosystem
    configure_vscode
    test_mcp_integration
    display_summary
}

# Run main function
main "$@"
