# 🔍 403 FORBIDDEN - QUICK FIX

**Error:** `127.0.0.1:49699 - "POST /api/upload/blacklist HTTP/1.1" 403 Forbidden`

---

## ❓ What's the Issue?

**403 Forbidden** means the request is reaching the server but **you're not logged in** or **don't have permission**.

---

## ✅ THE FIX (99% of the time)

### You Need to Login First! 🔑

The upload page is accessible without login, but the **API endpoint requires authentication**.

**Steps:**
1. Open your frontend: http://localhost:5173
2. Look for the **Login button** (top-right corner)
3. Login with these credentials:
   - **Username:** `screener`
   - **Password:** `password123`
4. Try uploading again

That's it! Once logged in, the token is automatically added to all requests.

---

## 🧪 Test If You're Logged In

Open browser console (F12) and run:
```javascript
// Check if you have a token
console.log('Logged in:', !!localStorage.getItem('access_token'));

// See your user info
console.log('User:', JSON.parse(localStorage.getItem('user') || '{}'));
```

**If both are null/empty** → You're not logged in!

---

## 🔧 If Still Getting 403 After Login

### Option 1: Token Expired
**Solution:** Refresh the page - token will auto-renew

### Option 2: User Inactive
**Check:**
```bash
cd backend
python3 -c "from database.connection import SessionLocal; from models.auth import User; db = SessionLocal(); u = db.query(User).filter(User.username=='screener').first(); print(f'Active: {u.is_active if u else \"NO USER\"}'); db.close()"
```

**If False or NO USER:**
```bash
cd backend
python3 scripts/seed_database.py
```

### Option 3: Check Backend Logs
Look at your backend terminal for specific error messages like:
- `"User account is inactive"`
- `"Could not validate credentials"`

---

## 📝 How It Works

```
When you login:
1. Frontend gets access_token + refresh_token
2. Saves them to localStorage
3. apiClient automatically adds: Authorization: Bearer {token}
4. Backend verifies token → Allows upload
```

**Without login:**
```
1. No token in localStorage
2. Request sent WITHOUT Authorization header
3. Backend sees no auth → Returns 403 Forbidden
```

---

## 🎯 Summary

**Problem:** Not logged in  
**Solution:** Login at http://localhost:5173  
**Credentials:** screener / password123  

**Then try upload again!** ✅

---

**Still not working?** Check:
1. Backend running? `python3 ./main.py`
2. Frontend running? `npm run dev`
3. Users created? `python3 scripts/seed_database.py`
