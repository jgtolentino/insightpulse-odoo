"""
BIR E-Invoicing Validator Agent
Validates invoice JSON against BIR e-invoicing requirements
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from tools.bir_validator import BIRValidator, BIRFormType
from tools.odoo_client import OdooClient
from memory.kv_store import MemoryKVStore

logger = logging.getLogger(__name__)


class BIREInvoicingValidatorAgent:
    """
    BIR E-Invoicing Validator Agent

    Validates invoice JSON structure against Philippine BIR e-invoicing requirements.
    Provides compliance scoring and detailed validation reports.

    Workflow:
    1. Receive invoice JSON
    2. Validate against BIR schema
    3. Check business logic (VAT calculation, totals)
    4. Generate compliance report
    5. Store validation result in Odoo
    6. Notify via Slack if compliance score < 80%
    """

    def __init__(
        self,
        odoo_client: OdooClient,
        memory_store: MemoryKVStore,
        slack_client: Optional[Any] = None
    ):
        self.odoo = odoo_client
        self.memory = memory_store
        self.slack = slack_client
        self.validator = BIRValidator()
        logger.info("✅ BIR E-Invoicing Validator Agent initialized")

    async def execute(
        self,
        invoice_data: Dict[str, Any],
        run_id: int,
        user_id: Optional[int] = None,
        strict_mode: bool = False,
        store_result: bool = True
    ) -> Dict[str, Any]:
        """
        Execute validation workflow

        Args:
            invoice_data: Invoice JSON to validate
            run_id: Agent run ID (from agent log)
            user_id: User who requested validation
            strict_mode: Treat warnings as errors
            store_result: Store result in Odoo

        Returns:
            Validation result dict
        """
        try:
            logger.info(f"Starting BIR E-Invoice validation for run {run_id}")

            # Update run status
            self.odoo.update_agent_run(run_id, {"status": "running"})

            # 1. Validate invoice
            result = self.validator.validate_einvoice(
                invoice_data=invoice_data,
                strict_mode=strict_mode
            )

            # 2. Store validation result in Odoo (if requested)
            if store_result:
                validation_record_id = self._store_validation_result(
                    invoice_data=invoice_data,
                    validation_result=result,
                    user_id=user_id
                )
                result["validation_record_id"] = validation_record_id

            # 3. Send Slack notification if compliance is low
            if self.slack and result["compliance_score"] < 0.80:
                await self._send_compliance_alert(
                    invoice_data=invoice_data,
                    result=result
                )

            # 4. Update run status with result
            self.odoo.update_agent_run(run_id, {
                "status": "completed",
                "result": result,
                "completed_at": datetime.utcnow().isoformat()
            })

            logger.info(
                f"✅ Validation completed: {result['compliance_score'] * 100:.1f}% compliant"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Validation failed: {str(e)}", exc_info=True)

            # Update run status with error
            self.odoo.update_agent_run(run_id, {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            })

            raise

    def _store_validation_result(
        self,
        invoice_data: Dict[str, Any],
        validation_result: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> int:
        """
        Store validation result in Odoo

        Creates a record in `bir.validation.result` model
        """
        try:
            # Check if model exists
            model_name = "bir.validation.result"

            # Create validation record
            record_id = self.odoo.create(model_name, {
                "invoice_number": invoice_data.get("invoice_number", "N/A"),
                "invoice_date": invoice_data.get("invoice_date"),
                "form_type": "e-invoice",
                "validation_date": datetime.utcnow().isoformat(),
                "is_valid": validation_result["valid"],
                "compliance_score": validation_result["compliance_score"],
                "error_count": len(validation_result["errors"]),
                "warning_count": len(validation_result["warnings"]),
                "validation_data": validation_result,
                "invoice_data": invoice_data,
                "validated_by": user_id
            })

            logger.info(f"✅ Validation result stored: {model_name} #{record_id}")
            return record_id

        except Exception as e:
            logger.error(f"❌ Failed to store validation result: {str(e)}")
            # Don't fail the whole workflow if storage fails
            return 0

    async def _send_compliance_alert(
        self,
        invoice_data: Dict[str, Any],
        result: Dict[str, Any]
    ):
        """
        Send Slack alert for low compliance scores

        Alerts sent to #bir-compliance channel
        """
        try:
            channels = self.memory.get_slack_channels()
            bir_channel = channels.get("bir-compliance")

            if not bir_channel:
                logger.warning("BIR compliance Slack channel not configured")
                return

            # Build alert message
            invoice_number = invoice_data.get("invoice_number", "N/A")
            score = result["compliance_score"] * 100

            message = f"""
⚠️ **BIR E-Invoice Compliance Alert**

Invoice: `{invoice_number}`
Compliance Score: `{score:.1f}%`

**Issues:**
• Errors: {len(result["errors"])}
• Warnings: {len(result["warnings"])}

**Summary:** {result["summary"]}

Action required: Review and fix validation errors before submission.
            """.strip()

            # Send to Slack
            await self.slack.send_message(
                channel=bir_channel,
                text=message
            )

            logger.info(f"✅ Compliance alert sent to {bir_channel}")

        except Exception as e:
            logger.error(f"❌ Failed to send Slack alert: {str(e)}")
            # Don't fail the whole workflow if Slack fails

    async def validate_batch(
        self,
        invoices: list[Dict[str, Any]],
        run_id: int,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate batch of invoices

        Args:
            invoices: List of invoice JSONs
            run_id: Agent run ID
            user_id: User who requested validation

        Returns:
            Batch validation result
        """
        try:
            logger.info(f"Starting batch validation for {len(invoices)} invoices")

            # Update run status
            self.odoo.update_agent_run(run_id, {"status": "running"})

            # Validate batch
            batch_result = self.validator.validate_batch(
                invoices=invoices,
                form_type=BIRFormType.EINVOICE
            )

            # Store batch result summary
            summary_id = self.odoo.create("bir.validation.batch", {
                "validation_date": datetime.utcnow().isoformat(),
                "total_invoices": batch_result["total"],
                "valid_invoices": batch_result["valid"],
                "invalid_invoices": batch_result["invalid"],
                "average_compliance": batch_result["average_compliance"],
                "validated_by": user_id
            })

            batch_result["summary_record_id"] = summary_id

            # Update run status
            self.odoo.update_agent_run(run_id, {
                "status": "completed",
                "result": batch_result,
                "completed_at": datetime.utcnow().isoformat()
            })

            logger.info(
                f"✅ Batch validation completed: {batch_result['valid']}/{batch_result['total']} valid"
            )

            return batch_result

        except Exception as e:
            logger.error(f"❌ Batch validation failed: {str(e)}", exc_info=True)

            # Update run status with error
            self.odoo.update_agent_run(run_id, {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            })

            raise
