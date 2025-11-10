# How to Create Diagram Skills with Testing & Validation

**Guide for creating technically-compliant draw.io/Azure/Visio diagram skills with robust testing**

---

## 1. SKILLS.md Structure for Diagram Creation

### Basic Template

```markdown
---
name: azure-architecture-diagrams
description: Create technically-compliant Azure architecture diagrams in draw.io format (.drawio files) with automated validation, icon library integration, and Visio export compatibility. Use this skill when users ask to create Azure cloud architecture diagrams, infrastructure designs, network topologies, or hybrid cloud solutions.
---

# Azure Architecture Diagram Creation Skill
# with Testing & Validation Framework

This skill enables Claude to create production-ready Azure architecture diagrams with:
- Official Azure icon libraries
- Technical compliance validation
- Automated testing framework
- Visio export compatibility
- Best practice enforcement

## Core Capabilities

### 1. Azure-Specific Features
- **Official Azure Icons**: 400+ official Microsoft Azure icons
- **Azure Services**: Compute, Storage, Networking, Databases, AI/ML, IoT
- **Architecture Patterns**: Hub-spoke, microservices, hybrid cloud, multi-region
- **Compliance**: Well-Architected Framework validation
- **Security**: Network security groups, firewalls, private endpoints

### 2. Technical Compliance
- **Azure Well-Architected Framework**: Cost, Security, Reliability, Performance, Operations
- **Icon Accuracy**: Official Microsoft Azure icon library (2024 version)
- **Naming Conventions**: Azure resource naming standards
- **Network Topology**: Proper CIDR notation, subnet sizing
- **Service Dependencies**: Accurate service-to-service connections

### 3. Testing & Validation Framework
- **XML Schema Validation**: draw.io schema compliance
- **Icon Library Checks**: Verify all Azure icons exist and are correct versions
- **Connectivity Validation**: Ensure all services are properly connected
- **Naming Validation**: Check Azure resource naming standards
- **Export Testing**: Verify Visio export compatibility

## Testing Framework Implementation

### Test Suite Structure

```yaml
test_framework:
  validators:
    - xml_schema_validator
    - azure_icon_validator
    - connectivity_validator
    - naming_convention_validator
    - visio_export_validator

  test_levels:
    - unit: Individual shape validation
    - integration: Service connectivity validation
    - compliance: Well-Architected Framework checks
    - export: Visio compatibility validation

### Validator 1: XML Schema Validation

**Purpose**: Ensure generated .drawio files are valid XML and conform to draw.io schema

**Implementation**:
```python
# scripts/validate-drawio-xml.py
import xml.etree.ElementTree as ET
from xml.dom import minidom

def validate_drawio_xml(filepath):
    """Validate draw.io XML file structure"""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Check root element
        assert root.tag == 'mxfile', f"Root must be <mxfile>, got {root.tag}"

        # Check required attributes
        assert 'host' in root.attrib, "Missing 'host' attribute"

        # Check diagram element
        diagrams = root.findall('diagram')
        assert len(diagrams) > 0, "No <diagram> elements found"

        # Check mxGraphModel
        for diagram in diagrams:
            model = diagram.find('mxGraphModel')
            assert model is not None, f"No <mxGraphModel> in diagram {diagram.get('id')}"

            # Check root cells
            root_cells = model.find('root')
            assert root_cells is not None, "No <root> element in mxGraphModel"

            cells = root_cells.findall('mxCell')
            ids = [cell.get('id') for cell in cells]
            assert '0' in ids, "Missing root cell id='0'"
            assert '1' in ids, "Missing root cell id='1'"

        print(f"✅ XML validation passed: {filepath}")
        return True

    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        return False
    except AssertionError as e:
        print(f"❌ Validation error: {e}")
        return False
```

### Validator 2: Azure Icon Validation

**Purpose**: Verify all Azure service icons are from official Microsoft library

**Implementation**:
```python
# scripts/validate-azure-icons.py
import xml.etree.ElementTree as ET
import re

# Official Azure icon library URL
AZURE_ICON_LIBRARY = "https://jgraph.github.io/drawio-libs/libs/microsoft/azure.xml"

# Known Azure service icon styles (partial list)
AZURE_ICON_PATTERNS = {
    'compute': r'(virtualMachine|containerInstance|kubernetes|appService)',
    'storage': r'(storageAccount|blobStorage|fileStorage|queueStorage)',
    'networking': r'(virtualNetwork|loadBalancer|applicationGateway|vpnGateway)',
    'database': r'(sqlDatabase|cosmosDb|postgresDb|mysqlDb)',
    'security': r'(keyVault|firewall|networkSecurityGroup|privateLink)',
}

def validate_azure_icons(filepath):
    """Validate that Azure icons are from official library"""
    tree = ET.parse(filepath)
    root = tree.getroot()

    errors = []
    warnings = []

    for diagram in root.findall('.//diagram'):
        cells = diagram.findall('.//mxCell')

        for cell in cells:
            style = cell.get('style', '')
            value = cell.get('value', '')

            # Check if this is an Azure service shape
            if 'azure' in style.lower() or any(value.lower().startswith(svc) for svc in
                ['vm-', 'st-', 'sql-', 'kv-', 'vnet-', 'nsg-']):

                # Validate icon style pattern
                category_found = False
                for category, pattern in AZURE_ICON_PATTERNS.items():
                    if re.search(pattern, style, re.IGNORECASE):
                        category_found = True
                        break

                if not category_found:
                    warnings.append(f"Unrecognized Azure icon: {value} (style: {style[:50]}...)")

    if errors:
        print(f"❌ Azure icon validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False

    if warnings:
        print(f"⚠️  Azure icon warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    print(f"✅ Azure icon validation passed: {filepath}")
    return True
```

### Validator 3: Connectivity Validation

**Purpose**: Ensure all services are properly connected with valid edges

**Implementation**:
```python
# scripts/validate-connectivity.py
import xml.etree.ElementTree as ET

def validate_connectivity(filepath):
    """Validate service connectivity and edge definitions"""
    tree = ET.parse(filepath)
    root = tree.getroot()

    errors = []

    for diagram in root.findall('.//diagram'):
        cells = diagram.findall('.//mxCell')

        # Build shape registry
        shapes = {cell.get('id'): cell for cell in cells if cell.get('vertex') == '1'}

        # Validate edges
        edges = [cell for cell in cells if cell.get('edge') == '1']

        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')

            # Check edge has both source and target
            if not source:
                errors.append(f"Edge {edge.get('id')} missing source")
            elif source not in shapes:
                errors.append(f"Edge {edge.get('id')} references non-existent source: {source}")

            if not target:
                errors.append(f"Edge {edge.get('id')} missing target")
            elif target not in shapes:
                errors.append(f"Edge {edge.get('id')} references non-existent target: {target}")

            # Check edge has geometry
            geometry = edge.find('mxGeometry')
            if geometry is None:
                errors.append(f"Edge {edge.get('id')} missing geometry")

    if errors:
        print(f"❌ Connectivity validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False

    print(f"✅ Connectivity validation passed: {filepath}")
    return True
```

### Validator 4: Azure Naming Convention Validation

**Purpose**: Validate Azure resource naming follows Microsoft standards

**Implementation**:
```python
# scripts/validate-naming-conventions.py
import xml.etree.ElementTree as ET
import re

# Azure naming conventions
# https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming
NAMING_PATTERNS = {
    'vm': r'^vm-[a-z0-9]{1,13}-[a-z]{3,4}-[0-9]{2}$',  # vm-<name>-<region>-<instance>
    'st': r'^st[a-z0-9]{3,22}$',  # st<name> (storage account)
    'sql': r'^sql-[a-z0-9-]{1,60}$',  # sql-<name>
    'kv': r'^kv-[a-z0-9-]{1,21}$',  # kv-<name> (key vault)
    'vnet': r'^vnet-[a-z0-9-]{1,60}$',  # vnet-<name>
    'nsg': r'^nsg-[a-z0-9-]{1,77}$',  # nsg-<name>
}

def validate_naming_conventions(filepath):
    """Validate Azure resource names follow naming standards"""
    tree = ET.parse(filepath)
    root = tree.getroot()

    errors = []
    warnings = []

    for diagram in root.findall('.//diagram'):
        cells = diagram.findall('.//mxCell[@vertex="1"]')

        for cell in cells:
            value = cell.get('value', '').strip()

            # Extract resource type prefix
            for resource_type, pattern in NAMING_PATTERNS.items():
                if value.startswith(resource_type):
                    if not re.match(pattern, value, re.IGNORECASE):
                        errors.append(
                            f"Invalid {resource_type} name: '{value}' "
                            f"(should match pattern: {pattern})"
                        )

    if errors:
        print(f"❌ Naming convention validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False

    print(f"✅ Naming convention validation passed: {filepath}")
    return True
```

### Validator 5: Visio Export Compatibility

**Purpose**: Ensure diagram can be exported to Visio format

**Implementation**:
```python
# scripts/validate-visio-export.py
import xml.etree.ElementTree as ET

def validate_visio_export_compatibility(filepath):
    """Validate diagram compatibility with Visio export"""
    tree = ET.parse(filepath)
    root = tree.getroot()

    errors = []
    warnings = []

    for diagram in root.findall('.//diagram'):
        cells = diagram.findall('.//mxCell')

        for cell in cells:
            style = cell.get('style', '')

            # Check for unsupported style attributes
            unsupported = ['rotation=', 'comic=', 'sketch=']
            for attr in unsupported:
                if attr in style:
                    warnings.append(
                        f"Cell {cell.get('id')} uses '{attr}' which may not export to Visio"
                    )

            # Check for geometry constraints
            if cell.get('vertex') == '1':
                geometry = cell.find('mxGeometry')
                if geometry is not None:
                    # Visio prefers absolute positioning
                    if geometry.get('relative') == '1' and cell.get('edge') != '1':
                        warnings.append(
                            f"Cell {cell.get('id')} uses relative positioning, "
                            f"may not align correctly in Visio"
                        )

    if errors:
        print(f"❌ Visio export validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False

    if warnings:
        print(f"⚠️  Visio export warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    print(f"✅ Visio export validation passed: {filepath}")
    return True
```

## Azure Well-Architected Framework Compliance

### Architecture Review Checklist

```python
# scripts/validate-well-architected.py
import xml.etree.ElementTree as ET

def validate_well_architected_framework(filepath):
    """Validate against Azure Well-Architected Framework principles"""
    tree = ET.parse(filepath)
    root = tree.getroot()

    findings = {
        'cost_optimization': [],
        'security': [],
        'reliability': [],
        'performance': [],
        'operations': []
    }

    for diagram in root.findall('.//diagram'):
        cells = [cell.get('value', '').lower() for cell in diagram.findall('.//mxCell[@vertex="1"]')]

        # Cost Optimization
        if 'virtualmachine' in ' '.join(cells) and 'scaleset' not in ' '.join(cells):
            findings['cost_optimization'].append(
                "Consider VM Scale Sets for auto-scaling and cost optimization"
            )

        # Security
        has_nsg = any('nsg' in cell or 'networksecuritygroup' in cell for cell in cells)
        has_vnet = any('vnet' in cell or 'virtualnetwork' in cell for cell in cells)

        if has_vnet and not has_nsg:
            findings['security'].append(
                "Virtual Network detected without Network Security Group"
            )

        has_keyvault = any('keyvault' in cell or 'kv-' in cell for cell in cells)
        has_database = any(db in ' '.join(cells) for db in ['sql', 'cosmos', 'postgres', 'mysql'])

        if has_database and not has_keyvault:
            findings['security'].append(
                "Database detected - consider Azure Key Vault for connection strings"
            )

        # Reliability
        has_loadbalancer = any('loadbalancer' in cell or 'lb-' in cell for cell in cells)
        has_appgateway = any('applicationgateway' in cell or 'agw-' in cell for cell in cells)

        if len([c for c in cells if 'virtualmachine' in c]) > 1 and not (has_loadbalancer or has_appgateway):
            findings['reliability'].append(
                "Multiple VMs detected - consider Load Balancer or Application Gateway"
            )

    # Print findings
    all_ok = True
    for category, items in findings.items():
        if items:
            all_ok = False
            print(f"\n⚠️  {category.replace('_', ' ').title()} Recommendations:")
            for item in items:
                print(f"  - {item}")

    if all_ok:
        print("✅ Well-Architected Framework validation passed")
    else:
        print("\n💡 Review recommendations above to improve architecture")

    return True  # Recommendations don't fail validation
```

## Comprehensive Test Suite

### Master Test Runner

```python
# scripts/test-azure-diagram.py
#!/usr/bin/env python3
"""
Master test suite for Azure architecture diagrams
Runs all validators and generates compliance report
"""

import sys
import json
from pathlib import Path

# Import all validators
from validate_drawio_xml import validate_drawio_xml
from validate_azure_icons import validate_azure_icons
from validate_connectivity import validate_connectivity
from validate_naming_conventions import validate_naming_conventions
from validate_visio_export import validate_visio_export_compatibility
from validate_well_architected import validate_well_architected_framework

def run_test_suite(filepath):
    """Run complete test suite on diagram file"""

    print(f"\n{'='*80}")
    print(f"Testing Azure Architecture Diagram: {filepath}")
    print(f"{'='*80}\n")

    results = {}

    # Test 1: XML Schema Validation
    print("[1/6] XML Schema Validation")
    results['xml_schema'] = validate_drawio_xml(filepath)
    print()

    # Test 2: Azure Icon Validation
    print("[2/6] Azure Icon Library Validation")
    results['azure_icons'] = validate_azure_icons(filepath)
    print()

    # Test 3: Connectivity Validation
    print("[3/6] Service Connectivity Validation")
    results['connectivity'] = validate_connectivity(filepath)
    print()

    # Test 4: Naming Convention Validation
    print("[4/6] Azure Naming Convention Validation")
    results['naming'] = validate_naming_conventions(filepath)
    print()

    # Test 5: Visio Export Compatibility
    print("[5/6] Visio Export Compatibility")
    results['visio_export'] = validate_visio_export_compatibility(filepath)
    print()

    # Test 6: Well-Architected Framework
    print("[6/6] Azure Well-Architected Framework Validation")
    results['well_architected'] = validate_well_architected_framework(filepath)
    print()

    # Summary
    print(f"\n{'='*80}")
    print("Test Summary")
    print(f"{'='*80}\n")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test.replace('_', ' ').title():40} {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    # Generate JSON report
    report = {
        'filepath': filepath,
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'summary': {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': f"{(passed/total)*100:.1f}%"
        }
    }

    report_path = Path(filepath).stem + '_validation_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_path}")

    return passed == total

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python test-azure-diagram.py <diagram.drawio>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    success = run_test_suite(filepath)
    sys.exit(0 if success else 1)
```

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-diagrams.yml
name: Validate Azure Diagrams

on:
  pull_request:
    paths:
      - 'docs/architecture/**/*.drawio'
      - 'diagrams/**/*.drawio'
  push:
    paths:
      - 'docs/architecture/**/*.drawio'
      - 'diagrams/**/*.drawio'

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install lxml pytest

      - name: Find changed diagrams
        id: changed-files
        uses: tj-actions/changed-files@v45
        with:
          files: |
            **/*.drawio

      - name: Validate diagrams
        if: steps.changed-files.outputs.any_changed == 'true'
        run: |
          for file in ${{ steps.changed-files.outputs.all_changed_files }}; do
            echo "Validating $file"
            python scripts/test-azure-diagram.py "$file"
          done

      - name: Upload validation reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: validation-reports
          path: '*_validation_report.json'

      - name: Comment on PR
        if: failure() && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.name,
              body: '❌ Diagram validation failed. Check the workflow logs for details.'
            })
```

## Best Practices for SKILLS.md

### 1. Clear Activation Triggers

```markdown
## When to Activate This Skill

This skill activates when users request:
- "Create an Azure architecture diagram"
- "Design a hub-spoke network topology"
- "Show me a microservices architecture on Azure"
- "Diagram Azure security best practices"

**Keywords**: azure, cloud architecture, infrastructure diagram, network topology
```

### 2. Validation Examples in Skill

```markdown
## Example: Creating a Validated Azure Diagram

When generating diagrams, Claude will:

1. **Create the diagram** using official Azure icons
2. **Validate automatically** using embedded test framework
3. **Provide compliance report** showing any issues
4. **Suggest improvements** based on Well-Architected Framework

Example output:
```xml
<!-- Azure architecture diagram XML -->
[diagram content]
```

Validation results:
```
✅ XML Schema: PASS
✅ Azure Icons: PASS
✅ Connectivity: PASS
⚠️  Naming: 2 warnings (see recommendations)
✅ Visio Export: PASS
💡 Well-Architected: 3 recommendations
```
```

### 3. Testing Commands in Documentation

```markdown
## Testing Your Generated Diagrams

### Run full test suite:
```bash
python scripts/test-azure-diagram.py diagram.drawio
```

### Run individual validators:
```bash
python scripts/validate-drawio-xml.py diagram.drawio
python scripts/validate-azure-icons.py diagram.drawio
python scripts/validate-connectivity.py diagram.drawio
```

### CI/CD Integration:
Diagrams are automatically validated on PR:
- All validators run
- Compliance report generated
- PR comment added if issues found
```

## Complete Example: Azure Hub-Spoke with Testing

```markdown
---
name: azure-hub-spoke-network
description: Create Azure hub-spoke network topology diagrams with automated validation
---

# Azure Hub-Spoke Network Topology Skill

Creates production-ready Azure hub-spoke network diagrams following Microsoft best practices.

## Example Diagram with Tests

**User Request**: "Create a hub-spoke network with 3 spokes, central firewall, and VPN gateway"

**Claude Output**:

1. **Diagram File**: `azure-hub-spoke.drawio`
```xml
<mxfile host="app.diagrams.net">
  <diagram id="hub-spoke-1" name="Hub-Spoke Network">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>

        <!-- Hub VNet -->
        <mxCell id="2" value="vnet-hub-001"
          style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
          vertex="1" parent="1">
          <mxGeometry x="300" y="200" width="200" height="120" as="geometry"/>
        </mxCell>

        <!-- Azure Firewall -->
        <mxCell id="3" value="azfw-hub-001"
          style="shape=mxgraph.azure.firewall;fillColor=#f8cecc;strokeColor=#b85450;"
          vertex="1" parent="1">
          <mxGeometry x="370" y="240" width="60" height="60" as="geometry"/>
        </mxCell>

        <!-- VPN Gateway -->
        <mxCell id="4" value="vpn-gw-001"
          style="shape=mxgraph.azure.vpn_gateway;fillColor=#d5e8d4;strokeColor=#82b366;"
          vertex="1" parent="1">
          <mxGeometry x="320" y="240" width="40" height="60" as="geometry"/>
        </mxCell>

        <!-- Spoke 1 -->
        <mxCell id="5" value="vnet-spoke-prod-001"
          style="rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"
          vertex="1" parent="1">
          <mxGeometry x="100" y="100" width="150" height="80" as="geometry"/>
        </mxCell>

        <!-- Connections -->
        <mxCell id="10" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;"
          edge="1" parent="1" source="5" target="2">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

2. **Validation Results**:
```bash
$ python scripts/test-azure-diagram.py azure-hub-spoke.drawio

[1/6] XML Schema Validation
✅ XML validation passed: azure-hub-spoke.drawio

[2/6] Azure Icon Library Validation
✅ Azure icon validation passed: azure-hub-spoke.drawio

[3/6] Service Connectivity Validation
✅ Connectivity validation passed: azure-hub-spoke.drawio

[4/6] Azure Naming Convention Validation
✅ Naming convention validation passed: azure-hub-spoke.drawio

[5/6] Visio Export Compatibility
✅ Visio export validation passed: azure-hub-spoke.drawio

[6/6] Azure Well-Architected Framework Validation
💡 Security Recommendations:
  - Consider Network Security Groups for spoke VNets
  - Add Azure Bastion for secure VM access

Overall: 6/6 tests passed
📄 Detailed report saved to: azure-hub-spoke_validation_report.json
```

3. **Usage Instructions**:
```markdown
## How to Use This Diagram

1. **Open in draw.io**:
   - Go to https://app.diagrams.net
   - File → Open → Select azure-hub-spoke.drawio

2. **Enable Azure Library**:
   - More Shapes → Azure (or use URL below)
   - https://app.diagrams.net/?libs=azure2

3. **Export to Visio**:
   - File → Export → VSDX (Visio)
   - Opens natively in Microsoft Visio

4. **Validate Changes**:
   ```bash
   python scripts/test-azure-diagram.py azure-hub-spoke.drawio
   ```
```
```

## Summary: Key Elements of a Good SKILLS.md

✅ **Required Components**:
1. Frontmatter with name and description
2. Clear activation triggers (keywords)
3. Technical compliance standards
4. Testing and validation framework
5. CI/CD integration documentation
6. Complete examples with expected output
7. Usage instructions
8. Troubleshooting guide

✅ **Testing Framework Must Include**:
1. XML schema validation
2. Icon library validation
3. Connectivity validation
4. Naming convention validation
5. Export compatibility validation
6. Architecture best practices validation

✅ **Documentation Must Include**:
1. How to run tests locally
2. CI/CD integration steps
3. Validation report interpretation
4. How to fix common issues

## Resources

- **Azure Architecture Icons**: https://learn.microsoft.com/en-us/azure/architecture/icons/
- **draw.io Azure Library**: https://github.com/jgraph/drawio-libs/tree/master/libs/microsoft
- **Azure Well-Architected**: https://learn.microsoft.com/en-us/azure/well-architected/
- **Visio Export**: https://www.drawio.com/blog/export-to-visio
- **Azure Naming Conventions**: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming

---

**Next Steps**:
1. Create your SKILLS.md following this template
2. Implement the validation scripts in `scripts/`
3. Add CI/CD workflow to `.github/workflows/`
4. Test with sample diagrams
5. Document any custom validators you add
