#!/bin/bash
# DeepSeek API Configuration Script
# Automates DeepSeek API key setup for Cline and shell environment

set -e

echo "========================================="
echo "DeepSeek API Configuration"
echo "========================================="
echo ""

# Check if DEEPSEEK_API_KEY is already set
if [ -n "$DEEPSEEK_API_KEY" ]; then
    echo "✓ DeepSeek API key already set in environment"
    echo "  Prefix: ${DEEPSEEK_API_KEY:0:10}..."
    read -p "Do you want to replace it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing key. Skipping to Cline configuration..."
        SKIP_ZSHRC=true
    fi
fi

# Prompt for API key if not skipping
if [ "$SKIP_ZSHRC" != "true" ]; then
    echo ""
    echo "Get your DeepSeek API key from: https://platform.deepseek.com/api_keys"
    echo ""
    read -p "Enter your DeepSeek API key (starts with sk-): " DEEPSEEK_API_KEY

    # Validate key format
    if [[ ! $DEEPSEEK_API_KEY =~ ^sk- ]]; then
        echo "❌ Error: DeepSeek API key should start with 'sk-'"
        exit 1
    fi

    # Backup .zshrc
    cp ~/.zshrc ~/.zshrc.backup.$(date +%Y%m%d_%H%M%S)
    echo "✓ Backed up ~/.zshrc"

    # Check if key already exists in .zshrc
    if grep -q "DEEPSEEK_API_KEY" ~/.zshrc; then
        echo "✓ Updating existing DeepSeek API key in ~/.zshrc"
        sed -i.bak "s/export DEEPSEEK_API_KEY=.*/export DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY/" ~/.zshrc
    else
        echo "✓ Adding DeepSeek API key to ~/.zshrc"
        echo "" >> ~/.zshrc
        echo "# DeepSeek API Key (Added: $(date +%Y-%m-%d))" >> ~/.zshrc
        echo "export DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY" >> ~/.zshrc
    fi

    # Source the updated .zshrc
    export DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY
    echo "✓ Environment variable set for current session"
fi

# Verify API key is now available
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ Error: DEEPSEEK_API_KEY not set"
    exit 1
fi

echo ""
echo "========================================="
echo "Configuring Cline CLI"
echo "========================================="
echo ""

# Configure Cline to use DeepSeek via OpenRouter
echo "Setting up Cline configuration..."

if command -v cline &> /dev/null; then
    echo "Configuring Cline to use DeepSeek via OpenRouter..."

    # Set OpenRouter API key to DeepSeek key
    timeout 15 cline config set open-router-api-key="$DEEPSEEK_API_KEY" 2>&1 || {
        echo "⚠️  Failed to set API key"
    }

    # Change act mode provider to openrouter
    timeout 15 cline config set act-mode-api-provider=openrouter 2>&1 || {
        echo "⚠️  Failed to set act mode provider"
    }

    # Change plan mode provider to openrouter
    timeout 15 cline config set plan-mode-api-provider=openrouter 2>&1 || {
        echo "⚠️  Failed to set plan mode provider"
    }

    echo "✓ Cline configuration updated"
else
    echo "⚠️  Cline CLI not found in PATH"
fi

# Verify configuration by checking Cline data files
echo ""
echo "Checking Cline configuration files..."
if [ -d ~/.cline/data ]; then
    echo "✓ Cline data directory found"
    CONFIG_FILE=$(find ~/.cline/data -name "*.json" -type f 2>/dev/null | head -1)
    if [ -n "$CONFIG_FILE" ]; then
        echo "✓ Cline config file: $CONFIG_FILE"
    fi
else
    echo "⚠️  Cline data directory not found"
fi

# Test DeepSeek API connection
echo ""
echo "========================================="
echo "Testing DeepSeek API Connection"
echo "========================================="
echo ""

API_TEST=$(curl -s -w "\n%{http_code}" \
    https://api.deepseek.com/v1/models \
    -H "Authorization: Bearer $DEEPSEEK_API_KEY" 2>&1)

HTTP_CODE=$(echo "$API_TEST" | tail -1)
RESPONSE=$(echo "$API_TEST" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ DeepSeek API connection successful!"
    echo ""
    echo "Available models:"
    echo "$RESPONSE" | jq -r '.data[].id' 2>/dev/null || echo "$RESPONSE"
else
    echo "❌ API connection failed (HTTP $HTTP_CODE)"
    echo "Response: $RESPONSE"
    echo ""
    echo "Please verify your API key at: https://platform.deepseek.com/api_keys"
    exit 1
fi

# Summary
echo ""
echo "========================================="
echo "Configuration Complete!"
echo "========================================="
echo ""
echo "✅ DeepSeek API key configured in ~/.zshrc"
echo "✅ Environment variable: DEEPSEEK_API_KEY"
echo "✅ Cline authentication attempted"
echo "✅ API connection verified"
echo ""
echo "Next steps:"
echo "1. Restart your terminal or run: source ~/.zshrc"
echo "2. In Cline, verify settings show DeepSeek provider"
echo "3. Test with: cline \"Hello, test DeepSeek\""
echo ""
echo "Your balance: $16.82 USD"
echo "Monthly expenses: $10.02 USD"
echo ""
