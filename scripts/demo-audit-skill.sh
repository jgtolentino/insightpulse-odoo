#!/usr/bin/env bash
#
# demo-audit-skill.sh - Demonstration of the Audit Skill capabilities
# Shows how to use the newly implemented audit skill to perform comprehensive audits
#
# Usage: ./scripts/demo-audit-skill.sh [module_path]
#
# Example:
#   ./scripts/demo-audit-skill.sh addons/custom/ipai_expense

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC}  $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

# Helper function to sanitize numeric values
sanitize_number() {
    local value="$1"
    value=$(echo "$value" | tr -d ' \n' | grep -o '[0-9]*' | head -1)
    echo "${value:-0}"
}

# Module to audit (default to ipai_expense)
MODULE_PATH="${1:-addons/custom/ipai_expense}"
MODULE_NAME=$(basename "$MODULE_PATH")

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Audit Skill Demonstration                                    ║${NC}"
echo -e "${BLUE}║  Module: $MODULE_NAME${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_info "Reading audit skill documentation..."
echo "📚 Skill location: docs/claude-code-skills/audit-skill/SKILL.md"
echo ""

# Security Audit
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Security Audit${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

log_info "1. Scanning for hardcoded credentials..."
CREDS_FOUND=$(sanitize_number "$(grep -r "password\s*=\s*['\"]" "$MODULE_PATH" --include="*.py" --include="*.conf" 2>/dev/null | wc -l || echo 0)")
if [ "$CREDS_FOUND" -gt 0 ]; then
    log_error "Found $CREDS_FOUND potential hardcoded credentials"
    grep -rn "password\s*=\s*['\"]" "$MODULE_PATH" --include="*.py" --include="*.conf" 2>/dev/null | head -3
else
    log_success "No hardcoded credentials found"
fi
echo ""

log_info "2. Scanning for API keys and tokens..."
API_KEYS=$(sanitize_number "$(grep -r "api_key\|API_KEY\|token\s*=\s*['\"]" "$MODULE_PATH" --include="*.py" 2>/dev/null | wc -l || echo 0)")
if [ "$API_KEYS" -gt 0 ]; then
    log_error "Found $API_KEYS potential API keys/tokens"
    grep -rn "api_key\|API_KEY\|token\s*=\s*['\"]" "$MODULE_PATH" --include="*.py" 2>/dev/null | head -3
else
    log_success "No hardcoded API keys found"
fi
echo ""

log_info "3. Checking for SQL injection vulnerabilities..."
SQL_EXEC=$(sanitize_number "$(grep -r "self\.env\.cr\.execute\|self\._cr\.execute" "$MODULE_PATH" --include="*.py" 2>/dev/null | wc -l || echo 0)")
if [ "$SQL_EXEC" -gt 0 ]; then
    log_warning "Found $SQL_EXEC direct SQL executions (review for parameterization)"
else
    log_success "No direct SQL execution found"
fi
echo ""

log_info "4. Checking for insecure external API calls..."
INSECURE_API=$(sanitize_number "$(grep -r "verify=False\|timeout=None" "$MODULE_PATH" --include="*.py" 2>/dev/null | wc -l || echo 0)")
if [ "$INSECURE_API" -gt 0 ]; then
    log_error "Found $INSECURE_API insecure API configurations"
else
    log_success "No insecure API configurations found"
fi
echo ""

# Module Structure Audit
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Module Structure Audit${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

log_info "5. Checking directory structure..."
REQUIRED_DIRS=("models" "views" "security")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$MODULE_PATH/$dir" ]; then
        log_success "$dir/ directory exists"
    else
        log_error "$dir/ directory missing"
    fi
done
echo ""

log_info "6. Checking required files..."
if [ -f "$MODULE_PATH/__manifest__.py" ]; then
    log_success "__manifest__.py exists"
else
    log_error "__manifest__.py missing (CRITICAL)"
fi

if [ -f "$MODULE_PATH/__init__.py" ]; then
    log_success "__init__.py exists"
else
    log_error "__init__.py missing (CRITICAL)"
fi

if [ -f "$MODULE_PATH/README.rst" ] || [ -f "$MODULE_PATH/README.md" ]; then
    log_success "README file exists"
else
    log_warning "README file missing (recommended)"
fi
echo ""

log_info "7. Validating security configuration..."
if [ -f "$MODULE_PATH/security/ir.model.access.csv" ]; then
    log_success "ir.model.access.csv exists"
    RULES=$(tail -n +2 "$MODULE_PATH/security/ir.model.access.csv" 2>/dev/null | wc -l || echo "0")
    echo "   Access rules: $RULES"
else
    log_error "ir.model.access.csv missing (CRITICAL)"
fi
echo ""

# Manifest Validation
log_info "8. Validating manifest..."
if [ -f "$MODULE_PATH/__manifest__.py" ]; then
    python3 << PYTHON_SCRIPT
import ast

try:
    with open("$MODULE_PATH/__manifest__.py") as f:
        manifest = ast.literal_eval(f.read())
    
    required_keys = ['name', 'version', 'category', 'author', 'license', 'depends']
    missing = [k for k in required_keys if k not in manifest]
    
    if missing:
        print(f"❌ Missing required keys: {', '.join(missing)}")
    else:
        print("✅ All required manifest keys present")
    
    # Version check
    if 'version' in manifest:
        version = manifest['version']
        parts = version.split('.')
        if len(parts) == 5:
            print(f"✅ Version format valid: {version}")
        else:
            print(f"⚠️  Version format should be X.0.Y.Z.W, got: {version}")
    
    # License check
    if 'license' in manifest:
        valid_licenses = ['AGPL-3', 'GPL-2', 'GPL-3', 'LGPL-3', 'MIT', 'Apache-2.0']
        if manifest['license'] in valid_licenses:
            print(f"✅ License valid: {manifest['license']}")
        else:
            print(f"⚠️  Non-standard license: {manifest['license']}")
            
except Exception as e:
    print(f"❌ Error parsing manifest: {e}")
PYTHON_SCRIPT
fi
echo ""

# Performance Check
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Performance Check${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

log_info "9. Checking for potential performance issues..."
# Check for fields that might need indexes
if [ -d "$MODULE_PATH/models" ]; then
    CHAR_FIELDS=$(sanitize_number "$(grep -r "fields\.Char\|fields\.Text" "$MODULE_PATH/models" --include="*.py" 2>/dev/null | wc -l || echo 0)")
    INDEXED_FIELDS=$(sanitize_number "$(grep -r "index=True" "$MODULE_PATH/models" --include="*.py" 2>/dev/null | wc -l || echo 0)")
    echo "   Char/Text fields: $CHAR_FIELDS"
    echo "   Indexed fields: $INDEXED_FIELDS"
    
    if [ "$CHAR_FIELDS" -gt 0 ] && [ "$INDEXED_FIELDS" -eq 0 ]; then
        log_warning "Consider adding indexes to frequently searched fields"
    else
        log_success "Some fields have indexes"
    fi
fi
echo ""

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Audit Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

CRITICAL_ISSUES=0
HIGH_ISSUES=0
MEDIUM_ISSUES=0

# Count issues (values already sanitized by helper function)
if [ "$CREDS_FOUND" -gt 0 ]; then ((CRITICAL_ISSUES++)); fi
if [ "$API_KEYS" -gt 0 ]; then ((CRITICAL_ISSUES++)); fi
if [ "$INSECURE_API" -gt 0 ]; then ((HIGH_ISSUES++)); fi
if [ "$SQL_EXEC" -gt 0 ]; then ((MEDIUM_ISSUES++)); fi

echo "📊 Issue Count:"
echo "   🔴 Critical: $CRITICAL_ISSUES"
echo "   🟠 High: $HIGH_ISSUES"
echo "   🟡 Medium: $MEDIUM_ISSUES"
echo ""

if [ $CRITICAL_ISSUES -eq 0 ] && [ $HIGH_ISSUES -eq 0 ]; then
    log_success "Module passes security audit!"
    echo ""
    echo "✅ Ready for production deployment"
elif [ $CRITICAL_ISSUES -gt 0 ]; then
    log_error "Critical issues found - immediate remediation required"
    echo ""
    echo "❌ NOT ready for production"
else
    log_warning "Some issues found - review before deployment"
    echo ""
    echo "⚠️  Address issues before production"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
log_info "For detailed audit procedures, see:"
echo "   • docs/claude-code-skills/audit-skill/SKILL.md"
echo "   • docs/claude-code-skills/audit-skill/reference/security-audit-guide.md"
echo "   • docs/claude-code-skills/audit-skill/reference/module-audit-guide.md"
echo ""
log_info "For examples, see:"
echo "   • docs/claude-code-skills/audit-skill/examples/security-audit-example.md"
echo "   • docs/claude-code-skills/audit-skill/examples/module-audit-example.md"
echo ""

exit 0
