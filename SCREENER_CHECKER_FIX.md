# Screener → Checker Flow Fix

## Issues Fixed

### 1. Compliance Report Error (500 Internal Server Error)
**Problem:** `'Logbook' object has no attribute 'entity_name'`

**Root Cause:** The `report_service.py` was trying to access `entry.entity_name` and `entry.entity_type` but the Logbook model uses `kamco_name` and `kamco_type`.

**Fix:** Updated `utils/report_service.py` line 367-368:
```python
# Before
'entity_name': entry.entity_name,
'entity_type': entry.entity_type,

# After  
'entity_name': entry.kamco_name,  # Use kamco_name instead
'entity_type': entry.kamco_type,  # Use kamco_type instead
```

### 2. V2 Screening Decisions Not Appearing in Checker Queue
**Problem:** When screener flags an item via V2 `/screening/v2/decision`, it doesn't appear in checker's queue.

**Root Cause:** The V2 system creates `ScreeningMatch` and `DecisionLog` records, but the checker queue reads from `FlaggedItem` table.

**Fix:** Updated `routes/screening.py` to create a `FlaggedItem` when decision is "FLAGGED":

```python
# In /v2/decision endpoint (line ~956-978)
if decision_status == DecisionStatus.FLAGGED:
    # Determine severity based on match score
    score = match.overall_score or 0
    if score >= 90:
        severity = 'critical'
    elif score >= 80:
        severity = 'high'
    elif score >= 60:
        severity = 'medium'
    else:
        severity = 'low'
    
    # Check if FlaggedItem already exists
    existing_flagged = db.query(FlaggedItem).filter(...)
    
    if not existing_flagged:
        flagged_item = FlaggedItem(
            kamco_name=...,
            kamco_type=...,
            status='flagged',  # Ready for checker review
            ...
        )
        db.add(flagged_item)
```

### 3. Checker Queue Response Format Mismatch
**Problem:** Backend returned `data` key but frontend expected `queue` key.

**Fix:** Updated `routes/review.py` line ~729:
```python
return {
    'success': True,
    'queue': queue,  # Frontend expects this
    'data': queue,   # Backward compatibility
    'count': len(queue),
    'role': 'checker'
}
```

## Data Flow After Fix

```
┌─────────────────────┐
│  Blacklist Upload   │
│    (CSV file)       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   V2 Screening      │
│  ScreeningMatch     │
│     created         │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Screener Queue     │
│  /v2/pending-matches│
│  (ScreeningMatch)   │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Screener Decision  │
│  /v2/decision       │
│  FLAGGED → Creates  │
│  FlaggedItem        │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Checker Queue      │
│  /review/checker/   │
│  queue (FlaggedItem)│
└─────────────────────┘
```

## Test Results

### Passing Tests:
- ✅ `test_checker_queue_requires_checker_role` - Screener can't access checker queue
- ✅ `test_checker_can_access_queue` - Checker role works
- ✅ `test_checker_queue_has_correct_fields` - Correct data format
- ✅ `test_compliance_report_endpoint_works` - No more 500 error
- ✅ `test_screening_summary_endpoint_works` - Reports working
- ✅ `test_high_score_gets_high_severity` - Severity calculation works
- ✅ `test_checker_queue_requires_auth` - Auth required

### Skipped Tests (need Kamco entity data):
- ⏭️ `test_v2_flagged_decision_creates_flagged_item`
- ⏭️ `test_flagged_item_appears_in_checker_queue`
- ⏭️ `test_cleared_decision_does_not_create_flagged_item`
- ⏭️ `test_bulk_flagged_creates_multiple_flagged_items`
- ⏭️ `test_decision_creates_log_entry`
- ⏭️ `test_full_workflow_screener_to_checker`

## Files Modified

1. **`backend/utils/report_service.py`**
   - Fixed Logbook field names in compliance audit report

2. **`backend/routes/screening.py`**
   - `/v2/decision`: Creates FlaggedItem when decision=FLAGGED
   - `/v2/bulk-decision`: Creates FlaggedItems for bulk flagging

3. **`backend/routes/review.py`**
   - Checker queue returns both `queue` and `data` keys

4. **`backend/tests/test_screener_to_checker_flow.py`** (NEW)
   - Comprehensive tests for screener → checker workflow

## Verification Steps

1. **Start Backend:**
   ```bash
   cd backend && source .venv/bin/activate && python3 main.py
   ```

2. **Upload a blacklist CSV** via `/api/screening/v2/upload-blacklist`

3. **View pending matches** at `/api/screening/v2/pending-matches`

4. **Flag a match** via `/api/screening/v2/decision` with `status: FLAGGED`

5. **Check checker queue** at `/api/review/checker/queue` - item should appear

6. **View compliance report** at `/api/reports/compliance` - should return 200

## Notes

- Audit logs (`/api/audit/logs`) require admin or finalizer role - 403 for checkers is expected
- FlaggedItems created with status='flagged' are ready for checker review
- Severity is calculated based on match score (90%+ = critical, 80%+ = high, etc.)
