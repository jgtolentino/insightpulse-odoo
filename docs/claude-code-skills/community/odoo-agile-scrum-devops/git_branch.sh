#!/bin/bash
# OCA-Compliant Git Branch Creator
# Creates properly named feature branches following OCA conventions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Default values
ODOO_VERSION=""
BRANCH_TYPE=""
MODULE_NAME=""
ISSUE_NUMBER=""

# Help message
show_help() {
    cat << EOF
OCA-Compliant Git Branch Creator

Usage: $(basename "$0") [OPTIONS]

Creates properly named Git branches following OCA conventions.
Format: {version}-{type}-{module_name}[-{issue}]

Options:
    -v, --version       Odoo version (e.g., 18.0, 19.0)
    -t, --type         Branch type: feature, fix, refactor, docs
    -m, --module       Module name (e.g., finance_bir_compliance)
    -i, --issue        GitHub issue number (optional)
    -h, --help         Show this help message

Examples:
    $(basename "$0") -v 19.0 -t feature -m finance_bir_compliance
    $(basename "$0") -v 18.0 -t fix -m expense_ocr -i 123
    $(basename "$0") --version 19.0 --type refactor --module multi_agency

Supported Branch Types:
    feature   - New functionality
    fix       - Bug fixes
    refactor  - Code refactoring (no functional changes)
    docs      - Documentation updates
    
OCA Commit Message Tags (for reference):
    [ADD]     - New features or modules
    [FIX]     - Bug fixes
    [REF]     - Refactoring
    [REM]     - Removed features
    [MOV]     - Moved files
    [REL]     - Release commits
    [I18N]    - Translations
    [MERGE]   - Merge commits
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--version)
                ODOO_VERSION="$2"
                shift 2
                ;;
            -t|--type)
                BRANCH_TYPE="$2"
                shift 2
                ;;
            -m|--module)
                MODULE_NAME="$2"
                shift 2
                ;;
            -i|--issue)
                ISSUE_NUMBER="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use -h or --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Validate inputs
validate_inputs() {
    local errors=0
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not a git repository"
        errors=$((errors + 1))
    fi
    
    # Validate Odoo version
    if [[ -z "$ODOO_VERSION" ]]; then
        print_error "Odoo version is required (-v or --version)"
        errors=$((errors + 1))
    elif ! [[ "$ODOO_VERSION" =~ ^[0-9]+\.[0-9]$ ]]; then
        print_error "Invalid Odoo version format. Expected format: 18.0, 19.0, etc."
        errors=$((errors + 1))
    fi
    
    # Validate branch type
    if [[ -z "$BRANCH_TYPE" ]]; then
        print_error "Branch type is required (-t or --type)"
        errors=$((errors + 1))
    elif ! [[ "$BRANCH_TYPE" =~ ^(feature|fix|refactor|docs)$ ]]; then
        print_error "Invalid branch type. Must be: feature, fix, refactor, or docs"
        errors=$((errors + 1))
    fi
    
    # Validate module name
    if [[ -z "$MODULE_NAME" ]]; then
        print_error "Module name is required (-m or --module)"
        errors=$((errors + 1))
    elif ! [[ "$MODULE_NAME" =~ ^[a-z0-9_]+$ ]]; then
        print_error "Invalid module name. Use lowercase letters, numbers, and underscores only"
        errors=$((errors + 1))
    fi
    
    # Validate issue number (optional)
    if [[ -n "$ISSUE_NUMBER" ]] && ! [[ "$ISSUE_NUMBER" =~ ^[0-9]+$ ]]; then
        print_error "Invalid issue number. Must be numeric"
        errors=$((errors + 1))
    fi
    
    if [[ $errors -gt 0 ]]; then
        echo ""
        echo "Use -h or --help for usage information"
        return 1
    fi
    
    return 0
}

# Construct branch name
construct_branch_name() {
    local branch_name="${ODOO_VERSION}-${BRANCH_TYPE}-${MODULE_NAME}"
    
    if [[ -n "$ISSUE_NUMBER" ]]; then
        branch_name="${branch_name}-${ISSUE_NUMBER}"
    fi
    
    echo "$branch_name"
}

# Check if branch already exists
check_branch_exists() {
    local branch_name=$1
    
    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        return 0  # Branch exists
    else
        return 1  # Branch doesn't exist
    fi
}

# Create branch
create_branch() {
    local branch_name=$1
    
    print_info "Creating branch: $branch_name"
    
    # Make sure we're on the latest main/master
    local main_branch=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')
    print_info "Ensuring $main_branch is up to date..."
    
    git checkout "$main_branch"
    git pull origin "$main_branch"
    
    # Create and checkout new branch
    git checkout -b "$branch_name"
    
    print_success "Branch created: $branch_name"
    print_info "You are now on branch: $(git branch --show-current)"
    
    # Show helpful next steps
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Next steps:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Make your changes to the code"
    echo ""
    echo "2. Commit with OCA-compliant message:"
    
    case $BRANCH_TYPE in
        feature)
            echo "   git commit -m \"[ADD] $MODULE_NAME: Brief description\""
            ;;
        fix)
            echo "   git commit -m \"[FIX] $MODULE_NAME: Brief description\""
            ;;
        refactor)
            echo "   git commit -m \"[REF] $MODULE_NAME: Brief description\""
            ;;
        docs)
            echo "   git commit -m \"[DOC] $MODULE_NAME: Brief description\""
            ;;
    esac
    
    echo ""
    echo "3. Push branch to remote:"
    echo "   git push -u origin $branch_name"
    echo ""
    echo "4. Create Pull Request on GitHub"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main function
main() {
    # Parse arguments
    parse_args "$@"
    
    # Show help if no arguments
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi
    
    # Validate inputs
    if ! validate_inputs; then
        exit 1
    fi
    
    # Construct branch name
    local branch_name=$(construct_branch_name)
    
    # Check if branch exists
    if check_branch_exists "$branch_name"; then
        print_error "Branch '$branch_name' already exists"
        print_info "Checking out existing branch..."
        git checkout "$branch_name"
        exit 0
    fi
    
    # Create branch
    create_branch "$branch_name"
}

# Run main function
main "$@"
