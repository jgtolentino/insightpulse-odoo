---
name: oca-module-discovery
description: Discover relevant OCA modules for business needs and analyze compatibility
version: 1.0.0
tags: [oca, modules, discovery, compatibility, dependencies]
requires:
  files:
    - vendor/oca-apps-store/README.md
    - vendor/oca-apps-store/apps/
    - vendor/oca-apps-store/categories/
---

# OCA Module Discovery Skill

## Purpose

Intelligently discover and recommend OCA modules based on business requirements, analyze compatibility with current setup, and generate installation scripts.

## When to use

- Finding OCA modules for specific business needs
- Analyzing module compatibility and dependencies
- Generating installation and configuration scripts
- Managing module versions and updates
- Resolving dependency conflicts

## Actions

1. **Requirement Analysis**: Analyze business requirements to identify needed modules
2. **Module Discovery**: Search OCA apps-store and repositories for relevant modules
3. **Compatibility Analysis**: Check module compatibility with Odoo version and existing modules
4. **Dependency Resolution**: Analyze and resolve module dependencies
5. **Installation Planning**: Generate installation scripts and configuration guidance

## Inputs

- `business_requirements`: Description of business needs or functionality
- `target_odoo_version`: Odoo version for compatibility checking
- `existing_modules`: List of currently installed modules
- `search_categories`: Specific OCA categories to search (optional)
- `compatibility_check`: Boolean to perform detailed compatibility analysis

## Outputs

- Recommended OCA modules with relevance scores
- Compatibility analysis report
- Installation scripts and commands
- Configuration guidance and best practices
- Dependency resolution plan

## Examples

### Example 1: Module Discovery
```
User: "Find modules for project management and timesheets"

Agent:
1. Analyzes project management and timesheet requirements
2. Searches OCA apps-store for relevant modules:
   - project (core project management)
   - hr_timesheet (timesheet tracking)
   - project_timesheet_time_control (time control)
   - project_task_dependency (task dependencies)
3. Provides compatibility analysis with current Odoo 19 setup
4. Generates installation script with proper dependency order
5. Suggests configuration best practices
```

### Example 2: Compatibility Analysis
```
User: "Check if OCA accounting modules work with our setup"

Agent:
1. Analyzes current Odoo 19 installation and existing modules
2. Checks OCA accounting modules compatibility:
   - account_financial_reporting
   - account_asset_management
   - account_budget
3. Identifies potential conflicts and dependencies
4. Provides migration strategy if needed
5. Generates step-by-step installation guide
```

### Example 3: Dependency Resolution
```
User: "Install OCA HR modules and resolve dependencies"

Agent:
1. Analyzes OCA HR module ecosystem
2. Identifies core dependencies and optional modules
3. Creates dependency resolution plan:
   - Core HR modules first
   - Dependent modules in proper order
   - Conflict resolution for overlapping functionality
4. Generates installation script with dependency management
5. Provides testing and validation steps
```

## Implementation Details

### Discovery Process

```typescript
interface DiscoveryProcess {
  requirement_analysis: {
    business_needs: string[];
    functional_requirements: string[];
    technical_constraints: string[];
  };
  module_search: {
    search_terms: string[];
    categories: string[];
    repositories: string[];
  };
  compatibility_check: {
    odoo_version: string;
    existing_modules: string[];
    dependency_analysis: string[];
    conflict_detection: string[];
  };
  recommendation: {
    recommended_modules: ModuleRecommendation[];
    installation_plan: InstallationStep[];
    configuration_guide: ConfigurationStep[];
  };
}
```

### Module Recommendation Engine

**Scoring Criteria:**
- Functional match with requirements
- Popularity and community adoption
- Maintenance status and activity
- Documentation quality
- Test coverage
- Compatibility with target Odoo version

**Recommendation Levels:**
- **Essential**: Core modules that directly match requirements
- **Recommended**: Modules that enhance functionality
- **Optional**: Additional modules for extended features
- **Alternative**: Different approaches to same requirements

### Compatibility Analysis

**Compatibility Checks:**
- Odoo version compatibility
- Module dependency satisfaction
- Conflict detection with existing modules
- Database migration requirements
- Performance impact assessment

**Dependency Resolution:**
```yaml
installation_order:
  - core_dependencies:
    - base
    - web
  - framework_modules:
    - queue_job
    - base_import
  - functional_modules:
    - hr
    - project
  - enhancement_modules:
    - hr_skills
    - project_timesheet
```

### Installation Script Generation

```bash
# Generated installation script
#!/bin/bash

# Install core dependencies
odoo --stop-after-init -i base,web

# Install framework modules
odoo --stop-after-init -i queue_job,base_import

# Install functional modules
odoo --stop-after-init -i hr,project

# Install enhancement modules
odoo --stop-after-init -i hr_skills,project_timesheet

# Run post-installation configuration
echo "Configuration steps:"
echo "1. Configure HR settings in Settings > Employees"
echo "2. Set up project templates in Project > Configuration"
echo "3. Configure timesheet policies in Settings > Timesheets"
```

## Success Metrics

- **Relevance Accuracy**: ≥ 90% match with business requirements
- **Compatibility Detection**: 100% conflict identification
- **Installation Success**: ≥ 95% successful installations
- **Dependency Resolution**: 100% dependency satisfaction
- **User Satisfaction**: ≥ 4.5/5 for module recommendations

## References

- [OCA Apps Store](vendor/oca-apps-store/)
- [OCA Module Categories](vendor/oca-apps-store/categories/)
- [OCA Module Documentation](vendor/oca-apps-store/apps/)
- [OCA Compatibility Guidelines](vendor/oca-apps-store/doc/compatibility.md)
