#!/bin/bash
# OCA Module Installation Script
# InsightPulse Odoo Finance SSC Edition
# Version: 1.0
# Date: 2025-11-05

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ODOO_VERSION="${ODOO_VERSION:-19.0}"
OCA_DIR="${OCA_DIR:-./addons/oca}"
INSTALL_LOG="./logs/oca_installation_$(date +%Y%m%d_%H%M%S).log"

# Create log directory
mkdir -p "$(dirname "$INSTALL_LOG")"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$INSTALL_LOG"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$INSTALL_LOG"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$INSTALL_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$INSTALL_LOG"
}

# OCA repositories to clone
OCA_REPOS=(
    # Core security & authentication
    "server-auth"
    "server-backend"
    "server-tools"

    # Document management
    "knowledge"
    "dms"

    # Web & UI enhancements
    "web"

    # Communication
    "social"

    # Integrations
    "connector"
    "rest-framework"

    # Reporting & Analytics
    "reporting-engine"
    "mis-builder"

    # Workflows
    "approval"

    # Finance modules
    "account-financial-reporting"
    "account-financial-tools"
    "account-invoicing"
    "bank-payment"

    # Data protection
    "data-protection"
)

# Essential modules to install (auto-install)
ESSENTIAL_MODULES=(
    # Security
    "auth_totp"
    "password_security"
    "auth_session_timeout"

    # Audit
    "auditlog"

    # Document management
    "document_page"

    # Reporting
    "report_xlsx"

    # Web enhancements
    "web_widget_markdown"
)

# Optional modules (user can choose)
OPTIONAL_MODULES=(
    # SAML SSO
    "auth_saml"

    # Advanced roles
    "base_user_role"

    # Document versioning
    "document_versioning"

    # Approval workflows
    "approval_request"

    # REST API
    "base_rest"
    "base_rest_auth_jwt"

    # Finance reporting
    "mis_builder"

    # GDPR compliance
    "privacy"
    "privacy_consent"

    # Mail tracking
    "mail_tracking"

    # Web views
    "web_timeline"
    "web_view_gallery"
)

# Function to clone OCA repository
clone_oca_repo() {
    local repo=$1
    local repo_url="https://github.com/OCA/${repo}.git"
    local target_dir="${OCA_DIR}/${repo}"

    if [ -d "$target_dir" ]; then
        log_warning "Repository $repo already exists. Pulling latest changes..."
        cd "$target_dir"
        git pull origin "$ODOO_VERSION" 2>&1 | tee -a "$INSTALL_LOG"
        cd - > /dev/null
    else
        log_info "Cloning $repo..."
        if git clone --depth 1 --branch "$ODOO_VERSION" "$repo_url" "$target_dir" 2>&1 | tee -a "$INSTALL_LOG"; then
            log_success "Successfully cloned $repo"
        else
            log_error "Failed to clone $repo (branch $ODOO_VERSION may not exist)"
            return 1
        fi
    fi
}

# Function to create symlinks for modules
create_module_symlinks() {
    local repo=$1
    local repo_dir="${OCA_DIR}/${repo}"
    local target_dir="${OCA_DIR}/modules"

    mkdir -p "$target_dir"

    log_info "Creating symlinks for modules in $repo..."

    for module_path in "$repo_dir"/*; do
        if [ -d "$module_path" ] && [ -f "$module_path/__manifest__.py" ]; then
            local module_name=$(basename "$module_path")
            local link_path="$target_dir/$module_name"

            if [ ! -L "$link_path" ]; then
                ln -sf "$(realpath "$module_path")" "$link_path"
                log_info "  ✓ $module_name"
            fi
        fi
    done
}

# Function to install Python dependencies
install_python_dependencies() {
    log_info "Installing Python dependencies for OCA modules..."

    pip3 install --break-system-packages \
        pysaml2==7.4.2 \
        xmlsec==1.3.13 \
        pyotp==2.9.0 \
        qrcode==7.4.2 \
        openpyxl==3.1.2 \
        xlsxwriter==3.1.9 \
        xlrd==2.0.1 \
        py3o.template==0.10.0 \
        py3o.formats==0.3 \
        python-docx==1.1.0 \
        pypdf2==3.0.1 \
        apispec==6.3.1 \
        marshmallow==3.20.1 \
        watchdog==3.0.0 \
        2>&1 | tee -a "$INSTALL_LOG"

    log_success "Python dependencies installed"
}

# Function to generate module installation guide
generate_install_guide() {
    local guide_file="./docs/OCA_MODULE_INSTALLATION.md"

    log_info "Generating installation guide..."

    cat > "$guide_file" <<EOF
# OCA Module Installation Guide

**Generated:** $(date)
**Odoo Version:** ${ODOO_VERSION}

## Installation Summary

### Repositories Cloned

The following OCA repositories have been cloned:

$(for repo in "${OCA_REPOS[@]}"; do echo "- ✅ $repo"; done)

### Essential Modules (Auto-Install Recommended)

These modules are essential for Finance SSC operations and should be installed immediately:

\`\`\`bash
# Install essential modules
odoo-bin -c /etc/odoo/odoo.conf -d odoo19 -i $(IFS=,; echo "${ESSENTIAL_MODULES[*]}") --stop-after-init
\`\`\`

**Modules:**
$(for module in "${ESSENTIAL_MODULES[@]}"; do echo "- \`$module\`"; done)

### Optional Modules (Install as Needed)

These modules provide additional functionality and can be installed based on requirements:

**Security & Authentication:**
- \`auth_saml\` - SAML 2.0 SSO integration
- \`base_user_role\` - Advanced role management

**Document Management:**
- \`document_versioning\` - Document version control
- \`document_page_approval\` - Approval workflows for documents

**REST API:**
- \`base_rest\` - REST API framework
- \`base_rest_auth_jwt\` - JWT authentication for REST API

**Finance & Reporting:**
- \`mis_builder\` - Management Information System builder
- \`account_financial_reporting\` - Financial reports

**Compliance:**
- \`privacy\` - GDPR compliance
- \`privacy_consent\` - Consent management

**Communication:**
- \`mail_tracking\` - Email tracking

**UI Enhancements:**
- \`web_timeline\` - Timeline view
- \`web_view_gallery\` - Gallery view

### Installation Commands

#### 1. Install Essential Modules (Recommended)

\`\`\`bash
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \\
  -c /etc/odoo/odoo.conf \\
  -d odoo19 \\
  -i $(IFS=,; echo "${ESSENTIAL_MODULES[*]}") \\
  --stop-after-init
\`\`\`

#### 2. Install Optional Modules (Choose what you need)

Example for SAML SSO + Audit + REST API:

\`\`\`bash
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \\
  -c /etc/odoo/odoo.conf \\
  -d odoo19 \\
  -i auth_saml,auditlog,base_rest,base_rest_auth_jwt \\
  --stop-after-init
\`\`\`

#### 3. Update Module List

After adding new modules, update the module list:

\`\`\`bash
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \\
  -c /etc/odoo/odoo.conf \\
  -d odoo19 \\
  -u all \\
  --stop-after-init
\`\`\`

### Module Configuration

#### SAML SSO Configuration

1. Install \`auth_saml\` module
2. Configure SAML settings in Odoo:
   - Go to Settings > Users & Companies > SAML Providers
   - Add your IdP metadata URL
   - Configure SP entity ID
   - Set attribute mappings

#### Audit Log Configuration

1. Install \`auditlog\` module
2. Configure rules:
   - Go to Settings > Technical > Audit > Rules
   - Create rules for models you want to audit
   - Enable logging for Finance SSC models

#### REST API Configuration

1. Install \`base_rest\` and \`base_rest_auth_jwt\`
2. Generate API keys:
   - Go to Settings > Users
   - Generate API token for integration users
3. Configure JWT settings if needed

### Troubleshooting

#### Module Not Found

If a module is not visible:

\`\`\`bash
# Update apps list
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \\
  -c /etc/odoo/odoo.conf \\
  -d odoo19 \\
  --update-all \\
  --stop-after-init
\`\`\`

#### Dependency Errors

If you encounter missing dependencies:

\`\`\`bash
# Install Python dependencies
docker-compose -f docker-compose.oca.yml exec odoo pip3 install <package-name>
\`\`\`

#### Database Migration Issues

If upgrading from older versions:

\`\`\`bash
# Run migration scripts
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \\
  -c /etc/odoo/odoo.conf \\
  -d odoo19 \\
  -u all \\
  --stop-after-init
\`\`\`

### Verification

Verify installed modules:

\`\`\`bash
# Check installed modules
docker-compose -f docker-compose.oca.yml exec odoo /opt/odoo/odoo-bin \\
  shell -c /etc/odoo/odoo.conf -d odoo19 \\
  --eval "env['ir.module.module'].search([('state', '=', 'installed')]).mapped('name')"
\`\`\`

### Next Steps

1. Configure multi-company setup (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
2. Set up SAML SSO integration
3. Configure audit logging for Finance SSC models
4. Deploy custom Finance SSC modules
5. Integrate with InsightPulse AI services
6. Setup Superset dashboards

### References

- [OCA Documentation](https://odoo-community.org/)
- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)
- [InsightPulse AI Documentation](../README.md)
- [Notion to Odoo Mapping](./NOTION_TO_ODOO_MAPPING.md)

---

**Maintained by:** InsightPulse AI Finance SSC Team
**Last Updated:** $(date)
EOF

    log_success "Installation guide created: $guide_file"
}

# Main execution
main() {
    echo ""
    echo "======================================"
    echo " OCA Module Installation Script"
    echo " InsightPulse Odoo Finance SSC"
    echo "======================================"
    echo ""
    echo "Odoo Version: $ODOO_VERSION"
    echo "Target Directory: $OCA_DIR"
    echo "Log File: $INSTALL_LOG"
    echo ""

    # Create OCA directory
    mkdir -p "$OCA_DIR"

    # Install Python dependencies
    read -p "Install Python dependencies? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_python_dependencies
    fi

    # Clone repositories
    log_info "Cloning OCA repositories..."
    for repo in "${OCA_REPOS[@]}"; do
        clone_oca_repo "$repo" || log_warning "Skipping $repo"
    done

    # Create symlinks
    log_info "Creating module symlinks..."
    for repo in "${OCA_REPOS[@]}"; do
        if [ -d "${OCA_DIR}/${repo}" ]; then
            create_module_symlinks "$repo"
        fi
    done

    # Generate installation guide
    generate_install_guide

    # Summary
    echo ""
    log_success "OCA module installation complete!"
    echo ""
    echo "Next steps:"
    echo "1. Review the installation guide: ./docs/OCA_MODULE_INSTALLATION.md"
    echo "2. Start Odoo with OCA modules: docker-compose -f docker-compose.oca.yml up -d"
    echo "3. Install essential modules via Odoo UI or CLI"
    echo "4. Configure SAML, audit logging, and other features"
    echo ""
    log_info "Installation log saved to: $INSTALL_LOG"
}

# Run main function
main "$@"
