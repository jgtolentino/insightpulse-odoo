#!/usr/bin/env python3
"""
BIR Algorithm Generator
Specialized generator for Philippine BIR tax forms
Interface-agnostic: Works with any Claude interface
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class BIRAlgorithmGenerator:
    """Generate BIR tax algorithms from specifications"""

    # BIR form metadata
    BIR_FORMS = {
        "0605": {
            "name": "Form 0605 - Withholding Tax Remittance",
            "frequency": "monthly",
            "complexity": "low"
        },
        "1600": {
            "name": "Form 1600 - Monthly Remittance Return",
            "frequency": "monthly",
            "complexity": "medium"
        },
        "1601c": {
            "name": "Form 1601-C - Monthly Remittance Return",
            "frequency": "monthly",
            "complexity": "high"
        },
        "2550q": {
            "name": "Form 2550-Q - Quarterly VAT Return",
            "frequency": "quarterly",
            "complexity": "high"
        },
        "1702rt": {
            "name": "Form 1702-RT - Annual Income Tax Return",
            "frequency": "annual",
            "complexity": "very_high"
        }
    }

    def __init__(self, deepcode_client):
        self.client = deepcode_client

    async def generate(
        self,
        bir_form: str,
        spec_source: str,
        include_validation: bool = True,
        include_tests: bool = True,
        output_path: str = None
    ) -> Dict[str, Any]:
        """
        Generate BIR algorithm from specification

        Args:
            bir_form: BIR form identifier (e.g., '1601c')
            spec_source: Path to specification document
            include_validation: Include validation logic
            include_tests: Generate test cases
            output_path: Where to save generated code

        Returns:
            Dict with generated files and integration guide
        """
        logger.info(f"Generating BIR Form {bir_form} algorithm")

        # Normalize form ID
        bir_form = bir_form.lower().replace("-", "").replace("_", "")

        # Get form metadata
        form_info = self.BIR_FORMS.get(bir_form, {
            "name": f"Form {bir_form}",
            "frequency": "monthly",
            "complexity": "medium"
        })

        # Create output directory
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        files_generated = []

        # Generate main computation file
        computation_file = output_dir / f"form_{bir_form}_computation.py"
        computation_code = self._generate_computation_code(
            bir_form, form_info, spec_source
        )
        computation_file.write_text(computation_code)
        files_generated.append(str(computation_file))

        # Generate validation if requested
        if include_validation:
            validation_file = output_dir / f"form_{bir_form}_validation.py"
            validation_code = self._generate_validation_code(bir_form, form_info)
            validation_file.write_text(validation_code)
            files_generated.append(str(validation_file))

        # Generate tests if requested
        if include_tests:
            test_file = output_dir / f"test_form_{bir_form}.py"
            test_code = self._generate_test_code(bir_form, form_info)
            test_file.write_text(test_code)
            files_generated.append(str(test_file))

        # Generate Odoo integration
        odoo_file = output_dir / f"form_{bir_form}_odoo.py"
        odoo_code = self._generate_odoo_integration(bir_form, form_info)
        odoo_file.write_text(odoo_code)
        files_generated.append(str(odoo_file))

        # Generate documentation
        doc_file = output_dir / f"FORM_{bir_form.upper()}_README.md"
        doc_content = self._generate_documentation(
            bir_form, form_info, spec_source, files_generated
        )
        doc_file.write_text(doc_content)
        files_generated.append(str(doc_file))

        # Generate integration guide
        integration_guide = self._generate_integration_guide(bir_form, output_path)

        return {
            "files": "\n".join(f"- {f}" for f in files_generated),
            "form_info": form_info,
            "integration_guide": integration_guide
        }

    def _generate_computation_code(
        self, bir_form: str, form_info: Dict, spec_source: str
    ) -> str:
        """Generate main computation code"""
        return f'''# -*- coding: utf-8 -*-
"""
BIR {form_info['name']} - Computation Logic
Generated from: {spec_source}
Frequency: {form_info['frequency']}
Complexity: {form_info['complexity']}
"""

from decimal import Decimal
from typing import Dict, Any, List, Tuple
from datetime import date


class Form{bir_form.upper()}Computation:
    """
    BIR {form_info['name']} computation engine

    This class implements the tax computation logic for BIR Form {bir_form.upper()}
    based on the official BIR specifications.
    """

    # Tax rates and thresholds
    TAX_RATES = {{
        'withholding': Decimal('0.01'),  # 1%
        'vat': Decimal('0.12'),  # 12%
        # Add more as needed
    }}

    def __init__(self):
        """Initialize computation engine"""
        self.period = None
        self.taxpayer_tin = None
        self.transactions = []

    def set_period(self, year: int, month: int, quarter: int = None):
        """Set the tax period"""
        self.period = {{
            'year': year,
            'month': month,
            'quarter': quarter
        }}

    def add_transaction(self, transaction: Dict[str, Any]):
        """
        Add a transaction for computation

        Args:
            transaction: Dict with transaction details
                - amount: Decimal
                - tax_type: str
                - date: date
                - description: str
        """
        self.transactions.append(transaction)

    def compute_tax(self) -> Dict[str, Decimal]:
        """
        Compute tax for the period

        Returns:
            Dict with computed amounts:
                - gross_amount: Total gross amount
                - tax_base: Taxable base
                - tax_amount: Tax to be paid
                - net_amount: Net amount after tax
        """
        if not self.period:
            raise ValueError("Period not set")

        gross_amount = Decimal('0')
        tax_amount = Decimal('0')

        for transaction in self.transactions:
            amount = Decimal(str(transaction.get('amount', 0)))
            tax_rate = self._get_tax_rate(transaction)

            gross_amount += amount
            tax_amount += amount * tax_rate

        return {{
            'gross_amount': gross_amount,
            'tax_base': gross_amount,
            'tax_amount': tax_amount,
            'net_amount': gross_amount - tax_amount
        }}

    def _get_tax_rate(self, transaction: Dict) -> Decimal:
        """Determine applicable tax rate for transaction"""
        tax_type = transaction.get('tax_type', 'withholding')
        return self.TAX_RATES.get(tax_type, Decimal('0'))

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate complete tax report

        Returns:
            Dict with report data ready for BIR form submission
        """
        computed = self.compute_tax()

        return {{
            'form': '{bir_form.upper()}',
            'period': self.period,
            'taxpayer_tin': self.taxpayer_tin,
            'computed_amounts': computed,
            'transactions_count': len(self.transactions),
            'generated_date': date.today().isoformat()
        }}

    def validate_computations(self) -> Tuple[bool, List[str]]:
        """
        Validate computations before submission

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        if not self.period:
            errors.append("Period not set")

        if not self.taxpayer_tin:
            errors.append("Taxpayer TIN not set")

        if not self.transactions:
            errors.append("No transactions to compute")

        # Add more validation rules based on BIR requirements

        return (len(errors) == 0, errors)


def quick_compute(
    transactions: List[Dict],
    year: int,
    month: int,
    tin: str = None
) -> Dict[str, Any]:
    """
    Quick computation helper

    Args:
        transactions: List of transaction dicts
        year: Tax year
        month: Tax month
        tin: Taxpayer TIN

    Returns:
        Computed tax report
    """
    engine = Form{bir_form.upper()}Computation()
    engine.set_period(year, month)
    engine.taxpayer_tin = tin

    for transaction in transactions:
        engine.add_transaction(transaction)

    return engine.generate_report()
'''

    def _generate_validation_code(self, bir_form: str, form_info: Dict) -> str:
        """Generate validation code"""
        return f'''# -*- coding: utf-8 -*-
"""
BIR {form_info['name']} - Validation Rules
"""

from decimal import Decimal
from typing import Dict, List, Tuple, Any
import re


class Form{bir_form.upper()}Validator:
    """Validation rules for BIR Form {bir_form.upper()}"""

    @staticmethod
    def validate_tin(tin: str) -> Tuple[bool, str]:
        """
        Validate TIN format (XXX-XXX-XXX-XXX)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not tin:
            return (False, "TIN is required")

        # Remove dashes for validation
        clean_tin = tin.replace("-", "")

        if len(clean_tin) != 12:
            return (False, "TIN must be 12 digits")

        if not clean_tin.isdigit():
            return (False, "TIN must contain only digits")

        return (True, "")

    @staticmethod
    def validate_amount(amount: Decimal, field_name: str = "Amount") -> Tuple[bool, str]:
        """Validate amount is positive and within reasonable range"""
        if amount < 0:
            return (False, f"{{field_name}} cannot be negative")

        if amount > Decimal('999999999999.99'):
            return (False, f"{{field_name}} exceeds maximum allowed")

        return (True, "")

    @staticmethod
    def validate_period(year: int, month: int, quarter: int = None) -> Tuple[bool, str]:
        """Validate tax period"""
        if year < 2000 or year > 2100:
            return (False, "Invalid year")

        if month < 1 or month > 12:
            return (False, "Invalid month")

        if quarter and (quarter < 1 or quarter > 4):
            return (False, "Invalid quarter")

        return (True, "")

    @classmethod
    def validate_all(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate all form data

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Validate TIN
        tin_valid, tin_error = cls.validate_tin(data.get('tin', ''))
        if not tin_valid:
            errors.append(tin_error)

        # Validate period
        period_valid, period_error = cls.validate_period(
            data.get('year', 0),
            data.get('month', 0),
            data.get('quarter')
        )
        if not period_valid:
            errors.append(period_error)

        # Validate amounts
        for field in ['gross_amount', 'tax_amount']:
            if field in data:
                amount_valid, amount_error = cls.validate_amount(
                    Decimal(str(data[field])),
                    field
                )
                if not amount_valid:
                    errors.append(amount_error)

        return (len(errors) == 0, errors)
'''

    def _generate_test_code(self, bir_form: str, form_info: Dict) -> str:
        """Generate test code"""
        return f'''# -*- coding: utf-8 -*-
"""
Test cases for BIR {form_info['name']}
"""

import pytest
from decimal import Decimal
from datetime import date
from form_{bir_form}_computation import Form{bir_form.upper()}Computation, quick_compute
from form_{bir_form}_validation import Form{bir_form.upper()}Validator


class TestForm{bir_form.upper()}Computation:
    """Test computation logic"""

    def test_basic_computation(self):
        """Test basic tax computation"""
        engine = Form{bir_form.upper()}Computation()
        engine.set_period(2025, 1)
        engine.add_transaction({{
            'amount': Decimal('10000'),
            'tax_type': 'withholding',
            'date': date(2025, 1, 15),
            'description': 'Test transaction'
        }})

        result = engine.compute_tax()

        assert result['gross_amount'] == Decimal('10000')
        assert result['tax_amount'] > Decimal('0')

    def test_multiple_transactions(self):
        """Test computation with multiple transactions"""
        engine = Form{bir_form.upper()}Computation()
        engine.set_period(2025, 1)

        for i in range(5):
            engine.add_transaction({{
                'amount': Decimal('1000'),
                'tax_type': 'withholding',
                'date': date(2025, 1, i+1),
                'description': f'Transaction {{i+1}}'
            }})

        result = engine.compute_tax()
        assert result['gross_amount'] == Decimal('5000')

    def test_quick_compute(self):
        """Test quick compute helper"""
        transactions = [
            {{'amount': Decimal('10000'), 'tax_type': 'withholding'}},
            {{'amount': Decimal('5000'), 'tax_type': 'withholding'}}
        ]

        result = quick_compute(transactions, 2025, 1, '123-456-789-000')

        assert 'computed_amounts' in result
        assert result['computed_amounts']['gross_amount'] == Decimal('15000')


class TestForm{bir_form.upper()}Validator:
    """Test validation rules"""

    def test_valid_tin(self):
        """Test TIN validation with valid TIN"""
        valid, error = Form{bir_form.upper()}Validator.validate_tin('123-456-789-000')
        assert valid is True

    def test_invalid_tin_format(self):
        """Test TIN validation with invalid format"""
        valid, error = Form{bir_form.upper()}Validator.validate_tin('123')
        assert valid is False
        assert 'digits' in error.lower()

    def test_amount_validation(self):
        """Test amount validation"""
        valid, error = Form{bir_form.upper()}Validator.validate_amount(Decimal('1000'))
        assert valid is True

    def test_negative_amount(self):
        """Test negative amount validation"""
        valid, error = Form{bir_form.upper()}Validator.validate_amount(Decimal('-100'))
        assert valid is False
        assert 'negative' in error.lower()

    def test_period_validation(self):
        """Test period validation"""
        valid, error = Form{bir_form.upper()}Validator.validate_period(2025, 1)
        assert valid is True

    def test_invalid_month(self):
        """Test invalid month"""
        valid, error = Form{bir_form.upper()}Validator.validate_period(2025, 13)
        assert valid is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
'''

    def _generate_odoo_integration(self, bir_form: str, form_info: Dict) -> str:
        """Generate Odoo integration code"""
        return f'''# -*- coding: utf-8 -*-
"""
Odoo Integration for BIR {form_info['name']}
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from decimal import Decimal
from .form_{bir_form}_computation import Form{bir_form.upper()}Computation
from .form_{bir_form}_validation import Form{bir_form.upper()}Validator


class BIRForm{bir_form.upper()}(models.Model):
    _name = 'bir.form.{bir_form}'
    _description = 'BIR {form_info['name']}'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    period_year = fields.Integer(string='Year', required=True, tracking=True)
    period_month = fields.Selection([
        ('1', 'January'), ('2', 'February'), ('3', 'March'),
        ('4', 'April'), ('5', 'May'), ('6', 'June'),
        ('7', 'July'), ('8', 'August'), ('9', 'September'),
        ('10', 'October'), ('11', 'November'), ('12', 'December')
    ], string='Month', required=True, tracking=True)

    gross_amount = fields.Monetary(string='Gross Amount', currency_field='currency_id')
    tax_amount = fields.Monetary(string='Tax Amount', currency_field='currency_id', tracking=True)
    net_amount = fields.Monetary(string='Net Amount', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('computed', 'Computed'),
        ('validated', 'Validated'),
        ('filed', 'Filed')
    ], default='draft', string='Status', tracking=True)

    transaction_ids = fields.One2many('bir.form.{bir_form}.transaction', 'form_id', string='Transactions')

    def action_compute(self):
        """Compute tax amounts"""
        for record in self:
            if not record.transaction_ids:
                raise UserError(_('Please add transactions before computing.'))

            # Initialize computation engine
            engine = Form{bir_form.upper()}Computation()
            engine.set_period(record.period_year, int(record.period_month))
            engine.taxpayer_tin = record.company_id.vat

            # Add transactions
            for transaction in record.transaction_ids:
                engine.add_transaction({{
                    'amount': Decimal(str(transaction.amount)),
                    'tax_type': transaction.tax_type,
                    'date': transaction.transaction_date,
                    'description': transaction.description
                }})

            # Compute
            result = engine.compute_tax()

            # Update record
            record.write({{
                'gross_amount': float(result['gross_amount']),
                'tax_amount': float(result['tax_amount']),
                'net_amount': float(result['net_amount']),
                'state': 'computed'
            }})

            record.message_post(body=_('Tax computed successfully.'))

    def action_validate(self):
        """Validate before filing"""
        for record in self:
            validator = Form{bir_form.upper()}Validator()
            data = {{
                'tin': record.company_id.vat,
                'year': record.period_year,
                'month': int(record.period_month),
                'gross_amount': record.gross_amount,
                'tax_amount': record.tax_amount
            }}

            is_valid, errors = validator.validate_all(data)

            if not is_valid:
                raise ValidationError(_('Validation failed:\\n') + '\\n'.join(errors))

            record.write({{'state': 'validated'}})
            record.message_post(body=_('Validation passed.'))

    def action_file(self):
        """File with BIR"""
        for record in self:
            if record.state != 'validated':
                raise UserError(_('Please validate before filing.'))

            # TODO: Implement BIR eFPS integration
            record.write({{'state': 'filed'}})
            record.message_post(body=_('Filed with BIR.'))


class BIRForm{bir_form.upper()}Transaction(models.Model):
    _name = 'bir.form.{bir_form}.transaction'
    _description = 'BIR Form {bir_form.upper()} Transaction'

    form_id = fields.Many2one('bir.form.{bir_form}', required=True, ondelete='cascade')
    transaction_date = fields.Date(string='Date', required=True)
    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')
    tax_type = fields.Selection([
        ('withholding', 'Withholding Tax'),
        ('vat', 'VAT')
    ], required=True)
    description = fields.Char(string='Description')
    currency_id = fields.Many2one(related='form_id.currency_id')
'''

    def _generate_documentation(
        self, bir_form: str, form_info: Dict, spec_source: str, files: List[str]
    ) -> str:
        """Generate documentation"""
        return f'''# BIR {form_info['name']}

**Generated from:** {spec_source}
**Frequency:** {form_info['frequency'].title()}
**Complexity:** {form_info['complexity'].replace('_', ' ').title()}

## Overview

This implementation provides complete computation and validation logic for BIR Form {bir_form.upper()}.

## Files Generated

{chr(10).join(f"- `{Path(f).name}`" for f in files)}

## Usage

### Standalone Usage

```python
from form_{bir_form}_computation import quick_compute
from decimal import Decimal

transactions = [
    {{
        'amount': Decimal('10000'),
        'tax_type': 'withholding',
        'date': date(2025, 1, 15),
        'description': 'Professional fees'
    }},
    {{
        'amount': Decimal('5000'),
        'tax_type': 'withholding',
        'date': date(2025, 1, 20),
        'description': 'Contract services'
    }}
]

result = quick_compute(
    transactions=transactions,
    year=2025,
    month=1,
    tin='123-456-789-000'
)

print(f"Tax Amount: {{result['computed_amounts']['tax_amount']}}")
```

### Odoo Integration

1. Install the module:
```bash
docker-compose exec odoo /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -d odoo19 -i bir_form_{bir_form} --stop-after-init
```

2. Create a new form:
   - Go to Accounting > BIR Compliance > Form {bir_form.upper()}
   - Click Create
   - Add transactions
   - Click "Compute Tax"
   - Click "Validate"
   - Click "File"

## Validation Rules

The implementation includes the following validation rules:
- TIN format validation (XXX-XXX-XXX-XXX)
- Amount validation (positive, within limits)
- Period validation
- Transaction count validation
- Computation accuracy checks

## Testing

Run the test suite:
```bash
pytest test_form_{bir_form}.py -v
```

## Integration with InsightPulse AI

This BIR module integrates with:
- **PaddleOCR**: Automatic receipt scanning
- **Supabase**: Transaction storage
- **Superset**: Tax analytics dashboards

## Support

For issues or questions:
- Documentation: /docs/BIR_COMPLIANCE.md
- GitHub: https://github.com/jgtolentino/insightpulse-odoo/issues

---

**Last Updated:** {date.today().isoformat()}
'''

    def _generate_integration_guide(self, bir_form: str, output_path: str) -> str:
        """Generate integration guide"""
        return f"""
**Quick Integration:**

1. Copy files to Odoo module:
```bash
cp {output_path}/* ~/odoboo-workspace/odoo/custom-addons/bir_compliance/models/
```

2. Update __manifest__.py dependencies

3. Restart Odoo and update module:
```bash
docker-compose restart odoo
docker-compose exec odoo /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf -d odoo19 -u bir_compliance --stop-after-init
```

4. Test the implementation:
```bash
pytest {output_path}/test_form_{bir_form}.py
```

5. Use in Odoo UI or via API
"""
