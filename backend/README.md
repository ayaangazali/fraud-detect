# Kamco Compliance Screening - Backend

FastAPI backend for compliance screening with multi-sheet Excel parsing, fuzzy matching, and Actor field extraction.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python seed_database.py
```

This will create the database and populate it with sample data:
- 5 Clients (with Actor names)
- 4 Vendors (with Actor names)
- 5 Staff members
- 3 Tenants
- 3 Others

### 3. Run the Server

```bash
python main.py
```

Or use uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will run at: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
├── seed_database.py        # Database seeding script
├── database/
│   ├── connection.py       # Database connection & session
│   └── kamco.db           # SQLite database (created on first run)
├── models/
│   └── database.py         # SQLAlchemy models (7 tables)
├── routes/
│   ├── scan.py            # Scan endpoints (/upload, /run)
│   └── review.py          # Review endpoints (/queue, /flag, /approve, etc.)
└── utils/
    ├── excel_parser.py     # Multi-sheet Excel parsing
    ├── actor_extractor.py  # Actor field extraction (Clients/Vendors)
    ├── fuzzy_matcher.py    # Fuzzy matching algorithm
    └── logbook.py          # Logbook deduplication
```

## 🔗 API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Scan Operations
- `POST /api/scan/upload` - Upload blacklist Excel (preview only)
- `POST /api/scan/run` - Run full scan (parse, match, dedupe, queue)

### Review Operations
- `GET /api/review/queue` - Get items in review queue
- `POST /api/review/flag` - Flag an item
- `POST /api/review/undo` - Undo a flag
- `GET /api/review/flagged` - Get flagged items
- `POST /api/review/approve` - Checker approves flagged item
- `POST /api/review/recheck` - Checker requests re-check
- `POST /api/review/override` - Checker overrides flag

## 🗄️ Database Schema

### Kamco Tables (Pre-loaded)
1. **kamco_clients** - Client records with Actor field
2. **kamco_vendors** - Vendor records with Actor field
3. **kamco_staff** - Staff records (no Actor field)
4. **kamco_tenants** - Tenant records (no Actor field)
5. **kamco_others** - Other entities (no Actor field)

### Workflow Tables
6. **in_review_queue** - Items awaiting review
7. **flagged_items** - Flagged items (pending/approved/recheck/overridden)
8. **logbook** - Historical review decisions (deduplication)

## 📊 How It Works

### 1. Upload Blacklist
- User uploads Excel file with 5 sheets: Clients, Vendors, Staff, Tenants, Others
- Backend parses all sheets using `openpyxl`

### 2. Fuzzy Matching
- Each Kamco record is compared against blacklist names
- Uses `fuzzywuzzy` with token_sort_ratio
- Match threshold: 80% similarity
- Returns matches with scores

### 3. Actor Extraction (Clients/Vendors Only)
- Extracts Actor/Representative field from Clients and Vendors sheets
- Performs additional fuzzy matching on actor names
- Actor match threshold: 75%

### 4. Logbook Deduplication
- Checks if (kamco_name, blacklist_name) pair exists in logbook
- Skips previously reviewed matches
- Only new matches added to queue

### 5. Review Workflow
- **Screener**: Reviews queue, flags suspicious matches
- **Checker**: Reviews flagged items, can Approve/Recheck/Override
- **Approved**: Added to logbook as "flagged"
- **Overridden**: Added to logbook as "cleared"
- **Recheck**: Moved back to queue with notification

## 🔧 Configuration

Edit `.env` file:

```env
DATABASE_URL=sqlite:///./database/kamco.db
FRONTEND_URL=http://localhost:5173
```

## 📝 Example Request

### Run Scan

```bash
curl -X POST "http://localhost:8000/api/scan/run" \
  -F "file=@blacklist.xlsx"
```

Response:
```json
{
  "success": true,
  "message": "Scan completed. Found 12 new matches.",
  "stats": {
    "total_matches_found": 15,
    "new_matches_added": 12,
    "duplicates_skipped": 3
  }
}
```

## 🧪 Testing

1. **Seed Database**: `python seed_database.py`
2. **Start Server**: `python main.py`
3. **Open Docs**: http://localhost:8000/docs
4. **Test Upload**: Use Swagger UI to upload sample Excel file
5. **Run Scan**: Test `/api/scan/run` endpoint
6. **Check Queue**: GET `/api/review/queue`

## 🐛 Troubleshooting

### Import Errors
```bash
pip install --upgrade fuzzywuzzy python-Levenshtein openpyxl
```

### Database Issues
```bash
rm database/kamco.db
python seed_database.py
```

### CORS Issues
Check `.env` file - Frontend URL must match React dev server

## 🚦 Next Steps

1. ✅ Backend setup complete
2. ⏳ Wire frontend to backend
3. ⏳ Replace alert() with toast notifications
4. ⏳ Add loading states
5. ⏳ Email notifications for re-checks
6. ⏳ Report generation

---

**Ready to connect with frontend!** 🎉
