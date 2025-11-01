#!/bin/bash

# Build the MCP Docker image
echo "Building Pulser Hub MCP Docker image..."
docker build -t pulser-hub-mcp:latest .

echo "Build complete!"
echo ""
echo "To test the MCP server manually:"
echo "  docker run -it --rm pulser-hub-mcp:latest"
echo ""
echo "To use with Cursor, ensure the image is built and then restart Cursor."
echo "Cursor will automatically detect the MCP server from .cursor/mcp.json"
