#!/bin/bash
###############################################################################
# deployment-checklist.sh - Interactive deployment checklist tracker
#
# Usage:
#   ./scripts/deployment-checklist.sh [--env prod|staging|dev]
#
# What this script does:
#   1. Guides through deployment phases
#   2. Tracks completion status
#   3. Validates each step
#   4. Provides next actions
###############################################################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
ENV="${1:-prod}"
CHECKLIST_FILE=".deployment-checklist-${ENV}.txt"

# Checklist items (phase:item:description:validation_command)
declare -a CHECKLIST_ITEMS=(
    # Phase 1: Supabase Setup (15 minutes)
    "1:supabase_table:Create health_check table:psql \$POSTGRES_URL -c 'SELECT COUNT(*) FROM public.health_check;'"
    "1:supabase_views:Verify helper views exist:psql \$POSTGRES_URL -c 'SELECT * FROM public.health_check_summary;'"
    "1:knowledge_embeddings:Create knowledge_embeddings table:psql \$POSTGRES_URL -c 'SELECT COUNT(*) FROM public.knowledge_embeddings;'"

    # Phase 2: Server Deployment (30 minutes)
    "2:server_directories:Create server directories:ssh root@erp.insightpulseai.net 'test -d /opt/odoo-ce/scripts'"
    "2:copy_scripts:Copy scripts to server:ssh root@erp.insightpulseai.net 'test -f /opt/odoo-ce/scripts/check_project_tasks.py'"
    "2:script_permissions:Set script permissions:ssh root@erp.insightpulseai.net 'test -x /opt/odoo-ce/scripts/check_project_tasks.py'"
    "2:test_project_tasks:Test check_project_tasks.py:ssh root@erp.insightpulseai.net 'cd /opt/odoo-ce && python3 scripts/check_project_tasks.py'"
    "2:test_finance_stack:Test verify_finance_stack.sh:ssh root@erp.insightpulseai.net 'cd /opt/odoo-ce/notion-n8n-monthly-close && ./scripts/verify_finance_stack.sh --env ${ENV}'"

    # Phase 3: n8n Configuration (45 minutes)
    "3:n8n_odoo_creds:Create Odoo credentials in n8n:curl -s -H 'X-N8N-API-KEY: \$N8N_API_KEY' https://ipa.insightpulseai.net/api/v1/credentials"
    "3:n8n_openai_creds:Create OpenAI credentials:curl -s -H 'X-N8N-API-KEY: \$N8N_API_KEY' https://ipa.insightpulseai.net/api/v1/credentials"
    "3:n8n_supabase_creds:Create Supabase credentials:curl -s -H 'X-N8N-API-KEY: \$N8N_API_KEY' https://ipa.insightpulseai.net/api/v1/credentials"
    "3:import_w150:Import W150 workflow:curl -s -H 'X-N8N-API-KEY: \$N8N_API_KEY' https://ipa.insightpulseai.net/api/v1/workflows | grep -q W150"
    "3:import_expense_ocr:Import ODOO_EXPENSE_OCR workflow:curl -s -H 'X-N8N-API-KEY: \$N8N_API_KEY' https://ipa.insightpulseai.net/api/v1/workflows | grep -q EXPENSE_OCR"
    "3:import_bir_prep:Import ODOO_BIR_PREP workflow:curl -s -H 'X-N8N-API-KEY: \$N8N_API_KEY' https://ipa.insightpulseai.net/api/v1/workflows | grep -q BIR_PREP"
    "3:import_knowledge:Import ODOO_KNOWLEDGE_GOV workflow:curl -s -H 'X-N8N-API-KEY: \$N8N_API_KEY' https://ipa.insightpulseai.net/api/v1/workflows | grep -q KNOWLEDGE_GOV"
    "3:test_w150:Test W150 workflow:echo 'Manual test required'"

    # Phase 4: GitHub Actions Setup (20 minutes)
    "4:gh_secrets:Add GitHub secrets:gh secret list | grep -q SUPABASE_SERVICE_ROLE_KEY"
    "4:enable_workflow:Enable health-check.yml workflow:echo 'Manual check required'"
    "4:test_workflow:Run workflow manually:gh workflow run health-check.yml"
    "4:verify_artifacts:Verify artifacts uploaded:echo 'Check GitHub Actions tab'"

    # Phase 5: Odoo Integration (30 minutes)
    "5:expense_webhook:Create expense webhook server action:echo 'Manual Odoo configuration'"
    "5:knowledge_webhook:Create knowledge webhook server action:echo 'Manual Odoo configuration'"
    "5:test_expense_webhook:Test expense webhook:echo 'Create test expense in Odoo'"

    # Phase 6: Monitoring Setup (15 minutes)
    "6:mattermost_channels:Configure Mattermost channels:echo 'Verify #finance-alerts exists'"
    "6:supabase_dashboard:Create Supabase saved queries:echo 'Manual dashboard setup'"
    "6:bookmark_links:Bookmark monitoring links:echo 'Save important URLs'"
)

# Function to print colored messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_pending() {
    echo -e "${CYAN}[ ]${NC} $1"
}

# Function to load checklist status
load_checklist() {
    if [ -f "$CHECKLIST_FILE" ]; then
        source "$CHECKLIST_FILE"
    fi
}

# Function to save checklist status
save_checklist() {
    local phase=$1
    local item=$2
    echo "completed_${phase}_${item}=true" >> "$CHECKLIST_FILE"
}

# Function to check if item is completed
is_completed() {
    local phase=$1
    local item=$2
    local var_name="completed_${phase}_${item}"
    [ "${!var_name:-false}" = "true" ]
}

# Function to validate item
validate_item() {
    local validation_cmd=$1

    if [ "$validation_cmd" = "echo 'Manual test required'" ] || \
       [ "$validation_cmd" = "echo 'Manual check required'" ] || \
       [ "$validation_cmd" = "echo 'Manual Odoo configuration'" ] || \
       [ "$validation_cmd" = "echo 'Manual dashboard setup'" ] || \
       [ "$validation_cmd" = "echo 'Save important URLs'" ] || \
       [ "$validation_cmd" = "echo 'Verify #finance-alerts exists'" ] || \
       [ "$validation_cmd" = "echo 'Create test expense in Odoo'" ] || \
       [ "$validation_cmd" = "echo 'Check GitHub Actions tab'" ]; then
        return 2  # Manual validation required
    fi

    if eval "$validation_cmd" &>/dev/null; then
        return 0  # Validation passed
    else
        return 1  # Validation failed
    fi
}

# Function to display phase
display_phase() {
    local phase=$1
    local phase_name=$2
    local estimated_time=$3

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}Phase $phase: $phase_name${NC} (Est. $estimated_time)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to display summary
display_summary() {
    local total=0
    local completed=0
    local pending=0
    local manual=0

    for item in "${CHECKLIST_ITEMS[@]}"; do
        IFS=':' read -r phase item_name description validation_cmd <<< "$item"
        ((total++))

        if is_completed "$phase" "$item_name"; then
            ((completed++))
        else
            validate_item "$validation_cmd"
            local result=$?
            if [ $result -eq 2 ]; then
                ((manual++))
            else
                ((pending++))
            fi
        fi
    done

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Deployment Progress Summary ($ENV)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${GREEN}Completed:${NC} $completed / $total"
    echo -e "${CYAN}Pending:${NC} $pending"
    echo -e "${YELLOW}Manual:${NC} $manual"
    echo ""

    local percentage=$((completed * 100 / total))
    echo -e "Progress: ${BLUE}[$percentage%]${NC}"

    # Progress bar
    local bar_length=50
    local filled=$((percentage * bar_length / 100))
    local empty=$((bar_length - filled))
    printf "${GREEN}"
    printf '█%.0s' $(seq 1 $filled)
    printf "${NC}"
    printf '░%.0s' $(seq 1 $empty)
    echo ""
    echo ""
}

# Function to display checklist
display_checklist() {
    load_checklist

    local current_phase=""

    for item in "${CHECKLIST_ITEMS[@]}"; do
        IFS=':' read -r phase item_name description validation_cmd <<< "$item"

        # Display phase header
        if [ "$phase" != "$current_phase" ]; then
            case $phase in
                1) display_phase "$phase" "Supabase Setup" "15 minutes" ;;
                2) display_phase "$phase" "Server Deployment" "30 minutes" ;;
                3) display_phase "$phase" "n8n Configuration" "45 minutes" ;;
                4) display_phase "$phase" "GitHub Actions Setup" "20 minutes" ;;
                5) display_phase "$phase" "Odoo Integration" "30 minutes" ;;
                6) display_phase "$phase" "Monitoring Setup" "15 minutes" ;;
            esac
            current_phase=$phase
        fi

        # Check completion status
        if is_completed "$phase" "$item_name"; then
            log_success "$description"
        else
            # Validate item
            validate_item "$validation_cmd"
            local result=$?

            if [ $result -eq 0 ]; then
                log_success "$description (auto-validated)"
                save_checklist "$phase" "$item_name"
            elif [ $result -eq 2 ]; then
                log_warning "$description (manual validation required)"
            else
                log_pending "$description"
            fi
        fi
    done

    display_summary
}

# Function to mark item as complete
mark_complete() {
    local phase=$1
    local item=$2

    save_checklist "$phase" "$item"
    log_success "Marked as complete: Phase $phase - $item"
}

# Function to reset checklist
reset_checklist() {
    if [ -f "$CHECKLIST_FILE" ]; then
        rm "$CHECKLIST_FILE"
        log_info "Checklist reset for $ENV environment"
    else
        log_warning "No checklist file found"
    fi
}

# Function to display help
display_help() {
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --env ENV          Environment (prod|staging|dev) [default: prod]"
    echo "  --mark PHASE ITEM  Mark item as complete"
    echo "  --reset            Reset checklist"
    echo "  --help             Display this help"
    echo ""
    echo "Examples:"
    echo "  $0 --env prod                     # View prod checklist"
    echo "  $0 --mark 1 supabase_table       # Mark Supabase table as complete"
    echo "  $0 --reset                       # Reset checklist"
    echo ""
}

# Main execution
main() {
    local action="display"
    local mark_phase=""
    local mark_item=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env)
                ENV="$2"
                CHECKLIST_FILE=".deployment-checklist-${ENV}.txt"
                shift 2
                ;;
            --mark)
                action="mark"
                mark_phase="$2"
                mark_item="$3"
                shift 3
                ;;
            --reset)
                action="reset"
                shift
                ;;
            --help)
                display_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                display_help
                exit 1
                ;;
        esac
    done

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Finance Stack Health Monitor - Deployment Checklist"
    echo "  Environment: $ENV"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    case $action in
        display)
            display_checklist
            ;;
        mark)
            mark_complete "$mark_phase" "$mark_item"
            ;;
        reset)
            reset_checklist
            ;;
    esac

    echo ""
}

# Run main function
main "$@"
