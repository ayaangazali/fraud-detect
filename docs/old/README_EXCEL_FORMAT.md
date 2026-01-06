# 🎯 KAMCO AML/KYC Screening System - Excel Format

## Quick Links

📚 **Documentation:**
- [✅ Migration Complete](./MIGRATION_COMPLETE.md) - Summary of all changes
- [🚀 Quick Start Guide](./QUICK_START_GUIDE.md) - How to use the system
- [📊 Excel Format Guide](./EXCEL_FORMAT_GUIDE.md) - Field examples and validation
- [🔧 Migration Summary](./MIGRATION_SUMMARY.md) - Technical details

📁 **Sample File:**
- `sample-data/screening-list-sample.xlsx` - Ready-to-use Excel file with 2 sheets

---

## What Changed?

### Before (CSV Format):
```csv
full_name,alias_alternate_names,dob_or_reg_no,nationality_country,source,effective_date
Ahmad holding co,,,Kuwait,User Upload,2026-01-05
```

### After (Excel Format):
```
📊 Excel File (.xlsx) with 2 Sheets:
├── Sheet 1: WC Result (Historical - 36 columns)
└── Sheet 2: Change Log (Active - 11 columns) ⭐ SYSTEM READS THIS
```

**Change Log Format:**
```
CRM_REFERENCE | WC1_REF | CRM_NAME | PRIMARY_NAME | MATCH_SCORE | MATCH_STRENGTH | CHANGE_TYPE | CHANGE_FIELD | FROM_VAL | TO_VAL | RECORD_DATE
123456 | e_tr_wco_11220089 | Ahmad holding co | Ahmad holding co | 99 | STRONG | update | address | 2025-12-12 | 2026-02-01 | 03/01/2026
```

---

## File Structure

### ✅ Your Excel file MUST have:
1. **File extension:** `.xlsx` (not .csv or .xls)
2. **Two sheets:**
   - Sheet 1: "WC Result" (historical archive - optional)
   - Sheet 2: "Change Log" (active queue - **required**)
3. **11 columns in Change Log sheet** (in this exact order):
   - CRM_REFERENCE
   - WC1_REF
   - CRM_NAME
   - PRIMARY_NAME
   - MATCH_SCORE
   - MATCH_STRENGTH
   - CHANGE_TYPE
   - CHANGE_FIELD
   - FROM_VAL
   - TO_VAL
   - RECORD_DATE

---

## Quick Start

### 1️⃣ Use the Sample File
```bash
# File location:
sample-data/screening-list-sample.xlsx

# Contains:
- Sheet 1 (WC Result): 5 historical flagged cases
- Sheet 2 (Change Log): 15 new cases for review
```

### 2️⃣ Upload to System
1. Open KAMCO screening dashboard
2. Go to "Upload Screening List" section
3. Drag & drop your `.xlsx` file
4. System extracts "Change Log" sheet automatically
5. Click "Start Screening"

### 3️⃣ Review Matches
1. Click "Enter Review Mode"
2. Use keyboard shortcuts:
   - **F** = Flag case (requires 10+ character comment)
   - **S** = Mark as Safe
   - **→** = Skip to next
   - **←** = Go back
3. Complete review and download reports

---

## Field Requirements

### Match Strength Values (MUST be uppercase):
- `VERY_STRONG` - 95-100% match
- `STRONG` - 85-94% match  
- `MEDIUM` - 70-84% match
- `WEAK` - 50-69% match

### Change Type Values (MUST be lowercase):
- `new` - First appearance in World-Check
- `update` - Existing entry modified
- `delete` - Entry removed (rare)

### Date Format:
- **RECORD_DATE:** DD/MM/YYYY (e.g., 03/01/2026)
- **FROM_VAL:** Date or "N/A" for new entries
- **TO_VAL:** Date

---

## Sample Row Examples

### High Priority - New Sanctions:
```
567890 | e_tr_wco_55667788 | Noor Financial Services | Noor Financial Services Ltd | 95 | VERY_STRONG | new | sanctions_status | N/A | 2026-01-03 | 03/01/2026
```

### Medium Priority - Update:
```
234567 | e_tr_wco_22334455 | Khalid Investment Group | Khalid Investment Group LLC | 87 | MEDIUM | update | entity_type | 2025-12-01 | 2026-01-15 | 04/01/2026
```

### Low Priority - Registration Change:
```
456789 | e_tr_wco_44556677 | Abdullah Trading Co | Abdullah Trading Company | 78 | WEAK | update | registration | 2025-10-01 | 2026-01-02 | 02/01/2026
```

---

## Common Errors & Solutions

### ❌ "Change Log sheet not found"
**Problem:** Sheet 2 is not named "Change Log"  
**Solution:** Rename Sheet 2 to exactly "Change Log" (case-sensitive)

### ❌ "Please upload an Excel (.xlsx) file"
**Problem:** Wrong file format  
**Solution:** Save file as .xlsx format (not .csv or .xls)

### ❌ "No valid entries found"
**Problem:** CRM_NAME column is empty or has values less than 3 characters  
**Solution:** Ensure all CRM_NAME fields have at least 3 characters

### ❌ "Invalid MATCH_STRENGTH value"
**Problem:** Value is not WEAK, MEDIUM, STRONG, or VERY_STRONG  
**Solution:** Use exact uppercase values with underscore (e.g., VERY_STRONG)

---

## Data Flow

```
1. Upload Excel file (.xlsx)
   ↓
2. System extracts "Change Log" sheet (Sheet 2)
   ↓
3. Parse 11 columns → Create ScreeningEntry objects
   ↓
4. Screen against KAMCO database (100 clients)
   ↓
5. Display matches above threshold
   ↓
6. Review Mode: FLAG / SAFE / SKIP
   ↓
7. Save flagged cases to logbook
   ↓
8. Generate PDF & Excel reports
```

---

## Documentation Index

| Document | Purpose | Audience |
|----------|---------|----------|
| **MIGRATION_COMPLETE.md** | Complete summary of all changes | Everyone |
| **QUICK_START_GUIDE.md** | Step-by-step usage instructions | End users |
| **EXCEL_FORMAT_GUIDE.md** | Field examples and validation rules | Data preparers |
| **MIGRATION_SUMMARY.md** | Technical implementation details | Developers |

---

## System Requirements

### File Format:
- ✅ Extension: `.xlsx` (Excel 2007+)
- ❌ NOT supported: `.csv`, `.xls`, `.xlsm`, `.xlsb`

### Excel Structure:
- ✅ Must have 2 sheets
- ✅ Sheet 2 must be named "Change Log"
- ✅ Change Log must have 11 columns (exact names)
- ✅ First row must be headers

### Data Requirements:
- ✅ CRM_NAME: Minimum 3 characters
- ✅ MATCH_SCORE: Number between 0-100
- ✅ MATCH_STRENGTH: WEAK, MEDIUM, STRONG, or VERY_STRONG
- ✅ CHANGE_TYPE: new, update, or delete
- ✅ RECORD_DATE: DD/MM/YYYY format

---

## Testing Checklist

Before uploading your Excel file:

- [ ] File extension is `.xlsx`
- [ ] File has 2 sheets
- [ ] Sheet 2 is named "Change Log"
- [ ] Change Log has 11 columns in correct order
- [ ] All column headers match exactly (case-sensitive)
- [ ] All CRM_NAME values are 3+ characters
- [ ] All MATCH_SCORE values are 0-100
- [ ] All MATCH_STRENGTH values are valid (WEAK/MEDIUM/STRONG/VERY_STRONG)
- [ ] All CHANGE_TYPE values are valid (new/update/delete)
- [ ] All FROM_VAL for new entries are "N/A"
- [ ] All RECORD_DATE follow DD/MM/YYYY format
- [ ] No empty rows in data

---

## Support

Need help? Check these resources in order:

1. 📊 **EXCEL_FORMAT_GUIDE.md** - See field examples and valid values
2. 🚀 **QUICK_START_GUIDE.md** - Follow step-by-step instructions  
3. 📁 **sample-data/screening-list-sample.xlsx** - Use as template
4. 🔧 **MIGRATION_SUMMARY.md** - Understand technical details

---

## Quick Reference: 11 Required Columns

1. **CRM_REFERENCE** - Customer ID (e.g., "123456")
2. **WC1_REF** - World-Check ID (e.g., "e_tr_wco_11220089")
3. **CRM_NAME** - Name in CRM (e.g., "Ahmad holding co")
4. **PRIMARY_NAME** - Full name (e.g., "Ahmad holding co")
5. **MATCH_SCORE** - Score 0-100 (e.g., "99")
6. **MATCH_STRENGTH** - WEAK|MEDIUM|STRONG|VERY_STRONG
7. **CHANGE_TYPE** - new|update|delete
8. **CHANGE_FIELD** - What changed (e.g., "address")
9. **FROM_VAL** - Previous value or "N/A"
10. **TO_VAL** - New value
11. **RECORD_DATE** - Date in DD/MM/YYYY format

---

**System Version:** 2.0 (Excel Multi-Sheet Format)  
**Last Updated:** January 6, 2026  
**Sample File:** `/sample-data/screening-list-sample.xlsx` (11KB)

🎉 **Ready to use!** Upload the sample file to test the system.
