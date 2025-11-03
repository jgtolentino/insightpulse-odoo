#!/usr/bin/env python3
"""
End-to-End Integration Test for Skill Hub
Tests Odoo, Superset, and Skills integration
"""
import requests
import json
import sys
from typing import Dict, Any
from datetime import datetime

# Configuration
BASE_URL = "https://mcp.insightpulseai.net"  # Change to your deployed URL
# BASE_URL = "http://localhost:8000"  # For local testing
BEARER_TOKEN = ""  # Set this from environment or .env file

def get_headers() -> Dict[str, str]:
    """Get authorization headers"""
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

def test_health() -> bool:
    """Test health endpoint"""
    print("\n🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"✅ Health check passed")
        print(f"   Status: {data['status']}")
        print(f"   Version: {data['version']}")
        print(f"   Odoo configured: {data['integrations']['odoo']['configured']}")
        print(f"   Superset configured: {data['integrations']['superset']['configured']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_skills_catalog() -> bool:
    """Test skills catalog endpoint"""
    print("\n🔍 Testing skills catalog...")
    try:
        response = requests.get(
            f"{BASE_URL}/skills/catalog",
            headers=get_headers(),
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        print(f"✅ Skills catalog retrieved")
        print(f"   Total skills: {data['total_skills']}")
        print(f"   Categories: {len(data['categories'])}")

        # Print some categories
        for category, info in list(data['categories'].items())[:3]:
            if 'count' in info:
                print(f"   - {category}: {info['count']} skills")
            elif 'skills' in info and isinstance(info['skills'], list):
                print(f"   - {category}: {len(info['skills'])} skills")

        return True
    except Exception as e:
        print(f"❌ Skills catalog failed: {e}")
        return False

def test_odoo_version() -> bool:
    """Test Odoo version endpoint"""
    print("\n🔍 Testing Odoo version...")
    try:
        response = requests.get(
            f"{BASE_URL}/odoo/version",
            headers=get_headers(),
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        print(f"✅ Odoo connection successful")
        print(f"   Server version: {data['version']['server_version']}")
        print(f"   Protocol version: {data['version']['protocol_version']}")
        return True
    except Exception as e:
        print(f"❌ Odoo version failed: {e}")
        return False

def test_odoo_search_partners() -> bool:
    """Test Odoo partner search"""
    print("\n🔍 Testing Odoo partner search...")
    try:
        payload = {
            "model": "res.partner",
            "method": "search_read",
            "args": [[("is_company", "=", True)]],
            "kwargs": {
                "fields": ["name", "email", "phone"],
                "limit": 5
            }
        }

        response = requests.post(
            f"{BASE_URL}/odoo/execute",
            headers=get_headers(),
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        print(f"✅ Odoo partner search successful")
        print(f"   Found {len(data['result'])} partners")
        if data['result']:
            print(f"   First partner: {data['result'][0].get('name', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Odoo partner search failed: {e}")
        return False

def test_odoo_create_lead() -> bool:
    """Test Odoo lead creation"""
    print("\n🔍 Testing Odoo lead creation...")
    try:
        payload = {
            "model": "crm.lead",
            "method": "create",
            "args": [{
                "name": f"Test Lead {datetime.now().strftime('%Y%m%d%H%M%S')}",
                "partner_name": "Test Company",
                "email_from": "test@example.com",
                "phone": "+1234567890",
                "type": "opportunity",
                "description": "Test lead created by Skill Hub integration test"
            }]
        }

        response = requests.post(
            f"{BASE_URL}/odoo/execute",
            headers=get_headers(),
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        print(f"✅ Odoo lead creation successful")
        print(f"   Created lead ID: {data['result']}")
        return True
    except Exception as e:
        print(f"❌ Odoo lead creation failed: {e}")
        return False

def test_superset_dashboards() -> bool:
    """Test Superset dashboards list"""
    print("\n🔍 Testing Superset dashboards...")
    try:
        payload = {
            "action": "dashboards"
        }

        response = requests.post(
            f"{BASE_URL}/superset/query",
            headers=get_headers(),
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        print(f"✅ Superset dashboards retrieved")
        print(f"   Found {len(data['result'])} dashboards")
        if data['result']:
            print(f"   First dashboard: {data['result'][0].get('dashboard_title', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Superset dashboards failed: {e}")
        return False

def test_superset_charts() -> bool:
    """Test Superset charts list"""
    print("\n🔍 Testing Superset charts...")
    try:
        payload = {
            "action": "charts"
        }

        response = requests.post(
            f"{BASE_URL}/superset/query",
            headers=get_headers(),
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        print(f"✅ Superset charts retrieved")
        print(f"   Found {len(data['result'])} charts")
        if data['result']:
            print(f"   First chart: {data['result'][0].get('slice_name', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Superset charts failed: {e}")
        return False

def test_authentication() -> bool:
    """Test bearer token authentication"""
    print("\n🔍 Testing authentication...")

    # Test without token
    try:
        response = requests.get(f"{BASE_URL}/skills/catalog", timeout=10)
        if response.status_code == 401:
            print("✅ Correctly rejected request without token")
        else:
            print(f"⚠️  Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return False

    # Test with invalid token
    try:
        headers = {"Authorization": "Bearer invalid-token-12345"}
        response = requests.get(
            f"{BASE_URL}/skills/catalog",
            headers=headers,
            timeout=10
        )
        if response.status_code == 401:
            print("✅ Correctly rejected request with invalid token")
        else:
            print(f"⚠️  Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return False

    # Test with valid token
    try:
        response = requests.get(
            f"{BASE_URL}/skills/catalog",
            headers=get_headers(),
            timeout=10
        )
        response.raise_for_status()
        print("✅ Correctly accepted request with valid token")
        return True
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("="*80)
    print("🧪 Skill Hub End-to-End Integration Tests")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Token configured: {'Yes' if BEARER_TOKEN else 'No (will fail auth tests)'}")
    print("="*80)

    tests = [
        ("Health Check", test_health),
        ("Authentication", test_authentication),
        ("Skills Catalog", test_skills_catalog),
        ("Odoo Version", test_odoo_version),
        ("Odoo Search Partners", test_odoo_search_partners),
        ("Odoo Create Lead", test_odoo_create_lead),
        ("Superset Dashboards", test_superset_dashboards),
        ("Superset Charts", test_superset_charts),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
            results.append((name, False))

    # Print summary
    print("\n" + "="*80)
    print("📊 Test Summary")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("="*80)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*80)

    return passed == total

if __name__ == "__main__":
    import os

    # Load token from environment
    BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
    if not BEARER_TOKEN:
        print("\n⚠️  Warning: BEARER_TOKEN not set. Auth tests will fail.")
        print("   Set it with: export BEARER_TOKEN='your-token-here'\n")

    # Allow overriding base URL
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        print(f"Using custom base URL: {BASE_URL}")

    success = run_all_tests()
    sys.exit(0 if success else 1)
