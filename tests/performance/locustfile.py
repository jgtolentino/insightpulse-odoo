#!/usr/bin/env python3
"""
Locust Performance Testing for InsightPulse Odoo

Simulates realistic user load to validate system performance under stress.
Tests critical paths: login, expense creation, report generation.

Usage:
    locust -f locustfile.py --host=http://localhost:8069 --users=50 --spawn-rate=5
"""

from locust import HttpUser, task, between
import random
import json


class OdooUser(HttpUser):
    """
    Simulates a typical Odoo user performing common operations.

    Load profile:
    - 40% browse expenses
    - 30% create expenses
    - 20% search/filter
    - 10% generate reports
    """

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Login before starting tasks"""
        self.login()

    def login(self):
        """Authenticate to Odoo"""
        response = self.client.post("/web/session/authenticate", json={
            "jsonrpc": "2.0",
            "params": {
                "db": "odoo",
                "login": "admin",
                "password": "admin"
            }
        })

        if response.status_code == 200:
            data = response.json()
            if data.get("result", {}).get("uid"):
                self.session_id = response.cookies.get("session_id")
                print(f"✓ Login successful (UID: {data['result']['uid']})")
            else:
                print(f"✗ Login failed: {data}")
        else:
            print(f"✗ Login request failed: {response.status_code}")

    @task(4)
    def browse_expenses(self):
        """Browse expense list (40% of traffic)"""
        with self.client.get(
            "/web/dataset/search_read",
            params={
                "model": "hr.expense",
                "domain": "[]",
                "fields": '["name","date","employee_id","unit_amount","state"]',
                "limit": 80,
                "offset": 0
            },
            name="Browse Expenses",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to browse expenses: {response.status_code}")

    @task(3)
    def create_expense(self):
        """Create new expense (30% of traffic)"""
        expense_data = {
            "name": f"Test Expense {random.randint(1000, 9999)}",
            "unit_amount": random.uniform(50.0, 500.0),
            "date": "2025-10-30",
            "employee_id": 1,  # Admin employee
            "product_id": random.choice([1, 2, 3]),  # Random expense category
        }

        with self.client.post(
            "/web/dataset/call_kw/hr.expense/create",
            json={
                "jsonrpc": "2.0",
                "params": {
                    "model": "hr.expense",
                    "method": "create",
                    "args": [expense_data],
                    "kwargs": {}
                }
            },
            name="Create Expense",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    response.success()
                else:
                    response.failure("Create returned no result")
            else:
                response.failure(f"Failed to create expense: {response.status_code}")

    @task(2)
    def search_expenses(self):
        """Search and filter expenses (20% of traffic)"""
        search_domain = random.choice([
            '[["state","=","submit"]]',  # Submitted expenses
            '[["unit_amount",">",100]]',  # Large expenses
            '[["date",">=","2025-01-01"]]',  # This year
        ])

        with self.client.get(
            "/web/dataset/search_read",
            params={
                "model": "hr.expense",
                "domain": search_domain,
                "fields": '["name","unit_amount","state"]',
                "limit": 20
            },
            name="Search Expenses",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Search failed: {response.status_code}")

    @task(1)
    def generate_report(self):
        """Generate expense report (10% of traffic)"""
        with self.client.post(
            "/web/dataset/call_kw/hr.expense/search_read",
            json={
                "jsonrpc": "2.0",
                "params": {
                    "model": "hr.expense",
                    "method": "search_read",
                    "args": [[]],
                    "kwargs": {
                        "fields": ["name", "unit_amount", "state", "employee_id"],
                        "limit": 100
                    }
                }
            },
            name="Generate Report",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    record_count = len(data["result"])
                    print(f"Generated report with {record_count} records")
                    response.success()
                else:
                    response.failure("Report generation failed")
            else:
                response.failure(f"Failed to generate report: {response.status_code}")


class AdminUser(HttpUser):
    """
    Simulates admin performing system operations.

    Load profile:
    - Module updates
    - User management
    - Settings changes
    """

    wait_time = between(5, 10)
    weight = 1  # Only 1 admin for every 10 normal users

    def on_start(self):
        """Login as admin"""
        self.client.post("/web/session/authenticate", json={
            "jsonrpc": "2.0",
            "params": {
                "db": "odoo",
                "login": "admin",
                "password": "admin"
            }
        })

    @task
    def view_system_settings(self):
        """View system settings"""
        with self.client.get(
            "/web#menu_id=1&action=1",
            name="View Settings",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Failed to load settings")


# Performance thresholds for validation
class PerformanceMetrics:
    """Define acceptable performance thresholds"""

    MAX_LOGIN_TIME_MS = 2000
    MAX_LIST_LOAD_TIME_MS = 1500
    MAX_CREATE_TIME_MS = 1000
    MAX_SEARCH_TIME_MS = 800

    @staticmethod
    def validate(operation, response_time_ms):
        """Validate if operation meets performance threshold"""
        thresholds = {
            "login": PerformanceMetrics.MAX_LOGIN_TIME_MS,
            "list": PerformanceMetrics.MAX_LIST_LOAD_TIME_MS,
            "create": PerformanceMetrics.MAX_CREATE_TIME_MS,
            "search": PerformanceMetrics.MAX_SEARCH_TIME_MS,
        }

        threshold = thresholds.get(operation, 2000)

        if response_time_ms > threshold:
            print(f"⚠️ Performance warning: {operation} took {response_time_ms}ms (threshold: {threshold}ms)")
            return False

        return True
