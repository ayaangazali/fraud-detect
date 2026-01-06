# CSV to Excel Migration - Summary of Changes

## Overview
The system has been updated to use a multi-sheet Excel file format instead of CSV files. The Excel file now contains two sheets:

1. **WC Result** (Sheet 1) - Historical flagged cases
2. **Change Log** (Sheet 2) - New cases for review

## File Structure

### Sheet 1: WC Result (Historical Flagged Cases)
Contains 36 columns with comprehensive historical data:
- ROLE, CRM_REF, WC1_REF, CRM_TYPE, CRM_SUBTYPE, WC1_TYPE
- CRM_NAME, WC1_NAME, WC1_MATCH_TERM
- CRM_GENDER, WC1_GENDER
- CRM_BIRTH_DATE, WC1_BIRTH_DATE
- CRM_LOCATION, WC1_LOCATION
- CRM_BIRTH_PLACE, WC1_BIRTH_PLACE
- CRM_NATIONALITY, WC1_NATIONALITY
- CRM_STATUS, CRM_STATUS_REASON
- CATEGORIES, BIOGRAPHY
- MATCH_STRENGTH, MATCH_SCORE
- IDENTIFICATION, REPORTS
- CREATION_DATE, MODIFICATION_DATE
- PEP_NAME, PEP_CREATION_DATE
- ADDRESSES, ASSOCIATES, ASSOCIATES_EXT
- PROVIDER_TYPES, SOURCES

**Purpose:** Archive of all previously flagged cases with full audit trail

### Sheet 2: Change Log (Active Screening Queue)
Contains 11 columns for cases under review:
- CRM_REFERENCE - Customer reference from CRM system
- WC1_REF - World-Check reference ID
- CRM_NAME - Name in CRM system
- PRIMARY_NAME - Primary name (may differ from CRM_NAME)
- MATCH_SCORE - Similarity score (0-100)
- MATCH_STRENGTH - WEAK | MEDIUM | STRONG | VERY_STRONG
- CHANGE_TYPE - new | update | delete
- CHANGE_FIELD - Field that changed (address, nationality, pep_status, etc.)
- FROM_VAL - Previous value or date
- TO_VAL - New value or date
- RECORD_DATE - Date of record (DD/MM/YYYY format)

**Purpose:** New cases for compliance team to review

## Backend Changes

### 1. TypeScript Types (`backend/src/types/index.ts`)
Updated `ScreeningEntry` interface to match Change Log format:
```typescript
export interface ScreeningEntry {
  crm_reference: string;
  wc1_ref: string;
  crm_name: string;
  primary_name: string;
  match_score: string;
  match_strength: 'WEAK' | 'MEDIUM' | 'STRONG' | 'VERY_STRONG';
  change_type: 'new' | 'update' | 'delete';
  change_field: string;
  from_val: string;
  to_val: string;
  record_date: string;
}
```

### 2. Upload Route (`backend/src/routes/screeningRoutesV2.ts`)
**Changed from:** CSV parsing with Papa Parse
**Changed to:** Excel parsing with ExcelJS

Key updates:
- Now accepts base64-encoded Excel file data instead of CSV text
- Reads specifically from "Change Log" sheet (2nd sheet)
- Extracts 11 columns from Change Log format
- Validates that Change Log sheet exists

```typescript
// Parse Excel data (base64)
const buffer = Buffer.from(excelData, 'base64');
const workbook = new ExcelJS.Workbook();
await workbook.xlsx.load(buffer.buffer.slice(...));

// Get the "Change Log" sheet (2nd sheet)
const changeLogSheet = workbook.getWorksheet('Change Log') || workbook.getWorksheet(2);
```

### 3. Screening Service (`backend/src/services/screeningServiceV2.ts`)
Updated field mappings:
- `screeningEntry.full_name` → `screeningEntry.crm_name`
- `screeningEntry.alias_alternate_names` → `screeningEntry.primary_name` (when different from crm_name)
- `screeningEntry.source` → `screeningEntry.wc1_ref`
- `screeningEntry.effective_date` → `screeningEntry.record_date`

Match result now includes:
- `matched_blacklist_name` = `crm_name`
- `matched_alias` = `primary_name` (if different)
- `source` = `wc1_ref`
- `effective_date` = `record_date`

## Frontend Changes

### 1. API Service (`frontend/src/services/api.ts`)
Updated `uploadScreeningList` function:
```typescript
// OLD: Read as text and send as CSV
const text = await file.text();
const response = await axios.post(`${API_BASE_URL}/upload/screening-list`, {
  csvData: text,
});

// NEW: Read as ArrayBuffer and send as base64
const arrayBuffer = await file.arrayBuffer();
const base64 = btoa(
  new Uint8Array(arrayBuffer).reduce((data, byte) => data + String.fromCharCode(byte), '')
);
const response = await axios.post(`${API_BASE_URL}/upload/screening-list`, {
  excelData: base64,
});
```

### 2. Upload Component (`frontend/src/components/ScreeningListUpload.tsx`)
- Changed accepted file type from `.csv` to `.xlsx`
- Updated validation message: "Please upload an Excel (.xlsx) file"
- Updated hint text: "Excel file (.xlsx) with Change Log sheet"

## Sample Data

### Generated File
**Location:** `/sample-data/screening-list-sample.xlsx`

**Sheet 1 (WC Result):** 5 historical flagged cases including:
- Ahmad Al-Mansour (PEP)
- Global Trade Holdings (Sanctions)
- Fatima Al-Sabah (PEP Family)
- Mohammed Ibrahim (Adverse Media)
- Mideast Supplies Co (EU Sanctions)

**Sheet 2 (Change Log):** 15 new cases for review including:
- Ahmad holding co (99% match - STRONG)
- Khalid Investment Group (87% match - MEDIUM)
- Sarah Al-Mutawa (92% match - STRONG)
- Noor Financial Services (95% match - VERY_STRONG)
- Hassan Al-Dhaheri (93% match - STRONG)
- And 10 more...

## Testing Instructions

1. **Start Backend:**
   ```bash
   cd backend
   npm run dev
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Upload Test File:**
   - Navigate to screening page
   - Upload `/sample-data/screening-list-sample.xlsx`
   - System will automatically extract Change Log sheet
   - Start screening against KAMCO database

4. **Expected Behavior:**
   - File upload accepts only .xlsx files
   - Backend extracts 15 entries from Change Log sheet
   - Screening matches against 100 KAMCO clients
   - Results show CRM_NAME, MATCH_SCORE, and MATCH_STRENGTH
   - Review mode allows FLAG/SAFE actions with investigation notes

## Migration Notes

### Breaking Changes
⚠️ **CSV files are no longer supported** - System now requires Excel (.xlsx) format

### Backward Compatibility
- Old CSV files will not work and will show "Change Log sheet not found" error
- Need to convert existing CSV data to new Excel format with Change Log sheet

### Data Migration Script
To convert existing CSV files to new format, use:
```bash
cd backend
npx ts-node src/scripts/generateMockData.ts
```

This generates sample Excel file with both sheets populated with mock data.

## Benefits of New Format

1. **Structured Multi-Sheet Support:** Separate historical data from active review queue
2. **Rich Metadata:** 11 detailed fields including change tracking (CHANGE_TYPE, CHANGE_FIELD, FROM_VAL, TO_VAL)
3. **Match Strength Indicators:** Pre-calculated MATCH_STRENGTH values (WEAK/MEDIUM/STRONG/VERY_STRONG)
4. **World-Check Integration:** WC1_REF field for direct reference to World-Check entries
5. **Audit Trail:** RECORD_DATE tracks when each entry was added
6. **Change History:** FROM_VAL and TO_VAL show what changed and when

## File Locations

### Modified Files:
1. `backend/src/types/index.ts` - Updated ScreeningEntry interface
2. `backend/src/routes/screeningRoutesV2.ts` - Excel parsing with ExcelJS
3. `backend/src/services/screeningServiceV2.ts` - Updated field mappings
4. `frontend/src/services/api.ts` - Base64 encoding for Excel upload
5. `frontend/src/components/ScreeningListUpload.tsx` - .xlsx file validation

### New Files:
1. `backend/src/scripts/generateMockData.ts` - Excel generation script
2. `sample-data/screening-list-sample.xlsx` - Sample Excel file with 2 sheets

## Next Steps

1. ✅ Test file upload with sample Excel file
2. ✅ Verify Change Log sheet is correctly parsed
3. ✅ Confirm screening results show correct match data
4. ✅ Test FLAG/SAFE actions with new data structure
5. ✅ Verify flagged cases save to logbook correctly
6. ✅ Test PDF report generation with new format
7. ✅ Update any existing CSV files to new Excel format

---

**Last Updated:** January 5, 2026
**System Version:** 2.0 (Excel Multi-Sheet Format)
