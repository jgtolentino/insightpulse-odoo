"""
BIR Validation Tool
Validates invoices and tax forms against Philippine BIR requirements
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from enum import Enum

logger = logging.getLogger(__name__)


class BIRFormType(str, Enum):
    """Supported BIR form types"""
    EINVOICE = "e-invoice"
    FORM_2307 = "2307"
    FORM_2316 = "2316"
    FORM_1601C = "1601-C"
    FORM_2550Q = "2550Q"


class ValidationSeverity(str, Enum):
    """Validation issue severity levels"""
    ERROR = "error"  # Blocks submission
    WARNING = "warning"  # Should be fixed
    INFO = "info"  # Recommendation


class BIRValidator:
    """
    BIR E-Invoicing and Form Validator

    Validates invoice JSON structure and tax forms against BIR requirements.
    Extensible schema system to accommodate future BIR e-invoicing specs.
    """

    # E-Invoice schema (based on international standards + PH requirements)
    # Will be updated when official BIR specs are released
    EINVOICE_SCHEMA = {
        "required_fields": [
            "invoice_number",
            "invoice_date",
            "seller_tin",
            "seller_name",
            "seller_address",
            "buyer_tin",
            "buyer_name",
            "buyer_address",
            "currency",
            "total_amount",
            "vat_amount",
            "line_items"
        ],
        "optional_fields": [
            "payment_terms",
            "payment_method",
            "discount_amount",
            "remarks",
            "qr_code"
        ],
        "line_item_fields": [
            "description",
            "quantity",
            "unit_price",
            "amount",
            "vat_rate"
        ],
        "validation_rules": {
            "invoice_number": {"type": "string", "pattern": r"^[A-Z0-9\-]+$"},
            "invoice_date": {"type": "date", "format": "YYYY-MM-DD"},
            "seller_tin": {"type": "string", "pattern": r"^\d{3}-\d{3}-\d{3}-\d{3}$"},
            "buyer_tin": {"type": "string", "pattern": r"^\d{3}-\d{3}-\d{3}-\d{3}$"},
            "currency": {"type": "string", "allowed": ["PHP", "USD"]},
            "total_amount": {"type": "number", "min": 0},
            "vat_amount": {"type": "number", "min": 0},
            "vat_rate": {"type": "number", "allowed": [0.00, 0.12]}  # 0% or 12%
        }
    }

    def __init__(self):
        """Initialize BIR validator"""
        logger.info("✅ BIR Validator initialized")

    def validate_einvoice(
        self,
        invoice_data: Dict[str, Any],
        strict_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Validate e-invoice JSON against BIR requirements

        Args:
            invoice_data: Invoice data as dict
            strict_mode: If True, treat warnings as errors

        Returns:
            {
                "valid": bool,
                "compliance_score": float (0.0-1.0),
                "errors": [...],
                "warnings": [...],
                "info": [...],
                "summary": str
            }
        """
        issues = {
            "errors": [],
            "warnings": [],
            "info": []
        }

        # 1. Validate required fields
        for field in self.EINVOICE_SCHEMA["required_fields"]:
            if field not in invoice_data or not invoice_data[field]:
                issues["errors"].append({
                    "field": field,
                    "severity": ValidationSeverity.ERROR,
                    "message": f"Required field '{field}' is missing or empty"
                })

        # 2. Validate field formats
        for field, rules in self.EINVOICE_SCHEMA["validation_rules"].items():
            if field not in invoice_data:
                continue

            value = invoice_data[field]

            # Type validation
            if rules["type"] == "string" and not isinstance(value, str):
                issues["errors"].append({
                    "field": field,
                    "severity": ValidationSeverity.ERROR,
                    "message": f"Field '{field}' must be a string"
                })
            elif rules["type"] == "number" and not isinstance(value, (int, float)):
                issues["errors"].append({
                    "field": field,
                    "severity": ValidationSeverity.ERROR,
                    "message": f"Field '{field}' must be a number"
                })

            # Pattern validation
            if "pattern" in rules and isinstance(value, str):
                import re
                if not re.match(rules["pattern"], value):
                    issues["errors"].append({
                        "field": field,
                        "severity": ValidationSeverity.ERROR,
                        "message": f"Field '{field}' format is invalid. Expected pattern: {rules['pattern']}"
                    })

            # Allowed values
            if "allowed" in rules and value not in rules["allowed"]:
                issues["errors"].append({
                    "field": field,
                    "severity": ValidationSeverity.ERROR,
                    "message": f"Field '{field}' has invalid value. Allowed: {rules['allowed']}"
                })

            # Min value
            if "min" in rules and isinstance(value, (int, float)):
                if value < rules["min"]:
                    issues["errors"].append({
                        "field": field,
                        "severity": ValidationSeverity.ERROR,
                        "message": f"Field '{field}' must be >= {rules['min']}"
                    })

        # 3. Validate line items
        if "line_items" in invoice_data:
            if not isinstance(invoice_data["line_items"], list):
                issues["errors"].append({
                    "field": "line_items",
                    "severity": ValidationSeverity.ERROR,
                    "message": "Line items must be an array"
                })
            else:
                for idx, item in enumerate(invoice_data["line_items"]):
                    for required_field in self.EINVOICE_SCHEMA["line_item_fields"]:
                        if required_field not in item:
                            issues["warnings"].append({
                                "field": f"line_items[{idx}].{required_field}",
                                "severity": ValidationSeverity.WARNING,
                                "message": f"Line item {idx} missing '{required_field}'"
                            })

        # 4. Business logic validations
        if "total_amount" in invoice_data and "vat_amount" in invoice_data:
            total = invoice_data["total_amount"]
            vat = invoice_data["vat_amount"]

            # VAT should be ~12% of taxable amount
            expected_vat = total * 0.12 / 1.12  # Assuming VAT-inclusive
            tolerance = 1.0  # PHP 1.00 tolerance

            if abs(vat - expected_vat) > tolerance:
                issues["warnings"].append({
                    "field": "vat_amount",
                    "severity": ValidationSeverity.WARNING,
                    "message": f"VAT amount ({vat}) doesn't match expected ({expected_vat:.2f})"
                })

        # 5. Calculate compliance score
        total_checks = len(self.EINVOICE_SCHEMA["required_fields"]) + len(self.EINVOICE_SCHEMA["validation_rules"])
        failed_checks = len(issues["errors"])
        warning_checks = len(issues["warnings"])

        compliance_score = max(0.0, (total_checks - failed_checks - (warning_checks * 0.5)) / total_checks)

        # 6. Generate summary
        is_valid = len(issues["errors"]) == 0 and (not strict_mode or len(issues["warnings"]) == 0)

        summary_parts = []
        if is_valid:
            summary_parts.append("✅ Invoice is valid and BIR-compliant")
        else:
            summary_parts.append(f"❌ Invoice has {len(issues['errors'])} errors")

        if issues["warnings"]:
            summary_parts.append(f"⚠️  {len(issues['warnings'])} warnings")

        summary_parts.append(f"Compliance score: {compliance_score * 100:.1f}%")

        logger.info(f"E-Invoice validation: {compliance_score * 100:.1f}% compliant, {len(issues['errors'])} errors")

        return {
            "valid": is_valid,
            "compliance_score": compliance_score,
            "errors": issues["errors"],
            "warnings": issues["warnings"],
            "info": issues["info"],
            "summary": " | ".join(summary_parts),
            "timestamp": datetime.utcnow().isoformat()
        }

    def validate_form_2307(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate BIR Form 2307 (Certificate of Creditable Tax Withheld at Source)

        Required fields for Form 2307:
        - Payee TIN
        - Income payment details
        - Tax withheld amount
        - Tax rate
        """
        issues = {
            "errors": [],
            "warnings": [],
            "info": []
        }

        required_fields = [
            "payee_tin",
            "payee_name",
            "income_payment",
            "tax_withheld",
            "tax_rate"
        ]

        for field in required_fields:
            if field not in form_data:
                issues["errors"].append({
                    "field": field,
                    "severity": ValidationSeverity.ERROR,
                    "message": f"Required field '{field}' is missing"
                })

        # Validate tax computation
        if all(f in form_data for f in ["income_payment", "tax_withheld", "tax_rate"]):
            expected_tax = form_data["income_payment"] * (form_data["tax_rate"] / 100)
            tolerance = 1.0

            if abs(form_data["tax_withheld"] - expected_tax) > tolerance:
                issues["warnings"].append({
                    "field": "tax_withheld",
                    "severity": ValidationSeverity.WARNING,
                    "message": f"Tax amount ({form_data['tax_withheld']}) doesn't match expected ({expected_tax:.2f})"
                })

        is_valid = len(issues["errors"]) == 0
        compliance_score = 1.0 if is_valid else 0.5

        return {
            "valid": is_valid,
            "compliance_score": compliance_score,
            "errors": issues["errors"],
            "warnings": issues["warnings"],
            "info": issues["info"],
            "summary": "✅ Form 2307 is valid" if is_valid else "❌ Form 2307 has errors",
            "timestamp": datetime.utcnow().isoformat()
        }

    def validate_batch(
        self,
        invoices: List[Dict[str, Any]],
        form_type: BIRFormType = BIRFormType.EINVOICE
    ) -> Dict[str, Any]:
        """
        Validate batch of invoices/forms

        Returns:
            {
                "total": int,
                "valid": int,
                "invalid": int,
                "average_compliance": float,
                "results": [...]
            }
        """
        results = []

        for idx, invoice in enumerate(invoices):
            if form_type == BIRFormType.EINVOICE:
                result = self.validate_einvoice(invoice)
            elif form_type == BIRFormType.FORM_2307:
                result = self.validate_form_2307(invoice)
            else:
                result = {"valid": False, "compliance_score": 0.0}

            result["index"] = idx
            results.append(result)

        valid_count = sum(1 for r in results if r["valid"])
        invalid_count = len(results) - valid_count
        avg_compliance = sum(r["compliance_score"] for r in results) / len(results) if results else 0.0

        logger.info(f"Batch validation: {valid_count}/{len(results)} valid, {avg_compliance * 100:.1f}% avg compliance")

        return {
            "total": len(results),
            "valid": valid_count,
            "invalid": invalid_count,
            "average_compliance": avg_compliance,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
