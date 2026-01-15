# Kamco Fraud Detection System



A compliance screening tool that checks if your clients, vendors, or staff appear on any sanctions or blacklists.

---

## What This Software Does

Financial institutions need to screen people against government blacklists to prevent money laundering and fraud. This system automates that process.

You upload a blacklist file, and the system automatically compares every name against your database of clients, vendors, and staff. When it finds a potential match, it flags it for human review.

The matching is smart - it catches variations like "Mohammed" vs "Muhammad" or "Al-Rashid" vs "Al-Rasheed" that would be missed by exact matching.

---

## How to Run It

**What you need installed:**
- Python 3.13 or higher
- Node.js 20 or higher

**Step 1 - Get the code:**
```bash
git clone https://github.com/ayaangazali/fraud-detect.git
cd fraud-detect
```

**Step 2 - Start the backend:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 seed_database.py
python -m uvicorn main:app --reload --port 8000
```

**Step 3 - Start the frontend (open a new terminal):**
```bash
cd frontend
npm install
npm run dev
```

**Step 4 - Open your browser:**
Go to http://localhost:5173 and login with:
- Username: `admin`
- Password: `Admin123`

---

## How to Use It

**1. Upload a Blacklist**

Go to the Screening page and upload a CSV or Excel file with names you want to screen. The file should have columns for name, civil ID, passport number, etc.

**2. View Matches**

The system automatically screens against all your entities. Any matches above 85% similarity appear in the queue.

**3. Review Matches**

Click on a flagged item to see the details. You'll see:
- The blacklist entry
- The matching Kamco entity
- The similarity score
- Why it was flagged

Then decide: Approve (it's a real match), Reject (false positive), or Escalate (needs more review).

**4. Three-Tier Review**

Matches go through three stages:
- Screener does initial review
- Checker verifies the decision
- Finalizer gives final approval

This prevents mistakes and meets regulatory requirements.

---

## What's In the System

**Dashboard** - Shows stats like total screenings, how many items are pending, approval rates.

**Screening Queue** - List of all flagged items waiting for review.

**Individual Search** - Look up a single person against the blacklist database.

**Audit Log** - Complete history of every action taken in the system.

**User Management** - Add/remove users, assign roles.

---

## User Roles

**Screener** - Can upload files and do initial screening.

**Checker** - Reviews items flagged by screeners, can approve or reject.

**Finalizer** - Makes final decisions, can override previous decisions.

**Admin** - Can do everything, plus manage users.

---

## Test Accounts

These accounts are pre-loaded for testing:

- `screener_test` / `password123`
- `checker_test` / `password123`
- `finalizer_test` / `password123`
- `admin` / `Admin123`

---

## Tech Details

**Frontend:** React, TypeScript, Tailwind CSS

**Backend:** Python FastAPI, SQLite database

**Matching:** Uses fuzzy string matching with 85% threshold

---

## Project Files

```
fraud-detect/
├── backend/          # Python API server
│   ├── routes/       # API endpoints
│   ├── models/       # Database stuff
│   └── utils/        # Matching logic, auth, etc
├── frontend/         # React web app
│   └── src/
│       ├── pages/    # Different screens
│       └── components/  # Reusable UI parts
└── docs/             # Extra documentation
```

---

## Need Help?

- API docs are at http://localhost:8000/docs when the backend is running
- Check the `docs/` folder for more detailed guides
- Open a GitHub issue if something's broken

---

Built by Ayaan Gazali
