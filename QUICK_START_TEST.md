# 🚀 Quick Start Guide - Testing the System

## Current System State

✅ **3 Users Ready:**
- screener@kamco.com (password: `password123`)
- checker@kamco.com (password: `password123`)  
- finalizer@kamco.com (password: `password123`)

✅ **2 Cases Already Created:**
- CASE-2026-0001 (High priority, in review)
- CASE-2026-0002 (Medium priority, flagged)

✅ **5 Items in Review Queue**

✅ **Database Migrated:** All Phase 3 fields added

---

## ⚡ Quick Test Commands

### 1. Start Backend
```bash
cd backend
python3 main.py
```

Server starts at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

---

### 2. Login (Get Token)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "screener@kamco.com", "password": "password123"}'
```

**Save the `access_token` from response!**

---

### 3. View What's in Database
```bash
cd backend
python3 check_database.py
```

Shows:
- 👥 All users
- 📁 All cases  
- 📝 All case notes
- 🔄 Review queue items
- 📧 Notifications
- 📊 Statistics

---

### 4. Test Checker Workflow

**A. Login as Checker**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "checker@kamco.com", "password": "password123"}'
```

**B. Get Checker Queue**
```bash
curl -X GET http://localhost:8000/api/checker/queue \
  -H "Authorization: Bearer YOUR_CHECKER_TOKEN"
```

**C. Assign Case to Self**
```bash
curl -X POST http://localhost:8000/api/checker/assign/1 \
  -H "Authorization: Bearer YOUR_CHECKER_TOKEN"
```

**D. Check Database - See Updates**
```bash
python3 backend/check_database.py
```

You'll see:
- `checker_id` updated
- `checker_assigned_at` timestamp added
- Status changed

**E. Approve Item**
```bash
curl -X POST http://localhost:8000/api/checker/approve/1 \
  -H "Authorization: Bearer YOUR_CHECKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Reviewed and approved. Entity verified as legitimate.",
    "recommend_close": false
  }'
```

**F. Check Database Again**
```bash
python3 backend/check_database.py
```

You'll see:
- `checker_notes` added
- `checker_reviewed_at` timestamp
- `status` changed to "finalizer_review"
- New case note created

---

### 5. Test Finalizer Workflow

**A. Login as Finalizer**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "finalizer@kamco.com", "password": "password123"}'
```

**B. Get Finalizer Queue**
```bash
curl -X GET http://localhost:8000/api/finalizer/queue \
  -H "Authorization: Bearer YOUR_FINALIZER_TOKEN"
```

**C. Assign to Self**
```bash
curl -X POST http://localhost:8000/api/finalizer/assign/1 \
  -H "Authorization: Bearer YOUR_FINALIZER_TOKEN"
```

**D. Approve and Close**
```bash
curl -X POST http://localhost:8000/api/finalizer/approve/1 \
  -H "Authorization: Bearer YOUR_FINALIZER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Final approval. Case closed as false positive.",
    "close_case": true
  }'
```

**E. Check Database Final State**
```bash
python3 backend/check_database.py
```

You'll see:
- `finalizer_id` updated
- `finalizer_notes` added
- `finalizer_reviewed_at` timestamp
- `resolution_date` set
- `status` changed to "approved"
- Case status changed to "closed"

---

### 6. Test Escalation

**Escalate to Executive Level**
```bash
curl -X POST http://localhost:8000/api/finalizer/escalate/2 \
  -H "Authorization: Bearer YOUR_FINALIZER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "High-value transaction requires executive approval",
    "escalation_level": "executive",
    "new_priority": "critical"
  }'
```

**Check Database**
```bash
python3 backend/check_database.py
```

You'll see:
- `escalation_level` set to "executive"
- Status changed to "escalated"
- Priority changed to "critical"
- Email notification created
- Case note with escalation details

---

## 📊 Complete Workflow Test

Run this complete test sequence:

```bash
#!/bin/bash

# 1. Login as screener
SCREENER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "screener@kamco.com", "password": "password123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Screener token: $SCREENER_TOKEN"

# 2. Login as checker
CHECKER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "checker@kamco.com", "password": "password123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Checker token: $CHECKER_TOKEN"

# 3. Login as finalizer
FINALIZER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "finalizer@kamco.com", "password": "password123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Finalizer token: $FINALIZER_TOKEN"

# 4. Checker assigns case
curl -X POST http://localhost:8000/api/checker/assign/1 \
  -H "Authorization: Bearer $CHECKER_TOKEN"

# 5. Check database
python3 backend/check_database.py

# 6. Checker approves
curl -X POST http://localhost:8000/api/checker/approve/1 \
  -H "Authorization: Bearer $CHECKER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Approved after review", "recommend_close": false}'

# 7. Check database
python3 backend/check_database.py

# 8. Finalizer assigns
curl -X POST http://localhost:8000/api/finalizer/assign/1 \
  -H "Authorization: Bearer $FINALIZER_TOKEN"

# 9. Finalizer approves and closes
curl -X POST http://localhost:8000/api/finalizer/approve/1 \
  -H "Authorization: Bearer $FINALIZER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Final approval granted", "close_case": true}'

# 10. Final database check
python3 backend/check_database.py
```

---

## 🎯 What to Look For

After each API call, run `python3 backend/check_database.py` and look for:

### After Checker Assign:
```
flagged_items:
  checker_id: 2 ✅
  checker_assigned_at: 2026-01-07 XX:XX:XX ✅
  status: checker_review ✅
```

### After Checker Approve:
```
flagged_items:
  checker_notes: "Approved after review" ✅
  checker_reviewed_at: 2026-01-07 XX:XX:XX ✅
  status: finalizer_review ✅

case_notes:
  New note with checker's comments ✅
```

### After Finalizer Assign:
```
flagged_items:
  finalizer_id: 3 ✅
```

### After Finalizer Approve:
```
flagged_items:
  finalizer_notes: "Final approval granted" ✅
  finalizer_reviewed_at: 2026-01-07 XX:XX:XX ✅
  resolution_date: 2026-01-07 XX:XX:XX ✅
  status: approved ✅

cases:
  status: closed ✅
  closed_at: 2026-01-07 XX:XX:XX ✅
```

---

## 📱 Using the API Docs (Swagger UI)

1. Start backend: `python3 backend/main.py`
2. Open browser: `http://localhost:8000/docs`
3. Click "Authorize" button (🔒)
4. Login first to get token
5. Paste token in: `Bearer YOUR_TOKEN`
6. Click "Authorize"
7. Now test any endpoint with the UI!

---

## 🔍 Verify Migration Worked

```bash
cd backend
python3 -c "
from models.database import FlaggedItem

# Check FlaggedItem has all Phase 3 fields
fields = [c.name for c in FlaggedItem.__table__.columns]

phase3_fields = [
    'checker_assigned_at',
    'checker_reviewed_at',
    'finalizer_reviewed_at',
    'resolution_date',
    'checker_notes',
    'finalizer_notes',
    'escalation_level'
]

print('Phase 3 Fields Check:')
for field in phase3_fields:
    status = '✅' if field in fields else '❌'
    print(f'  {status} {field}')

print(f'\nTotal FlaggedItem fields: {len(fields)}')
"
```

Expected output:
```
Phase 3 Fields Check:
  ✅ checker_assigned_at
  ✅ checker_reviewed_at
  ✅ finalizer_reviewed_at
  ✅ resolution_date
  ✅ checker_notes
  ✅ finalizer_notes
  ✅ escalation_level

Total FlaggedItem fields: 32
```

---

## 🎉 Success Criteria

After running tests, you should see:

✅ **Login works** - Gets JWT token
✅ **Checker can assign** - checker_id and timestamp set
✅ **Checker can approve** - Notes and timestamps stored
✅ **Finalizer can assign** - finalizer_id set
✅ **Finalizer can approve** - Case closes with all data
✅ **Escalation works** - escalation_level set
✅ **All data persists** - Visible in check_database.py
✅ **Audit trail complete** - Case notes created for each action

---

## 📚 Reference Files

1. **SAMPLE_DATA_GUIDE.md** - All sample inputs and expected outputs
2. **DATABASE_STATUS.md** - Current database state and schema
3. **backend/check_database.py** - View all data anytime
4. **backend/run_migration.py** - Migration script (already ran)

---

## 💡 Tips

1. **Always check database after API calls**
   ```bash
   python3 backend/check_database.py
   ```

2. **Use API docs for easy testing**
   ```
   http://localhost:8000/docs
   ```

3. **Watch backend logs**
   - Shows each request
   - Shows any errors
   - Shows database queries

4. **Reset database if needed**
   ```bash
   rm backend/database/kamco.db
   python3 backend/main.py  # Will recreate
   python3 backend/run_migration.py  # Re-run migration
   ```

---

## 🚨 Troubleshooting

**Problem:** "No such column: checker_assigned_at"
**Solution:** Run migration: `python3 backend/run_migration.py`

**Problem:** "401 Unauthorized"
**Solution:** Token expired or invalid - login again

**Problem:** "403 Forbidden"  
**Solution:** Wrong role - use checker/finalizer token for those endpoints

**Problem:** "Database locked"
**Solution:** Close any other database connections, restart backend

---

## ✨ You're All Set!

Your system is ready to test. Start with:

1. `python3 backend/main.py` (start server)
2. Visit `http://localhost:8000/docs` (API docs)
3. Login with test accounts
4. Test workflows
5. Run `python3 backend/check_database.py` to see results

**Happy Testing! 🎉**
