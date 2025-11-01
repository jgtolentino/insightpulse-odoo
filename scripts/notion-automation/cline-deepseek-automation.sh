#!/bin/bash
#
# Cline CLI + DeepSeek: Notion-to-Odoo Automation
#
# Cost: ~$0.001 per module (100x cheaper than Claude!)
#
# Requirements:
# - npm install -g @yaegaki/cline-cli
# - Python 3.9+ with notion-client, python-dotenv
# - DeepSeek API key
# - GitHub CLI (gh)

set -e

# Configuration
NOTION_DB_ID="${NOTION_DB_ID:-}"
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"
OUTPUT_DIR="${OUTPUT_DIR:-addons}"

# Colors
RED='\033[0.31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check Cline CLI
    if ! command -v cline &> /dev/null; then
        error "Cline CLI not found. Install: npm install -g @yaegaki/cline-cli"
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 not found"
    fi

    # Check GitHub CLI
    if ! command -v gh &> /dev/null; then
        warn "GitHub CLI not found. PR creation will be skipped"
    fi

    # Check environment variables
    if [ -z "$NOTION_DB_ID" ]; then
        error "NOTION_DB_ID environment variable required"
    fi

    if [ -z "$DEEPSEEK_API_KEY" ]; then
        error "DEEPSEEK_API_KEY environment variable required"
    fi

    log "Prerequisites OK"
}

# Configure Cline CLI with DeepSeek
configure_cline() {
    log "Configuring Cline CLI with DeepSeek..."

    # Cline CLI supports OpenAI-compatible APIs
    # DeepSeek is OpenAI-compatible at https://api.deepseek.com

    cline config set api_provider openai
    cline config set api_base_url https://api.deepseek.com
    cline config set api_key "$DEEPSEEK_API_KEY"
    cline config set model deepseek-chat

    log "Cline CLI configured with DeepSeek"
}

# Fetch Notion specs
fetch_specs() {
    log "Fetching Notion specifications..."

    python3 scripts/notion-automation/fetch_notion_specs.py \
        --database-id "$NOTION_DB_ID" \
        --status "Ready for Dev" \
        --output /tmp/notion-specs.json

    SPEC_COUNT=$(jq 'length' /tmp/notion-specs.json)
    log "Found $SPEC_COUNT specifications"
}

# Generate module using Cline CLI
generate_module_with_cline() {
    local spec_file=$1
    local spec=$(cat "$spec_file")

    log "Generating module with Cline CLI..."

    # Extract spec details
    local title=$(echo "$spec" | jq -r '.title')
    local content=$(echo "$spec" | jq -r '.content')
    local technical_specs=$(echo "$spec" | jq -r '.technical_specs // ""')

    # Create Cline CLI prompt
    local prompt="You are an expert Odoo 19.0 module developer. Generate a complete, OCA-compliant Odoo module:

**Module**: $title

**Description**:
$content

**Technical Specifications**:
$technical_specs

**Requirements**:
1. Follow OCA coding guidelines
2. Include complete __manifest__.py
3. Implement all models with proper ORM
4. Create XML views (list, form, search)
5. Define security (ir.model.access.csv, RLS rules)
6. Add pytest tests
7. Include README.rst
8. Philippine BIR compliance (Forms 2550M, 2550Q, 2551M, 2307)
9. Multi-agency patterns (RIM, CKVC, BOM, JPAL)
10. NO TODO comments or placeholders

Generate in $OUTPUT_DIR/ directory. Use proper Odoo 19.0 structure."

    # Run Cline CLI in autonomous mode with DeepSeek
    echo "$prompt" | cline -y --auto-approve-mcp \
        --workspace "$PWD" \
        --custom-instructions "Use Odoo 19.0 OCA guidelines"

    log "Module generation complete"
}

# Create GitHub PR
create_pr() {
    local module_name=$1

    if ! command -v gh &> /dev/null; then
        warn "GitHub CLI not found. Skipping PR creation"
        return
    fi

    log "Creating GitHub PR for $module_name..."

    # Stage changes
    git add "$OUTPUT_DIR/$module_name"

    # Create commit
    git commit -m "feat: auto-generated Odoo module $module_name

Generated with Cline CLI + DeepSeek API

Module: $module_name
Cost: ~\$0.001
Generator: Cline CLI (@yaegaki/cline-cli)
Model: DeepSeek Chat
"

    # Create PR
    gh pr create \
        --title "🤖 [Auto-Generated] Odoo Module: $module_name" \
        --body "## Automated Module Generation

**Module Name**: \`$module_name\`
**Generator**: Cline CLI + DeepSeek API
**Model**: deepseek-chat
**Cost**: ~\$0.001 (100x cheaper than Claude!)

### Features
- OCA-compliant Odoo 19.0 module
- Complete implementation (no TODOs)
- BIR compliance (Forms 2550M, 2550Q, 2551M, 2307)
- Multi-agency patterns (RIM, CKVC, BOM, JPAL)
- Comprehensive tests and documentation

### Review Checklist
- [ ] Code follows OCA guidelines
- [ ] All models have proper security
- [ ] Tests pass
- [ ] Documentation complete

---
🤖 Generated with Cline CLI + DeepSeek
" \
        --label "auto-generated,odoo-module,needs-review"

    PR_URL=$(gh pr list --limit 1 --json url --jq '.[0].url')
    log "PR created: $PR_URL"

    echo "$PR_URL"
}

# Update Notion status
update_notion() {
    local page_id=$1
    local pr_url=$2
    local module_name=$3

    log "Updating Notion page $page_id..."

    python3 scripts/notion-automation/update_notion_status.py \
        --page-id "$page_id" \
        --status "In Development" \
        --pr-url "$pr_url" \
        --module-name "$module_name"

    log "Notion page updated"
}

# Main workflow
main() {
    log "Starting Cline CLI + DeepSeek automation..."

    # Check prerequisites
    check_prerequisites

    # Configure Cline
    configure_cline

    # Fetch Notion specs
    fetch_specs

    # Process each spec
    jq -c '.[]' /tmp/notion-specs.json | while read -r spec; do
        # Save spec to temp file
        echo "$spec" > /tmp/current-spec.json

        # Extract details
        PAGE_ID=$(echo "$spec" | jq -r '.page_id')
        TITLE=$(echo "$spec" | jq -r '.title')

        log "Processing: $TITLE (Page: $PAGE_ID)"

        # Generate module with Cline CLI
        generate_module_with_cline /tmp/current-spec.json

        # Derive module name
        MODULE_NAME=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | sed 's/[^a-z0-9_]//g')

        # Create PR
        PR_URL=$(create_pr "$MODULE_NAME")

        # Update Notion
        update_notion "$PAGE_ID" "$PR_URL" "$MODULE_NAME"

        log "Completed: $TITLE"
    done

    log "All modules generated successfully!"
}

# Run main workflow
main "$@"
