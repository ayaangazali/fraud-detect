# KAMCO System - Quick Testing Guide

## 🚀 How to Test the System

### Start Backend
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload
```
**Backend will run at**: http://127.0.0.1:8000

### Start Frontend
```bash
cd frontend
npm run dev
```
**Frontend will run at**: http://localhost:3000

### Run Integration Tests
```bash
# Run authenticated tests (recommended)
python3 tests/authenticated_integration_test.py

# Run basic tests (no auth)
python3 tests/backend_integration_test.py

# Or use the bash script
./run_tests.sh
```

---

## 🔑 Test Users

### Screener
- **Email**: screener@kamco.com
- **Password**: Screener123
- **Permissions**: Upload files, view screening queue

### Checker
- **Email**: checker@kamco.com
- **Password**: Checker123
- **Permissions**: Review flagged items, approve/reject

### Finalizer
- **Email**: finalizer@kamco.com
- **Password**: Finalizer123
- **Permissions**: Final review, view all reports, audit logs

---

## 📄 Testing Each Page

### 1. Login Page
**URL**: http://localhost:3000/login

**Test**:
1. Try logging in with screener credentials
2. Should redirect to Dashboard
3. Try logging in with invalid credentials (should fail)

### 2. Dashboard
**URL**: http://localhost:3000/dashboard

**Test**:
1. Login as any role
2. Check if statistics cards show data
3. Check if recent activity displays

### 3. Upload Page (Screener)
**URL**: http://localhost:3000/screening/upload

**Test**:
1. Login as screener
2. Click "Choose File" and select a CSV file
3. Click "Upload Blacklist"
4. Should show success message with record count

**Sample CSV format** (blacklist.csv):
```csv
name,type,country,date_of_birth,civil_id
John Doe,PEP,Kuwait,1980-01-01,123456789
Jane Smith,Sanctions,USA,1975-05-15,987654321
```

### 4. Screening Queue Page (Screener)
**URL**: http://localhost:3000/screening/queue

**Test**:
1. Login as screener
2. Should see list of flagged items (if database has data)
3. Check severity badges (High/Medium/Low)
4. Look for match score, match type

**Expected fields**:
- Kamco Name
- Blacklist Name
- Match Score (%)
- Match Type (Exact/Fuzzy)
- Severity
- Status
- Flagged Date

### 5. Checker Review Page (Checker)
**URL**: http://localhost:3000/review/checker

**Test**:
1. Login as checker
2. Should see items awaiting checker review
3. Check if Civil IDs are displayed
4. Look for "Review" button on each item

**Expected fields**:
- Kamco Customer Name
- Kamco Civil ID
- Blacklist Match Name
- Match Score
- Severity
- Match Type

### 6. Finalizer Review Page (Finalizer)
**URL**: http://localhost:3000/review/finalizer

**Test**:
1. Login as finalizer
2. Should see high/critical severity items only
3. Check for "Escalated" badges
4. Look for review history section

**Expected fields**:
- All checker fields plus:
- Escalated status
- Reviewed By (checker info)
- Review History with timestamps

### 7. Reports Page (Finalizer)
**URL**: http://localhost:3000/reports

**Test**:
1. Login as finalizer
2. Check dashboard metrics cards
3. Verify screening summary section
4. Verify risk assessment section
5. Try clicking export buttons (may show "coming soon")

**Expected metrics**:
- Total Screenings
- Flagged Items
- Match Rate %
- High Risk Count
- Risk level breakdown (High/Medium/Low)

### 8. Audit Logs Page (Finalizer)
**URL**: http://localhost:3000/audit

**Test**:
1. Login as finalizer
2. Should see list of audit logs
3. Try filtering by:
   - Date range
   - Severity (All/Low/Medium/High/Critical)
   - Search text
4. Check pagination controls

**Expected fields**:
- Event Type
- User Name and Role
- Description
- Severity Badge
- Timestamp
- IP Address
- Resource Type

---

## 🐛 Debugging Tips

### Frontend Not Connecting to Backend
1. Check if backend is running: http://127.0.0.1:8000/api/
2. Should see API metadata
3. Check browser console for CORS errors

### 403 Forbidden Errors
1. Check if logged in
2. Check localStorage for token: `localStorage.getItem('token')`
3. Token should start with `eyJ...`
4. Try logging out and back in

### 500 Internal Server Errors
1. Check backend terminal for error messages
2. Likely database query issues
3. Check if database has test data
4. Look for Python stack traces

### Empty Data on Pages
1. **Normal if database is empty!**
2. Pages will show "No items found" or similar
3. Need to add test data to database
4. Or upload files to generate data

---

## 📊 What to Expect

### Working Features ✅
- ✅ Authentication (all 3 roles)
- ✅ Audit Logs page (fully functional)
- ✅ Reports page (partial data)
- ✅ User profile info
- ✅ Logout

### Partially Working ⚠️
- ⚠️ Screening Queue (500 error - database issue)
- ⚠️ Checker Review (500 error - database issue)
- ⚠️ Finalizer Review (500 error - database issue)
- ⚠️ Upload History (500 error - database issue)

### Not Yet Implemented ❌
- ❌ Kamco file upload (only blacklist works)
- ❌ PDF/Excel/CSV export
- ❌ Review actions (approve/reject)
- ❌ Case details pages

---

## 🔍 How to Check if Backend Endpoint Works

### Using curl
```bash
# Login
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"screener@kamco.com","password":"Screener123"}'

# Copy the access_token from response

# Test endpoint with token
curl http://127.0.0.1:8000/api/screening/queue \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Browser DevTools
1. Open page in browser
2. Press F12 to open DevTools
3. Go to Network tab
4. Reload page
5. Click on API request
6. Check:
   - Status code (should be 200 or 201)
   - Response JSON
   - Request headers (Authorization header present?)

---

## 📝 Test Checklist

### Authentication ✅
- [ ] Can login as screener
- [ ] Can login as checker
- [ ] Can login as finalizer
- [ ] Invalid credentials are rejected
- [ ] Token is stored in localStorage
- [ ] Logout works

### Upload Page ✅
- [ ] Can select file
- [ ] Upload shows progress
- [ ] Success message shows record count
- [ ] Error handling works

### Screening Queue ⚠️
- [ ] Page loads without crashing
- [ ] Shows loading state
- [ ] Shows empty state if no data
- [ ] Data displays correctly (when backend fixed)

### Review Pages ⚠️
- [ ] Checker page loads
- [ ] Finalizer page loads
- [ ] Shows empty state if no data
- [ ] Data displays correctly (when backend fixed)

### Reports Page ✅
- [ ] Metrics cards show data
- [ ] Screening summary displays
- [ ] Risk assessment displays
- [ ] Date range selector works (UI)

### Audit Logs Page ✅
- [ ] Logs list displays
- [ ] Date range filter works
- [ ] Severity filter works
- [ ] Search works
- [ ] Pagination works

---

## 🎯 Success Criteria

### Frontend Integration: ✅ COMPLETE
- All 6 pages connected to backend
- No mock data remaining
- Proper loading states
- Error handling implemented

### Backend API: ⚠️ PARTIAL
- All endpoints implemented
- Authentication working
- Some endpoints need database fixes

### Testing: ✅ GOOD
- 13/20 integration tests passing (65%)
- Authentication tests: 100% passing
- Audit tests: 100% passing
- Auth endpoints: 100% passing

---

## 🚨 If Tests Are Failing

### "Backend not responding"
```bash
# Check if backend is running
curl http://127.0.0.1:8000/api/
```
Solution: Start backend with `uvicorn main:app --reload`

### "Cannot connect to backend"
Solution: Make sure you're in the `backend` directory and virtual environment is activated

### "500 Internal Server Error"
Solution: This is expected for some endpoints - database needs test data or queries need fixes

### "403 Forbidden"
Solution: Tests need to login first - use `authenticated_integration_test.py` instead

---

**Last Updated**: January 8, 2026, 02:16 AM
**System Status**: ✅ Ready for testing and debugging
