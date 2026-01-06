# Excel File Format Example

## 📊 File Structure Overview

```
📁 screening-list-sample.xlsx
   ├── 📄 Sheet 1: WC Result (Historical Archive - 36 columns)
   └── 📄 Sheet 2: Change Log (Active Queue - 11 columns) ⭐ SYSTEM READS THIS SHEET
```

---

## Sheet 2: Change Log (Active Queue)

### This is what the system uploads and processes!

```
┌─────────────────┬──────────────────────┬─────────────────────┬─────────────────────┬─────────────┬────────────────┬─────────────┬──────────────┬─────────────┬─────────────┬─────────────┐
│ CRM_REFERENCE   │ WC1_REF              │ CRM_NAME            │ PRIMARY_NAME        │ MATCH_SCORE │ MATCH_STRENGTH │ CHANGE_TYPE │ CHANGE_FIELD │ FROM_VAL    │ TO_VAL      │ RECORD_DATE │
├─────────────────┼──────────────────────┼─────────────────────┼─────────────────────┼─────────────┼────────────────┼─────────────┼──────────────┼─────────────┼─────────────┼─────────────┤
│ 123456          │ e_tr_wco_11220089    │ Ahmad holding co    │ Ahmad holding co    │ 99          │ STRONG         │ update      │ address      │ 2025-12-12  │ 2026-02-01  │ 03/01/2026  │
├─────────────────┼──────────────────────┼─────────────────────┼─────────────────────┼─────────────┼────────────────┼─────────────┼──────────────┼─────────────┼─────────────┼─────────────┤
│ 234567          │ e_tr_wco_22334455    │ Khalid Investment   │ Khalid Investment   │ 87          │ MEDIUM         │ new         │ entity_type  │ N/A         │ 2026-01-15  │ 04/01/2026  │
│                 │                      │ Group               │ Group LLC           │             │                │             │              │             │             │             │
├─────────────────┼──────────────────────┼─────────────────────┼─────────────────────┼─────────────┼────────────────┼─────────────┼──────────────┼─────────────┼─────────────┼─────────────┤
│ 345678          │ e_tr_wco_33445566    │ Sarah Al-Mutawa     │ Sarah Abdullah      │ 92          │ STRONG         │ update      │ nationality  │ 2025-11-20  │ 2026-01-05  │ 05/01/2026  │
│                 │                      │                     │ Al-Mutawa           │             │                │             │              │             │             │             │
├─────────────────┼──────────────────────┼─────────────────────┼─────────────────────┼─────────────┼────────────────┼─────────────┼──────────────┼─────────────┼─────────────┼─────────────┤
│ 456789          │ e_tr_wco_44556677    │ Abdullah Trading Co │ Abdullah Trading    │ 78          │ WEAK           │ update      │ registration │ 2025-10-01  │ 2026-01-02  │ 02/01/2026  │
│                 │                      │                     │ Company             │             │                │             │              │             │             │             │
├─────────────────┼──────────────────────┼─────────────────────┼─────────────────────┼─────────────┼────────────────┼─────────────┼──────────────┼─────────────┼─────────────┼─────────────┤
│ 567890          │ e_tr_wco_55667788    │ Noor Financial      │ Noor Financial      │ 95          │ VERY_STRONG    │ new         │ sanctions    │ N/A         │ 2026-01-03  │ 03/01/2026  │
│                 │                      │ Services            │ Services Ltd        │             │                │             │ _status      │             │             │             │
└─────────────────┴──────────────────────┴─────────────────────┴─────────────────────┴─────────────┴────────────────┴─────────────┴──────────────┴─────────────┴─────────────┴─────────────┘
```

---

## Sheet 1: WC Result (Historical Archive)

### This sheet is for reference only - system does NOT process this during upload

```
┌──────────┬──────────┬──────────────────┬──────────┬─────────────┬──────────┬─────────────────────┬─────────────────────┬ ... (36 columns total)
│ ROLE     │ CRM_REF  │ WC1_REF          │ CRM_TYPE │ CRM_SUBTYPE │ WC1_TYPE │ CRM_NAME            │ WC1_NAME            │
├──────────┼──────────┼──────────────────┼──────────┼─────────────┼──────────┼─────────────────────┼─────────────────────┤
│ Customer │ KC-001   │ e_tr_wco_11220089│Individual│ Retail      │ PEP      │ Ahmad Al-Mansour    │ Ahmad Al Mansour    │
├──────────┼──────────┼──────────────────┼──────────┼─────────────┼──────────┼─────────────────────┼─────────────────────┤
│ Vendor   │ KC-042   │ e_tr_wco_22334455│ Entity   │ Corporate   │ Sanctions│ Global Trade Holdings│Global Trade Holdings│
├──────────┼──────────┼──────────────────┼──────────┼─────────────┼──────────┼─────────────────────┼─────────────────────┤
│ Customer │ KC-015   │ e_tr_wco_33445566│Individual│ Private     │ PEP      │ Fatima Al-Sabah     │ Fatima Al Sabah     │
└──────────┴──────────┴──────────────────┴──────────┴─────────────┴──────────┴─────────────────────┴─────────────────────┘

... and 30 more columns: WC1_MATCH_TERM, CRM_GENDER, WC1_GENDER, CRM_BIRTH_DATE, WC1_BIRTH_DATE, 
    CRM_LOCATION, WC1_LOCATION, CRM_BIRTH_PLACE, WC1_BIRTH_PLACE, CRM_NATIONALITY, WC1_NATIONALITY,
    CRM_STATUS, CRM_STATUS_REASON, CATEGORIES, BIOGRAPHY, MATCH_STRENGTH, MATCH_SCORE, IDENTIFICATION,
    REPORTS, CREATION_DATE, MODIFICATION_DATE, PEP_NAME, PEP_CREATION_DATE, ADDRESSES, ASSOCIATES,
    ASSOCIATES_EXT, PROVIDER_TYPES, SOURCES
```

---

## Field Value Examples

### CRM_REFERENCE
```
Valid Examples:
✅ 123456
✅ KC-001
✅ CUST-2026-001
✅ 789012

Invalid:
❌ (empty)
```

### WC1_REF (World-Check Reference)
```
Valid Format: e_tr_wco_XXXXXXXX

Examples:
✅ e_tr_wco_11220089
✅ e_tr_wco_99001122
✅ e_tr_wco_12345678

Invalid:
❌ WC123456 (wrong format)
❌ (empty)
```

### CRM_NAME
```
Valid Examples:
✅ Ahmad holding co
✅ Sarah Al-Mutawa
✅ Khalid Investment Group
✅ Noor Financial Services

Invalid:
❌ A (too short - minimum 3 characters)
❌ (empty)
```

### PRIMARY_NAME
```
Valid Examples:
✅ Ahmad holding co (same as CRM_NAME)
✅ Sarah Abdullah Al-Mutawa (expanded name)
✅ Khalid Investment Group LLC (with legal suffix)

Tip: Can be same as CRM_NAME or a variation
```

### MATCH_SCORE
```
Valid Range: 0-100

Examples:
✅ 99 (very high match)
✅ 87 (high match)
✅ 72 (medium match)
✅ 55 (low match)

Invalid:
❌ 105 (exceeds 100)
❌ -5 (negative)
❌ high (must be number)
```

### MATCH_STRENGTH
```
Valid Values (case-sensitive):
✅ VERY_STRONG (95-100)
✅ STRONG (85-94)
✅ MEDIUM (70-84)
✅ WEAK (50-69)

Invalid:
❌ Very Strong (use underscore)
❌ strong (must be uppercase)
❌ HIGH (not valid value)
```

### CHANGE_TYPE
```
Valid Values:
✅ new - First appearance in World-Check
✅ update - Existing entry modified
✅ delete - Entry removed (rare)

Invalid:
❌ NEW (must be lowercase)
❌ modified (use "update")
❌ add (use "new")
```

### CHANGE_FIELD
```
Valid Examples:
✅ address
✅ nationality
✅ pep_status
✅ sanctions_status
✅ adverse_media
✅ entity_type
✅ ownership
✅ directors
✅ beneficiary
✅ business_activity

Tip: Use descriptive field name that changed
```

### FROM_VAL
```
Valid Examples:
✅ 2025-12-12 (date format)
✅ N/A (for new entries)
✅ 2025-10-01

Invalid:
❌ (empty for new entries - use "N/A")
```

### TO_VAL
```
Valid Examples:
✅ 2026-02-01 (date format)
✅ 2026-01-15
✅ 2025-12-30

Invalid:
❌ N/A (should have actual date)
❌ (empty)
```

### RECORD_DATE
```
Valid Format: DD/MM/YYYY

Examples:
✅ 03/01/2026
✅ 15/12/2025
✅ 28/02/2026

Invalid:
❌ 2026-01-03 (wrong format)
❌ 01/03/2026 (if you meant Jan 3rd, use 03/01/2026)
❌ 3/1/2026 (needs leading zeros)
```

---

## Complete Row Examples

### Example 1: High Match - New Sanctions Entry
```
123456 | e_tr_wco_11220089 | Ahmad holding co | Ahmad holding co | 99 | STRONG | update | address | 2025-12-12 | 2026-02-01 | 03/01/2026
```
**Meaning:** Customer 123456 "Ahmad holding co" has 99% match. Their address was updated from 2025-12-12 to 2026-02-01. Recorded on Jan 3, 2026.

### Example 2: New PEP Entry
```
567890 | e_tr_wco_55667788 | Noor Financial Services | Noor Financial Services Ltd | 95 | VERY_STRONG | new | sanctions_status | N/A | 2026-01-03 | 03/01/2026
```
**Meaning:** New entry for "Noor Financial Services" with 95% match strength. Added to sanctions list on Jan 3, 2026.

### Example 3: Name Variation with Update
```
345678 | e_tr_wco_33445566 | Sarah Al-Mutawa | Sarah Abdullah Al-Mutawa | 92 | STRONG | update | nationality | 2025-11-20 | 2026-01-05 | 05/01/2026
```
**Meaning:** "Sarah Al-Mutawa" also known as "Sarah Abdullah Al-Mutawa" has 92% match. Nationality info updated from Nov 20, 2025 to Jan 5, 2026.

---

## Data Validation Checklist

Before uploading your Excel file, verify:

- [ ] File extension is `.xlsx` (not `.xls` or `.csv`)
- [ ] File has exactly 2 sheets
- [ ] Sheet 2 is named "Change Log" (exact spelling, case-sensitive)
- [ ] Change Log sheet has 11 columns in correct order
- [ ] First row has column headers (CRM_REFERENCE, WC1_REF, etc.)
- [ ] All CRM_NAME values are at least 3 characters
- [ ] All MATCH_SCORE values are between 0-100
- [ ] All MATCH_STRENGTH values are: WEAK, MEDIUM, STRONG, or VERY_STRONG
- [ ] All CHANGE_TYPE values are: new, update, or delete
- [ ] All FROM_VAL for new entries are "N/A"
- [ ] All RECORD_DATE follow DD/MM/YYYY format
- [ ] No empty rows between data
- [ ] No extra columns after RECORD_DATE

---

## Testing Your File

1. **Visual Check**: Open in Excel and verify structure matches examples above
2. **Upload Test**: Try uploading to system - should see "X valid entries found"
3. **Preview Check**: System shows first 5 entries correctly
4. **Screening Test**: Run screening - should match against KAMCO database

---

## Template Download

Use the provided sample file as a template:
```bash
📁 sample-data/screening-list-sample.xlsx
```

Copy this file and replace the data with your own entries!

---

**Quick Tip:** The system ONLY reads Sheet 2 (Change Log). Sheet 1 (WC Result) is optional and for your reference only.
