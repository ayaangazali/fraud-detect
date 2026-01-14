# Screening Queue Fix Summary

## Problem
When uploading a blacklist CSV file, matches were found and shown in notifications, but they didn't appear in the Screening Queue page.

## Root Cause
**Data flow disconnect between V2 and legacy systems:**

1. **Upload endpoint** (`/screening/v2/upload-blacklist`) creates `ScreeningMatch` records in the `screening_matches` table
2. **Queue page** was calling `/screening/queue` which reads from `FlaggedItem` table (legacy system)
3. These are **TWO DIFFERENT TABLES** - the data wasn't connected!

## Solution

### Backend Changes

1. **Enhanced `/screening/v2/pending-matches` endpoint** (`routes/screening.py`)
   - Now returns full Kamco entity details (name, type, civil_id)
   - Calculates severity based on match score
   - Returns both `queue` and `matches` arrays for compatibility
   - Added all fields needed by ScreeningQueuePage

2. **Fixed `/screening/v2/decision` endpoint** (`routes/screening.py`)
   - Correctly updates `decision_status` field (was using wrong field name)
   - Creates proper `DecisionLog` records with correct field names
   - Records decision_by, decision_notes, decision_date

3. **Added `/screening/v2/bulk-decision` endpoint** (`routes/screening.py`)
   - New endpoint for bulk decisions on multiple matches
   - Accepts `match_ids`, `status`, and `notes`
   - Returns success count and any errors

### Frontend Changes

1. **ScreeningQueuePage.tsx**
   - Changed API call from `/screening/queue` to `/screening/v2/pending-matches`
   - Maps V2 response format to QueueItem interface
   - Uses `match_id` instead of `id` for compatibility

2. **ReviewModal.tsx**
   - Changed API call from `/reviews/review/${id}` to `/screening/v2/decision`
   - Maps frontend decisions (approved/rejected/escalated) to V2 statuses (CLEARED/FLAGGED/ESCALATED)
   - Uses `match_id` parameter

3. **BulkReviewModal.tsx**
   - Changed API call from `/reviews/review/bulk` to `/screening/v2/bulk-decision`
   - Uses `match_ids` instead of `item_ids`
   - Maps decisions to V2 statuses

## Data Flow (Fixed)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BEFORE (BROKEN)                               │
├─────────────────────────────────────────────────────────────────────┤
│  Upload CSV → screening_matches table                                │
│  Queue Page → flagged_items table (DIFFERENT!)                       │
│  Result: No matches shown in queue                                   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        AFTER (FIXED)                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Upload CSV → screening_matches table                                │
│  Queue Page → screening_matches table (SAME!)                        │
│  Result: Matches appear in queue ✓                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Files Modified

### Backend
- `backend/routes/screening.py` - Enhanced V2 endpoints
- `backend/tests/test_screening_queue_flow.py` - New comprehensive tests
- `backend/tests/conftest.py` - Added admin fixture and Kamco entities

### Frontend
- `frontend/src/pages/screening/ScreeningQueuePage.tsx` - Use V2 endpoint
- `frontend/src/components/review/ReviewModal.tsx` - Use V2 decision endpoint
- `frontend/src/components/review/BulkReviewModal.tsx` - Use V2 bulk-decision endpoint

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/screening/v2/upload-blacklist` | Upload blacklist CSV, creates ScreeningMatch records |
| `GET /api/screening/v2/pending-matches` | Get pending matches for review queue |
| `POST /api/screening/v2/decision` | Make decision on single match |
| `POST /api/screening/v2/bulk-decision` | Make decision on multiple matches |

## Testing

New test file: `test_screening_queue_flow.py` covers:
- Full screening flow (upload → queue → decision)
- Queue field validation for frontend compatibility
- Bulk decision operations
- Authentication requirements
- Filtering (min_score, limit)
- Decision logging

## Status
✅ Backend endpoints working
✅ Frontend updated to use V2 endpoints
✅ Bulk operations supported
✅ Decision logging working
