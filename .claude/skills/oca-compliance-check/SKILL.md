---
name: oca-compliance-check
description: Validate custom modules against OCA standards and generate improvement suggestions
version: 1.0.0
tags: [oca, compliance, standards, validation, quality]
requires:
  files:
    - vendor/oca-template/.copier-answers.yml
    - vendor/oca-template/.pre-commit-config.yaml
    - vendor/oca-web/doc/standards.md
---

# OCA Compliance Check Skill

## Purpose

Validate custom Odoo modules against OCA standards, identify compliance gaps, and generate specific improvement suggestions for OCA contribution readiness.

## When to use

- Validating custom modules before OCA contribution
- Checking existing modules against OCA standards
- Generating compliance improvement plans
- Preparing modules for OCA repository submission
- Maintaining OCA compliance in ongoing development

## Actions

1. **Standards Validation**: Check modules against OCA coding and structural standards
2. **Compliance Scoring**: Generate comprehensive compliance scores and reports
3. **Improvement Suggestions**: Provide specific, actionable improvement recommendations
4. **Automated Fixes**: Generate scripts for automatic compliance fixes where possible
5. **Contribution Readiness**: Assess module readiness for OCA contribution

## Inputs

- `module_path`: Path to the module to validate
- `validation_level`: Level of validation (basic, standard, strict)
- `generate_fixes`: Boolean to generate automatic fix scripts
- `contribution_check`: Boolean to check OCA contribution readiness
- `report_format`: Output format (markdown, html, json)

## Outputs

- Compliance validation report with scores
- Detailed improvement suggestions
- Automatic fix scripts (where applicable)
- OCA contribution readiness assessment
- Standards documentation references

## Examples

### Example 1: Basic Compliance Check
```
User: "Check my custom CRM module against OCA standards"

Agent:
1. Analyzes module structure and code
2. Validates against OCA standards:
   - Manifest file completeness
   - Security implementation
   - Code formatting (PEP 8, XML standards)
   - Documentation quality
   - Test coverage
3. Generates compliance report:
   - Overall score: 75%
   - Passed: 15 checks
   - Warnings: 8 items
   - Failures: 5 critical issues
4. Provides specific improvement commands
```

### Example 2: Contribution Readiness
```
User: "Is my module ready for OCA contribution?"

Agent:
1. Performs comprehensive OCA compliance check
2. Assesses contribution readiness:
   - Code quality and standards
   - Documentation completeness
   - Test coverage and quality
   - License compatibility
   - Community guidelines adherence
3. Provides contribution checklist:
   - Required fixes (must complete)
   - Recommended improvements (should complete)
   - Optional enhancements (could complete)
4. Generates contribution preparation guide
```

### Example 3: Automated Fixes
```
User: "Generate fixes for OCA compliance issues"

Agent:
1. Identifies automatable compliance issues:
   - Code formatting (black, isort)
   - XML structure (prettier-xml)
   - Manifest metadata updates
   - Security file generation
2. Generates fix scripts:
   - format_code.sh (black + isort)
   - update_manifest.py (metadata fixes)
   - generate_security.py (access rules)
3. Provides manual fix instructions for non-automatable issues
```

## Implementation Details

### Compliance Validation Framework

```typescript
interface ComplianceValidation {
  structural_checks: {
    manifest_completeness: boolean;
    directory_structure: boolean;
    file_naming: boolean;
    required_files: boolean;
  };
  code_quality: {
    pep8_compliance: boolean;
    xml_standards: boolean;
    security_best_practices: boolean;
    performance_considerations: boolean;
  };
  documentation: {
    readme_quality: boolean;
    code_documentation: boolean;
    changelog_presence: boolean;
    license_compliance: boolean;
  };
  testing: {
    test_structure: boolean;
    test_coverage: boolean;
    test_quality: boolean;
  };
}
```

### Validation Levels

**Basic Validation:**
- Manifest file completeness
- Basic directory structure
- Required files presence
- License compliance

**Standard Validation:**
- All basic checks
- Code formatting standards
- Security implementation
- Documentation quality
- Test structure

**Strict Validation:**
- All standard checks
- Performance considerations
- Community guidelines
- Contribution readiness
- Best practices adherence

### Automatic Fix Generation

**Code Formatting Fixes:**
```bash
# Generated fix script
#!/bin/bash

# Install formatting tools
pip install black isort

# Format Python code
black models/ views/ controllers/
isort models/ views/ controllers/

# Format XML files
find . -name "*.xml" -exec xmllint --format {} \;
```

**Manifest Updates:**
```python
# Generated manifest update script
def update_manifest(manifest_path):
    with open(manifest_path, 'r') as f:
        manifest = eval(f.read())
    
    # Add required OCA metadata
    manifest.update({
        'license': 'LGPL-3',
        'author': 'Your Name, OCA',
        'website': 'https://github.com/OCA/your-repo',
        'category': 'Your Category',
        'version': '16.0.1.0.0',
    })
    
    with open(manifest_path, 'w') as f:
        f.write(repr(manifest))
```

### Contribution Readiness Assessment

**Readiness Levels:**
- **Ready**: Meets all OCA contribution requirements
- **Nearly Ready**: Minor fixes required
- **Needs Work**: Significant improvements needed
- **Not Ready**: Major restructuring required

**Assessment Criteria:**
- Code quality and standards compliance
- Documentation completeness
- Test coverage and quality
- License and legal compliance
- Community guidelines adherence
- Technical architecture quality

## Success Metrics

- **Validation Accuracy**: 100% standards detection
- **Improvement Actionability**: Specific, executable suggestions
- **Fix Automation**: ≥ 70% of issues automatable
- **Compliance Improvement**: ≥ 50% score improvement after fixes
- **Contribution Success**: ≥ 90% OCA acceptance rate for compliant modules

## References

- [OCA Template Standards](vendor/oca-template/.copier-answers.yml)
- [OCA Pre-commit Configuration](vendor/oca-template/.pre-commit-config.yaml)
- [OCA Web Standards](vendor/oca-web/doc/standards.md)
- [OCA Contribution Guidelines](vendor/oca-template/CONTRIBUTING.md)
