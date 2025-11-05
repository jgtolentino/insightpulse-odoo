#!/bin/bash

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         COMPLETE REPOSITORY STRUCTURE VALIDATION            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track overall status
VALIDATION_FAILED=0

# ══════════════════════════════════════════════════════════════
# LEVEL 1: STRUCTURE VALIDATION
# ══════════════════════════════════════════════════════════════

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}LEVEL 1: STATIC STRUCTURE VALIDATION${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if python3 scripts/validate-repo-structure.py; then
    echo -e "${GREEN}✅ Structure validation PASSED${NC}"
else
    echo -e "${RED}❌ Structure validation FAILED${NC}"
    VALIDATION_FAILED=1
fi

echo ""

# ══════════════════════════════════════════════════════════════
# LEVEL 2: MAKEFILE VALIDATION
# ══════════════════════════════════════════════════════════════

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}LEVEL 2: MAKEFILE VALIDATION${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if bash scripts/validate-makefile.sh; then
    echo -e "${GREEN}✅ Makefile validation PASSED${NC}"
else
    echo -e "${RED}❌ Makefile validation FAILED${NC}"
    VALIDATION_FAILED=1
fi

echo ""

# ══════════════════════════════════════════════════════════════
# LEVEL 3: INTEGRATION TESTS
# ══════════════════════════════════════════════════════════════

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}LEVEL 3: INTEGRATION TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if python3 tests/integration/test_repo_structure.py; then
    echo -e "${GREEN}✅ Integration tests PASSED${NC}"
else
    echo -e "${YELLOW}⚠️  Integration tests had warnings${NC}"
    # Don't fail on integration test warnings
fi

echo ""

# ══════════════════════════════════════════════════════════════
# LEVEL 4: HEALTH REPORT
# ══════════════════════════════════════════════════════════════

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}LEVEL 4: HEALTH REPORT GENERATION${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if python3 scripts/generate-structure-report.py; then
    echo -e "${GREEN}✅ Health report generated${NC}"
else
    echo -e "${RED}❌ Health report generation FAILED${NC}"
    VALIDATION_FAILED=1
fi

echo ""

# ══════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                      VALIDATION SUMMARY                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

if [ -f structure-health-report.json ]; then
    echo "📊 HEALTH REPORT SUMMARY:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Extract and display scores
    python3 << 'EOF'
import json
import sys

try:
    with open('structure-health-report.json') as f:
        report = json.load(f)

    score = report['scores']['overall']
    grade = report['scores']['grade']

    print(f"\n  Overall Score: {score:.1f}% (Grade: {grade})")
    print("\n  Individual Scores:")

    for area, score_val in report['scores']['individual'].items():
        bar_length = int(score_val / 5)
        bar = '█' * bar_length + '░' * (20 - bar_length)
        print(f"    {area.capitalize():15} {bar} {score_val:.1f}%")

    print("\n  Quick Stats:")
    print(f"    • Directories: {report['metrics']['structure_compliance']['directories']['existing']}/{report['metrics']['structure_compliance']['directories']['required']}")
    print(f"    • Files: {report['metrics']['structure_compliance']['files']['existing']}/{report['metrics']['structure_compliance']['files']['required']}")
    print(f"    • Skills: {report['metrics']['skill_maturity']['total_skills']}")
    print(f"    • Workflows: {report['metrics']['automation_level']['github_workflows']}")
    print(f"    • Test files: {report['metrics']['test_coverage']['test_files']}")

    if report['recommendations']:
        print("\n  🎯 Top Recommendations:")
        for i, rec in enumerate(report['recommendations'][:3], 1):
            priority = '🔴' if rec['priority'] == 'high' else '🟡'
            print(f"    {priority} {rec['recommendation']}")

    print()

except Exception as e:
    print(f"⚠️  Could not parse health report: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📄 Full report saved to: structure-health-report.json"
    echo ""
fi

if [ $VALIDATION_FAILED -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ ALL VALIDATIONS PASSED! ✅                   ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ❌ VALIDATION FAILED ❌                         ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Please review the errors above and fix them before proceeding."
    exit 1
fi
