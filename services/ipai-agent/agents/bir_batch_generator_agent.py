"""
BIR Multi-Form Batch Generator Agent
Orchestrates month-end BIR form generation workflows
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from tools.bir_batch_generator import BIRBatchGenerator, BIRFormType
from tools.odoo_client import OdooClient
from memory.kv_store import MemoryKVStore

logger = logging.getLogger(__name__)


class BIRBatchGeneratorAgent:
    """
    BIR Multi-Form Batch Generator Agent

    Orchestrates month-end closing workflows by generating multiple BIR forms:
    - Form 1601-C: Monthly Withholding Tax Return
    - Form 2550Q: Quarterly VAT Return
    - Form 2550M: Monthly VAT Return
    - Form 2307: Withholding Tax Certificates (batch)

    Workflow:
    1. Fetch transaction data from Supabase
    2. Validate batch data and form requirements
    3. Generate forms using BIRBatchGenerator
    4. Store batch results in Odoo
    5. Generate downloadable form files
    6. Send Slack notification with batch summary
    """

    def __init__(
        self,
        odoo_client: OdooClient,
        memory_store: MemoryKVStore,
        slack_client: Optional[Any] = None,
        supabase_client: Optional[Any] = None
    ):
        self.odoo = odoo_client
        self.memory = memory_store
        self.slack = slack_client
        self.supabase = supabase_client
        self.generator = BIRBatchGenerator()
        logger.info("✅ BIR Batch Generator Agent initialized")

    async def execute(
        self,
        month: int,
        year: int,
        company_id: int,
        forms: List[str],
        run_id: int,
        user_id: Optional[int] = None,
        auto_submit: bool = False
    ) -> Dict[str, Any]:
        """
        Execute batch form generation workflow

        Args:
            month: Month (1-12)
            year: Year (e.g., 2025)
            company_id: Company ID (legal entity for multi-tenant isolation)
            forms: List of form types to generate (e.g., ["1601-C", "2550Q"])
            run_id: Agent run ID (from agent log)
            user_id: User who requested generation
            auto_submit: Auto-submit forms after generation

        Returns:
            Batch generation result
        """
        try:
            logger.info(f"Starting batch generation for company {company_id} - {year}-{month:02d}")

            # Update run status
            self.odoo.update_agent_run(run_id, {"status": "running"})

            # 1. Fetch company info from Odoo
            company_info = self._get_company_info(company_id)

            # 2. Fetch transaction data from Supabase
            transaction_data = await self._fetch_transaction_data(
                month=month,
                year=year,
                company_id=company_id
            )

            # 3. Validate batch data
            validation_result = self.generator.validate_batch_data(
                month=month,
                year=year,
                transaction_data=transaction_data,
                forms=forms
            )

            if not validation_result["valid"]:
                logger.error(f"❌ Batch validation failed: {validation_result['errors']}")
                self.odoo.update_agent_run(run_id, {
                    "status": "failed",
                    "error": f"Validation failed: {validation_result['errors']}",
                    "completed_at": datetime.utcnow().isoformat()
                })
                return validation_result

            # 4. Generate forms
            batch_result = self.generator.generate_batch(
                month=month,
                year=year,
                company_id=company_id,
                transaction_data=transaction_data,
                forms=forms,
                company_info=company_info
            )

            # 5. Store batch results in Odoo
            batch_record_id = self._store_batch_result(
                batch_result=batch_result,
                user_id=user_id,
                auto_submit=auto_submit
            )
            batch_result["batch_record_id"] = batch_record_id

            # 6. Send Slack notification
            if self.slack:
                await self._send_batch_notification(
                    batch_result=batch_result,
                    company_id=company_id
                )

            # 7. Update run status with result
            self.odoo.update_agent_run(run_id, {
                "status": "completed",
                "result": batch_result,
                "completed_at": datetime.utcnow().isoformat()
            })

            logger.info(
                f"✅ Batch generated: {batch_result['summary']['total_forms']} forms for company {company_id}"
            )

            return batch_result

        except Exception as e:
            logger.error(f"❌ Batch generation failed: {str(e)}", exc_info=True)

            # Update run status with error
            self.odoo.update_agent_run(run_id, {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            })

            raise

    def _get_company_info(self, company_id: int) -> Dict[str, Any]:
        """
        Get company info from Odoo

        Fetches company details (TIN, name, address) for the legal entity
        """
        try:
            # Fetch company from Odoo res.company model
            company = self.odoo.read(
                model="res.company",
                record_id=company_id,
                fields=["name", "vat", "street", "city", "country_id"]
            )

            if not company:
                logger.warning(f"⚠️ Company {company_id} not found in Odoo")
                return {
                    "tin": "000-000-000-000",
                    "name": f"Company {company_id}",
                    "address": "Philippines"
                }

            # Extract TIN from VAT field (format: PH123456789000)
            vat = company.get("vat", "")
            tin = vat.replace("PH", "") if vat.startswith("PH") else vat

            # Format TIN with dashes (123-456-789-000)
            if len(tin) == 12 and tin.isdigit():
                tin = f"{tin[0:3]}-{tin[3:6]}-{tin[6:9]}-{tin[9:12]}"

            return {
                "tin": tin,
                "name": company.get("name", f"Company {company_id}"),
                "address": f"{company.get('street', '')}, {company.get('city', '')}, {company.get('country_id', ['', 'Philippines'])[1]}"
            }

        except Exception as e:
            logger.error(f"❌ Failed to fetch company info: {str(e)}")
            return {
                "tin": "000-000-000-000",
                "name": f"Company {company_id}",
                "address": "Philippines"
            }

    async def _fetch_transaction_data(
        self,
        month: int,
        year: int,
        company_id: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch transaction data from Supabase

        Queries:
        - scout.transactions (for withholding tax) filtered by company_id
        - scout.vat_transactions (for VAT) filtered by company_id
        """
        try:
            if not self.supabase:
                logger.warning("⚠️ Supabase client not configured - returning empty data")
                return []

            # Fetch withholding tax transactions (multi-tenant isolation via company_id)
            wht_query = self.supabase.table("transactions").select("*").filter(
                "company_id", "eq", company_id
            ).filter(
                "transaction_date", "gte", f"{year}-{month:02d}-01"
            ).filter(
                "transaction_date", "lt", f"{year}-{month + 1 if month < 12 else 1:02d}-01"
            ).filter(
                "transaction_type", "eq", "withholding_tax"
            ).execute()

            # Fetch VAT transactions (multi-tenant isolation via company_id)
            vat_query = self.supabase.table("vat_transactions").select("*").filter(
                "company_id", "eq", company_id
            ).filter(
                "month", "eq", month
            ).filter(
                "year", "eq", year
            ).execute()

            wht_data = wht_query.data if wht_query.data else []
            vat_data = vat_query.data if vat_query.data else []

            logger.info(f"✅ Fetched {len(wht_data)} WHT + {len(vat_data)} VAT transactions for company {company_id}")

            return wht_data + vat_data

        except Exception as e:
            logger.error(f"❌ Failed to fetch transaction data: {str(e)}")
            return []

    def _store_batch_result(
        self,
        batch_result: Dict[str, Any],
        user_id: Optional[int] = None,
        auto_submit: bool = False
    ) -> int:
        """
        Store batch result in Odoo

        Creates a record in `bir.batch.generation` model
        """
        try:
            # Check if model exists
            model_name = "bir.batch.generation"

            # Create batch record (with multi-tenant company_id)
            record_id = self.odoo.create(model_name, {
                "batch_id": batch_result["batch_id"],
                "month": batch_result["month"],
                "year": batch_result["year"],
                "company_id": batch_result["company_id"],
                "forms_generated": len(batch_result["forms_generated"]),
                "form_types": ",".join([f["form_type"] for f in batch_result["forms_generated"]]),
                "batch_data": batch_result,
                "generated_by": user_id,
                "state": "submitted" if auto_submit else "draft",
                "generated_at": datetime.utcnow().isoformat()
            })

            logger.info(f"✅ Batch result stored: {model_name} #{record_id}")
            return record_id

        except Exception as e:
            logger.error(f"❌ Failed to store batch result: {str(e)}")
            # Don't fail the whole workflow if storage fails
            return 0

    async def _send_batch_notification(
        self,
        batch_result: Dict[str, Any],
        company_id: int
    ):
        """
        Send Slack notification with batch summary

        Alerts sent to #bir-month-end channel
        """
        try:
            channels = self.memory.get_slack_channels()
            month_end_channel = channels.get("bir-month-end")

            if not month_end_channel:
                logger.warning("BIR month-end Slack channel not configured")
                return

            # Build notification message
            summary = batch_result["summary"]
            batch_id = batch_result["batch_id"]
            forms = batch_result["forms_generated"]

            message = f"""
✅ **BIR Batch Generation Complete**

**Batch ID:** `{batch_id}`
**Company ID:** {company_id}
**Period:** {batch_result['year']}-{batch_result['month']:02d}

**Forms Generated:** {summary['total_forms']}
{chr(10).join([f"• {f['form_type']}" for f in forms])}

**Summary:**
{chr(10).join([f"• {k}: {v}" for k, v in summary.get('totals', {}).items()])}

Action: Review and submit forms via Odoo
            """.strip()

            # Send to Slack
            await self.slack.send_message(
                channel=month_end_channel,
                text=message
            )

            logger.info(f"✅ Batch notification sent to {month_end_channel}")

        except Exception as e:
            logger.error(f"❌ Failed to send Slack notification: {str(e)}")
            # Don't fail the whole workflow if Slack fails

    async def validate_batch_only(
        self,
        month: int,
        year: int,
        company_id: int,
        forms: List[str],
        run_id: int
    ) -> Dict[str, Any]:
        """
        Validate batch data without generating forms

        Useful for pre-flight checks before month-end closing
        """
        try:
            logger.info(f"Validating batch data for company {company_id} - {year}-{month:02d}")

            # Update run status
            self.odoo.update_agent_run(run_id, {"status": "running"})

            # Fetch transaction data
            transaction_data = await self._fetch_transaction_data(
                month=month,
                year=year,
                company_id=company_id
            )

            # Validate
            validation_result = self.generator.validate_batch_data(
                month=month,
                year=year,
                transaction_data=transaction_data,
                forms=forms
            )

            # Add transaction counts
            validation_result["transaction_count"] = len(transaction_data)
            validation_result["wht_count"] = len([
                t for t in transaction_data
                if t.get("transaction_type") == "withholding_tax"
            ])
            validation_result["vat_count"] = len([
                t for t in transaction_data
                if t.get("transaction_type") in ["vat_output", "vat_input"]
            ])

            # Update run status
            self.odoo.update_agent_run(run_id, {
                "status": "completed",
                "result": validation_result,
                "completed_at": datetime.utcnow().isoformat()
            })

            return validation_result

        except Exception as e:
            logger.error(f"❌ Validation failed: {str(e)}", exc_info=True)

            # Update run status with error
            self.odoo.update_agent_run(run_id, {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            })

            raise
