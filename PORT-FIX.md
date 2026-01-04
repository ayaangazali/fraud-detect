# 🚀 FIXED - Port Conflict Resolved!

## ✅ What Was Fixed

**Problem:** Port 5000 was already in use by macOS ControlCenter (AirPlay)

**Solution:** Changed backend to use **port 5001** instead

## 📝 Changes Made

1. **Backend Port:** `5000` → `5001`
   - File: `backend/src/index.ts`
   
2. **Frontend Proxy:** Updated to point to `5001`
   - File: `frontend/vite.config.ts`

3. **Created start script:** `start.sh` (auto-cleans ports)

---

## 🎯 How to Start the App (3 Options)

### Option 1: Use the Start Script (Easiest)
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco
./start.sh
```

### Option 2: Use npm (Standard)
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco
npm run dev
```

### Option 3: Run Separately (If needed)

**Terminal 1 - Backend:**
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/backend
npm run dev
```

**Terminal 2 - Frontend:**
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/frontend
npm run dev
```

---

## 🌐 Application URLs

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:5001
- **Health Check:** http://localhost:5001/api/health

---

## 🎉 No More Errors!

The `EADDRINUSE` error is now completely fixed. The app will start cleanly!

---

## 📊 Quick Test

After starting, you should see:
```
[0] 🚀 Server running on http://localhost:5001
[0] 📊 API endpoints:
[0]    POST http://localhost:5001/api/upload/customers
[0]    POST http://localhost:5001/api/upload/blacklist
[0]    POST http://localhost:5001/api/screen
[1]   VITE v5.4.21  ready in 130 ms
[1]   ➜  Local:   http://localhost:3000/
```

---

## 🔧 If Port 5001 is Also Blocked

Run this command first:
```bash
lsof -ti:5001 | xargs kill -9
```

Then start the app normally.

---

## 💡 Why Port 5000 Was Blocked

macOS Monterey and later uses port 5000 for **AirPlay Receiver**. 

To permanently disable it:
1. System Settings → General → AirDrop & Handoff
2. Uncheck "AirPlay Receiver"

But we've already fixed it by using port 5001! ✅
