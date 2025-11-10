#!/bin/bash
# Validate all workflow files for syntax and best practices

set -e

echo "Validating GitHub Actions workflows..."

WORKFLOWS=(
    ".github/workflows/self-healing.yml"
    ".github/workflows/router.yml"
    ".github/workflows/scheduled.yml"
    ".github/workflows/agent-review.yml"
    ".github/workflows/monitor.yml"
)

ERRORS=0

for workflow in "${WORKFLOWS[@]}"; do
    echo "Checking $workflow..."
    
    # Check if file exists
    if [ ! -f "$workflow" ]; then
        echo "  ✗ File not found"
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    # Validate YAML syntax
    if ! python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
        echo "  ✗ Invalid YAML syntax"
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    # Check for required fields
    if ! grep -q "^name:" "$workflow"; then
        echo "  ✗ Missing 'name' field"
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    if ! grep -q "^on:" "$workflow"; then
        echo "  ✗ Missing 'on' field"
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    if ! grep -q "^jobs:" "$workflow"; then
        echo "  ✗ Missing 'jobs' field"
        ERRORS=$((ERRORS + 1))
        continue
    fi
    
    # Check for permissions (security best practice)
    if ! grep -q "permissions:" "$workflow"; then
        echo "  ⚠ Warning: No permissions defined (not required but recommended)"
    fi
    
    echo "  ✓ Valid"
done

# Validate custom action
echo "Checking custom actions..."
ACTION=".github/actions/smart-cache/action.yml"

if [ -f "$ACTION" ]; then
    if python3 -c "import yaml; yaml.safe_load(open('$ACTION'))" 2>/dev/null; then
        echo "  ✓ $ACTION is valid"
    else
        echo "  ✗ $ACTION has invalid YAML"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ✗ $ACTION not found"
    ERRORS=$((ERRORS + 1))
fi

# Check CI scripts
echo "Checking CI scripts..."
for script in .github/scripts/ci/*.sh; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo "  ✓ $script is executable"
        else
            echo "  ⚠ Warning: $script is not executable"
        fi
        
        # Basic shell syntax check
        if bash -n "$script" 2>/dev/null; then
            echo "  ✓ $script has valid syntax"
        else
            echo "  ✗ $script has syntax errors"
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All validations passed!"
    exit 0
else
    echo "❌ Found $ERRORS error(s)"
    exit 1
fi
