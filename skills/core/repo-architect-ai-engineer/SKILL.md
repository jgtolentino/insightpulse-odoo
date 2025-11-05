# Repository Architect & AI Engineering Expert

**Skill ID:** `repo-architect-ai-engineer`
**Version:** 1.0.0
**Last Updated:** 2025-11-05
**Category:** Infrastructure, AI/LLM Engineering, DevOps
**Expertise Level:** Expert (10+ years equivalent)

---

## 🎯 Purpose

This skill enables an AI agent to design, architect, and implement enterprise-grade repository structures with comprehensive AI/LLM engineering capabilities, including:

- Monorepo vs polyrepo architecture decisions
- AI/LLM pipeline design and implementation
- Evaluation frameworks and testing strategies
- Prompt engineering workflows
- Observability and monitoring
- CI/CD automation
- Security and compliance

---

## 🧠 Core Competencies

### 1. Software Architecture & System Design

#### 1.1 Repository Architecture
**Expertise Required:**
- ✅ Monorepo design patterns (Nx, Turborepo, Lerna)
- ✅ Polyrepo orchestration strategies
- ✅ Module boundaries and separation of concerns
- ✅ Dependency management (git submodules, npm workspaces)
- ✅ Build system optimization (Make, Bazel, Gradle)
- ✅ Code organization patterns (Domain-Driven Design, Clean Architecture)

**Evaluation Criteria:**
```python
Can design a repo structure that:
- Supports 50+ microservices
- Enables independent deployment
- Maintains code reusability
- Minimizes build times (<5 min for full build)
- Supports multiple programming languages
```

**Example Artifacts:**
- `/docs/architecture/system-diagram.mmd`
- `/docs/architecture/decisions/0001-monorepo-structure.md`
- Project root `Makefile` with common commands

---

#### 1.2 Microservices & Distributed Systems
**Expertise Required:**
- ✅ Service mesh design (Istio, Linkerd)
- ✅ API gateway patterns (Kong, Nginx)
- ✅ Event-driven architecture (Kafka, RabbitMQ)
- ✅ Distributed tracing (Jaeger, Tempo)
- ✅ Service discovery (Consul, etcd)
- ✅ Circuit breakers and resilience patterns

**Evaluation Criteria:**
```python
Can architect a system that:
- Handles 10k+ requests/second
- Maintains 99.95% uptime
- Recovers from partial failures
- Traces requests across 20+ services
```

**Example Artifacts:**
- `/infrastructure/api-gateway/`
- `/events/schemas/`
- `/docs/architecture/event-driven-architecture.md`

---

### 2. AI/LLM Engineering

#### 2.1 Prompt Engineering
**Expertise Required:**
- ✅ Zero-shot, few-shot, chain-of-thought prompting
- ✅ Prompt versioning and A/B testing
- ✅ Token optimization techniques
- ✅ System prompt design for role-based behavior
- ✅ Structured output extraction (JSON, XML)
- ✅ Multi-modal prompting (text + image)

**Evaluation Criteria:**
```python
Can create prompts that:
- Achieve >95% accuracy on domain tasks
- Maintain consistency across 1000+ runs
- Optimize token usage by 30%+
- Handle edge cases gracefully
- Support multi-language inputs
```

**Example Artifacts:**
- `/prompts/templates/document-extraction/receipt-parser.md`
- `/prompts/versions/receipt-parser/v2.1.0.md`
- `/prompt-ops/experiments/a-b-tests/`

**Key Frameworks:**
- LangChain, LlamaIndex
- DSPy (declarative prompting)
- Guidance (Microsoft)

---

#### 2.2 Retrieval Augmented Generation (RAG)
**Expertise Required:**
- ✅ Vector database selection (Qdrant, Pinecone, Weaviate, pgvector)
- ✅ Embedding strategies (OpenAI, Cohere, Sentence Transformers)
- ✅ Chunking strategies (recursive, semantic, document-aware)
- ✅ Retrieval optimization (MMR, hybrid search, reranking)
- ✅ Context window management
- ✅ RAG pipeline patterns (simple, conversational, agentic)

**Evaluation Criteria:**
```python
Can build RAG systems that:
- Retrieve relevant docs with >90% precision
- Handle 1M+ document corpus
- Respond in <2 seconds
- Support conversational context
- Cost <$0.01 per query
```

**Example Artifacts:**
- `/context-engineering/rag/pipelines/conversational-rag.py`
- `/context-engineering/rag/embeddings/text-splitters/`
- `/context-engineering/rag/vector-stores/qdrant-config.yml`

**Key Techniques:**
- Parent-document retrieval
- Multi-query retrieval
- Hypothetical document embeddings (HyDE)
- Self-RAG

---

#### 2.3 AI Evaluation & Testing
**Expertise Required:**
- ✅ Metrics design (accuracy, precision, recall, F1, BLEU, ROUGE)
- ✅ Human evaluation protocols
- ✅ Benchmark dataset creation
- ✅ Regression testing strategies
- ✅ A/B testing frameworks
- ✅ Statistical significance testing

**Evaluation Criteria:**
```python
Can create eval systems that:
- Test 1000+ cases in <10 minutes
- Detect 2% accuracy regressions
- Cost <$10 per full eval run
- Generate actionable reports
- Support automated CI/CD integration
```

**Example Artifacts:**
- `/evals/datasets/receipt-extraction/test-cases.json`
- `/evals/benchmarks/ocr-benchmark.py`
- `/evals/metrics/accuracy/exact-match.py`
- `/.github/workflows/ai-eval-on-pr.yml`

**Key Frameworks:**
- OpenAI Evals
- LangSmith Evaluations
- Anthropic Claude Evals

---

#### 2.4 LLMOps & Model Management
**Expertise Required:**
- ✅ Model versioning and registry
- ✅ Fine-tuning workflows (LoRA, QLoRA, full fine-tuning)
- ✅ Model deployment strategies (API, self-hosted, edge)
- ✅ Cost optimization (caching, batching, model selection)
- ✅ Observability (tracing, logging, metrics)
- ✅ Guardrails and safety mechanisms

**Evaluation Criteria:**
```python
Can manage LLM systems that:
- Deploy new models in <1 hour
- Track all predictions for auditing
- Cost optimize by 40%+
- Maintain 99.9% availability
- Block 99%+ of adversarial inputs
```

**Example Artifacts:**
- `/llm-ops/model-management/model-registry.yml`
- `/llm-ops/fine-tuning/datasets/bir-form-extraction.jsonl`
- `/guardrails/input-validation/prompt-injection-detector.py`
- `/ai-observability/dashboards/llm-performance.json`

**Key Tools:**
- LangSmith, Arize Phoenix, Weights & Biases
- MLflow for model tracking
- BentoML for serving

---

#### 2.5 Prompt Operations (PromptOps)
**Expertise Required:**
- ✅ Prompt versioning strategies
- ✅ Automated prompt optimization
- ✅ Deployment pipelines for prompts
- ✅ Rollback mechanisms
- ✅ Feature flags for prompts
- ✅ Cost tracking per prompt version

**Evaluation Criteria:**
```python
Can implement PromptOps that:
- Versions all prompts with Git
- A/B tests new prompts automatically
- Rolls back failing prompts in <5 min
- Tracks cost per prompt version
- Optimizes prompts for token reduction
```

**Example Artifacts:**
- `/prompt-ops/registry/catalog.yml`
- `/prompt-ops/experiments/a-b-tests/`
- `/prompt-ops/deployment/production-prompts/`

---

### 3. DevOps & Infrastructure

#### 3.1 CI/CD Pipelines
**Expertise Required:**
- ✅ GitHub Actions, GitLab CI, Jenkins
- ✅ Multi-stage build optimization
- ✅ Automated testing (unit, integration, E2E)
- ✅ Security scanning (Trivy, Snyk, Semgrep)
- ✅ Deployment strategies (blue-green, canary, rolling)
- ✅ Rollback automation

**Evaluation Criteria:**
```python
Can create CI/CD that:
- Runs full pipeline in <15 minutes
- Catches 95%+ of bugs pre-production
- Deploys 10+ times per day
- Auto-rolls back on failure
- Costs <$100/month
```

**Example Artifacts:**
- `/.github/workflows/01-lint-and-validate.yml`
- `/.github/workflows/08-deploy-production.yml`
- `/.github/workflows/12-auto-heal.yml`

---

#### 3.2 Infrastructure as Code (IaC)
**Expertise Required:**
- ✅ Terraform, Pulumi, CloudFormation
- ✅ Ansible, Chef, Puppet
- ✅ Docker & Docker Compose
- ✅ Kubernetes (K8s) manifests
- ✅ Helm charts
- ✅ GitOps (ArgoCD, Flux)

**Evaluation Criteria:**
```python
Can provision infrastructure that:
- Deploys full stack in <10 minutes
- Is reproducible across environments
- Manages 50+ cloud resources
- Supports disaster recovery (RPO < 1 hour)
- Costs optimized by 30%+
```

**Example Artifacts:**
- `/infrastructure/terraform/main.tf`
- `/infrastructure/ansible/playbooks/deploy-odoo.yml`
- `/infrastructure/docker/docker-compose.yml`

---

#### 3.3 Observability & Monitoring
**Expertise Required:**
- ✅ Prometheus metrics design
- ✅ Grafana dashboard creation
- ✅ Loki log aggregation
- ✅ Distributed tracing (Tempo, Jaeger)
- ✅ Alerting rules (Alertmanager)
- ✅ SLI/SLO/SLA definition

**Evaluation Criteria:**
```python
Can implement observability that:
- Collects 100+ metrics per service
- Provides <1 minute alert latency
- Traces requests across 20+ services
- Retains logs for 90 days
- Dashboards load in <2 seconds
```

**Example Artifacts:**
- `/monitoring/prometheus/prometheus.yml`
- `/monitoring/grafana/dashboards/system-overview.json`
- `/monitoring/alertmanager/alertmanager.yml`
- `/docs/observability/sli-slo-sla.md`

---

#### 3.4 Auto-Healing & Resilience
**Expertise Required:**
- ✅ Health check design
- ✅ Self-healing scripts
- ✅ Chaos engineering (Chaos Monkey)
- ✅ Circuit breakers
- ✅ Retry strategies with exponential backoff
- ✅ Graceful degradation

**Evaluation Criteria:**
```python
Can build systems that:
- Detect failures in <30 seconds
- Auto-recover from 80%+ of failures
- Handle 5x traffic spikes
- Maintain 99.95% uptime
- Pass chaos testing
```

**Example Artifacts:**
- `/auto-healing/health-checks/odoo-health.sh`
- `/auto-healing/recovery-scripts/restart-odoo.sh`
- `/auto-healing/chaos-engineering/kill-random-pod.sh`

---

### 4. Security & Compliance

#### 4.1 Application Security
**Expertise Required:**
- ✅ OWASP Top 10 mitigation
- ✅ Secrets management (Vault, Sealed Secrets)
- ✅ SAST/DAST scanning
- ✅ Dependency vulnerability scanning
- ✅ Container security (Trivy, Clair)
- ✅ API security (rate limiting, authentication)

**Evaluation Criteria:**
```python
Can secure systems that:
- Pass OWASP ZAP scan with 0 high-severity issues
- Rotate secrets every 90 days
- Detect vulnerabilities in <24 hours
- Block 99%+ of malicious requests
- Maintain least-privilege access
```

**Example Artifacts:**
- `/secrets/vault/config.hcl`
- `/guardrails/input-validation/prompt-injection-detector.py`
- `/.github/workflows/04-security-scan.yml`

---

#### 4.2 Compliance & Auditing
**Expertise Required:**
- ✅ SOC 2 controls implementation
- ✅ GDPR compliance (data privacy)
- ✅ HIPAA compliance (healthcare data)
- ✅ ISO 27001 (information security)
- ✅ Audit trail design
- ✅ Compliance documentation

**Evaluation Criteria:**
```python
Can implement compliance that:
- Tracks all data access
- Retains audit logs for 7 years
- Supports right-to-erasure (GDPR)
- Passes SOC 2 Type II audit
- Encrypts all PII
```

**Example Artifacts:**
- `/compliance/soc2/controls-matrix.xlsx`
- `/compliance/gdpr/data-inventory.md`
- `/docs/security/audit-procedures.md`

---

### 5. Knowledge Management & Documentation

#### 5.1 Technical Documentation
**Expertise Required:**
- ✅ Architecture Decision Records (ADRs)
- ✅ API documentation (OpenAPI, GraphQL)
- ✅ Runbooks for operations
- ✅ Knowledge base creation
- ✅ Documentation-as-code
- ✅ Auto-generated docs (Sphinx, Doxygen)

**Evaluation Criteria:**
```python
Can create documentation that:
- Is searchable in <1 second
- Covers 95%+ of use cases
- Is auto-updated on code changes
- Includes runnable examples
- Passes readability tests (Flesch-Kincaid)
```

**Example Artifacts:**
- `/docs/architecture/decisions/0001-monorepo-structure.md`
- `/docs/api/openapi.yml`
- `/docs/runbooks/incidents/database-down.md`

---

#### 5.2 Skills Library Management
**Expertise Required:**
- ✅ Claude Skills format (SKILL.md)
- ✅ Skill categorization and tagging
- ✅ Version control for skills
- ✅ Skill indexing and search
- ✅ Auto-generation of skills from code
- ✅ Skill effectiveness tracking

**Evaluation Criteria:**
```python
Can manage skills library that:
- Contains 50+ domain-specific skills
- Updates automatically from codebase
- Enables AI to find relevant skills in <5s
- Tracks skill usage and effectiveness
- Versions skills with semantic versioning
```

**Example Artifacts:**
- `/skills/README.md`
- `/skills/core/odoo-agile-scrum-devops/SKILL.md`
- `/skills/librarian-indexer/SKILL.md` (meta-skill)

---

### 6. Data Engineering

#### 6.1 Database Design
**Expertise Required:**
- ✅ Relational design (PostgreSQL, MySQL)
- ✅ NoSQL design (MongoDB, Cassandra)
- ✅ Vector databases (Qdrant, Pinecone)
- ✅ Time-series databases (TimescaleDB, InfluxDB)
- ✅ Data warehousing (Snowflake, BigQuery)
- ✅ Query optimization

**Evaluation Criteria:**
```python
Can design databases that:
- Handle 1M+ records with <100ms queries
- Support 10k+ concurrent connections
- Maintain ACID properties
- Enable full-text search in <50ms
- Back up incrementally every hour
```

**Example Artifacts:**
- `/infrastructure/docker/postgres/init-scripts/`
- `/migrations/schema-changes/add-bir-fields.sql`

---

#### 6.2 Data Pipelines & ETL
**Expertise Required:**
- ✅ Airflow, Dagster, Prefect
- ✅ Kafka, RabbitMQ for streaming
- ✅ dbt for transformations
- ✅ Data quality checks
- ✅ Schema evolution strategies
- ✅ Data lineage tracking

**Evaluation Criteria:**
```python
Can build pipelines that:
- Process 1M+ records/hour
- Maintain 99.9% data quality
- Support backfills for 1 year
- Track data lineage end-to-end
- Cost <$500/month
```

---

### 7. Business Domain Expertise

#### 7.1 Finance & Accounting
**Expertise Required:**
- ✅ Double-entry bookkeeping
- ✅ Financial statements (P&L, Balance Sheet, Cash Flow)
- ✅ Month-end closing procedures
- ✅ General Ledger (GL) structure
- ✅ Chart of accounts design
- ✅ Tax compliance (VAT, withholding tax)

**Domain Knowledge:**
```
Philippines BIR Compliance:
- Form 1601-C (Monthly Remittance Return)
- Form 1702-RT (Annual Income Tax Return)
- Form 2550Q (Quarterly VAT Return)
- ATP (Authorization to Print) requirements
- COR (Certificate of Registration)
- Alphanumeric Tax Code (ATC) system
```

**Example Artifacts:**
- `/custom/finance_ssc/month_end_closing/`
- `/custom/bir_compliance/`
- `/data/localization/ph-chart-of-accounts.csv`

---

#### 7.2 Procurement & Supply Chain
**Expertise Required:**
- ✅ Purchase requisition workflows
- ✅ RFQ/RFP processes
- ✅ Three-way matching (PO-GR-Invoice)
- ✅ Vendor management
- ✅ Contract lifecycle management
- ✅ Inventory optimization

---

#### 7.3 Expense Management
**Expertise Required:**
- ✅ Travel & expense policies
- ✅ Receipt validation rules
- ✅ Approval workflows (multi-level)
- ✅ GL posting automation
- ✅ Per diem calculations
- ✅ Mileage reimbursement

---

### 8. AI Safety & Ethics

#### 8.1 AI Guardrails
**Expertise Required:**
- ✅ Prompt injection detection
- ✅ PII/PHI redaction
- ✅ Toxicity filtering
- ✅ Bias detection and mitigation
- ✅ Hallucination detection
- ✅ Output validation

**Evaluation Criteria:**
```python
Can implement guardrails that:
- Block 99.9% of prompt injections
- Redact 100% of credit card numbers
- Detect hallucinations with 90%+ accuracy
- Filter toxic content with 95%+ precision
- Cost <$0.001 per request
```

**Example Artifacts:**
- `/guardrails/input-validation/prompt-injection-detector.py`
- `/guardrails/output-validation/hallucination-detector.py`

---

#### 8.2 Responsible AI
**Expertise Required:**
- ✅ Fairness metrics (demographic parity, equal opportunity)
- ✅ Explainability (LIME, SHAP)
- ✅ Privacy preservation (differential privacy)
- ✅ Model cards and documentation
- ✅ Red teaming
- ✅ Human oversight mechanisms

---

## 🛠️ Tools & Technologies Mastery

### Programming Languages
- ✅ **Python** (Expert) - Primary for AI/ML, automation
- ✅ **JavaScript/TypeScript** (Advanced) - Frontend, n8n workflows
- ✅ **Bash/Shell** (Expert) - Automation scripts
- ✅ **SQL** (Expert) - Database queries, migrations
- ✅ **YAML** (Expert) - Configuration files
- ✅ **Markdown** (Expert) - Documentation

### Frameworks & Libraries
**AI/ML:**
- LangChain, LlamaIndex
- OpenAI Python SDK
- Anthropic SDK
- Transformers (HuggingFace)
- PyTorch (for custom models)

**Web/Backend:**
- Odoo ORM
- FastAPI, Flask
- Celery (task queues)

**Testing:**
- pytest, unittest
- Playwright, Cypress (E2E)
- k6, Locust (load testing)

### Infrastructure
**Cloud Providers:**
- DigitalOcean (primary)
- AWS, GCP, Azure (secondary)

**Containerization:**
- Docker, Docker Compose
- Kubernetes (K8s)

**Databases:**
- PostgreSQL (+ pgvector)
- Redis
- Qdrant

**Message Queues:**
- RabbitMQ
- Kafka (optional)

**Monitoring:**
- Prometheus + Grafana
- Loki (logs)
- Tempo (traces)

### AI/LLM Services
- OpenAI (GPT-4o, GPT-4o-mini)
- Anthropic Claude (Sonnet, Opus)
- Cohere (embeddings)
- HuggingFace (open-source models)

---

## 📋 Competency Validation

### Self-Assessment Checklist

**Repository Architecture** (20 points)
- [ ] Can design monorepo structure for 50+ modules (5 pts)
- [ ] Can implement efficient build system (5 pts)
- [ ] Can establish clear module boundaries (5 pts)
- [ ] Can document architecture decisions (ADRs) (5 pts)

**AI/LLM Engineering** (30 points)
- [ ] Can create effective prompts (95%+ accuracy) (10 pts)
- [ ] Can build RAG systems (>90% retrieval precision) (10 pts)
- [ ] Can design evaluation frameworks (10 pts)

**DevOps/Infrastructure** (20 points)
- [ ] Can write CI/CD pipelines (<15 min runtime) (7 pts)
- [ ] Can implement auto-healing (80%+ recovery rate) (7 pts)
- [ ] Can set up observability (Prometheus + Grafana) (6 pts)

**Security & Compliance** (15 points)
- [ ] Can implement AI guardrails (99%+ attack blocking) (8 pts)
- [ ] Can ensure compliance (SOC 2, GDPR) (7 pts)

**Documentation & Knowledge** (15 points)
- [ ] Can write clear ADRs (5 pts)
- [ ] Can create runbooks (5 pts)
- [ ] Can manage skills library (5 pts)

**Total Score:** ___/100

**Expertise Levels:**
- 90-100: Expert (can lead implementation)
- 75-89: Advanced (can implement with guidance)
- 60-74: Intermediate (needs supervision)
- <60: Beginner (needs training)

---

## 🎯 Usage Examples

### Example 1: Restructure Existing Repo
```
Human: We need to add AI evaluation framework to our existing Odoo repo.

Agent (with this skill): I'll add comprehensive AI evaluation infrastructure:

1. Create evaluation directory structure:
   - /evals/datasets/
   - /evals/metrics/
   - /evals/benchmarks/

2. Implement evaluation framework:
   - OCR benchmark for receipt extraction
   - Classification metrics for expense categories
   - Regression testing for prompt versions

3. Integrate with CI/CD:
   - GitHub Actions workflow for PR evaluation
   - Automated regression detection
   - Cost tracking

[Proceeds to implement with detailed code examples]
```

---

### Example 2: Design New AI Feature
```
Human: We want to add semantic search to our knowledge base.

Agent (with this skill): I'll design a complete RAG pipeline:

1. Context Engineering:
   - pgvector for vector storage
   - OpenAI embeddings (text-embedding-3-large)
   - Recursive text splitter with 1000 token chunks

2. Retrieval Strategy:
   - Hybrid search (semantic + keyword)
   - MMR for diversity
   - Reranking with Cohere

3. Evaluation:
   - Test dataset with 500 Q&A pairs
   - Metrics: precision@5, MRR, latency
   - Benchmark: >90% precision, <2s response

4. Observability:
   - Track query latency
   - Monitor retrieval accuracy
   - Cost per query

[Provides implementation files with code]
```

---

### Example 3: Implement Auto-Healing
```
Human: Our Odoo instance crashes sometimes. Can we auto-heal?

Agent (with this skill): I'll implement comprehensive auto-healing:

1. Health Checks:
   - HTTP endpoint monitoring (/web/health)
   - PostgreSQL connection check
   - Disk space monitoring
   - Memory usage tracking

2. Recovery Scripts:
   - Restart Odoo if crashed
   - Clear cache if memory high
   - Kill long-running queries
   - Scale horizontally if CPU > 80%

3. Automation:
   - GitHub Actions workflow (every 5 min)
   - Slack notifications
   - Incident log creation

4. Chaos Testing:
   - Random pod killing
   - Network latency injection
   - Validate recovery time < 5 min

[Creates all necessary files]
```

---

## 📚 Learning Resources

### Books
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Building LLMs for Production" by Chip Huyen
- "Prompt Engineering Guide" by DAIR.AI
- "Site Reliability Engineering" by Google

### Courses
- Fast.ai: Practical Deep Learning
- DeepLearning.AI: LangChain courses
- Andrew Ng: Machine Learning Specialization

### Documentation
- LangChain Docs: https://python.langchain.com
- Odoo Documentation: https://www.odoo.com/documentation/19.0/
- OCA Guidelines: https://odoo-community.org/
- Prometheus Best Practices

---

## 🔄 Continuous Improvement

### Skill Update Triggers
- New AI/LLM techniques published
- Framework major version releases
- Security vulnerabilities discovered
- Business requirements change
- Performance bottlenecks identified

### Feedback Loop
1. Implementation experience
2. Metric tracking (what works/doesn't)
3. Peer review
4. User feedback
5. Skill refinement

---

## 🎓 Skill Dependencies

**Prerequisites:**
- Software engineering fundamentals
- Linux/Unix proficiency
- Git/GitHub expertise
- SQL and database concepts
- Python programming

**Related Skills:**
- `odoo-agile-scrum-devops` - Odoo-specific workflows
- `mcp-complete-guide` - MCP server development
- `librarian-indexer` - Skill management meta-skill
- `superset-dashboard-automation` - BI/analytics

---

## 📊 Success Metrics

**Repository Quality:**
- Build time < 15 minutes
- Test coverage > 80%
- Documentation coverage > 90%

**AI/LLM Performance:**
- Accuracy > 95%
- Latency < 2 seconds
- Cost < budget

**System Reliability:**
- Uptime > 99.9%
- MTTR < 5 minutes
- Auto-recovery rate > 80%

**Developer Experience:**
- Onboarding time < 1 day
- Deployment frequency > 10/day
- Lead time < 1 hour

---

## 📞 Support & Community

**GitHub Discussions:** https://github.com/jgtolentino/insightpulse-odoo/discussions
**Slack Channel:** #ai-engineering
**Office Hours:** Every Friday 3-4 PM

---

**Maintained by:** Jake Tolentino
**Contributors:** InsightPulse AI Team
**License:** AGPL-3.0
