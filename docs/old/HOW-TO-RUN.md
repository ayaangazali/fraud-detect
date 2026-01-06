# 🚀 Quick Start Guide - Running the App

## ⚠️ IMPORTANT: Port Update
**Backend now runs on port 5001** (changed from 5000 to avoid macOS AirPlay conflict)

## Step 1: Start Both Servers

### Option A: Use Start Script (Easiest - Auto-cleans ports)
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco
./start.sh
```

### Option B: Run Both Together (Standard)
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco
npm run dev
```
This starts:
- **Backend** on `http://localhost:5001` ✅
- **Frontend** on `http://localhost:3000` ✅

### Option C: Run Separately (If needed)

**Terminal 1 - Backend:**
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco
npm run dev:backend
```

**Terminal 2 - Frontend:**
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco
npm run dev:frontend
```

---

## Step 2: Open the Application

Open your browser to:
```
http://localhost:3000
```

You should see the **Bloomberg Terminal-style dark theme** interface! 🎨

---

## Step 3: Upload Customer Data

1. Click **"Choose File"** in the "Customer Upload" section
2. Select: `sample-data/customers-middle-east.csv`
3. Click **"Upload"**
4. You should see:
   - ✅ **50 Total Rows**
   - ✅ **50 Valid Rows**
   - Preview of first 20 customers
   - Names like "Mohammed Ahmed Al-Rashid", "Fatima Hassan Al-Mutairi", etc.

---

## Step 4: Upload Custom Blacklist (Optional but Recommended)

1. Click **"Choose File"** in the "Blacklist Upload" section
2. Select: `sample-data/blacklist-middle-east.csv`
3. Click **"Upload"**
4. You should see:
   - ✅ **40 Total Rows**
   - ✅ **40 Valid Rows**
   - Preview of sanctioned individuals
   - Names like "Osama Bin Laden", "Hassan Nasrallah", etc.

**Note:** Even if you don't upload a blacklist, the **30 hardcoded police entries** will still be checked!

---

## Step 5: Configure Screening

In the "Screening Controls" section:

1. **Similarity Threshold:** Set between 0-100
   - **90-100**: Very strict (only exact matches)
   - **70-85**: Recommended (catches typos/variations) ✅
   - **50-69**: More lenient
   - **Below 50**: Very loose (many false positives)

2. **Include Aliases:** ✅ Check this box (recommended)
   - This checks alternate names like "El Chapo" for "Joaquin Guzman"

---

## Step 6: Run Screening

Click the big orange **"RUN SCREENING"** button! 🔥

The backend will:
1. Load 30 hardcoded police entries ✅
2. Combine with your 40 uploaded blacklist entries ✅
3. Check all 50 customers against 70 total blacklist entries ✅
4. Display results!

---

## Step 7: Review Results

You should see matches in the results table:

### Expected Match (Guaranteed):
**Customer:** Omar Abdullah Bin Laden (C018)
**Matches:**
- 🚔 **POLICE** - "Omar Abdullah Bin Laden" (hardcoded police blacklist)
- 📋 **USER** - "Omar Abdullah Bin Laden" (your uploaded blacklist)

**This customer will show TWO matches** - one from each blacklist!

### Understanding the Badges:

| Badge | Meaning | Source |
|-------|---------|--------|
| 🚔 **POLICE** (Red) | Matched hardcoded police list | `backend/src/data/police-blacklist.ts` |
| 📋 **USER** (Purple) | Matched your uploaded CSV | `sample-data/blacklist-middle-east.csv` |

### Score Colors:
- **90-100%** (Red) - Critical risk, very close match
- **80-89%** (Orange) - High risk
- **70-79%** (Yellow) - Medium risk
- **60-69%** (Blue) - Low risk
- **Below 60%** (Gray) - Minimal risk

---

## Step 8: Filter & Sort Results

**Filter By:**
- Min Similarity Score (slider)
- Source (Government, Regulator, Other, Police)
- Blacklist Type:
  - 🚔 **Police Blacklist** - Show only hardcoded matches
  - 📋 **User Blacklist** - Show only uploaded matches

**Sort:**
- Click any column header to sort
- Click again to reverse order

---

## Step 9: Export Results

Click the green **"EXPORT TO EXCEL"** button to download:
```
screening_results_2026-01-04.xlsx
```

The Excel file includes:
- Customer ID
- Customer Name
- Customer Type
- DOB/Reg No
- Nationality/Country
- Matched Blacklist Name
- Matched Alias
- Source
- **Blacklist Type** (POLICE or USER) ⭐
- Effective Date
- Similarity Score

---

## 🎯 Testing Scenarios

### Scenario 1: Test Police Blacklist Only
1. Upload customers
2. **Don't upload any blacklist**
3. Run screening
4. You'll see matches with 🚔 **POLICE** badge only
5. This proves the hardcoded list is working!

### Scenario 2: Test Both Blacklists
1. Upload customers
2. Upload blacklist CSV
3. Run screening
4. You'll see both 🚔 **POLICE** and 📋 **USER** badges
5. Customer C018 should match BOTH!

### Scenario 3: Test Threshold Sensitivity
1. Set threshold to 95
2. Run screening → Few matches
3. Set threshold to 70
4. Run screening → More matches
5. See how threshold affects results!

### Scenario 4: Test Alias Matching
1. Uncheck "Include Aliases"
2. Run screening → Fewer matches
3. Check "Include Aliases"
4. Run screening → More matches (catches "El Chapo", "KSM", etc.)

---

## 📊 Backend Logging

Watch the terminal running the backend. You'll see:
```
Screening against 30 police entries and 40 user entries
```

This confirms:
- 30 = Hardcoded police blacklist ✅
- 40 = Your uploaded CSV ✅
- Total = 70 entries checked ✅

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/backend
npm install
npm run dev
```

### Frontend won't start?
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/frontend
npm install
npm run dev
```

### Port already in use?
Kill the process:
```bash
# Kill backend (port 5000)
lsof -ti:5000 | xargs kill -9

# Kill frontend (port 3000)
lsof -ti:3000 | xargs kill -9
```

### Can't see dark theme?
- Clear browser cache (Cmd+Shift+R)
- Check browser console for errors

### No matches found?
- Lower the threshold (try 70-75)
- Check "Include Aliases" box
- Verify files uploaded successfully

---

## 🎨 UI Features to Test

### Dark Theme (Bloomberg Terminal Style)
- Dark navy background (`#0a0e1a`)
- Orange accent color (`#ff7043`)
- Professional data tables
- Custom scrollbars (webkit browsers)

### Interactive Elements
- Hover effects on cards
- Sortable table columns (click headers)
- Filter dropdowns
- Loading states on buttons

### Responsive Design
- Resize browser window
- Check mobile view
- Grid layouts adapt

---

## 📝 What Files Do What?

### You Upload (Through UI):
```
sample-data/customers-middle-east.csv     → Customer data
sample-data/blacklist-middle-east.csv     → Your custom blacklist
```

### Automatically Loaded (Backend):
```
backend/src/data/police-blacklist.ts      → 30 hardcoded dangerous individuals
```

### Results Show:
```
🚔 POLICE badge  = Matched hardcoded list
📋 USER badge    = Matched your uploaded CSV
```

---

## 🎉 Success Indicators

You know it's working when:
- ✅ Both servers start without errors
- ✅ UI loads with dark theme
- ✅ File uploads show valid row counts
- ✅ Screening shows matches
- ✅ Customer C018 matches BOTH blacklists
- ✅ Excel export downloads successfully
- ✅ You see both 🚔 and 📋 badges in results

---

## 🚀 Ready to Start!

Run this command to begin:
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco && npm run dev
```

Then open: **http://localhost:3000**

Happy screening! 🎯
