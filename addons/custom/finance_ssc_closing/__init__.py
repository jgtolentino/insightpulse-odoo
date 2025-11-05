# -*- coding: utf-8 -*-

from . import models
from . import wizard

def post_init_hook(cr, registry):
    """
    Post-installation hook to set up initial data
    """
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # Create default closing periods for current fiscal year
    ClosingPeriod = env['finance.closing.period']

    # Check if any periods exist
    if not ClosingPeriod.search([]):
        # Create periods for current year
        import datetime
        current_year = datetime.date.today().year

        for month in range(1, 13):
            period_name = f"{current_year}-{month:02d}"
            start_date = datetime.date(current_year, month, 1)

            # Calculate end date
            if month == 12:
                end_date = datetime.date(current_year, 12, 31)
            else:
                end_date = datetime.date(current_year, month + 1, 1) - datetime.timedelta(days=1)

            ClosingPeriod.create({
                'name': period_name,
                'start_date': start_date,
                'end_date': end_date,
                'fiscal_year': str(current_year),
                'state': 'draft',
            })

    return True
