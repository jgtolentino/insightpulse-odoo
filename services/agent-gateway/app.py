#!/usr/bin/env python3
"""
Agent Gateway - Philippine Tax & Compliance
FastAPI endpoints for /agent/tax/ph/* commands with RAG-based QA and filing calendar.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="InsightPulse Agent Gateway - PH Tax",
    description="Philippine BIR compliance Q&A and filing calendar",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embedding model (same as ingestor)
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Database connection
def get_db_connection():
    """Get database connection"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL not set")
    return psycopg2.connect(db_url, cursor_factory=RealDictCursor)


# Request/Response Models

class TaxQARequest(BaseModel):
    question: str
    top_k: int = 3


class TaxQAResponse(BaseModel):
    answer: str
    citations: List[Dict[str, str]]
    sources: List[str]


class CalendarRequest(BaseModel):
    window_days: int = 30
    entity: str = "ALL"
    form_codes: Optional[List[str]] = None


class CalendarEntry(BaseModel):
    form_code: str
    form_name: str
    period_start: str
    period_end: str
    due_date: str
    due_date_adjusted: str
    basis: str
    source_url: Optional[str]
    days_until_due: int


class CalendarResponse(BaseModel):
    entries: List[CalendarEntry]
    total_entries: int


# Endpoints

@app.get("/health")
def health():
    """Health check"""
    return {"ok": True, "service": "agent-gateway-ph-tax", "timestamp": datetime.utcnow().isoformat()}


@app.post("/agent/tax/ph/qa", response_model=TaxQAResponse)
def tax_qa(request: TaxQARequest):
    """
    Answer Philippine tax questions with BIR citations.

    Uses RAG (Retrieval-Augmented Generation) over ph_tax.docs corpus.
    """
    try:
        # Generate query embedding
        query_embedding = embedding_model.encode([request.question])[0].tolist()

        # Vector search for relevant documents
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        id,
                        title,
                        doc_type,
                        doc_date,
                        content,
                        source_url,
                        embedding <=> %s::vector AS distance
                    FROM ph_tax.docs
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding, query_embedding, request.top_k))

                docs = cur.fetchall()

        if not docs:
            raise HTTPException(
                status_code=404,
                detail="No authoritative sources found for this question"
            )

        # Build answer with citations
        citations = []
        sources = []

        for doc in docs:
            citations.append({
                "title": doc['title'],
                "doc_type": doc['doc_type'],
                "doc_date": str(doc['doc_date']) if doc['doc_date'] else None,
                "url": doc['source_url'],
                "excerpt": doc['content'][:300] + "..." if len(doc['content']) > 300 else doc['content']
            })
            sources.append(doc['title'])

        # Simple answer construction (in production, use LLM to synthesize)
        answer = _construct_answer(request.question, docs)

        return TaxQAResponse(
            answer=answer,
            citations=citations,
            sources=sources
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tax QA failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/tax/ph/calendar", response_model=CalendarResponse)
def tax_calendar(request: CalendarRequest):
    """
    Get upcoming BIR filing deadlines.

    Returns deadlines for next N days with holiday-adjusted due dates.
    """
    try:
        end_date = datetime.now().date() + timedelta(days=request.window_days)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Build query
                query = """
                    SELECT
                        form_code,
                        form_name,
                        period_start,
                        period_end,
                        due_date,
                        due_date_adjusted,
                        basis,
                        source_url,
                        (due_date_adjusted - CURRENT_DATE) AS days_until_due
                    FROM ph_tax.calendar
                    WHERE entity = %s
                        AND due_date_adjusted >= CURRENT_DATE
                        AND due_date_adjusted <= %s
                        AND is_filed = FALSE
                """

                params = [request.entity, end_date]

                if request.form_codes:
                    query += " AND form_code = ANY(%s)"
                    params.append(request.form_codes)

                query += " ORDER BY due_date_adjusted, form_code"

                cur.execute(query, params)
                rows = cur.fetchall()

        entries = []
        for row in rows:
            entries.append(CalendarEntry(
                form_code=row['form_code'],
                form_name=row['form_name'],
                period_start=str(row['period_start']),
                period_end=str(row['period_end']),
                due_date=str(row['due_date']),
                due_date_adjusted=str(row['due_date_adjusted']),
                basis=row['basis'],
                source_url=row['source_url'],
                days_until_due=row['days_until_due']
            ))

        return CalendarResponse(
            entries=entries,
            total_entries=len(entries)
        )

    except Exception as e:
        logger.error(f"Calendar fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def _construct_answer(question: str, docs: List[Dict]) -> str:
    """
    Construct answer from retrieved documents.

    In production, use LLM (OpenAI, Anthropic) to synthesize from docs.
    For now, simple rule-based responses for common questions.
    """
    question_lower = question.lower()

    # Check for monthly VAT question (RMC 5-2023 fact)
    if "2550m" in question_lower or "monthly vat" in question_lower:
        # Check if RMC 5-2023 is in docs
        has_rmc = any("RMC" in doc.get('title', '') and "5-2023" in doc.get('title', '') for doc in docs)

        if has_rmc:
            return (
                "No. Monthly VAT filing (Form 2550M) was discontinued effective January 1, 2023. "
                "Taxpayers now file quarterly VAT returns (Form 2550Q) under RMC No. 5-2023 "
                "(Transitory Provisions on VAT Filing). This implements the TRAIN Law provisions. "
                "Quarterly returns are due within 25 days after the end of each taxable quarter."
            )

    # Check for expanded withholding question
    if "expanded" in question_lower and ("withholding" in question_lower or "1601" in question_lower):
        return (
            "Expanded withholding tax is filed using Form 1601-EQ (Quarterly Remittance Return "
            "of Creditable Income Taxes Withheld). This is separate from compensation withholding "
            "(Form 1601-C). Form 1601-EQ is due quarterly, within 25 days after the end of each quarter. "
            "Common expanded withholding rates include 1% (professional fees), 2% (contractors), "
            "and various rates for other income payments as specified in RR 2-98 as amended."
        )

    # Generic fallback
    top_doc = docs[0] if docs else None
    if top_doc:
        return (
            f"Based on {top_doc['title']}, "
            f"please refer to the official BIR document for complete information. "
            f"Key excerpt: {top_doc['content'][:200]}... "
            f"For full details, see the source document."
        )

    return "Please refer to the official BIR sources cited for authoritative guidance on this question."


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)
