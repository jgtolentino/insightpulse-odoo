#!/usr/bin/env bash
# sync-claude-configs.sh - Synchronize Claude interface configurations
# Purpose: Validate claude.md structure and sync with scattered configs
# Last Updated: 2025-11-08

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root (assume script is in scripts/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_MD="${PROJECT_ROOT}/claude.md"
DRIFT_REPORT="${PROJECT_ROOT}/docs/claude-config-drift.md"

# Configuration paths
MCP_CONFIG="$HOME/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
AGENT_DIR="$HOME/.claude/superclaude/agents"
SKILLS_DIR="$PROJECT_ROOT/docs/claude-code-skills"

# Counter for issues
ISSUES=0

echo "======================================"
echo "Claude Config Sync - InsightPulse Odoo"
echo "======================================"
echo

# Function to log errors
log_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
    ((ISSUES++))
}

# Function to log warnings
log_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
}

# Function to log success
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Step 1: Validate claude.md structure
echo "1. Validating /claude.md structure..."

if [[ ! -f "$CLAUDE_MD" ]]; then
    log_error "claude.md not found at $CLAUDE_MD"
    exit 1
fi

# Check for all required sections (0-23)
MISSING_SECTIONS=()
for i in {0..23}; do
    if ! grep -q "^## $i)" "$CLAUDE_MD"; then
        MISSING_SECTIONS+=("$i")
    fi
done

if [[ ${#MISSING_SECTIONS[@]} -gt 0 ]]; then
    log_error "Missing sections in claude.md: ${MISSING_SECTIONS[*]}"
else
    log_success "All 24 sections (0-23) present in claude.md"
fi

# Step 2: Extract and validate model version from section 22
echo
echo "2. Extracting Claude model version from section 22..."

# Extract model from section 22 (Model Configuration)
MODEL_VERSION=$(sed -n '/^## 22) Model Configuration/,/^## 23)/p' "$CLAUDE_MD" | \
    grep -oE 'claude-[a-z0-9-]+' | head -n 1)

if [[ -z "$MODEL_VERSION" ]]; then
    log_warning "Could not extract model version from section 22"
else
    log_success "Model version: $MODEL_VERSION"
    echo "   → Will update CI workflows to use: $MODEL_VERSION"
fi

# Step 3: Validate MCP servers (section 17)
echo
echo "3. Validating MCP servers..."

if [[ ! -f "$MCP_CONFIG" ]]; then
    log_warning "MCP config file not found at $MCP_CONFIG"
else
    # Extract configured MCP servers from claude.md section 17
    CLAUDE_MCP_SERVERS=$(sed -n '/^## 17) MCP Server Matrix/,/^## 18)/p' "$CLAUDE_MD" | \
        grep -oE '\*\*[a-z_-]+\*\*' | sed 's/\*\*//g' | sort | uniq)

    # Extract MCP servers from actual config
    ACTUAL_MCP_SERVERS=$(jq -r '.mcpServers | keys[]' "$MCP_CONFIG" 2>/dev/null | sort)

    # Compare
    MISSING_IN_CONFIG=$(comm -23 <(echo "$CLAUDE_MCP_SERVERS") <(echo "$ACTUAL_MCP_SERVERS"))
    EXTRA_IN_CONFIG=$(comm -13 <(echo "$CLAUDE_MCP_SERVERS") <(echo "$ACTUAL_MCP_SERVERS"))

    if [[ -n "$MISSING_IN_CONFIG" ]]; then
        log_warning "MCP servers in claude.md but NOT in config: $MISSING_IN_CONFIG"
    fi

    if [[ -n "$EXTRA_IN_CONFIG" ]]; then
        log_warning "MCP servers in config but NOT in claude.md: $EXTRA_IN_CONFIG"
    fi

    if [[ -z "$MISSING_IN_CONFIG" && -z "$EXTRA_IN_CONFIG" ]]; then
        log_success "MCP server configuration matches claude.md"
    fi
fi

# Step 4: Validate agent definitions (section 18)
echo
echo "4. Validating agent definitions..."

# Extract agent names from claude.md section 18
CLAUDE_AGENTS=$(sed -n '/^## 18) SuperClaude Agents/,/^## 19)/p' "$CLAUDE_MD" | \
    grep -oE '### [0-9]+\. [a-z_]+' | awk '{print $3}' | sort)

# Get actual agent files
if [[ -d "$AGENT_DIR/domain" ]]; then
    ACTUAL_AGENTS=$(find "$AGENT_DIR/domain" -name "*.agent.yaml" | \
        xargs -I {} basename {} .agent.yaml | sort)

    # Compare
    MISSING_AGENTS=$(comm -23 <(echo "$CLAUDE_AGENTS") <(echo "$ACTUAL_AGENTS"))
    EXTRA_AGENTS=$(comm -13 <(echo "$CLAUDE_AGENTS") <(echo "$ACTUAL_AGENTS"))

    if [[ -n "$MISSING_AGENTS" ]]; then
        log_warning "Agents in claude.md but missing files: $MISSING_AGENTS"
    fi

    if [[ -n "$EXTRA_AGENTS" ]]; then
        log_warning "Agent files exist but not documented in claude.md: $EXTRA_AGENTS"
    fi

    if [[ -z "$MISSING_AGENTS" && -z "$EXTRA_AGENTS" ]]; then
        log_success "Agent definitions match claude.md"
    fi
else
    log_warning "Agent directory not found: $AGENT_DIR/domain"
fi

# Step 5: Validate skills inventory (section 19)
echo
echo "5. Validating skills inventory..."

# Extract skill names from claude.md section 19
CLAUDE_SKILLS=$(sed -n '/^## 19) Skills Inventory/,/^## 20)/p' "$CLAUDE_MD" | \
    grep -oE '\*\*[a-z0-9-]+\*\*' | sed 's/\*\*//g' | sort | uniq)

# Get actual skill directories
if [[ -d "$SKILLS_DIR" ]]; then
    ACTUAL_SKILLS=$(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | \
        xargs -I {} basename {} | sort)

    # Compare
    MISSING_SKILLS=$(comm -23 <(echo "$CLAUDE_SKILLS") <(echo "$ACTUAL_SKILLS"))
    EXTRA_SKILLS=$(comm -13 <(echo "$CLAUDE_SKILLS") <(echo "$ACTUAL_SKILLS"))

    if [[ -n "$MISSING_SKILLS" ]]; then
        log_warning "Skills in claude.md but missing directories: $MISSING_SKILLS"
    fi

    if [[ -n "$EXTRA_SKILLS" ]]; then
        log_warning "Skill directories exist but not documented in claude.md: $EXTRA_SKILLS"
    fi

    if [[ -z "$MISSING_SKILLS" && -z "$EXTRA_SKILLS" ]]; then
        log_success "Skills inventory matches claude.md"
    fi
else
    log_warning "Skills directory not found: $SKILLS_DIR"
fi

# Step 6: Generate drift report
echo
echo "6. Generating drift report..."

mkdir -p "$(dirname "$DRIFT_REPORT")"

cat > "$DRIFT_REPORT" <<EOF
# Claude Configuration Drift Report

**Generated**: $(date '+%Y-%m-%d %H:%M:%S')
**Repository**: InsightPulse Odoo
**Canonical Source**: /claude.md

---

## Summary

- **Total Issues Found**: $ISSUES
- **Model Version**: ${MODEL_VERSION:-"NOT FOUND"}
- **Missing Sections**: ${#MISSING_SECTIONS[@]}

---

## Detailed Findings

### Section Structure
EOF

if [[ ${#MISSING_SECTIONS[@]} -gt 0 ]]; then
    echo "❌ Missing sections: ${MISSING_SECTIONS[*]}" >> "$DRIFT_REPORT"
else
    echo "✅ All 24 sections present (0-23)" >> "$DRIFT_REPORT"
fi

cat >> "$DRIFT_REPORT" <<EOF

### Model Configuration
- **Extracted Model**: ${MODEL_VERSION:-"NOT FOUND"}
- **Status**: ${MODEL_VERSION:+"✅ Available for CI sync"}${MODEL_VERSION:+"❌ Extraction failed"}

### MCP Servers
EOF

if [[ -n "$MISSING_IN_CONFIG" ]]; then
    echo "⚠️ Missing in config: $MISSING_IN_CONFIG" >> "$DRIFT_REPORT"
fi

if [[ -n "$EXTRA_IN_CONFIG" ]]; then
    echo "⚠️ Extra in config: $EXTRA_IN_CONFIG" >> "$DRIFT_REPORT"
fi

if [[ -z "$MISSING_IN_CONFIG" && -z "$EXTRA_IN_CONFIG" ]]; then
    echo "✅ Configuration matches claude.md" >> "$DRIFT_REPORT"
fi

cat >> "$DRIFT_REPORT" <<EOF

### Agent Definitions
EOF

if [[ -n "$MISSING_AGENTS" ]]; then
    echo "⚠️ Missing agent files: $MISSING_AGENTS" >> "$DRIFT_REPORT"
fi

if [[ -n "$EXTRA_AGENTS" ]]; then
    echo "⚠️ Undocumented agents: $EXTRA_AGENTS" >> "$DRIFT_REPORT"
fi

if [[ -z "$MISSING_AGENTS" && -z "$EXTRA_AGENTS" ]]; then
    echo "✅ Agent definitions match claude.md" >> "$DRIFT_REPORT"
fi

cat >> "$DRIFT_REPORT" <<EOF

### Skills Inventory
EOF

if [[ -n "$MISSING_SKILLS" ]]; then
    echo "⚠️ Missing skill directories: $MISSING_SKILLS" >> "$DRIFT_REPORT"
fi

if [[ -n "$EXTRA_SKILLS" ]]; then
    echo "⚠️ Undocumented skills: $EXTRA_SKILLS" >> "$DRIFT_REPORT"
fi

if [[ -z "$MISSING_SKILLS" && -z "$EXTRA_SKILLS" ]]; then
    echo "✅ Skills inventory matches claude.md" >> "$DRIFT_REPORT"
fi

cat >> "$DRIFT_REPORT" <<EOF

---

## Recommendations

EOF

if [[ $ISSUES -gt 0 ]]; then
    cat >> "$DRIFT_REPORT" <<EOF
1. **Fix Missing Sections**: Add missing sections to /claude.md
2. **Sync MCP Servers**: Update configuration or documentation
3. **Update Agent Docs**: Document all agent files in section 18
4. **Update Skills Inventory**: Document all skills in section 19
5. **Run Validation**: Execute \`scripts/validate-claude-config.py\` for detailed checks
EOF
else
    echo "✅ No drift detected. Configuration is synchronized." >> "$DRIFT_REPORT"
fi

log_success "Drift report generated: $DRIFT_REPORT"

# Step 7: Summary
echo
echo "======================================"
echo "Sync Summary"
echo "======================================"
echo "Total Issues: $ISSUES"
echo "Drift Report: $DRIFT_REPORT"
echo

if [[ $ISSUES -eq 0 ]]; then
    log_success "Configuration is synchronized!"
    exit 0
else
    log_warning "Configuration drift detected. Review $DRIFT_REPORT for details."
    exit 1
fi
