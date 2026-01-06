#!/bin/bash
echo "🚀 Starting Kamco Compliance Screening System..."
echo ""
echo "🧹 Cleaning up old processes..."
pkill -f "python3.*main.py" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
lsof -ti :5173 | xargs kill -9 2>/dev/null || true
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
sleep 2
echo "✅ Ready to start"
echo ""
echo "Starting Backend on port 8000..."
cd /Users/ayaangazali/Documents/hackathons/Kamco/backend
python3 main.py &
sleep 3
echo ""
echo "Starting Frontend on port 5173..."
cd /Users/ayaangazali/Documents/hackathons/Kamco/frontend
npm run dev
