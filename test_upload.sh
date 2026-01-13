#!/bin/bash
# Quick Test Script for Kamco Upload System
# Tests the new /api/upload/kamco-entities endpoint

echo "=================================="
echo "🧪 KAMCO UPLOAD QUICK TEST"
echo "=================================="
echo ""

BASE_URL="http://127.0.0.1:8000"

echo "Step 1: Login as Screener..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"screener@kamco.com","password":"Screener123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed! Check credentials or backend."
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Login successful!"
echo ""

echo "Step 2: Upload sample CSV..."
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/upload/kamco-entities" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample-data/kamco_entities_sample.csv")

echo "$UPLOAD_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UPLOAD_RESPONSE"

SUCCESS=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)

if [ "$SUCCESS" = "True" ]; then
    echo ""
    echo "✅ Upload successful!"
    
    # Extract summary
    TOTAL=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['summary']['stored_entities'])" 2>/dev/null)
    CLIENTS=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['summary']['by_type']['clients'])" 2>/dev/null)
    VENDORS=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['summary']['by_type']['vendors'])" 2>/dev/null)
    STAFF=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['summary']['by_type']['staff'])" 2>/dev/null)
    OTHERS=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['summary']['by_type']['others'])" 2>/dev/null)
    
    echo ""
    echo "📊 Upload Summary:"
    echo "   Total entities: $TOTAL"
    echo "   - Clients: $CLIENTS"
    echo "   - Vendors: $VENDORS"
    echo "   - Staff: $STAFF"
    echo "   - Others: $OTHERS"
else
    echo ""
    echo "❌ Upload failed!"
fi

echo ""
echo "Step 3: Get summary..."
SUMMARY_RESPONSE=$(curl -s -X GET "$BASE_URL/api/upload/kamco-entities/summary" \
  -H "Authorization: Bearer $TOKEN")

echo "$SUMMARY_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SUMMARY_RESPONSE"

echo ""
echo "=================================="
echo "✅ TEST COMPLETE!"
echo "=================================="
echo ""
echo "🌐 View API docs: http://127.0.0.1:8000/docs"
echo "📊 Frontend: http://localhost:3001"
echo ""
