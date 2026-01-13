# 🔐 Test Login Credentials

**Last Updated:** January 13, 2026

---

## 📋 Available Test Accounts

### 1. Screener Account
- **Username:** `screener_test`
- **Password:** `Screener123`
- **Role:** Screener
- **Email:** screener@kamco.com
- **Permissions:** Upload files, view screening results

### 2. Checker Account
- **Username:** `checker_test`
- **Password:** `Checker123`
- **Role:** Checker
- **Email:** checker@kamco.com
- **Permissions:** Review matches, approve/reject flags

### 3. Finalizer Account
- **Username:** `finalizer_test`
- **Password:** `Finalizer123`
- **Role:** Finalizer
- **Email:** finalizer@kamco.com
- **Permissions:** Final approval, generate reports

---

## 🚀 Quick Start

### Step 1: Start Backend
```bash
cd backend
source venv/bin/activate
python3 main.py
```

Backend will run on: **http://localhost:8000**

### Step 2: Start Frontend
```bash
cd frontend
npm run dev
```

Frontend will run on: **http://localhost:5173**

### Step 3: Login
1. Open browser to **http://localhost:5173**
2. Use any of the credentials above
3. Start testing!

---

## 🔍 Testing Each Role

### As Screener (`screener_test` / `Screener123`)
1. Login with screener credentials
2. Go to Upload page
3. Upload Kamco entities CSV file
4. View screening results

### As Checker (`checker_test` / `Checker123`)
1. Login with checker credentials
2. Go to Checker Review page
3. Review flagged matches
4. Approve/Reject/Escalate items
5. Use Bulk Review Wizard for multiple items

### As Finalizer (`finalizer_test` / `Finalizer123`)
1. Login with finalizer credentials
2. Go to Finalizer Review page
3. Review escalated items
4. Final approval/rejection
5. Generate compliance reports

---

## ⚠️ Important Notes

### Password Requirements
All passwords must have:
- ✅ At least 8 characters
- ✅ At least 1 uppercase letter
- ✅ At least 1 lowercase letter
- ✅ At least 1 digit

### Session Management
- **Access Token:** Valid for 15 minutes
- **Refresh Token:** Valid for 7 days
- Automatic refresh when needed

### Rate Limiting
- **Failed Logins:** 5 attempts allowed
- **Lockout Time:** 5 minutes after 5 failed attempts
- Resets on successful login

---

## 🛠️ Troubleshooting

### Getting 401 Unauthorized?

1. **Check Backend is Running**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy"}`

2. **Verify User Exists in Database**
   ```bash
   cd backend
   source venv/bin/activate
   python3 -c "
   from database.connection import SessionLocal
   from models.auth import User
   db = SessionLocal()
   users = db.query(User).all()
   for u in users:
       print(f'{u.username} - {u.email} - {u.role.value}')
   db.close()
   "
   ```

3. **Re-seed Database if Needed**
   ```bash
   cd backend
   source venv/bin/activate
   python seed_database.py
   ```

4. **Check Browser Console**
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Check Network tab for API responses

5. **Verify Credentials**
   - Username is case-sensitive
   - Password is case-sensitive
   - No extra spaces before/after

### Token Expired?
- Tokens expire after 15 minutes
- Frontend should auto-refresh
- If not, logout and login again

### CORS Issues?
- Backend should allow `http://localhost:5173`
- Check `main.py` CORS configuration
- Restart backend if changed

---

## 📊 Test Data

### Sample Kamco Entities
Located in: `test_data/sample_kamco_entities.csv`

### Sample Blacklist
Located in: `test_data/sample_blacklist.csv`

---

## 🔒 Security Features

✅ **Bcrypt password hashing**
✅ **JWT token authentication**  
✅ **Rate limiting (5 attempts)**
✅ **SQL injection prevention**
✅ **XSS attack prevention**
✅ **Input sanitization**
✅ **Audit logging**
✅ **Role-based access control**

---

## 📞 Need Help?

If you're still getting 401 errors:
1. Check this file for correct credentials
2. Verify backend is running
3. Re-seed the database
4. Clear browser cache and cookies
5. Try incognito/private browsing mode

---

**Status:** ✅ All test accounts are active and working!
