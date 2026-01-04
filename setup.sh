#!/bin/bash

# AML/KYC Name Screening - Updated Setup Script
# This script sets up the reorganized project structure

echo "🔍 AML/KYC Name Screening - Setup Script (Updated Structure)"
echo "============================================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✓ Node.js version: $(node --version)"
echo ""

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install root dependencies"
    exit 1
fi
echo "✓ Root dependencies installed"
echo ""

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install backend dependencies"
    exit 1
fi
cd ..
echo "✓ Backend dependencies installed"
echo ""

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi
cd ..
echo "✓ Frontend dependencies installed"
echo ""

echo "✅ Setup complete!"
echo ""
echo "📁 Project Structure:"
echo "   ├── frontend/   (React app on port 3000)"
echo "   ├── backend/    (API server on port 5000)"
echo "   ├── sample-data/ (Mock CSV files)"
echo "   └── docs/       (Documentation)"
echo ""
echo "🚀 To start the application, run:"
echo "   npm run dev"
echo ""
echo "📊 Test with Middle Eastern data:"
echo "   • sample-data/customers-middle-east.csv (50 customers)"
echo "   • sample-data/blacklist-middle-east.csv (40 sanctioned entities)"
echo ""
echo "📖 For more information, see:"
echo "   - README.md (main overview)"
echo "   - PROJECT-STRUCTURE.md (file organization)"
echo "   - docs/QUICKSTART.md (quick start guide)"
echo ""
