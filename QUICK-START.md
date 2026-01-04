# 🚀 Quick Start Guide - Enhanced Dashboard

## Backend Status: ✅ Running on http://localhost:5001

## Start the Frontend

Open a **new terminal** and run:

```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/frontend
npm run dev
```

Then open your browser to: **http://localhost:3000**

---

## 🎯 New Features to Try

### 1. **Language Switching**
- Look for the language switcher in the top-right header
- Click **"AR | عربي"** to switch to Arabic
- Click **"EN"** to switch back to English
- The entire interface (including stats and modal) changes language

### 2. **Dashboard Statistics**
You'll see 8 live stats cards showing:
- 👥 Total Customers
- 📋 Total Blacklist (includes 30 hardcoded police entries)
- 🎯 Total Matches
- 📊 Match Rate (%)
- ⭐ Average Score
- 🚔 Police Matches (red card)
- 📁 User Matches (purple card)
- ⚠️ Risk Breakdown (High/Medium/Low)

### 3. **Enhanced Match Details**
In the results table, you'll now see:
- **Reason column** with badge showing match type:
  - 🎯 **Direct** (green) - 95%+ similarity, virtually identical names
  - 🔄 **Alias** (purple) - Matched via alternate name
  - 🔍 **Fuzzy** (yellow) - Pattern-based matching
- **Details column** with "View Details" button

### 4. **Match Details Popup**
Click any "View Details" button to see:
- ✅ Complete customer information
- ✅ Blacklist match details with badges
- ✅ **WHY the match occurred** (with icon and explanation)
- ✅ Score breakdown with circular progress
- ✅ Name/Alias similarity bars
- ✅ Risk level (Critical/High/Medium/Low/Minimal)
- ✅ All metadata (DOB, nationality, effective date, etc.)

---

## 🧪 Test Scenario

### Quick Test:
1. **Upload** `sample-data/customers-middle-east.csv` (50 customers)
2. **Upload** `sample-data/blacklist-middle-east.csv` (40 entries)
3. Click **"Run Screening"** with threshold 75
4. **Observe Dashboard:**
   - Total Customers: 50
   - Total Blacklist: 70 (40 user + 30 police)
   - Total Matches: ~5-10 (varies by threshold)
   - Match Rate: ~10-20%
5. **Find Customer C018** ("Omar Abdullah Bin Laden") in results
6. Click **"View Details"** button for C018
7. **In the modal, you'll see:**
   - Customer: Omar Abdullah Bin Laden
   - Matched: Osama bin Laden (Police) + Omar Abdullah Bin Laden (User)
   - Match Type: 🎯 Direct (or 🔄 Alias depending on exact match)
   - **Reason**: "Direct name match - Names are virtually identical" (or alias explanation)
   - **Score Breakdown**: 95%+ score with visual progress
   - **Risk Level**: Critical (red) or High (orange)

### Language Test:
8. Click **"AR | عربي"** button in header
9. Entire interface switches to Arabic (RTL layout)
10. Dashboard labels, table headers, buttons all in Arabic
11. Click **"EN"** to switch back

---

## 📊 What Each Match Type Means

### 🎯 Direct Match (Green Badge)
- **Confidence:** Very High (95%+)
- **Meaning:** Names are virtually identical
- **Example:** "Osama bin Laden" matches "Osama Bin Laden"
- **Action:** High priority - Investigate immediately

### 🔄 Alias Match (Purple Badge)
- **Confidence:** High-Medium (varies)
- **Meaning:** Matched via alternate name or alias
- **Example:** Customer "OBL" matches alias "Osama Bin Laden"
- **Action:** Review alias validity, check context

### 🔍 Fuzzy Match (Yellow Badge)
- **Confidence:** Medium-Low (<95%)
- **Meaning:** Pattern-based similarity detection
- **Example:** "Mohamed Ali" matches "Muhammad Ali" (80%)
- **Action:** Manual review recommended, possible false positive

---

## 🎨 Visual Indicators

### Risk Levels (by Score):
- **🔴 Critical:** ≥95% - Immediate action required
- **🟠 High:** 85-94% - Priority investigation
- **🟡 Medium:** 75-84% - Standard review
- **🟢 Low:** 65-74% - Low priority check
- **⚪ Minimal:** <65% - Likely false positive

### Blacklist Type Badges:
- **🚔 Police** (Red) - Hardcoded permanent blacklist (30 dangerous individuals)
- **📋 User** (Purple) - Your uploaded blacklist

---

## 🌍 Arabic Support

The application now fully supports Arabic:
- ✅ Arabic names in customer data
- ✅ Arabic names in blacklist
- ✅ Arabic interface (all labels, buttons, text)
- ✅ RTL (Right-to-Left) layout
- ✅ Cairo font for proper Arabic rendering
- ✅ Mixed English/Arabic content

Try uploading a CSV with Arabic names - they'll be handled perfectly!

---

## 💡 Pro Tips

1. **Match Details Modal:**
   - Click anywhere outside the modal to close it
   - Or click the "✕" button in top-right
   - Or click "Close" button at bottom

2. **Dashboard Stats:**
   - Hover over stat cards for visual feedback
   - Stats update in real-time as you filter results
   - Risk breakdown shows distribution of match severity

3. **Language Preference:**
   - Your language choice is saved automatically
   - Next time you visit, it remembers your preference
   - Stored in browser's localStorage

4. **Match Reasoning:**
   - Hover over the reason badge to see tooltip
   - Click "View Details" for full explanation
   - Score breakdown shows exactly how match was calculated

5. **Filtering:**
   - Use filters to narrow down matches
   - Dashboard "Filtered Matches" stat updates accordingly
   - Match rate recalculates based on filters

---

## 🐛 Troubleshooting

**Backend not running?**
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/backend
npm run dev
```

**Frontend not starting?**
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/frontend
npm install
npm run dev
```

**Port conflicts?**
```bash
# Use the helper script to auto-clean ports
cd /Users/ayaangazali/Documents/hackathons/Kamco
./start.sh
```

**Match details not showing?**
- Make sure you've run screening first
- Check that results table has data
- Click the blue "View Details" button in the Details column

---

## 📖 More Information

See **DASHBOARD-BILINGUAL-GUIDE.md** for:
- Complete feature documentation
- Technical implementation details
- Translation system explanation
- All 105+ translation keys
- CSS styling architecture
- Future enhancement ideas

---

## ✨ Enjoy Your Enhanced Dashboard!

You now have:
- 📊 Real-time statistics dashboard
- 🌍 Full bilingual support (EN/AR)
- 🔍 Detailed match explanations
- 💡 Match reasoning and confidence levels
- 🎯 Visual indicators and badges
- 📱 Responsive design
- 🎨 Bloomberg Terminal-inspired dark theme

Happy screening! 🚀
