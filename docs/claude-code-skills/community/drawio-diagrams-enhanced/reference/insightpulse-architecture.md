# Example: InsightPulse AI System Architecture

## Use Case
Create a technical architecture diagram for InsightPulse AI - a self-hosted Odoo ERP with AI-powered document processing.

## Request to Claude

```
Create a network/system architecture diagram for InsightPulse AI with the following components:

**Application Layer:**
- Odoo 18/19 ERP (self-hosted)
  - Expense Management Module
  - Travel Management Module
  - Document Management Module

**AI/OCR Processing Layer:**
- PaddleOCR-VL (Vision-Language Model)
  - Receipt OCR
  - Invoice OCR
  - Travel document OCR
- Vector Database: Qdrant
  - Document embeddings
  - Semantic search

**Database Layer:**
- PostgreSQL (Odoo primary database)
- pgvector extension (for vector operations)
- Supabase (project: spdtwktxdalcfigzeqrz)
  - User authentication
  - API gateway
  - Real-time subscriptions

**Infrastructure Layer:**
- DigitalOcean (project ID: 29cde7a1-8280-46ad-9fdf-dea7b21a7825)
  - Docker containers
  - Load balancer
  - Object storage for documents
- On-premise GPU server
  - NVIDIA RTX 4090 (for OCR processing)

**Data Flow:**
1. User uploads document → Odoo
2. Document sent to PaddleOCR-VL → OCR processing
3. Extracted text + embeddings → Qdrant
4. Structured data → PostgreSQL
5. Audit trail → Supabase

**Color Scheme:**
- Odoo/ERP: Blue (#1ba1e2)
- AI/OCR: Orange (#FFA500)
- Databases: Green (#60a917)
- Infrastructure: Gray (#666666)

**Additional:**
- Show data flow arrows with labels
- Indicate API connections (REST, GraphQL)
- Mark secure connections (SSL/TLS)
- Show Docker container boundaries
```

## Expected Output
A comprehensive network diagram with:
- Clear component boxes organized by layer
- Data flow arrows with labels
- Color-coded by function
- Docker container groupings
- Network connections properly illustrated
- Professional cloud architecture styling

## Follow-up Requests

- "Add authentication flow using Supabase Auth"
- "Show the expense approval workflow through the system"
- "Include monitoring and logging components"
- "Add a CI/CD pipeline diagram"
- "Create a deployment sequence diagram"
