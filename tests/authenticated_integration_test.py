"""
KAMCO Compliance System - Authenticated Integration Tests
Tests all backend endpoints with proper JWT authentication tokens
"""
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

# Test credentials
TEST_USERS = {
    "screener": {
        "email": "screener@kamco.com",
        "password": "Screener123"
    },
    "checker": {
        "email": "checker@kamco.com",
        "password": "Checker123"
    },
    "finalizer": {
        "email": "finalizer@kamco.com",
        "password": "Finalizer123"
    }
}

# Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

# Test results
test_results = {
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "tests": []
}

# Store tokens
tokens = {}

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_section(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*len(text)}{Colors.END}")

def print_test(name: str, status: str, message: str = ""):
    if status == "PASS":
        icon = "✅"
        color = Colors.GREEN
        test_results["passed"] += 1
    elif status == "FAIL":
        icon = "❌"
        color = Colors.RED
        test_results["failed"] += 1
    else:
        icon = "⚠️"
        color = Colors.YELLOW
        test_results["warnings"] += 1
    
    result = f"{icon} {name}: {color}{status}{Colors.END}"
    if message:
        result += f" - {message}"
    print(result)
    
    test_results["tests"].append({
        "name": name,
        "status": status,
        "message": message
    })

def login_as(role: str) -> Optional[str]:
    """Login as a specific role and return access token"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=TEST_USERS[role]
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            tokens[role] = token
            print_test(f"Login as {role}", "PASS", f"Token obtained")
            return token
        else:
            print_test(f"Login as {role}", "FAIL", f"Status: {response.status_code}")
            return None
    except Exception as e:
        print_test(f"Login as {role}", "FAIL", str(e))
        return None

def get_auth_headers(role: str) -> Dict[str, str]:
    """Get authorization headers for a role"""
    token = tokens.get(role)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def test_authenticated_endpoint(name: str, method: str, endpoint: str, role: str, 
                                 expected_status: int = 200, data: Dict = None, 
                                 params: Dict = None):
    """Test an endpoint with authentication"""
    url = f"{API_BASE}{endpoint}"
    headers = get_auth_headers(role)
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print_test(name, "FAIL", f"Unknown method: {method}")
            return None
        
        if response.status_code == expected_status:
            print_test(name, "PASS", f"Status: {response.status_code}")
            return response.json() if response.text else None
        else:
            print_test(name, "FAIL", f"Expected {expected_status}, got {response.status_code}")
            return None
    except Exception as e:
        print_test(name, "FAIL", str(e))
        return None

def run_authentication_tests():
    """Test authentication for all roles"""
    print_section("Authentication Tests")
    
    for role in ["screener", "checker", "finalizer"]:
        login_as(role)

def run_screening_tests():
    """Test screening endpoints"""
    print_section("Screening Endpoints (Screener Role)")
    
    # Get screening queue
    test_authenticated_endpoint(
        "Get Screening Queue",
        "GET",
        "/screening/queue",
        "screener"
    )
    
    # Get screening results
    test_authenticated_endpoint(
        "Get Screening Results",
        "GET",
        "/screening/results",
        "screener",
        params={"status": "flagged"}
    )
    
    # Get upload history
    test_authenticated_endpoint(
        "Get Upload History",
        "GET",
        "/upload/history",
        "screener"
    )

def run_review_tests():
    """Test review endpoints"""
    print_section("Review Endpoints")
    
    # Checker endpoints
    test_authenticated_endpoint(
        "Get Checker Queue",
        "GET",
        "/review/checker/queue",
        "checker"
    )
    
    # Finalizer endpoints
    test_authenticated_endpoint(
        "Get Finalizer Queue",
        "GET",
        "/review/finalizer/queue",
        "finalizer"
    )
    
    # Get all cases
    test_authenticated_endpoint(
        "Get Review Cases",
        "GET",
        "/review/cases",
        "checker",
        params={"role": "checker", "status": "pending"}
    )

def run_reports_tests():
    """Test reports endpoints"""
    print_section("Reports Endpoints (Finalizer Role)")
    
    test_authenticated_endpoint(
        "Get Compliance Report",
        "GET",
        "/reports/compliance",
        "finalizer"
    )
    
    test_authenticated_endpoint(
        "Get Screening Summary",
        "GET",
        "/reports/screening-summary",
        "finalizer"
    )
    
    test_authenticated_endpoint(
        "Get Risk Assessment",
        "GET",
        "/reports/risk-assessment",
        "finalizer"
    )
    
    test_authenticated_endpoint(
        "Get Dashboard Metrics",
        "GET",
        "/reports/dashboard-metrics",
        "finalizer"
    )

def run_audit_tests():
    """Test audit endpoints"""
    print_section("Audit Endpoints (Finalizer Role)")
    
    test_authenticated_endpoint(
        "Get Audit Logs",
        "GET",
        "/audit/logs",
        "finalizer",
        params={
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "page": 1,
            "page_size": 20
        }
    )
    
    test_authenticated_endpoint(
        "Get Security Events",
        "GET",
        "/audit/security-events",
        "finalizer"
    )
    
    test_authenticated_endpoint(
        "Get User Activity",
        "GET",
        "/audit/user-activity",
        "finalizer",
        params={"user_id": 1}
    )

def run_auth_tests():
    """Test auth endpoints"""
    print_section("Auth Endpoints")
    
    test_authenticated_endpoint(
        "Get Users List",
        "GET",
        "/auth/users",
        "finalizer",
        params={"role": "screener", "limit": 10}
    )
    
    # Test current user info
    test_authenticated_endpoint(
        "Get Current User (Screener)",
        "GET",
        "/auth/me",
        "screener"
    )
    
    test_authenticated_endpoint(
        "Get Current User (Checker)",
        "GET",
        "/auth/me",
        "checker"
    )
    
    test_authenticated_endpoint(
        "Get Current User (Finalizer)",
        "GET",
        "/auth/me",
        "finalizer"
    )

def print_summary():
    """Print test summary"""
    print_header("Test Summary")
    
    total = test_results["passed"] + test_results["failed"] + test_results["warnings"]
    passed_pct = (test_results["passed"] / total * 100) if total > 0 else 0
    failed_pct = (test_results["failed"] / total * 100) if total > 0 else 0
    warning_pct = (test_results["warnings"] / total * 100) if total > 0 else 0
    
    print(f"{Colors.GREEN}✅ Passed:    {test_results['passed']}/{total} ({passed_pct:.1f}%){Colors.END}")
    print(f"{Colors.RED}❌ Failed:    {test_results['failed']}/{total} ({failed_pct:.1f}%){Colors.END}")
    print(f"{Colors.YELLOW}⚠️  Warnings: {test_results['warnings']}/{total} ({warning_pct:.1f}%){Colors.END}")
    
    if test_results["failed"] > 0:
        print(f"\n{Colors.RED}Failed tests:{Colors.END}")
        for test in test_results["tests"]:
            if test["status"] == "FAIL":
                print(f"  • {test['name']}: {test['message']}")
    
    print()
    return test_results["failed"] == 0

def main():
    print_header("KAMCO Authenticated Integration Tests")
    print(f"Testing against: {Colors.BOLD}{BASE_URL}{Colors.END}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # First, verify backend is running
        response = requests.get(f"{API_BASE}/")
        if response.status_code != 200:
            print(f"{Colors.RED}❌ Backend not responding at {BASE_URL}{Colors.END}")
            sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ Cannot connect to backend: {e}{Colors.END}")
        sys.exit(1)
    
    # Run test suites
    run_authentication_tests()
    run_screening_tests()
    run_review_tests()
    run_reports_tests()
    run_audit_tests()
    run_auth_tests()
    
    # Print summary
    success = print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
