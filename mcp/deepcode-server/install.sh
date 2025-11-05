#!/bin/bash
# DeepCode MCP Server Installation Script
# Interface-agnostic: Works with any Claude interface

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   DeepCode MCP Server Installation           ║${NC}"
echo -e "${BLUE}║   Paper2Code + Text2Web + Text2Backend       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Step 1: Check Python version
echo -e "${YELLOW}[1/6]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python 3.11 or higher is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Step 2: Install Python dependencies
echo -e "\n${YELLOW}[2/6]${NC} Installing Python dependencies..."
pip3 install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 3: Setup configuration
echo -e "\n${YELLOW}[3/6]${NC} Setting up configuration..."

if [ ! -f "config/deepcode.config.yaml" ]; then
    echo "Creating config/deepcode.config.yaml..."
    cp config/deepcode.config.yaml.example config/deepcode.config.yaml
    echo -e "${GREEN}✓ Created config/deepcode.config.yaml${NC}"
else
    echo -e "${BLUE}ℹ config/deepcode.config.yaml already exists${NC}"
fi

if [ ! -f "config/deepcode.secrets.yaml" ]; then
    echo "Creating config/deepcode.secrets.yaml..."
    cp config/deepcode.secrets.yaml.example config/deepcode.secrets.yaml
    echo -e "${YELLOW}⚠ Please update config/deepcode.secrets.yaml with your API keys${NC}"
else
    echo -e "${BLUE}ℹ config/deepcode.secrets.yaml already exists${NC}"
fi

# Step 4: Create directories
echo -e "\n${YELLOW}[4/6]${NC} Creating directories..."
mkdir -p workflows tests logs
echo -e "${GREEN}✓ Directories created${NC}"

# Step 5: Detect Claude interface
echo -e "\n${YELLOW}[5/6]${NC} Detecting Claude interface..."

CLAUDE_DETECTED=""

# Check for Claude Desktop
if [ -d "$HOME/Library/Application Support/Claude" ]; then
    CLAUDE_DETECTED="desktop"
    echo -e "${GREEN}✓ Claude Desktop detected${NC}"

    # Ask if user wants to update config
    read -p "Update Claude Desktop config? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

        if [ -f "$CLAUDE_CONFIG" ]; then
            echo "Backing up existing config..."
            cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
        fi

        # Merge with existing config
        echo "Updating Claude Desktop config..."
        python3 -c "
import json
import os
from pathlib import Path

config_path = Path('$CLAUDE_CONFIG')
deepcode_config = json.load(open('claude_desktop_config.json'))

if config_path.exists():
    existing = json.load(open(config_path))
    if 'mcpServers' not in existing:
        existing['mcpServers'] = {}
    existing['mcpServers']['deepcode'] = deepcode_config['mcpServers']['deepcode']
    json.dump(existing, open(config_path, 'w'), indent=2)
else:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(deepcode_config, open(config_path, 'w'), indent=2)
print('✓ Config updated')
"

        echo -e "${GREEN}✓ Claude Desktop config updated${NC}"
        echo -e "${YELLOW}⚠ Please restart Claude Desktop${NC}"
    fi
fi

# Check for Claude Code
if [ -d "$HOME/.config/claude-code" ] || command -v claude-code &> /dev/null; then
    CLAUDE_DETECTED="code"
    echo -e "${GREEN}✓ Claude Code detected${NC}"
    echo -e "${BLUE}ℹ DeepCode MCP server is ready for Claude Code${NC}"
fi

if [ -z "$CLAUDE_DETECTED" ]; then
    echo -e "${YELLOW}⚠ No Claude interface detected${NC}"
    echo -e "${BLUE}ℹ You can still use this with any MCP-compatible client${NC}"
fi

# Step 6: Test installation
echo -e "\n${YELLOW}[6/6]${NC} Testing installation..."
python3 -c "
try:
    from src.server import DeepCodeMCPServer
    print('✓ Server module loads correctly')
except Exception as e:
    print(f'✗ Error: {e}')
    exit(1)
" && echo -e "${GREEN}✓ Installation test passed${NC}" || echo -e "${RED}✗ Installation test failed${NC}"

# Summary
echo -e "\n${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Installation Complete!                ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Update API keys in: ${YELLOW}config/deepcode.secrets.yaml${NC}"
echo -e "2. Test the server: ${YELLOW}python3 -m src.server${NC}"

if [ "$CLAUDE_DETECTED" = "desktop" ]; then
    echo -e "3. Restart Claude Desktop"
    echo -e "4. DeepCode tools will be available in Claude"
fi

echo -e "\n${BLUE}Usage examples:${NC}"
echo -e "  - ${GREEN}'Generate BIR Form 1601-C algorithm'${NC}"
echo -e "  - ${GREEN}'Create a React dashboard with Tailwind'${NC}"
echo -e "  - ${GREEN}'Build a FastAPI backend with Supabase'${NC}"
echo -e "  - ${GREEN}'Optimize OCR algorithm for RTX 4090'${NC}"

echo -e "\n${BLUE}Documentation:${NC} ${YELLOW}README.md${NC}"
echo
