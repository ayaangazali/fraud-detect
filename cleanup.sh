#!/bin/bash

# Kamco Project Cleanup Script
# This script removes temporary development files while preserving production code

echo "🧹 Starting Kamco Project Cleanup..."
echo "This will remove temporary documentation and test files."
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
removed_count=0

# Function to remove file safely
remove_file() {
    if [ -f "$1" ]; then
        rm "$1"
        echo -e "${GREEN}✓${NC} Removed: $1"
        ((removed_count++))
    fi
}

# Function to remove directory safely
remove_dir() {
    if [ -d "$1" ]; then
        rm -rf "$1"
        echo -e "${GREEN}✓${NC} Removed directory: $1"
        ((removed_count++))
    fi
}

echo "📁 Cleaning root directory..."
# Remove temporary documentation files from root
remove_file "403_ERROR_FIXED.md"
remove_file "ALL_PHASES_COMPLETE.md"
remove_file "ALL_TESTS_PASSING.md"
remove_file "AUTO_SCREENING_TEST_RESULTS.md"
remove_file "AUTO_SCREENING_WORKING.md"
remove_file "BACKEND_TO_FRONTEND_TODO.md"
remove_file "BLACKLIST_FORMAT_REFERENCE.md"
remove_file "BULK_REVIEW_STATUS.md"
remove_file "BULK_REVIEW_WIZARD_COMPLETE.md"
remove_file "CHANGES_SUMMARY.md"
remove_file "COMPLETE_FEATURES.txt"
remove_file "COMPLETION_CHECKLIST.md"
remove_file "CRITICAL_FIXES.md"
remove_file "DATABASE_STATUS.md"
remove_file "ENV_SETUP.md"
remove_file "FILES_CHANGED.md"
remove_file "FINAL_COMPLETION_SUMMARY.md"
remove_file "FINAL_FIXES.md"
remove_file "FINAL_STATUS.md"
remove_file "FINAL_ULTRA_FLEXIBLE_SUMMARY.md"
remove_file "FIXES_COMPLETE.md"
remove_file "FIX_403_ERROR.md"
remove_file "FIX_SUMMARY.md"
remove_file "FRONTEND_REVIEW_SYSTEM.md"
remove_file "GIT_COMMIT_MESSAGE.md"
remove_file "IMPLEMENTATION_COMPLETE.md"
remove_file "INTEGRATION_COMPLETE.md"
remove_file "LOGBOOK_FIX.md"
remove_file "ORGANIZATION_COMPLETE.md"
remove_file "PARSER_TESTING_RESULTS.md"
remove_file "PHASE10_COMPLETE.md"
remove_file "PHASE2_FINAL_SUMMARY.md"
remove_file "PHASE9_COMPLETE_FIXES.md"
remove_file "QUICK_FIX_SUMMARY.md"
remove_file "QUICK_START.txt"
remove_file "QUICK_START_TEST.md"
remove_file "REVIEW_QUICK_START.md"
remove_file "REVIEW_SYSTEM_GUIDE.md"
remove_file "SAMPLE_DATA_COMPLETE.md"
remove_file "SAMPLE_DATA_GUIDE.md"
remove_file "SCREENER_CHECKER_FIX.md"
remove_file "SCREENING_FIX_COMPLETE.md"
remove_file "SCREENING_QUEUE_FIX.md"
remove_file "SIDE_BY_SIDE_COMPARISON.md"
remove_file "SYSTEM_READY.md"
remove_file "SYSTEM_STATUS.txt"
remove_file "TESTING_GUIDE.md"
remove_file "TEST_RESULTS_SUMMARY.md"
remove_file "TROUBLESHOOTING_403.md"
remove_file "UI_FIXES_COMPLETE.txt"
remove_file "UI_TEXT_FIXED.txt"
remove_file "ULTRA_FLEXIBLE_PARSER.md"
remove_file "UPLOAD_ERROR_FIXED.md"
remove_file "UPLOAD_FIX_COMPLETE.md"
remove_file "UPLOAD_FRONTEND_FIX.md"
remove_file "UPLOAD_SYSTEM_FIXED.md"
remove_file "V2_FIXED_SUMMARY.txt"
remove_file "V2_UPLOAD_FIXED.txt"
remove_file "VISUAL_OVERVIEW.md"
remove_file "WHAT_TO_UPLOAD.md"
remove_file "WHY_403_FORBIDDEN.md"

# Remove test scripts from root
remove_file "run_tests.sh"
remove_file "test_phase9.sh"
remove_file "test_upload.sh"

# Remove root-level node_modules (if frontend has its own)
remove_dir "node_modules"
remove_file "package.json"
remove_file "package-lock.json"

# Remove root-level tests directory if exists
remove_dir "tests"

echo ""
echo "📁 Cleaning backend directory..."
cd backend

# Remove temporary backend documentation
remove_file "AUTH_COMPLETE.md"
remove_file "AUTH_README.md"
remove_file "PHASE1_COMPLETE.md"
remove_file "PHASE2_COMPLETE.md"
remove_file "PHASE3_GUIDE.md"
remove_file "PHASE4_COMPLETE.md"
remove_file "PHASE5_COMPLETE.md"
remove_file "PHASE6_COMPLETE.md"
remove_file "PHASE7_COMPLETE.md"
remove_file "PHASE8_COMPLETE.md"
remove_file "PHASE8_VERIFICATION_REPORT.md"
remove_file "TEST_CHECKLIST.md"
remove_file "TEST_RESULTS.md"

# Remove test scripts and test databases
remove_file "test_auth_fix.py"
remove_file "test_auth_phase1.py"
remove_file "test_blacklist.json"
remove_file "test_blacklist.xml"
remove_file "test_blacklist_for_matching.xlsx"
remove_file "test_comprehensive.db"
remove_file "test_login.py"
remove_file "test_matching_upload.py"
remove_file "test_phase4.py"
remove_file "test_phase5.py"
remove_file "test_phase5_old.py"
remove_file "test_phase6.py"
remove_file "test_phase7.py"
remove_file "test_phase8.py"
remove_file "test_queue.py"
remove_file "test_review_system.py"
remove_file "test_rollback.py"
remove_file "test_screening_v2.db"
remove_file "test_upload_api.py"
remove_file "test_upload_auth.py"
remove_file "test_upload_complete.py"
remove_file "test_workflow_phase3.py"
remove_file "verify_phase8.py"

# Remove unnecessary backend files
remove_file "backup_database.py"
remove_file "check_database.py"
remove_file "jest.config.js"
remove_file "package.json"
remove_file "tsconfig.json"
remove_dir "node_modules"
remove_dir "dist"
remove_dir "src"

# Remove old venv (keep .venv)
remove_dir "venv"

# Clean up logs and cache
remove_file "backend.log"
remove_dir ".pytest_cache"
remove_dir "__pycache__"

cd ..

echo ""
echo "📁 Cleaning frontend directory..."
cd frontend

# Remove temporary frontend documentation
remove_file "ARCHITECTURE.md"
remove_file "PHASE9_COMPLETE.md"
remove_file "PHASE9_PROGRESS.md"

# Remove build artifacts (will be regenerated)
remove_dir "dist"

cd ..

echo ""
echo "📁 Creating project documentation..."

# Create a proper .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
.cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# Test
.pytest_cache/
.coverage
htmlcov/
.tox/

# Backend specific
backend/database/kamco.db
backend/logs/
backend/.pytest_cache/

# Frontend specific
frontend/dist/
frontend/.vite/
EOF
    echo -e "${GREEN}✓${NC} Created .gitignore"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ Cleanup Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "📊 Summary:"
echo -e "  ${GREEN}✓${NC} Removed $removed_count temporary files/directories"
echo -e "  ${GREEN}✓${NC} Preserved all production code"
echo -e "  ${GREEN}✓${NC} Preserved test suite in backend/tests/"
echo -e "  ${GREEN}✓${NC} Preserved documentation files:"
echo -e "     - README.md (main)"
echo -e "     - CREDENTIALS.md"
echo -e "     - BACKEND_DEPLOYMENT.md"
echo -e "     - QUICK_START.md"
echo -e "     - backend/AUTH_SECURITY_GUIDE.md"
echo -e "     - backend/tests/README.md"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "  1. Review changes: git status"
echo "  2. Test the application: ./start.sh"
echo "  3. Run tests: cd backend && pytest tests/ -v"
echo "  4. Commit cleaned code: git add . && git commit -m 'chore: Clean up temporary files'"
echo "  5. Push to GitHub: git push origin main"
echo ""
echo -e "${GREEN}✅ Your project is now clean and production-ready!${NC}"
