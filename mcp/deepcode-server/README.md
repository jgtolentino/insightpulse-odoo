# DeepCode MCP Server

**Paper2Code + Text2Web + Text2Backend Integration for InsightPulse AI**

## Overview

This MCP server integrates DeepCode's capabilities into your Claude Code workflow, enabling:
- 📄 **Paper2Code**: Convert research papers → production code
- 💬 **Text2Web**: Generate frontend applications from descriptions
- 🗄️ **Text2Backend**: Build backend systems from requirements
- 🔄 **Odoo Integration**: Seamless module generation
- 🧾 **BIR Automation**: Tax algorithm implementation from specs

## Features

### 1. Paper2Code Operations
- Convert research papers to production code
- Support for arXiv, HuggingFace Papers, PDF files
- Automatic test generation
- Documentation creation
- Integration with Odoo models

### 2. Text2Web Operations
- Generate React/Vue/Svelte applications
- Tailwind CSS styling
- Component-based architecture
- API integration scaffolding

### 3. Text2Backend Operations
- FastAPI/Django backends
- Database models (PostgreSQL, Supabase)
- Authentication (JWT, OAuth)
- REST/GraphQL APIs

### 4. BIR-Specific Tools
- BIR form algorithm generation
- Tax computation engines
- Validation logic
- Compliance checking

## Installation

### Prerequisites

```bash
# Install DeepCode
pip install deepcode-hku

# Install dependencies
pip install anthropic mcp httpx aiohttp
```

### Configuration

1. Copy configuration templates:
```bash
cp config/deepcode.config.yaml.example config/deepcode.config.yaml
cp config/deepcode.secrets.yaml.example config/deepcode.secrets.yaml
```

2. Update `config/deepcode.secrets.yaml`:
```yaml
anthropic:
  api_key: "your-claude-api-key"

openai:
  api_key: "your-openai-key"  # Optional

supabase:
  url: "your-supabase-url"
  key: "your-supabase-key"
```

## Usage with Claude Desktop

### Add to Claude Desktop Config

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "deepcode": {
      "command": "python",
      "args": ["-m", "mcp.deepcode-server.src.server"],
      "env": {
        "PYTHONPATH": "/home/user/insightpulse-odoo",
        "WORKSPACE_DIR": "/home/user/insightpulse-odoo",
        "CONFIG_PATH": "/home/user/insightpulse-odoo/mcp/deepcode-server/config"
      }
    }
  }
}
```

### Available Tools

#### 1. `deepcode_paper2code`
Generate production code from research papers.

**Parameters:**
- `paper_source`: URL or path to paper (arXiv, HuggingFace, local PDF)
- `output_type`: "algorithm" | "model" | "full_module"
- `target_framework`: "odoo" | "fastapi" | "django" | "generic"
- `optimizations`: List of optimization flags
- `output_path`: Where to save generated code

**Example:**
```
Generate BIR tax computation algorithm from the official BIR Form 1601-C specification PDF at /Users/jake/Documents/BIR-1601C-Spec.pdf. Output as an Odoo model to addons/custom/bir_compliance/models/
```

#### 2. `deepcode_text2web`
Generate frontend applications from natural language.

**Parameters:**
- `description`: Natural language description of the app
- `framework`: "react" | "vue" | "svelte"
- `styling`: "tailwind" | "bootstrap" | "material-ui"
- `features`: List of required features
- `output_path`: Where to save generated code

**Example:**
```
Create a Finance SSC dashboard with multi-agency GL summary table, trial balance viewer, BIR form status tracker, and real-time validation indicators. Use React with Tailwind CSS.
```

#### 3. `deepcode_text2backend`
Generate backend systems from requirements.

**Parameters:**
- `requirements`: Natural language description or structured spec
- `framework`: "fastapi" | "django" | "flask"
- `database`: "postgresql" | "supabase" | "mongodb"
- `features`: List of required features
- `output_path`: Where to save generated code

**Example:**
```
Build a travel & expense management backend with FastAPI and Supabase. Include travel request workflow, expense report with OCR, multi-level approval chain, GL posting integration, and email notifications.
```

#### 4. `deepcode_bir_algorithm`
Generate BIR tax algorithms from specifications.

**Parameters:**
- `bir_form`: Form identifier (e.g., "1601c", "2550q", "1702rt")
- `spec_source`: Path to specification document
- `include_validation`: Boolean - include validation logic
- `include_tests`: Boolean - generate test cases
- `output_path`: Where to save generated code

**Example:**
```
Generate BIR Form 1601-C withholding tax computation algorithm with validation and tests. Output to addons/custom/bir_compliance/models/form_1601c.py
```

#### 5. `deepcode_odoo_module`
Generate complete Odoo module with frontend and backend.

**Parameters:**
- `module_name`: Name of the Odoo module
- `description`: What the module should do
- `models`: List of required models
- `views`: List of required views
- `features`: Additional features
- `output_path`: Where to save the module

**Example:**
```
Create an Odoo module called "expense_ocr" for expense report management with OCR integration. Include models for expense reports, expense lines, and receipts. Add kanban, tree, and form views. Integrate with PaddleOCR for receipt scanning.
```

#### 6. `deepcode_optimize_algorithm`
Optimize existing algorithms from latest research.

**Parameters:**
- `algorithm_path`: Path to current algorithm
- `research_query`: What to search for (e.g., "OCR optimization 2025")
- `target_hardware`: "cpu" | "gpu" | "rtx4090" | "tpu"
- `metrics`: Performance metrics to optimize

**Example:**
```
Optimize the PaddleOCR implementation at infra/paddleocr/app/ocr_engine.py using latest OCR research. Target RTX 4090 GPU. Optimize for speed and accuracy.
```

#### 7. `deepcode_workflow`
Execute multi-step DeepCode workflows.

**Parameters:**
- `workflow_name`: "bir_full_compliance" | "finance_dashboard" | "ocr_pipeline" | "custom"
- `workflow_spec`: Workflow definition (for custom workflows)
- `parameters`: Workflow-specific parameters

**Example:**
```
Execute the "bir_full_compliance" workflow to generate all BIR form algorithms for Forms 1601-C, 2550-Q, and 1702-RT.
```

## Workflows

### Pre-defined Workflows

#### 1. BIR Full Compliance
```yaml
workflow: bir_full_compliance
steps:
  - Generate Form 1601-C algorithm
  - Generate Form 2550-Q algorithm
  - Generate Form 1702-RT algorithm
  - Create Odoo BIR compliance module
  - Generate test cases
  - Create documentation
```

#### 2. Finance SSC Dashboard
```yaml
workflow: finance_dashboard
steps:
  - Generate backend API (FastAPI)
  - Generate frontend (React + Tailwind)
  - Create database models (Supabase)
  - Integrate with Odoo
  - Deploy configuration
```

#### 3. OCR Optimization Pipeline
```yaml
workflow: ocr_pipeline
steps:
  - Search latest OCR papers
  - Generate optimized implementation
  - Benchmark against current
  - Deploy if better
  - Update documentation
```

## Integration with Existing Tools

### With Notion MCP
```python
# Store specs in Notion, generate with DeepCode
1. Fetch BIR spec from Notion database
2. Use deepcode_paper2code to generate algorithm
3. Update Notion with implementation status
```

### With Supabase MCP
```python
# Store generated code and metadata
1. Generate code with DeepCode
2. Store in Supabase with metadata
3. Track version history
```

### With Odoo Automation
```bash
# Seamless integration with your automation pipeline
odoo-search "OCR optimization" | \
  deepcode-generate --type algorithm | \
  odoo-create-module | \
  odoo-cursor
```

## Examples

### Example 1: BIR Tax Algorithm

**Prompt to Claude:**
```
Using the deepcode MCP server, generate a BIR Form 1601-C withholding tax computation algorithm from the specification document at /Users/jake/Documents/BIR-Specs/1601C.pdf.

Requirements:
- Output as Odoo model
- Include validation logic
- Generate test cases
- Add documentation
- Save to addons/custom/bir_compliance/models/form_1601c.py
```

**What happens:**
1. DeepCode reads the PDF specification
2. Analyzes tax computation logic
3. Generates Python/Odoo code
4. Creates validation functions
5. Generates test cases
6. Adds comprehensive documentation
7. Saves to specified path

### Example 2: Finance Dashboard

**Prompt to Claude:**
```
Create a complete Finance SSC dashboard using deepcode:

Frontend:
- React with Tailwind CSS
- Multi-agency GL summary table
- Trial balance viewer with drill-down
- BIR form status tracker
- Real-time validation indicators

Backend:
- FastAPI with Supabase
- Multi-tenancy support
- JWT authentication
- WebSocket for real-time updates

Save frontend to ./finance-ssc-frontend/
Save backend to ./finance-ssc-backend/
```

**What happens:**
1. DeepCode generates React components
2. Creates API endpoints with FastAPI
3. Sets up Supabase schema
4. Implements authentication
5. Adds WebSocket support
6. Creates deployment configs
7. Generates documentation

### Example 3: OCR Optimization

**Prompt to Claude:**
```
Optimize our PaddleOCR implementation using the latest research:

Current: infra/paddleocr/app/ocr_engine.py
Target: RTX 4090 GPU
Search: "OCR optimization 2025 transformer"

Requirements:
- Maintain accuracy
- Improve speed by 50%
- Add batch processing
- Generate benchmarks
```

**What happens:**
1. DeepCode searches arXiv for latest papers
2. Analyzes current implementation
3. Generates optimized version
4. Adds GPU acceleration
5. Implements batch processing
6. Creates benchmark suite
7. Compares performance

## Best Practices

### 1. Specification Quality
- Provide detailed specifications
- Include examples and edge cases
- Reference official documentation
- Add context about use case

### 2. Output Validation
- Always review generated code
- Run tests before deploying
- Check for security issues
- Validate against requirements

### 3. Iterative Improvement
- Start with basic implementation
- Test and validate
- Use deepcode_optimize_algorithm for improvements
- Document changes

### 4. Version Control
- Commit generated code
- Tag releases
- Track changes
- Document generation parameters

## Troubleshooting

### Issue: Paper parsing fails
**Solution:**
- Ensure PDF is text-based (not scanned image)
- Try providing paper abstract separately
- Use OCR for scanned documents

### Issue: Generated code doesn't match expectations
**Solution:**
- Provide more detailed specifications
- Include examples in prompt
- Specify exact framework versions
- Review DeepCode logs

### Issue: Integration with Odoo fails
**Solution:**
- Check Odoo version compatibility
- Verify module structure
- Test models independently
- Review access rights

## Development

### Running Tests
```bash
pytest tests/
```

### Adding Custom Workflows
Create workflow definition in `workflows/`:

```yaml
# workflows/custom_workflow.yaml
name: "custom_workflow"
description: "Description of workflow"
steps:
  - name: "Step 1"
    tool: "deepcode_paper2code"
    parameters:
      paper_source: "{{input.paper_url}}"
      output_type: "algorithm"

  - name: "Step 2"
    tool: "deepcode_odoo_module"
    parameters:
      module_name: "{{input.module_name}}"
      models: ["{{step1.output}}"]
```

## Resources

- **DeepCode GitHub:** https://github.com/HKUDS/DeepCode
- **Research Paper:** https://huggingface.co/papers/2504.17192
- **MCP Specification:** https://modelcontextprotocol.io
- **InsightPulse AI:** https://github.com/jgtolentino/insightpulse-odoo

## Support

For issues or questions:
- GitHub Issues: https://github.com/jgtolentino/insightpulse-odoo/issues
- Documentation: /docs/
- Team: finance-ssc@insightpulse.ai

---

**Last Updated:** 2025-11-05
**Version:** 1.0.0
