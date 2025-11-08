# Financial Filings Scraping & Embedding Architecture

## Overview

This document describes the architecture for automated ingestion of global financial filings (SEC EDGAR, LSE RNS, EU ESEF, Japan EDINET/TDnet) using official APIs, with embedding storage in pgvector for RAG-based financial analysis.

**Answer: Yes, you can run a cron job using your knowledge agent to scrape these sources for training and embedding.**

## Executive Summary

| Region | Source | Data Format | API Access | Rate Limits |
|--------|--------|-------------|------------|-------------|
| **US** | SEC EDGAR | JSON, XBRL, HTML | Public API | ≤10 req/s |
| **EU** | ESEF/iXBRL | iXBRL | Public files | None |
| **UK** | LSE RNS | JSON | Commercial API | Per contract |
| **Japan** | EDINET | JSON, XBRL, CSV | API key required | Per terms |
| **Japan** | TDnet | JSON | Commercial API | Per contract |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Cron Scheduler                          │
│               (Daily 01:15 Asia/Manila)                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Fetchers (Official APIs)                   │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│  │ EDGAR   │  │ EDINET  │  │   RNS   │  │  ESEF   │      │
│  │ Fetcher │  │ Fetcher │  │ Fetcher │  │ Fetcher │      │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘      │
│       │            │             │             │            │
└───────┼────────────┼─────────────┼─────────────┼───────────┘
        │            │             │             │
        ▼            ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Parser & Chunker                           │
│                                                             │
│  - XBRL/iXBRL numeric extraction                           │
│  - HTML text extraction (MD&A, Risk, Notes)                │
│  - Section-aware chunking (preserve section boundaries)    │
│  - Metadata tagging (issuer, jurisdiction, filing type)    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Embedding Model                            │
│                                                             │
│  Options:                                                   │
│  - OpenAI text-embedding-3-small (cloud, $$$)              │
│  - Local: sentence-transformers/all-MiniLM-L6-v2 (free)    │
│  - Local: BAAI/bge-large-en-v1.5 (higher quality)          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Supabase PostgreSQL + pgvector                 │
│                                                             │
│  Tables:                                                    │
│  - finserv_filing (metadata: issuer, CIK, filing_type)     │
│  - finserv_chunks (text, embedding, section, source_url)   │
│  - finserv_audit_log (track all access for compliance)     │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              RAG Applications (MCP Servers)                 │
│                                                             │
│  - DCF Builder Skill                                        │
│  - Coverage Note Writer Skill                              │
│  - Earnings Call Analyzer Skill                            │
│  - Policy Q&A Skill                                         │
└─────────────────────────────────────────────────────────────┘
```

## Data Sources

### 1. US: SEC EDGAR

**What**: 10-K, 10-Q, 8-K filings for US-listed companies

**API**: https://data.sec.gov/api/xbrl/companyfacts/

**Authentication**: User-Agent header required

**Rate Limit**: ≤10 requests/second

**Data Format**: JSON (metadata), XBRL (financials), HTML (narrative)

**Coverage**: All US public companies (Omnicom, Interpublic, Stagwell, etc.)

#### Implementation

```python
# services/filings/edgar_fetcher.py
import requests
import time
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "InsightPulseAI FilingsBot <business@insightpulseai.com>"
}

CIKS = {
    'OMC': '0001364742',  # Omnicom Group
    'IPG': '0000051644',  # Interpublic Group
    'STGW': '0001783398', # Stagwell Inc
    # Add more companies...
}

def fetch_company_facts(cik):
    """Fetch XBRL company facts from SEC EDGAR"""
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    time.sleep(0.12)  # Rate limit: ~8 req/s
    return response.json()

def fetch_company_submissions(cik):
    """Fetch company filing submissions (10-K, 10-Q, 8-K list)"""
    url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    time.sleep(0.12)
    return response.json()

def download_filing_document(cik, accession_number, primary_document):
    """Download full filing HTML/XBRL document"""
    acc_no_dashes = accession_number.replace('-', '')
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no_dashes}/{primary_document}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    time.sleep(0.12)
    return response.text
```

### 2. EU: ESEF (European Single Electronic Format)

**What**: Annual financial reports in iXBRL format

**Access**: Public download from issuer websites or regulators

**Authentication**: None (public)

**Rate Limit**: None (file downloads)

**Data Format**: iXBRL (Inline XBRL)

**Coverage**: EU-listed companies (Publicis, Havas, WPP EU filings)

#### Implementation

```python
# services/filings/esef_fetcher.py
import requests
from lxml import etree

def fetch_esef_filing(issuer_url):
    """Download ESEF iXBRL filing"""
    response = requests.get(issuer_url, timeout=30)
    response.raise_for_status()
    return response.content

def parse_ixbrl(ixbrl_content):
    """Parse iXBRL for facts and narrative"""
    root = etree.fromstring(ixbrl_content)

    # Extract XBRL facts (numeric data)
    facts = []
    for elem in root.iter():
        if elem.get('name'):  # XBRL fact
            facts.append({
                'concept': elem.get('name'),
                'value': elem.text,
                'context': elem.get('contextRef'),
                'unit': elem.get('unitRef'),
            })

    # Extract narrative sections
    # (iXBRL embeds narrative in HTML with XBRL tags)
    narrative = etree.tostring(root, method='text', encoding='unicode')

    return {'facts': facts, 'narrative': narrative}
```

### 3. Japan: EDINET

**What**: Annual and quarterly securities reports (Yūhō)

**API**: https://disclosure2dl.edinet-fsa.go.jp/

**Authentication**: API key required (free registration)

**Rate Limit**: Per API terms

**Data Format**: JSON (metadata), XBRL/CSV (data), PDF

**Coverage**: TSE-listed companies (Dentsu, Hakuhodo DY)

#### Implementation

```python
# services/filings/edinet_fetcher.py
import requests
import os

EDINET_API_KEY = os.environ['EDINET_API_KEY']
BASE_URL = "https://disclosure2dl.edinet-fsa.go.jp/api/v2"

def search_edinet_documents(issuer_code, from_date, to_date):
    """Search EDINET for documents"""
    url = f"{BASE_URL}/documents.json"
    params = {
        'date': from_date,  # YYYY-MM-DD
        'type': 2,  # Securities reports
        'Subscription-Key': EDINET_API_KEY,
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def download_edinet_document(doc_id):
    """Download EDINET document (ZIP with XBRL/CSV)"""
    url = f"{BASE_URL}/documents/{doc_id}"
    params = {'type': 1, 'Subscription-Key': EDINET_API_KEY}  # type=1 for ZIP
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.content  # ZIP file
```

### 4. Japan: TDnet (Timely Disclosure Network)

**What**: Real-time corporate announcements and earnings

**API**: Commercial (JPX paid service)

**Authentication**: API key (commercial license)

**Rate Limit**: Per commercial agreement

**Data Format**: JSON

**Coverage**: TSE-listed companies (real-time announcements)

#### Implementation

```python
# services/filings/tdnet_fetcher.py
import requests
import os

TDNET_API_KEY = os.environ['TDNET_API_KEY']
BASE_URL = "https://tdnet-api.jpx.co.jp"  # Example URL

def fetch_tdnet_disclosures(issuer_code, from_date, to_date):
    """Fetch TDnet timely disclosures"""
    headers = {'Authorization': f'Bearer {TDNET_API_KEY}'}
    params = {
        'issuer': issuer_code,
        'from': from_date,
        'to': to_date,
    }
    response = requests.get(f"{BASE_URL}/disclosures", headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()
```

### 5. UK: LSE RNS (Regulatory News Service)

**What**: UK-listed company announcements

**API**: Commercial (LSE RNS Data Feed)

**Authentication**: OAuth (commercial license)

**Rate Limit**: Per commercial agreement

**Data Format**: JSON

**Coverage**: LSE-listed companies (WPP plc)

#### Implementation

```python
# services/filings/rns_fetcher.py
import requests
import os

RNS_API_KEY = os.environ['RNS_API_KEY']
BASE_URL = "https://api.londonstockexchange.com/rns"

def fetch_rns_announcements(issuer_tidm, from_date, to_date):
    """Fetch RNS announcements"""
    headers = {'Authorization': f'Bearer {RNS_API_KEY}'}
    params = {
        'tidm': issuer_tidm,  # Trading Symbol (e.g., WPP)
        'from': from_date,
        'to': to_date,
    }
    response = requests.get(f"{BASE_URL}/announcements", headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()
```

## Parsing & Chunking

### Section-Aware Chunking

Preserve section boundaries to maintain context:

```python
# services/filings/chunker.py
import re

SECTIONS = [
    'MD&A',
    'Management Discussion',
    'Risk Factors',
    'Item 1A',
    'Item 7',
    'Notes to Financial Statements',
    'Liquidity',
    'Capital Resources',
]

def parse_sections(html_text):
    """Extract sections from HTML filing"""
    sections = {}

    for section_name in SECTIONS:
        pattern = re.compile(rf'(Item\s+[\dA]+[\.:]\s*{section_name}|{section_name})', re.IGNORECASE)
        match = pattern.search(html_text)

        if match:
            start_pos = match.start()
            # Find next section or max length
            end_pos = find_next_section(html_text, start_pos + 100, SECTIONS)
            section_text = html_text[start_pos:end_pos]

            # Clean HTML
            from lxml import html as lxml_html
            tree = lxml_html.fromstring(f'<div>{section_text}</div>')
            clean_text = tree.text_content()
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()

            sections[section_name] = clean_text

    return sections

def chunk_section(section_name, section_text, chunk_size=1000, overlap=200):
    """Chunk section while preserving context"""
    words = section_text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = ' '.join(chunk_words)

        chunks.append({
            'text': chunk_text,
            'section': section_name,
            'word_count': len(chunk_words),
        })

    return chunks
```

## Embedding & Storage

### Local Embedding Model (Recommended)

Use local embedding model to avoid cloud costs:

```python
# services/filings/embedder.py
from sentence_transformers import SentenceTransformer
import numpy as np

# Choose model:
# - all-MiniLM-L6-v2: Fast, 384 dimensions, good quality
# - BAAI/bge-large-en-v1.5: Higher quality, 1024 dimensions, slower

MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def embed_chunks(chunks):
    """Embed all chunks in batch"""
    texts = [c['text'] for c in chunks]
    embeddings = MODEL.encode(texts, batch_size=32, show_progress_bar=True)
    return embeddings.tolist()
```

### pgvector Storage

Store embeddings in PostgreSQL with pgvector:

```sql
-- Database schema
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE finserv_filing (
    id SERIAL PRIMARY KEY,
    issuer VARCHAR(255) NOT NULL,
    cik_or_code VARCHAR(50),
    jurisdiction VARCHAR(10) NOT NULL,  -- US, EU, JP, UK
    filing_type VARCHAR(50) NOT NULL,   -- 10-K, 10-Q, 8-K, URD, etc.
    filed_at TIMESTAMP NOT NULL,
    accession_number VARCHAR(255),
    source_url TEXT NOT NULL,
    checksum VARCHAR(64),
    processed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON finserv_filing (issuer, jurisdiction, filing_type);
CREATE INDEX ON finserv_filing (filed_at DESC);

CREATE TABLE finserv_chunks (
    id SERIAL PRIMARY KEY,
    filing_id INTEGER REFERENCES finserv_filing(id),
    text TEXT NOT NULL,
    embedding vector(384),  -- Dimension depends on model
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

-- Vector similarity index
CREATE INDEX ON finserv_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Text search indexes
CREATE INDEX ON finserv_chunks (issuer, filing_type, filed_at);
CREATE INDEX ON finserv_chunks (section);
```

### Ingestion Pipeline

```python
# jobs/cron/ingest_filings.py
import psycopg2
from psycopg2.extras import execute_values
import hashlib

def ingest_filing(issuer, cik, filing_type, filed_at, accession_number, source_url, document_text):
    """Ingest filing into pgvector"""

    # 1. Calculate checksum (avoid duplicate ingestion)
    checksum = hashlib.sha256(document_text.encode()).hexdigest()

    conn = psycopg2.connect(os.environ['POSTGRES_URL'])
    cursor = conn.cursor()

    # Check if already ingested
    cursor.execute("SELECT id FROM finserv_filing WHERE checksum = %s", (checksum,))
    if cursor.fetchone():
        print(f"Already ingested: {issuer} {filing_type} {filed_at}")
        return

    # 2. Insert filing metadata
    cursor.execute("""
        INSERT INTO finserv_filing (
            issuer, cik_or_code, jurisdiction, filing_type, filed_at,
            accession_number, source_url, checksum
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (issuer, cik, 'US', filing_type, filed_at, accession_number, source_url, checksum))

    filing_id = cursor.fetchone()[0]

    # 3. Parse sections
    sections = parse_sections(document_text)

    # 4. Chunk each section
    all_chunks = []
    for section_name, section_text in sections.items():
        chunks = chunk_section(section_name, section_text)
        all_chunks.extend(chunks)

    # 5. Embed chunks
    embeddings = embed_chunks(all_chunks)

    # 6. Insert chunks
    data = []
    for chunk, embedding in zip(all_chunks, embeddings):
        data.append((
            filing_id,
            chunk['text'],
            embedding,
            issuer,
            cik,
            'US',
            filing_type,
            filed_at,
            source_url,
            chunk['section'],
            checksum,
        ))

    execute_values(cursor, """
        INSERT INTO finserv_chunks (
            filing_id, text, embedding, issuer, cik_or_code,
            jurisdiction, filing_type, filed_at, source_url,
            section, checksum
        ) VALUES %s
    """, data)

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Ingested: {issuer} {filing_type} {filed_at} ({len(all_chunks)} chunks)")
```

## Cron Job Setup

### Daily Ingestion Schedule

```bash
# /etc/cron.d/filings-ingest
# Run daily at 01:15 Asia/Manila (after market close)
15 1 * * * /usr/bin/python3 /srv/agents/jobs/pull_filings.py >> /var/log/filings.log 2>&1
```

### Main Ingestion Script

```python
#!/usr/bin/env python3
# jobs/cron/pull_filings.py
"""
Daily filings ingestion cron job

Fetches latest filings from:
- SEC EDGAR (US)
- EDINET (Japan)
- ESEF (EU)
- RNS (UK, if licensed)
- TDnet (Japan, if licensed)
"""

import sys
import os
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/filings_ingest.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from services.filings.edgar_fetcher import fetch_company_submissions, download_filing_document
from services.filings.ingest import ingest_filing

# Companies to track
COMPANIES = {
    'Omnicom Group': {'cik': '0001364742', 'jurisdiction': 'US'},
    'Interpublic Group': {'cik': '0000051644', 'jurisdiction': 'US'},
    'WPP plc': {'cik': '0001410636', 'jurisdiction': 'US'},  # ADR
    'Publicis Groupe': {'issuer_code': 'FR0000130577', 'jurisdiction': 'EU'},
    'Dentsu Group': {'issuer_code': 'E04274', 'jurisdiction': 'JP'},
    # Add more...
}

def main():
    """Main ingestion job"""
    logger.info("Starting filings ingestion job")

    lookback_days = 90  # Ingest last 90 days on first run; then incremental

    for company_name, meta in COMPANIES.items():
        try:
            if meta['jurisdiction'] == 'US':
                ingest_us_company(company_name, meta['cik'], lookback_days)
            elif meta['jurisdiction'] == 'EU':
                ingest_eu_company(company_name, meta['issuer_code'], lookback_days)
            elif meta['jurisdiction'] == 'JP':
                ingest_jp_company(company_name, meta['issuer_code'], lookback_days)

        except Exception as e:
            logger.error(f"Error ingesting {company_name}: {e}", exc_info=True)

    logger.info("Filings ingestion job completed")

def ingest_us_company(company_name, cik, lookback_days):
    """Ingest US company filings from SEC EDGAR"""
    logger.info(f"Ingesting US company: {company_name} (CIK: {cik})")

    # Fetch submissions list
    submissions = fetch_company_submissions(cik)
    recent = submissions['filings']['recent']

    cutoff_date = datetime.now() - timedelta(days=lookback_days)

    # Filter recent 10-K, 10-Q, 8-K
    for i in range(len(recent['form'])):
        filing_type = recent['form'][i]
        if filing_type not in ['10-K', '10-Q', '8-K']:
            continue

        filing_date = datetime.strptime(recent['filingDate'][i], '%Y-%m-%d')
        if filing_date < cutoff_date:
            continue

        accession_number = recent['accessionNumber'][i]
        primary_document = recent['primaryDocument'][i]

        # Download document
        document_text = download_filing_document(cik, accession_number, primary_document)

        # Ingest
        source_url = f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={cik}&accession_number={accession_number}"
        ingest_filing(
            issuer=company_name,
            cik=cik,
            filing_type=filing_type,
            filed_at=filing_date,
            accession_number=accession_number,
            source_url=source_url,
            document_text=document_text
        )

def ingest_eu_company(company_name, issuer_code, lookback_days):
    """Ingest EU company ESEF filings"""
    # Implementation for ESEF ingestion
    pass

def ingest_jp_company(company_name, issuer_code, lookback_days):
    """Ingest Japan company EDINET filings"""
    # Implementation for EDINET ingestion
    pass

if __name__ == '__main__':
    main()
```

## Compliance & Guardrails

### 1. Respect Rate Limits

```python
# Rate limiter with exponential backoff
class RateLimiter:
    def __init__(self, max_calls_per_second):
        self.max_calls = max_calls_per_second
        self.calls = []

    def wait_if_needed(self):
        now = time.time()
        self.calls = [c for c in self.calls if c > now - 1.0]

        if len(self.calls) >= self.max_calls:
            sleep_time = 1.0 - (now - self.calls[0])
            time.sleep(sleep_time)

        self.calls.append(time.time())

# Usage
edgar_limiter = RateLimiter(max_calls_per_second=8)  # < 10 req/s SEC limit

def fetch_from_edgar(url):
    edgar_limiter.wait_if_needed()
    return requests.get(url, headers=HEADERS)
```

### 2. Store Source URLs & Accession IDs

Every chunk MUST reference original source for audit:

```python
# All chunks include:
chunk = {
    'text': '...',
    'source_url': 'https://www.sec.gov/...',
    'accession_number': '0001364742-20240215',  # SEC accession
    'filed_at': '2024-02-15',
}
```

### 3. Audit Logging

Log all ingestion activity:

```python
CREATE TABLE finserv_ingest_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    issuer VARCHAR(255),
    filing_type VARCHAR(50),
    accession_number VARCHAR(255),
    chunks_ingested INTEGER,
    status VARCHAR(50),  -- success, error, duplicate
    error_message TEXT
);
```

### 4. No Training on Customer Data

**Important**: Only use PUBLIC filings. Do NOT ingest:
- Proprietary client MNPI (material non-public information)
- Internal financial models
- Confidential client data

## Retrieval & RAG

### Semantic Search

```python
def retrieve_filings(question, top_k=5):
    """Retrieve relevant filing chunks"""
    # Embed question
    question_embedding = MODEL.encode([question])[0].tolist()

    conn = psycopg2.connect(os.environ['POSTGRES_URL'])
    cursor = conn.cursor()

    # Vector similarity search
    cursor.execute("""
        SELECT
            text,
            issuer,
            filing_type,
            section,
            source_url,
            1 - (embedding <=> %s::vector) AS similarity
        FROM finserv_chunks
        WHERE 1 - (embedding <=> %s::vector) > 0.5
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (question_embedding, question_embedding, question_embedding, top_k))

    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return [{
        'text': r[0],
        'issuer': r[1],
        'filing_type': r[2],
        'section': r[3],
        'source_url': r[4],
        'similarity': r[5],
    } for r in results]
```

### Filtered Search

Filter by issuer, filing type, date range:

```python
def retrieve_filings_filtered(question, issuer=None, filing_type=None, after_date=None, top_k=5):
    """Retrieve with filters"""
    question_embedding = MODEL.encode([question])[0].tolist()

    conditions = ["1 - (embedding <=> %s::vector) > 0.5"]
    params = [question_embedding, question_embedding, question_embedding]

    if issuer:
        conditions.append("issuer = %s")
        params.append(issuer)

    if filing_type:
        conditions.append("filing_type = %s")
        params.append(filing_type)

    if after_date:
        conditions.append("filed_at >= %s")
        params.append(after_date)

    params.append(top_k)

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            text, issuer, filing_type, section, source_url, filed_at,
            1 - (embedding <=> %s::vector) AS similarity
        FROM finserv_chunks
        WHERE {where_clause}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """

    conn = psycopg2.connect(os.environ['POSTGRES_URL'])
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    return results
```

## Monitoring & Alerting

### Ingestion Metrics

Track in Superset dashboard:

- **Filings ingested**: Count per day, per jurisdiction
- **Chunks created**: Volume over time
- **Ingestion errors**: Failed downloads, parsing errors
- **Latency**: Time to ingest each filing
- **Storage**: pgvector table size growth

### Alerts

Set up alerts for:

- **Ingestion failures**: > 5 errors in 1 hour
- **No new filings**: No ingestion in 48 hours (check cron)
- **Rate limit violations**: 429 errors from SEC EDGAR
- **Storage capacity**: pgvector table > 80% capacity

## Cost Estimate

### Cloud Embedding (OpenAI)

- **Model**: text-embedding-3-small
- **Cost**: $0.02 / 1M tokens
- **Estimate**: 10,000 filings × 50,000 words/filing × 1.3 tokens/word ≈ 650M tokens
- **Total**: $13/month for initial ingestion, ~$2/month incremental

### Local Embedding (Free)

- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Cost**: $0 (run on CPU or GPU)
- **Performance**: ~1000 chunks/minute on CPU, 10,000 chunks/minute on GPU

**Recommendation**: Use local embedding model to save $156/year.

### Storage (Supabase/PostgreSQL)

- **Chunks**: 1M chunks × (500 words × 384 dimensions) ≈ 2GB embeddings
- **Cost**: Included in Supabase Pro plan

## References

- SEC EDGAR API: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- EDINET API: https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WEEK0060.html
- LSE RNS API: https://docs.londonstockexchange.com/sites/default/files/documents/RNS%20Data%20Feed%20Technical%20Specification%20-%20v1.3.pdf
- ESMA ESEF: https://www.esma.europa.eu/sites/default/files/library/esma32-60-254_esef_reporting_manual.pdf
- pgvector: https://github.com/pgvector/pgvector
- Sentence Transformers: https://www.sbert.net/

## Next Steps

1. **Setup Infrastructure**: Create PostgreSQL tables with pgvector
2. **Implement Fetchers**: Start with SEC EDGAR (highest priority)
3. **Configure Cron**: Deploy daily ingestion job
4. **Build Skills**: Implement DCF, coverage notes, policy Q&A
5. **Create Evals**: Test retrieval quality and citation precision
6. **Monitor**: Setup Superset dashboards for ingestion metrics
