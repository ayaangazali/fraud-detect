# 📊 Mock Data - Simple Guide

## Files Provided (2 files only!)

### 1. `blacklist_mock_data.csv` (15 records)
Blacklist/sanctions data to screen against Kamco entities

**Columns:**
- Name (English), Name (Arabic), Civil ID, Passport Number
- Nationality, Source, Date Added, Notes

**What happens when uploaded:**
- ✅ Stored in database
- ✅ Auto-screening runs if Kamco data exists
- ✅ Matches create flagged items
- ✅ Email notification sent

### 2. `kamco_all_entities.csv` (50 records)
**ALL Kamco data in ONE file** - Clients, Vendors, Staff, Others

**Columns:**
- Name, Type, ID Number, Date, Actor Name
- Category/Department, Country, Notes

**Types:**
- `Client` (10 records) - Customer accounts
- `Vendor` (10 records) - Suppliers/service providers
- `Staff` (15 records) - Employees
- `Other` (15 records) - Regulators, partners, auditors

**What happens when uploaded:**
- ✅ Parsed by Type column
- ✅ Clients → kamco_clients table
- ✅ Vendors → kamco_vendors table
- ✅ Staff → kamco_staff table
- ✅ Others → kamco_others table
- ✅ Auto-screening runs if blacklist exists

---

## Expected Matches

When you upload both files, these will match:

1. **Mohammed Al-Rashid** (Client) → 100% match with blacklist
2. **Sarah Investment Corp** (Client) → 100% match with blacklist
3. **Tech Solutions International** (Vendor) → 100% match with blacklist
4. **Ahmed Hassan Al-Mutairi** (Staff) → 100% match with blacklist

**Total Flagged Items:** 3-4 HIGH severity matches

---

## Quick Test

### Option 1: Upload via Frontend
```
1. Go to upload page
2. Upload blacklist_mock_data.csv
3. Upload kamco_all_entities.csv
4. Check screening queue → See 3-4 matches!
```

### Option 2: Check Database
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/backend

python3 << 'EOF'
import sys
sys.path.insert(0, '/Users/ayaangazali/Documents/hackathons/Kamco/backend')
from database.connection import get_db
from models.blacklist import BlacklistEntry
from models.database import FlaggedItem, KamcoClient, KamcoVendor, KamcoStaff, KamcoOther

db = next(get_db())
print(f"Blacklist: {db.query(BlacklistEntry).count()} records")
print(f"Clients: {db.query(KamcoClient).count()} records")
print(f"Vendors: {db.query(KamcoVendor).count()} records")
print(f"Staff: {db.query(KamcoStaff).count()} records")
print(f"Others: {db.query(KamcoOther).count()} records")
print(f"Flagged: {db.query(FlaggedItem).count()} matches")
EOF
```

---

## What Gets Stored

### blacklist_mock_data.csv → blacklist_entries table (15 records)
```
Ahmed Hassan Al-Mutairi, Fatima Mohammed Al-Sabah, Mohammed Al-Rashid,
Sarah Investment Corp, Tech Solutions International, Abdullah Khalid Al-Rashidi,
Noor Trading LLC, Hassan Ali Al-Dosari, Maryam Finance Group,
Yousef Ahmad Al-Mansoori, Global Investment Partners, Layla Hassan Al-Sabah,
Omar Trading Company, Khalid Mohammed Al-Ghanim, Diamond Enterprises
```

### kamco_all_entities.csv → 4 tables (50 records total)

**→ kamco_clients table (10 records)**
```
Mohammed Al-Rashid, Sarah Investment Corp, Global Trading LLC,
Kuwait Finance House Client, Al-Salam Holdings, Premier Investments,
National Corp Limited, Tech Ventures Kuwait, Retail Group International,
Energy Solutions Co
```

**→ kamco_vendors table (10 records)**
```
Tech Solutions International, Office Supplies Kuwait, Legal Consultants LLC,
Maintenance Plus, Security Services Co, Catering Excellence,
Marketing Solutions, Transport Logistics, Training Institute,
Financial Auditors
```

**→ kamco_staff table (15 records)**
```
Ahmed Hassan Al-Mutairi (CFO), Sarah Mohammed Al-Sabah (Compliance Manager),
Khalid Abdullah Al-Rashidi (Operations Director), Fatima Ali Al-Dosari (Risk Analyst),
Mohammed Yousef Al-Ghanim (IT Manager), and 10 more employees...
```

**→ kamco_others table (15 records)**
```
Kuwait Stock Exchange, Central Bank of Kuwait, Ministry of Commerce,
Kuwait Chamber of Commerce, National Bank of Kuwait, Kuwait Finance House,
KPMG Kuwait, Ernst & Young Kuwait, and 7 more entities...
```

---

## Database Summary After Upload

```
Total Records: 65

blacklist_entries:  15 records
kamco_clients:      10 records
kamco_vendors:      10 records
kamco_staff:        15 records
kamco_others:       15 records
flagged_items:      3-4 records (matches)
logbook:            2+ records (audit trail)
```

---

## CSV Format Examples

### blacklist_mock_data.csv
```csv
Name (English),Name (Arabic),Civil ID,Passport Number,Nationality,Source,Date Added,Notes
Mohammed Al-Rashid,محمد الرشيد,276543210987,K3456789,Kuwaiti,Local Blacklist,2024-03-10,Multiple loan defaults
```

### kamco_all_entities.csv
```csv
Name,Type,ID Number,Date,Actor Name,Category/Department,Country,Notes
Mohammed Al-Rashid,Client,ACC-2024-001,2020-03-15,Ahmed Al-Rashid,,Kuwait,High net worth individual
Tech Solutions International,Vendor,VEN-2024-001,2020-01-15,Michael Johnson,IT Services,,Software provider
Ahmed Hassan Al-Mutairi,Staff,EMP-001,2015-03-01,,Finance,,Chief Financial Officer
Kuwait Stock Exchange,Other,REG-001,,,,Kuwait,Regulatory Body
```

---

## Upload Order (Either Works!)

### Option A: Blacklist First
```
1. Upload blacklist_mock_data.csv → No Kamco data yet, no matches
2. Upload kamco_all_entities.csv → Auto-screening runs, 3-4 matches found!
```

### Option B: Kamco First
```
1. Upload kamco_all_entities.csv → 50 entities stored
2. Upload blacklist_mock_data.csv → Auto-screening runs, 3-4 matches found!
```

---

## File Locations

```
/Users/ayaangazali/Documents/hackathons/Kamco/test_data/
├── blacklist_mock_data.csv        (15 blacklist entries)
├── kamco_all_entities.csv         (50 Kamco entities - ALL types)
├── QUICK_START.md                 (This file)
├── DATABASE_STORAGE_GUIDE.md      (Detailed storage info)
└── README_MOCK_DATA.md            (Complete documentation)
```

---

## That's It!

Just **2 files** to upload:
1. `blacklist_mock_data.csv` - The bad guys
2. `kamco_all_entities.csv` - Your entities (clients, vendors, staff, others)

Upload both → Get 3-4 automatic matches → Done! 🎉
