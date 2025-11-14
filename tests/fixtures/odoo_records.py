import pytest

@pytest.fixture
def sample_expense():
    return {
        "name": "Test Expense",
        "total_amount": 1000.00,
        "employee_id": 1,
        "product_id": 1,
        "company_id": 1,
    }

@pytest.fixture
def sample_warehouse_data():
    return {
        "agency": "RIM",
        "period": "2025-10",
        "total_expense": 123456.78,
    }
