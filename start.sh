#!/bin/bash

# Kill any processes on ports 3000 and 5001
echo "🔧 Cleaning up ports..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

echo "✅ Ports cleared!"
echo ""
echo "🚀 Starting AML/KYC Application..."
echo ""
echo "Backend will run on: http://localhost:5001"
echo "Frontend will run on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start the application
npm run dev
