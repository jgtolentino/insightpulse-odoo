# SPEC-001: Financial Services Skills Parity

> **Status**: Approved
> **Owner**: Platform AI Team
> **Created**: 2025-11-08
> **Updated**: 2025-11-08
> **Reviewers**: Finance SSC Team, Compliance

## Problem Statement

### Business Context
Anthropic launched **Claude for Financial Services** (July 2025) with pre-built skills for DCF modeling, coverage notes, LSEG data integration, and Excel workflows. InsightPulse needs equivalent capabilities to:
- Automate financial research and analysis for Finance SSC
- Enable policy Q&A with strict citations for compliance
- Ingest and analyze regulatory filings (SEC EDGAR, EU ESEF, Japan EDINET)
- Generate financial models and reports with full audit trail

### Current State
- Manual research and analysis using external tools
- No standardized filings ingestion from SEC EDGAR, LSE RNS, or EDINET
- Limited Excel automation capabilities
- No policy Q&A system with citation requirements
- Missing compliance guardrails for financial data handling

### Desired State
- **Pre-built financial skills**: DCF builder, coverage notes, portfolio risk metrics
- **Automated filings ingestion**: SEC EDGAR (10-K/10-Q/8-K), EU iXBRL, Japan EDINET
- **Excel workflow automation**: Read/write workbooks, formulas, charts, sensitivity tables
- **Policy Q&A with citations**: Strict source attribution, no hallucinations
- **Compliance guardrails**: PII/MNPI redaction, audit logging, externalization controls

## Goals & Non-Goals

### Goals (What We Will Do)
- [ ] Build pre-built skills: DCF, coverage notes, portfolio metrics, earnings call analysis
- [ ] Implement filings ingestion via official APIs (EDGAR, EDINET, RNS, iXBRL)
- [ ] Enable Excel workflows (read/write/generate workbooks with formulas)
- [ ] Create policy Q&A system with mandatory citations
- [ ] Implement compliance guardrails (redaction, audit, source tracking)
- [ ] Achieve ≥90% doc-QA accuracy with ≥0.85 retrieval hit-rate
- [ ] Maintain P95 latency ≤3.5s for doc-QA, ≤15s for Excel generation

### Non-Goals (What We Won't Do)
- ❌ Trading/investment advice or order routing
- ❌ Real-time market-making capabilities
- ❌ Proprietary client MNPI ingestion (until DLP finalized)
- ❌ Custom LSEG integration (optional for future)

## User Stories

### Primary Users
- **Research Analyst**: Needs DCF models, coverage notes, earnings analysis
- **Finance Ops**: Requires policy Q&A, financial data extraction
- **CFO Staff**: Needs consolidated reporting, multi-agency analysis
- **Risk/Compliance**: Requires audit trails, source verification, redaction

### User Stories
1. **As a** Research Analyst
   **I want** to generate DCF models with sensitivity analysis
   **So that** I can value companies using latest filings data
   **Acceptance**: Excel output with formulas, citations, sensitivity tables

2. **As a** Finance Ops user
   **I want** to ask policy questions and get cited answers
   **So that** I can ensure compliance without manual document searches
   **Acceptance**: Answers include section references, refuse without sources

3. **As a** Compliance officer
   **I want** PII/MNPI automatically redacted before export
   **So that** we don't accidentally leak sensitive information
   **Acceptance**: Redaction blocks export, logs all decisions

4. **As a** Research Analyst
   **I want** to auto-ingest latest 10-K/10-Q filings
   **So that** analysis is always based on current data
   **Acceptance**: Daily fetch, XBRL/iXBRL parsing, pgvector storage

## Requirements

### Functional Requirements
| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1 | Ingest SEC EDGAR 10-K/10-Q/8-K via API | P0 | Store accession IDs |
| FR-2 | Parse EU iXBRL (ESEF) filings | P1 | Extract facts/notes |
| FR-3 | Parse Japan EDINET filings (API v2) | P2 | Requires API key |
| FR-4 | LSE RNS announcement ingestion | P2 | Commercial API |
| FR-5 | DCF builder skill with Excel export | P0 | 5-10y forecast, WACC, sensitivity |
| FR-6 | Coverage note writer skill | P0 | Thesis/catalysts/risks/valuation |
| FR-7 | Portfolio risk metrics skill | P1 | VaR, factor exposure, returns |
| FR-8 | Earnings call analyzer skill | P1 | Summarize transcripts |
| FR-9 | Policy Q&A with mandatory citations | P0 | Refuse without sources |
| FR-10 | Compliance redactor (PII/MNPI) | P0 | Block export if detected |
| FR-11 | Excel analyst skill | P0 | Read/write workbooks, formulas, charts |
| FR-12 | Audit logging for all LLM calls | P0 | User, timestamp, sources, outputs |

### Non-Functional Requirements
| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-1 | Doc-QA accuracy | ≥90% | Eval suite |
| NFR-2 | Retrieval hit-rate | ≥0.85 | Eval suite |
| NFR-3 | Citation precision | ≥0.95 | Eval suite |
| NFR-4 | P95 doc-QA latency | ≤3.5s | Monitoring |
| NFR-5 | P95 Excel generation latency | ≤15s | Monitoring |
| NFR-6 | EDGAR API rate limit compliance | ≤10 req/s | Rate limiter |
| NFR-7 | Data retention | 7 years | Storage policy |

### BIR Compliance Requirements
- [ ] Not directly applicable (financial research tool)
- [ ] Audit trail for all financial data access
- [ ] Source tracking for all numeric claims

### MCP Integration Requirements
- **EDGAR MCP Server**: HTTP connector for SEC EDGAR API
- **Filesystem MCP Server**: Export outputs to `/exports`
- **Python MCP Server**: Code execution for calculations
- **PostgreSQL MCP Server**: pgvector storage and retrieval
- **LSEG MCP Server**: Optional licensed data (future)

## Acceptance Criteria

### Must Have (P0)
- [ ] **E2E DCF Demo**: Request DCF for ticker → cites sources → Excel with formulas
- [ ] **Policy Q&A Demo**: Ask policy question → cited answer with section references
- [ ] **EDGAR Ingestion**: Daily fetch of 10-K/10-Q/8-K with accession IDs stored
- [ ] **Redaction**: PII/MNPI detected and export blocked with audit log
- [ ] **Excel Export**: Workbooks open with working formulas and sensitivity tables
- [ ] **Citation Fidelity**: All numeric claims have source anchors (URL/accession)
- [ ] **Evals Passing**: ≥90% accuracy, ≥0.85 hit-rate, ≥0.95 citation precision
- [ ] **Latency**: P95 doc-QA ≤3.5s, Excel gen ≤15s

### Should Have (P1)
- [ ] EU iXBRL parsing for ESEF filings
- [ ] Coverage note generation with structured format
- [ ] Portfolio risk metrics (VaR, factor exposure)
- [ ] Earnings call summarization

### Could Have (P2)
- [ ] Japan EDINET API integration
- [ ] LSE RNS announcement feed
- [ ] LSEG Workspace connector

## Data Model

### Filings Metadata (PostgreSQL)
```python
class FilingMetadata(models.Model):
    _name = 'finserv.filing'
    _description = 'Financial Filing Metadata'

    issuer = fields.Char(string='Issuer Name', required=True, index=True)
    cik_or_code = fields.Char(string='CIK/Issuer Code', index=True)
    jurisdiction = fields.Selection([
        ('US', 'United States'),
        ('EU', 'European Union'),
        ('JP', 'Japan'),
        ('UK', 'United Kingdom'),
    ], required=True)
    filing_type = fields.Char(string='Filing Type')  # 10-K, 10-Q, 8-K, URD, etc.
    filed_at = fields.Datetime(string='Filing Date', required=True)
    accession_number = fields.Char(string='Accession/Reference Number', index=True)
    source_url = fields.Char(string='Source URL', required=True)
    checksum = fields.Char(string='Content Checksum')
    processed_at = fields.Datetime(string='Processed Date')
```

### Vector Storage (pgvector)
```sql
CREATE TABLE finserv_chunks (
    id SERIAL PRIMARY KEY,
    filing_id INTEGER REFERENCES finserv_filing(id),
    text TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI embedding dimension
    issuer VARCHAR(255),
    cik_or_code VARCHAR(50),
    jurisdiction VARCHAR(10),
    filing_type VARCHAR(50),
    filed_at TIMESTAMP,
    source_url TEXT,
    section VARCHAR(255),  -- MD&A, Risk Factors, Notes, etc.
    checksum VARCHAR(64),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON finserv_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON finserv_chunks (issuer, filing_type, filed_at);
```

### Audit Log
```python
class FinservAuditLog(models.Model):
    _name = 'finserv.audit.log'
    _description = 'Financial Services Audit Log'

    user_id = fields.Many2one('res.users', string='User', required=True)
    timestamp = fields.Datetime(string='Timestamp', required=True, default=fields.Datetime.now)
    action = fields.Selection([
        ('query', 'Query'),
        ('export', 'Export'),
        ('redaction', 'Redaction'),
        ('filing_access', 'Filing Access'),
    ], required=True)
    sources = fields.Text(string='Sources Used')  # JSON list of URLs/accession IDs
    inputs = fields.Text(string='Input Prompt')
    outputs = fields.Text(string='Output Summary')
    redaction_applied = fields.Boolean(string='Redaction Applied')
    export_blocked = fields.Boolean(string='Export Blocked')
```

## User Interface

### Views
- **Skill Dashboard**: Launch pre-built skills (DCF, coverage notes, etc.)
- **Filings Browser**: Search and view ingested filings
- **Policy Q&A Interface**: Ask questions, view cited answers
- **Audit Log Viewer**: View all LLM interactions with sources
- **Export Manager**: Manage Excel/CSV exports with approval workflow

### User Workflows
1. **DCF Generation**:
   - User enters ticker/CIK
   - Skill fetches latest 10-K/10-Q
   - Extracts financials from XBRL
   - Builds DCF model (WACC, FCF, terminal value)
   - Generates Excel with formulas + sensitivity tables
   - Outputs Markdown summary with source footnotes

2. **Policy Q&A**:
   - User asks policy question
   - System searches policy corpus (pgvector)
   - Retrieves relevant sections
   - Generates answer with citations
   - Logs query, sources, answer in audit trail

3. **Filing Ingestion**:
   - Cron job fetches latest filings (daily)
   - Parses XBRL/iXBRL/HTML
   - Chunks section-aware (MD&A, Risk, Notes)
   - Embeds and stores in pgvector
   - Updates filing metadata

## Integration Points

### External Integrations
| System | Integration Type | Authentication | Data Format |
|--------|-----------------|----------------|-------------|
| SEC EDGAR | REST API | User-Agent header | JSON, XBRL, HTML |
| EDINET API | REST API | API Key | JSON, XBRL, CSV |
| LSE RNS | REST API | OAuth | JSON |
| EU ESEF | File Download | None (public) | iXBRL |

### MCP Connectors
- [ ] **edgar**: SEC EDGAR API connector (HTTP)
- [ ] **filesystem**: Export manager for `/exports`
- [ ] **python**: Code execution sandbox for calculations
- [ ] **postgres**: pgvector storage and retrieval
- [ ] **lseg**: Optional LSEG Workspace connector (future)

### Rate Limiting
- SEC EDGAR: ≤10 req/s, exponential backoff on 429/503
- EDINET: Per API terms (TBD)
- LSE RNS: Per commercial agreement

## Security & Privacy

### Access Control
| Role | Permissions |
|------|-------------|
| Finance Analyst | Query, view filings, generate models |
| Compliance Officer | View audit logs, manage redaction rules |
| System Admin | Configure MCP servers, manage API keys |
| Auditor | Read-only access to all logs and outputs |

### Data Sensitivity
- **PII**: Names, addresses, emails → Detect and redact
- **MNPI**: Material non-public information → Block export
- **Financial Data**: All filings data public, but track sources for audit
- **Audit Trail**: 7-year retention, encrypted at rest

### Compliance
- [ ] Source attribution: All numbers cite accession ID/URL
- [ ] Redaction: Automated PII/MNPI detection before export
- [ ] Audit logging: Every LLM call logged with user, timestamp, sources
- [ ] No training on customer data: Use only public filings
- [ ] API terms compliance: Respect rate limits, User-Agent requirements

## Performance & Scalability

### Performance Targets
- Doc-QA response: P95 ≤3.5s
- Excel generation: P95 ≤15s
- Filing ingestion: Daily batch within 4 hours
- Concurrent users: 50 analysts

### Data Volume
- Filings: ~10,000 filings/year (100+ issuers)
- Chunks: ~1M chunks in pgvector
- Growth: 20% YoY
- Retention: 7 years

### Caching Strategy
- Cache filing metadata for 24 hours
- Cache embeddings indefinitely (immutable)
- Cache policy Q&A results for 1 hour (policy corpus changes infrequent)

## Testing Strategy

### Unit Tests
- [ ] EDGAR fetcher: Mock API responses
- [ ] XBRL parser: Parse sample filings
- [ ] Chunker: Section-aware chunking logic
- [ ] Redactor: PII/MNPI detection accuracy

### Integration Tests
- [ ] End-to-end DCF generation
- [ ] End-to-end policy Q&A with citations
- [ ] Filing ingestion pipeline
- [ ] Excel export with formulas

### Evals (Golden Test Set)
```yaml
suite: finserv-core
thresholds:
  retrieval_hit_rate: 0.85
  citation_precision: 0.95
  p95_docqa_seconds: 3.5

cases:
  - id: ev-10k-mdna
    prompt: "Summarize liquidity risks for {ticker} from latest 10-K MD&A. Cite exact sections."
    expects:
      - cites_accession: true
      - metrics: [retrieval_hit_rate, citation_precision, p95_docqa_seconds]

  - id: ev-dcf
    prompt: "Build a base-case DCF for {ticker} with 5y forecast and sensitivity."
    expects:
      - has_excel_export: true
      - has_sensitivities: true
      - cites_sources: true

  - id: ev-policy-qa
    prompt: "What is the approval workflow for journal entries over $100K?"
    expects:
      - has_citations: true
      - citation_precision: 0.95
      - refuses_without_source: true
```

### Performance Tests
- [ ] Load test: 50 concurrent doc-QA requests
- [ ] Stress test: 10,000 filings ingestion
- [ ] Latency benchmark: P95 ≤ targets

## Dependencies

### Technical Dependencies
- [ ] PostgreSQL 15+ with pgvector extension
- [ ] Python 3.11+ with pandas, openpyxl, lxml
- [ ] MCP servers: edgar, filesystem, python, postgres
- [ ] OpenAI API or local embedding model
- [ ] SEC EDGAR API access (public, rate-limited)

### Team Dependencies
- [ ] Finance SSC Team: Define eval cases, validate outputs
- [ ] Compliance Team: Define redaction rules, audit requirements
- [ ] Platform AI Team: Implement skills, MCP servers, evals

### Timeline Dependencies
- [ ] M1 (2025-11-30): EDGAR intake + doc-QA
- [ ] M2 (2025-12-15): Excel flows + DCF skill
- [ ] M3 (2026-01-15): iXBRL + coverage notes + risk metrics

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| EDGAR API rate limits | Medium | Medium | Exponential backoff, daily batch processing |
| XBRL parsing errors | Medium | High | Extensive test suite, fallback to HTML parsing |
| Embedding cost overruns | Low | Medium | Use local embedding model (e.g., BGE) |
| Low citation precision | Medium | High | Strict prompting, evals as CI gate |
| Redaction false negatives | Low | Critical | Human review for high-risk exports |

## Assumptions & Constraints

### Assumptions
- SEC EDGAR API remains public and rate-limited at 10 req/s
- XBRL/iXBRL formats remain stable
- Finance team has expertise to validate DCF outputs
- Policy corpus is maintained and up-to-date

### Constraints
- Budget: Prefer local models over cloud API costs
- Timeline: M1 delivery by 2025-11-30
- Compliance: No MNPI ingestion until DLP finalized
- Technology: Use existing Supabase + Odoo stack

## Success Metrics

### KPIs
| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Doc-QA accuracy | N/A | ≥90% | Eval suite |
| Retrieval hit-rate | N/A | ≥0.85 | Eval suite |
| Citation precision | N/A | ≥0.95 | Eval suite |
| P95 doc-QA latency | N/A | ≤3.5s | APM monitoring |
| P95 Excel gen latency | N/A | ≤15s | APM monitoring |
| Analyst time saved | N/A | 30% | Survey |

### Business Impact
- **ROI**: 30% reduction in analyst research time = ~$50K/year savings
- **Cost savings**: Use local models instead of cloud APIs = ~$10K/year
- **Efficiency gain**: DCF models generated in minutes vs. hours

## Release Strategy

### Rollout Plan
- **Phase 1 (M1)**: EDGAR ingestion + policy Q&A (internal only)
- **Phase 2 (M2)**: DCF builder + Excel export (pilot with 5 analysts)
- **Phase 3 (M3)**: Full rollout + iXBRL + coverage notes

### Rollback Plan
- Feature flags for each skill (can disable individually)
- Revert to manual processes if critical bugs
- Database backups before each deployment

### Communication Plan
- **Stakeholders**: Finance SSC, Compliance, Platform AI
- **Training**: 2-hour workshop on skills usage, policy Q&A
- **Documentation**: User guides, skill reference, troubleshooting

## Open Questions

1. **LSEG Licensing**: Do we license LSEG Workspace data?
   - **Impact**: Adds professional financial data feeds
   - **Owner**: Finance Director
   - **Due**: 2025-11-15

2. **Local vs. Cloud Embeddings**: Use OpenAI or local model (BGE)?
   - **Impact**: Cost vs. quality trade-off
   - **Owner**: Platform AI Team
   - **Due**: 2025-11-10

3. **Redaction Review**: Should high-risk exports require human review?
   - **Impact**: Reduces false negative risk but adds manual step
   - **Owner**: Compliance Team
   - **Due**: 2025-11-12

## References

- Anthropic Claude for Financial Services: https://www.anthropic.com/news/claude-for-financial-services
- SEC EDGAR API: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- EDINET API: https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WEEK0060.html
- OCA Skills: https://github.com/anthropics/skills
- InsightPulse Constitution: `docs/spec-kit/templates/constitution-template.md`

## Changelog

| Date | Author | Changes |
|------|--------|---------|
| 2025-11-08 | Platform AI | Initial draft |

---

## Review Checklist

- [x] Business value clearly articulated (30% analyst time savings)
- [x] All functional requirements defined (FR-1 through FR-12)
- [x] Non-functional requirements specified (NFR-1 through NFR-7)
- [x] Acceptance criteria are testable (Evals suite defined)
- [x] Security and privacy requirements defined (Redaction, audit logging)
- [x] Dependencies identified (PostgreSQL, MCP servers, APIs)
- [x] Risks documented (Rate limits, parsing errors, redaction)
- [x] Success metrics defined (KPIs table)
- [x] Stakeholder review completed (Finance SSC, Compliance)
