#!/bin/bash

set -e

echo "🔧 Validating Makefile..."

# Check Makefile exists
if [ ! -f Makefile ]; then
    echo "❌ Makefile not found"
    exit 1
fi

echo "   ✓ Makefile exists"

# Check Makefile syntax
if make -n help > /dev/null 2>&1; then
    echo "   ✓ Makefile syntax is valid"
else
    echo "❌ Makefile has syntax errors"
    exit 1
fi

# Check all targets are documented
echo ""
echo "📋 Checking Makefile targets..."

# Extract all targets
targets=$(make -qp 2>/dev/null | awk -F':' '/^[a-zA-Z0-9][^$#\/\t=]*:([^=]|$)/ {split($1,A,/ /);for(i in A)print A[i]}' | sort -u | grep -v '^$' | grep -v '^Makefile$' || true)

undocumented=0
total_targets=0

for target in $targets; do
    # Skip special targets
    if [[ "$target" =~ ^[.%] ]] || [[ "$target" == "all" ]]; then
        continue
    fi

    total_targets=$((total_targets + 1))

    # Check if target is documented with ##
    if ! grep -q "^${target}:.*##" Makefile 2>/dev/null; then
        echo "   ⚠️  Undocumented target: $target"
        undocumented=$((undocumented + 1))
    fi
done

if [ $undocumented -eq 0 ]; then
    echo "   ✓ All $total_targets targets documented"
else
    echo "   ⚠️  $undocumented of $total_targets targets undocumented"
fi

# Test that key targets work
echo ""
echo "🧪 Testing key Makefile targets..."

key_targets="help"

for target in $key_targets; do
    if make -n $target > /dev/null 2>&1; then
        echo "   ✅ $target works"
    else
        echo "   ❌ $target is broken"
        exit 1
    fi
done

echo ""
echo "✅ Makefile validation passed"
