---
name: oca-module-scaffold
description: Generate OCA-compliant modules from templates and validate against OCA standards
version: 1.0.0
tags: [oca, module, scaffolding, standards, compliance]
requires:
  files:
    - vendor/oca-template/README.md
    - vendor/oca-template/.copier-answers.yml
    - vendor/oca-template/.pre-commit-config.yaml
---

# OCA Module Scaffold Skill

## Purpose

Generate OCA-compliant Odoo modules with proper structure, standards, and best practices. Validate existing modules against OCA standards and suggest improvements.

## When to use

- Creating new Odoo modules that should be OCA-compliant
- Validating existing modules against OCA standards
- Converting custom modules to OCA format
- Generating module boilerplate and structure

## Actions

1. **Module Generation**: Create OCA-compliant module structure from business requirements
2. **Standards Validation**: Check modules against OCA coding standards and best practices
3. **Template Application**: Apply OCA template patterns to existing modules
4. **Compliance Reports**: Generate detailed compliance reports with improvement suggestions

## Inputs

- `module_name`: Name of the module to create/validate
- `business_requirements`: Description of module functionality
- `target_odoo_version`: Odoo version (default: 19.0)
- `validate_only`: Boolean to only validate without generation
- `existing_module_path`: Path to existing module for validation

## Outputs

- Generated module structure with all required files
- Compliance validation report
- Improvement suggestions for existing modules
- Installation and configuration instructions

## Examples

### Example 1: Generate New Module
```
User: "Create an expense approval module with OCA standards"

Agent:
1. Analyzes business requirements for expense approval
2. Generates OCA-compliant module structure:
   - __manifest__.py with proper metadata
   - Security files (ir.model.access.csv, security.xml)
   - Views, models, controllers structure
   - Tests directory with sample tests
   - README.md with installation instructions
3. Validates against OCA template standards
4. Provides installation commands
```

### Example 2: Validate Existing Module
```
User: "Validate my custom HR module against OCA standards"

Agent:
1. Analyzes existing module structure
2. Checks against OCA standards:
   - Manifest file completeness
   - Security implementation
   - Code formatting and style
   - Test coverage
   - Documentation quality
3. Generates compliance report with:
   - Passed checks (green)
   - Warnings (yellow)
   - Required fixes (red)
4. Provides specific improvement commands
```

### Example 3: Convert Custom Module
```
User: "Convert my custom CRM module to OCA format"

Agent:
1. Analyzes current module structure
2. Identifies OCA compliance gaps
3. Applies OCA template patterns:
   - Updates manifest with OCA metadata
   - Adds proper security files
   - Restructures directories
   - Adds test framework
   - Updates documentation
4. Generates migration report
```

## Implementation Details

### Module Structure Generation

```yaml
module_name/
├── __manifest__.py          # OCA-compliant manifest
├── __init__.py
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── models/
│   ├── __init__.py
│   └── [model_files].py
├── views/
│   ├── [view_files].xml
│   └── templates.xml
├── controllers/
│   ├── __init__.py
│   └── main.py
├── static/
│   └── description/
│       └── icon.png
├── tests/
│   ├── __init__.py
│   └── test_[module].py
├── data/
│   └── [data_files].xml
└── README.rst
```

### OCA Standards Validation

**Manifest Requirements:**
- Complete metadata (name, version, category, summary, description)
- Proper author and maintainer information
- Correct license (LGPL-3)
- Appropriate website and dependencies
- Valid application categorization

**Code Standards:**
- PEP 8 compliance for Python code
- Proper XML structure for views
- Security best practices
- Test coverage requirements
- Documentation standards

**File Structure:**
- Proper directory organization
- Required files presence
- Naming conventions
- Import organization

### Template Integration

Leverages OCA template patterns from:
- `vendor/oca-template/.copier-answers.yml` for configuration
- `vendor/oca-template/.pre-commit-config.yaml` for code quality
- OCA web patterns for UI components

## Success Metrics

- **Compliance Score**: ≥ 90% OCA standards adherence
- **Generation Time**: < 2 minutes for standard modules
- **Validation Accuracy**: 100% standards detection
- **Improvement Actionability**: Specific, executable suggestions

## References

- [OCA Module Template](vendor/oca-template/)
- [OCA Coding Guidelines](vendor/oca-template/README.md)
- [OCA Pre-commit Configuration](vendor/oca-template/.pre-commit-config.yaml)
- [OCA Module Standards Documentation](vendor/oca-web/doc/standards.md)
