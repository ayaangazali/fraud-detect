# 🎯 KAMCO SAMPLE DATA - COMPLETE PACKAGE

## 📦 What You Have

This directory contains **complete sample data** for the Kamco Fraud Detection System, including:

1. **Current database to screen** (75 entities)
2. **Historical logbook** (20 past cases with full audit trails)
3. **Sanctions blacklist** (18 sanctioned entities)
4. **Comprehensive documentation**

---

## 📁 FILE INVENTORY

### 🎯 PRIMARY DATA FILES

| File | Size | Records | Purpose |
|------|------|---------|---------|
| **kamco_entities_sample.csv** | NEW | 40 entities | **MAIN INPUT FILE** - Comprehensive entity data with Arabic/English names |
| **kamco_master_database.xlsx** | 12 KB | 75 entities | Current Kamco database to screen |
| **historical_logbook.xlsx** | 16 KB | 140 entries | Past cases with complete audit trail |
| **blacklist_comprehensive.xlsx** | 7.5 KB | 18 entities | Sanctions watchlist |

### � NEW: COMPREHENSIVE CSV INPUT FILE

**kamco_entities_sample.csv** contains 40 sample entities with complete information:

**Columns:**
- Customer_ID (e.g., KCLI-2024-001, KVEN-2024-001, KSTA-2024-001, KOTH-2024-001)
- Name_English (English name)
- Name_Arabic (Arabic name - محمد أحمد الراشد)
- Entity_Type (Client/Vendor/Staff/Other)
- Entity_Category (Individual/Corporate/Regulatory Authority/etc.)
- ID_Number (Unique identifier)
- Registration_Date
- Contact_Person
- Type_Individual_Corporate (Individual or Corporate)
- Nationality (Kuwaiti, Saudi, American, etc.)
- Country_of_Origin (Kuwait, UAE, USA, etc.)
- Industry_Sector (Real Estate, Banking, IT Services, etc.)
- Risk_Level (High/Medium/Low/N/A)
- Account_Status (Active/Inactive)
- Phone, Email, Address
- Notes (Additional details)

**Entity Breakdown:**
- 10 Clients (KCLI) - Mix of individuals and corporations
- 10 Vendors (KVEN) - Service providers and suppliers
- 10 Staff (KSTA) - Kamco employees
- 10 Others (KOTH) - Regulatory bodies, government entities, associations

### 📖 DOCUMENTATION

| File | Size | Contents |
|------|------|----------|
| **DATABASE_GUIDE.md** | 16 KB | Complete guide to database & logbook structure |
| **LOGBOOK_VISUAL_SUMMARY.txt** | 20 KB | Visual ASCII summary of all 20 cases |
| **README_SAMPLE_DATA.md** | 20 KB | Original comprehensive documentation |
| **QUICK_REFERENCE.md** | 8 KB | Quick lookup tables |
| **DATA_VISUALIZATION.txt** | 4 KB | Visual data summary |

---

## 🚀 QUICK START

### Step 1: Upload the Master Database
```bash
# Use this file for screening
kamco_master_database.xlsx
```

**Contains**:
- 📄 **Clients Sheet**: 25 companies (5 flagged)
- 📄 **Vendors Sheet**: 20 suppliers (4 flagged)
- 📄 **Staff Sheet**: 15 employees (all cleared)
- 📄 **Others Sheet**: 15 beneficial owners/advisors (7 flagged)

### Step 2: Run Screening
Screen against `blacklist_comprehensive.xlsx`

**Expected**: ~16 high-risk entities flagged

### Step 3: Reference Historical Cases
Use `historical_logbook.xlsx` to see:
- How past cases were resolved
- Decision-making patterns
- Average processing times
- Staff performance data

---

## 📊 DATABASE OVERVIEW

### KAMCO MASTER DATABASE (75 Entities)

```
┌─────────────────────────────────────────────┐
│  CLIENTS (25)                               │
│  ├─ 18 Clean: Kuwait & GCC businesses      │
│  └─ 7 Flagged: Russian connections, PEPs   │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│  VENDORS (20)                               │
│  ├─ 16 Clean: Local service providers      │
│  └─ 4 Flagged: Russian nationals, matches  │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│  STAFF (15)                                 │
│  ├─ 14 Clean: Employees cleared            │
│  └─ 1 PEP: CEO (documented & cleared)      │
└─────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│  OTHERS (15)                                │
│  ├─ 8 Clean: Kuwait/GCC nationals          │
│  └─ 7 High-Risk: Sanctioned matches        │
└─────────────────────────────────────────────┘

TOTAL: 75 entities | 16 flagged (21%)
```

---

## 🎯 TOP HIGH-RISK ENTITIES TO WATCH

### 🚨 CRITICAL (Must Block Immediately)

1. **Igor Petrov** (KC-OTH-008)
   - 40% shareholder in Falcon Investment Group
   - **EXACT MATCH**: OFAC SDN list
   - **Action**: BLOCK + Report

2. **Hassan Nasrallah** (Vendor KC-VND-016)
   - Actor in Energy Solutions International
   - **EXACT MATCH**: OFAC/UN Terrorist designation
   - **Action**: BLOCK + Report to authorities

3. **Sergei Mikhailov** (KC-OTH-010)
   - Majority owner of Atlas Holdings Group
   - **Sanctioned Russian oligarch**
   - **Action**: BLOCK + Freeze assets

4. **Phoenix Trading Limited** (Client KC-CLT-019)
   - **100% exact match** with EU sanctioned entity
   - **Action**: BLOCK immediately

### ⚠️ HIGH RISK (Enhanced Due Diligence Required)

5. **Hassan Nasrallah Jr** (KC-OTH-012)
   - 60% owner of International Finance Corp
   - **Name similarity** to terrorist designation
   - **Action**: Enhanced verification

6. **Alexander Volkov** (KC-OTH-009)
   - 25% shareholder
   - **EU sanctions list match**
   - **Action**: Enhanced screening

7. **Viktor Petrov** (Vendor KC-VND-014)
   - **Similar name** to sanctioned individual
   - **Action**: Identity verification

---

## 📋 HISTORICAL LOGBOOK INSIGHTS

### 20 Complete Cases (July - December 2025)

```
OUTCOMES:
✅ CLEARED: 11 cases (55%)
🚫 BLOCKED: 9 cases (45%)

SEVERITY:
🔴 CRITICAL: 7 cases (35%) → 71% blocked
🟠 HIGH:     8 cases (40%) → 38% blocked  
🟡 MEDIUM:   4 cases (20%) → 25% blocked
🟢 LOW:      1 case  (5%)  → 0% blocked

PROCESSING TIME:
Critical: 1.4 days average
High:     4.8 days average
Medium:   4.0 days average
Low:      3.0 days average
```

### Key Learning Patterns

**✅ Always Clear**:
- Common Arabic names (Hassan, Ahmed, Ali)
- Generic business names (Gulf/Global Trading)
- Historical entities (defunct >5 years)
- Different jurisdictions

**🚫 Always Block**:
- Exact matches (100% score)
- Terrorist designations
- Family members of sanctioned individuals
- Recent designations (<30 days)
- IRGC/Hezbollah connections

**🔍 Enhanced Review Required**:
- High match scores (>85%)
- PEP connections
- Complex ownership structures
- Shell company indicators
- Offshore entities

---

## 🎓 TRAINING USE CASES

### Module 1: Exact Matches
**Cases**: 0002, 0011, 0018
- How to identify 100% matches
- Immediate blocking procedures
- Regulatory reporting requirements

### Module 2: False Positives
**Cases**: 0001, 0005, 0014, 0016
- Common name matches
- Generic business names
- Documentation requirements for clearance

### Module 3: Enhanced Due Diligence
**Cases**: 0003, 0010, 0012
- High match scores requiring detailed review
- Information gathering techniques
- Verification procedures

### Module 4: Complex Cases
**Cases**: 0007, 0013, 0020
- Family members of sanctioned individuals
- Indirect ownership structures
- Associate relationships

### Module 5: Regulatory Reporting
**Cases**: 0009, 0011, 0018
- When to report to FIU
- Law enforcement notification
- Compliance timelines

---

## 📖 DOCUMENTATION GUIDE

### For System Testing
👉 **Read**: `DATABASE_GUIDE.md`
- Detailed field descriptions
- Expected system behavior
- Validation checklist

### For Quick Reference
👉 **Read**: `QUICK_REFERENCE.md`
- Entity lookup tables
- Quick stats
- Testing commands

### For Visual Overview
👉 **Read**: `LOGBOOK_VISUAL_SUMMARY.txt`
- ASCII art case summaries
- Timeline visualization
- Match score distributions

### For Comprehensive Details
👉 **Read**: `README_SAMPLE_DATA.md`
- Original detailed documentation
- All entity listings
- Complete test scenarios

---

## 🔍 DATA QUALITY METRICS

### Database Quality ✅
- ✅ 75 total entities across 4 sheets
- ✅ Realistic Kuwait business names
- ✅ 16 high-risk entities for testing
- ✅ Complete field coverage (no missing data)
- ✅ Consistent ID formats
- ✅ Date ranges realistic (2015-2025)
- ✅ Geographic diversity (Kuwait, GCC, Russia, Lebanon, China)

### Logbook Quality ✅
- ✅ 20 complete cases
- ✅ 140 total audit trail entries
- ✅ 7 actions per case (full lifecycle)
- ✅ Mix of CLEARED and BLOCKED decisions
- ✅ Detailed notes for every action
- ✅ Realistic match scores (45%-100%)
- ✅ 6-month historical coverage
- ✅ Multiple staff members involved

### Testing Coverage ✅
- ✅ Exact match scenarios (100%)
- ✅ High confidence matches (85-99%)
- ✅ Medium confidence matches (70-84%)
- ✅ Low confidence matches (<70%)
- ✅ False positives
- ✅ Shell company indicators
- ✅ Family member connections
- ✅ PEP screening scenarios
- ✅ Terrorist designations
- ✅ Multiple sanctions sources (OFAC, EU, UN, UK)

---

## 💻 QUICK COMMANDS

### View Files in Excel
```bash
cd sample-data
open kamco_master_database.xlsx
open historical_logbook.xlsx
open blacklist_comprehensive.xlsx
```

### Analyze with Python
```python
import pandas as pd

# Load master database (all sheets)
clients = pd.read_excel('kamco_master_database.xlsx', sheet_name='Clients')
vendors = pd.read_excel('kamco_master_database.xlsx', sheet_name='Vendors')
staff = pd.read_excel('kamco_master_database.xlsx', sheet_name='Staff')
others = pd.read_excel('kamco_master_database.xlsx', sheet_name='Others')

# Load logbook
logbook = pd.read_excel('historical_logbook.xlsx')

# Filter flagged entities
flagged = clients[clients['notes'].str.contains('⚠️|FLAGGED', na=False)]
print(f"Flagged clients: {len(flagged)}")

# Analyze case outcomes
outcomes = logbook[logbook['action'] == 'FINAL_DECISION']['status'].value_counts()
print(outcomes)
```

### Count Records
```bash
# Quick Python one-liner
python3 -c "import pandas as pd; df = pd.read_excel('kamco_master_database.xlsx', sheet_name=None); print('Total:', sum(len(sheet) for sheet in df.values()))"
```

---

## 🎯 TESTING WORKFLOW

### 1️⃣ Upload Database
```
File: kamco_master_database.xlsx
Expected: 75 entities loaded across 4 sheets
```

### 2️⃣ Run Screening
```
Against: blacklist_comprehensive.xlsx
Expected: ~16 entities flagged
```

### 3️⃣ Verify Critical Matches
```
Must Block:
✓ Igor Petrov (98.5% - OFAC SDN)
✓ Hassan Nasrallah (100% - Terrorist)
✓ Sergei Mikhailov (Oligarch)
✓ Phoenix Trading Limited (100% - EU)
```

### 4️⃣ Test Workflow
```
Screener → Flags entities
   ↓
Checker → Reviews and recommends
   ↓
Finalizer → Makes final decision (BLOCK/CLEAR)
   ↓
System → Logs all actions to database
```

### 5️⃣ Verify Audit Trail
```
Check: flagged_items table
Check: cases table
Check: case_notes table
Check: logbook table (if implemented)
```

### 6️⃣ Compare with Historical Data
```
Reference: historical_logbook.xlsx
Compare: Decision patterns, processing times
Validate: Similar cases handled consistently
```

---

## 🎯 SUCCESS CRITERIA

### System Should:
- ✅ Detect all 16 high-risk entities
- ✅ Flag 4 CRITICAL entities for immediate blocking
- ✅ Create cases with proper workflow (Screener → Checker → Finalizer)
- ✅ Log all actions with timestamps
- ✅ Store detailed notes for audit trail
- ✅ Handle false positives appropriately
- ✅ Calculate match scores accurately
- ✅ Support multi-level review process
- ✅ Generate email notifications for critical cases
- ✅ Maintain complete audit trail

### Performance Targets:
- ⏱️ Screening: <5 seconds for 75 entities vs 18 blacklist
- 📊 Match accuracy: ~85% precision
- 🚨 Critical detection: 100% (no false negatives)
- 📈 False positive rate: ~55% (appropriate sensitivity)

---

## 📞 SUPPORT

### For Questions About:

**Database Structure**
→ See `DATABASE_GUIDE.md` - Sheet-specific sections

**Expected Matches**
→ See `DATABASE_GUIDE.md` - Critical/High/Medium risk sections

**Logbook Format**
→ See `LOGBOOK_VISUAL_SUMMARY.txt` - Complete case summaries

**Testing Scenarios**
→ See `QUICK_REFERENCE.md` - Testing checklist

**Historical Patterns**
→ See `historical_logbook.xlsx` - 20 complete cases

---

## 📊 FILE COMPARISON

### Which Database to Use?

| Feature | kamco_master_database.xlsx | kamco_database_sample.xlsx |
|---------|----------------------------|---------------------------|
| Entities | **75** | 45 |
| Clients | **25** | 15 |
| Vendors | **20** | 12 |
| Staff | **15** | 10 |
| Others | **15** | 8 |
| Flagged | **16 entities** | 8 entities |
| Documentation | **Complete** | Basic |
| **Recommended** | **✅ YES** | ❌ Legacy |

**Use**: `kamco_master_database.xlsx` for complete testing coverage

---

## ✅ SUMMARY

You now have:

✅ **75 realistic Kamco entities** to screen
✅ **18 sanctioned entities** to match against  
✅ **20 historical cases** showing decision patterns
✅ **140 audit trail entries** demonstrating workflow
✅ **16 high-risk entities** for comprehensive testing
✅ **Complete documentation** (5 files, 75+ pages)
✅ **Visual summaries** for quick understanding
✅ **Training materials** for staff education
✅ **Validation checklists** for quality assurance

**Everything you need to fully test and demonstrate your sanctions screening system!** 🎉

---

## 🚀 NEXT STEPS

1. **Open** `kamco_master_database.xlsx` in Excel
2. **Review** the 4 sheets (Clients, Vendors, Staff, Others)
3. **Upload** to your system's screening module
4. **Run** sanctions screening
5. **Compare** results against `historical_logbook.xlsx`
6. **Verify** workflow (Screener → Checker → Finalizer)
7. **Check** audit trail in database
8. **Use** for training, demos, and compliance validation

---

**Last Updated**: January 7, 2026
**Total Records**: 75 entities + 20 historical cases + 18 blacklist entries = 113 total records
**Status**: ✅ Production-ready for testing
