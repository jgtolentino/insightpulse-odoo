"""
BIR Multi-Form Batch Generator
Generates multiple BIR forms for month-end closing workflows
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import json

logger = logging.getLogger(__name__)


class BIRFormType:
    """BIR Form Type Enumeration"""
    FORM_1601C = "1601-C"  # Monthly Remittance Return of Income Taxes Withheld
    FORM_2550Q = "2550Q"   # Quarterly VAT Return
    FORM_2550M = "2550M"   # Monthly VAT Return
    FORM_2307 = "2307"     # Certificate of Creditable Tax Withheld at Source


class BIRBatchGenerator:
    """
    BIR Multi-Form Batch Generator

    Generates multiple BIR forms for month-end closing:
    - Form 1601-C: Monthly Withholding Tax Return
    - Form 2550Q: Quarterly VAT Return
    - Form 2550M: Monthly VAT Return
    - Form 2307: Withholding Tax Certificates (batch)

    Integrates with:
    - Supabase transactions table
    - Odoo journal entries
    - Multi-agency context (8 agencies)
    """

    FORM_SCHEMAS = {
        BIRFormType.FORM_1601C: {
            "required_fields": [
                "month", "year", "tin", "registered_name",
                "total_amount_withheld", "total_remittance"
            ],
            "schedules": ["schedule_1", "schedule_2"]  # ATC codes breakdown
        },
        BIRFormType.FORM_2550Q: {
            "required_fields": [
                "quarter", "year", "tin", "registered_name",
                "total_sales", "taxable_sales", "vat_output",
                "vat_input", "net_vat_payable"
            ],
            "parts": ["part_1_vat_output", "part_2_vat_input", "part_3_computation"]
        },
        BIRFormType.FORM_2550M: {
            "required_fields": [
                "month", "year", "tin", "registered_name",
                "total_sales", "vat_exempt_sales", "vat_zero_rated",
                "vat_output", "net_vat_payable"
            ]
        },
        BIRFormType.FORM_2307: {
            "required_fields": [
                "payee_tin", "payee_name", "income_payment",
                "atc_code", "tax_rate", "amount_withheld",
                "payor_tin", "payor_name"
            ]
        }
    }

    WHT_RATES = {
        "WC010": 0.01,   # Professional fees
        "WC020": 0.02,   # Professional fees (2%)
        "WC030": 0.05,   # Rental income
        "WC040": 0.10,   # Rental income (10%)
        "WC050": 0.15,   # Interest income
        "WI010": 0.01,   # Government money payments
        "WI020": 0.02,   # Rentals
        "WI030": 0.05,   # Professional fees
        "WI040": 0.10,   # Management/technical fees
        "WI050": 0.15,   # Interest income
    }

    VAT_RATE = Decimal("0.12")  # 12% VAT

    def __init__(self):
        logger.info("✅ BIR Batch Generator initialized")

    def generate_batch(
        self,
        month: int,
        year: int,
        company_id: int,
        transaction_data: List[Dict[str, Any]],
        forms: List[str],
        company_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate batch of BIR forms for month-end closing

        Args:
            month: Month (1-12)
            year: Year (e.g., 2025)
            company_id: Company ID (legal entity for multi-tenant isolation)
            transaction_data: List of transactions from Supabase
            forms: List of form types to generate (e.g., ["1601-C", "2550Q"])
            company_info: Company TIN, name, address

        Returns:
            Batch generation result with form data and files
        """
        try:
            logger.info(f"Generating batch for company {company_id} - {year}-{month:02d}")

            results = {
                "batch_id": f"company{company_id}_{year}{month:02d}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "month": month,
                "year": year,
                "company_id": company_id,
                "forms_generated": [],
                "summary": {}
            }

            # Generate each requested form
            for form_type in forms:
                if form_type == BIRFormType.FORM_1601C:
                    form_data = self._generate_1601c(
                        month, year, transaction_data, company_info
                    )
                    results["forms_generated"].append(form_data)

                elif form_type == BIRFormType.FORM_2550Q:
                    quarter = (month - 1) // 3 + 1
                    form_data = self._generate_2550q(
                        quarter, year, transaction_data, company_info
                    )
                    results["forms_generated"].append(form_data)

                elif form_type == BIRFormType.FORM_2550M:
                    form_data = self._generate_2550m(
                        month, year, transaction_data, company_info
                    )
                    results["forms_generated"].append(form_data)

                elif form_type == BIRFormType.FORM_2307:
                    form_data = self._generate_2307_batch(
                        month, year, transaction_data, company_info
                    )
                    results["forms_generated"].append(form_data)

            # Generate summary
            results["summary"] = self._generate_summary(results["forms_generated"])

            logger.info(f"✅ Batch generated: {len(results['forms_generated'])} forms")
            return results

        except Exception as e:
            logger.error(f"❌ Batch generation failed: {str(e)}", exc_info=True)
            raise

    def _generate_1601c(
        self,
        month: int,
        year: int,
        transactions: List[Dict[str, Any]],
        company_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Form 1601-C: Monthly Withholding Tax Return"""

        # Filter withholding tax transactions
        wht_transactions = [
            t for t in transactions
            if t.get("transaction_type") == "withholding_tax"
        ]

        # Group by ATC code
        atc_breakdown = {}
        total_withheld = Decimal("0.00")

        for txn in wht_transactions:
            atc_code = txn.get("atc_code", "WC010")
            amount = Decimal(str(txn.get("amount_withheld", 0)))

            if atc_code not in atc_breakdown:
                atc_breakdown[atc_code] = {
                    "income_payment": Decimal("0.00"),
                    "amount_withheld": Decimal("0.00"),
                    "tax_rate": self.WHT_RATES.get(atc_code, 0.01)
                }

            atc_breakdown[atc_code]["amount_withheld"] += amount
            atc_breakdown[atc_code]["income_payment"] += amount / Decimal(str(atc_breakdown[atc_code]["tax_rate"]))
            total_withheld += amount

        return {
            "form_type": BIRFormType.FORM_1601C,
            "month": month,
            "year": year,
            "tin": company_info.get("tin"),
            "registered_name": company_info.get("name"),
            "total_amount_withheld": float(total_withheld),
            "total_remittance": float(total_withheld),
            "atc_breakdown": {
                atc: {
                    "income_payment": float(data["income_payment"]),
                    "amount_withheld": float(data["amount_withheld"]),
                    "tax_rate": data["tax_rate"]
                }
                for atc, data in atc_breakdown.items()
            },
            "generated_at": datetime.now().isoformat()
        }

    def _generate_2550q(
        self,
        quarter: int,
        year: int,
        transactions: List[Dict[str, Any]],
        company_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Form 2550Q: Quarterly VAT Return"""

        # Filter VAT transactions for the quarter
        quarter_months = range((quarter - 1) * 3 + 1, quarter * 3 + 1)
        vat_transactions = [
            t for t in transactions
            if t.get("transaction_type") in ["vat_output", "vat_input"]
            and t.get("month") in quarter_months
        ]

        total_sales = Decimal("0.00")
        taxable_sales = Decimal("0.00")
        vat_output = Decimal("0.00")
        vat_input = Decimal("0.00")

        for txn in vat_transactions:
            if txn.get("transaction_type") == "vat_output":
                sales_amount = Decimal(str(txn.get("amount", 0)))
                total_sales += sales_amount

                if txn.get("vat_applicable", True):
                    taxable_sales += sales_amount
                    vat_output += sales_amount * self.VAT_RATE

            elif txn.get("transaction_type") == "vat_input":
                vat_input += Decimal(str(txn.get("amount", 0)))

        net_vat_payable = max(vat_output - vat_input, Decimal("0.00"))

        return {
            "form_type": BIRFormType.FORM_2550Q,
            "quarter": quarter,
            "year": year,
            "tin": company_info.get("tin"),
            "registered_name": company_info.get("name"),
            "total_sales": float(total_sales),
            "taxable_sales": float(taxable_sales),
            "vat_exempt_sales": float(total_sales - taxable_sales),
            "vat_output": float(vat_output),
            "vat_input": float(vat_input),
            "net_vat_payable": float(net_vat_payable),
            "generated_at": datetime.now().isoformat()
        }

    def _generate_2550m(
        self,
        month: int,
        year: int,
        transactions: List[Dict[str, Any]],
        company_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Form 2550M: Monthly VAT Return"""

        # Filter VAT transactions for the month
        monthly_vat = [
            t for t in transactions
            if t.get("transaction_type") == "vat_output"
            and t.get("month") == month
        ]

        total_sales = Decimal("0.00")
        vat_exempt_sales = Decimal("0.00")
        vat_zero_rated = Decimal("0.00")
        vat_output = Decimal("0.00")

        for txn in monthly_vat:
            sales_amount = Decimal(str(txn.get("amount", 0)))
            total_sales += sales_amount

            if txn.get("vat_exempt", False):
                vat_exempt_sales += sales_amount
            elif txn.get("vat_zero_rated", False):
                vat_zero_rated += sales_amount
            else:
                vat_output += sales_amount * self.VAT_RATE

        net_vat_payable = vat_output

        return {
            "form_type": BIRFormType.FORM_2550M,
            "month": month,
            "year": year,
            "tin": company_info.get("tin"),
            "registered_name": company_info.get("name"),
            "total_sales": float(total_sales),
            "vat_exempt_sales": float(vat_exempt_sales),
            "vat_zero_rated": float(vat_zero_rated),
            "vat_output": float(vat_output),
            "net_vat_payable": float(net_vat_payable),
            "generated_at": datetime.now().isoformat()
        }

    def _generate_2307_batch(
        self,
        month: int,
        year: int,
        transactions: List[Dict[str, Any]],
        company_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Form 2307 Batch: Withholding Tax Certificates"""

        # Filter withholding tax transactions
        wht_transactions = [
            t for t in transactions
            if t.get("transaction_type") == "withholding_tax"
            and t.get("month") == month
        ]

        certificates = []
        total_certificates = 0
        total_amount_withheld = Decimal("0.00")

        for txn in wht_transactions:
            certificate = {
                "certificate_number": f"{year}{month:02d}-{total_certificates + 1:05d}",
                "payee_tin": txn.get("vendor_tin"),
                "payee_name": txn.get("vendor_name"),
                "income_payment": float(Decimal(str(txn.get("income_payment", 0)))),
                "atc_code": txn.get("atc_code", "WC010"),
                "tax_rate": self.WHT_RATES.get(txn.get("atc_code", "WC010"), 0.01),
                "amount_withheld": float(Decimal(str(txn.get("amount_withheld", 0)))),
                "payor_tin": company_info.get("tin"),
                "payor_name": company_info.get("name"),
                "date_withheld": txn.get("transaction_date")
            }

            certificates.append(certificate)
            total_certificates += 1
            total_amount_withheld += Decimal(str(certificate["amount_withheld"]))

        return {
            "form_type": BIRFormType.FORM_2307,
            "month": month,
            "year": year,
            "certificates": certificates,
            "total_certificates": total_certificates,
            "total_amount_withheld": float(total_amount_withheld),
            "payor_tin": company_info.get("tin"),
            "payor_name": company_info.get("name"),
            "generated_at": datetime.now().isoformat()
        }

    def _generate_summary(self, forms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of batch generation"""

        summary = {
            "total_forms": len(forms),
            "form_types": [],
            "totals": {}
        }

        for form in forms:
            form_type = form["form_type"]
            summary["form_types"].append(form_type)

            if form_type == BIRFormType.FORM_1601C:
                summary["totals"]["total_wht"] = form["total_amount_withheld"]

            elif form_type in [BIRFormType.FORM_2550Q, BIRFormType.FORM_2550M]:
                summary["totals"]["total_vat_payable"] = form["net_vat_payable"]

            elif form_type == BIRFormType.FORM_2307:
                summary["totals"]["total_2307_certificates"] = form["total_certificates"]

        return summary

    def validate_batch_data(
        self,
        month: int,
        year: int,
        transaction_data: List[Dict[str, Any]],
        forms: List[str]
    ) -> Dict[str, Any]:
        """
        Validate batch data before generation

        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []

        # Validate month/year
        if not (1 <= month <= 12):
            errors.append(f"Invalid month: {month} (must be 1-12)")

        if year < 2000 or year > 2100:
            errors.append(f"Invalid year: {year}")

        # Validate form types
        valid_forms = [BIRFormType.FORM_1601C, BIRFormType.FORM_2550Q,
                      BIRFormType.FORM_2550M, BIRFormType.FORM_2307]
        for form_type in forms:
            if form_type not in valid_forms:
                errors.append(f"Invalid form type: {form_type}")

        # Validate transaction data
        if not transaction_data:
            warnings.append("No transaction data provided - forms will be empty")

        # Check for required fields in transactions
        required_fields = ["transaction_type", "amount", "month", "year"]
        for idx, txn in enumerate(transaction_data[:10]):  # Sample first 10
            missing = [f for f in required_fields if f not in txn]
            if missing:
                warnings.append(f"Transaction {idx} missing fields: {missing}")

        is_valid = len(errors) == 0

        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "summary": f"{'✅ Valid' if is_valid else '❌ Invalid'} - {len(errors)} errors, {len(warnings)} warnings"
        }
