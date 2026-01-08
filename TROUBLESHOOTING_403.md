# 🔍 TROUBLESHOOTING 403 FORBIDDEN ERROR

**Issue:** Upload endpoint returning 403 Forbidden

---

## 🎯 Possible Causes

### 1. **No Access Token in Browser**
The frontend might not have a valid access token stored in localStorage.

**How to Check:**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Run: `localStorage.getItem('access_token')`
4. Run: `localStorage.getItem('user')`

**If null or undefined:**
- You need to log in first!
- Go to http://localhost:5173 and login with:
  - Username: `screener` or `checker` or `finalizer`
  - Password: `password123`

---

### 2. **Token Expired**
Access tokens expire after 30 minutes by default.

**Solution:** Just refresh the page - the app will auto-refresh the token using the refresh token.

---

### 3. **User Account Inactive**
The user account might be marked as inactive in the database.

**How to Check:**
```bash
cd backend
python3 -c "from database.connection import SessionLocal; from models.auth import User; db = SessionLocal(); user = db.query(User).first(); print(f'User: {user.username}, Active: {user.is_active}'); db.close()"
```

**If False:** Re-run the seed script:
```bash
cd backend
python3 scripts/seed_database.py
```

---

### 4. **Role Permission Issue**
Some endpoints require specific roles (screener, checker, finalizer).

**Upload Endpoint Requirements:**
- `/api/upload/blacklist` - Requires: **Any authenticated user**
- No specific role required, just needs to be logged in

---

## ✅ Quick Fix Steps

### Step 1: Login to the Frontend
```bash
# Make sure backend is running
cd backend
python3 ./main.py

# In another terminal, make sure frontend is running
cd frontend
npm run dev
```

Then go to http://localhost:5173 and **login with any user**:
- Username: `screener`
- Password: `password123`

### Step 2: Check Token in Console
Open DevTools Console (F12) and run:
```javascript
console.log('Token:', localStorage.getItem('access_token'));
console.log('User:', JSON.parse(localStorage.getItem('user') || '{}'));
```

### Step 3: Try Upload Again
Once logged in, the token should be automatically added to all requests.

---

## 🔧 If Still Getting 403

### Check Backend Logs
Look for these error messages in the backend terminal:
- `"User account is inactive"` → User is disabled
- `"Screener role required"` → Wrong role (shouldn't happen for upload)
- `"Could not validate credentials"` → Token is invalid

### Manual Token Test
You can test with curl:
```bash
# First, login to get a token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "screener", "password": "password123"}'

# Copy the access_token from response, then test upload
curl -X POST http://localhost:8000/api/upload/blacklist \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@test.xlsx"
```

---

## 🎯 Most Likely Cause

**You're not logged in!** 😊

The frontend shows the upload page even when not logged in, but the API requires authentication.

**Solution:**
1. Go to http://localhost:5173
2. Login with: `screener` / `password123`
3. Try upload again

The token will be automatically added to the request by the apiClient interceptor.

---

## 📝 How Authentication Works

```
Frontend Request Flow:
1. User logs in → Gets access_token & refresh_token
2. Tokens stored in localStorage
3. apiClient interceptor adds: Authorization: Bearer {token}
4. Backend verifies token → Returns user
5. If user.is_active == False → 403 Forbidden
6. If token expired → 401 Unauthorized → Auto-refresh
7. If no token → 401 Unauthorized
```

---

## ✅ Expected Behavior After Login

Once logged in, you should see:
- User info in top-right corner of UI
- Upload requests include `Authorization: Bearer ...` header
- No more 403 errors!

---

**TL;DR: Just login first!** 🔑
