# Visual Compliance Agent

**OCA Compliance Automation for Odoo 18.0 CE Modules**

The Visual Compliance Agent automates validation of Odoo Community Association (OCA) standards for InsightPulse Odoo modules using a modular Skills Registry architecture.

## Architecture

### Skills Registry Pattern

```
Skills (agents/skills.yaml)
    ↓
Skill Registry (agents/skill_registry.py)
    ↓
CLI Wrapper (agents/run_skill.py) ← CI/CD
    ↓
Validators (visual_compliance/validators/) ← Agents
    ↓
Core Tools (visual_compliance/tools/)
```

**Key Principles:**
- **Single Source of Truth**: `agents/skills.yaml` defines all capabilities
- **Standard Interface**: All skills implement `run_skill(params: Dict) -> Dict`
- **Zero Duplication**: Same skill code runs in CI, agents, and Visual Agent UI
- **Pluggable**: Add new validators without modifying orchestration layer

## Available Skills

### 1. odoo.manifest.validate
**Purpose**: Validates `__manifest__.py` files for Odoo 18.0, LGPL-3, and InsightPulseAI metadata

**Validations:**
- ✅ Odoo version format: `18.0.x.y.z`
- ✅ License: `LGPL-3`
- ✅ Author: `InsightPulseAI`
- ✅ Website: `https://github.com/jgtolentino/insightpulse-odoo`

**Auto-Fix:** ✅ Supported

**Usage:**
```bash
python -m agents.run_skill odoo.manifest.validate --repo-path . --fix
```

### 2. odoo.directory.validate
**Purpose**: Validates single canonical `odoo_addons/` directory (OCA standard)

**Validations:**
- ✅ Canonical `odoo_addons/` directory exists
- ✅ No multiple addon directories (`addons/`, `custom_addons/`)
- ✅ No duplicate modules across directories

**Auto-Fix:** ✅ Supported (consolidates to `odoo_addons/`)

**Usage:**
```bash
python -m agents.run_skill odoo.directory.validate --repo-path . --fix
```

### 3. odoo.naming.validate
**Purpose**: Validates `ipai_*` prefix for custom modules

**Validations:**
- ✅ Module name starts with `ipai_`
- ✅ No hyphens, uppercase, or invalid characters
- ✅ Excludes OCA community modules

**Auto-Fix:** ❌ Not supported (requires manual intervention)

**Usage:**
```bash
python -m agents.run_skill odoo.naming.validate --repo-path .
```

### 4. odoo.readme.validate
**Purpose**: Validates and generates README.rst documentation (OCA standard)

**Validations:**
- ✅ README.rst exists for each module
- ✅ Required sections: Description, Installation, Configuration, Usage, Bug Tracker, Credits
- ✅ OCA documentation format

**Auto-Fix:** ✅ Supported (generates README templates)

**Usage:**
```bash
python -m agents.run_skill odoo.readme.validate --repo-path . --fix
```

### 5. visual_compliance.full_scan
**Purpose**: Orchestrates all validators and generates comprehensive compliance report

**Features:**
- Runs all 4 validators
- Generates summary statistics
- Optional GitHub issue creation
- JSON and human-readable output

**Usage:**
```bash
python -m agents.run_skill visual_compliance.full_scan \
  --repo-path . \
  --fix \
  --create-issues \
  --json
```

## Skill Profiles

Predefined combinations of skills for common scenarios:

### fast_check
Quick manifest + directory validation for CI:
```bash
python -m agents.run_skill --profile fast_check --repo-path .
```

### full_compliance
Complete validation suite:
```bash
python -m agents.run_skill --profile full_compliance --repo-path .
```

### pr_review
Validation for PR checks (no auto-fix):
```bash
python -m agents.run_skill --profile pr_review --repo-path .
```

### weekly_audit
Full scan with GitHub issue creation:
```bash
python -m agents.run_skill --profile weekly_audit --repo-path .
```

## CLI Usage

### List Available Skills
```bash
# List all skills
python -m agents.run_skill --list

# Filter by tag
python -m agents.run_skill --list --tag fast-check

# List profiles
python -m agents.run_skill --list-profiles
```

### Execute Single Skill
```bash
# Run without auto-fix
python -m agents.run_skill odoo.manifest.validate --repo-path .

# Run with auto-fix
python -m agents.run_skill odoo.manifest.validate --repo-path . --fix

# JSON output
python -m agents.run_skill odoo.manifest.validate --repo-path . --json
```

### Execute Profile
```bash
# Run predefined profile
python -m agents.run_skill --profile fast_check --repo-path .

# Profile with auto-fix
python -m agents.run_skill --profile full_compliance --repo-path . --fix
```

### Get Skill Metadata
```bash
python -m agents.run_skill odoo.manifest.validate --info
```

## GitHub Actions Integration

### CI Workflow Example
```yaml
- name: Fast compliance check
  run: |
    python -m agents.run_skill --profile fast_check --repo-path .

- name: Full scan with auto-fix
  run: |
    python -m agents.run_skill visual_compliance.full_scan \
      --repo-path . \
      --fix \
      --json > results.json
```

### Existing Workflows
- `.github/workflows/visual-compliance-agent.yml` - Full compliance scan
- `.github/workflows/docs-validation.yml` - Documentation validation
- `.github/workflows/wiki-alignment.yml` - Wiki governance check

## Python API Usage

### Programmatic Skill Execution
```python
from agents.skill_registry import get_skill

# Get skill entrypoint
run_skill, meta = get_skill("odoo.manifest.validate")

# Execute skill
result = run_skill({
    "repo_path": ".",
    "fix": False
})

# Check results
if result["ok"]:
    print(f"✅ All {result['total_modules']} modules compliant")
else:
    print(f"❌ {len(result['violations'])} violations detected")
```

### Skill Result Schema
```python
{
    "ok": bool,                    # Overall compliance status
    "total_modules": int,          # Total modules checked
    "compliant_modules": int,      # Compliant module count
    "violations": [                # List of violations
        {
            "violation_type": str,
            "severity": str,       # CRITICAL, HIGH, MEDIUM, LOW
            "description": str,
            "module_name": str,
            "module_path": str,
            "auto_fixable": bool,
            "migration_complexity": str  # LOW, MEDIUM, HIGH
        }
    ]
}
```

## Development

### Adding a New Skill

1. **Define skill in `agents/skills.yaml`:**
```yaml
- id: odoo.new_validator.validate
  name: "New validator"
  description: "Validates new compliance requirement"
  module: "visual_compliance.validators.new_validator"
  entrypoint: "run_skill"
  tags: ["odoo", "oca", "compliance"]
  inputs:
    - name: "repo_path"
      type: "string"
      default: "."
  outputs:
    - name: "ok"
      type: "boolean"
```

2. **Create validator wrapper:**
```python
# agents/visual-compliance/src/visual_compliance/validators/new_validator.py

def run_skill(params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute new validation skill."""
    repo_path = Path(params.get("repo_path", "."))

    # Validation logic here

    return {
        "ok": is_compliant,
        "violations": violations,
    }
```

3. **Test skill:**
```bash
python -m agents.run_skill odoo.new_validator.validate --repo-path .
```

### Running Tests
```bash
# Unit tests
pytest agents/visual-compliance/tests/ -v

# Integration tests
python -m agents.run_skill --profile full_compliance --repo-path .
```

## Troubleshooting

### Skill Not Found
```bash
$ python -m agents.run_skill odoo.unknown.validate
Error: Skill 'odoo.unknown.validate' not found in registry.
Available skills: odoo.manifest.validate, odoo.directory.validate, ...
```

**Solution**: Check `agents/skills.yaml` for correct skill ID.

### Import Error
```bash
$ python -m agents.run_skill odoo.manifest.validate
ImportError: No module named 'visual_compliance'
```

**Solution**: Install dependencies or ensure Python path includes project root.

### Permission Denied
```bash
$ python -m agents.run_skill odoo.manifest.validate --fix
PermissionError: [Errno 13] Permission denied: '__manifest__.py'
```

**Solution**: Check file permissions or run with appropriate user.

## References

- [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- [Odoo 18.0 Documentation](https://www.odoo.com/documentation/18.0/)
- [InsightPulse Odoo Repository](https://github.com/jgtolentino/insightpulse-odoo)
- [GitHub Pages Documentation](https://jgtolentino.github.io/insightpulse-odoo/)

## License

LGPL-3 - See LICENSE file for details.

---

*Last updated: 2025-11-10 by Visual Compliance Agent*
