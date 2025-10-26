#!/usr/bin/env python3
"""
Test script for Superset Connector module

This script validates:
- Module structure is correct
- All required files exist
- Python files compile successfully
- XML files are valid
- Manifest is properly configured
"""

import os
import sys
import py_compile
import xml.etree.ElementTree as ET
from pathlib import Path


def test_module_structure():
    """Test that module structure is correct"""
    print("Testing module structure...")
    
    module_path = Path("addons/custom/superset_connector")
    
    if not module_path.exists():
        print(f"❌ Module directory not found: {module_path}")
        return False
    
    required_files = [
        "__init__.py",
        "__manifest__.py",
        "models/__init__.py",
        "models/res_config_settings.py",
        "models/superset_token.py",
        "controllers/__init__.py",
        "controllers/embedded.py",
        "views/res_config_settings_views.xml",
        "views/superset_menu.xml",
        "security/ir.model.access.csv",
        "sql/erp_analytics_views.sql",
        "README.rst",
    ]
    
    missing = []
    for file in required_files:
        file_path = module_path / file
        if not file_path.exists():
            missing.append(file)
            print(f"❌ Missing: {file}")
        else:
            print(f"✅ Found: {file}")
    
    if missing:
        print(f"\n❌ {len(missing)} required files missing")
        return False
    
    print("✅ All required files present")
    return True


def test_python_syntax():
    """Test that all Python files compile"""
    print("\nTesting Python syntax...")
    
    module_path = Path("addons/custom/superset_connector")
    python_files = list(module_path.rglob("*.py"))
    
    errors = []
    for py_file in python_files:
        try:
            py_compile.compile(str(py_file), doraise=True)
            print(f"✅ {py_file.relative_to(module_path)}")
        except py_compile.PyCompileError as e:
            errors.append(str(py_file))
            print(f"❌ {py_file.relative_to(module_path)}: {e}")
    
    if errors:
        print(f"\n❌ {len(errors)} Python files have syntax errors")
        return False
    
    print("✅ All Python files compile successfully")
    return True


def test_xml_validity():
    """Test that all XML files are valid"""
    print("\nTesting XML validity...")
    
    module_path = Path("addons/custom/superset_connector")
    xml_files = list(module_path.rglob("*.xml"))
    
    errors = []
    for xml_file in xml_files:
        try:
            ET.parse(str(xml_file))
            print(f"✅ {xml_file.relative_to(module_path)}")
        except ET.ParseError as e:
            errors.append(str(xml_file))
            print(f"❌ {xml_file.relative_to(module_path)}: {e}")
    
    if errors:
        print(f"\n❌ {len(errors)} XML files are invalid")
        return False
    
    print("✅ All XML files are valid")
    return True


def test_manifest():
    """Test that manifest is properly configured"""
    print("\nTesting manifest configuration...")
    
    manifest_path = Path("addons/custom/superset_connector/__manifest__.py")
    
    try:
        # Read manifest
        with open(manifest_path) as f:
            content = f.read()
        
        # Execute to get dictionary
        manifest = eval(content)
        
        # Check required fields
        required_fields = ['name', 'version', 'category', 'depends', 'data']
        missing = [f for f in required_fields if f not in manifest]
        
        if missing:
            print(f"❌ Missing fields in manifest: {missing}")
            return False
        
        print(f"✅ Module name: {manifest['name']}")
        print(f"✅ Version: {manifest['version']}")
        print(f"✅ Category: {manifest['category']}")
        print(f"✅ Dependencies: {manifest['depends']}")
        print(f"✅ Data files: {len(manifest['data'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False


def test_sql_views():
    """Test that SQL file exists and is readable"""
    print("\nTesting SQL views...")
    
    sql_path = Path("addons/custom/superset_connector/sql/erp_analytics_views.sql")
    
    if not sql_path.exists():
        print("❌ SQL views file not found")
        return False
    
    try:
        with open(sql_path) as f:
            content = f.read()
        
        # Check for expected view names
        expected_views = [
            'vw_sales_kpi_day',
            'vw_product_performance',
            'vw_customer_ltv',
            'vw_stock_level_summary',
            'vw_inventory_turnover',
            'vw_ar_aging',
            'vw_monthly_revenue',
            'vw_employee_headcount',
        ]
        
        missing = []
        for view in expected_views:
            if view not in content:
                missing.append(view)
                print(f"❌ Missing view: {view}")
            else:
                print(f"✅ Found view: {view}")
        
        if missing:
            print(f"\n❌ {len(missing)} expected views missing")
            return False
        
        print("✅ All expected views present in SQL file")
        return True
        
    except Exception as e:
        print(f"❌ Error reading SQL file: {e}")
        return False


def test_documentation():
    """Test that documentation exists"""
    print("\nTesting documentation...")
    
    docs = [
        ("Module README", "addons/custom/superset_connector/README.rst"),
        ("Integration Guide", "docs/SUPERSET_INTEGRATION.md"),
        ("BI Architecture", "docs/BI_ARCHITECTURE.md"),
        ("Quick Start", "docs/QUICKSTART_SUPERSET.md"),
    ]
    
    missing = []
    for name, path in docs:
        doc_path = Path(path)
        if not doc_path.exists():
            missing.append(name)
            print(f"❌ Missing: {name}")
        else:
            size = doc_path.stat().st_size
            print(f"✅ Found: {name} ({size} bytes)")
    
    if missing:
        print(f"\n❌ {len(missing)} documentation files missing")
        return False
    
    print("✅ All documentation present")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Superset Connector Module Tests")
    print("=" * 60)
    
    tests = [
        ("Module Structure", test_module_structure),
        ("Python Syntax", test_python_syntax),
        ("XML Validity", test_xml_validity),
        ("Manifest Configuration", test_manifest),
        ("SQL Views", test_sql_views),
        ("Documentation", test_documentation),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
