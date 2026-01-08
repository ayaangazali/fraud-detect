#!/bin/bash

# KAMCO Phase 9 - Comprehensive Test Script
# Tests all critical functionality after admin role removal

echo "🧪 KAMCO Phase 9 - Comprehensive Testing"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test API endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="$3"
    local data="$4"
    
    echo -n "Testing $name... "
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -X POST "$url" -H "Content-Type: application/json" -d "$data" -w "\n%{http_code}")
    else
        response=$(curl -s "$url" -w "\n%{http_code}")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code)"
        echo "   Response: $body"
        ((FAILED++))
        return 1
    fi
}

echo "📡 Testing Backend Connectivity"
echo "--------------------------------"

# Test health endpoint
test_endpoint "Health Check" "http://localhost:8000/health" "GET"

echo ""
echo "🔐 Testing Authentication"
echo "-------------------------"

# Test screener login
SCREENER_DATA='{"username": "screener", "password": "screener123"}'
test_endpoint "Screener Login" "http://localhost:8000/api/auth/login" "POST" "$SCREENER_DATA"

# Test checker login
CHECKER_DATA='{"username": "checker", "password": "checker123"}'
test_endpoint "Checker Login" "http://localhost:8000/api/auth/login" "POST" "$CHECKER_DATA"

# Test finalizer login
FINALIZER_DATA='{"username": "finalizer", "password": "finalizer123"}'
test_endpoint "Finalizer Login" "http://localhost:8000/api/auth/login" "POST" "$FINALIZER_DATA"

# Test admin login should fail or not exist
echo -n "Testing Admin Login (should fail)... "
ADMIN_DATA='{"username": "admin", "password": "admin123"}'
response=$(curl -s -X POST "http://localhost:8000/api/auth/login" -H "Content-Type: application/json" -d "$ADMIN_DATA" -w "\n%{http_code}")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "401" ] || [ "$http_code" = "404" ]; then
    echo -e "${GREEN}✅ PASS${NC} (Correctly rejected - HTTP $http_code)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (Admin should not exist - HTTP $http_code)"
    ((FAILED++))
fi

echo ""
echo "🌐 Testing Frontend"
echo "-------------------"

# Test frontend is accessible
echo -n "Testing Frontend Accessibility... "
frontend_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$frontend_response" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC} (HTTP $frontend_response)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (HTTP $frontend_response)"
    ((FAILED++))
fi

echo ""
echo "📊 Testing Frontend Build"
echo "-------------------------"

cd /Users/ayaangazali/Documents/hackathons/Kamco/frontend
echo -n "Building frontend... "
BUILD_OUTPUT=$(npm run build 2>&1)
if echo "$BUILD_OUTPUT" | grep -q "build complete"; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC}"
    echo "$BUILD_OUTPUT" | tail -20
    ((FAILED++))
fi

echo ""
echo "🔍 Verifying Admin Role Removal"
echo "--------------------------------"

cd /Users/ayaangazali/Documents/hackathons/Kamco/frontend/src
echo -n "Checking for 'admin' in role arrays... "
ADMIN_COUNT=$(grep -r "'\admin'" . --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l | tr -d ' ')
if [ "$ADMIN_COUNT" = "0" ]; then
    echo -e "${GREEN}✅ PASS${NC} (0 occurrences found)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} ($ADMIN_COUNT occurrences found)"
    grep -r "'admin'" . --include="*.tsx" --include="*.ts" 2>/dev/null | head -5
    ((FAILED++))
fi

echo ""
echo "📝 Test Summary"
echo "==============="
TOTAL=$((PASSED + FAILED))
echo "Total Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo "✅ Frontend is running at: http://localhost:3000"
    echo "✅ Backend is running at: http://localhost:8000"
    echo ""
    echo "Test credentials:"
    echo "  Screener: screener / screener123"
    echo "  Checker: checker / checker123"
    echo "  Finalizer: finalizer / finalizer123"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  Some tests failed. Please review the errors above.${NC}"
    exit 1
fi
