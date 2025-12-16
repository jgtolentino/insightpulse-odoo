#!/bin/bash
# Clarity PPM Parity - Complete Installation Script
# Author: InsightPulse AI
# License: AGPL-3

set -e

echo "=========================================="
echo "Clarity PPM Parity Installation Script"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
ODOO_PATH="${ODOO_PATH:-/opt/odoo}"
ADDONS_PATH="${ADDONS_PATH:-/opt/odoo/custom-addons}"
OCA_PATH="${OCA_PATH:-/opt/odoo/oca-addons}"
ODOO_USER="${ODOO_USER:-odoo}"
DB_NAME="${DB_NAME:-production}"

echo "Configuration:"
echo "  Odoo Path: $ODOO_PATH"
echo "  Addons Path: $ADDONS_PATH"
echo "  OCA Path: $OCA_PATH"
echo "  Odoo User: $ODOO_USER"
echo "  Database: $DB_NAME"
echo ""

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"

if ! command_exists git; then
    echo -e "${RED}Error: git is not installed${NC}"
    exit 1
fi

if ! command_exists python3; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    exit 1
fi

if [ ! -d "$ODOO_PATH" ]; then
    echo -e "${RED}Error: Odoo path not found: $ODOO_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Clone OCA project repository
echo -e "${YELLOW}Step 2: Cloning OCA project repository...${NC}"

if [ -d "$OCA_PATH/project" ]; then
    echo "OCA project repository already exists. Updating..."
    cd "$OCA_PATH/project"
    git pull origin 18.0
else
    echo "Cloning OCA project repository..."
    mkdir -p "$OCA_PATH"
    git clone https://github.com/OCA/project.git -b 18.0 "$OCA_PATH/project"
fi

echo -e "${GREEN}✓ OCA repository ready${NC}"
echo ""

# Update odoo.conf
echo -e "${YELLOW}Step 3: Updating odoo.conf...${NC}"

ODOO_CONF="${ODOO_CONF:-/etc/odoo/odoo.conf}"

if [ -f "$ODOO_CONF" ]; then
    echo "Backing up odoo.conf..."
    cp "$ODOO_CONF" "$ODOO_CONF.backup.$(date +%Y%m%d-%H%M%S)"

    # Check if OCA path already in addons_path
    if grep -q "$OCA_PATH/project" "$ODOO_CONF"; then
        echo "OCA path already in addons_path"
    else
        echo "Adding OCA path to addons_path..."
        # Get current addons_path
        CURRENT_ADDONS=$(grep "^addons_path" "$ODOO_CONF" | cut -d'=' -f2)
        NEW_ADDONS="${CURRENT_ADDONS},${OCA_PATH}/project"

        # Update addons_path
        sed -i.bak "s|^addons_path.*|addons_path = $NEW_ADDONS|" "$ODOO_CONF"
    fi

    echo -e "${GREEN}✓ odoo.conf updated${NC}"
else
    echo -e "${YELLOW}Warning: odoo.conf not found at $ODOO_CONF${NC}"
    echo "Please manually add the following to your addons_path:"
    echo "  $OCA_PATH/project"
fi

echo ""

# Install Python dependencies
echo -e "${YELLOW}Step 4: Installing Python dependencies...${NC}"

if [ -f "$OCA_PATH/project/requirements.txt" ]; then
    pip3 install -r "$OCA_PATH/project/requirements.txt"
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}Warning: requirements.txt not found${NC}"
fi

echo ""

# Restart Odoo
echo -e "${YELLOW}Step 5: Restarting Odoo...${NC}"

if systemctl is-active --quiet odoo; then
    sudo systemctl restart odoo
    echo -e "${GREEN}✓ Odoo restarted${NC}"
else
    echo -e "${YELLOW}Warning: Odoo service not running or not managed by systemctl${NC}"
    echo "Please restart Odoo manually"
fi

echo ""

# Print OCA modules to install
echo -e "${YELLOW}Step 6: OCA Modules to Install${NC}"
echo ""
echo "Install these modules IN ORDER via Odoo UI (Apps → Update Apps List):"
echo ""
echo "  1. project_key              - Unique project codes"
echo "  2. project_category         - Portfolios/programs"
echo "  3. project_wbs              - Work Breakdown Structure"
echo "  4. project_parent_task_filter - Parent/child management"
echo "  5. project_milestone        - Milestone entity"
echo "  6. project_task_milestone   - Task-milestone linking"
echo "  7. project_task_dependency  - Task dependencies (FS/SS/FF/SF)"
echo "  8. project_task_checklist   - To-Do items"
echo "  9. project_timeline         - Gantt chart"
echo ""

# Print manual installation steps
echo -e "${YELLOW}Step 7: Manual Installation Steps${NC}"
echo ""
echo "1. Log into Odoo as admin"
echo "2. Go to Apps → Update Apps List"
echo "3. Install OCA modules in the order above"
echo "4. Install 'InsightPulse Clarity PPM Parity' module"
echo "5. Verify installation:"
echo "   - Check Project form has 'Clarity ID' field"
echo "   - Check 'Baseline & Variance' tab exists"
echo "   - Check 'Phases' tab shows WBS hierarchy"
echo "   - Verify seed data: 2 projects, 8 phases, 6 milestones"
echo ""

# Print database upgrade command
echo -e "${YELLOW}Alternative: Database Upgrade (CLI)${NC}"
echo ""
echo "To install via CLI:"
echo ""
echo "  cd $ODOO_PATH"
echo "  ./odoo-bin -d $DB_NAME \\"
echo "    -i project_key,project_category,project_wbs,project_parent_task_filter,\\"
echo "project_milestone,project_task_milestone,project_task_dependency,\\"
echo "project_task_checklist,project_timeline,ipai_clarity_ppm_parity \\"
echo "    --stop-after-init"
echo ""

echo -e "${GREEN}=========================================="
echo "Installation Script Complete!"
echo "==========================================${NC}"
echo ""
echo "Next Steps:"
echo "  1. Install OCA modules via UI (or use CLI command above)"
echo "  2. Install ipai_clarity_ppm_parity module"
echo "  3. Configure portfolios: Project → Configuration → Project Categories"
echo "  4. Verify seed data loaded successfully"
echo "  5. Read README.rst for usage examples"
echo ""
echo "Documentation:"
echo "  - Module README: $ADDONS_PATH/ipai_clarity_ppm_parity/README.rst"
echo "  - Implementation Summary: $ADDONS_PATH/ipai_clarity_ppm_parity/IMPLEMENTATION_SUMMARY.md"
echo "  - Skill Guide: $ADDONS_PATH/../skills/odoo/clarity-ppm-parity/SKILL.md"
echo ""
