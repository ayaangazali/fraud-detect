#!/bin/bash

# KAMCO Compliance System - Master Test Runner
# Runs all integration and connectivity tests

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Users/ayaangazali/Documents/hackathons/Kamco"
BACKEND_URL="http://127.0.0.1:8000"
FRONTEND_URL="http://localhost:3000"

echo -e "${BOLD}${CYAN}"
echo "================================================================================"
echo "               KAMCO COMPLIANCE SYSTEM - INTEGRATION TEST SUITE               "
echo "================================================================================"
echo -e "${NC}"

echo -e "${BOLD}Test Suite: ${NC}Backend API + Frontend Connectivity"
echo -e "${BOLD}Date: ${NC}$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Function to check if service is running
check_service() {
    local name=$1
    local url=$2
    
    echo -n "Checking $name... "
    
    if curl -s --max-time 5 "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Running${NC}"
        return 0
    else
        echo -e "${RED}❌ Not running${NC}"
        return 1
    fi
}

# Check prerequisites
echo -e "${BOLD}${BLUE}Checking Prerequisites${NC}"
echo "-----------------------------------------------------------"

BACKEND_RUNNING=false
FRONTEND_RUNNING=false

if check_service "Backend" "$BACKEND_URL/health"; then
    BACKEND_RUNNING=true
fi

if check_service "Frontend" "$FRONTEND_URL"; then
    FRONTEND_RUNNING=true
fi

echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "Python: ${GREEN}✅ $PYTHON_VERSION${NC}"
else
    echo -e "Python: ${RED}❌ Not found${NC}"
    exit 1
fi

# Check required Python packages
echo -n "Python requests library: "
if python3 -c "import requests" 2>/dev/null; then
    echo -e "${GREEN}✅ Installed${NC}"
else
    echo -e "${YELLOW}⚠️  Not installed - installing...${NC}"
    pip3 install requests > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "   ${GREEN}✅ Installed successfully${NC}"
    else
        echo -e "   ${RED}❌ Installation failed${NC}"
        exit 1
    fi
fi

echo ""

# Test 1: Backend API Integration Tests
echo -e "${BOLD}${CYAN}"
echo "================================================================================"
echo "                         TEST 1: BACKEND API INTEGRATION                       "
echo "================================================================================"
echo -e "${NC}"

if [ "$BACKEND_RUNNING" = true ]; then
    python3 "$PROJECT_ROOT/tests/backend_integration_test.py"
    BACKEND_TEST_RESULT=$?
    echo ""
else
    echo -e "${RED}❌ Cannot run backend tests - backend is not running${NC}"
    echo -e "${YELLOW}   Start backend: cd backend && python3 main.py${NC}"
    BACKEND_TEST_RESULT=1
    echo ""
fi

# Test 2: Frontend Connectivity Tests
echo -e "${BOLD}${CYAN}"
echo "================================================================================"
echo "                    TEST 2: FRONTEND CONNECTIVITY ANALYSIS                     "
echo "================================================================================"
echo -e "${NC}"

python3 "$PROJECT_ROOT/tests/frontend_connectivity_test.py"
FRONTEND_TEST_RESULT=$?
echo ""

# Test 3: Quick API Smoke Tests
echo -e "${BOLD}${CYAN}"
echo "================================================================================"
echo "                          TEST 3: API SMOKE TESTS                              "
echo "================================================================================"
echo -e "${NC}"

if [ "$BACKEND_RUNNING" = true ]; then
    echo "Running quick API smoke tests..."
    echo ""
    
    # Test 1: Health check
    echo -n "1. Health Check... "
    if curl -s "$BACKEND_URL/health" | grep -q "ok"; then
        echo -e "${GREEN}✅ PASS${NC}"
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
    
    # Test 2: Root endpoint
    echo -n "2. Root Endpoint... "
    if curl -s "$BACKEND_URL/api" | grep -q "status"; then
        echo -e "${GREEN}✅ PASS${NC}"
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
    
    # Test 3: Login endpoint
    echo -n "3. Login Endpoint... "
    RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"screener@kamco.com","password":"Screener123"}')
    
    if echo "$RESPONSE" | grep -q "access_token"; then
        echo -e "${GREEN}✅ PASS${NC}"
        
        # Extract token for further tests
        TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
        
        if [ ! -z "$TOKEN" ]; then
            # Test 4: Authenticated endpoint
            echo -n "4. Authenticated Request (/auth/me)... "
            if curl -s -H "Authorization: Bearer $TOKEN" "$BACKEND_URL/api/auth/me" | grep -q "username"; then
                echo -e "${GREEN}✅ PASS${NC}"
            else
                echo -e "${RED}❌ FAIL${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
    
    echo ""
else
    echo -e "${YELLOW}⚠️  Skipping smoke tests - backend not running${NC}"
    echo ""
fi

# Test 4: File Structure Validation
echo -e "${BOLD}${CYAN}"
echo "================================================================================"
echo "                      TEST 4: FILE STRUCTURE VALIDATION                        "
echo "================================================================================"
echo -e "${NC}"

echo "Checking critical files..."
echo ""

check_file() {
    local file=$1
    local name=$2
    
    echo -n "$name... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ Exists${NC}"
        return 0
    else
        echo -e "${RED}❌ Missing${NC}"
        return 1
    fi
}

# Backend files
echo -e "${BOLD}Backend:${NC}"
check_file "$PROJECT_ROOT/backend/main.py" "  main.py"
check_file "$PROJECT_ROOT/backend/routes/auth.py" "  routes/auth.py"
check_file "$PROJECT_ROOT/backend/routes/upload.py" "  routes/upload.py"
check_file "$PROJECT_ROOT/backend/routes/screening.py" "  routes/screening.py"
check_file "$PROJECT_ROOT/backend/routes/review.py" "  routes/review.py"

echo ""

# Frontend files
echo -e "${BOLD}Frontend:${NC}"
check_file "$PROJECT_ROOT/frontend/src/App.tsx" "  App.tsx"
check_file "$PROJECT_ROOT/frontend/src/pages/Login.tsx" "  Login.tsx"
check_file "$PROJECT_ROOT/frontend/src/pages/screening/UploadPage.tsx" "  UploadPage.tsx"
check_file "$PROJECT_ROOT/frontend/src/pages/screening/ScreeningQueuePage.tsx" "  ScreeningQueuePage.tsx"
check_file "$PROJECT_ROOT/frontend/src/services/apiClient.ts" "  apiClient.ts"

echo ""

# Documentation files
echo -e "${BOLD}Documentation:${NC}"
check_file "$PROJECT_ROOT/BACKEND_TO_FRONTEND_TODO.md" "  Integration TODO"
check_file "$PROJECT_ROOT/BLACKLIST_FORMAT_REFERENCE.md" "  Format Reference"
check_file "$PROJECT_ROOT/SYSTEM_READY.md" "  System Ready Guide"

echo ""

# Generate Final Report
echo -e "${BOLD}${CYAN}"
echo "================================================================================"
echo "                              FINAL TEST REPORT                                "
echo "================================================================================"
echo -e "${NC}"

echo -e "${BOLD}Test Results:${NC}"
echo ""

if [ $BACKEND_TEST_RESULT -eq 0 ]; then
    echo -e "  Backend API Tests:     ${GREEN}✅ PASSED${NC}"
else
    echo -e "  Backend API Tests:     ${RED}❌ FAILED${NC}"
fi

if [ $FRONTEND_TEST_RESULT -eq 0 ]; then
    echo -e "  Frontend Connectivity: ${GREEN}✅ PASSED${NC}"
else
    echo -e "  Frontend Connectivity: ${YELLOW}⚠️  NEEDS WORK${NC}"
fi

echo ""
echo -e "${BOLD}Service Status:${NC}"
echo ""
echo -e "  Backend (http://127.0.0.1:8000):     $([ "$BACKEND_RUNNING" = true ] && echo -e "${GREEN}✅ Running${NC}" || echo -e "${RED}❌ Not Running${NC}")"
echo -e "  Frontend (http://localhost:3000):    $([ "$FRONTEND_RUNNING" = true ] && echo -e "${GREEN}✅ Running${NC}" || echo -e "${RED}❌ Not Running${NC}")"

echo ""
echo -e "${BOLD}Overall Assessment:${NC}"
echo ""

if [ $BACKEND_TEST_RESULT -eq 0 ] && [ $FRONTEND_TEST_RESULT -eq 0 ] && [ "$BACKEND_RUNNING" = true ] && [ "$FRONTEND_RUNNING" = true ]; then
    echo -e "${GREEN}${BOLD}🎉 ALL SYSTEMS GO!${NC}"
    echo -e "${GREEN}   Backend is operational and ready for frontend integration${NC}"
    EXIT_CODE=0
elif [ $BACKEND_TEST_RESULT -eq 0 ] && [ "$BACKEND_RUNNING" = true ]; then
    echo -e "${YELLOW}${BOLD}⚠️  PARTIALLY READY${NC}"
    echo -e "${YELLOW}   Backend is working but frontend integration incomplete${NC}"
    echo -e "${YELLOW}   Next steps: Connect frontend pages to backend APIs${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}${BOLD}❌ ATTENTION NEEDED${NC}"
    echo -e "${RED}   Some tests failed or services are not running${NC}"
    echo -e "${RED}   Please review the test output above${NC}"
    EXIT_CODE=1
fi

echo ""
echo -e "${BOLD}Next Steps:${NC}"
echo ""
echo "  1. Review BACKEND_TO_FRONTEND_TODO.md for integration tasks"
echo "  2. Connect UploadPage.tsx to POST /api/upload/blacklist"
echo "  3. Connect ScreeningQueuePage.tsx to GET /api/screening/queue"
echo "  4. Remove mock data from Review pages"
echo "  5. Connect Dashboard and Reports to backend endpoints"
echo ""
echo -e "${CYAN}📝 For detailed integration plan, see: BACKEND_TO_FRONTEND_TODO.md${NC}"
echo ""

# Save test report
REPORT_FILE="$PROJECT_ROOT/test-report-$(date '+%Y%m%d-%H%M%S').txt"
echo "Test report saved to: $REPORT_FILE"
echo ""

exit $EXIT_CODE
