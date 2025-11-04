#!/bin/bash
# Test MCP Server Setup

set -e

echo "======================================"
echo "MCP Server Setup Test"
echo "======================================"
echo ""

# 1. Check MCP config exists
echo "✅ Checking MCP config file..."
if [ -f ~/.mcp/config.json ]; then
    echo "   Config file exists at ~/.mcp/config.json"
    cat ~/.mcp/config.json | python3 -m json.tool > /dev/null && echo "   Config is valid JSON"
else
    echo "❌ Config file not found"
    exit 1
fi
echo ""

# 2. Check server.py exists
echo "✅ Checking MCP server file..."
if [ -f services/mcp-server/server.py ]; then
    echo "   Server file exists"
else
    echo "❌ Server file not found"
    exit 1
fi
echo ""

# 3. Check Python dependencies
echo "✅ Checking Python dependencies..."
python3 -c "import fastapi; print('   fastapi:', fastapi.__version__)" 2>/dev/null || echo "   ⚠️  fastapi not installed"
python3 -c "import jwt; print('   PyJWT:', jwt.__version__)" 2>/dev/null || echo "   ⚠️  PyJWT not installed"
python3 -c "import httpx; print('   httpx:', httpx.__version__)" 2>/dev/null || echo "   ⚠️  httpx not installed"
python3 -c "import uvicorn; print('   uvicorn:', uvicorn.__version__)" 2>/dev/null || echo "   ⚠️  uvicorn not installed"
echo ""

# 4. Test server syntax
echo "✅ Checking server.py syntax..."
python3 -m py_compile services/mcp-server/server.py && echo "   Python syntax is valid"
echo ""

# 5. Check environment variables
echo "✅ Checking environment variables..."
[ -n "$GITHUB_APP_ID" ] && echo "   GITHUB_APP_ID is set" || echo "   ⚠️  GITHUB_APP_ID not set"
[ -n "$GITHUB_PRIVATE_KEY" ] && echo "   GITHUB_PRIVATE_KEY is set" || echo "   ⚠️  GITHUB_PRIVATE_KEY not set"
[ -n "$GITHUB_INSTALLATION_ID" ] && echo "   GITHUB_INSTALLATION_ID is set" || echo "   ⚠️  GITHUB_INSTALLATION_ID not set"
echo ""

echo "======================================"
echo "Setup test complete!"
echo ""
echo "To start the MCP server:"
echo "  cd services/mcp-server"
echo "  python3 -m uvicorn server:app --host 127.0.0.1 --port 8000"
echo ""
echo "To test endpoints:"
echo "  curl -s http://127.0.0.1:8000/health | jq"
echo "  curl -s http://127.0.0.1:8000/mcp/catalog | jq"
echo "======================================"
