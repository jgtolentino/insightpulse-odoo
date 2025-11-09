# Architecture Documentation

This directory contains architecture documentation, system diagrams, and architectural decision records (ADRs).

## 📁 Contents

- **System Diagrams**: High-level system architecture
- **ADRs**: Architecture Decision Records
- **Component Diagrams**: Detailed component designs
- **Data Flow**: Data flow and integration patterns

## 🏗️ Architecture Overview

InsightPulse Odoo follows a layered architecture:

1. **Presentation Layer**: Odoo Web UI
2. **Application Layer**: Odoo Business Logic
3. **Data Layer**: PostgreSQL + pgvector
4. **Integration Layer**: APIs, MCP servers
5. **AI/ML Layer**: LLM integration, RAG systems

## 📊 Key Components

### Core Services
- **Odoo 19**: ERP application
- **PostgreSQL**: Relational database
- **Superset**: Business intelligence
- **n8n**: Workflow automation

### AI Stack
- **Qdrant**: Vector database
- **Context Engineering**: RAG systems
- **Guardrails**: AI safety

## 🔗 Related Documentation

- [Main README](../../README.md)
- [Infrastructure](../../infrastructure/README.md)
- [Deployment](../DEPLOYMENT.md)

---

For architectural decisions, see the `decisions/` subdirectory (ADRs).
