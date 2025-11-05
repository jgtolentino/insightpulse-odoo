#!/bin/bash
#
# Manual Conflict Resolution Helper
#
# This script helps resolve merge conflicts by attempting multiple strategies:
# 1. AI-powered resolution using Claude
# 2. Automatic merge strategies (patience, ours, theirs)
# 3. Interactive resolution with editor support
#
# Usage:
#   ./scripts/resolve-conflicts.sh <branch-name>
#   ./scripts/resolve-conflicts.sh feature/my-feature
#
# Options:
#   --skip-ai          Skip AI resolution attempt
#   --auto-commit      Automatically commit if successful
#   --base-branch      Specify base branch (default: main)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
BASE_BRANCH="main"
SKIP_AI=false
AUTO_COMMIT=false
BRANCH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-ai)
            SKIP_AI=true
            shift
            ;;
        --auto-commit)
            AUTO_COMMIT=true
            shift
            ;;
        --base-branch)
            BASE_BRANCH="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 <branch-name> [options]"
            echo ""
            echo "Options:"
            echo "  --skip-ai          Skip AI resolution attempt"
            echo "  --auto-commit      Automatically commit if successful"
            echo "  --base-branch      Specify base branch (default: main)"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 feature/my-feature"
            echo "  $0 feature/my-feature --base-branch develop"
            echo "  $0 feature/my-feature --skip-ai --auto-commit"
            exit 0
            ;;
        *)
            if [ -z "$BRANCH" ]; then
                BRANCH="$1"
            else
                echo -e "${RED}❌ Error: Unknown argument '$1'${NC}"
                exit 1
            fi
            shift
            ;;
    esac
done

if [ -z "$BRANCH" ]; then
    echo -e "${RED}❌ Error: Branch name required${NC}"
    echo "Usage: $0 <branch-name>"
    exit 1
fi

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_conflicts() {
    # Return 0 if conflicts exist, 1 if no conflicts
    if git diff --name-only --diff-filter=U | grep -q .; then
        return 0
    else
        return 1
    fi
}

list_conflicts() {
    echo "Conflicted files:"
    git diff --name-only --diff-filter=U | while read -r file; do
        echo "  - $file"
    done
}

# ============================================================================
# Main Script
# ============================================================================

print_header "🔧 Resolving Conflicts for Branch: $BRANCH"

# Check if we're in a git repository
if [ ! -d .git ]; then
    print_error "Not in a git repository"
    exit 1
fi

# Checkout the branch
print_info "Checking out branch: $BRANCH"
if ! git checkout "$BRANCH" 2>/dev/null; then
    print_error "Failed to checkout branch: $BRANCH"
    print_info "Make sure the branch exists"
    exit 1
fi

print_success "On branch: $BRANCH"

# Fetch latest changes
print_info "Fetching latest changes from origin/$BASE_BRANCH..."
git fetch origin "$BASE_BRANCH"
print_success "Fetched latest changes"

# Check if there's already a merge in progress
if [ -f .git/MERGE_HEAD ]; then
    print_warning "Merge already in progress"
    print_info "Attempting to resolve existing conflicts..."
else
    # Attempt merge
    print_info "Merging origin/$BASE_BRANCH into $BRANCH..."

    if git merge "origin/$BASE_BRANCH" --no-commit --no-ff; then
        print_success "No conflicts! Merge successful."

        if [ "$AUTO_COMMIT" = true ]; then
            git commit -m "Merge branch '$BASE_BRANCH' into $BRANCH"
            print_success "Committed merge"

            echo ""
            print_info "Push changes with:"
            echo "  git push origin $BRANCH"
        else
            print_info "Review changes and commit manually:"
            echo "  git diff --cached"
            echo "  git commit"
        fi

        exit 0
    fi

    print_warning "Conflicts detected"
fi

# List conflicted files
echo ""
list_conflicts
echo ""

# Count conflicts
CONFLICT_COUNT=$(git diff --name-only --diff-filter=U | wc -l)
print_info "Found $CONFLICT_COUNT conflicted file(s)"

# ============================================================================
# Resolution Strategy 1: AI-Powered Resolution
# ============================================================================

if [ "$SKIP_AI" = false ]; then
    print_header "🤖 Strategy 1: AI-Powered Resolution"

    # Check if AI resolver script exists
    if [ ! -f .github/scripts/ai-conflict-resolver.py ]; then
        print_warning "AI resolver script not found"
        print_info "Skipping AI resolution"
    else
        # Check for ANTHROPIC_API_KEY
        if [ -z "$ANTHROPIC_API_KEY" ]; then
            print_warning "ANTHROPIC_API_KEY not set"
            print_info "Skipping AI resolution"
            print_info "Set ANTHROPIC_API_KEY to enable AI-powered resolution"
        else
            print_info "Attempting AI-powered resolution..."

            if python3 .github/scripts/ai-conflict-resolver.py \
                --base-ref "origin/$BASE_BRANCH" \
                --head-ref HEAD \
                --max-auto-resolve 20; then

                print_success "AI resolution successful!"

                # Check if conflicts still exist
                if ! check_conflicts; then
                    print_header "✅ All Conflicts Resolved!"

                    # Run tests
                    if [ -f Makefile ] && grep -q "^test:" Makefile; then
                        print_info "Running tests..."
                        if make test; then
                            print_success "Tests passed!"
                        else
                            print_error "Tests failed - please review changes"
                            exit 1
                        fi
                    fi

                    # Commit if auto-commit enabled
                    if [ "$AUTO_COMMIT" = true ]; then
                        git add -A
                        git commit -m "🤖 Auto-resolved merge conflicts

Merged: origin/$BASE_BRANCH into $BRANCH
Strategy: AI-powered resolution
Resolved: $CONFLICT_COUNT files
"
                        print_success "Changes committed"

                        echo ""
                        print_info "Push changes with:"
                        echo "  git push origin $BRANCH"
                    else
                        print_info "Review changes and commit manually:"
                        echo "  git diff"
                        echo "  git add -A"
                        echo "  git commit"
                    fi

                    exit 0
                fi
            else
                print_warning "AI resolution failed or incomplete"
            fi
        fi
    fi
fi

# ============================================================================
# Resolution Strategy 2: Manual Resolution with Editor
# ============================================================================

print_header "🔧 Strategy 2: Manual Resolution"

echo "Remaining conflicts:"
list_conflicts
echo ""

# Check if VS Code is available
if command -v code &> /dev/null; then
    print_info "Opening conflicted files in VS Code..."

    # Get list of conflicted files
    CONFLICTED_FILES=$(git diff --name-only --diff-filter=U | tr '\n' ' ')

    # Open in VS Code
    code --wait $CONFLICTED_FILES

    echo ""
    print_info "After resolving conflicts in VS Code:"
    echo "  1. Save all files"
    echo "  2. This script will continue automatically"
    echo ""

    # Wait for user to close editor
    read -p "Press Enter when you've resolved conflicts in VS Code..."

# Check if vim is available
elif command -v vim &> /dev/null; then
    print_info "Opening conflicts in vim..."
    print_info "Use :cq to abort, :wq to continue after resolving"

    git diff --name-only --diff-filter=U | while read -r file; do
        vim "$file"
    done

# Fallback to git mergetool
else
    print_info "Opening git mergetool..."
    git mergetool
fi

# ============================================================================
# Verification
# ============================================================================

print_header "🧪 Verification"

# Check if conflicts still exist
if check_conflicts; then
    print_error "Conflicts still exist!"
    echo ""
    list_conflicts
    echo ""
    print_info "Please resolve manually and run:"
    echo "  git add <resolved-files>"
    echo "  git commit"
    exit 1
fi

print_success "No conflicts remaining!"

# Validate resolved files
print_info "Validating resolved files..."

VALIDATION_FAILED=false

# YAML validation
for file in $(git diff --name-only HEAD | grep -E '\.(yml|yaml)$' || true); do
    if [ -f "$file" ]; then
        echo -n "  Validating YAML: $file ... "
        if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            VALIDATION_FAILED=true
        fi
    fi
done

# Python syntax check
for file in $(git diff --name-only HEAD | grep '\.py$' || true); do
    if [ -f "$file" ]; then
        echo -n "  Validating Python: $file ... "
        if python3 -m py_compile "$file" 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            VALIDATION_FAILED=true
        fi
    fi
done

# JSON validation
for file in $(git diff --name-only HEAD | grep '\.json$' || true); do
    if [ -f "$file" ]; then
        echo -n "  Validating JSON: $file ... "
        if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            VALIDATION_FAILED=true
        fi
    fi
done

if [ "$VALIDATION_FAILED" = true ]; then
    print_error "Validation failed for some files"
    print_info "Please fix syntax errors before committing"
    exit 1
fi

print_success "All validations passed!"

# ============================================================================
# Commit
# ============================================================================

print_header "📝 Commit Changes"

# Stage all resolved files
git add -A

# Show what will be committed
echo "Changes to be committed:"
git diff --cached --stat
echo ""

if [ "$AUTO_COMMIT" = true ]; then
    git commit -m "Merge branch '$BASE_BRANCH' into $BRANCH

Resolved conflicts in $CONFLICT_COUNT files manually.
"
    print_success "Changes committed!"

    echo ""
    print_info "Push changes with:"
    echo "  git push origin $BRANCH"
else
    print_info "Ready to commit. Run:"
    echo "  git commit -m 'your message'"
    echo ""
    print_info "Or commit now:"
    read -p "Commit now? (y/N) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git commit -m "Merge branch '$BASE_BRANCH' into $BRANCH

Resolved conflicts in $CONFLICT_COUNT files.
"
        print_success "Changes committed!"

        echo ""
        print_info "Push changes with:"
        echo "  git push origin $BRANCH"
    else
        print_info "Commit manually when ready:"
        echo "  git commit"
    fi
fi

print_header "✅ Conflict Resolution Complete!"

echo ""
echo "Summary:"
echo "  Branch: $BRANCH"
echo "  Base: $BASE_BRANCH"
echo "  Files resolved: $CONFLICT_COUNT"
echo ""
print_success "Done! 🎉"
