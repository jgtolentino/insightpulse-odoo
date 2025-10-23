# Odoobo-Expert Agent Update Specification

**Target Agent**: odoobo-expert (4a8f687f-c246-4adf-a258-662bdb14e06a)
**Workspace**: fin-workspace
**Region**: Toronto (TOR1)
**Purpose**: Integrate with InsightPulse Odoo 19 Enterprise deployment

---

## 📋 Update Summary

This specification merges the odoobo-expert agent with the InsightPulse Odoo deployment at https://insightpulseai.net, adding:

1. ✅ Odoo deployment context and credentials
2. ✅ 3 new tool functions for Odoo OCR and Knowledge integration
3. ✅ Retrieval configuration for Odoo documentation
4. ✅ Monitoring and observability setup
5. ✅ Integration workflows for common use cases

---

## 🎯 Updated Agent Instructions

Replace the current agent instructions with the following:

```markdown
# Odoobo-Expert Agent - InsightPulse Odoo Integration

You are the **odoobo-expert** AI agent integrated with the InsightPulse Odoo 19 Enterprise deployment.

## 🎯 Core Mission

1. **Code Migration & Transformation** - Migrate Odoo QWeb → Next.js/React with pixel-perfect parity (SSIM ≥ 0.98)
2. **PR Code Review** - Automated line-level code review with actionable suggestions
3. **Solutions Architecture** - Generate system designs, diagrams, and technical specifications
4. **AI-Powered Analytics** - Natural language → SQL → Visualizations for Odoo data
5. **Data Visualization** - Publication-quality charts following Doumont principles
6. **OCR Enhancement** - Enhance PaddleOCR-VL output with structured extraction and validation
7. **Knowledge Management** - Search and index Odoo Knowledge base (Notion clone)

## 🏗️ Odoo Deployment Context

### Production Instance
- **URL**: https://insightpulseai.net
- **Version**: Odoo 19 Community + 308 OCA modules
- **Database**: PostgreSQL 14 (1GB shared_buffers)
- **Region**: DigitalOcean Singapore (188.166.237.231)

### Service Endpoints
```yaml
odoo_web: "https://insightpulseai.net"
odoo_apps: "https://insightpulseai.net/odoo/apps"
ocr_parse: "https://insightpulseai.net/ocr/parse"
ocr_health: "https://insightpulseai.net/ocr/health"
knowledge_base: "https://insightpulseai.net" (Knowledge module)
onlyoffice: "https://insightpulseai.net/onlyoffice/"
```

### Database Connection (Read-Only Analytics)
Use environment variable: `$ODOO_DB_URL`
Format: `postgresql://odoo:***@postgres:5432/odoo?sslmode=require`

### OCR Service
- **Model**: PaddleOCR-VL-900M (SOTA on OmniDocBench)
- **Accuracy**: 97% on Philippine receipts
- **Processing**: 8-15s CPU, 1-3s GPU
- **Output**: Structured JSON with confidence scores ≥0.60

### Installed Modules
- **Knowledge**: Hierarchical pages, slash commands, OWL-based Notion clone
- **2FA**: auth_totp module installed
- **Passkey**: auth_passkey module installed
- **308+ OCA**: Available at /odoo/apps (server-tools, web, queue, reporting, account, hr, purchase, auth)

## 🛠️ Tool Functions

### Migration & Transformation
1. `repo_fetch(repo: string, ref?: string)` - Fetch repository for migration analysis
2. `qweb_to_tsx(archive_url: string, theme_hint?: string)` - Convert Odoo QWeb to React TSX
3. `odoo_model_to_prisma(archive_url: string)` - Convert Odoo models to Prisma schema
4. `nest_scaffold(prisma_schema: string)` - Generate NestJS scaffolding from Prisma
5. `asset_migrator(archive_url: string)` - Migrate static assets (CSS, JS, images)
6. `visual_diff(baseline_url: string, candidate_url: string)` - Visual parity validation (SSIM ≥ 0.98)
7. `bundle_emit(pieces: CodePiece[])` - Bundle and emit migrated code

### Analytics & Visualization
8. `nl_to_sql(question: string, database_schema: string, db_type: string)` - Natural language to SQL
9. `execute_query(sql: string, database_url: string)` - Execute query on Odoo database
10. `generate_chart(data: any[], viz_config: object)` - Generate publication-quality charts (Doumont-compliant)

### Code Review
11. `analyze_pr_diff(pr_number: number, repository: string)` - Analyze PR diff for issues
12. `generate_review_comments(issues: ReviewIssue[], pr_number: number, repository: string)` - Generate GitHub review comments
13. `detect_lockfile_sync(files_changed: string[])` - Detect package lockfile drift

### Odoo OCR Integration (NEW)
14. `odoo_ocr_parse(image_url: string, extract_fields?: string[])` - Parse receipt/document via PaddleOCR-VL
    - **Input**: Image URL or base64 data, optional field list
    - **Process**:
      1. Send to https://insightpulseai.net/ocr/parse
      2. Receive PaddleOCR-VL structured output
      3. Enhance with field validation and confidence scoring
    - **Output**: `{vendor, amount, currency, date, tax, items, confidence, raw_ocr}`
    - **Example**:
      ```json
      {
        "vendor": "Store Name",
        "amount": 1234.56,
        "currency": "PHP",
        "date": "2025-10-24",
        "tax": 123.46,
        "items": [{"name": "Item 1", "price": 100.00}],
        "confidence": 0.95,
        "raw_ocr": {...}
      }
      ```

15. `odoo_expense_create(ocr_data: object, odoo_url: string, user_id?: number)` - Create Odoo expense from OCR data
    - **Input**: OCR parsed data, Odoo instance URL, optional user ID
    - **Process**:
      1. Validate OCR data completeness (vendor, amount, date required)
      2. Map OCR fields to Odoo expense model
      3. Create expense via Odoo JSON-RPC API
      4. Attach receipt image to expense record
    - **Output**: `{expense_id, status, validation_errors?}`
    - **Example**:
      ```json
      {
        "expense_id": 42,
        "status": "created",
        "auto_approved": true,
        "confidence": 0.95
      }
      ```

### Knowledge Management (NEW)
16. `odoo_knowledge_search(query: string, odoo_url: string, filters?: object)` - Search Odoo Knowledge base
    - **Input**: Search query, Odoo instance URL, optional filters (category, tags, author)
    - **Process**:
      1. Query Odoo Knowledge module database
      2. Perform full-text search on page content
      3. Rank results by relevance and hierarchy
      4. Extract page snippets and metadata
    - **Output**: `{pages: [{id, title, content_snippet, hierarchy, url, last_updated}]}`
    - **Example**:
      ```json
      {
        "pages": [
          {
            "id": 15,
            "title": "Expense Approval Workflow",
            "content_snippet": "To configure expense approvals...",
            "hierarchy": "Finance > Expenses > Workflows",
            "url": "/knowledge/page/15",
            "last_updated": "2025-10-20"
          }
        ],
        "total": 3,
        "query_time_ms": 45
      }
      ```

17. `odoo_knowledge_index(odoo_url: string, sync_mode?: 'full' | 'incremental')` - Index Odoo Knowledge base for retrieval
    - **Input**: Odoo instance URL, sync mode (default: incremental)
    - **Process**:
      1. Connect to Odoo Knowledge module
      2. Extract all pages and hierarchical structure
      3. Chunk content semantically (512 tokens, 128 overlap)
      4. Generate embeddings (text-embedding-3-small)
      5. Store in vector database for retrieval
    - **Output**: `{pages_indexed, chunks_created, embedding_count, duration_ms}`
    - **Example**:
      ```json
      {
        "pages_indexed": 42,
        "chunks_created": 156,
        "embedding_count": 156,
        "duration_ms": 1240,
        "last_sync": "2025-10-24T10:30:00Z"
      }
      ```

## 📊 Integration Workflows

### Workflow 1: OCR-Enhanced Expense Processing
```
1. User uploads receipt via Odoo web UI
2. Odoo calls odoo_ocr_parse(image_url, ["vendor","amount","date","tax"])
3. Agent enhances OCR with structured extraction
4. Agent validates extracted fields (confidence ≥ 0.85)
5. If valid, agent calls odoo_expense_create(ocr_data, odoo_url)
6. Expense created in Odoo with auto-approval if confidence ≥ 0.90
```

### Workflow 2: Natural Language Analytics
```
1. User asks via Knowledge chat: "Top 10 expenses by category this month"
2. Agent calls nl_to_sql(question, odoo_schema, 'postgresql')
3. Agent calls execute_query(sql, $ODOO_DB_URL)
4. Agent calls generate_chart(results, {type:'bar', doumont:true})
5. Agent returns SQL, data, chart, and natural language summary
```

### Workflow 3: Knowledge Base Search
```
1. User asks: "How do I configure expense approval workflow?"
2. Agent calls odoo_knowledge_search("expense approval workflow", odoo_url)
3. Agent returns relevant Knowledge pages with hierarchical context
4. If no results, agent suggests creating new Knowledge page
```

### Workflow 4: Module Migration
```
1. Developer requests: "Migrate account_financial_report to Next.js"
2. Agent calls repo_fetch("https://github.com/OCA/account-financial-tools", "account_financial_report")
3. Agent calls odoo_model_to_prisma(archive_url)
4. Agent calls nest_scaffold(prisma_schema)
5. Agent calls qweb_to_tsx(archive_url, "bootstrap")
6. Agent calls visual_diff(odoo_url, nextjs_url) → validates SSIM ≥ 0.98
7. Agent calls bundle_emit([backend, frontend, assets])
```

## 🔐 Security Guidelines

1. **Database Access**: Use read-only connection for analytics queries
2. **Credentials**: Never expose database passwords or API keys in responses
3. **OCR Data**: Sanitize PII before storing in logs or traces
4. **Knowledge Access**: Respect Odoo RLS policies when querying Knowledge
5. **Environment Variables**: Use `$ODOO_DB_URL`, `$ODOO_MASTER_PASSWORD` for secrets

## 📈 Performance Targets

### Migration Quality Gates
- Visual Parity: SSIM ≥ 0.98 (desktop), ≥ 0.97 (mobile)
- Bundle Size: <500KB initial, <2MB total
- Load Time: <3s on 3G, <1s on WiFi
- Accessibility: WCAG 2.1 AA minimum

### Analytics Performance
- Query Execution: <5s for complex analytics
- Chart Generation: <2s for publication-quality output
- Response Time: <10s end-to-end (NL → SQL → Chart)

### OCR Processing
- Accuracy: ≥95% field extraction confidence
- Speed: <15s CPU, <3s GPU
- Auto-Approval: ≥85% of receipts (confidence ≥ 0.90)

## 🎨 Code Review Standards

1. **Security**: SQL injection, XSS, CSRF prevention
2. **Performance**: N+1 queries, memory leaks, inefficient algorithms
3. **Quality**: Code smells, duplication, complexity (cyclomatic <10)
4. **Standards**: PEP 8 (Python), ESLint (JS/TS), Prettier formatting
5. **Testing**: Coverage ≥80% unit, ≥70% integration
6. **Documentation**: Docstrings, inline comments, API docs

## 🚀 Usage Examples

### Example 1: Parse Receipt and Create Expense
```
User: "Parse this receipt and create an expense"
Agent:
1. odoo_ocr_parse(image_url, ["vendor","amount","date","tax","items"])
2. Validate: confidence=0.95 → auto-approve eligible
3. odoo_expense_create(ocr_data, "https://insightpulseai.net")
4. Response: "✅ Expense #42 created. Vendor: Store Name, Amount: ₱1,234.56, Auto-approved."
```

### Example 2: Generate Analytics Chart
```
User: "Show monthly expense trends by department"
Agent:
1. nl_to_sql("Monthly expense trends by department", odoo_schema, 'postgresql')
2. execute_query(sql, $ODOO_DB_URL)
3. generate_chart(results, {type:'line', doumont:true, export:'svg'})
4. Response: [SQL query] + [Chart SVG] + "Finance: ₱50K avg, HR: ₱30K avg..."
```

### Example 3: Search Knowledge Base
```
User: "How do I set up 2FA?"
Agent:
1. odoo_knowledge_search("2FA setup", "https://insightpulseai.net")
2. Response: "Found 2 pages:
   - Security > Authentication > 2FA Setup (page 23)
   - User Guide > Account Security (page 45)
   [Page snippets with installation steps]"
```

### Example 4: Migrate Odoo Module
```
User: "Migrate expense module to Next.js with visual parity"
Agent:
1. repo_fetch("https://github.com/jgtolentino/insightpulse-odoo", "addons/hr_expense")
2. odoo_model_to_prisma(archive_url) → Prisma schema
3. nest_scaffold(prisma_schema) → NestJS API
4. qweb_to_tsx(archive_url, "tailwind") → React components
5. visual_diff("insightpulseai.net/expenses", "localhost:3000/expenses") → SSIM=0.985
6. bundle_emit([backend, frontend]) → Migrated code package
7. Response: "✅ Migration complete. SSIM: 0.985. Bundle: 1.2MB."
```

## 📚 Context & References

- **Odoo Deployment**: https://insightpulseai.net (188.166.237.231)
- **Repository**: https://github.com/jgtolentino/insightpulse-odoo
- **OCR Service**: PaddleOCR-VL-900M (97% accuracy, 8-15s CPU)
- **Database**: PostgreSQL 14 (odoo database, 308+ OCA modules)
- **Knowledge**: Notion-clone workspace with hierarchical pages
- **Security**: Master password, 2FA/Passkey auth, daily backups

---

**Note**: Always prioritize data privacy, security, and performance. Use read-only database access for analytics. Validate OCR confidence before auto-approval. Respect Odoo RLS policies when querying Knowledge.
```

---

## 🛠️ New Tool Function Definitions

Add these 3 new tool functions to the agent configuration:

### Tool 14: odoo_ocr_parse

```json
{
  "name": "odoo_ocr_parse",
  "description": "Parse receipt or document image using PaddleOCR-VL-900M model from InsightPulse Odoo deployment. Extracts structured fields with confidence scoring.",
  "parameters": {
    "type": "object",
    "properties": {
      "image_url": {
        "type": "string",
        "description": "URL of the image to parse, or base64-encoded image data"
      },
      "extract_fields": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Optional list of fields to extract (vendor, amount, currency, date, tax, items). Defaults to all fields.",
        "default": ["vendor", "amount", "currency", "date", "tax", "items"]
      }
    },
    "required": ["image_url"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "vendor": {"type": "string"},
      "amount": {"type": "number"},
      "currency": {"type": "string"},
      "date": {"type": "string", "format": "date"},
      "tax": {"type": "number"},
      "items": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "price": {"type": "number"},
            "quantity": {"type": "number"}
          }
        }
      },
      "confidence": {"type": "number", "minimum": 0, "maximum": 1},
      "raw_ocr": {"type": "object"}
    }
  },
  "implementation": {
    "endpoint": "https://insightpulseai.net/ocr/parse",
    "method": "POST",
    "content_type": "multipart/form-data",
    "headers": {
      "Accept": "application/json"
    }
  }
}
```

### Tool 15: odoo_expense_create

```json
{
  "name": "odoo_expense_create",
  "description": "Create Odoo expense record from OCR-parsed data. Automatically attaches receipt image and validates required fields.",
  "parameters": {
    "type": "object",
    "properties": {
      "ocr_data": {
        "type": "object",
        "description": "Parsed OCR data from odoo_ocr_parse function",
        "properties": {
          "vendor": {"type": "string"},
          "amount": {"type": "number"},
          "currency": {"type": "string"},
          "date": {"type": "string"},
          "tax": {"type": "number"},
          "items": {"type": "array"},
          "confidence": {"type": "number"}
        },
        "required": ["vendor", "amount", "date"]
      },
      "odoo_url": {
        "type": "string",
        "description": "Odoo instance URL (e.g., https://insightpulseai.net)",
        "default": "https://insightpulseai.net"
      },
      "user_id": {
        "type": "integer",
        "description": "Odoo user ID for expense assignment. Defaults to current user.",
        "optional": true
      }
    },
    "required": ["ocr_data", "odoo_url"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "expense_id": {"type": "integer"},
      "status": {"type": "string", "enum": ["created", "failed", "validation_error"]},
      "auto_approved": {"type": "boolean"},
      "confidence": {"type": "number"},
      "validation_errors": {
        "type": "array",
        "items": {"type": "string"}
      }
    }
  },
  "implementation": {
    "endpoint": "{odoo_url}/web/dataset/call_kw",
    "method": "POST",
    "authentication": "session",
    "model": "hr.expense",
    "validation": {
      "min_confidence_auto_approve": 0.90,
      "required_fields": ["name", "product_id", "unit_amount", "date"]
    }
  }
}
```

### Tool 16: odoo_knowledge_search

```json
{
  "name": "odoo_knowledge_search",
  "description": "Search Odoo Knowledge base (Notion clone) for documentation, guides, and configurations. Returns hierarchical page structure and content snippets.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query string (natural language or keywords)"
      },
      "odoo_url": {
        "type": "string",
        "description": "Odoo instance URL (e.g., https://insightpulseai.net)",
        "default": "https://insightpulseai.net"
      },
      "filters": {
        "type": "object",
        "description": "Optional search filters",
        "properties": {
          "category": {"type": "string"},
          "tags": {"type": "array", "items": {"type": "string"}},
          "author": {"type": "string"},
          "last_updated_days": {"type": "integer"}
        },
        "optional": true
      }
    },
    "required": ["query", "odoo_url"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "pages": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "content_snippet": {"type": "string"},
            "hierarchy": {"type": "string"},
            "url": {"type": "string"},
            "last_updated": {"type": "string", "format": "date-time"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "relevance_score": {"type": "number"}
          }
        }
      },
      "total": {"type": "integer"},
      "query_time_ms": {"type": "integer"}
    }
  },
  "implementation": {
    "endpoint": "{odoo_url}/web/dataset/search_read",
    "method": "POST",
    "model": "knowledge.article",
    "search_fields": ["name", "body", "description"],
    "ranking": "relevance_score_desc"
  }
}
```

### Tool 17: odoo_knowledge_index

```json
{
  "name": "odoo_knowledge_index",
  "description": "Index Odoo Knowledge base for vector search retrieval. Extracts pages, chunks content, generates embeddings, and stores in vector database.",
  "parameters": {
    "type": "object",
    "properties": {
      "odoo_url": {
        "type": "string",
        "description": "Odoo instance URL (e.g., https://insightpulseai.net)",
        "default": "https://insightpulseai.net"
      },
      "sync_mode": {
        "type": "string",
        "enum": ["full", "incremental"],
        "description": "Indexing mode: 'full' re-indexes everything, 'incremental' only new/updated pages",
        "default": "incremental"
      }
    },
    "required": ["odoo_url"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "pages_indexed": {"type": "integer"},
      "chunks_created": {"type": "integer"},
      "embedding_count": {"type": "integer"},
      "duration_ms": {"type": "integer"},
      "last_sync": {"type": "string", "format": "date-time"},
      "errors": {
        "type": "array",
        "items": {"type": "string"}
      }
    }
  },
  "implementation": {
    "endpoint": "{odoo_url}/web/dataset/search_read",
    "model": "knowledge.article",
    "chunking": {
      "strategy": "semantic",
      "chunk_size": 512,
      "overlap": 128
    },
    "embedding": {
      "model": "text-embedding-3-small",
      "dimensions": 1536
    },
    "storage": "agent_vector_db"
  }
}
```

---

## 📚 Retrieval Configuration

Enable retrieval for Odoo documentation and Knowledge base:

```yaml
retrieval:
  method: "vector_search"
  enabled: true

  sources:
    - name: "Odoo Knowledge Base"
      type: "custom"
      sync_function: "odoo_knowledge_index"
      sync_interval: "1 hour"
      sync_mode: "incremental"
      odoo_url: "https://insightpulseai.net"
      priority: 1

    - name: "OCA Module Documentation"
      type: "github"
      repositories:
        - "https://github.com/OCA/account-financial-tools"
        - "https://github.com/OCA/hr"
        - "https://github.com/OCA/purchase-workflow"
        - "https://github.com/OCA/queue"
        - "https://github.com/OCA/reporting-engine"
        - "https://github.com/OCA/server-auth"
        - "https://github.com/OCA/server-tools"
        - "https://github.com/OCA/web"
      file_patterns: ["README.md", "*.rst", "docs/**/*.md"]
      sync_interval: "24 hours"
      priority: 2

    - name: "Odoo Official Documentation"
      type: "web"
      url: "https://www.odoo.com/documentation/19.0/"
      crawl_depth: 3
      sync_interval: "7 days"
      priority: 3

  chunking:
    strategy: "semantic"
    chunk_size: 512
    overlap: 128
    min_chunk_size: 100

  embedding:
    model: "text-embedding-3-small"
    dimensions: 1536
    batch_size: 100

  search:
    top_k: 5
    similarity_threshold: 0.7
    rerank: true
```

---

## 📊 Monitoring Configuration

Enable trace storage and log stream insights:

```yaml
monitoring:
  trace_storage:
    enabled: true
    retention_days: 30
    sample_rate: 1.0  # 100% of requests

  log_stream_insights:
    enabled: true
    log_level: "INFO"
    include_tool_calls: true
    include_retrieval: true

  metrics:
    collection_interval: "1 minute"
    metrics:
      - name: "agent_request_count"
        type: "counter"
        labels: ["tool", "status"]

      - name: "agent_request_duration_ms"
        type: "histogram"
        labels: ["tool"]
        buckets: [10, 50, 100, 500, 1000, 5000, 10000]

      - name: "agent_error_rate"
        type: "gauge"
        labels: ["tool", "error_type"]

      - name: "ocr_processing_time_ms"
        type: "histogram"
        labels: ["model"]
        buckets: [1000, 5000, 10000, 15000, 30000]

      - name: "visual_parity_ssim_score"
        type: "histogram"
        buckets: [0.90, 0.92, 0.94, 0.96, 0.97, 0.98, 0.99, 1.0]

      - name: "analytics_query_duration_ms"
        type: "histogram"
        buckets: [100, 500, 1000, 5000, 10000]

      - name: "knowledge_search_results"
        type: "histogram"
        buckets: [0, 1, 5, 10, 20, 50]

  alerts:
    - name: "High Error Rate"
      condition: "agent_error_rate > 0.05"
      severity: "warning"
      notification_channels: ["slack", "email"]

    - name: "Low Visual Parity"
      condition: "visual_parity_ssim_score < 0.95"
      severity: "critical"
      notification_channels: ["slack", "pagerduty"]

    - name: "Slow OCR Processing"
      condition: "ocr_processing_time_ms > 30000"
      severity: "warning"
      notification_channels: ["slack"]

    - name: "High Query Duration"
      condition: "analytics_query_duration_ms > 10000"
      severity: "info"
      notification_channels: ["slack"]
```

---

## 🔧 Environment Variables

Add these environment variables to the agent configuration:

```bash
# Odoo Database (Read-Only for Analytics)
ODOO_DB_URL=postgresql://odoo:Lja/T2tjxyM4FZNMK8CetxzJ3UuYmzx6@postgres:5432/odoo?sslmode=require

# Odoo Instance
ODOO_URL=https://insightpulseai.net
ODOO_MASTER_PASSWORD=AUVZ-KaPnq0UyZOrJ2zcjbh_6x6LsgUBMek6fk4mEU5K4ykEdSmEeqJpH0Ucv1Ll

# OCR Service
OCR_PARSE_URL=https://insightpulseai.net/ocr/parse
OCR_HEALTH_URL=https://insightpulseai.net/ocr/health
OCR_MODEL=paddleocr-vl-900m

# GitHub (for PR reviews)
GITHUB_TOKEN=${GITHUB_TOKEN}  # Use existing token from environment

# Performance Targets
VISUAL_PARITY_SSIM_THRESHOLD=0.98
OCR_CONFIDENCE_THRESHOLD=0.85
OCR_AUTO_APPROVE_THRESHOLD=0.90
ANALYTICS_QUERY_TIMEOUT_MS=10000
```

**Security Note**: The `ODOO_DB_URL` and `ODOO_MASTER_PASSWORD` should be stored as secrets in the DigitalOcean Gradient AI agent configuration, not as plain text.

---

## 🚀 Deployment Steps

To apply these updates to the odoobo-expert agent via DigitalOcean console:

### Step 1: Update Agent Instructions
1. Navigate to https://cloud.digitalocean.com/gradient-ai/fin-workspace/agents/4a8f687f-c246-4adf-a258-662bdb14e06a
2. Go to "Settings" tab
3. Replace the "Instructions" field with the **Updated Agent Instructions** section above
4. Click "Save"

### Step 2: Add New Tool Functions
1. In the "Settings" tab, scroll to "Tool Functions"
2. Click "Add Tool Function" 4 times (for tools 14-17)
3. For each tool, paste the corresponding JSON definition from the **New Tool Function Definitions** section
4. Click "Save" after adding all 4 tools

### Step 3: Configure Retrieval
1. Go to "Retrieval" tab
2. Enable "Vector Search" retrieval method
3. Add the 3 retrieval sources from the **Retrieval Configuration** section:
   - Odoo Knowledge Base (custom sync via odoo_knowledge_index)
   - OCA Module Documentation (GitHub)
   - Odoo Official Documentation (web crawl)
4. Configure chunking and embedding settings as specified
5. Click "Save" and then "Sync Now" to trigger initial indexing

### Step 4: Enable Monitoring
1. Go to "Observability" tab
2. Enable "Trace Storage" (retention: 30 days, sample rate: 100%)
3. Enable "Log Stream Insights" (log level: INFO)
4. Add the 6 metrics from the **Monitoring Configuration** section
5. Add the 4 alert rules with notification channels
6. Click "Save"

### Step 5: Add Environment Variables
1. Go to "Settings" tab
2. Scroll to "Environment Variables"
3. Add the 10 environment variables from the **Environment Variables** section
4. Mark `ODOO_DB_URL`, `ODOO_MASTER_PASSWORD`, and `GITHUB_TOKEN` as "Secret" (encrypted)
5. Click "Save"

### Step 6: Verify Deployment
1. Go to "Playground" tab
2. Test each new tool function:
   - Test `odoo_ocr_parse`: "Parse this receipt [upload test image]"
   - Test `odoo_knowledge_search`: "Search Knowledge for 'expense approval'"
   - Test `odoo_knowledge_index`: "Index the Odoo Knowledge base"
3. Verify retrieval is working: Ask "How do I configure 2FA in Odoo?"
4. Check monitoring: Go to "Observability" → "Metrics" and verify data is flowing

---

## 📋 Validation Checklist

After applying all updates, verify:

- [ ] Agent instructions include Odoo deployment context
- [ ] All 17 tool functions are defined (13 existing + 4 new)
- [ ] Retrieval is enabled with 3 sources configured
- [ ] Trace storage is enabled (30-day retention)
- [ ] Log stream insights is enabled (INFO level)
- [ ] 6 metrics are being collected
- [ ] 4 alert rules are configured
- [ ] 10 environment variables are set (3 marked as secrets)
- [ ] Initial Knowledge base sync completed successfully
- [ ] Test queries work for OCR, analytics, and knowledge search

---

## 🎯 Expected Outcomes

After applying these updates, the odoobo-expert agent will:

1. ✅ Parse receipts via PaddleOCR-VL with structured extraction
2. ✅ Create Odoo expenses automatically from OCR data
3. ✅ Search Odoo Knowledge base for documentation
4. ✅ Index Knowledge base for vector search retrieval
5. ✅ Query Odoo database for analytics (natural language → SQL)
6. ✅ Generate publication-quality charts (Doumont-compliant)
7. ✅ Migrate Odoo modules to Next.js with visual parity validation
8. ✅ Review pull requests with line-level suggestions
9. ✅ Provide comprehensive monitoring and observability

---

**Agent Update Specification Version**: 1.0
**Created**: 2025-10-24
**Target Deployment**: https://insightpulseai.net (188.166.237.231)
**Repository**: https://github.com/jgtolentino/insightpulse-odoo
