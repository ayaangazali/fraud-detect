"""
KAMCO Compliance System - Frontend to Backend Connectivity Tests
Tests if frontend pages are ready and connected to backend APIs
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import sys

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
results = {
    "connected": 0,
    "not_connected": 0,
    "missing": 0,
    "pages": []
}

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_section(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'-'*len(text)}{Colors.END}")

def check_file_exists(file_path: str) -> bool:
    """Check if file exists"""
    return os.path.exists(file_path)

def analyze_component(file_path: str, component_name: str) -> Dict:
    """Analyze a component/page for backend connectivity"""
    
    if not check_file_exists(file_path):
        return {
            "name": component_name,
            "exists": False,
            "status": "MISSING",
            "api_calls": [],
            "mock_data": False,
            "todos": []
        }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for API calls
    api_patterns = [
        r'apiClient\.(get|post|put|delete|patch)\(',
        r'fetch\([\'"].*?/api/',
        r'axios\.(get|post|put|delete|patch)\(',
        r'await\s+\w+\.(get|post|put|delete)\([\'"]\/api\/',
    ]
    
    api_calls = []
    for pattern in api_patterns:
        matches = re.findall(pattern, content)
        api_calls.extend(matches)
    
    # Check for mock data
    mock_patterns = [
        r'const\s+\w+\s*:\s*\w+\[\]\s*=\s*\[',  # const items: Type[] = [
        r'Mock\s+data',
        r'mock\w+',
        r'// TODO.*mock',
    ]
    
    has_mock_data = any(re.search(pattern, content, re.IGNORECASE) for pattern in mock_patterns)
    
    # Check for TODOs
    todo_pattern = r'//\s*TODO:?\s*(.+?)(?:\n|$)'
    todos = re.findall(todo_pattern, content, re.IGNORECASE)
    
    # Determine status
    if len(api_calls) > 0:
        status = "CONNECTED"
    elif has_mock_data or "TODO" in content:
        status = "NOT_CONNECTED"
    else:
        status = "UNKNOWN"
    
    return {
        "name": component_name,
        "exists": True,
        "status": status,
        "api_calls": api_calls,
        "mock_data": has_mock_data,
        "todos": todos
    }

def print_component_status(result: Dict):
    """Print component analysis result"""
    name = result["name"]
    
    if not result["exists"]:
        print(f"  ❌ {name}: {Colors.RED}MISSING{Colors.END}")
        results["missing"] += 1
        return
    
    status = result["status"]
    
    if status == "CONNECTED":
        color = Colors.GREEN
        icon = "✅"
        results["connected"] += 1
    elif status == "NOT_CONNECTED":
        color = Colors.YELLOW
        icon = "⚠️"
        results["not_connected"] += 1
    else:
        color = Colors.BLUE
        icon = "❔"
    
    print(f"  {icon} {name}: {color}{status}{Colors.END}")
    
    if result["api_calls"]:
        print(f"     └─ API calls found: {len(result['api_calls'])}")
    
    if result["mock_data"]:
        print(f"     └─ ⚠️  Mock data detected")
    
    if result["todos"]:
        print(f"     └─ TODOs: {len(result['todos'])}")
        for todo in result["todos"][:2]:  # Show first 2
            print(f"        • {todo.strip()}")
    
    results["pages"].append(result)

def test_frontend_pages():
    """Test all frontend pages"""
    
    base_path = "/Users/ayaangazali/Documents/hackathons/Kamco/frontend/src"
    
    pages = {
        "Authentication": [
            (f"{base_path}/pages/Login.tsx", "Login Page"),
        ],
        "Screening Workflow": [
            (f"{base_path}/pages/screening/UploadPage.tsx", "Upload Page"),
            (f"{base_path}/pages/screening/ScreeningQueuePage.tsx", "Screening Queue"),
        ],
        "Case Review": [
            (f"{base_path}/pages/review/CheckerReviewPage.tsx", "Checker Review"),
            (f"{base_path}/pages/review/FinalizerReviewPage.tsx", "Finalizer Review"),
        ],
        "Reports & Analytics": [
            (f"{base_path}/pages/reports/ReportsPage.tsx", "Reports Page"),
            (f"{base_path}/pages/audit/AuditLogsPage.tsx", "Audit Logs"),
        ],
        "Dashboard": [
            (f"{base_path}/pages/dashboard/DashboardPage.tsx", "Dashboard"),
        ]
    }
    
    for category, page_list in pages.items():
        print_section(f"{category}")
        for file_path, name in page_list:
            result = analyze_component(file_path, name)
            print_component_status(result)

def test_services():
    """Test service files"""
    print_section("Service Layer")
    
    base_path = "/Users/ayaangazali/Documents/hackathons/Kamco/frontend/src/services"
    
    services = [
        (f"{base_path}/authService.ts", "Auth Service"),
        (f"{base_path}/apiClient.ts", "API Client"),
    ]
    
    for file_path, name in services:
        result = analyze_component(file_path, name)
        print_component_status(result)

def test_components():
    """Test key components"""
    print_section("Key Components")
    
    base_path = "/Users/ayaangazali/Documents/hackathons/Kamco/frontend/src/components"
    
    components = [
        (f"{base_path}/providers/RealTimeProvider.tsx", "WebSocket Provider"),
        (f"{base_path}/screening/FileUploadComponent.tsx", "File Upload"),
    ]
    
    for file_path, name in components:
        result = analyze_component(file_path, name)
        print_component_status(result)

def analyze_backend_endpoints():
    """Analyze backend routes to list all available endpoints"""
    print_section("Backend Endpoints Available")
    
    backend_path = "/Users/ayaangazali/Documents/hackathons/Kamco/backend/routes"
    
    if not os.path.exists(backend_path):
        print(f"  {Colors.YELLOW}Backend routes directory not found{Colors.END}")
        return
    
    route_files = [
        "auth.py",
        "upload.py",
        "screening.py",
        "review.py",
        "checker.py",
        "finalizer.py",
        "reports.py",
        "audit.py",
        "scan.py"
    ]
    
    endpoints = {}
    
    for route_file in route_files:
        file_path = os.path.join(backend_path, route_file)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Find route decorators
            route_pattern = r'@router\.(get|post|put|delete|patch)\([\'"](.+?)[\'"]\)'
            matches = re.findall(route_pattern, content)
            
            if matches:
                module = route_file.replace('.py', '')
                endpoints[module] = matches
                print(f"\n  📁 {module.upper()}")
                for method, path in matches:
                    print(f"     {Colors.GREEN}{method.upper()}{Colors.END} /api/{module}{path}")
    
    return endpoints

def generate_integration_report():
    """Generate detailed integration report"""
    print_section("Integration Gap Analysis")
    
    gaps = [
        ("File Upload", "UploadPage.tsx", "POST /api/upload/blacklist", "Mock data, no API call"),
        ("Screening Queue", "ScreeningQueuePage.tsx", "GET /api/screening/queue", "Empty state, needs connection"),
        ("Checker Review", "CheckerReviewPage.tsx", "GET /api/review/checker/queue", "Mock data present"),
        ("Finalizer Review", "FinalizerReviewPage.tsx", "GET /api/review/finalizer/queue", "Mock data present"),
        ("Reports", "ReportsPage.tsx", "GET /api/reports/compliance", "Mock charts, no API"),
        ("Audit Logs", "AuditLogsPage.tsx", "GET /api/audit/logs", "Mock data, needs connection"),
        ("Dashboard", "DashboardPage.tsx", "GET /api/reports/dashboard-metrics", "Mock data present"),
    ]
    
    print(f"\n{Colors.BOLD}Critical Integration Gaps:{Colors.END}\n")
    
    for feature, component, endpoint, issue in gaps:
        print(f"  📌 {Colors.BOLD}{feature}{Colors.END}")
        print(f"     Component: {component}")
        print(f"     Backend:   {endpoint}")
        print(f"     Status:    {Colors.YELLOW}{issue}{Colors.END}\n")

def run_all_tests():
    """Run all frontend connectivity tests"""
    print_header("KAMCO FRONTEND TO BACKEND CONNECTIVITY TESTS")
    
    print(f"{Colors.BOLD}Analyzing: {Colors.END}Frontend Components\n")
    
    # Run tests
    test_frontend_pages()
    test_services()
    test_components()
    analyze_backend_endpoints()
    generate_integration_report()
    
    # Print summary
    print_header("CONNECTIVITY SUMMARY")
    
    total = results["connected"] + results["not_connected"] + results["missing"]
    
    print(f"{Colors.GREEN}✅ Connected:     {results['connected']}/{total}{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  Not Connected: {results['not_connected']}/{total}{Colors.END}")
    print(f"{Colors.RED}❌ Missing:       {results['missing']}/{total}{Colors.END}")
    
    if total > 0:
        connectivity_rate = (results["connected"] / total) * 100
        print(f"\n{Colors.BOLD}Connectivity Rate: {connectivity_rate:.1f}%{Colors.END}")
    
    # Assessment
    print(f"\n{Colors.BOLD}{Colors.CYAN}Overall Assessment:{Colors.END}")
    
    if results["connected"] >= 7:
        print(f"{Colors.GREEN}✅ Most features connected - Good progress!{Colors.END}")
    elif results["connected"] >= 3:
        print(f"{Colors.YELLOW}⚠️  Some features connected - More work needed{Colors.END}")
    else:
        print(f"{Colors.RED}❌ Few features connected - Significant integration required{Colors.END}")
    
    # Recommendations
    print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
    print(f"  1. Connect Upload page to POST /api/upload/blacklist")
    print(f"  2. Connect Screening Queue to GET /api/screening/queue")
    print(f"  3. Remove mock data from Review pages")
    print(f"  4. Connect Dashboard to GET /api/reports/dashboard-metrics")
    print(f"  5. Connect Reports to backend endpoints")
    print(f"  6. Connect Audit Logs to GET /api/audit/logs")
    
    print(f"\n{Colors.CYAN}📝 See BACKEND_TO_FRONTEND_TODO.md for detailed integration plan{Colors.END}\n")
    
    return 0 if results["missing"] == 0 else 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
