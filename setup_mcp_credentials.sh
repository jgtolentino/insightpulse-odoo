#!/bin/bash
# Interactive setup for MCP Server credentials

set -e

echo "======================================"
echo "MCP Server Credential Setup"
echo "======================================"
echo ""

# Check if private key file exists
echo "Step 1: Locate private key file"
echo "--------------------------------"
echo ""
echo "Where is your pulser-hub private key (.pem file)?"
echo "Common locations:"
echo "  1. ~/Downloads/pulser-hub.*.pem"
echo "  2. ~/.ssh/pulser-hub-private-key.pem"
echo "  3. Custom path"
echo ""

# Search for .pem files
PEM_FILES=$(find ~/Downloads ~/.ssh -name "*.pem" -type f 2>/dev/null)
if [ -n "$PEM_FILES" ]; then
    echo "Found these .pem files:"
    echo "$PEM_FILES"
    echo ""
fi

read -p "Enter path to private key file: " PRIVATE_KEY_PATH

if [ ! -f "$PRIVATE_KEY_PATH" ]; then
    echo "❌ File not found: $PRIVATE_KEY_PATH"
    echo ""
    echo "To download from GitHub:"
    echo "1. Go to: https://github.com/organizations/YOUR_ORG/settings/apps/pulser-hub"
    echo "2. Scroll to 'Private keys'"
    echo "3. Click 'Generate a private key'"
    echo "4. Save the .pem file and run this script again"
    exit 1
fi

echo "✅ Found private key file"
echo ""

# Read private key
PRIVATE_KEY_CONTENT=$(cat "$PRIVATE_KEY_PATH")

echo "Step 2: Find installation ID"
echo "-----------------------------"
echo ""
echo "Attempting to fetch installation ID..."

# Generate JWT
JWT=$(python3 -c "
import jwt
import time

private_key = '''$PRIVATE_KEY_CONTENT'''

payload = {
    'iat': int(time.time()),
    'exp': int(time.time()) + 600,
    'iss': 2191216
}

print(jwt.encode(payload, private_key, algorithm='RS256'))
" 2>&1)

if [ $? -ne 0 ]; then
    echo "❌ Error generating JWT token"
    echo "$JWT"
    exit 1
fi

# Fetch installations
INSTALLATIONS=$(curl -s -H "Authorization: Bearer $JWT" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/app/installations)

if [ "$(echo "$INSTALLATIONS" | jq -r 'type')" != "array" ]; then
    echo "❌ Error fetching installations:"
    echo "$INSTALLATIONS" | jq
    exit 1
fi

echo "Available installations:"
echo "$INSTALLATIONS" | jq -r '.[] | "  ID: \(.id) | \(.account.login) (\(.account.type))"'
echo ""

read -p "Enter installation ID to use: " INSTALLATION_ID

echo ""
echo "Step 3: Save credentials to ~/.zshrc"
echo "-------------------------------------"
echo ""

# Check if already exists
if grep -q "GITHUB_INSTALLATION_ID" ~/.zshrc 2>/dev/null; then
    echo "⚠️  Credentials already exist in ~/.zshrc"
    read -p "Overwrite? (y/n): " OVERWRITE
    if [ "$OVERWRITE" != "y" ]; then
        echo "Cancelled"
        exit 0
    fi
    # Remove old credentials
    sed -i '' '/# Pulser Hub MCP Server/,/export GITHUB_INSTALLATION_ID/d' ~/.zshrc
fi

# Add credentials
cat >> ~/.zshrc << EOF

# Pulser Hub MCP Server - GitHub App Credentials
export GITHUB_APP_ID="2191216"
export GITHUB_PRIVATE_KEY='$PRIVATE_KEY_CONTENT'
export GITHUB_INSTALLATION_ID="$INSTALLATION_ID"
EOF

echo "✅ Credentials saved to ~/.zshrc"
echo ""

echo "Step 4: Test configuration"
echo "--------------------------"
echo ""

# Reload and test
source ~/.zshrc

if [ -n "$GITHUB_APP_ID" ] && [ -n "$GITHUB_PRIVATE_KEY" ] && [ -n "$GITHUB_INSTALLATION_ID" ]; then
    echo "✅ All environment variables are set"
else
    echo "❌ Environment variables not set correctly"
    exit 1
fi

echo ""
echo "======================================"
echo "Setup Complete! 🎉"
echo "======================================"
echo ""
echo "App ID: $GITHUB_APP_ID"
echo "Installation ID: $INSTALLATION_ID"
echo "Private Key: $(echo "$PRIVATE_KEY_CONTENT" | head -1)"
echo ""
echo "Next steps:"
echo "1. Reload your shell: source ~/.zshrc"
echo "2. Start MCP server: cd services/mcp-server && python3 -m uvicorn server:app --host 127.0.0.1 --port 8000"
echo "3. Test: curl -s http://127.0.0.1:8000/health | jq"
echo "4. Open Docker Desktop → MCP Toolkit"
echo ""
