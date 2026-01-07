# 🎯 Sample Data Quick Reference Card

## 📂 Files Created

```
sample-data/
├── kamco_database_sample.xlsx       (9.9 KB) - Your internal database
├── blacklist_comprehensive.xlsx     (7.5 KB) - Sanctions watchlist
├── blacklist_comprehensive.csv      (4.6 KB) - CSV version
├── potential_matches_report.xlsx    (5.8 KB) - Expected test results
├── potential_matches_report.csv     (1.6 KB) - CSV version
└── README_SAMPLE_DATA.md                    - Full documentation
```

---

## 🎯 Key Entities to Watch

### 🔴 CRITICAL MATCHES (Should Alert Immediately)

| Kamco Entity | Type | Actor/Owner | Blacklist Match | Score | Action |
|--------------|------|-------------|-----------------|-------|--------|
| **Falcon Investment Group** | Client | Igor Petrov | Igor Petrov (OFAC) | 98% | 🚫 BLOCK |
| **Atlas Holdings Group** | Client | Sergei Mikhailov | Atlas Holdings Group (OFAC) | 100% | 🚫 BLOCK |
| **Energy Solutions Intl** | Vendor | Hassan Nasrallah | Hassan Nasrallah (OFAC/UN) | 100% | 🚫 BLOCK + REPORT |
| **Phoenix Trading Limited** | Client | Dmitry Ivanov | Phoenix Trading Ltd (EU) | 100% | 🚫 BLOCK |

### 🟠 HIGH RISK (Needs Enhanced Review)

| Kamco Entity | Type | Actor/Owner | Blacklist Match | Score | Action |
|--------------|------|-------------|-----------------|-------|--------|
| **Eastern Trading Partners** | Client | Vladimir Sokolov | Eastern Trading LLC (OFAC) | 92% | ⚠️ REVIEW |
| **International Finance Corp** | Client | Hassan Nasrallah Jr | Hassan Nasrallah (OFAC) | 86% | ⚠️ ESCALATE |

### 🟡 MEDIUM RISK (Verify Identity)

| Kamco Entity | Type | Actor/Owner | Blacklist Match | Score | Action |
|--------------|------|-------------|-----------------|-------|--------|
| **Advanced IT Solutions** | Vendor | Igor Sokolov | Dmitry Sokolov (EU) | 72% | 🔍 VERIFY |

### 🟢 FALSE POSITIVES (Should Clear)

| Kamco Entity | Type | Actor/Owner | Weak Match | Score | Action |
|--------------|------|-------------|------------|-------|--------|
| **ABC Trading Corporation** | Client | Mohammed Al-Hassan | Atlas Holdings | 45% | ✅ CLEAR |

---

## 📊 Quick Stats

### Kamco Database: **45 Total Entities**
```
Clients:  15 (33%) → Customer accounts
Vendors:  12 (27%) → Service providers
Staff:    10 (22%) → Employees
Others:    8 (18%) → Beneficial owners, consultants
```

### Blacklist: **18 Sanctioned Entities**
```
Individuals: 10 (56%) → Terrorists, oligarchs, officials
Companies:    8 (44%) → Shell companies, fronts

Risk Levels:
  🔴 Critical: 5 entities (Terrorism, High-value targets)
  🟠 High:    12 entities (Sanctions, PEPs)
  🟡 Medium:   1 entity  (Associates)
```

### Expected Matches: **8 Test Scenarios**
```
🔴 Block Immediately:     4 matches (50%)
🟠 Enhanced Review:       2 matches (25%)
🟡 Verify Identity:       1 match  (12%)
🟢 False Positive/Clear:  1 match  (12%)
```

---

## 🏗️ Data Structure

### Kamco Database Sheets

**Sheet 1: Clients**
```
name, account_number, date_opened, actor_name, country, notes
```

**Sheet 2: Vendors**
```
name, vendor_id, date_registered, actor_name, category, notes
```

**Sheet 3: Staff**
```
name, employee_id, department, position, hire_date, notes
```

**Sheet 4: Others**
```
name, entity_type, entity_id, relationship, country, notes
```

### Blacklist Structure
```
name, aliases, entity_type, date_of_birth, nationality, country,
source, list_date, category, risk_level, description,
identification, addresses
```

---

## 🎭 Notable Entities

### From Kamco Database:

**Clients:**
- ABC Trading Corporation (Clean)
- Falcon Investment Group (⚠️ Igor Petrov - SANCTIONED)
- Eastern Trading Partners (⚠️ Vladimir Sokolov - SANCTIONED)
- International Finance Corp (⚠️ Hassan Nasrallah Jr - HIGH RISK)
- Atlas Holdings Group (⚠️ EXACT MATCH - SANCTIONED)

**Vendors:**
- Kuwait Office Supplies Co (Clean)
- Energy Solutions International (⚠️ Hassan Nasrallah - TERRORIST)
- Advanced IT Solutions (⚠️ Igor Sokolov - SIMILAR NAME)

**Others (Beneficial Owners):**
- Igor Petrov - 40% owner of Falcon Investment (SANCTIONED)
- Hassan Nasrallah Jr - 60% owner of Intl Finance (HIGH RISK)
- Sergei Mikhailov - Majority owner of Atlas Holdings (SANCTIONED)

### From Blacklist:

**Critical Risk:**
- Hassan Nasrallah (Hezbollah leader - OFAC/UN)
- North Korean Trading Company (DPRK sanctions)
- Ali Hassan Al-Majid (War crimes)

**High Risk:**
- Igor Petrov (Russian sanctions)
- Alexander Volkov (Russian oligarch)
- Viktor Petrov (Military official)
- Sergei Mikhailov (Energy sector)
- Eastern Trading Partners LLC (Sanctioned company)
- Atlas Holdings Group (Investment entity)
- Phoenix Trading Limited (Shell company)

---

## 🔍 Testing Workflow

```
1. Upload Kamco Database
   ↓
2. Upload Blacklist
   ↓
3. System Runs Fuzzy Matching
   ↓
4. Expected Results:
   - 4 Critical matches → BLOCK immediately
   - 2 High-risk matches → Enhanced review
   - 1 Medium match → Verify identity
   - 1 False positive → Clear after review
   ↓
5. Compare with potential_matches_report.xlsx
```

---

## 📋 Test Checklist

- [ ] Upload kamco_database_sample.xlsx (4 sheets)
- [ ] Upload blacklist_comprehensive.xlsx
- [ ] Run screening
- [ ] Verify Igor Petrov flagged (Client actor)
- [ ] Verify Hassan Nasrallah flagged (Vendor actor)
- [ ] Verify Atlas Holdings flagged (Company exact match)
- [ ] Verify Eastern Trading flagged (Company name match)
- [ ] Verify Hassan Nasrallah Jr flagged (Name similarity)
- [ ] Review false positive (ABC Trading Corp)
- [ ] Checker reviews matches
- [ ] Finalizer makes decisions
- [ ] Check database for all audit trails

---

## 🚀 Quick Commands

```bash
# View Kamco database
cd sample-data
python3 -c "import pandas as pd; print(pd.read_excel('kamco_database_sample.xlsx', sheet_name='Clients'))"

# View blacklist
python3 -c "import pandas as pd; df = pd.read_excel('blacklist_comprehensive.xlsx'); print(df[['name', 'risk_level', 'source']])"

# View expected matches
python3 -c "import pandas as pd; df = pd.read_excel('potential_matches_report.xlsx'); print(df[['kamco_name', 'match_score', 'recommendation']])"

# Count by risk
python3 -c "import pandas as pd; df = pd.read_excel('blacklist_comprehensive.xlsx'); print(df['risk_level'].value_counts())"
```

---

## 💡 Pro Tips

1. **Start with Critical Matches**: Test Igor Petrov and Hassan Nasrallah first
2. **Check Audit Trail**: Every action should create case notes and logbook entries
3. **Test False Positives**: ABC Trading Corp should clear after review
4. **Test Escalation**: Use Hassan Nasrallah Jr to test escalation workflow
5. **Monitor Performance**: With 45 entities vs 18 blacklist items, screening should be fast

---

## 📞 Support

See full documentation in:
- `README_SAMPLE_DATA.md` - Complete guide
- `SAMPLE_DATA_GUIDE.md` - API usage examples
- `DATABASE_STATUS.md` - Backend schema
- `QUICK_START_TEST.md` - Testing workflows

---

**Last Updated:** January 7, 2026  
**Total Test Records:** 71 (45 Kamco + 18 Blacklist + 8 Scenarios)  
**Critical Matches:** 4 expected  
**System Status:** ✅ Ready for Testing
