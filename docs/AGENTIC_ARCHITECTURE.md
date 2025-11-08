# PRODUCTION-READY AGENTIC ARCHITECTURE
## Comprehensive AI Agent System Design for InsightPulse AI

**Version:** 1.0
**Date:** 2025-11-08
**Status:** Active
**Owner:** InsightPulse AI Engineering Team

---

## TABLE OF CONTENTS

1. [Architecture Overview](#architecture-overview)
2. [3-Tier Agent Hierarchy](#3-tier-agent-hierarchy)
3. [Tier 1: Orchestrator Agents](#tier-1-orchestrator-agents)
4. [Tier 2: Domain Specialist Agents](#tier-2-domain-specialist-agents)
5. [Tier 3: Task Executor Agents](#tier-3-task-executor-agents)
6. [Knowledge Base Architecture](#knowledge-base-architecture)
7. [Production Readiness Framework](#production-readiness-framework)
8. [Implementation Guide](#implementation-guide)

---

## ARCHITECTURE OVERVIEW

### System Design Principles

```yaml
Principles:
  Modularity:
    - Each agent has a single, well-defined responsibility
    - Agents are composable (can be combined for complex workflows)
    - Loose coupling between agents

  Observability:
    - Every agent call is traced
    - Confidence scores tracked
    - Costs monitored per operation
    - Human escalation points logged

  Reliability:
    - Graceful degradation (fallback to human on low confidence)
    - State persistence (can resume after failures)
    - Retry logic with exponential backoff
    - Circuit breakers for failing dependencies

  Production_Quality:
    - Comprehensive testing (unit, integration, golden prompts)
    - SLA monitoring (latency, accuracy, cost)
    - Continuous learning (feedback loops)
    - Security-first design (input validation, auth, audit trails)
```

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Odoo Web UI  │  │ Mobile App   │  │ API Clients  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────────────┐
│                  API GATEWAY (Edge Function)                       │
│              Rate Limiting │ Auth │ Request Routing                │
└─────────────────────────────┼─────────────────────────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────────────┐
│               TIER 1: ORCHESTRATOR AGENTS                          │
│  ┌────────────────────────────────────────────────────────┐       │
│  │  MonthEndCloseOrchestrator                             │       │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │       │
│  │  │ Workflow │  │  State   │  │ Decision │            │       │
│  │  │  Engine  │  │Checkpoint│  │  Logic   │            │       │
│  │  └──────────┘  └──────────┘  └──────────┘            │       │
│  └────────────────┬───────────────────────────────────────┘       │
│                   │                                                │
│  ┌────────────────┼───────────────────────────────────────┐       │
│  │  BIRComplianceOrchestrator                             │       │
│  │  ┌──────────┐  │  ┌──────────┐  ┌──────────┐          │       │
│  │  │Tax Form  │  │  │Deadline  │  │E-Filing  │          │       │
│  │  │Generator │  │  │Tracking  │  │  RPA     │          │       │
│  │  └──────────┘  │  └──────────┘  └──────────┘          │       │
│  └────────────────┼───────────────────────────────────────┘       │
└───────────────────┼───────────────────────────────────────────────┘
                    │
                    │ (coordinates)
                    ┴
┌─────────────────────────────────────────────────────────────────┐
│               TIER 2: DOMAIN SPECIALIST AGENTS                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ReconciliationAgent│  │ExpenseValidation │  │Financial     │  │
│  │                  │  │     Agent        │  │Reporting     │  │
│  │ - Bank/GL match  │  │ - Policy check   │  │Agent         │  │
│  │ - ML fuzzy match │  │ - BIR compliance │  │ - P&L, BS    │  │
│  │ - Exception hdlg │  │ - Fraud detection│  │ - Cash flow  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ (uses)
                             ┴
┌─────────────────────────────────────────────────────────────────┐
│               TIER 3: TASK EXECUTOR AGENTS                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │OCRExtraction │  │DataValidation│  │PDFGeneration │          │
│  │   Agent      │  │    Agent     │  │    Agent     │          │
│  │              │  │              │  │              │          │
│  │ - PaddleOCR  │  │ - Schema val │  │ - Report gen │          │
│  │ - Field ext  │  │ - Business   │  │ - Formatting │          │
│  │              │  │   rules      │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ (accesses)
                             ┴
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Vector Store │  │  Knowledge   │  │  Relational  │          │
│  │   (Qdrant)   │  │    Graph     │  │   Database   │          │
│  │              │  │  (NetworkX)  │  │ (PostgreSQL) │          │
│  │ - BIR regs   │  │ - COA graph  │  │ - GL entries │          │
│  │ - Acct stds  │  │ - Tax rules  │  │ - Invoices   │          │
│  │ - Policies   │  │ - Approvals  │  │ - Payments   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ (stores in)
                             ┴
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ PostgreSQL   │  │    Redis     │  │  DigitalOcean│          │
│  │   (HA)       │  │   (Cache)    │  │    Spaces    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3-TIER AGENT HIERARCHY

### Hierarchy Design

```yaml
Tier_1_Orchestrator_Agents:
  purpose: "Strategic coordination, multi-agent workflow management"
  characteristics:
    - Manage complex workflows with 5+ steps
    - Coordinate multiple sub-agents
    - State persistence and checkpointing
    - Human-in-the-loop for exceptions
    - Rollback capability
  maturity_level_required: "Production V2 (Level 4)"
  examples:
    - MonthEndCloseOrchestrator
    - BIRComplianceOrchestrator
    - MultiEntityConsolidationOrchestrator

Tier_2_Domain_Specialist_Agents:
  purpose: "Deep expertise in specific business domains"
  characteristics:
    - Single domain focus (recon, expenses, tax, etc.)
    - ML models for predictions
    - RAG for domain knowledge
    - Self-contained (don't need other agents)
  maturity_level_required: "Production V1 (Level 3)"
  examples:
    - ReconciliationAgent
    - ExpenseValidationAgent
    - TaxCalculationAgent
    - FinancialReportingAgent

Tier_3_Task_Executor_Agents:
  purpose: "Narrow, specific tasks (single function)"
  characteristics:
    - Simple input/output
    - No complex decision-making
    - Fast execution (< 5 seconds)
    - Highly reusable
  maturity_level_required: "Beta (Level 2)"
  examples:
    - OCRExtractionAgent
    - DataValidationAgent
    - PDFGenerationAgent
    - EmailNotificationAgent
```

---

## TIER 1: ORCHESTRATOR AGENTS

### MonthEndCloseOrchestrator

**Purpose:** Automate the entire month-end closing process across multiple entities

#### Capabilities

```python
class MonthEndCloseOrchestrator(BaseAgent):
    """
    Master orchestrator for month-end closing.

    Coordinates 20+ sub-agents in a stateful workflow.
    Reduces close time from 12 days to < 3 days.
    """

    capabilities = {
        "workflow_management": {
            "pattern": "DAG-based with parallel execution",
            "state_persistence": "PostgreSQL + Redis",
            "checkpoint_frequency": "After each major step",
            "rollback_capability": True,
            "human_in_the_loop": [
                "final_approval",
                "exception_handling",
                "variance_review"
            ]
        },

        "coordination": {
            "manages_agents": [
                "ReconciliationAgent",
                "FinancialReportingAgent",
                "BIRComplianceAgent",
                "IntercompanyEliminationAgent",
                "DepreciationAgent",
                "AccrualAgent",
                "TrialBalanceValidator",
                "PeriodCloseAgent"
            ],
            "dependency_management": "Critical path analysis",
            "parallel_execution": "Up to 5 agents concurrently",
            "failure_handling": "Checkpoint rollback + human escalation"
        },

        "decision_making": {
            "prerequisites": "Check all dependencies before each step",
            "exception_detection": "Variance thresholds, balance checks",
            "adaptive_routing": "Skip steps if prerequisites not met",
            "confidence_threshold": 0.90,
            "escalation_logic": "Low confidence → human review"
        },

        "monitoring": {
            "progress_tracking": "Real-time dashboard",
            "sla_monitoring": "Alert if close at risk",
            "cost_tracking": "LLM token usage per step",
            "quality_metrics": "Accuracy, completeness per step"
        }
    }
```

#### Workflow Definition

```python
async def orchestrate_close(self, period: str, entities: List[str]) -> CloseResult:
    """
    Execute month-end closing workflow.

    Critical Path (8 steps):
    1. Bank Reconciliation (parallel by entity)
    2. AP/AR Reconciliation (parallel by entity)
    3. Intercompany Elimination (sequential, cross-entity)
    4. Depreciation & Accruals (parallel by entity)
    5. Trial Balance Validation (parallel by entity)
    6. Financial Reports Generation (sequential)
    7. BIR Compliance Check (sequential)
    8. Period Close & Lock (sequential)
    """

    # Initialize workflow state
    workflow = WorkflowState(
        id=self.generate_workflow_id(),
        period=period,
        entities=entities,
        status="initiated",
        started_at=datetime.utcnow(),
        checkpoints=[]
    )

    try:
        # ============================================
        # STEP 1: Bank Reconciliation (PARALLEL)
        # ============================================
        logger.info(f"Step 1/8: Bank reconciliation for {len(entities)} entities")

        bank_tasks = [
            ReconciliationAgent(
                entity=entity,
                account_type="bank",
                period=period
            ).execute()
            for entity in entities
        ]

        bank_results = await asyncio.gather(*bank_tasks, return_exceptions=True)

        # Check for failures
        failed = [r for r in bank_results if isinstance(r, Exception)]
        if failed:
            await self.escalate_to_human(
                workflow_id=workflow.id,
                step="bank_reconciliation",
                issue="Reconciliation failures detected",
                details=failed
            )
            await self.wait_for_resolution(workflow.id)

        await self.checkpoint(workflow, "bank_reconciliation", bank_results)

        # ============================================
        # STEP 2: AP/AR Reconciliation (PARALLEL)
        # ============================================
        logger.info(f"Step 2/8: AP/AR reconciliation")

        ar_ap_tasks = []
        for entity in entities:
            ar_ap_tasks.append(
                ReconciliationAgent(entity=entity, account_type="receivables").execute()
            )
            ar_ap_tasks.append(
                ReconciliationAgent(entity=entity, account_type="payables").execute()
            )

        ar_ap_results = await asyncio.gather(*ar_ap_tasks, return_exceptions=True)

        await self.checkpoint(workflow, "ar_ap_reconciliation", ar_ap_results)

        # ============================================
        # STEP 3: Intercompany Elimination (SEQUENTIAL)
        # ============================================
        if len(entities) > 1:
            logger.info(f"Step 3/8: Intercompany elimination")

            ic_result = await IntercompanyEliminationAgent(
                entities=entities,
                period=period
            ).execute()

            if ic_result.adjustments_required > 0:
                logger.warning(f"Intercompany adjustments required: {ic_result.adjustments_required}")
                await self.post_journal_entries(ic_result.journal_entries)

            await self.checkpoint(workflow, "intercompany_elimination", ic_result)

        # ============================================
        # STEP 4: Depreciation & Accruals (PARALLEL)
        # ============================================
        logger.info(f"Step 4/8: Depreciation & Accruals")

        depreciation_tasks = [
            DepreciationAgent(entity=e, period=period).execute()
            for e in entities
        ]

        accrual_tasks = [
            AccrualAgent(entity=e, period=period).execute()
            for e in entities
        ]

        depreciation_results = await asyncio.gather(*depreciation_tasks)
        accrual_results = await asyncio.gather(*accrual_tasks)

        await self.checkpoint(workflow, "depreciation_accruals", {
            "depreciation": depreciation_results,
            "accruals": accrual_results
        })

        # ============================================
        # STEP 5: Trial Balance Validation (PARALLEL)
        # ============================================
        logger.info(f"Step 5/8: Trial Balance validation")

        tb_tasks = [
            TrialBalanceValidator(entity=e, period=period).execute()
            for e in entities
        ]

        tb_results = await asyncio.gather(*tb_tasks)

        # CRITICAL: Check for imbalances
        imbalanced = [r for r in tb_results if not r.is_balanced]
        if imbalanced:
            await self.escalate_to_human(
                workflow_id=workflow.id,
                step="trial_balance",
                issue="Trial balance imbalance detected",
                details=imbalanced,
                severity="CRITICAL"
            )
            await self.wait_for_resolution(workflow.id)

            # Re-validate after fixes
            tb_results = await asyncio.gather(*tb_tasks)

        await self.checkpoint(workflow, "trial_balance", tb_results)

        # ============================================
        # STEP 6: Financial Reports Generation
        # ============================================
        logger.info(f"Step 6/8: Generating financial reports")

        reports = await FinancialReportingAgent(
            entities=entities,
            period=period
        ).generate_all()

        # Validate reports
        variances = await self.check_variances(reports, period)
        if variances.requires_review:
            await self.escalate_to_human(
                workflow_id=workflow.id,
                step="financial_reports",
                issue="Significant variances detected",
                details=variances
            )
            await self.wait_for_resolution(workflow.id)

        await self.checkpoint(workflow, "financial_reports", reports)

        # ============================================
        # STEP 7: BIR Compliance Validation
        # ============================================
        logger.info(f"Step 7/8: BIR compliance validation")

        bir_validation = await BIRComplianceAgent().validate_period(
            entities=entities,
            period=period
        )

        if not bir_validation.compliant:
            await self.escalate_to_human(
                workflow_id=workflow.id,
                step="bir_compliance",
                issue="BIR compliance issues detected",
                details=bir_validation.issues,
                severity="CRITICAL"
            )
            await self.wait_for_resolution(workflow.id)

        await self.checkpoint(workflow, "bir_compliance", bir_validation)

        # ============================================
        # STEP 8: Close and Lock Period
        # ============================================
        logger.info(f"Step 8/8: Closing period {period}")

        close_result = await PeriodCloseAgent().close_period(
            entities=entities,
            period=period,
            lock=True
        )

        workflow.status = "completed"
        workflow.completed_at = datetime.utcnow()
        workflow.duration_hours = (workflow.completed_at - workflow.started_at).total_seconds() / 3600

        await self.save_workflow(workflow)

        logger.info(f"✅ Month-end close completed in {workflow.duration_hours:.1f} hours")

        return CloseResult(
            success=True,
            workflow=workflow,
            reports=reports,
            compliance=bir_validation
        )

    except Exception as e:
        logger.error(f"❌ Month-end close failed: {e}")

        # Automatic rollback to last checkpoint
        await self.rollback_to_checkpoint(workflow)

        # Alert on-call
        await self.alert_failure(workflow, e)

        return CloseResult(
            success=False,
            error=str(e),
            workflow=workflow
        )
```

#### Production SLA

```yaml
MonthEndCloseOrchestrator_SLA:
  Reliability:
    success_rate: ">= 95%"
    rollback_success: "100%"
    zero_data_loss: "100%"
    mttr: "< 2 hours"

  Performance:
    total_duration: "< 72 hours (3 days)"
    critical_path: "< 8 hours"
    parallel_efficiency: ">= 80%"

  Quality:
    accuracy: ">= 99.9%"
    trial_balance_accuracy: "100%"
    bir_compliance: "100%"

  Cost:
    llm_cost_per_close: "< $50 USD"
    total_automation_cost: "< $200 USD"

  Observability:
    real_time_progress: "Yes"
    checkpoint_frequency: "After each step"
    alert_latency: "< 5 minutes"
    audit_trail: "Complete"
```

---

### BIRComplianceOrchestrator

**Purpose:** Ensure 100% Philippine BIR compliance

#### Capabilities

```python
class BIRComplianceOrchestrator(BaseAgent):
    """
    Master agent for Philippine BIR compliance.

    Handles all tax forms, deadlines, e-filing, validations.
    ZERO late filings, ZERO penalties.
    """

    capabilities = {
        "tax_calendar_management": {
            "track_deadlines": "All BIR forms by entity",
            "auto_reminder": ["7_days", "3_days", "1_day"],
            "penalty_calculation": "Compute surcharges if late",
            "amendment_handling": "Detect need for amended returns"
        },

        "form_generation": {
            "supported_forms": [
                "1601C",   # Monthly withholding tax remittance
                "2550Q",   # Quarterly income tax
                "1702RT",  # Annual income tax return
                "2316",    # Certificate of compensation
                "1604CF",  # Annual information return
                "0605",    # Payment form
                "1606",    # Withholding tax remittance
            ],
            "validation": "Pre-submission BIR rules check",
            "amendment_detection": "Auto-detect when amendment needed"
        },

        "e_filing": {
            "rpa_integration": "Auto-submit to BIR eServices portal",
            "confirmation_tracking": "Store TRN (Transaction Reference Number)",
            "retry_logic": "Handle portal errors, timeouts",
            "evidence_storage": "PDF copies, confirmation emails"
        },

        "compliance_monitoring": {
            "real_time_validation": "Check every GL transaction",
            "risk_scoring": "Identify high-risk transactions",
            "audit_readiness": "Maintain complete documentation",
            "variance_detection": "Flag unusual patterns"
        }
    }
```

#### Form Generation Example

```python
async def generate_form_1601c(self, entity: str, period: str) -> Form1601C:
    """
    Generate Form 1601-C (Monthly Withholding Tax Remittance).

    Requirements:
    - Creditable Withholding Tax (CWT)
    - Expanded Withholding Tax (EWT)
    - Compensation

    Deadline: 10th day of following month
    """

    # 1. Extract withholding tax transactions from GL
    wht_transactions = await self.mcp.search_account_moves(
        entity=entity,
        period=period,
        account_codes=["2150*", "2151*", "2152*"]  # WHT payable accounts
    )

    # 2. Classify by ATC (Alphanumeric Tax Code)
    classified = await self.classify_by_atc(wht_transactions)

    # 3. Compute totals
    totals = {
        "ewt_5_percent": 0,
        "ewt_10_percent": 0,
        "ewt_15_percent": 0,
        "compensation": 0
    }

    for atc, txns in classified.items():
        amount = sum(t.debit - t.credit for t in txns)

        if atc.startswith("WC"):  # Compensation
            totals["compensation"] += amount
        elif atc.startswith("WI"):  # EWT on income payments
            # Get tax rate from knowledge base
            rate = await self.kb.get_tax_rate(atc)
            totals[f"ewt_{int(rate * 100)}_percent"] += amount

    # 4. Validate against payments
    payments = await self.mcp.search_payments(
        entity=entity,
        period=period,
        payment_type="supplier"
    )

    # Cross-check: WHT should match % of payments
    expected_wht = sum(p.amount * p.wht_rate for p in payments)
    actual_wht = sum(totals.values())

    variance = abs(expected_wht - actual_wht)
    if variance > 100:  # ₱100 tolerance
        logger.warning(f"WHT variance detected: ₱{variance:.2f}")
        await self.escalate_variance(entity, period, variance)

    # 5. Generate form
    form = Form1601C(
        tin=await self.get_entity_tin(entity),
        period=period,
        **totals
    )

    # 6. Pre-submission validation
    validation = await self.validate_1601c(form)
    if not validation.passed:
        raise ValidationError(f"Form 1601-C validation failed: {validation.errors}")

    # 7. Generate PDF
    pdf_path = await self.generate_pdf(form)

    # 8. Store for audit trail
    await self.store_form(entity, period, "1601C", form, pdf_path)

    logger.info(f"✅ Form 1601-C generated for {entity} / {period}")

    return form
```

#### Production SLA

```yaml
BIRComplianceOrchestrator_SLA:
  Reliability:
    filing_success_rate: ">= 99%"
    zero_late_filings: "100%"
    zero_penalties: "Target 100%, allow 1/year max"

  Accuracy:
    tax_calculation_accuracy: "100%"
    form_field_accuracy: ">= 99.9%"
    bir_audit_pass_rate: "100%"

  Performance:
    form_generation_time: "< 5 minutes"
    e_filing_time: "< 10 minutes"
    validation_time: "< 30 seconds"

  Cost:
    cost_per_filing: "< $5 USD"

  Compliance:
    deadline_adherence: "100%"
    documentation_completeness: "100%"
    audit_readiness: "Always"
```

---

## TIER 2: DOMAIN SPECIALIST AGENTS

### ReconciliationAgent

**Purpose:** Autonomous bank/GL reconciliation with ML matching

```python
class ReconciliationAgent(BaseAgent):
    """
    Autonomous bank reconciliation.

    Features:
    - Exact matching (amount + date + ref)
    - ML fuzzy matching (confidence > 95%)
    - Exception handling
    - Continuous learning from human corrections
    """

    async def reconcile(
        self,
        entity: str,
        period: str,
        account: str
    ) -> ReconciliationResult:
        """
        Perform bank reconciliation.

        Algorithm:
        1. Extract bank statement transactions
        2. Extract GL transactions
        3. Exact matching
        4. ML fuzzy matching
        5. Flag unmatched items
        6. Generate reconciliation report
        """

        # 1. Extract bank statement
        bank_txns = await self.extract_bank_statement(account, period)
        logger.info(f"Extracted {len(bank_txns)} bank transactions")

        # 2. Extract GL transactions
        gl_txns = await self.mcp.search_account_moves(
            entity=entity,
            account_code=account,
            period=period
        )
        logger.info(f"Extracted {len(gl_txns)} GL transactions")

        matches = []
        unmatched_bank = []
        unmatched_gl = list(gl_txns)

        # 3. Stage 1: Exact matching
        for bank_txn in bank_txns:
            exact_match = None

            for gl_txn in unmatched_gl:
                if self.is_exact_match(bank_txn, gl_txn):
                    exact_match = gl_txn
                    break

            if exact_match:
                matches.append(Match(
                    bank_txn=bank_txn,
                    gl_txn=exact_match,
                    confidence=1.0,
                    match_type="exact"
                ))
                unmatched_gl.remove(exact_match)
            else:
                unmatched_bank.append(bank_txn)

        logger.info(f"Exact matches: {len(matches)}")

        # 4. Stage 2: ML fuzzy matching
        for bank_txn in unmatched_bank[:]:
            best_match = None
            best_score = 0.0

            for gl_txn in unmatched_gl:
                score = await self.ml_match_score(bank_txn, gl_txn)

                if score > best_score and score > 0.95:
                    best_score = score
                    best_match = gl_txn

            if best_match:
                matches.append(Match(
                    bank_txn=bank_txn,
                    gl_txn=best_match,
                    confidence=best_score,
                    match_type="fuzzy"
                ))
                unmatched_bank.remove(bank_txn)
                unmatched_gl.remove(best_match)

        logger.info(f"Fuzzy matches: {len([m for m in matches if m.match_type == 'fuzzy'])}")
        logger.info(f"Unmatched bank: {len(unmatched_bank)}")
        logger.info(f"Unmatched GL: {len(unmatched_gl)}")

        # 5. Generate reconciliation report
        result = ReconciliationResult(
            entity=entity,
            period=period,
            account=account,
            matched_count=len(matches),
            matched_amount=sum(m.amount for m in matches),
            unmatched_bank=unmatched_bank,
            unmatched_gl=unmatched_gl,
            confidence=sum(m.confidence for m in matches) / len(matches) if matches else 0,
            requires_human_review=len(unmatched_bank) > 5 or len(unmatched_gl) > 5
        )

        # 6. Store for audit trail
        await self.store_reconciliation(result)

        # 7. Escalate if too many unmatched
        if result.requires_human_review:
            await self.escalate_to_human(
                entity=entity,
                period=period,
                account=account,
                issue="High unmatched transaction count",
                details=result
            )

        return result

    def is_exact_match(self, bank_txn, gl_txn) -> bool:
        """Check for exact match."""
        return (
            abs(bank_txn.amount - gl_txn.amount) < 0.01 and  # Amount match
            abs((bank_txn.date - gl_txn.date).days) <= 3 and  # Date within 3 days
            self.reference_match(bank_txn.reference, gl_txn.reference)  # Reference similarity
        )

    async def ml_match_score(self, bank_txn, gl_txn) -> float:
        """
        Compute ML-based match score.

        Features:
        - Amount similarity (exact or within 1%)
        - Date proximity (exponential decay)
        - Description similarity (TF-IDF cosine)
        - Counterparty name matching (fuzzy string match)
        - Historical pattern (has this pair matched before?)
        """

        features = {}

        # Amount similarity
        amount_diff = abs(bank_txn.amount - gl_txn.amount)
        features["amount_exact"] = 1.0 if amount_diff < 0.01 else 0.0
        features["amount_percent_diff"] = amount_diff / max(bank_txn.amount, gl_txn.amount)

        # Date proximity (exponential decay)
        date_diff_days = abs((bank_txn.date - gl_txn.date).days)
        features["date_proximity"] = math.exp(-date_diff_days / 3.0)  # Decay over 3 days

        # Description similarity (TF-IDF)
        features["description_similarity"] = await self.compute_text_similarity(
            bank_txn.description,
            gl_txn.name
        )

        # Counterparty matching
        features["counterparty_match"] = fuzz.ratio(
            bank_txn.counterparty or "",
            gl_txn.partner_name or ""
        ) / 100.0

        # Historical pattern
        features["historical_match"] = await self.check_historical_pattern(
            bank_txn,
            gl_txn
        )

        # Feed to ML model (trained on 10,000+ labeled examples)
        score = await self.ml_model.predict(features)

        return score
```

**Production SLA:**

```yaml
ReconciliationAgent_SLA:
  Accuracy:
    match_accuracy: ">= 98%"
    false_positive_rate: "< 1%"
    false_negative_rate: "< 2%"

  Performance:
    reconciliation_time: "< 10 min for 500 txns"
    auto_match_rate: ">= 85%"

  Quality:
    confidence_calibration: "95% confidence = 95% accuracy"
    escalation_precision: ">= 90%"
```

---

### ExpenseValidationAgent

**Purpose:** Validate expense reports against company policy and BIR compliance

```python
class ExpenseValidationAgent(BaseAgent):
    """
    Validate expense reports.

    Features:
    - OCR receipt extraction
    - Policy validation (amount limits, categories)
    - BIR compliance (OR validation, TIN check)
    - Fraud detection (anomalies, fake receipts)
    """

    async def validate_expense(
        self,
        expense_id: str
    ) -> ValidationResult:
        """
        Validate an expense report.

        Steps:
        1. Extract expense details
        2. OCR receipt (if image)
        3. Policy validation
        4. BIR compliance check
        5. Fraud detection
        6. Routing decision (approve/reject/escalate)
        """

        # 1. Get expense details
        expense = await self.mcp.get_expense(expense_id)

        # 2. OCR receipt
        if expense.receipt_image:
            ocr_result = await OCRExtractionAgent().extract(
                expense.receipt_image
            )

            # Validate OCR data matches expense
            if abs(ocr_result.amount - expense.amount) > 1.0:
                return ValidationResult(
                    approved=False,
                    reason="Amount mismatch: Receipt shows ₱{:.2f}, claimed ₱{:.2f}".format(
                        ocr_result.amount,
                        expense.amount
                    )
                )

        # 3. Policy validation
        policy_check = await self.validate_policy(expense)
        if not policy_check.passed:
            return ValidationResult(
                approved=False,
                reason=f"Policy violation: {policy_check.reason}"
            )

        # 4. BIR compliance
        bir_check = await self.validate_bir_compliance(expense)
        if not bir_check.passed:
            return ValidationResult(
                approved=False,
                reason=f"BIR compliance issue: {bir_check.reason}"
            )

        # 5. Fraud detection
        fraud_score = await self.detect_fraud(expense)
        if fraud_score > 0.7:  # High fraud risk
            return ValidationResult(
                approved=False,
                reason=f"High fraud risk score: {fraud_score:.2f}",
                escalate=True
            )

        # 6. Auto-approve if all checks pass
        return ValidationResult(
            approved=True,
            confidence=min(
                policy_check.confidence,
                bir_check.confidence,
                1.0 - fraud_score
            )
        )

    async def validate_policy(self, expense) -> PolicyCheck:
        """
        Check against company expense policy.

        Rules:
        - Amount limits by category
        - Approval routing by amount
        - Blacklisted merchants
        - Valid expense categories
        - Receipt required for > ₱100
        """

        # Get policy rules from knowledge base
        policy = await self.kb.get_expense_policy(expense.company_id)

        # Check amount limit
        category_limit = policy.limits.get(expense.category)
        if expense.amount > category_limit:
            return PolicyCheck(
                passed=False,
                reason=f"{expense.category} limit is ₱{category_limit:,.2f}, claimed ₱{expense.amount:,.2f}"
            )

        # Check receipt requirement
        if expense.amount > 100 and not expense.receipt_image:
            return PolicyCheck(
                passed=False,
                reason="Receipt required for expenses > ₱100"
            )

        # Check blacklisted merchants
        if expense.merchant in policy.blacklist:
            return PolicyCheck(
                passed=False,
                reason=f"Merchant '{expense.merchant}' is blacklisted"
            )

        return PolicyCheck(passed=True, confidence=1.0)

    async def validate_bir_compliance(self, expense) -> BIRCheck:
        """
        BIR compliance validation.

        Requirements:
        - Official Receipt (OR) for ₱100+
        - Valid TIN format
        - VAT calculation correct (12%)
        """

        if expense.amount >= 100:
            # Check OR number present
            if not expense.or_number:
                return BIRCheck(
                    passed=False,
                    reason="Official Receipt number required for ₱100+"
                )

            # Validate TIN format
            if expense.merchant_tin:
                if not self.validate_tin_format(expense.merchant_tin):
                    return BIRCheck(
                        passed=False,
                        reason=f"Invalid TIN format: {expense.merchant_tin}"
                    )

        # Validate VAT calculation
        if expense.vat_amount:
            expected_vat = expense.amount * 0.12 / 1.12  # Inclusive VAT
            if abs(expense.vat_amount - expected_vat) > 0.50:
                return BIRCheck(
                    passed=False,
                    reason=f"VAT mismatch: Expected ₱{expected_vat:.2f}, claimed ₱{expense.vat_amount:.2f}"
                )

        return BIRCheck(passed=True, confidence=1.0)
```

**Production SLA:**

```yaml
ExpenseValidationAgent_SLA:
  Accuracy:
    policy_violation_detection: ">= 98%"
    fraud_detection_rate: ">= 90%"
    false_positive_rate: "< 5%"

  Performance:
    validation_time: "< 30 seconds"
    auto_approval_rate: ">= 70%"

  User_Experience:
    clear_rejection_reasons: "100%"
    escalation_time: "< 2 minutes"
```

---

## TIER 3: TASK EXECUTOR AGENTS

### OCRExtractionAgent

**Purpose:** Extract structured data from Philippine receipts/invoices

```python
class OCRExtractionAgent(BaseAgent):
    """
    Extract structured data from receipts using PaddleOCR.

    Optimized for Philippine documents.
    """

    async def extract(self, image_path: str) -> OCRResult:
        """
        Extract fields from receipt.

        Fields:
        - Merchant name
        - TIN
        - Address
        - Date, time
        - Items (if itemized)
        - Subtotal, VAT, total
        - OR number, SI number
        """

        # 1. Image preprocessing
        image = await self.preprocess_image(image_path)

        # 2. OCR with PaddleOCR
        ocr = PaddleOCR(lang='en', use_gpu=True)
        result = ocr.ocr(image)

        # 3. Extract text with confidence scores
        text_blocks = []
        for line in result[0]:
            bbox, (text, confidence) = line
            text_blocks.append({
                "text": text,
                "confidence": confidence,
                "bbox": bbox
            })

        # 4. Structured extraction
        fields = {}

        # Extract TIN (XXX-XXX-XXX-XXX format)
        tin_pattern = r'\d{3}-\d{3}-\d{3}-\d{3,4}'
        for block in text_blocks:
            match = re.search(tin_pattern, block["text"])
            if match:
                fields["tin"] = match.group()
                fields["tin_confidence"] = block["confidence"]
                break

        # Extract amounts
        amount_pattern = r'₱?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        amounts = []
        for block in text_blocks:
            matches = re.findall(amount_pattern, block["text"])
            for match in matches:
                amount = float(match.replace(',', ''))
                amounts.append((amount, block["confidence"]))

        # Total is usually the largest amount
        if amounts:
            fields["total"], fields["total_confidence"] = max(amounts, key=lambda x: x[0])

        # Extract date
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{4}-\d{2}-\d{2}',
            r'[A-Z][a-z]+ \d{1,2}, \d{4}'
        ]

        for block in text_blocks:
            for pattern in date_patterns:
                match = re.search(pattern, block["text"])
                if match:
                    fields["date"] = match.group()
                    fields["date_confidence"] = block["confidence"]
                    break

        # Extract merchant name (usually top of receipt)
        merchant_candidates = [b for b in text_blocks[:5] if len(b["text"]) > 3]
        if merchant_candidates:
            fields["merchant_name"] = merchant_candidates[0]["text"]
            fields["merchant_confidence"] = merchant_candidates[0]["confidence"]

        # 5. Validation
        if "total" not in fields:
            raise OCRError("Could not extract total amount")

        if fields.get("total_confidence", 0) < 0.85:
            logger.warning(f"Low confidence on total amount: {fields['total_confidence']}")

        return OCRResult(**fields)
```

**Production SLA:**

```yaml
OCRExtractionAgent_SLA:
  Accuracy:
    field_extraction_accuracy: ">= 95%"
    amount_accuracy: "100%"  # Zero tolerance
    date_accuracy: ">= 98%"

  Performance:
    processing_time: "< 5 seconds per receipt"
    throughput: ">= 100 receipts/minute"

  Quality:
    confidence_calibration: "85% confidence = 85% accuracy"
    reject_rate: "< 10%"
```

---

## KNOWLEDGE BASE ARCHITECTURE

### Hybrid Approach: Vector + Graph + Relational

```python
class HybridKnowledgeBase:
    """
    Three-layer knowledge architecture for agents.

    Layer 1: Vector Store (RAG) - Unstructured documents
    Layer 2: Knowledge Graph - Structured relationships
    Layer 3: Relational DB - Transactional data
    """

    def __init__(self):
        # Layer 1: Qdrant vector store
        self.vector_store = QdrantClient(url="http://qdrant:6333")

        # Layer 2: Knowledge graph (NetworkX for now, Neo4j later)
        self.knowledge_graph = KnowledgeGraph()

        # Layer 3: PostgreSQL
        self.relational_db = asyncpg.connect(DATABASE_URL)
```

### Layer 1: Vector Store (RAG)

```python
async def setup_vector_store(self):
    """
    Setup Qdrant collections.
    """

    collections = {
        "bir_regulations": {
            "description": "Revenue Regulations, RMCs, Tax Code",
            "documents": [
                "RR No. 2-98 (Expanded Withholding Tax)",
                "RR No. 11-2018 (Invoicing Requirements)",
                "NIRC (National Internal Revenue Code)",
                # 500+ BIR documents
            ]
        },

        "accounting_standards": {
            "description": "PFRS, PAS, COA guidelines",
            "documents": [
                "PFRS 9 (Financial Instruments)",
                "PAS 1 (Presentation of Financial Statements)",
                # 200+ accounting standards
            ]
        },

        "company_policies": {
            "description": "Internal policies, SOPs",
            "documents": [
                "Expense Policy Manual",
                "Month-End Closing Checklist",
                "Approval Matrix",
                # 100+ company documents
            ]
        },

        "historical_cases": {
            "description": "Past issues, resolutions",
            "documents": [
                "BIR audit findings 2020-2024",
                "Month-end close issues log",
                # 1000+ cases
            ]
        }
    }

    for collection_name, config in collections.items():
        await self.vector_store.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,  # OpenAI text-embedding-3-small
                distance=Distance.COSINE
            )
        )
```

### Layer 2: Knowledge Graph

```python
async def build_knowledge_graph(self):
    """
    Build structured knowledge graphs.
    """

    # BIR Tax Rules Graph
    self.kg.add_node("TaxType", name="Expanded Withholding Tax")
    self.kg.add_node("TaxRate", percentage=1.0)
    self.kg.add_node("Form", code="1601C")
    self.kg.add_node("Deadline", description="10th of following month")

    self.kg.add_edge("Expanded Withholding Tax", "REQUIRES_FORM", "1601C")
    self.kg.add_edge("1601C", "HAS_DEADLINE", "10th of following month")
    self.kg.add_edge("Expanded Withholding Tax", "HAS_RATE", "1%")

    # Chart of Accounts Graph
    await self.build_coa_graph()

    # Approval Hierarchy Graph
    await self.build_approval_graph()
```

### When to Use Each Layer

```yaml
Vector_Store_RAG:
  use_when:
    - Unstructured documents (PDFs, manuals)
    - Semantic similarity matters
    - Natural language Q&A
    - Document content changes frequently

  examples:
    - "What does RR 2-98 say about withholding tax?"
    - "Find similar BIR audit findings"
    - "How do we handle employee reimbursements?"

Knowledge_Graph:
  use_when:
    - Relationships matter (multi-hop queries)
    - Hierarchical structures (COA, org chart)
    - Rule-based logic with dependencies

  examples:
    - "What forms are required for EWT?"
    - "Who approves expenses > ₱10,000?"
    - "What accounts roll up to Current Assets?"

Relational_Database:
  use_when:
    - Transactional data (GL, invoices)
    - Exact lookups by ID
    - Aggregations (SUM, COUNT, AVG)
    - ACID guarantees required

  examples:
    - "Total revenue for Q3 2024"
    - "All unreconciled bank transactions"
    - "Invoice #INV-12345 details"
```

---

## PRODUCTION READINESS FRAMEWORK

### 5-Level Maturity Model

```yaml
Level_0_Prototype:
  description: "Proof of concept only"
  characteristics:
    - Happy path only
    - No error handling
    - No testing
    - Hardcoded values
  readiness: "NOT PRODUCTION READY"

Level_1_Alpha:
  description: "Internal testing"
  characteristics:
    - Basic error handling
    - Unit tests (>= 50% coverage)
    - Manual testing
    - Console logging
  sla:
    availability: "No guarantee"
    accuracy: ">= 80%"
    latency: "< 30 seconds"
  readiness: "Internal team only"

Level_2_Beta:
  description: "Pilot with friendly clients"
  characteristics:
    - Comprehensive error handling
    - Unit + integration tests (>= 80%)
    - Automated CI/CD testing
    - Structured logging
    - Human-in-the-loop
  sla:
    availability: ">= 95%"
    accuracy: ">= 90%"
    latency: "< 10 seconds"
    escalation_rate: "< 20%"
  readiness: "Pilot clients"

Level_3_Production_V1:
  description: "General availability"
  characteristics:
    - Robust error handling + retries
    - Unit + integration + e2e (>= 90%)
    - Golden prompt evaluation
    - Prometheus metrics
    - Distributed tracing
    - Automated alerting
  sla:
    availability: ">= 99%"
    accuracy: ">= 95%"
    latency: "< 5 seconds (p95)"
    escalation_rate: "< 10%"
    cost_per_operation: "< $1 USD"
  readiness: "General availability"

Level_4_Production_V2_Enterprise:
  description: "Mission-critical"
  characteristics:
    - Self-healing
    - Chaos engineering tested
    - Multi-region failover
    - SOC 2 compliant
    - Audit trail
    - Explainable AI
    - A/B testing
  sla:
    availability: ">= 99.9%"
    accuracy: ">= 99%"
    latency: "< 2 seconds (p99)"
    escalation_rate: "< 5%"
    cost_per_operation: "< $0.50"
    mttr: "< 15 minutes"
  readiness: "Enterprise mission-critical"
```

### Production Readiness Checklist

```markdown
## Agent Production Readiness Checklist

### 1. Functionality (30 points)
- [ ] (5) Happy path works end-to-end
- [ ] (5) All edge cases handled
- [ ] (5) Graceful degradation
- [ ] (5) Rollback/undo capability
- [ ] (5) Human escalation for low confidence
- [ ] (5) Idempotent operations

### 2. Testing (25 points)
- [ ] (10) Unit tests (>= 90% coverage)
- [ ] (5) Integration tests
- [ ] (5) Golden prompt evaluation (>= 20 cases)
- [ ] (3) Load/performance testing
- [ ] (2) Chaos engineering

### 3. Observability (20 points)
- [ ] (5) Structured logging (JSON)
- [ ] (5) Prometheus metrics (RED: Rate, Errors, Duration)
- [ ] (5) Distributed tracing
- [ ] (3) Grafana dashboards
- [ ] (2) Alerting

### 4. Reliability (15 points)
- [ ] (5) Error handling & retries
- [ ] (5) Circuit breaker pattern
- [ ] (3) State persistence
- [ ] (2) Auto-recovery

### 5. Security (10 points)
- [ ] (3) Input validation
- [ ] (3) Authentication & authorization
- [ ] (2) Secrets management
- [ ] (2) Audit trail

**TOTAL: ___ / 100 points**

Minimum for Production:
- Level 3 (Production V1): >= 75 points
- Level 4 (Production V2): >= 90 points
```

---

## IMPLEMENTATION GUIDE

### Phase 1: Foundation (Weeks 1-4)

```yaml
Week_1_2:
  - Deploy Qdrant vector store
  - Index 500+ BIR documents
  - Test semantic search quality
  - Build basic RAG pipeline

Week_3_4:
  - Design knowledge graph schema
  - Build COA graph
  - Build BIR tax rules graph
  - Implement hybrid query system
```

### Phase 2: Core Agents (Weeks 5-12)

```yaml
Week_5_6:
  - Build OCRExtractionAgent (Level 2)
  - Train on Philippine receipts
  - Deploy to Beta

Week_7_8:
  - Build ReconciliationAgent (Level 3)
  - Train ML matching model
  - Deploy to Production V1

Week_9_10:
  - Build ExpenseValidationAgent (Level 3)
  - Policy rules engine
  - Deploy to Production V1

Week_11_12:
  - Build BIRComplianceOrchestrator (Level 3)
  - Auto-generate forms
  - Deploy to Production V1
```

### Phase 3: Orchestration (Weeks 13-16)

```yaml
Week_13_14:
  - Build MonthEndCloseOrchestrator (Level 4)
  - Workflow engine with checkpointing
  - Integration testing

Week_15_16:
  - Production hardening
  - Chaos engineering
  - Deploy to Production V2
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Maintained by:** InsightPulse AI Engineering Team
**Next Review:** 2025-12-08
