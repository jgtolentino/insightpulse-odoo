import pytest

pytestmark = pytest.mark.financial

def test_month_end_closing_process():
    """End-to-end month-end closing for one agency."""
    # TODO: implement
    pass

def test_journal_entry_validation():
    """Journal entries must balance and respect chart of accounts."""
    pass

def test_account_reconciliation():
    """Bank and ledger reconciliation rules."""
    pass

def test_trial_balance_generation():
    """Trial balance output is consistent with posted entries."""
    pass

def test_multi_agency_consolidation():
    """Consolidated reporting across 8 agencies with isolation."""
    pass

def test_immutable_posted_entries():
    """Posted entries cannot be edited, only reversed."""
    pass
