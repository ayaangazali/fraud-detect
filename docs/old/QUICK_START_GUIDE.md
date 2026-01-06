# Quick Start Guide - New Excel Format

## System Overview

The KAMCO AML/KYC screening system now uses a **multi-sheet Excel file** instead of CSV files.

## Excel File Structure

### 📊 Your Excel file must have 2 sheets:

#### **Sheet 1: WC Result** (Historical Archive)
- Contains all previously flagged cases
- 36 columns with full audit trail
- **System ignores this sheet during upload** - it's for reference only

#### **Sheet 2: Change Log** (Active Queue) ⭐
- Contains new cases to review
- **This is what gets uploaded and screened**
- 11 required columns (see below)

## Change Log Format (Sheet 2)

### Required Columns:
```
CRM_REFERENCE | WC1_REF | CRM_NAME | PRIMARY_NAME | MATCH_SCORE | MATCH_STRENGTH | CHANGE_TYPE | CHANGE_FIELD | FROM_VAL | TO_VAL | RECORD_DATE
```

### Example Row:
```
123456 | e_tr_wco_11220089 | Ahmad holding co | Ahmad holding co | 99 | STRONG | update | address | 2025-12-12 | 2026-02-01 | 03/01/2026
```

### Field Descriptions:

1. **CRM_REFERENCE** - Customer ID from your CRM system (e.g., "123456")
2. **WC1_REF** - World-Check reference ID (e.g., "e_tr_wco_11220089")
3. **CRM_NAME** - Name as it appears in CRM (e.g., "Ahmad holding co")
4. **PRIMARY_NAME** - Primary name for matching (can be same as CRM_NAME)
5. **MATCH_SCORE** - Similarity score 0-100 (e.g., "99")
6. **MATCH_STRENGTH** - WEAK | MEDIUM | STRONG | VERY_STRONG
7. **CHANGE_TYPE** - new | update | delete
8. **CHANGE_FIELD** - What changed (e.g., "address", "nationality", "pep_status")
9. **FROM_VAL** - Previous value or date (use "N/A" for new entries)
10. **TO_VAL** - New value or date
11. **RECORD_DATE** - Date of record (DD/MM/YYYY format)

## How to Use

### Step 1: Prepare Your Excel File
1. Create new Excel file (.xlsx)
2. Create two sheets: "WC Result" and "Change Log"
3. Fill "Change Log" sheet with cases to review
4. Fill "WC Result" sheet with historical data (optional)

### Step 2: Upload to System
1. Go to KAMCO screening dashboard
2. Click "Upload Screening List" section
3. Drag and drop your .xlsx file or click to browse
4. System will automatically:
   - Extract "Change Log" sheet
   - Parse all 11 columns
   - Show preview of first 5 entries

### Step 3: Start Screening
1. Click "Start Screening" button
2. Set threshold (default: 70%)
3. System screens against 100 KAMCO clients
4. Results show all matches above threshold

### Step 4: Review Mode
1. Click "Enter Review Mode"
2. Swipe through each match:
   - **FLAG** (F key) - Mark as suspicious (requires comments)
   - **SAFE** (S key) - Mark as cleared
   - **Skip** (→ arrow) - Review later
3. Add investigation notes for flagged cases

### Step 5: Complete Review
1. Click "Complete Review" when done
2. Download PDF report
3. Download flagged cases Excel file
4. Flagged cases automatically saved to logbook

## Sample File

Use the provided sample file to test:
```
📁 sample-data/screening-list-sample.xlsx
```

This file contains:
- **Sheet 1 (WC Result):** 5 historical flagged cases
- **Sheet 2 (Change Log):** 15 new cases for review

## Common Issues

### ❌ "Change Log sheet not found"
**Problem:** Excel file doesn't have "Change Log" sheet  
**Solution:** Ensure Sheet 2 is named exactly "Change Log" (case-sensitive)

### ❌ "Please upload an Excel (.xlsx) file"
**Problem:** Wrong file format  
**Solution:** File must be .xlsx (not .csv or .xls)

### ❌ "No valid entries found"
**Problem:** Change Log sheet is empty or has invalid data  
**Solution:** Ensure CRM_NAME column has values (at least 3 characters)

### ❌ "Invalid column format"
**Problem:** Missing required columns  
**Solution:** Change Log must have all 11 columns in correct order

## Match Strength Guidelines

| Match Strength | Score Range | Action |
|---------------|-------------|---------|
| **VERY_STRONG** | 95-100 | Always review |
| **STRONG** | 85-94 | High priority review |
| **MEDIUM** | 70-84 | Standard review |
| **WEAK** | 50-69 | Low priority review |

## Change Type Values

- **new** - First time appearance in World-Check
- **update** - Existing entry was modified
- **delete** - Entry was removed (rare)

## Keyboard Shortcuts (Review Mode)

- **F** - Flag case (requires 10+ character comment)
- **S** - Mark as Safe
- **→** (Right Arrow) - Skip to next
- **←** (Left Arrow) - Go back to previous
- **ESC** - Exit review mode

## Report Generation

### PDF Report Includes:
- Summary statistics (Total/Flagged/Safe/Skipped)
- List of all flagged cases with details
- Investigation notes and comments
- Match scores and reasons
- Timestamp and reviewer info

### Excel Export Includes:
- All flagged cases
- Customer details from KAMCO database
- Screening details from Change Log
- Match scores and types
- User comments and timestamps

## Data Flow

```
Excel Upload → Extract Change Log Sheet → Parse 11 Columns → 
Screen vs KAMCO DB → Review Matches → FLAG/SAFE Actions → 
Save to Logbook → Generate Reports
```

## Need Help?

Check the detailed migration summary:
```
📄 MIGRATION_SUMMARY.md
```

---

**System Version:** 2.0 (Excel Multi-Sheet Format)  
**Last Updated:** January 6, 2026
