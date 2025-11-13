# IPAI Agentic Document Extraction Service Specification

**Version:** 1.0
**Date:** 2025-11-13
**Status:** Design Phase
**Owner:** InsightPulse AI Engineering Team
**Inspired By:** LandingAI's vision-agent, agentic-doc, and vision-agent-mcp repositories

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Architecture Mapping: LandingAI → InsightPulse AI](#architecture-mapping-landingai--insightpulse-ai)
3. [Service Architecture](#service-architecture)
4. [API Specification](#api-specification)
5. [MCP Server Tools](#mcp-server-tools)
6. [Supabase Schema](#supabase-schema)
7. [Integration Points](#integration-points)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Production Readiness](#production-readiness)

---

## EXECUTIVE SUMMARY

### What This Is

The **IPAI Agentic Document Extraction Service** (`ipai-agentic-doc`) is a production-grade document understanding and extraction system that brings LandingAI's proven patterns to InsightPulse AI's Finance Shared Service Center (SSC) architecture.

### Key Capabilities

1. **Agentic Document Extraction (ADE)**
   - Complex document understanding (invoices, receipts, contracts, forms)
   - Table/form extraction with spatial understanding
   - DocVQA-style natural language queries over documents
   - Multi-page PDF processing with auto-splitting

2. **Vision Agent Integration**
   - See → Reason → Act workflow for visual documents
   - Self-correcting extraction with confidence scoring
   - Code-generation-first approach for custom extraction logic

3. **MCP Protocol Support**
   - Expose document tools to Claude Code and other LLM clients
   - Proxy pattern: MCP calls → REST API → Document processing
   - Integration with existing Codex CLI workflow

### Why This Matters

**Current State:**
- Basic OCR extraction with PaddleOCR (~97% confidence)
- Manual field mapping from OCR JSON
- Limited to simple receipt extraction
- No semantic understanding or reasoning

**Future State with ipai-agentic-doc:**
- Intelligent document understanding (not just OCR)
- Natural language queries: "What's the total amount excluding VAT?"
- Complex table extraction from financial statements
- Self-correcting with test-driven validation
- Seamless integration with Odoo ERP + Scout/Concur workflows

---

## ARCHITECTURE MAPPING: LandingAI → InsightPulse AI

### Pattern 1: Vision Agent → Document Understanding Agent

| LandingAI Vision Agent | InsightPulse AI Implementation |
|------------------------|-------------------------------|
| **See:** Image input → VLM processing | PaddleOCR-VL 900M + Claude Sonnet 4.5 (vision) |
| **Reason:** Task decomposition, plan generation | LLM-based reasoning over OCR output + bounding boxes |
| **Act:** Code generation + test validation | Generate Python extraction code, validate with test cases |
| **Tools:** `florence2_object_detection`, `extract_frames` | `extract_receipt_fields`, `classify_document_type`, `answer_docvqa` |
| **Output:** Ready-to-run Python code | Structured JSON + Pydantic models + confidence scores |

### Pattern 2: Agentic Doc → Document Extraction Pipeline

| LandingAI Agentic Doc | InsightPulse AI Implementation |
|----------------------|-------------------------------|
| **Input Handling:** PDF, images, URLs, bytes | PDF, images, Odoo attachments, Supabase Storage URLs |
| **Large Document Splitting:** Auto-split 1000+ page PDFs | Split at 50 pages, parallel process, stitch results |
| **Parallel Processing:** Thread-pool with configurable workers | Supabase Edge Functions with parallelism |
| **Extraction Model:** Pydantic BaseModel with confidence | Pydantic + BIR-specific schemas (Form 2307, 1601C) |
| **Batch Processing:** Multiple files, exponential backoff | Batch API for Scout/Concur expense report ingestion |
| **Visualization:** Bounding boxes, grounding images | Overlay on original receipt/invoice in Odoo |
| **Connectors:** Google Drive, S3, local | Supabase Storage, Odoo attachments, DigitalOcean Spaces |

### Pattern 3: Vision Agent MCP → Document MCP Server

| LandingAI Vision Agent MCP | InsightPulse AI Implementation |
|---------------------------|-------------------------------|
| **Proxy Pattern:** MCP → REST API (Landing AI) | MCP → REST API (ipai-agentic-doc service) |
| **Tool Definition Generation:** From OpenAPI spec | Generate from FastAPI auto-docs |
| **File Processing:** Base64 encoding for multipart | Base64 + Supabase Storage signed URLs |
| **HTTP Layer:** Axios with auth headers | Python `httpx` with Supabase service key |
| **Visualization:** Save PNG overlays to `OUTPUT_DIRECTORY` | Save to Supabase Storage, link in Odoo |
| **Error Handling:** MCP-compliant error codes | `-32602` (validation), `-32000` (network), `-32603` (internal) |

---

## SERVICE ARCHITECTURE

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ Codex CLI    │  │ Odoo ERP     │  │ Mobile App   │                  │
│  │ + Claude Code│  │ Web UI       │  │ (Future)     │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
└─────────┼──────────────────┼──────────────────┼──────────────────────────┘
          │                  │                  │
          │ MCP Protocol     │ REST API         │ REST API
          │                  │                  │
┌─────────┼──────────────────┼──────────────────┼──────────────────────────┐
│         │         IPAI AGENTIC DOC SERVICE                               │
│  ┌──────▼──────────────────▼──────────────────▼───────┐                 │
│  │  MCP Server         │  REST API Gateway             │                 │
│  │  (stdio transport)  │  (FastAPI)                    │                 │
│  └──────┬──────────────┴────────┬──────────────────────┘                 │
│         │                       │                                         │
│         └───────────┬───────────┘                                         │
│                     │                                                     │
│  ┌──────────────────▼──────────────────────────────────────┐             │
│  │           DOCUMENT UNDERSTANDING ENGINE                 │             │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────┐  │             │
│  │  │ Vision Agent   │  │ DocVQA Engine  │  │ ADE      │  │             │
│  │  │ (See→Reason→   │  │ (LLM + OCR)    │  │ Pipeline │  │             │
│  │  │  Act)          │  │                │  │          │  │             │
│  │  └────────┬───────┘  └────────┬───────┘  └────┬─────┘  │             │
│  └───────────┼──────────────────┬─┼───────────────┼────────┘             │
│              │                  │ │               │                      │
│              │ Uses tools       │ │ Queries       │ Extracts             │
│              │                  │ │               │                      │
│  ┌───────────▼──────────────────▼─▼───────────────▼────────┐             │
│  │                 TOOL LIBRARY                             │             │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │             │
│  │  │ OCR Tool     │  │ Field Extract│  │ Doc Classify │  │             │
│  │  │ (PaddleOCR)  │  │ (Pydantic)   │  │ (ML)         │  │             │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │             │
│  └──────────────────────────────────────────────────────────┘             │
└─────────────────────────────┬───────────────────────────────────────────┘
                              │
                              │ Reads/Writes
                              │
┌─────────────────────────────▼───────────────────────────────────────────┐
│                       DATA LAYER                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ Supabase     │  │ Odoo ERP     │  │ DigitalOcean │                  │
│  │ PostgreSQL   │  │ Database     │  │ Spaces       │                  │
│  │              │  │              │  │ (S3)         │                  │
│  │ - Document   │  │ - OCR        │  │ - Document   │                  │
│  │   metadata   │  │   receipts   │  │   originals  │                  │
│  │ - Extraction │  │ - Expenses   │  │ - Grounding  │                  │
│  │   history    │  │ - Invoices   │  │   images     │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. MCP Server (Python)
- **Purpose:** Expose document tools to Claude Code via MCP protocol
- **Transport:** STDIO (launched by Claude Code)
- **Tools Exposed:**
  - `extract_fields_from_invoice`
  - `classify_document_type`
  - `answer_question_about_document`
  - `extract_table_from_pdf`
  - `validate_bir_form`
- **Implementation:** Python MCP SDK or FastMCP

#### 2. REST API Gateway (FastAPI)
- **Purpose:** HTTP interface for Odoo, mobile apps, batch jobs
- **Endpoints:**
  - `POST /v1/documents/extract` - Single document extraction
  - `POST /v1/documents/batch` - Batch document processing
  - `POST /v1/documents/query` - DocVQA queries
  - `GET /v1/documents/{id}` - Retrieve extraction result
  - `GET /v1/documents/{id}/visualization` - Get grounding image
- **Authentication:** Supabase JWT + API keys

#### 3. Document Understanding Engine
- **Vision Agent Module:**
  - See: Image → OCR + bounding boxes
  - Reason: LLM analyzes structure, identifies fields
  - Act: Generates extraction code, validates with tests
- **DocVQA Engine:**
  - Natural language questions over documents
  - Example: "What's the total amount before tax?"
  - Uses Claude Sonnet 4.5 vision + OCR grounding
- **ADE Pipeline:**
  - Large document splitting (50 pages/chunk)
  - Parallel processing with stitching
  - Pydantic schema validation

#### 4. Tool Library
- **OCR Tool:** PaddleOCR-VL 900M (existing)
- **Field Extractor:** Pydantic models + regex + LLM
- **Document Classifier:** ML model (invoice, receipt, contract, form)
- **Table Extractor:** Spatial analysis + row/column detection
- **BIR Validator:** Philippine tax form validation logic

---

## API SPECIFICATION

### Endpoint: Extract Fields from Document

```http
POST /v1/documents/extract
Content-Type: multipart/form-data
Authorization: Bearer {supabase_jwt}
```

**Request:**
```python
{
  "file": <binary>,  # PDF or image
  "document_type": "invoice" | "receipt" | "contract" | "form",
  "extraction_schema": "bir_2307" | "bir_1601c" | "generic_invoice" | "custom",
  "custom_fields": [  # Optional: for custom extraction
    {
      "name": "total_amount",
      "type": "currency",
      "description": "Total amount including tax"
    }
  ],
  "options": {
    "enable_docvqa": true,
    "generate_visualization": true,
    "confidence_threshold": 0.85
  }
}
```

**Response (200 OK):**
```json
{
  "document_id": "doc_abc123",
  "document_type": "invoice",
  "confidence": 0.97,
  "extracted_fields": {
    "merchant_name": {
      "value": "ABC Corporation",
      "confidence": 0.99,
      "bbox": [100, 50, 300, 80]
    },
    "total_amount": {
      "value": 12500.00,
      "confidence": 0.98,
      "bbox": [400, 500, 500, 520]
    },
    "date": {
      "value": "2025-11-13",
      "confidence": 0.95,
      "bbox": [100, 100, 200, 120]
    },
    "tin": {
      "value": "123-456-789-000",
      "confidence": 0.97,
      "bbox": [100, 120, 250, 140]
    }
  },
  "tables": [
    {
      "name": "line_items",
      "headers": ["Description", "Quantity", "Unit Price", "Amount"],
      "rows": [
        ["Widget A", "10", "1000.00", "10000.00"],
        ["Widget B", "5", "500.00", "2500.00"]
      ],
      "bbox": [50, 200, 550, 450]
    }
  ],
  "visualization_url": "https://spdtwktxdalcfigzeqrz.supabase.co/storage/v1/object/public/groundings/doc_abc123.png",
  "processing_time_ms": 2450,
  "metadata": {
    "ocr_engine": "paddleocr-vl-900m",
    "llm_model": "claude-sonnet-4.5",
    "page_count": 1
  }
}
```

**Error Responses:**
- `400` - Invalid document format or schema
- `422` - Extraction confidence below threshold
- `500` - Internal processing error

---

### Endpoint: DocVQA Query

```http
POST /v1/documents/query
Content-Type: application/json
Authorization: Bearer {supabase_jwt}
```

**Request:**
```json
{
  "document_id": "doc_abc123",
  "questions": [
    "What is the total amount excluding VAT?",
    "Who is the supplier?",
    "What is the payment due date?"
  ]
}
```

**Response (200 OK):**
```json
{
  "document_id": "doc_abc123",
  "answers": [
    {
      "question": "What is the total amount excluding VAT?",
      "answer": "11160.71",
      "confidence": 0.96,
      "reasoning": "Total amount is ₱12,500.00. VAT at 12% is ₱1,339.29. Subtotal = ₱12,500.00 / 1.12 = ₱11,160.71",
      "evidence_bbox": [400, 500, 500, 520]
    },
    {
      "question": "Who is the supplier?",
      "answer": "ABC Corporation",
      "confidence": 0.99,
      "reasoning": "Merchant name extracted from top of invoice",
      "evidence_bbox": [100, 50, 300, 80]
    },
    {
      "question": "What is the payment due date?",
      "answer": "2025-11-30",
      "confidence": 0.92,
      "reasoning": "Invoice date is 2025-11-13, payment terms are Net 17 days",
      "evidence_bbox": [100, 140, 250, 160]
    }
  ]
}
```

---

### Endpoint: Batch Processing

```http
POST /v1/documents/batch
Content-Type: application/json
Authorization: Bearer {supabase_jwt}
```

**Request:**
```json
{
  "documents": [
    {
      "url": "https://supabase.co/.../invoice1.pdf",
      "document_type": "invoice",
      "extraction_schema": "generic_invoice"
    },
    {
      "url": "https://supabase.co/.../receipt2.jpg",
      "document_type": "receipt",
      "extraction_schema": "bir_2307"
    }
  ],
  "callback_url": "https://erp.insightpulseai.net/api/documents/batch_callback",
  "options": {
    "parallel_workers": 5,
    "max_retry": 3
  }
}
```

**Response (202 Accepted):**
```json
{
  "batch_id": "batch_xyz789",
  "status": "processing",
  "total_documents": 2,
  "estimated_completion": "2025-11-13T10:15:00Z",
  "status_url": "/v1/documents/batch/batch_xyz789"
}
```

---

## MCP SERVER TOOLS

### Tool Definition

Following the LandingAI `vision-agent-mcp` pattern, we expose document tools via MCP protocol.

#### Tool 1: `extract_fields_from_invoice`

```typescript
{
  "name": "extract_fields_from_invoice",
  "description": "Extract structured fields from an invoice or receipt using agentic document extraction. Supports Philippine BIR forms (2307, 1601C) and generic invoices.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "Local file path to invoice/receipt (PDF or image)"
      },
      "extraction_schema": {
        "type": "string",
        "enum": ["bir_2307", "bir_1601c", "generic_invoice", "receipt"],
        "description": "Predefined schema for extraction"
      },
      "custom_fields": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "description": {"type": "string"}
          }
        },
        "description": "Optional custom fields to extract"
      }
    },
    "required": ["file_path"]
  }
}
```

#### Tool 2: `classify_document_type`

```typescript
{
  "name": "classify_document_type",
  "description": "Classify a document into one of the supported types: invoice, receipt, contract, bir_form, bank_statement, etc.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "Local file path to document"
      }
    },
    "required": ["file_path"]
  }
}
```

**Returns:**
```json
{
  "document_type": "invoice",
  "confidence": 0.98,
  "sub_type": "commercial_invoice",
  "detected_forms": ["BIR Form 2307"]
}
```

#### Tool 3: `answer_question_about_document`

```typescript
{
  "name": "answer_question_about_document",
  "description": "Answer natural language questions about a document using DocVQA. Supports complex reasoning over document content.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "Local file path to document"
      },
      "question": {
        "type": "string",
        "description": "Natural language question about the document"
      }
    },
    "required": ["file_path", "question"]
  }
}
```

**Example:**
```
Question: "What's the VAT amount on this invoice?"
Answer: {
  "answer": "₱1,339.29",
  "confidence": 0.96,
  "reasoning": "Total is ₱12,500.00 (inclusive). VAT = ₱12,500.00 - (₱12,500.00 / 1.12) = ₱1,339.29",
  "evidence_bbox": [400, 500, 500, 520]
}
```

#### Tool 4: `extract_table_from_pdf`

```typescript
{
  "name": "extract_table_from_pdf",
  "description": "Extract tables from a PDF with spatial understanding. Returns structured data with headers and rows.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "Local file path to PDF"
      },
      "page_number": {
        "type": "integer",
        "description": "Optional: specific page number (default: all pages)"
      },
      "table_index": {
        "type": "integer",
        "description": "Optional: specific table index on page (default: all tables)"
      }
    },
    "required": ["file_path"]
  }
}
```

**Returns:**
```json
{
  "tables": [
    {
      "page": 1,
      "index": 0,
      "headers": ["Description", "Quantity", "Unit Price", "Amount"],
      "rows": [
        ["Widget A", "10", "1000.00", "10000.00"],
        ["Widget B", "5", "500.00", "2500.00"]
      ],
      "bbox": [50, 200, 550, 450]
    }
  ]
}
```

#### Tool 5: `validate_bir_form`

```typescript
{
  "name": "validate_bir_form",
  "description": "Validate a Philippine BIR tax form for completeness and compliance. Checks required fields, TIN format, calculations, etc.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "Local file path to BIR form"
      },
      "form_type": {
        "type": "string",
        "enum": ["2307", "1601c", "2550q", "1702rt"],
        "description": "BIR form type"
      }
    },
    "required": ["file_path", "form_type"]
  }
}
```

**Returns:**
```json
{
  "valid": true,
  "compliance_score": 0.98,
  "issues": [],
  "warnings": [
    "TIN format is valid but not verified against BIR database"
  ],
  "completeness": {
    "required_fields": 15,
    "filled_fields": 15,
    "missing_fields": []
  }
}
```

---

## SUPABASE SCHEMA

### Table: `analytics.ipai_documents`

```sql
CREATE TABLE analytics.ipai_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_type VARCHAR(50) NOT NULL,  -- invoice, receipt, contract, bir_form
  sub_type VARCHAR(50),  -- bir_2307, bir_1601c, commercial_invoice
  original_filename VARCHAR(255) NOT NULL,
  storage_url TEXT NOT NULL,  -- DigitalOcean Spaces or Supabase Storage

  -- Extraction metadata
  extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  extraction_confidence NUMERIC(5,4),  -- 0.0000 to 1.0000
  processing_time_ms INTEGER,
  ocr_engine VARCHAR(50) DEFAULT 'paddleocr-vl-900m',
  llm_model VARCHAR(50) DEFAULT 'claude-sonnet-4.5',
  page_count INTEGER,

  -- Extracted fields (JSONB for flexibility)
  extracted_fields JSONB NOT NULL,  -- {merchant_name: {value, confidence, bbox}, ...}
  extracted_tables JSONB,  -- [{name, headers, rows, bbox}, ...]

  -- Grounding/visualization
  visualization_url TEXT,  -- PNG with bounding boxes overlaid

  -- Lineage
  source_system VARCHAR(50),  -- 'odoo', 'mobile_app', 'batch_job', 'mcp_client'
  source_record_id VARCHAR(100),  -- Odoo record ID or external ref
  uploaded_by VARCHAR(100),

  -- Audit
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- Indexes
  CONSTRAINT ipai_documents_confidence_check CHECK (extraction_confidence BETWEEN 0 AND 1)
);

CREATE INDEX idx_ipai_documents_type ON analytics.ipai_documents(document_type, sub_type);
CREATE INDEX idx_ipai_documents_extracted_at ON analytics.ipai_documents(extracted_at DESC);
CREATE INDEX idx_ipai_documents_source ON analytics.ipai_documents(source_system, source_record_id);
CREATE INDEX idx_ipai_documents_uploaded_by ON analytics.ipai_documents(uploaded_by);
CREATE INDEX idx_ipai_documents_fields ON analytics.ipai_documents USING GIN (extracted_fields);
```

### Table: `analytics.ipai_docvqa_queries`

```sql
CREATE TABLE analytics.ipai_docvqa_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES analytics.ipai_documents(id) ON DELETE CASCADE,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  confidence NUMERIC(5,4),
  reasoning TEXT,
  evidence_bbox JSONB,  -- [x1, y1, x2, y2]

  -- Metadata
  queried_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  queried_by VARCHAR(100),
  llm_model VARCHAR(50) DEFAULT 'claude-sonnet-4.5',
  response_time_ms INTEGER,

  CONSTRAINT ipai_docvqa_queries_confidence_check CHECK (confidence BETWEEN 0 AND 1)
);

CREATE INDEX idx_ipai_docvqa_queries_document ON analytics.ipai_docvqa_queries(document_id);
CREATE INDEX idx_ipai_docvqa_queries_queried_at ON analytics.ipai_docvqa_queries(queried_at DESC);
```

### Table: `analytics.ipai_batch_jobs`

```sql
CREATE TABLE analytics.ipai_batch_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  batch_id VARCHAR(100) UNIQUE NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, processing, completed, failed
  total_documents INTEGER NOT NULL,
  processed_documents INTEGER NOT NULL DEFAULT 0,
  failed_documents INTEGER NOT NULL DEFAULT 0,

  -- Timing
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  estimated_completion TIMESTAMPTZ,

  -- Configuration
  extraction_schema VARCHAR(50),
  parallel_workers INTEGER DEFAULT 5,
  callback_url TEXT,

  -- Results
  results_summary JSONB,  -- {avg_confidence, processing_time_ms, errors: [...]}

  -- Audit
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by VARCHAR(100)
);

CREATE INDEX idx_ipai_batch_jobs_batch_id ON analytics.ipai_batch_jobs(batch_id);
CREATE INDEX idx_ipai_batch_jobs_status ON analytics.ipai_batch_jobs(status);
CREATE INDEX idx_ipai_batch_jobs_created_at ON analytics.ipai_batch_jobs(created_at DESC);
```

### View: `analytics.v_ipai_documents_daily`

```sql
CREATE OR REPLACE VIEW analytics.v_ipai_documents_daily AS
SELECT
  DATE(extracted_at) AS extraction_date,
  document_type,
  sub_type,
  source_system,
  COUNT(*) AS document_count,
  AVG(extraction_confidence) AS avg_confidence,
  AVG(processing_time_ms) AS avg_processing_time_ms,
  SUM(page_count) AS total_pages
FROM analytics.ipai_documents
WHERE extracted_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 1, 2, 3, 4
ORDER BY extraction_date DESC, document_count DESC;
```

---

## INTEGRATION POINTS

### 1. Odoo ERP Integration

**Current Flow (Basic OCR):**
```
Mobile App → /ip/mobile/receipt → PaddleOCR → ip.ocr.receipt → Expense
```

**Enhanced Flow (Agentic Doc):**
```
Mobile App → /ip/mobile/receipt → ipai-agentic-doc service
  → Extract fields + tables + DocVQA
  → ip.ocr.receipt (enhanced with ADE data)
  → Auto-create Expense with:
    - Merchant name
    - Total amount (VAT-aware)
    - Line items (from table extraction)
    - Confidence scores per field
    - Grounding visualization
```

**Implementation:**
- Update `ip_expense_mvp` module to call `/v1/documents/extract` instead of basic OCR
- Pass `extraction_schema='receipt'` for receipts
- Store `visualization_url` in Odoo attachment
- Display bounding box overlay in Odoo UI for validation

### 2. Scout/Concur Integration

**Use Case:** Batch import expense reports from Scout/Concur exports

**Flow:**
```
Scout/Concur CSV export → Batch API → ipai-agentic-doc
  → Extract receipt images from Scout/Concur
  → Process each receipt in parallel (5 workers)
  → Match extracted data with CSV row
  → Flag discrepancies (amount mismatch, missing receipts)
  → Create Odoo expenses with matched data
```

**Batch Request:**
```json
{
  "documents": [
    {"url": "scout://receipts/exp_001.jpg", "document_type": "receipt"},
    {"url": "scout://receipts/exp_002.pdf", "document_type": "invoice"}
  ],
  "callback_url": "https://erp.insightpulseai.net/api/scout/batch_callback"
}
```

### 3. BIR Compliance Workflow

**Use Case:** Validate and extract BIR tax forms for month-end closing

**Flow:**
```
Month-End Close Orchestrator → BIRComplianceOrchestrator
  → Generate Form 1601-C (withholding tax)
  → Call ipai-agentic-doc to validate generated form
  → Extract fields from vendor-submitted 2307 certificates
  → Cross-check: Sum of 2307s = 1601-C total
  → Flag discrepancies for human review
  → Submit validated forms to BIR eServices
```

**Validation Request:**
```json
{
  "file_path": "/tmp/form_1601c_2025_11.pdf",
  "form_type": "1601c",
  "validation_rules": [
    "check_tin_format",
    "verify_totals_match",
    "validate_atc_codes",
    "check_deadline_compliance"
  ]
}
```

### 4. MCP + Claude Code Integration

**Use Case:** Interactive document analysis during development

**Example Session:**
```
User: Analyze invoice.pdf and tell me if the VAT calculation is correct

Claude Code:
1. [Invokes MCP tool] extract_fields_from_invoice(file_path="invoice.pdf")
   → Result: {total_amount: 12500.00, vat_amount: 1339.29}

2. [Invokes MCP tool] answer_question_about_document(
     file_path="invoice.pdf",
     question="What is the subtotal before VAT?"
   )
   → Result: {answer: "11160.71", confidence: 0.96}

3. [Validates]: 11160.71 * 1.12 = 12500.00 ✓ Correct!

Claude: The VAT calculation is correct. The subtotal is ₱11,160.71, and with 12% VAT (₱1,339.29), the total is ₱12,500.00.
```

---

## IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Weeks 1-2)

**Goal:** Basic ADE pipeline with REST API

**Tasks:**
1. Set up FastAPI project structure
2. Integrate existing PaddleOCR-VL service
3. Implement `/v1/documents/extract` endpoint
4. Define Pydantic models for BIR forms (2307, 1601C)
5. Create Supabase tables and RLS policies
6. Deploy to DigitalOcean Spaces + Supabase Edge Functions

**Deliverables:**
- REST API deployed at `https://ade.insightpulseai.net`
- Supabase schema live
- Basic receipt extraction working

### Phase 2: Vision Agent Integration (Weeks 3-4)

**Goal:** See → Reason → Act workflow

**Tasks:**
1. Implement Vision Agent wrapper (Claude Sonnet 4.5 vision)
2. Build code generation + test validation pipeline
3. Add confidence scoring and self-correction
4. Implement visualization generation (bounding boxes)
5. Store grounding images in Supabase Storage

**Deliverables:**
- Vision Agent working for complex invoices
- Grounding images generated
- Confidence > 95% on test set

### Phase 3: DocVQA + Advanced Features (Weeks 5-6)

**Goal:** Natural language queries and table extraction

**Tasks:**
1. Implement `/v1/documents/query` endpoint
2. Build table extraction with spatial analysis
3. Add BIR form validation logic
4. Create batch processing API
5. Implement parallel workers with stitching

**Deliverables:**
- DocVQA endpoint live
- Table extraction working
- Batch API deployed

### Phase 4: MCP Server (Week 7)

**Goal:** Expose tools to Claude Code

**Tasks:**
1. Implement MCP server (Python MCP SDK)
2. Define 5 core tools (extract, classify, query, table, validate)
3. Test with Claude Code locally
4. Document MCP server usage in README

**Deliverables:**
- MCP server published to npm/GitHub
- Integration guide for Codex CLI
- Working examples

### Phase 5: Integration (Weeks 8-9)

**Goal:** Wire up to Odoo + Scout/Concur

**Tasks:**
1. Update `ip_expense_mvp` module to use ADE API
2. Build Scout/Concur batch import flow
3. Integrate with BIRComplianceOrchestrator
4. Create Superset dashboard for document analytics

**Deliverables:**
- Odoo using ADE for expense receipts
- Scout/Concur batch import working
- BIR form validation in month-end close

### Phase 6: Production Hardening (Weeks 10-12)

**Goal:** Production-ready (Level 3 maturity)

**Tasks:**
1. Unit + integration + e2e tests (>= 90% coverage)
2. Golden prompt evaluation (50+ test cases)
3. Prometheus metrics + Grafana dashboards
4. Error handling + retries + circuit breakers
5. Load testing (100 documents/minute)
6. Security audit + penetration testing

**Deliverables:**
- Production checklist: >= 75/100 points
- SLA: 99% uptime, < 5s latency (p95), >= 95% accuracy
- Documentation complete

---

## PRODUCTION READINESS

### SLA Targets (Level 3: Production V1)

```yaml
Reliability:
  availability: ">= 99%"
  success_rate: ">= 95%"
  mttr: "< 2 hours"

Performance:
  latency_p50: "< 2 seconds"
  latency_p95: "< 5 seconds"
  latency_p99: "< 10 seconds"
  throughput: ">= 100 documents/minute (batch)"

Quality:
  extraction_accuracy: ">= 95%"
  field_accuracy: ">= 98%"
  amount_accuracy: "100%"  # Zero tolerance
  confidence_calibration: "95% confidence = 95% accuracy"

Cost:
  cost_per_document: "< $0.10 USD"
  llm_cost_per_document: "< $0.05 USD"
  ocr_cost_per_document: "< $0.02 USD"
```

### Monitoring & Observability

**Metrics (Prometheus):**
- `ipai_documents_total` - Counter (by type, schema, status)
- `ipai_extraction_duration_seconds` - Histogram
- `ipai_extraction_confidence` - Histogram
- `ipai_api_requests_total` - Counter (by endpoint, status)
- `ipai_batch_jobs_total` - Counter (by status)
- `ipai_llm_tokens_total` - Counter (by model)
- `ipai_llm_cost_usd_total` - Counter (by model)

**Dashboards (Grafana):**
1. **Document Extraction Overview**
   - Requests/minute by document type
   - Average extraction confidence
   - P50/P95/P99 latency
   - Error rate

2. **Quality Metrics**
   - Confidence distribution (histogram)
   - Field extraction accuracy (by field type)
   - Low confidence alerts (< 85%)

3. **Cost Tracking**
   - LLM token usage by model
   - Cost per document type
   - Daily/monthly burn rate

4. **Batch Processing**
   - Active batch jobs
   - Documents processed/hour
   - Failure rate by batch

**Alerts:**
- Error rate > 5% for 5 minutes
- Latency p95 > 10 seconds for 5 minutes
- Average confidence < 90% for 10 minutes
- Supabase connection failures
- LLM rate limit approaching

---

## NEXT STEPS

### Immediate Actions (Week 1)

1. **Create Project Repository**
   - Repository: `jgtolentino/ipai-agentic-doc`
   - License: MIT
   - Structure: FastAPI + MCP server + tests

2. **Set Up Development Environment**
   - Python 3.11+
   - Dependencies: FastAPI, PaddleOCR, Pydantic, httpx, MCP SDK
   - Docker Compose for local development

3. **Define Pydantic Schemas**
   - `BIRForm2307Schema`
   - `BIRForm1601CSchema`
   - `GenericInvoiceSchema`
   - `ReceiptSchema`

4. **Build MVP REST API**
   - `/v1/documents/extract` with basic OCR
   - Supabase integration
   - Test with sample invoices

5. **Document Architecture**
   - Update this spec with implementation details
   - Create API documentation (OpenAPI/Swagger)
   - Write MCP server usage guide

### Decision Points

**Q1: Hosting Strategy**
- Option A: Supabase Edge Functions (serverless, auto-scale)
- Option B: DigitalOcean App Platform (persistent, easier debugging)
- Option C: Dedicated droplet (full control, manual scaling)
- **Recommendation:** Start with DigitalOcean App Platform (like OCR service), migrate to Edge Functions for scale

**Q2: LLM Provider**
- Option A: Claude Sonnet 4.5 (best vision + reasoning)
- Option B: GPT-4V (good vision, lower cost)
- Option C: Gemini Flash 2.0 (fast, cost-effective)
- **Recommendation:** Claude Sonnet 4.5 for production, Gemini Flash for development/batch

**Q3: MCP Server Distribution**
- Option A: npm package (TypeScript)
- Option B: PyPI package (Python)
- Option C: Docker container
- **Recommendation:** Python package (aligns with Claude Code ecosystem)

---

## APPENDIX

### A. LandingAI References

- **vision-agent:** https://github.com/landing-ai/vision-agent
- **agentic-doc:** https://github.com/landing-ai/agentic-doc
- **vision-agent-mcp:** https://github.com/landing-ai/vision-agent-mcp
- **landingai-python:** https://github.com/landing-ai/landingai-python
- **ade-docvqa-benchmark:** https://github.com/landing-ai/ade-docvqa-benchmark

### B. Related Documentation

- `docs/AGENTIC_ARCHITECTURE.md` - 3-tier agent hierarchy
- `docs/ODOO_OCR_INTEGRATION_GUIDE.md` - Current OCR setup
- `docs/architecture.md` - System architecture overview
- `docs/PRODUCTION_DEPLOYMENT_OCR_2025-11-06.md` - OCR deployment

### C. Technology Stack

- **Backend:** FastAPI (Python 3.11+)
- **OCR:** PaddleOCR-VL 900M
- **LLM:** Claude Sonnet 4.5 (vision + reasoning)
- **MCP:** Python MCP SDK
- **Database:** Supabase PostgreSQL
- **Storage:** DigitalOcean Spaces + Supabase Storage
- **Deployment:** DigitalOcean App Platform
- **Monitoring:** Prometheus + Grafana
- **CI/CD:** GitHub Actions

---

**Document Status:** Design Phase - Ready for Review
**Next Review:** 2025-11-20
**Maintained By:** InsightPulse AI Engineering Team
**Questions/Feedback:** jgtolentino_rn@yahoo.com
