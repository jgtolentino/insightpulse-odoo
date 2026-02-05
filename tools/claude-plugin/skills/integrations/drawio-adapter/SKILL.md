# Draw.io Adapter Skill

**Version:** 0.1.0
**Category:** Integrations
**Status:** Active
**Last Updated:** 2025-11-08

---

## Overview

The Draw.io Adapter skill enables agentic diagram generation, validation, and export for process mining and orchestration visualization. It provides seamless integration with SAP Process Intelligence for automatic process map creation.

### Key Capabilities

- **Diagram Creation**: Create `.drawio` diagrams from Mermaid, BPMN, JSON, and CSV
- **Validation**: Verify diagram structure, page count, layers, and style integrity
- **Export**: Export diagrams to PNG, SVG, and PDF formats
- **URL Encoding**: Generate shareable diagrams.net URLs
- **Auto-Generation**: Create process maps directly from SAP event traces

---

## Installation

### Prerequisites

- Python 3.11+
- Draw.io CLI (optional, for PDF/PNG export)
- lxml library for XML parsing

### Python Dependencies

```bash
cd skills/integrations/drawio-adapter
pip install -r requirements.txt
```

**requirements.txt:**
```
pydantic>=2.0.0
lxml>=4.9.0
```

### Install Draw.io CLI (Optional)

**macOS:**
```bash
brew install --cask drawio
ln -s /Applications/draw.io.app/Contents/MacOS/draw.io /usr/local/bin/drawio
```

**Linux:**
```bash
wget https://github.com/jgraph/drawio-desktop/releases/download/v21.0.0/drawio-amd64-21.0.0.deb
sudo dpkg -i drawio-amd64-21.0.0.deb
```

---

## Usage

### 1. Create Diagram from Mermaid

```python
from skills.integrations.drawio_adapter.drawio_adapter import DrawIOAdapter, CreateDiagramInput

adapter = DrawIOAdapter()

mermaid_content = """
graph TD
    A[Start] --> B[Process Step]
    B --> C{Decision}
    C -->|Yes| D[End Success]
    C -->|No| E[End Failure]
"""

input_data = CreateDiagramInput(
    source_format="mermaid",
    content=mermaid_content,
    filename="diagrams/my-process.drawio"
)

output = adapter.create_diagram(input_data)
print(f"Created: {output.file_path}")
```

### 2. Validate Diagram

```python
from skills.integrations.drawio_adapter.drawio_adapter import ValidateDiagramInput

validate_input = ValidateDiagramInput(
    file_path="diagrams/my-process.drawio",
    strict_mode=True
)

validation = adapter.validate_diagram(validate_input)

print(f"Valid: {validation.valid}")
print(f"Pages: {validation.details.pages}")
print(f"Shapes: {validation.details.total_shapes}")
print(f"Connections: {validation.details.total_connections}")

if validation.details.errors:
    print("Errors:")
    for error in validation.details.errors:
        print(f"  - {error}")
```

### 3. Export Diagram

```python
from skills.integrations.drawio_adapter.drawio_adapter import ExportDiagramInput

export_input = ExportDiagramInput(
    file_path="diagrams/my-process.drawio",
    format="png",
    page_index=0,
    scale=2.0  # 2x resolution
)

export_output = adapter.export_diagram(export_input)
print(f"Exported to: {export_output.export_path}")
```

### 4. Generate Sharing URL

```python
from skills.integrations.drawio_adapter.drawio_adapter import EncodeURLInput

url_input = EncodeURLInput(
    file_path="diagrams/my-process.drawio"
)

url_output = adapter.encode_url(url_input)
print(f"Share at: {url_output.encoded_url}")
```

---

## Makefile Commands

```bash
# Validate all diagrams
make drawio-validate

# Export diagram to PNG
make drawio-export FILE=diagrams/process.drawio FORMAT=png

# Encode for web sharing
make drawio-encode FILE=diagrams/process.drawio
```

---

## Templates

Pre-built templates are available in `skills/integrations/drawio-adapter/templates/`:

### 1. SAP-Odoo Orchestration Map

**File:** `sap-odoo-orchestration.drawio`

Shows the complete data flow from SAP S/4HANA through the SAP Executor Agent to Odoo ERP and Supabase storage.

**Usage:**
```bash
cp skills/integrations/drawio-adapter/templates/sap-odoo-orchestration.drawio diagrams/
```

### 2. Procure-to-Pay Process Map

**File:** `procure-to-pay-map.drawio`

Standard P2P process with:
- Purchase Requisition creation
- Approval workflow
- Purchase Order generation
- Goods Receipt
- Invoice matching
- Payment scheduling

**Features:**
- Color-coded activities by type
- Bottleneck annotations
- Exception handling paths
- Duration estimates

---

## Integration with SAP Process Intelligence

Auto-generate process maps from SAP event traces:

```python
from skills.integrations.sap_process_intelligence.sap_executor import SAPProcessIntelligence
from skills.integrations.sap_process_intelligence.models.sap_event_model import (
    ExtractEventsRequest,
    GenerateProcessMapRequest
)
from skills.integrations.drawio_adapter.drawio_adapter import DrawIOAdapter, CreateDiagramInput

# 1. Extract events from SAP
sap_engine = SAPProcessIntelligence()
events_request = ExtractEventsRequest(
    process_id="PO_4500012345",
    date_range="2025-01-01/2025-01-31"
)
events_response = sap_engine.extract_process_events(events_request)

# 2. Generate Mermaid process map
map_request = GenerateProcessMapRequest(
    events=events_response.events,
    output_format="mermaid"
)
map_response = sap_engine.generate_process_map(map_request)

# 3. Create Draw.io diagram
adapter = DrawIOAdapter()
diagram_input = CreateDiagramInput(
    source_format="mermaid",
    content=map_response.process_map,
    filename="diagrams/sap-po-analysis.drawio"
)
diagram_output = adapter.create_diagram(diagram_input)

# 4. Export to PNG for reporting
export_input = ExportDiagramInput(
    file_path=diagram_output.file_path,
    format="png",
    scale=2.0
)
export_output = adapter.export_diagram(export_input)

print(f"Process map exported: {export_output.export_path}")
```

---

## Data Models

### CreateDiagramInput

```python
class CreateDiagramInput(BaseModel):
    source_format: Literal["mermaid", "csv", "json", "bpmn"]
    content: str
    filename: str  # Must end with .drawio
    template: Optional[str] = None
```

### ValidationDetails

```python
class ValidationDetails(BaseModel):
    pages: int
    layers: List[str]
    errors: List[str]
    warnings: List[str]
    total_shapes: int
    total_connections: int
```

### ExportDiagramInput

```python
class ExportDiagramInput(BaseModel):
    file_path: str
    format: Literal["png", "svg", "pdf"]
    page_index: int = 0
    scale: float = 1.0
```

---

## CI/CD Integration

The Draw.io adapter includes GitHub Actions for automated validation:

**Workflow:** `.github/workflows/sap-spec-validate.yml`

```yaml
validate-drawio-diagrams:
  steps:
    - name: Validate diagrams
      run: make drawio-validate
```

---

## Best Practices

### Diagram Organization

```
diagrams/
├── process-maps/
│   ├── procure-to-pay.drawio
│   ├── order-to-cash.drawio
│   └── record-to-report.drawio
├── orchestration/
│   ├── sap-odoo-flow.drawio
│   └── agent-coordination.drawio
└── exports/
    ├── procure-to-pay.png
    └── sap-odoo-flow.pdf
```

### Naming Conventions

- Use kebab-case: `procure-to-pay.drawio`
- Include date for time-series: `p2p-analysis-2025-01.drawio`
- Prefix with system: `sap-procure-to-pay.drawio`

### Version Control

- Commit `.drawio` source files
- `.gitignore` exported PNG/PDF files (regenerate on demand)
- Use Pull Requests for diagram reviews

---

## Roadmap

### v0.2.0 (Q2 2025)
- [ ] BPMN 2.0 native import/export
- [ ] SVG optimization for web embedding
- [ ] Collaborative editing via WebSocket
- [ ] Diagram diff for version control

### v0.3.0 (Q3 2025)
- [ ] AI-powered layout optimization
- [ ] Template library expansion
- [ ] Real-time sync with diagrams.net
- [ ] Plugin system for custom shapes

---

## Troubleshooting

### Draw.io CLI Not Found

If export fails with "drawio command not found":

1. Verify installation: `which drawio`
2. Set path manually: `export DRAWIO_CLI_PATH=/path/to/drawio`
3. Or use placeholder export (creates text file)

### XML Parse Errors

If validation fails with XML errors:

1. Check file is valid XML: `xmllint diagrams/file.drawio`
2. Ensure file extension is `.drawio`
3. Verify file wasn't corrupted during transfer

---

## Support

**Documentation:** `skills/integrations/drawio-adapter/`
**Templates:** `skills/integrations/drawio-adapter/templates/`
**Examples:** `skills/integrations/drawio-adapter/examples/`

---

## License

Copyright © 2025 InsightPulse AI. All rights reserved.
