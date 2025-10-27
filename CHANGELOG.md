# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation structure
- OCA-style module documentation
- Pre-commit hooks for automated documentation
- CI/CD pipeline with GitHub Actions
- Issue templates and labels
- Security hardening modules
- Vendor pin management

### Changed
- Updated module manifests with proper versioning
- Enhanced security access controls
- Improved module dependencies

### Fixed
- Sequence and cron file references in manifests
- Security rule implementations
- Documentation consistency

## [19.0.20251026.1] - 2025-10-26

### Added
- Initial release of InsightPulse Odoo modules
- Core IPAI modules: procure, expense, subscriptions
- Integration modules: superset, tableau, microservices
- System modules: apps_admin_enhancements, security_hardening
- Basic documentation structure

### Modules and Versions

#### IPAI Core Modules
- `ipai_procure`: 19.0.20251026.1
- `ipai_expense`: 19.0.20251026.1  
- `ipai_subscriptions`: 19.0.20251026.1

#### Integration Modules
- `superset_connector`: 19.0.20251026.1
- `tableau_connector`: 19.0.20251026.1
- `microservices_connector`: 19.0.20251026.1

#### System Modules
- `apps_admin_enhancements`: 19.0.20251026.1
- `security_hardening`: 19.0.20251026.1

### Features
- Procurement workflow with approvals and vendor management
- Expense management with OCR audit capabilities
- Subscription management with usage tracking
- Superset and Tableau BI integration
- Microservices health monitoring
- Enhanced module administration
- Security hardening features

## [19.0.20251025.1] - 2025-10-25

### Added
- Initial module scaffolding
- Basic model structures
- Security access controls
- View definitions

### Technical Details
- Odoo 19.0 compatibility
- PostgreSQL database support
- Docker containerization
- Basic CI/CD setup

## Module Version History

### ipai_procure
- **19.0.20251026.1**: Enhanced procurement workflow with vendor catalogs
- **19.0.20251025.1**: Initial procurement module with basic requisition workflow

### ipai_expense  
- **19.0.20251026.1**: Added OCR audit capabilities and expense policies
- **19.0.20251025.1**: Basic expense management with advances

### ipai_subscriptions
- **19.0.20251026.1**: Enhanced subscription management with dunning processes
- **19.0.20251025.1**: Basic subscription and usage tracking

### superset_connector
- **19.0.20251026.1**: Initial Superset integration with data export
- **19.0.20251025.1**: Basic configuration model

### tableau_connector
- **19.0.20251026.1**: Initial Tableau integration setup
- **19.0.20251025.1**: Basic configuration structure

### microservices_connector
- **19.0.20251026.1**: Health monitoring and service integration
- **19.0.20251025.1**: Initial microservices framework

### apps_admin_enhancements
- **19.0.20251026.1**: Module refresh automation and enhanced administration
- **19.0.20251025.1**: Basic module management features

### security_hardening
- **19.0.20251026.1**: Comprehensive security controls and access management
- **19.0.20251025.1**: Initial security framework

## Dependency Versions

### OCA Modules
- `queue_job`: 19.0.1.0.0
- `base_tier_validation`: 19.0.1.0.0
- `server_environment`: 19.0.1.0.0
- `report_xlsx`: 19.0.1.0.0
- `contract`: 19.0.1.0.0
- `contract_sale`: 19.0.1.0.0
- `contract_invoice`: 19.0.1.0.0

### Odoo Core
- Odoo Community Edition: 19.0
- PostgreSQL: 13+
- Python: 3.8+

## Upgrade Instructions

### From 19.0.20251025.1 to 19.0.20251026.1

1. **Backup Database**
   ```bash
   docker-compose exec postgres pg_dump -U odoo odoo > backup_20251026.sql
   ```

2. **Update Modules**
   ```bash
   # Update module code
   git pull origin main
   
   # Upgrade modules in Odoo
   # Navigate to Apps → Update Apps List
   # Upgrade all IPAI modules
   ```

3. **Run Post-Update Tasks**
   ```bash
   # Regenerate documentation
   pre-commit run oca-gen-addon-readme --all-files
   
   # Run tests
   pre-commit run --all-files
   ```

## Known Issues

### Current Limitations
- Real-time data sync for BI integration requires manual configuration
- Some advanced security features need additional setup
- Documentation generation requires pre-commit installation

### Planned Fixes
- Automated real-time sync configuration
- Enhanced security setup wizards
- Improved documentation tooling

## Future Releases

### Planned for 19.0.202511.1
- Advanced AI-powered analytics
- Enhanced mobile support
- Multi-tenant architecture
- Advanced reporting capabilities

### Planned for 19.0.202512.1  
- Comprehensive API ecosystem
- Advanced machine learning integration
- Enhanced performance optimization
- Extended third-party integrations
