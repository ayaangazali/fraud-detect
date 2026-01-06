# Kamco Compliance Screening System

A comprehensive web application for compliance screening combining multi-sheet Excel parsing, fuzzy name matching, and intelligent review workflows.

## 🎯 Project Overview

**Purpose**: Screen blacklist Excel files against pre-loaded Kamco database (Clients, Vendors, Staff, Tenants, Others) to identify potential compliance violations.

**Architecture**:
- **Frontend**: React 18 + TypeScript + Vite (Port 5173)
- **Backend**: FastAPI + SQLite (Port 8000)
- **Database**: SQLite with 8 tables (Kamco data pre-loaded)
- **Matching**: Fuzzy matching with Actor field extraction (Clients/Vendors only)

## 🚀 Quick Start

### 1. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: **http://localhost:5173**

**Test Credentials**:
- Screener: `screener` / `screener123`
- Checker: `checker` / `checker123`
- Finalizer: `finalizer` / `finalizer123`

### 2. Setup Backend
```bash
cd backend
pip install -r requirements.txt
python3 seed_database.py
python3 main.py
```
Backend runs at: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

## 📁 Project Structure

```
Kamco/
├── frontend/                    # React application (Port 5173)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.tsx       # 3 roles: screener, checker, finalizer
│   │   │   └── Dashboard.tsx   # 6 tabs: All/Clients/Vendors/Staff/Tenants/Others
│   │   ├── components/
│   │   │   ├── Dashboard/      # FileUpload, InReviewQueue, FlaggedItems, StatsCards, CheckerReview
│   │   │   ├── Modals/         # FlagModal, UndoModal
│   │   │   ├── Toast/          # Toast notifications (4 types)
│   │   │   └── Archive/        # Old unused components
│   │   ├── hooks/              # useToast custom hook
│   │   ├── services/           # API client
│   │   └── AppRouter.tsx       # Route protection
│   └── package.json
│
├── backend/                     # FastAPI application (Port 8000)
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt        # Python dependencies
│   ├── seed_database.py        # Database seeding (20 pre-loaded records)
│   ├── database/
│   │   ├── connection.py       # SQLite connection & session
│   │   └── kamco.db           # SQLite database
│   ├── models/
│   │   └── database.py         # SQLAlchemy models (8 tables)
│   ├── routes/
│   │   ├── scan.py            # POST /api/scan/* endpoints
│   │   └── review.py          # POST /api/review/* endpoints
│   └── utils/
│       ├── excel_parser.py    # Multi-sheet Excel parsing
│       ├── actor_extractor.py # Actor field extraction (Clients/Vendors)
│       ├── fuzzy_matcher.py   # Fuzzy matching (rapidfuzz)
│       └── logbook.py         # Deduplication logic
│
├── sample-data/               # Test Excel files
│   └── sample-blacklist.xlsx  # Sample blacklist with 5 sheets
│
├── docs/
│   └── old/                   # Archived documentation
│
└── README.md                  # This file
```

## 📊 Database

### Pre-loaded Kamco Data (20 records)
- **Clients** (5) - With Actor field (Representative)
- **Vendors** (4) - With Actor field (Agent)
- **Staff** (5) - No actor field
- **Tenants** (3) - No actor field
- **Others** (3) - No actor field

### Workflow Tables
- **in_review_queue** - Pending matches
- **flagged_items** - Flagged items (pending/approved/recheck/overridden)
- **logbook** - Historical decisions (prevents duplicate reviews)

## 🎯 Features

✅ **Multi-sheet Excel Parsing** - Reads 5 sheets (Clients, Vendors, Staff, Tenants, Others)
✅ **Fuzzy Matching** - 80% threshold, token_sort_ratio (rapidfuzz)
✅ **Actor Extraction** - Smart extraction from Clients/Vendors only
✅ **Logbook Deduplication** - Prevents duplicate reviews
✅ **Role-based Workflows** - Screener → Checker → Finalizer
✅ **Flag with Reason** - Minimum 10 characters
✅ **Undo with Validation** - 2-step confirmation (checkbox + text)
✅ **Toast Notifications** - Success, error, warning, info
✅ **Protected Routes** - Token-based authentication
✅ **Responsive Design** - Mobile-friendly UI

## 🔗 API Endpoints

### Health
```
GET /                    # Root
GET /health             # Health check
```

### Scan
```
POST /api/scan/upload   # Upload blacklist (preview)
POST /api/scan/run      # Run full scan (parse → match → dedupe → queue)
```

### Review
```
GET  /api/review/queue       # Get items in review queue
POST /api/review/flag        # Flag an item with reason
POST /api/review/undo        # Undo a flag
GET  /api/review/flagged     # Get flagged items
POST /api/review/approve     # Checker approves flag
POST /api/review/recheck     # Checker requests re-check
POST /api/review/override    # Checker overrides flag
```

## 🧪 Testing

### 1. Start Backend
```bash
cd backend
python3 main.py
# Runs at http://localhost:8000
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
# Runs at http://localhost:5173
```

### 3. Login
- URL: http://localhost:5173
- Credentials: `screener/screener123`

### 4. Upload Test File
- Create Excel with 5 sheets (Clients, Vendors, Staff, Tenants, Others)
- Each sheet has "Name" column with test names
- Upload and click "Run Scan"
- View matches in "In Review Queue"

### 5. Test Workflows
- **Flag**: Flag item with reason → Appears in "Flagged Items"
- **Undo**: Undo flagged item (2-step confirmation)
- **Checker**: Login as `checker/checker123` → Review flagged items
- **Actions**: Approve (→ Logbook), Recheck (→ Queue), Override (→ Logbook)

## 💡 How It Works

### Scanning Flow
1. **Upload** blacklist Excel with 5 sheets
2. **Parse** each sheet and extract Name field
3. **Match** each Kamco record against blacklist (80% threshold)
4. **Extract Actor** for Clients/Vendors (75% threshold)
5. **Deduplicate** against logbook (skip already reviewed)
6. **Queue** new matches for review

### Matching Example
```
Kamco: "Mohammed Al-Rashid" (Client)
Actor: "Ahmed Hassan"
Blacklist: "Muhammad Al-Rasheed", "Ahmed Hasan"

Results:
- Name match: 92% ✅ (above 80%) → Added to queue
- Actor match: 87% ✅ (above 75%) → Added to queue
```

### Review Workflow
```
Screener → Flags item
    ↓
Checker → Reviews (3 options)
    ├→ Approve → Logbook (flagged)
    ├→ Recheck → Back to queue
    └→ Override → Logbook (cleared)
    ↓
Finalizer → Reviews final decisions
```
   - Click "Run Screening"
   - ✅ Should find matches (e.g., "Omar Abdullah Bin Laden")

4. **Export Results**
   - Review matches
   - Click "Export to Excel"
   - ✅ Downloads formatted report

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/customers` | POST | Upload customer file |
| `/api/upload/blacklist` | POST | Upload blacklist file |
| `/api/screen` | POST | Run fuzzy matching |
| `/api/export` | POST | Generate Excel report |
| `/api/health` | GET | Health check |

## 🛠️ Available Commands

```bash
npm run dev              # Start both frontend + backend
npm run dev:frontend     # Start frontend only (port 3000)
npm run dev:backend      # Start backend only (port 5000)
npm test                 # Run all tests
npm run build            # Build for production
```

## 📚 Documentation

- **docs/README.md** - Complete documentation
- **docs/QUICKSTART.md** - 3-minute setup guide
- **docs/IMPLEMENTATION.md** - Technical details

## 🔐 Security & Compliance

This system is designed for AML/KYC compliance with:
- Name normalization for Arabic and English names
- Multi-alias matching
- Configurable risk thresholds
- Comprehensive audit trails via Excel export

## 🌍 Middle East Optimization

- **Arabic Name Support** - Handles Arabic transliterations
- **Regional Demographics** - Gulf countries focus
- **Local Regulations** - Compliant with GCC standards
- **Realistic Data** - Based on actual naming patterns

## ⚠️ Important Notes

1. **Blacklist Data**: Contains real names of sanctioned individuals for demonstration
2. **Customer Data**: Fictional but realistic Middle Eastern names
3. **One Match Alert**: Customer C018 "Omar Abdullah Bin Laden" will match blacklist entry "Omar Bin Laden"
4. **Fuzzy Matching**: Adjust threshold based on false positive tolerance

## 📞 Support

For issues or questions:
1. Check `docs/QUICKSTART.md` for common issues
2. Review `docs/README.md` for detailed documentation
3. Run tests: `cd backend && npm test`

## 🎉 Ready to Use!

```bash
npm run dev
```

Then open: **http://localhost:3000**

---

**Built for AML/KYC compliance in the Middle East region** 🔍✨
