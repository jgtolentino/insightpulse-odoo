---
name: "filings-edgar-ingest"
version: "1.0.0"
owner: "Platform AI Team"
description: "Ingest SEC EDGAR filings (10-K, 10-Q, 8-K) via official API with source tracking and pgvector storage"
dependencies:
  - mcp: "edgar"          # SEC EDGAR HTTP connector
  - mcp: "postgres"       # pgvector storage
  - mcp: "python"         # parsing and chunking
capabilities:
  - citations_required: true
  - code_execution: python
  - data_ingestion: edgar
guardrails:
  - "Respect SEC rate limit: ≤10 req/s"
  - "Include User-Agent header: InsightPulseAI FilingsBot <business@insightpulseai.com>"
  - "Store accession numbers and source URLs for all filings"
  - "Log all API requests for audit trail"
  - "Use exponential backoff on 429/503 errors"
inputs:
  - cik: "10-digit CIK (e.g., 0001364742 for Omnicom)"
  - filing_types: "[10-K, 10-Q, 8-K] or 'all'"
  - lookback_days: "Number of days to look back (default: 90)"
workflow:
  - step: "Fetch company metadata from SEC EDGAR API (data.sec.gov/submissions/CIK{cik}.json)"
  - step: "Filter filings by type and date"
  - step: "Download HTML/XBRL documents for each filing"
  - step: "Parse XBRL for numeric facts, HTML for text sections (MD&A, Risk Factors, Notes)"
  - step: "Chunk section-aware (preserve section boundaries)"
  - step: "Embed chunks with metadata: issuer, cik, filing_type, filed_at, accession_number, source_url"
  - step: "Store in pgvector table finserv_chunks"
  - step: "Update finserv_filing metadata table"
success_criteria:
  - "All filings have accession_number and source_url stored"
  - "Chunks are section-aware (MD&A chunks tagged with section='MD&A')"
  - "Retrieval hit-rate ≥0.85 on eval set"
  - "Rate limit respected (≤10 req/s)"
  - "Exponential backoff on errors"
---

# SEC EDGAR Filings Ingest Skill

## Purpose

Ingest SEC EDGAR filings (10-K, 10-Q, 8-K) via the official SEC EDGAR API and store in pgvector for retrieval. Maintains full audit trail with accession numbers and source URLs.

## Usage

```python
# Ingest latest filings for Omnicom Group
filings = ingest_edgar_filings(
    cik="0001364742",
    filing_types=["10-K", "10-Q"],
    lookback_days=90
)
```

## Workflow

### 1. Fetch Company Metadata

```python
import requests
import time

HEADERS = {
    "User-Agent": "InsightPulseAI FilingsBot <business@insightpulseai.com>"
}

def fetch_company_submissions(cik):
    """Fetch company filings list from SEC EDGAR"""
    url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    time.sleep(0.12)  # Rate limit: ~8 req/s < 10 req/s
    return response.json()
```

### 2. Filter Filings by Type and Date

```python
from datetime import datetime, timedelta

def filter_recent_filings(submissions, filing_types, lookback_days):
    """Filter filings by type and date"""
    cutoff_date = datetime.now() - timedelta(days=lookback_days)
    recent = submissions['filings']['recent']

    filings = []
    for i in range(len(recent['form'])):
        if recent['form'][i] in filing_types:
            filing_date = datetime.strptime(recent['filingDate'][i], '%Y-%m-%d')
            if filing_date >= cutoff_date:
                filings.append({
                    'accession_number': recent['accessionNumber'][i],
                    'filing_date': recent['filingDate'][i],
                    'filing_type': recent['form'][i],
                    'primary_document': recent['primaryDocument'][i],
                })
    return filings
```

### 3. Download Filing Documents

```python
def download_filing(cik, accession_number, primary_document):
    """Download filing document from SEC EDGAR"""
    # Remove dashes from accession number for URL
    acc_no_dashes = accession_number.replace('-', '')
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no_dashes}/{primary_document}"

    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    time.sleep(0.12)  # Rate limit
    return response.text
```

### 4. Parse XBRL and HTML

```python
from lxml import etree, html as lxml_html
import re

def parse_xbrl_facts(document_text):
    """Extract numeric facts from XBRL/iXBRL"""
    # Parse as XML
    try:
        root = etree.fromstring(document_text.encode('utf-8'))
        facts = []
        # Extract XBRL facts (simplified)
        for element in root.iter():
            if element.text and element.text.strip().replace('.', '').replace('-', '').isdigit():
                facts.append({
                    'concept': element.tag.split('}')[-1],  # Remove namespace
                    'value': element.text,
                    'context': element.get('contextRef'),
                })
        return facts
    except:
        return []

def parse_html_sections(document_text):
    """Extract text sections from HTML filing"""
    tree = lxml_html.fromstring(document_text)

    sections = {}

    # MD&A (Item 7 for 10-K, Item 2 for 10-Q)
    mdna_pattern = re.compile(r'(Item\s+[27][\.:]\s*Management.*Discussion)', re.IGNORECASE)
    mdna_match = mdna_pattern.search(document_text)
    if mdna_match:
        sections['MD&A'] = extract_section_text(document_text, mdna_match.start())

    # Risk Factors (Item 1A)
    risk_pattern = re.compile(r'(Item\s+1A[\.:]\s*Risk\s+Factors)', re.IGNORECASE)
    risk_match = risk_pattern.search(document_text)
    if risk_match:
        sections['Risk Factors'] = extract_section_text(document_text, risk_match.start())

    # Notes to Financial Statements
    notes_pattern = re.compile(r'(Notes\s+to\s+.*Financial\s+Statements)', re.IGNORECASE)
    notes_match = notes_pattern.search(document_text)
    if notes_match:
        sections['Notes'] = extract_section_text(document_text, notes_match.start())

    return sections

def extract_section_text(document_text, start_pos, max_length=50000):
    """Extract section text from start position"""
    # Extract up to max_length characters from start_pos
    section_text = document_text[start_pos:start_pos + max_length]

    # Clean HTML tags
    tree = lxml_html.fromstring(f'<div>{section_text}</div>')
    text = tree.text_content()

    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text
```

### 5. Chunk Section-Aware

```python
def chunk_section(section_name, section_text, chunk_size=1000, overlap=200):
    """Chunk text while preserving section context"""
    chunks = []
    words = section_text.split()

    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = ' '.join(chunk_words)

        chunks.append({
            'text': chunk_text,
            'section': section_name,
        })

    return chunks
```

### 6. Embed and Store in pgvector

```python
def embed_and_store(chunks, filing_metadata, embedding_model):
    """Embed chunks and store in pgvector"""
    import psycopg2
    from psycopg2.extras import execute_values

    conn = psycopg2.connect(os.environ['POSTGRES_URL'])
    cursor = conn.cursor()

    # Embed all chunks
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedding_model.embed_documents(texts)

    # Prepare data for insertion
    data = []
    for chunk, embedding in zip(chunks, embeddings):
        data.append((
            filing_metadata['filing_id'],
            chunk['text'],
            embedding,
            filing_metadata['issuer'],
            filing_metadata['cik'],
            'US',
            filing_metadata['filing_type'],
            filing_metadata['filed_at'],
            filing_metadata['source_url'],
            chunk['section'],
            filing_metadata['checksum'],
        ))

    # Insert into pgvector
    execute_values(
        cursor,
        """
        INSERT INTO finserv_chunks (
            filing_id, text, embedding, issuer, cik_or_code,
            jurisdiction, filing_type, filed_at, source_url,
            section, checksum
        ) VALUES %s
        """,
        data
    )

    conn.commit()
    cursor.close()
    conn.close()
```

## Rate Limiting

SEC requires ≤10 requests per second. Implement:

```python
import time
from functools import wraps

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove calls outside the period
            self.calls = [c for c in self.calls if c > now - self.period]

            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                time.sleep(sleep_time)

            self.calls.append(time.time())
            return func(*args, **kwargs)
        return wrapper

# Usage
@RateLimiter(max_calls=8, period=1.0)  # 8 req/s < 10 req/s ceiling
def fetch_from_edgar(url):
    return requests.get(url, headers=HEADERS, timeout=30)
```

## Error Handling

Implement exponential backoff:

```python
import time

def fetch_with_retry(url, max_retries=4):
    """Fetch with exponential backoff"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [429, 503]:
                # Rate limit or service unavailable
                wait_time = 2 ** attempt  # 2, 4, 8, 16 seconds
                time.sleep(wait_time)
            else:
                raise
    raise Exception(f"Failed to fetch {url} after {max_retries} retries")
```

## Audit Trail

Log all API requests:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_edgar_request(cik, filing_type, accession_number):
    """Log EDGAR API request for audit"""
    logger.info(
        "EDGAR_REQUEST",
        extra={
            'cik': cik,
            'filing_type': filing_type,
            'accession_number': accession_number,
            'timestamp': datetime.now().isoformat(),
            'user': os.environ.get('USER'),
        }
    )
```

## Evaluation

Test retrieval quality:

```python
def test_retrieval_hit_rate():
    """Test retrieval hit-rate on golden questions"""
    questions = [
        {
            'query': 'What were the liquidity risks for Omnicom in 2024?',
            'expected_sections': ['MD&A', 'Risk Factors'],
            'expected_filing': '10-K',
        },
        # ... more test cases
    ]

    hits = 0
    for q in questions:
        results = retrieve_from_pgvector(q['query'], top_k=5)
        if any(r['section'] in q['expected_sections'] for r in results):
            hits += 1

    hit_rate = hits / len(questions)
    assert hit_rate >= 0.85, f"Hit rate {hit_rate} < 0.85"
```

## Cron Schedule

Run daily to ingest latest filings:

```bash
# crontab -e
15 1 * * * /usr/bin/python3 /srv/agents/jobs/ingest_edgar_filings.py >> /var/log/edgar_ingest.log 2>&1
```

## References

- SEC EDGAR API: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- Rate Limits: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data
- XBRL Spec: https://www.xbrl.org/
