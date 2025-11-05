# DeepCode MCP Server - Usage Examples

**Interface-Agnostic:** Works with Claude Desktop, Claude Code, or any MCP client

---

## Quick Examples

### 1. BIR Tax Algorithm Generation

**In any Claude interface:**

```
Using the deepcode MCP server, generate a BIR Form 1601-C withholding tax computation algorithm.

Source: /Users/jake/Documents/BIR-Specs/1601C.pdf
Include: validation logic and test cases
Output: addons/custom/bir_compliance/models/

Framework: Odoo 19
```

**What DeepCode does:**
1. Reads the PDF specification
2. Extracts tax computation rules
3. Generates Python/Odoo code
4. Creates validation functions
5. Generates test cases
6. Adds integration guide

**Generated files:**
```
addons/custom/bir_compliance/models/
├── form_1601c_computation.py      # Main computation logic
├── form_1601c_validation.py       # Validation rules
├── form_1601c_odoo.py             # Odoo model integration
├── test_form_1601c.py             # Test cases
└── FORM_1601C_README.md           # Documentation
```

---

### 2. Finance SSC Dashboard (Full Stack)

**Frontend Generation:**

```
Create a Finance SSC dashboard frontend using deepcode_text2web:

Features:
- Multi-agency GL summary table
- Trial balance viewer with drill-down
- BIR form status tracker
- Real-time validation indicators
- Month-end closing checklist

Framework: React
Styling: Tailwind CSS
Output: ./finance-ssc-frontend/
```

**Backend Generation:**

```
Create a Finance SSC API backend using deepcode_text2backend:

Features:
- Multi-agency data isolation
- JWT authentication
- Real-time WebSocket updates
- GL data API endpoints
- BIR form status API
- Trial balance API

Framework: FastAPI
Database: Supabase
Output: ./finance-ssc-backend/
```

**Result:** Complete full-stack Finance SSC application ready to deploy!

---

### 3. OCR Optimization from Research

**Optimize PaddleOCR:**

```
Using deepcode_optimize_algorithm, optimize our PaddleOCR implementation:

Current implementation: infra/paddleocr/app/ocr_engine.py
Research query: "OCR optimization 2025 transformer"
Target hardware: RTX 4090 GPU
Metrics: speed, accuracy

Requirements:
- 50% speed improvement
- Maintain or improve accuracy
- Add batch processing
- Generate benchmarks
```

**What happens:**
1. DeepCode searches arXiv for latest papers
2. Analyzes papers for optimization techniques
3. Applies optimizations to your code
4. Generates GPU-accelerated version
5. Creates benchmark suite
6. Compares old vs new performance

---

### 4. Complete Odoo Module Generation

**Generate Expense OCR Module:**

```
Using deepcode_odoo_module, create a complete expense management module:

Module: expense_ocr
Description: "Expense report management with OCR integration"

Models:
- expense_report (header)
- expense_line (details)
- expense_receipt (attachments)

Views:
- kanban (for report overview)
- tree (for list view)
- form (for detail entry)
- calendar (for submission dates)

Features:
- OCR integration with PaddleOCR
- Multi-level approval workflow
- GL posting integration
- Email notifications
- Receipt scanning

Output: addons/custom/expense_ocr/
```

**Generated module structure:**
```
addons/custom/expense_ocr/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── expense_report.py
│   ├── expense_line.py
│   └── expense_receipt.py
├── views/
│   ├── expense_report_kanban_view.xml
│   ├── expense_report_tree_view.xml
│   ├── expense_report_form_view.xml
│   ├── expense_line_tree_view.xml
│   └── expense_receipt_form_view.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── mail_templates.xml
└── README.md
```

---

### 5. Workflow Execution

**BIR Full Compliance Workflow:**

```
Execute the "bir_full_compliance" workflow to generate all BIR form algorithms:

Forms to generate:
- Form 1601-C (Monthly Withholding)
- Form 2550-Q (Quarterly VAT)
- Form 1702-RT (Annual Income Tax)

All with:
- Computation logic
- Validation rules
- Test cases
- Odoo integration

Output: addons/custom/bir_compliance/models/
```

**What the workflow does:**
1. Generates Form 1601-C algorithm
2. Generates Form 2550-Q algorithm
3. Generates Form 1702-RT algorithm
4. Creates unified Odoo module
5. Generates comprehensive tests
6. Creates integration documentation

---

## Advanced Examples

### 6. Paper2Code for Algorithm Implementation

**Implement algorithm from arXiv paper:**

```
Generate production code from this OCR research paper:

Paper: https://arxiv.org/abs/2109.03144
Type: algorithm
Framework: generic Python
Optimizations: gpu, batch, rtx4090

Output: ./ocr-optimizations/

Requirements:
- Extract the core algorithm
- Implement in Python
- Add GPU acceleration
- Include benchmarking code
- Generate documentation
```

### 7. Multi-Agency Dashboard with Real-time Updates

```
Create a multi-agency Finance SSC dashboard:

Backend (deepcode_text2backend):
- FastAPI with WebSocket support
- Supabase for data storage
- Multi-tenancy (8 agencies)
- Real-time GL updates
- JWT authentication

Frontend (deepcode_text2web):
- React with real-time subscriptions
- Tailwind CSS for styling
- Multi-agency selector
- Real-time GL balance updates
- BIR form status indicators

Output:
- Backend: ./finance-ssc-backend/
- Frontend: ./finance-ssc-frontend/
```

### 8. BIR Algorithm with Custom Validation

```
Generate BIR Form 1601-C with custom validation rules:

Spec source: /Users/jake/BIR-Specs/1601C.pdf
BIR form: 1601c

Custom validation rules:
- TIN format: XXX-XXX-XXX-XXX
- Amount limits: 0 to 999,999,999.99
- Period validation: 2020-2030
- Zero-amount rejection
- Duplicate transaction detection

Include:
- Comprehensive validation
- Test cases for each rule
- Error message localization
- Validation report generation

Output: addons/custom/bir_compliance/models/
```

---

## Integration Examples

### 9. Notion → DeepCode → Odoo Pipeline

**Workflow:**
1. Store BIR specification in Notion
2. Fetch from Notion using Notion MCP
3. Generate algorithm using DeepCode
4. Create Odoo module
5. Update Notion with implementation status

**Claude prompt:**
```
1. Fetch the BIR Form 1601-C specification from Notion page ID 12345
2. Use deepcode_bir_algorithm to generate the implementation
3. Create an Odoo module in addons/custom/bir_compliance/
4. Update the Notion page with "Status: Implemented" and the module path
```

### 10. Continuous Algorithm Update

**Automated research monitoring:**
```
Set up a workflow to continuously monitor and implement algorithm improvements:

1. Monitor arXiv for "OCR optimization" papers (monthly)
2. When new paper found:
   - Use deepcode_paper2code to implement
   - Generate benchmarks
   - If performance improves by >10%:
     - Deploy to staging
     - Run integration tests
     - Create PR for review

Current implementation: infra/paddleocr/app/ocr_engine.py
Target metrics: speed +50%, accuracy +5%
```

---

## Interface-Specific Examples

### Claude Desktop

```
# Just type naturally:
"Generate a BIR Form 1601-C algorithm from the spec at ~/Documents/BIR/1601C.pdf"

# Or be specific:
"Using deepcode_bir_algorithm, generate Form 1601-C with validation and tests.
Output to addons/custom/bir_compliance/models/"
```

### Claude Code

```
# Same natural language:
"Create a React dashboard for Finance SSC with Tailwind CSS"

# Or use tool directly:
"Use deepcode_text2web to generate a Finance SSC dashboard.
Framework: React
Styling: Tailwind
Features: GL summary, trial balance, BIR status
Output: ./finance-ssc-frontend/"
```

### Any MCP Client

All examples work the same way in any MCP-compatible client!

---

## Batch Operations

### 11. Generate All BIR Forms at Once

```
Generate all Philippine BIR forms for our Finance SSC:

Forms:
- 0605 (Withholding Tax Remittance)
- 1600 (Monthly Remittance Return)
- 1601-C (Monthly Remittance)
- 1601-E (Quarterly Remittance)
- 1602 (Monthly Final Withholding)
- 2550-Q (Quarterly VAT)
- 2551-Q (Quarterly Percentage Tax)
- 1702-RT (Annual Income Tax)

Specs directory: ~/Documents/BIR-Specs/
Output: addons/custom/bir_compliance/models/

For each form:
- Generate computation logic
- Generate validation rules
- Generate test cases
- Create Odoo integration

Execute as workflow: bir_full_compliance
```

---

## Tips & Best Practices

### 1. Always Provide Context
```
✅ Good: "Generate BIR Form 1601-C algorithm from spec at ~/BIR/1601C.pdf for Odoo 19"
❌ Bad: "Generate BIR form"
```

### 2. Specify Output Paths
```
✅ Good: "Output to addons/custom/bir_compliance/models/"
❌ Bad: "Generate somewhere"
```

### 3. Include Requirements
```
✅ Good: "Include validation logic, test cases, and Odoo integration"
❌ Bad: "Generate the code"
```

### 4. Reference Framework Versions
```
✅ Good: "FastAPI 0.104+ with Supabase 2.0"
❌ Bad: "Use FastAPI"
```

---

## Next Steps

1. **Try the examples** - Start with simple ones
2. **Review generated code** - Always validate before using
3. **Run tests** - Generated tests help ensure correctness
4. **Customize** - Adapt examples to your needs
5. **Share feedback** - Help improve DeepCode integration

---

**Documentation:**
- Main README: [README.md](./README.md)
- Installation: [install.sh](./install.sh)
- Configuration: [config/](./config/)

**Support:**
- GitHub: https://github.com/jgtolentino/insightpulse-odoo/issues
- Team: finance-ssc@insightpulse.ai
