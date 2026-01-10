# 🔍 Kamco Compliance Screening System

> **Phase 9 Complete** - Advanced sanctions screening with comprehensive review workflows, bulk operations, email notifications, and detailed reporting.

A production-ready web application for AML/KYC compliance screening that identifies potential matches between internal Kamco entities (Clients, Vendors, Staff, Others) and blacklist/sanctions lists using fuzzy name matching and intelligent review workflows.

## 🎯 Project Overview

**Purpose**: Automated sanctions screening system that processes blacklist Excel files, identifies potential matches using fuzzy logic, and provides a comprehensive review workflow for compliance teams.

**Key Features**:
- 📊 **Excel Import** - Upload blacklist files with automatic parsing
- 🔎 **Fuzzy Matching** - 85% threshold with Arabic/English name support  
- 📋 **Review Workflows** - Three-tier review system (Screener → Checker → Finalizer)
- 📧 **Email Notifications** - Automated alerts for completed uploads and reviews
- 📑 **Bulk Operations** - Review multiple items simultaneously
- 📊 **Comprehensive Reports** - Item-level and cumulative decision reports
- 🔐 **Role-Based Access** - JWT authentication with role-specific permissions

**Architecture**:
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui (Port 5173)
- **Backend**: FastAPI + SQLAlchemy + SQLite (Port 8000)
- **Database**: SQLite with pre-loaded Kamco entities
- **Matching Engine**: RapidFuzz with token_sort_ratio algorithm

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (Frontend)
- Python 3.9+ (Backend)
- Modern web browser

### 1. Setup & Run Backend
```bash
cd backend
pip install -r requirements.txt
python3 main.py
```
Backend API: **http://localhost:8000**  
API Documentation: **http://localhost:8000/docs**

### 2. Setup & Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend UI: **http://localhost:5173**

### 3. Test Credentials
The system comes with pre-configured test users:

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| **Screener** | `screener_test` | `password123` | Initial screening, flag items |
| **Checker** | `checker_test` | `password123` | Review flags, approve/reject/escalate |
| **Finalizer** | `finalizer_test` | `password123` | Final approval authority |

### 4. Quick Test
1. Login as `checker_test` / `password123`
2. Navigate to **Screening Queue**
3. Upload test blacklist: `test_data/blacklist_with_matches.csv`
4. Click **"Run Screening"** - system auto-screens and flags matches
5. Review flagged items in the queue

## 📁 Project Structure

```
Kamco/
├── frontend/                           # React + TypeScript Application
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.tsx              # Authentication with role-based access
│   │   │   ├── Dashboard.tsx          # Main dashboard with stats
│   │   │   └── screening/
│   │   │       ├── ScreeningQueuePage.tsx  # Queue management & bulk review
│   │   │       └── ScreeningResultsPage.tsx # Historical results
│   │   ├── components/
│   │   │   ├── review/
│   │   │   │   ├── ReviewModal.tsx         # Single item review
│   │   │   │   ├── BulkReviewModal.tsx     # Bulk review operations
│   │   │   │   ├── EmailReportModal.tsx    # Email report generation
│   │   │   │   ├── ItemDetailReport.tsx    # Detailed item report
│   │   │   │   └── CumulativeReport.tsx    # Cumulative stats report
│   │   │   ├── dashboard/
│   │   │   │   └── StatsCards.tsx          # Statistics display
│   │   │   └── ui/                         # shadcn/ui components
│   │   ├── services/
│   │   │   ├── authService.ts              # Authentication API
│   │   │   └── api.ts                      # API client
│   │   └── AppRouter.tsx                   # Protected routes
│   └── package.json
│
├── backend/                            # FastAPI Application
│   ├── main.py                        # Application entry point
│   ├── requirements.txt               # Python dependencies
│   ├── database/
│   │   ├── connection.py              # SQLite connection & session
│   │   └── kamco.db                   # SQLite database
│   ├── models/
│   │   ├── database.py                # Kamco entity models (Client/Vendor/Staff/Other)
│   │   ├── blacklist.py               # Blacklist entry model
│   │   └── auth.py                    # User authentication models
│   ├── routes/
│   │   ├── auth.py                    # Authentication endpoints
│   │   ├── upload.py                  # File upload & parsing
│   │   ├── screening.py               # Screening & queue management
│   │   └── review_manager.py          # Review workflow endpoints
│   └── utils/
│       ├── auth.py                    # JWT & password utilities
│       ├── email_service.py           # Email notification system
│       ├── excel_parser.py            # Excel file parsing
│       └── fuzzy_matcher.py           # Fuzzy matching engine
│
├── test_data/                         # Test files
│   ├── kamco_all_entities.csv        # Sample Kamco entities (50+)
│   └── blacklist_with_matches.csv    # Sample blacklist with known matches
│
├── docs/                              # Documentation
│   ├── FRONTEND_REVIEW_SYSTEM.md     # Frontend component guide
│   ├── REVIEW_SYSTEM_GUIDE.md        # Complete review workflow guide
│   ├── IMPLEMENTATION_COMPLETE.md     # Technical implementation details
│   └── VISUAL_OVERVIEW.md            # Visual UI/UX guide
│
└── README.md                          # This file
```

## 📊 Database Schema

### Pre-loaded Kamco Entities (50+ records)
- **Clients** (10 records) - Investment clients with account numbers, actors, countries
- **Vendors** (10 records) - Service providers with vendor IDs, actors, categories
- **Staff** (15 records) - Employees with employee IDs, departments, positions
- **Others** (15 records) - Banks, auditors, legal firms, regulatory bodies

### Dynamic Tables
- **blacklist_entries** - Uploaded sanctions lists (Arabic + English names, Civil IDs, etc.)
- **flagged_items** - Items flagged for review (status: pending/approved/rejected/escalated)
- **logbook** - Complete audit trail of all screening decisions
- **users** - Authentication with role-based permissions

### Entity Fields

**KamcoClient**:
- name, account_number, date_opened, actor_name (representative), country, notes

**KamcoVendor**:
- name, vendor_id, date_registered, actor_name (agent), category, notes

**KamcoStaff**:
- name, employee_id, department, position, hire_date, notes

**KamcoOther**:
- name, category, reference_id, description, notes

**BlacklistEntry**:
- name_arabic, name_english, civil_id, passport_number, nationality, country
- entity_type, decree_number, list_date, source, category, risk_level, reason, notes

## 🎯 Key Features

### ✅ Automated Screening
- **Excel Import** - Flexible parsing supporting multiple formats (Arabic/English names, Civil IDs, etc.)
- **Fuzzy Matching** - 85% threshold using token_sort_ratio algorithm
- **Auto-Flagging** - Automatic flagging of matches upon blacklist upload
- **Duplicate Prevention** - Smart deduplication against historical logbook

### ✅ Review Workflows  
- **Single Review** - Review individual items with detailed comparison
- **Bulk Review** - Review multiple items simultaneously with batch operations
- **Three-Tier System** - Screener → Checker → Finalizer workflow
- **Decision Options** - Approve, Reject, Escalate, Request Recheck

### ✅ Reporting & Analytics
- **Item Detail Reports** - Individual item analysis with match details
- **Cumulative Reports** - Aggregate statistics across selected items
- **Email Notifications** - Automated alerts for upload completion and review actions
- **Export Functionality** - Generate and download detailed reports

### ✅ User Experience
- **Modern UI** - Clean, responsive interface with Tailwind CSS + shadcn/ui
- **Real-time Updates** - Instant feedback on all actions
- **Protected Routes** - JWT-based authentication with automatic token refresh
- **Role-Based Access** - Different permissions for Screeners, Checkers, Finalizers

### ✅ Technical Excellence
- **Type Safety** - Full TypeScript implementation on frontend
- **API Documentation** - Auto-generated Swagger/OpenAPI docs at `/docs`
- **Error Handling** - Comprehensive error handling with user-friendly messages
- **Audit Trail** - Complete logbook of all screening decisions

## 🔗 API Endpoints

### Authentication
```
POST /api/auth/login              # User login (returns JWT tokens)
POST /api/auth/refresh            # Refresh access token
POST /api/auth/logout             # User logout
GET  /api/auth/me                 # Get current user info
```

### File Upload & Screening
```
POST /api/upload/entities         # Upload Kamco entities CSV
POST /api/upload/blacklist        # Upload blacklist (auto-screens)
GET  /api/upload/history          # Upload history
```

### Screening & Queue Management  
```
GET  /api/screening/queue         # Get pending flagged items
GET  /api/screening/results       # Get historical screening results
POST /api/screening/run           # Manual screening run
GET  /api/screening/stats         # Get screening statistics
```

### Review Management
```
POST /api/review/single           # Review single item
POST /api/review/bulk             # Bulk review multiple items
POST /api/review/escalate         # Escalate item to higher authority
POST /api/review/recheck          # Request recheck
GET  /api/review/history          # Get review history
POST /api/review/email-report     # Generate & email report
GET  /api/review/item-report/:id  # Get detailed item report
POST /api/review/cumulative-report # Get cumulative statistics
```

### System
```
GET  /                           # Root endpoint
GET  /health                     # Health check
GET  /docs                       # Interactive API documentation (Swagger UI)
```

## 🧪 Testing Guide

### 1. Start the System
```bash
# Terminal 1 - Backend
cd backend
python3 main.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### 2. Login
- Navigate to **http://localhost:5173**
- Login with: `checker_test` / `password123`
- You'll see the Dashboard with system statistics

### 3. Upload Test Blacklist
- Go to **Screening Queue** page
- Click **"Upload Blacklist"**
- Select: `test_data/blacklist_with_matches.csv`
- System automatically:
  - Parses the file
  - Runs fuzzy matching against all Kamco entities
  - Flags matches (85%+ similarity)
  - Sends email notification (logged to file)

### 4. Review Flagged Items

**Single Review**:
- Click **"Review"** on any flagged item
- See match details, scores, and severity
- Add notes and select decision: Approve/Reject/Escalate
- Click **"Submit Decision"**

**Bulk Review**:
- Select multiple items using checkboxes
- Click **"Bulk Review"**
- Apply same decision to all selected items
- Saves time for obvious matches/non-matches

### 5. Generate Reports

**Item Detail Report**:
- Click **"View Report"** on any item
- See comprehensive analysis:
  - Match details and scores
  - Kamco entity information  
  - Blacklist entry details
  - Decision history

**Cumulative Report**:
- Select multiple items
- Click **"Generate Report"**
- View aggregate statistics:
  - Total items reviewed
  - Approval/Rejection breakdown
  - Average match scores
  - Entity type distribution

**Email Reports**:
- Click **"Email Report"**
- Select report type (Item/Cumulative)
- Enter recipient email
- System generates and emails report (logged to file in test mode)

### 6. Test Different Roles

**Screener** (`screener_test` / `password123`):
- Can view queue and flag items
- Cannot make final decisions

**Checker** (`checker_test` / `password123`):
- Can review and approve/reject items
- Can escalate complex cases
- Full access to reports

**Finalizer** (`finalizer_test` / `password123`):
- Final approval authority
- Can override checker decisions
- Access to all historical data

## 💡 How It Works

### Screening Flow
```
1. Upload Blacklist CSV
   ↓
2. Parse File (Extract: Name Arabic, Name English, Civil ID, Nationality, etc.)
   ↓
3. For Each Kamco Entity (Clients, Vendors, Staff, Others):
   ├─ Compare Name vs Blacklist Names (85% threshold)
   ├─ Compare Actor Name (for Clients/Vendors) vs Blacklist Names
   └─ Calculate Match Score (0-100)
   ↓
4. Flag High Matches (≥85% similarity)
   ├─ Check Logbook (skip if already reviewed)
   ├─ Assign Severity (HIGH/MEDIUM/LOW based on score)
   └─ Create Flagged Item
   ↓
5. Queue for Review
   ↓
6. Send Email Notification
```

### Fuzzy Matching Algorithm
```python
from rapidfuzz import fuzz

# Token Sort Ratio (handles word order variations)
score = fuzz.token_sort_ratio("Mohammed Al-Rashid", "Muhammad Al-Rasheed")
# Result: 92% → FLAGGED (above 85% threshold)

# Examples:
"Omar Abdullah" vs "Omar Bin Abdullah"      → 87% ✅
"Ahmed Hassan" vs "Ahmad Hasan"             → 91% ✅  
"Fatima Ali" vs "John Smith"                → 25% ❌
```

### Match Severity Levels
- **HIGH** (95-100%): Almost exact match - requires immediate review
- **MEDIUM** (90-94%): Strong match - likely positive
- **LOW** (85-89%): Possible match - needs careful review

### Review Workflow
```
┌─────────────┐
│  Screener   │ Flags items, adds initial notes
└──────┬──────┘
       ↓
┌──────────────┐
│   Checker    │ Reviews flags, makes decisions:
└──────┬───────┘  - APPROVE → Confirmed match → Logbook
       │          - REJECT → False positive → Logbook
       │          - ESCALATE → Complex case → Finalizer
       │          - RECHECK → Needs more review → Back to Queue
       ↓
┌──────────────┐
│  Finalizer   │ Final authority, can override any decision
└──────────────┘
       ↓
    Logbook (Permanent audit trail)
```

### Deduplication Logic
The system prevents duplicate reviews by checking the logbook:

```python
# Before flagging, check if this pair was already reviewed
existing = logbook.query(
    kamco_name == "Mohammed Al-Rashid" AND
    blacklist_name == "Muhammad Al-Rasheed"
)

if existing:
    skip  # Already reviewed - don't create duplicate flag
else:
    create_flag()  # New match - add to queue
```
## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[REVIEW_SYSTEM_GUIDE.md](docs/REVIEW_SYSTEM_GUIDE.md)** - Complete guide to the review workflow system
- **[FRONTEND_REVIEW_SYSTEM.md](docs/FRONTEND_REVIEW_SYSTEM.md)** - Frontend components and UI patterns
- **[IMPLEMENTATION_COMPLETE.md](docs/IMPLEMENTATION_COMPLETE.md)** - Technical implementation details
- **[VISUAL_OVERVIEW.md](docs/VISUAL_OVERVIEW.md)** - Visual guide to the user interface
- **[REVIEW_QUICK_START.md](docs/REVIEW_QUICK_START.md)** - Quick start guide for reviewers

## 🔐 Security & Compliance

### Authentication & Authorization
- **JWT Tokens**: Access tokens (15 min) + Refresh tokens (7 days)
- **Password Hashing**: bcrypt with salt
- **Role-Based Access Control**: Three-tier permission system
- **Protected Routes**: Frontend route guards + backend middleware

### Data Security
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Input Validation**: Pydantic models for request validation
- **CORS Protection**: Configured allowed origins
- **Audit Trail**: Complete logbook of all actions

### Compliance Features
- **AML/KYC Screening**: Sanctions list matching
- **Duplicate Prevention**: Automatic deduplication
- **Decision Tracking**: Full audit trail with timestamps
- **Email Notifications**: Automated alerts for compliance team
- **Comprehensive Reports**: Detailed match analysis and statistics

## 🌍 Middle East Optimization

### Arabic Language Support
- **Bidirectional Names**: Supports both Arabic and English names
- **Transliteration Handling**: Accounts for different English spellings of Arabic names
- **Civil ID Support**: Kuwait Civil ID format (12 digits)
- **Regional Names**: Optimized for Gulf region naming patterns

### Cultural Considerations
- **Name Variations**: Handles "Al-", "Bin", "Bint" prefixes
- **Family Names**: Supports multi-part family names
- **Honorifics**: Handles Sheikh, Dr., Eng., etc.
- **Company Names**: Arabic and English company name matching

## ⚙️ Configuration

### Backend Configuration (`backend/main.py`)
```python
# JWT Settings
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Fuzzy Matching
MATCH_THRESHOLD = 85  # Minimum similarity score (0-100)

# Email Settings (configure in .env)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
```

### Frontend Configuration (`frontend/src/services/api.ts`)
```typescript
// API Base URL
const API_BASE_URL = 'http://localhost:8000'

// Request Timeout
const REQUEST_TIMEOUT = 30000  // 30 seconds
```

## 🛠️ Available Commands

### Backend
```bash
cd backend
python3 main.py                    # Start development server
python3 -m pytest                  # Run tests (if configured)
python3 test_login.py              # Test authentication
python3 test_review_system.py     # Test review workflows
```

### Frontend
```bash
cd frontend
npm run dev                        # Start development server (port 5173)
npm run build                      # Build for production
npm run preview                    # Preview production build
npm run lint                       # Run ESLint
npm run type-check                 # TypeScript type checking
```

## ⚠️ Important Notes

1. **Test Data**: The system includes realistic test data for demonstration purposes
2. **Email Notifications**: In test mode, emails are logged to `backend/emails/` folder instead of being sent
3. **Database**: Uses SQLite - for production, consider PostgreSQL or MySQL
4. **Passwords**: Test passwords are simple for demo purposes - use strong passwords in production
5. **HTTPS**: Enable HTTPS in production environments
6. **File Size Limits**: Default upload limit is 10MB - adjust in backend if needed

## 📈 Performance

### Optimizations
- **Batch Processing**: Bulk operations reduce API calls
- **Database Indexing**: Indexed fields for fast queries
- **Lazy Loading**: Load data on demand in frontend
- **Caching**: Token caching reduces authentication overhead

### Scalability Considerations
- **Database**: Consider upgrading to PostgreSQL for high volume
- **File Storage**: Move uploads to S3/cloud storage for production
- **Caching Layer**: Add Redis for improved performance
- **Load Balancing**: Use Nginx or similar for multiple backend instances

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check if port 8000 is already in use
lsof -i :8000
# Kill the process if needed
kill -9 <PID>
```

**Frontend can't connect to backend:**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify API_BASE_URL in frontend

**Login fails:**
- Check that test users exist in database
- Verify password is correct: `password123`
- Check JWT secret key configuration

**Fuzzy matching too sensitive:**
- Adjust MATCH_THRESHOLD in `backend/utils/fuzzy_matcher.py`
- Higher threshold = fewer false positives
- Lower threshold = fewer missed matches

## 📞 Support & Contributing

For questions, issues, or contributions:
1. Check the documentation in `docs/` folder
2. Review the API documentation at `/docs` endpoint
3. Check the logbook for audit trails
4. Review email logs in `backend/emails/` folder

## 🎉 What's New in Phase 9

✨ **Major Features Added**:
- ✅ Comprehensive review workflow system (Single + Bulk)
- ✅ Email notification system with report generation
- ✅ Item detail and cumulative reports
- ✅ Enhanced UI with shadcn/ui components
- ✅ Improved role-based access control
- ✅ Complete audit trail in logbook
- ✅ Automatic screening on blacklist upload
- ✅ Advanced statistics and analytics
- ✅ Comprehensive documentation (5 guides!)

## 🚀 Ready to Use!

```bash
# Start both services
# Terminal 1
cd backend && python3 main.py

# Terminal 2  
cd frontend && npm run dev
```

Then open: **http://localhost:5173**

Login with: `checker_test` / `password123`

---

**Built for AML/KYC compliance screening in the Middle East region** 🔍✨

*Phase 9 Complete - January 2026*
Thank you
