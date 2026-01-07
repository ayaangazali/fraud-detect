"""
Phase 4: Excel Parser Enhancement - Test Suite
Tests upload endpoint and Excel parsing with sample data
"""
import sys
import os
import requests
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"
SAMPLE_DATA_PATH = Path(__file__).parent.parent / "sample-data"


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(test_name, success, message=""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"    {message}")


def test_server_health():
    """Test 1: Check if server is running"""
    print_header("TEST 1: Server Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200
        print_result("Server health check", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Server health check", False, str(e))
        return False


def register_test_user():
    """Register a test user for authentication"""
    print_header("TEST 2: Register Test User")
    
    try:
        payload = {
            "username": "phase4_tester",
            "email": "phase4@test.com",
            "password": "Testpass123",  # Strong password with uppercase
            "role": "screener"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=payload)
        
        if response.status_code == 201:
            print_result("User registration", True, "New user registered")
            return True
        elif response.status_code == 400 and "already registered" in response.text.lower():
            print_result("User registration", True, "User already exists (OK)")
            return True
        else:
            print_result("User registration", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("User registration", False, str(e))
        return False


def login_test_user():
    """Test 3: Login and get JWT token"""
    print_header("TEST 3: User Login")
    
    try:
        payload = {
            "email": "phase4@test.com",
            "password": "Testpass123"  # Match registration password
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print_result("User login", True, f"Token received: {token[:20]}...")
            return token
        else:
            print_result("User login", False, f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print_result("User login", False, str(e))
        return None


def test_validate_blacklist_file(token):
    """Test 4: Validate blacklist Excel file"""
    print_header("TEST 4: Validate Blacklist File")
    
    blacklist_file = SAMPLE_DATA_PATH / "blacklist_comprehensive.xlsx"
    
    if not blacklist_file.exists():
        print_result("Validate blacklist file", False, f"File not found: {blacklist_file}")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(blacklist_file, 'rb') as f:
            files = {'file': (blacklist_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{API_URL}/upload/blacklist/validate", files=files, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print_result("Validate blacklist file", True, f"Valid file with {data.get('preview', {}).get('total_rows', 0)} rows")
            print(f"    Preview: {data.get('preview', {}).get('valid_records', 0)} valid records")
            return True
        else:
            print_result("Validate blacklist file", False, f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_result("Validate blacklist file", False, str(e))
        return False


def test_upload_blacklist(token):
    """Test 5: Upload blacklist Excel file"""
    print_header("TEST 5: Upload Blacklist File")
    
    blacklist_file = SAMPLE_DATA_PATH / "blacklist_comprehensive.xlsx"
    
    if not blacklist_file.exists():
        print_result("Upload blacklist", False, f"File not found: {blacklist_file}")
        return False, None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        with open(blacklist_file, 'rb') as f:
            files = {'file': (blacklist_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(f"{API_URL}/upload/blacklist", files=files, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            uploaded_data = data.get('data', {})
            stored_count = uploaded_data.get('stored_count', 0)
            batch_id = uploaded_data.get('batch_id', 'unknown')
            
            print_result("Upload blacklist", True, f"Uploaded {stored_count} entries")
            print(f"    Batch ID: {batch_id}")
            print(f"    Total rows: {uploaded_data.get('total_rows', 0)}")
            print(f"    Valid records: {uploaded_data.get('valid_records', 0)}")
            print(f"    Errors: {uploaded_data.get('error_count', 0)}")
            
            return True, batch_id
        else:
            print_result("Upload blacklist", False, f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print_result("Upload blacklist", False, str(e))
        return False, None


def test_get_blacklist_entries(token):
    """Test 6: Retrieve blacklist entries"""
    print_header("TEST 6: Get Blacklist Entries")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/upload/blacklist?limit=10", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            entries_data = data.get('data', {})
            total = entries_data.get('total', 0)
            entries = entries_data.get('entries', [])
            
            print_result("Get blacklist entries", True, f"Retrieved {len(entries)} of {total} total entries")
            
            if entries:
                first_entry = entries[0]
                print(f"    First entry:")
                print(f"      - Name (Arabic): {first_entry.get('name_arabic', 'N/A')}")
                print(f"      - Civil ID: {first_entry.get('civil_id', 'N/A')}")
                print(f"      - Source: {first_entry.get('source', 'N/A')}")
                print(f"      - Risk Level: {first_entry.get('risk_level', 'N/A')}")
            
            return True
        else:
            print_result("Get blacklist entries", False, f"Status: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Get blacklist entries", False, str(e))
        return False


def test_search_blacklist(token):
    """Test 7: Search blacklist entries"""
    print_header("TEST 7: Search Blacklist")
    
    search_queries = ["أحمد", "272081412355"]  # Arabic name and Civil ID from sample
    
    all_success = True
    for query in search_queries:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{API_URL}/upload/blacklist/search/{query}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                result_count = data.get('data', {}).get('result_count', 0)
                print_result(f"Search: '{query}'", True, f"Found {result_count} matches")
            else:
                print_result(f"Search: '{query}'", False, f"Status: {response.status_code}")
                all_success = False
                
        except Exception as e:
            print_result(f"Search: '{query}'", False, str(e))
            all_success = False
    
    return all_success


def test_excel_parser_directly():
    """Test 8: Test Excel parser utility directly"""
    print_header("TEST 8: Direct Excel Parser Test")
    
    try:
        from utils.excel_parser import ExcelParser
        
        blacklist_file = SAMPLE_DATA_PATH / "blacklist_comprehensive.xlsx"
        
        if not blacklist_file.exists():
            print_result("Direct parser test", False, f"File not found: {blacklist_file}")
            return False
        
        # Test parser
        parser = ExcelParser(file_path=str(blacklist_file))
        
        # Validate
        validation = parser.validate_blacklist_file()
        if not validation['valid']:
            print_result("Direct parser test", False, f"Validation failed: {validation['error']}")
            return False
        
        # Parse
        records, summary = parser.parse_blacklist()
        
        print_result("Direct parser test", True, f"Parsed {len(records)} records")
        print(f"    Sheet: {summary['sheet_name']}")
        print(f"    Batch ID: {summary['batch_id']}")
        print(f"    Errors: {summary['error_count']}")
        
        if records:
            print(f"    Sample record:")
            print(f"      - Name: {records[0].get('name_arabic', 'N/A')}")
            print(f"      - Civil ID: {records[0].get('civil_id', 'N/A')}")
        
        return True
        
    except Exception as e:
        print_result("Direct parser test", False, str(e))
        return False


def test_database_model():
    """Test 9: Test BlacklistEntry model"""
    print_header("TEST 9: Database Model Test")
    
    try:
        from models.blacklist import BlacklistEntry
        from database.connection import engine, Base
        
        # Create table
        Base.metadata.create_all(bind=engine)
        
        print_result("Database model test", True, "BlacklistEntry table created/verified")
        return True
        
    except Exception as e:
        print_result("Database model test", False, str(e))
        return False


def run_all_tests():
    """Run all Phase 4 tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + "  PHASE 4: EXCEL PARSER ENHANCEMENT - TEST SUITE".center(78) + "║")
    print("║" + "  Testing Tasks 19-20: Upload & Parse Blacklist Excel".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    
    results = {}
    
    # Test 1: Server health
    results['health'] = test_server_health()
    if not results['health']:
        print("\n❌ Server is not running. Please start the server with:")
        print("   cd backend && python3 main.py")
        return
    
    # Test 2 & 3: Authentication
    results['register'] = register_test_user()
    token = login_test_user()
    results['login'] = token is not None
    
    if not token:
        print("\n❌ Authentication failed. Cannot proceed with upload tests.")
        return
    
    # Test 4-7: Upload and API tests
    results['validate'] = test_validate_blacklist_file(token)
    results['upload'], batch_id = test_upload_blacklist(token)
    results['get_entries'] = test_get_blacklist_entries(token)
    results['search'] = test_search_blacklist(token)
    
    # Test 8-9: Direct utility tests
    results['parser'] = test_excel_parser_directly()
    results['model'] = test_database_model()
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if failed == 0:
        print("\n" + "🎉" * 40)
        print("\n✅ ALL TESTS PASSED! PHASE 4 COMPLETE!")
        print("\n" + "🎉" * 40)
        print("\n✅ Task 19: Upload endpoint - COMPLETE")
        print("✅ Task 20: Multi-sheet Excel parsing - COMPLETE")
        print("\n📊 Phase 4 Status: 100% COMPLETE")
        print("\nReady to proceed to Phase 5: Fuzzy Matching & Deduplication")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    run_all_tests()
