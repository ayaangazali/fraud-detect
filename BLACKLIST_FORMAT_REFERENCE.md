# Blacklist File Format Reference
## KAMCO Compliance Screening System

---

## 📋 Overview

This document describes the expected format for blacklist files uploaded to the KAMCO screening system. The format is based on the reference file `blacklist_comprehensive.xlsx`.

---

## 📊 Excel File Structure

### Required Sheet Name
- **Sheet 1**: "Blacklist" or "Sheet1" (default)
- Multi-sheet files supported, will process the first sheet

### File Formats Supported
- `.xlsx` (Excel 2007+) - **Recommended**
- `.xls` (Excel 97-2003)
- `.csv` (Comma-separated values)

### Maximum File Size
- 10 MB per file

---

## 📝 Column Schema

### Required Columns

#### 1. **name_arabic** (REQUIRED)
- **Description**: Arabic name of the sanctioned entity
- **Type**: Text (Arabic script)
- **Example**: `محمد أحمد العبدالله`
- **Notes**: Primary matching field

### Optional Columns

#### 2. **name_english** (Optional)
- **Description**: English transliteration or translation
- **Type**: Text (Latin script)
- **Example**: `Mohammed Ahmed Al-Abdullah`
- **Notes**: Used for secondary matching

#### 3. **civil_id** (Optional)
- **Description**: Civil ID or national identification number
- **Type**: Text or Number
- **Example**: `123456789012`
- **Notes**: Exact match only, high confidence

#### 4. **decree_number** (Optional)
- **Description**: Sanction decree or resolution number
- **Type**: Text
- **Example**: `UN/2024/1234` or `OFAC-12345`
- **Notes**: Reference to legal basis

#### 5. **decree_date** (Optional)
- **Description**: Date of sanction decree
- **Type**: Date
- **Format**: `YYYY-MM-DD` or Excel date
- **Example**: `2024-01-15`

#### 6. **type** (Optional)
- **Description**: Entity type classification
- **Type**: Text
- **Allowed Values**: 
  - `Individual`
  - `Entity`
  - `Organization`
  - `Company`
  - `NGO`
- **Example**: `Individual`

#### 7. **nationality** (Optional)
- **Description**: Nationality of individual or entity origin
- **Type**: Text
- **Example**: `Syrian` or `SY`

#### 8. **date_of_birth** (Optional)
- **Description**: Date of birth (individuals only)
- **Type**: Date
- **Format**: `YYYY-MM-DD`
- **Example**: `1980-05-20`

#### 9. **passport_number** (Optional)
- **Description**: Passport number
- **Type**: Text
- **Example**: `A12345678`

#### 10. **address** (Optional)
- **Description**: Last known address
- **Type**: Text
- **Example**: `123 Main Street, Damascus`

#### 11. **sanction_type** (Optional)
- **Description**: Type of sanction
- **Type**: Text
- **Examples**: 
  - `Asset Freeze`
  - `Travel Ban`
  - `Arms Embargo`
  - `Financial Sanctions`

#### 12. **sanction_source** (Optional)
- **Description**: Sanctioning authority
- **Type**: Text
- **Examples**:
  - `UN Security Council`
  - `OFAC`
  - `EU Sanctions`
  - `Kuwait National Authority`

#### 13. **notes** (Optional)
- **Description**: Additional notes or comments
- **Type**: Text (Long)
- **Example**: `Designated for terrorism financing`

---

## 📐 Example Data

### Minimal Example (Required Fields Only)
```excel
| name_arabic           |
|----------------------|
| محمد أحمد السوري     |
| علي حسن المصري       |
| شركة التجارة الدولية |
```

### Complete Example (All Fields)
```excel
| name_arabic  | name_english      | civil_id      | decree_number | decree_date | type       | nationality | sanction_type | sanction_source |
|-------------|------------------|--------------|--------------|------------|-----------|------------|--------------|----------------|
| محمد أحمد   | Mohammed Ahmed   | 123456789012 | UN/2024/001  | 2024-01-15 | Individual| Syrian     | Asset Freeze | UN             |
| شركة ABC    | ABC Corporation  |              | OFAC-9876    | 2023-12-10 | Entity    | Lebanese   | Financial    | OFAC           |
```

---

## 🔍 Matching Behavior

### Name Matching
1. **Exact Match** (95%+ confidence)
   - Character-by-character comparison
   - Case insensitive
   - Whitespace normalized

2. **Fuzzy Match** (75-94% confidence)
   - Phonetic similarity
   - Character transposition
   - Missing/extra characters
   - Arabic diacritical marks ignored

3. **Name Normalization**
   - Arabic: Removes diacritics (تشكيل)
   - English: Converts to lowercase, removes special chars
   - Handles "Al-", "El-" prefixes

### Civil ID Matching
- **Exact match only**
- **100% confidence** when matched
- No fuzzy matching on numbers

### Multi-Field Matching
- System combines match scores from all available fields
- Higher weight given to:
  1. Civil ID (if present)
  2. Name (primary field)
  3. Decree number (supporting evidence)

---

## ⚠️ Data Quality Guidelines

### DO:
✅ Use UTF-8 encoding for Arabic text
✅ Provide name_arabic for every entry
✅ Use consistent date formats
✅ Remove duplicate entries before upload
✅ Validate civil IDs before upload
✅ Include decree numbers when available
✅ Use standard country codes

### DON'T:
❌ Leave name_arabic field empty
❌ Use mixed languages in same field
❌ Include formatting (bold, colors) - will be ignored
❌ Add formulas - values only
❌ Merge cells
❌ Use special characters in column headers

---

## 🚨 Common Errors & Solutions

### Error: "Invalid Excel structure"
**Cause**: Missing required columns
**Solution**: Ensure "name_arabic" column exists

### Error: "No valid records found"
**Cause**: All rows have empty name_arabic
**Solution**: Fill name_arabic for all entries

### Error: "Invalid file type"
**Cause**: File is not Excel or CSV
**Solution**: Convert to .xlsx format

### Error: "File too large"
**Cause**: File exceeds 10MB
**Solution**: Split into multiple files

---

## 📤 Upload Process

### Step 1: Prepare File
1. Open reference file: `blacklist_comprehensive.xlsx`
2. Copy column structure
3. Fill in your data
4. Save as .xlsx

### Step 2: Validate Data
1. Check all name_arabic cells are filled
2. Verify dates are in correct format
3. Remove any merged cells
4. Save file

### Step 3: Upload
1. Go to "Upload Files" page
2. Drag & drop file or click to select
3. Wait for validation
4. Review summary
5. Confirm upload

### Step 4: Review Results
1. Navigate to "Screening Queue"
2. View matched entities
3. Review match scores
4. Approve/flag/escalate as needed

---

## 💾 Batch Processing

### Small Batches (< 100 records)
- Upload processes immediately
- Results available in ~10 seconds

### Medium Batches (100-1000 records)
- Background processing
- Results available in 1-2 minutes
- Email notification sent when complete

### Large Batches (> 1000 records)
- Queued for processing
- Results available in 5-10 minutes
- Email notification sent
- Progress tracking available

---

## 🔄 Update Existing Blacklist

### Adding New Entries
1. Upload new file with additional entries
2. System will:
   - Check for duplicates
   - Merge with existing blacklist
   - Re-screen active customers

### Removing Entries
1. Cannot remove via upload
2. Use "Data Management" page
3. Select entries to remove
4. Confirm deletion

### Updating Entries
1. Upload file with same civil_id or name
2. System will prompt to:
   - Update existing entry
   - Create new entry
   - Skip duplicate

---

## 📚 Sample Files

### Available Sample Files
1. `blacklist_comprehensive.xlsx` - Full example with all fields
2. `blacklist_minimal.xlsx` - Minimal example (name_arabic only)
3. `blacklist_template.xlsx` - Empty template to fill

### Download Location
`/sample-data/` directory in project

---

## 🔗 Related Documentation

- [Backend to Frontend Integration TODO](./BACKEND_TO_FRONTEND_TODO.md)
- [System Ready Guide](./SYSTEM_READY.md)
- [Phase 9 Completion Report](./PHASE9_COMPLETE_FIXES.md)

---

## 📞 Support

For issues or questions:
- Check logs in "Audit Logs" page
- Review error messages carefully
- Verify file format against this guide
- Contact system administrator

---

*Last Updated: January 8, 2026*
*Format Version: 1.0*
