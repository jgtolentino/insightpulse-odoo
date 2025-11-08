#!/usr/bin/env python3
"""
BIR Document Ingestor
Fetches official BIR forms, guides, RMCs, RRs and ingests into ph_tax.docs with embeddings.

Sources:
- https://www.bir.gov.ph/bir-forms
- https://www.bir.gov.ph/ebirforms
- Official BIR CDN PDFs
"""
import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Try importing PyPDF2, fallback to simple text extraction
try:
    from PyPDF2 import PdfReader
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    logging.warning("PyPDF2 not installed. PDF extraction will be limited.")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Official BIR documents to ingest
BIR_DOCUMENTS = [
    {
        "url": "https://bir-cdn.bir.gov.ph/BIR/pdf/2550Q%20%20April%202024%20ENCS_Final.pdf",
        "title": "Form 2550Q - Quarterly Value-Added Tax Return (April 2024)",
        "doc_type": "Form",
        "doc_date": "2024-04-01"
    },
    {
        "url": "https://bir-cdn.bir.gov.ph/BIR/pdf/2550Q%20guidelines%20April%202024_final.pdf",
        "title": "Form 2550Q Guidelines (April 2024)",
        "doc_type": "Guide",
        "doc_date": "2024-04-01"
    },
    {
        "url": "https://bir-cdn.bir.gov.ph/local/pdf/RMC%20No.%205-2023.pdf",
        "title": "RMC No. 5-2023 - Transitory Provisions on VAT Filing",
        "doc_type": "RMC",
        "doc_date": "2023-01-09"
    },
    {
        "url": "https://bir-cdn.bir.gov.ph/local/pdf/1601C%20final%20Jan%202018%20with%20DPA.pdf",
        "title": "Form 1601-C - Monthly Remittance Return of Income Taxes Withheld on Compensation",
        "doc_type": "Form",
        "doc_date": "2018-01-01"
    },
]

# Additional documents to scrape from BIR website
BIR_PAGES_TO_SCRAPE = [
    {
        "url": "https://www.bir.gov.ph/bir-forms",
        "doc_type": "Form"
    },
    {
        "url": "https://www.bir.gov.ph/ebirforms",
        "doc_type": "FAQ"
    }
]


class BIRIngestor:
    """Ingest BIR documents into Supabase with embeddings"""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.conn = None

    def connect(self):
        """Connect to database"""
        self.conn = psycopg2.connect(self.db_url)
        logger.info("Connected to database")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def extract_pdf_text(self, pdf_url: str) -> str:
        """Extract text from PDF URL"""
        if not HAS_PDF:
            return f"[PDF content from {pdf_url} - PyPDF2 not available for extraction]"

        try:
            response = requests.get(pdf_url, timeout=60)
            response.raise_for_status()

            # Save to temp file
            temp_path = f"/tmp/bir_doc_{hash(pdf_url)}.pdf"
            with open(temp_path, 'wb') as f:
                f.write(response.content)

            # Extract text
            reader = PdfReader(temp_path)
            text_parts = []

            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")

            # Cleanup
            os.unlink(temp_path)

            full_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} chars from {len(reader.pages)} pages")

            return full_text

        except Exception as e:
            logger.error(f"PDF extraction failed for {pdf_url}: {e}")
            return f"[PDF extraction failed: {str(e)}]"

    def scrape_webpage(self, url: str) -> str:
        """Scrape text content from webpage"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style tags
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text
            text = soup.get_text(separator='\n', strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = '\n'.join(lines)

            logger.info(f"Scraped {len(text)} chars from {url}")
            return text

        except Exception as e:
            logger.error(f"Web scraping failed for {url}: {e}")
            return f"[Web scraping failed: {str(e)}]"

    def chunk_text(self, text: str, chunk_size: int = 512) -> List[str]:
        """Split text into chunks for embedding"""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            if current_size + para_size > chunk_size and current_chunk:
                # Save current chunk
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size

        # Add remaining chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))

        return chunks

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def upsert_document(self, doc_info: Dict[str, Any], content: str):
        """Insert or update document in database"""
        # Check if document exists
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM ph_tax.docs WHERE source_url = %s",
                (doc_info['url'],)
            )
            existing = cur.fetchone()

        # Chunk and embed
        chunks = self.chunk_text(content)
        embeddings = self.generate_embeddings(chunks)

        with self.conn.cursor() as cur:
            if existing:
                # Update existing
                doc_id = existing[0]
                cur.execute("""
                    UPDATE ph_tax.docs
                    SET content = %s,
                        embedding = %s::vector,
                        updated_at = NOW(),
                        title = %s,
                        doc_type = %s,
                        doc_date = %s
                    WHERE id = %s
                """, (
                    content,
                    embeddings[0],  # Use first chunk embedding as doc embedding
                    doc_info.get('title', ''),
                    doc_info.get('doc_type', 'Unknown'),
                    doc_info.get('doc_date'),
                    doc_id
                ))
                logger.info(f"Updated document {doc_id}: {doc_info.get('title', doc_info['url'])}")
            else:
                # Insert new
                cur.execute("""
                    INSERT INTO ph_tax.docs (
                        source_url, title, doc_type, doc_date,
                        content, embedding, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s::vector, %s)
                    RETURNING id
                """, (
                    doc_info['url'],
                    doc_info.get('title', ''),
                    doc_info.get('doc_type', 'Unknown'),
                    doc_info.get('doc_date'),
                    content,
                    embeddings[0],
                    {}
                ))
                doc_id = cur.fetchone()[0]
                logger.info(f"Inserted document {doc_id}: {doc_info.get('title', doc_info['url'])}")

        self.conn.commit()

    def ingest_pdf(self, doc_info: Dict[str, Any]):
        """Ingest a PDF document"""
        logger.info(f"Ingesting PDF: {doc_info['title']}")
        content = self.extract_pdf_text(doc_info['url'])
        self.upsert_document(doc_info, content)

    def ingest_webpage(self, doc_info: Dict[str, Any]):
        """Ingest a webpage"""
        logger.info(f"Ingesting webpage: {doc_info['url']}")
        content = self.scrape_webpage(doc_info['url'])

        # Use URL as title if not provided
        if 'title' not in doc_info:
            doc_info['title'] = doc_info['url']

        self.upsert_document(doc_info, content)

    def run(self):
        """Run full ingestion pipeline"""
        self.connect()

        try:
            # Ingest official PDFs
            for doc in BIR_DOCUMENTS:
                self.ingest_pdf(doc)

            # Scrape BIR pages
            for page in BIR_PAGES_TO_SCRAPE:
                self.ingest_webpage(page)

            logger.info("Ingestion complete!")

        finally:
            self.close()


if __name__ == "__main__":
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        logger.error("DATABASE_URL environment variable not set")
        exit(1)

    ingestor = BIRIngestor(db_url)
    ingestor.run()
