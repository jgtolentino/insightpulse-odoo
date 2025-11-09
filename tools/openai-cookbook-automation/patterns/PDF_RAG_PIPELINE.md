# PDF RAG Pipeline Pattern

## Overview

Ingest BIR forms, revenue memos, and regulations into pgvector for RAG. Adapted from OpenAI Cookbook's "Parse PDF docs for RAG" pattern.

## Target Systems

- OCR service (extraction)
- ipai-bot (ingestion task)
- Supabase (pgvector storage)
- pulser-copilot (search tool)

## Pattern

```
PDF Upload → Extract → Chunk → Embed → Store → Search
```

## Ingestion Pipeline

### Task Implementation

```python
# ipai-bot/src/tasks/pdf_ingest.py

@celery_app.task(name="ingest_bir_pdf")
def ingest_bir_pdf(pdf_url: str, metadata: dict):
    """
    Ingest BIR PDF into pgvector

    Args:
        pdf_url: URL or path to PDF
        metadata: {
            "bir_form": "1601-C",
            "section": "Part IV",
            "published_at": "2023-01-15",
            "document_type": "form|regulation|memo",
            "rmc_number": "5-2023"  # optional
        }
    """

    # 1. Download
    pdf_bytes = download_pdf(pdf_url)

    # 2. Extract with OCR service
    extraction = ocr_service.extract_pdf(
        pdf_bytes,
        mode="structured",  # preserve tables, headings, sections
        confidence_threshold=0.8,
    )

    # 3. Chunk text
    chunks = chunk_text(
        text=extraction.text,
        chunk_size=1000,      # tokens
        chunk_overlap=200,
        preserve_structure=True,  # don't break tables/sections
    )

    # 4. Generate embeddings
    texts = [chunk.text for chunk in chunks]
    embeddings = openai_client.embed(
        texts=texts,
        model="text-embedding-3-small",  # 1536 dims
    )

    # 5. Store in Supabase
    records = []
    for chunk, embedding in zip(chunks, embeddings):
        records.append({
            "content": chunk.text,
            "embedding": embedding,
            "metadata": {
                **metadata,
                "page": chunk.page,
                "chunk_index": chunk.index,
                "section_title": chunk.section_title,
                "has_table": chunk.has_table,
            },
        })

    # Batch insert
    supabase.table("bir_documents").insert(records).execute()

    return {
        "chunks_stored": len(records),
        "form_type": metadata.get("bir_form"),
        "pages_processed": extraction.total_pages,
    }
```

### Chunking Strategy

```python
# ipai-bot/src/utils/chunking.py

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    preserve_structure: bool = True,
) -> List[Chunk]:
    """
    Smart chunking that preserves document structure

    Strategies:
    1. Split on section headers first
    2. Then split on paragraphs
    3. Finally split on sentences if needed
    4. Preserve tables as single chunks
    """

    if preserve_structure:
        # Detect structure
        sections = detect_sections(text)
        tables = detect_tables(text)

        chunks = []

        for section in sections:
            # Check if section contains table
            section_tables = [t for t in tables if t.page == section.page]

            if section_tables:
                # Keep table as single chunk (don't split)
                chunks.append(Chunk(
                    text=section.text,
                    page=section.page,
                    section_title=section.title,
                    has_table=True,
                ))
            else:
                # Normal chunking
                section_chunks = split_section(
                    section.text,
                    chunk_size,
                    chunk_overlap,
                )
                chunks.extend(section_chunks)

    else:
        # Simple token-based chunking
        chunks = simple_chunk(text, chunk_size, chunk_overlap)

    return chunks


def detect_sections(text: str) -> List[Section]:
    """Detect section headers in BIR documents"""
    section_patterns = [
        r'^PART\s+[IVX]+:?\s+(.+)$',
        r'^Section\s+\d+\.?\s+(.+)$',
        r'^[A-Z\s]{20,}$',  # ALL CAPS headers
    ]

    sections = []
    lines = text.split('\n')

    for i, line in enumerate(lines):
        for pattern in section_patterns:
            if re.match(pattern, line.strip()):
                sections.append(Section(
                    title=line.strip(),
                    start_line=i,
                ))

    return sections
```

## Supabase Schema

```sql
-- supabase/migrations/005_bir_documents.sql

CREATE TABLE bir_documents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content text NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata jsonb NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- Metadata indexes
CREATE INDEX idx_bir_form ON bir_documents USING gin ((metadata -> 'bir_form'));
CREATE INDEX idx_doc_type ON bir_documents USING gin ((metadata -> 'document_type'));
CREATE INDEX idx_published_at ON bir_documents ((metadata ->> 'published_at'));

-- Vector similarity index
CREATE INDEX ON bir_documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Full-text search (backup)
ALTER TABLE bir_documents ADD COLUMN content_fts tsvector
    GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
CREATE INDEX idx_content_fts ON bir_documents USING gin (content_fts);
```

## Search Function

```sql
-- supabase/functions/search_bir_documents.sql

CREATE OR REPLACE FUNCTION search_bir_documents(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5,
    filters jsonb DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id uuid,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        bir_documents.id,
        bir_documents.content,
        bir_documents.metadata,
        1 - (bir_documents.embedding <=> query_embedding) AS similarity
    FROM bir_documents
    WHERE
        (filters = '{}'::jsonb OR bir_documents.metadata @> filters)
        AND 1 - (bir_documents.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
```

## pulser-copilot Search Tool

```python
# pulser-copilot/src/tools/search_bir_regulations.py

@mcp_tool("search_bir_regulations")
def search_bir_regulations(
    query: str,
    bir_form: str = None,
    document_type: str = None,
    threshold: float = 0.7,
    max_results: int = 5,
) -> List[Document]:
    """
    Search BIR regulations and forms

    Args:
        query: Natural language query
        bir_form: Filter by form (e.g., "1601-C")
        document_type: Filter by type (form/regulation/memo)
        threshold: Similarity threshold (0-1)
        max_results: Max results to return

    Returns:
        List of documents with content, metadata, and similarity
    """

    # Generate query embedding
    query_embedding = openai_client.embed(query)

    # Build filters
    filters = {}
    if bir_form:
        filters["bir_form"] = bir_form
    if document_type:
        filters["document_type"] = document_type

    # Search Supabase
    results = supabase.rpc(
        "search_bir_documents",
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": max_results,
            "filters": json.dumps(filters) if filters else "{}",
        }
    ).execute()

    # Format results
    documents = []
    for row in results.data:
        documents.append(Document(
            id=row["id"],
            content=row["content"],
            metadata=row["metadata"],
            similarity=row["similarity"],
        ))

    return documents
```

## Usage Example

```python
# Ingest a BIR form
task = ingest_bir_pdf.delay(
    pdf_url="https://bir.gov.ph/forms/1601-C.pdf",
    metadata={
        "bir_form": "1601-C",
        "document_type": "form",
        "published_at": "2023-01-15",
        "section": "Withholding Tax",
    }
)

# Search for regulations
results = search_bir_regulations(
    query="What are the validation rules for negative withholding tax amounts?",
    bir_form="1601-C",
    max_results=5,
)

for doc in results:
    print(f"[{doc.similarity:.2f}] {doc.metadata['section']}")
    print(doc.content[:200])
    print()
```

## OCR Fallback to GPT-4o Vision

```python
# ocr-service/src/ocr_fallback.py

class OCRWithLLMFallback:
    """Use PaddleOCR first, GPT-4o Vision as fallback"""

    def extract_pdf(
        self,
        pdf_bytes: bytes,
        confidence_threshold: float = 0.8,
    ) -> Extraction:

        # Try PaddleOCR
        paddle_result = paddle_ocr.extract(pdf_bytes)

        if paddle_result.confidence >= confidence_threshold:
            return paddle_result

        # Fallback to GPT-4o Vision
        logger.warning(f"PaddleOCR confidence {paddle_result.confidence:.2f} < threshold, using LLM")

        # Convert PDF to images
        images = pdf_to_images(pdf_bytes)

        # Extract with GPT-4o Vision
        extracted_pages = []
        for page_num, image in enumerate(images):
            page_text = self.extract_page_with_llm(image, page_num)
            extracted_pages.append(page_text)

        return Extraction(
            text="\n\n".join(extracted_pages),
            method="gpt-4o-vision",
            confidence=0.9,
            total_pages=len(images),
        )

    def extract_page_with_llm(self, image: bytes, page_num: int) -> str:
        """Extract single page with GPT-4o Vision"""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """
                            Extract all text from this BIR form page.

                            Preserve:
                            - Tables (use markdown tables)
                            - Section headers (use ## headers)
                            - Lists and numbering
                            - Field labels and values

                            Format as markdown.
                            """
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64.b64encode(image).decode()}"
                            }
                        }
                    ]
                }
            ],
        )

        return response.choices[0].message.content
```

## Metadata Schema

```python
BIR_METADATA_SCHEMA = {
    "bir_form": "string (1601-C, 2550Q, 1702-RT, etc)",
    "section": "string (Part IV - Tax Withheld)",
    "published_at": "date (YYYY-MM-DD)",
    "document_type": "enum (form, regulation, memo, guide)",
    "rmc_number": "string (optional, e.g., 5-2023)",
    "page": "int (page number in original PDF)",
    "chunk_index": "int (chunk number within page)",
    "section_title": "string (detected section title)",
    "has_table": "bool (chunk contains table)",
}
```

## Batch Ingestion

```python
# scripts/ingest_all_bir_pdfs.py

BIR_PDFS = [
    {
        "url": "https://bir.gov.ph/forms/1601-C.pdf",
        "metadata": {
            "bir_form": "1601-C",
            "document_type": "form",
            "published_at": "2023-01-15",
        }
    },
    {
        "url": "https://bir.gov.ph/forms/2550Q.pdf",
        "metadata": {
            "bir_form": "2550Q",
            "document_type": "form",
            "published_at": "2023-01-15",
        }
    },
    # ... 100+ more
]

for pdf in BIR_PDFS:
    task = ingest_bir_pdf.delay(pdf["url"], pdf["metadata"])
    print(f"Queued: {pdf['metadata']['bir_form']}")
```

## Cost Estimate

Per PDF:
- OCR: Free (PaddleOCR)
- Embeddings: ~$0.01 per 100 pages
- LLM fallback (if needed): ~$0.05 per 100 pages

**Total for 100 BIR PDFs**: ~$10-15

## Eval Criteria

```yaml
# ipai-bot/evals/pdf_rag.yaml

test_cases:
  - query: "What are the ATC codes for professional fees?"
    expected:
      - bir_form: "1601-C"
        similarity: "> 0.8"
        content_contains: ["ATC", "professional"]

  - query: "How to compute quarterly VAT?"
    expected:
      - bir_form: "2550Q"
        similarity: "> 0.75"
        content_contains: ["output VAT", "input VAT"]

behavioral_requirements:
  - "Must return most relevant BIR form first"
  - "Should not return unrelated forms"
  - "Similarity scores should be calibrated"
```

## Next Steps

1. Deploy OCR service with PaddleOCR
2. Implement chunking strategy
3. Create Supabase tables and functions
4. Build pulser-copilot search tool
5. Ingest initial 20 BIR PDFs
6. Add evals with 10+ test cases
