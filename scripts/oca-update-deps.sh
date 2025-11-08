#!/usr/bin/env bash
# OCA Dependency Management Script
# Purpose: Manage OCA module dependencies, updates, and compatibility checks
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OCA_TOOLS_DIR="$REPO_ROOT/.oca-tools"
ADDONS_DIR="$REPO_ROOT/apps/odoo/addons"
DEPS_FILE="$REPO_ROOT/oca-dependencies.txt"
ODOO_VERSION="${ODOO_VERSION:-17.0}"

ACTION="${1:-check}"

usage() {
  cat <<EOF
Usage: $0 <action> [options]

Actions:
  check       Check for missing dependencies
  install     Install missing OCA dependencies
  update      Update existing OCA dependencies
  list        List all OCA dependencies
  validate    Validate dependency versions
  analyze     Analyze dependency tree

Options:
  --version   Odoo version (default: $ODOO_VERSION)
  --dry-run   Show what would be done without making changes

Examples:
  $0 check                    # Check dependencies
  $0 install --version 17.0   # Install OCA deps for Odoo 17.0
  $0 update --dry-run         # Show what would be updated
  $0 analyze                  # Show dependency tree
EOF
  exit 1
}

if [ ! -d "$OCA_TOOLS_DIR/repo-maintainer" ]; then
  echo "❌ OCA tools not installed. Run: ./scripts/install-oca-tools.sh"
  exit 1
fi

# Initialize oca-dependencies.txt if it doesn't exist
if [ ! -f "$DEPS_FILE" ]; then
  cat > "$DEPS_FILE" <<'DEPS'
# OCA Dependencies for InsightPulse AI
# Format: <repo> [path] [branch]
#
# Example:
# server-tools
# account-financial-tools
# account-reconcile
# mis-builder
# web widgets/web_tree_many2one_clickable 17.0

# Core OCA dependencies
server-tools
web
reporting-engine
account-financial-reporting
account-financial-tools
server-ux
queue
rest-framework

# Finance & Accounting
account-reconcile
account-invoicing
account-payment
account-closing

# BIR & Philippines specific (if available)
# l10n-philippines

# Project Management
project
project-reporting

# Multi-company & Legal
multi-company

# Connector framework
connector
DEPS
  echo "📝 Created $DEPS_FILE"
fi

check_dependencies() {
  echo "🔍 Checking OCA Dependencies"
  echo "   Version: $ODOO_VERSION"
  echo ""

  local missing=()
  local found=()

  while IFS= read -r line; do
    # Skip comments and empty lines
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$line" ]] && continue

    # Parse dependency line
    read -ra parts <<< "$line"
    repo_name="${parts[0]}"
    repo_path="${parts[1]:-}"
    repo_branch="${parts[2]:-$ODOO_VERSION}"

    # Check if repo is cloned
    local repo_dir="$ADDONS_DIR/../oca-${repo_name}"
    if [ -d "$repo_dir" ]; then
      found+=("$repo_name")
      echo "   ✅ $repo_name (branch: $repo_branch)"
    else
      missing+=("$repo_name")
      echo "   ❌ $repo_name (missing)"
    fi
  done < "$DEPS_FILE"

  echo ""
  echo "📊 Summary:"
  echo "   Found:   ${#found[@]}"
  echo "   Missing: ${#missing[@]}"

  if [ ${#missing[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  Missing dependencies:"
    printf '   - %s\n' "${missing[@]}"
    echo ""
    echo "💡 Run: $0 install"
    return 1
  fi

  return 0
}

install_dependencies() {
  echo "📦 Installing OCA Dependencies"
  echo "   Version: $ODOO_VERSION"
  echo ""

  mkdir -p "$ADDONS_DIR/../oca-repos"
  cd "$ADDONS_DIR/../oca-repos"

  local installed=0
  local skipped=0

  while IFS= read -r line; do
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$line" ]] && continue

    read -ra parts <<< "$line"
    repo_name="${parts[0]}"
    repo_path="${parts[1]:-}"
    repo_branch="${parts[2]:-$ODOO_VERSION}"

    repo_dir="oca-${repo_name}"

    if [ -d "$repo_dir" ]; then
      echo "   ⏭️  $repo_name (already exists)"
      ((skipped++))
      continue
    fi

    echo "   📥 Cloning $repo_name (branch: $repo_branch)..."
    if git clone --depth 1 --branch "$repo_branch" \
        "https://github.com/OCA/$repo_name.git" "$repo_dir" 2>/dev/null; then
      echo "   ✅ Installed $repo_name"
      ((installed++))

      # Symlink modules to addons directory if specific path requested
      if [ -n "$repo_path" ]; then
        local source="$repo_dir/$repo_path"
        local target="$ADDONS_DIR/$(basename "$repo_path")"
        if [ -d "$source" ] && [ ! -e "$target" ]; then
          ln -s "$source" "$target"
          echo "      ↪️  Linked $(basename "$repo_path")"
        fi
      fi
    else
      echo "   ⚠️  Failed to clone $repo_name (branch $repo_branch may not exist)"
    fi
  done < "$DEPS_FILE"

  echo ""
  echo "✅ Installation Complete"
  echo "   Installed: $installed"
  echo "   Skipped:   $skipped"
  echo ""
  echo "📝 Next steps:"
  echo "   1. Review installed modules: ls -la $ADDONS_DIR/../oca-repos"
  echo "   2. Update addons path in odoo.conf to include OCA repos"
  echo "   3. Restart Odoo and install required modules"
}

update_dependencies() {
  echo "🔄 Updating OCA Dependencies"
  echo ""

  local updated=0
  local failed=0

  cd "$ADDONS_DIR/../oca-repos" 2>/dev/null || {
    echo "❌ No OCA repos found. Run: $0 install"
    exit 1
  }

  for repo_dir in oca-*; do
    [ -d "$repo_dir" ] || continue

    repo_name="${repo_dir#oca-}"
    echo "   📥 Updating $repo_name..."

    cd "$repo_dir"
    if git pull --ff-only 2>/dev/null; then
      echo "   ✅ Updated $repo_name"
      ((updated++))
    else
      echo "   ⚠️  Failed to update $repo_name"
      ((failed++))
    fi
    cd ..
  done

  echo ""
  echo "✅ Update Complete"
  echo "   Updated: $updated"
  echo "   Failed:  $failed"
}

list_dependencies() {
  echo "📋 OCA Dependencies List"
  echo ""

  if [ ! -d "$ADDONS_DIR/../oca-repos" ]; then
    echo "⚠️  No OCA repos installed yet"
    echo ""
    echo "Configured in $DEPS_FILE:"
    grep -v '^#' "$DEPS_FILE" | grep -v '^$' || echo "  (none)"
    return
  fi

  cd "$ADDONS_DIR/../oca-repos"

  printf "%-30s %-15s %-40s\n" "Repository" "Branch" "Last Update"
  printf "%s\n" "$(printf '─%.0s' {1..90})"

  for repo_dir in oca-*; do
    [ -d "$repo_dir" ] || continue

    repo_name="${repo_dir#oca-}"
    cd "$repo_dir"

    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    last_update=$(git log -1 --format="%ar" 2>/dev/null || echo "unknown")

    printf "%-30s %-15s %-40s\n" "$repo_name" "$branch" "$last_update"
    cd ..
  done
}

validate_dependencies() {
  echo "🔍 Validating OCA Dependencies"
  echo ""

  local errors=0
  cd "$ADDONS_DIR/../oca-repos" 2>/dev/null || {
    echo "❌ No OCA repos found"
    exit 1
  }

  for repo_dir in oca-*; do
    [ -d "$repo_dir" ] || continue

    repo_name="${repo_dir#oca-}"
    cd "$repo_dir"

    # Check if on correct branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" != "$ODOO_VERSION" ]; then
      echo "   ⚠️  $repo_name: on branch $current_branch (expected $ODOO_VERSION)"
      ((errors++))
    else
      echo "   ✅ $repo_name: correct branch ($ODOO_VERSION)"
    fi

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
      echo "      ⚠️  Has uncommitted changes"
      ((errors++))
    fi

    cd ..
  done

  echo ""
  if [ $errors -eq 0 ]; then
    echo "✅ All dependencies valid"
    return 0
  else
    echo "⚠️  Found $errors issue(s)"
    return 1
  fi
}

analyze_dependencies() {
  echo "🔬 Analyzing Dependency Tree"
  echo ""

  if [ ! -d "$ADDONS_DIR" ]; then
    echo "❌ Addons directory not found: $ADDONS_DIR"
    exit 1
  fi

  # Find all __manifest__.py files
  local total_modules=0
  local total_deps=0
  declare -A dep_count

  for manifest in $(find "$ADDONS_DIR" -name "__manifest__.py" -o -name "__openerp__.py"); do
    ((total_modules++))

    # Extract dependencies using Python
    deps=$(python3 -c "
import ast
try:
    manifest = ast.literal_eval(open('$manifest').read())
    deps = manifest.get('depends', [])
    print('\n'.join(deps))
except:
    pass
" 2>/dev/null)

    if [ -n "$deps" ]; then
      while IFS= read -r dep; do
        ((total_deps++))
        ((dep_count[$dep]=${dep_count[$dep]:-0}+1))
      done <<< "$deps"
    fi
  done

  echo "📊 Statistics:"
  echo "   Total modules: $total_modules"
  echo "   Total dependencies: $total_deps"
  echo "   Unique dependencies: ${#dep_count[@]}"
  echo ""

  echo "🔝 Most used dependencies:"
  for dep in "${!dep_count[@]}"; do
    echo "${dep_count[$dep]} $dep"
  done | sort -rn | head -10 | awk '{printf "   %2d  %s\n", $1, $2}'

  echo ""
  echo "📦 External (OCA) dependencies:"
  for dep in "${!dep_count[@]}"; do
    if [ ! -d "$ADDONS_DIR/$dep" ]; then
      echo "   ⚠️  $dep (used ${dep_count[$dep]} times, not found locally)"
    fi
  done
}

# Main logic
case "$ACTION" in
  check)
    check_dependencies
    ;;
  install)
    install_dependencies
    ;;
  update)
    update_dependencies
    ;;
  list)
    list_dependencies
    ;;
  validate)
    validate_dependencies
    ;;
  analyze)
    analyze_dependencies
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "❌ Unknown action: $ACTION"
    usage
    ;;
esac
