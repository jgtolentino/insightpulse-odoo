#!/bin/bash
#
# Notion to Odoo Module Automation
# Uses Continue CLI with Notion MCP to generate Odoo modules from feature requests
#
# Usage: ./scripts/notion-to-odoo.sh [options]
#
# Options:
#   --batch         Process all ready features
#   --single ID     Process single Notion card by ID
#   --dry-run       Show what would be done without executing
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ADDONS_PATH="$PROJECT_ROOT/addons"
LOG_FILE="$PROJECT_ROOT/automation.log"

# Ensure Continue CLI is installed
if ! command -v cn &> /dev/null; then
    echo -e "${RED}❌ Continue CLI not found${NC}"
    echo "Install with: npm i -g @continuedev/cli"
    exit 1
fi

# Ensure .continue config exists
if [ ! -f "$HOME/.continue/config.json" ]; then
    echo -e "${YELLOW}⚠️  Continue CLI config not found${NC}"
    echo "Copy .continue/config.example.json to ~/.continue/config.json"
    echo "Then add your API keys"
    exit 1
fi

# Parse arguments
MODE="batch"
NOTION_ID=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --batch)
            MODE="batch"
            shift
            ;;
        --single)
            MODE="single"
            NOTION_ID="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log "${GREEN}🚀 Starting Notion → Odoo automation${NC}"
log "$(date)"
log "Mode: $MODE"
log "Target: $ADDONS_PATH"
echo ""

# Function to query Notion for ready features
query_ready_features() {
    log "${YELLOW}🔍 Querying Notion for ready features...${NC}"

    cn << 'EOF'
Query the Notion database for all feature requests with these criteria:
- Status: "Ready for Development"
- Sort by: Priority (High to Low)

For each card, output in JSON format:
{
  "id": "notion-card-id",
  "title": "Feature title",
  "description": "Full description",
  "priority": "high/medium/low",
  "module_type": "finance/ops/analytics"
}
EOF
}

# Function to generate single module
generate_module() {
    local notion_id=$1
    local feature_data=$2

    log "${YELLOW}📦 Generating module for: $feature_data${NC}"

    if [ "$DRY_RUN" = true ]; then
        log "${YELLOW}[DRY RUN] Would generate module${NC}"
        return 0
    fi

    # Use Continue CLI with odoo-developer prompt
    cn -p "odoo-developer" << EOF
Read the Notion card with ID '$notion_id' and generate a complete OCA-compliant Odoo 19 module.

Requirements:
1. Follow the module structure from odoo-developer.md prompt
2. Save to: $ADDONS_PATH/
3. Include:
   - Complete models with type hints
   - All views (form, tree, search)
   - Security rules (ir.model.access.csv)
   - Tests with 80% coverage
   - README.md with full documentation
   - __manifest__.py following OCA standards

4. Integration points:
   - Supabase for document storage (if needed)
   - PaddleOCR for OCR features (if needed)
   - Apache Superset for analytics (if needed)

5. After generation:
   - Validate Python syntax
   - Check OCA compliance
   - Run basic tests
   - Update Notion card status to "In Development"

Output the module path and validation results.
EOF

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log "${GREEN}✅ Module generated successfully${NC}"
        return 0
    else
        log "${RED}❌ Module generation failed${NC}"
        return 1
    fi
}

# Function to validate generated module
validate_module() {
    local module_path=$1

    log "${YELLOW}🔍 Validating module: $module_path${NC}"

    # Check required files exist
    local required_files=(
        "__init__.py"
        "__manifest__.py"
        "models/__init__.py"
        "security/ir.model.access.csv"
        "README.md"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$module_path/$file" ]; then
            log "${RED}❌ Missing required file: $file${NC}"
            return 1
        fi
    done

    # Validate Python syntax
    log "Checking Python syntax..."
    find "$module_path" -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | tee -a "$LOG_FILE"

    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        log "${RED}❌ Python syntax errors found${NC}"
        return 1
    fi

    log "${GREEN}✅ Module validation passed${NC}"
    return 0
}

# Function to update Notion status
update_notion_status() {
    local notion_id=$1
    local new_status=$2

    log "${YELLOW}📝 Updating Notion card $notion_id to: $new_status${NC}"

    if [ "$DRY_RUN" = true ]; then
        log "${YELLOW}[DRY RUN] Would update Notion card${NC}"
        return 0
    fi

    cn << EOF
Update the Notion card with ID '$notion_id':
- Set Status to: $new_status
- Add a comment: "Module generated automatically on $(date)"
EOF
}

# Main execution
main() {
    if [ "$MODE" = "batch" ]; then
        log "${GREEN}Running in batch mode${NC}"

        # Query Notion for all ready features
        features=$(query_ready_features)

        # Process each feature (in real implementation, parse JSON)
        log "${YELLOW}Note: Full JSON parsing requires jq. Install with: apt-get install jq${NC}"

    elif [ "$MODE" = "single" ]; then
        log "${GREEN}Processing single feature: $NOTION_ID${NC}"

        # Generate module
        if generate_module "$NOTION_ID" "Feature from Notion"; then
            # Find the generated module path (assume last created directory)
            module_path=$(find "$ADDONS_PATH" -maxdepth 1 -type d -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)

            # Validate
            if validate_module "$module_path"; then
                # Update Notion
                update_notion_status "$NOTION_ID" "In Development"

                log "${GREEN}✅ Successfully processed feature${NC}"
                log "Module path: $module_path"
            else
                log "${RED}❌ Validation failed${NC}"
                exit 1
            fi
        else
            log "${RED}❌ Generation failed${NC}"
            exit 1
        fi
    fi

    log ""
    log "${GREEN}🎉 Automation complete${NC}"
    log "$(date)"
}

# Run main function
main

# Summary
echo ""
echo "========================================="
echo "📊 Automation Summary"
echo "========================================="
echo "Log file: $LOG_FILE"
echo "Modules location: $ADDONS_PATH"
echo ""
echo "Next steps:"
echo "1. Review generated modules"
echo "2. Run tests: python -m pytest addons/*/tests/"
echo "3. Install in Odoo: odoo-bin -d test_db --init=module_name"
echo "4. Create PR: gh pr create"
echo ""
