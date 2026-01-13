# 📋 WHAT TO UPLOAD - SIMPLE GUIDE

## 🎯 **Quick Answer**

**Upload this file:** `sample-data/kamco_entities_sample.csv`

**To this endpoint:** Kamco Entities File (first upload box - blue border)

**NOT to:** Additional Blacklist File (second upload box - optional)

---

## 📊 **Visual Guide - What Goes Where**

```
┌─────────────────────────────────────────────────────────────┐
│                    UPLOAD PAGE                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 📄 Kamco Entities File         [Required] [BLUE]      │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  👉 UPLOAD THIS FILE HERE:                             │ │
│  │     kamco_entities_sample.csv                          │ │
│  │                                                         │ │
│  │  Contains:                                              │ │
│  │  • 10 Clients (KCLI-2024-001 to 010)                  │ │
│  │  • 10 Vendors (KVEN-2024-001 to 010)                  │ │
│  │  • 10 Staff (KSTA-2024-001 to 010)                    │ │
│  │  • 10 Others (KOTH-2024-001 to 010)                   │ │
│  │  Total: 40 entities                                    │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 🛡️ Additional Blacklist File    [Optional] [GRAY]     │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │                                                         │ │
│  │  ⏸️ SKIP THIS - Leave empty                            │ │
│  │                                                         │ │
│  │  Only use if you have additional blacklist data       │ │
│  │  System already has blacklist from database            │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│                        [Cancel]  [Upload & Screen]           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 **The File You Need**

### **Location:**
```
/Users/ayaangazali/Documents/hackathons/Kamco/sample-data/kamco_entities_sample.csv
```

### **What's Inside:**
```csv
Customer_ID,Name_English,Name_Arabic,Entity_Type,Entity_Category,...
KCLI-2024-001,Mohammed Ahmed Al-Rashid,محمد أحمد الراشد,Client,Individual,...
KCLI-2024-002,Sarah Investment Corporation,شركة سارة للاستثمار,Client,Corporate,...
KVEN-2024-001,Tech Solutions International Ltd,الحلول التقنية الدولية المحدودة,Vendor,Corporate,...
KSTA-2024-001,Ahmed Mohammed Al-Sabah,أحمد محمد الصباح,Staff,Individual,...
KOTH-2024-001,Central Bank of Kuwait,البنك المركزي الكويتي,Other,Regulatory Authority,...
... (40 total rows)
```

### **Contains:**
- ✅ 10 Clients (customers)
- ✅ 10 Vendors (suppliers)
- ✅ 10 Staff (employees)
- ✅ 10 Others (regulators, government entities)
- ✅ 40 entities total with full details

---

## 🚀 **Step-by-Step: How to Upload**

### **Step 1: Start Servers**

**Terminal 1 - Backend:**
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/backend
/Users/ayaangazali/Documents/hackathons/Kamco/backend/venv/bin/python3 main.py
```

**Terminal 2 - Frontend:**
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/frontend
npm run dev
```

### **Step 2: Login**
1. Open http://localhost:3001 (or whatever port frontend shows)
2. Login with:
   - **Username:** `screener@kamco.com`
   - **Password:** `Screener123`

### **Step 3: Navigate to Upload**
- Click "Upload" in the sidebar
- OR go to URL: http://localhost:3001/upload

### **Step 4: Select File**
1. Look for the **FIRST upload box** (blue border, says "Required")
2. Click "Drop file or click to browse"
3. Navigate to: `/Users/ayaangazali/Documents/hackathons/Kamco/sample-data/`
4. Select: `kamco_entities_sample.csv`
5. See ✓ checkmark: "kamco_entities_sample.csv ready to upload"

### **Step 5: Upload**
1. **DO NOT** upload anything to the second box (Additional Blacklist - optional)
2. Click **"Upload & Screen"** button
3. Wait for processing

### **Step 6: See Results**
You should see:
- ✅ "Uploaded 40 Kamco entities successfully!"
- 🎯 "Auto-screening found X potential matches!" (if any matches)
- Redirects to Screening Queue page

---

## ✅ **Expected Success**

### **Toast Notifications:**
```
✅ Uploaded 40 Kamco entities successfully!

🎯 Auto-screening found 5 potential matches!
   (Only if blacklist entries exist in database)
```

### **API Response:**
```json
{
  "success": true,
  "message": "Successfully uploaded 40 Kamco entities",
  "data": {
    "summary": {
      "total_rows": 40,
      "valid_entities": 40,
      "stored_entities": 40,
      "by_type": {
        "clients": 10,
        "vendors": 10,
        "staff": 10,
        "others": 10
      }
    },
    "screening": {
      "blacklist_entries": 0,
      "entities_screened": 40,
      "matches_found": 0,
      "auto_screened": false,
      "message": "No blacklist data to screen against. Upload blacklist file first."
    }
  }
}
```

---

## 📝 **If You Want to Test Screening**

To see actual matches, you need blacklist data first:

### **Option 1: Upload Blacklist First (Recommended)**

1. **Create a simple blacklist CSV:**
   ```csv
   name_english,name_arabic,civil_id,nationality,source,risk_level
   Mohammed Rashid,محمد راشد,123456,Kuwaiti,UN Sanctions,High
   Ahmed Sabah,أحمد صباح,789012,Kuwaiti,OFAC,Medium
   ```

2. **Upload to blacklist endpoint first:**
   - Use second box (Additional Blacklist File)
   - OR use API directly: `POST /api/upload/blacklist`

3. **Then upload Kamco entities:**
   - Upload kamco_entities_sample.csv
   - System will auto-screen and find matches!

### **Option 2: Use Existing Database Blacklist**

If database already has blacklist entries (from seeding):
- Just upload kamco_entities_sample.csv
- Auto-screening will work automatically

---

## ❌ **Common Mistakes to Avoid**

### **Mistake 1: Wrong File Type**
```
❌ Uploading: blacklist.xlsx or customers.json
✅ Use: kamco_entities_sample.csv
```

### **Mistake 2: Wrong Upload Box**
```
❌ Uploading Kamco CSV to "Additional Blacklist File" box
✅ Use: "Kamco Entities File" box (first one, blue border)
```

### **Mistake 3: Wrong CSV Format**
```
❌ CSV with wrong columns (name, email, phone)
✅ CSV must have: Customer_ID, Name_English, Entity_Type
```

### **Mistake 4: No Authentication**
```
❌ Not logged in
✅ Login first as screener@kamco.com
```

---

## 📋 **File Format Quick Reference**

### **What You Have (Correct!):**
```
kamco_entities_sample.csv

Columns:
✅ Customer_ID         (Required) - KCLI-2024-001
✅ Name_English        (Required) - Mohammed Ahmed Al-Rashid
✅ Name_Arabic         (Optional) - محمد أحمد الراشد
✅ Entity_Type         (Required) - Client/Vendor/Staff/Other
✅ Entity_Category     (Optional) - Individual/Corporate
✅ ID_Number           (Optional) - 123456789
✅ + 12 more optional columns
```

### **What Blacklist CSV Looks Like (Different!):**
```
blacklist_entries.csv

Columns:
• name_english        - Mohammed Rashid
• name_arabic         - محمد راشد
• civil_id            - 123456
• passport_number     - PA789012
• nationality         - Kuwaiti
• source              - UN Sanctions
• risk_level          - High
• status              - Active
```

**They are DIFFERENT formats! Don't mix them up!**

---

## 🎯 **Summary**

| **What** | **Where** | **Required?** |
|----------|-----------|---------------|
| **kamco_entities_sample.csv** | First upload box (blue) | ✅ Yes |
| **Additional blacklist file** | Second upload box (gray) | ❌ No (optional) |

**One file is all you need to start!**

---

## 🧪 **Quick Test Command**

If you prefer command line:

```bash
# 1. Login and get token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"screener@kamco.com","password":"Screener123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Upload CSV
curl -X POST http://127.0.0.1:8000/api/upload/kamco-entities \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample-data/kamco_entities_sample.csv"
```

---

## ✅ **You're Ready!**

**Just upload:** `kamco_entities_sample.csv`

**To the:** First upload box (Kamco Entities File - blue border)

**And click:** "Upload & Screen"

**That's it!** 🚀

---

**See documentation:** `403_ERROR_FIXED.md` for more details!
