# Phase 3: Workflow Redesign - Quick Start Guide

## Current Status
✅ **Phase 2 Complete** - Database schema enhanced with case management, workflow tracking, email notifications, and reporting.

## Test User Credentials
```
Screener:  screener@kamco.com  / Screener123
Checker:   checker@kamco.com   / Checker123
Finalizer: finalizer@kamco.com / Finalizer123
```

## Phase 3 Tasks Overview

### 🔴 Task 3.1 - Flag Endpoint Enhancement
**File**: `backend/routes/review.py`  
**Endpoint**: POST `/api/review/flag`  
**Changes Needed**:
- Add `current_user: User = Depends(require_screener)` to function signature
- Create `Case` record with `Case.generate_case_number()`
- Update `InReviewQueue` with:
  - `case_id` (link to created case)
  - `screener_id` (current_user.id)
  - `risk_score` (calculate from match_percentage + actor_presence)
  - `requires_checker_review` (based on risk_score > 7)
  - `status` = "in_progress"
- Create `CaseNote` with NoteType.SYSTEM for flag creation
- Queue `EmailNotification` (EmailType.FLAG_CREATED) to checker
- Add to `Logbook` with action_type='flag'
- Return: case_number, case_id in response

**Risk Score Calculation**:
```python
risk_score = min(10, int((match_percentage / 10) + (3 if actor_presence else 0)))
requires_checker_review = risk_score >= 7
```

---

### 🔴 Task 3.2 - Undo Endpoint Enhancement
**File**: `backend/routes/review.py`  
**Endpoint**: POST `/api/review/undo`  
**Changes Needed**:
- Add `current_user: User = Depends(require_screener)` to function signature
- Validate ownership: `item.screener_id == current_user.id`
- Check if reviewed by checker: `if item.checker_id is not None: raise HTTPException(403)`
- Remove from `InReviewQueue`
- Update `Case` status to appropriate state
- Add `CaseNote` with NoteType.SYSTEM and undo reason
- If checker was assigned, queue `EmailNotification`
- Add to `Logbook` with:
  - `action_type` = 'clear'
  - `previous_status` = old case status
  - `new_status` = new case status
- Return: case info with updated status

---

### 🔴 Task 3.3 - Checker Review Endpoints
**File**: `backend/routes/checker.py` (NEW FILE)  
**Base Path**: `/api/review/checker`

#### Endpoint 1: POST `/assign`
**Purpose**: Assign flagged item to checker (auto or manual)  
**Auth**: `require_checker`  
**Actions**:
- Find pending InReviewQueue items or specific item_id
- Update `FlaggedItem`:
  - `checker_id` = current_user.id
  - `status` = 'under_review'
- Update `InReviewQueue.assigned_at` = now()
- Update `Case.status` = CaseStatus.CHECKER_REVIEW
- Queue `EmailNotification` (EmailType.CHECKER_ASSIGNED)
- Add `CaseNote` (NoteType.SYSTEM)
- Add to `Logbook` (action_type='assign')

#### Endpoint 2: POST `/approve`
**Purpose**: Approve flag and send to finalizer  
**Auth**: `require_checker`  
**Validation**: Min 15 chars for notes  
**Actions**:
- Update `FlaggedItem`:
  - `status` = 'approved'
  - `checker_notes` = notes
- Move item to `FlaggedItem` table (if not already there)
- Update `Case.status` = CaseStatus.AWAITING_FINAL
- Queue `EmailNotification` (EmailType.APPROVAL_REQUIRED) to finalizer
- Add `CaseNote` (NoteType.STATUS_CHANGE)
- Add to `Logbook` (action_type='approve')

#### Endpoint 3: POST `/recheck`
**Purpose**: Send back to screener for re-review  
**Auth**: `require_checker`  
**Actions**:
- Update `InReviewQueue`:
  - `status` = 'pending'
  - `requires_checker_review` = False
- Update `Case.status` = CaseStatus.IN_REVIEW
- Add `CaseNote` (NoteType.STATUS_CHANGE + recheck reason)
- Queue `EmailNotification` (EmailType.RECHECK_REQUESTED) to screener
- Track `recheck_count` in case metadata
- Add to `Logbook` (action_type='recheck')

---

### 🟠 Task 3.4 - Finalizer Approval Endpoints
**File**: `backend/routes/finalizer.py` (NEW FILE)  
**Base Path**: `/api/review/finalizer`

#### Endpoint 1: POST `/approve`
**Purpose**: Final approval and case closure  
**Auth**: `require_finalizer`  
**Actions**:
- Update `FlaggedItem`:
  - `finalizer_id` = current_user.id
  - `resolution_type` = 'cleared'
  - `resolved_at` = now()
- Update `Case`:
  - `status` = CaseStatus.CLOSED
  - `closed_at` = now()
- Add `CaseNote` (NoteType.DECISION)
- Queue `EmailNotification` (EmailType.CASE_CLOSED) to all participants
- Trigger report generation (optional)
- Add to `Logbook` (action_type='approve')

#### Endpoint 2: POST `/override`
**Purpose**: Override flag decision with justification  
**Auth**: `require_finalizer`  
**Validation**: Min 30 chars for justification  
**Actions**:
- Update `FlaggedItem`:
  - `finalizer_id` = current_user.id
  - `resolution_type` = 'overridden'
  - `resolved_at` = now()
- Update `Case.status` = CaseStatus.CLEARED
- Add `CaseNote` (NoteType.DECISION + justification)
- Queue `EmailNotification` (EmailType.OVERRIDE) to all users
- Add to `Logbook`:
  - `action_type` = 'override'
  - `ip_address` = request IP
  - `user_agent` = request user agent

#### Endpoint 3: POST `/escalate`
**Purpose**: Escalate to compliance team  
**Auth**: `require_finalizer`  
**Actions**:
- Update `FlaggedItem.requires_compliance_approval` = True
- Update `Logbook.requires_escalation` = True
- Add `escalation_notes` to Logbook
- Queue `EmailNotification` (EmailType.ESCALATION)
- Update `Case.status` = CaseStatus.FLAGGED (escalated)

---

### 🟠 Task 3.5 - Workflow Validation
**File**: `backend/utils/workflow.py` (NEW FILE)

#### WorkflowValidator Class
```python
class WorkflowValidator:
    ALLOWED_TRANSITIONS = {
        CaseStatus.OPEN: [CaseStatus.IN_REVIEW],
        CaseStatus.IN_REVIEW: [CaseStatus.FLAGGED, CaseStatus.CLEARED],
        CaseStatus.FLAGGED: [CaseStatus.CHECKER_REVIEW],
        CaseStatus.CHECKER_REVIEW: [CaseStatus.AWAITING_FINAL, CaseStatus.IN_REVIEW],
        CaseStatus.AWAITING_FINAL: [CaseStatus.CLEARED, CaseStatus.CLOSED, CaseStatus.REJECTED]
    }
    
    @staticmethod
    def validate_transition(from_status: CaseStatus, to_status: CaseStatus, user_role: UserRole) -> bool:
        """Validate if status transition is allowed"""
        pass
    
    @staticmethod
    def get_next_allowed_states(current_status: CaseStatus) -> List[CaseStatus]:
        """Get list of valid next states"""
        pass
    
    @staticmethod
    def can_user_perform_action(user: User, action: str, case: Case) -> bool:
        """Check if user has permission for action"""
        pass
```

**Integration**: Use in all workflow endpoints before making status changes

---

### 🟡 Task 3.6 - Update Existing Scan Endpoint
**File**: `backend/routes/scan.py`  
**Endpoint**: POST `/api/scan/run`  
**Changes Needed**:
- Add `current_user: User = Depends(require_screener)` (if not already)
- For each scan:
  - Create `Case` record with auto case_number
  - Link `InReviewQueue` items to case_id
  - Calculate risk_score for each match
  - Add scan_metadata (duration, rows_per_second, memory_used)
- Return case_id along with scan results

---

### 🟡 Task 3.7 - Update Main Application
**File**: `backend/main.py`  
**Changes**:
```python
from routes import auth, scan, review, checker, finalizer

app.include_router(checker.router, prefix="/api/review/checker", tags=["Checker"])
app.include_router(finalizer.router, prefix="/api/review/finalizer", tags=["Finalizer"])
```

---

### 🟡 Task 3.8 - Workflow Test Script
**File**: `backend/test_workflow_phase3.py` (NEW)  
**Test Sequence**:
1. Login as screener
2. Upload blacklist Excel
3. Run scan (creates case)
4. Flag item (updates case)
5. Login as checker
6. Assign to self
7. Approve flag
8. Login as finalizer
9. Final approve (closes case)
10. Verify logbook entries
11. Check email notifications queued

---

## Common Code Patterns

### Creating a Case Note
```python
from models.case import CaseNote, NoteType

note = CaseNote(
    case_id=case.id,
    user_id=current_user.id,
    note="Status changed from 'in_review' to 'checker_review'",
    note_type=NoteType.STATUS_CHANGE
)
db.add(note)
```

### Queueing an Email Notification
```python
from models.notification import EmailNotification, EmailType, EmailStatus
import json

notification = EmailNotification(
    user_id=target_user.id,
    to_email=target_user.email,
    email_type=EmailType.FLAG_CREATED,
    subject=f"New Flag Created - Case {case.case_number}",
    body=f"A new flag has been created for case {case.case_number}. Please review.",
    status=EmailStatus.PENDING,
    email_metadata=json.dumps({
        "case_id": case.id,
        "case_number": case.case_number,
        "priority": case.priority.value
    })
)
db.add(notification)
```

### Adding to Logbook
```python
from models.database import Logbook

log_entry = Logbook(
    case_id=case.id,
    entity_id=item.entity_id,
    entity_type=item.entity_type,
    reviewed_by_id=current_user.id,
    action_type='flag',
    decision='flagged',
    previous_status=case.status.value if case else None,
    new_status=CaseStatus.FLAGGED.value,
    notes=flag_reason,
    time_spent_seconds=0,  # Calculate if tracking time
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent")
)
db.add(log_entry)
```

### Validating User Ownership
```python
if item.screener_id != current_user.id:
    raise HTTPException(
        status_code=403,
        detail="You can only undo items you flagged"
    )
```

### Calculating Risk Score
```python
def calculate_risk_score(match_percentage: float, actor_presence: bool) -> int:
    """Calculate risk score (1-10) based on match percentage and actor presence"""
    base_score = match_percentage / 10  # 0-10 range
    actor_bonus = 3 if actor_presence else 0
    return min(10, int(base_score + actor_bonus))
```

---

## Database Query Examples

### Get User's Assigned Cases (Checker)
```python
from sqlalchemy import and_

cases = db.query(Case).join(FlaggedItem).filter(
    and_(
        FlaggedItem.checker_id == current_user.id,
        Case.status == CaseStatus.CHECKER_REVIEW
    )
).all()
```

### Get Case Timeline
```python
notes = db.query(CaseNote).filter(
    CaseNote.case_id == case_id
).order_by(CaseNote.created_at.asc()).all()

log_entries = db.query(Logbook).filter(
    Logbook.case_id == case_id
).order_by(Logbook.created_at.asc()).all()
```

### Get Pending Email Notifications
```python
from datetime import datetime, timezone

pending_emails = db.query(EmailNotification).filter(
    and_(
        EmailNotification.status == EmailStatus.PENDING,
        or_(
            EmailNotification.next_retry_at.is_(None),
            EmailNotification.next_retry_at <= datetime.now(timezone.utc)
        )
    )
).all()
```

---

## Testing Checklist

### Phase 3 Feature Testing

#### ✅ Authentication
- [ ] Screener can only access screener endpoints
- [ ] Checker can only access checker endpoints
- [ ] Finalizer can only access finalizer endpoints
- [ ] Invalid tokens rejected

#### ✅ Flag Endpoint
- [ ] Creates Case with auto case_number
- [ ] Links InReviewQueue to case
- [ ] Calculates risk_score correctly
- [ ] Queues email notification
- [ ] Adds logbook entry
- [ ] Returns case_number

#### ✅ Undo Endpoint
- [ ] Only owner can undo
- [ ] Cannot undo after checker review
- [ ] Updates case status
- [ ] Adds case note
- [ ] Adds logbook entry

#### ✅ Checker Endpoints
- [ ] Can assign cases to self
- [ ] Can approve flags
- [ ] Can request recheck
- [ ] Email notifications sent
- [ ] Case status updated correctly

#### ✅ Finalizer Endpoints
- [ ] Can approve cases
- [ ] Can override with justification
- [ ] Can escalate to compliance
- [ ] Case closed on approval
- [ ] All users notified

#### ✅ Workflow Validation
- [ ] Invalid status transitions rejected
- [ ] Users cannot perform unauthorized actions
- [ ] Detailed error messages

---

## Priority Order

1. 🔴 **Task 3.1** - Flag endpoint (foundation for workflow)
2. 🔴 **Task 3.2** - Undo endpoint (screener corrections)
3. 🔴 **Task 3.3** - Checker endpoints (middle workflow)
4. 🟠 **Task 3.4** - Finalizer endpoints (close workflow)
5. 🟠 **Task 3.5** - Workflow validation (safety)
6. 🟡 **Task 3.6** - Update scan endpoint (integration)
7. 🟡 **Task 3.7** - Update main.py (routing)
8. 🟡 **Task 3.8** - Test workflow (validation)

---

## Ready to Start Phase 3?

Run this command to verify Phase 2 is ready:
```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/backend
python3 -c "
from database.connection import SessionLocal
from models.auth import User, UserRole
from models.case import Case, CaseStatus

db = SessionLocal()
users = db.query(User).count()
cases = db.query(Case).count()
print(f'✅ Users: {users}')
print(f'✅ Cases: {cases}')
print(f'✅ Ready for Phase 3!')
db.close()
"
```

**Expected Output**:
```
✅ Users: 3
✅ Cases: 2
✅ Ready for Phase 3!
```

---

**Next Command**: Let me know when you're ready to start Phase 3, and I'll begin with Task 3.1 (Flag Endpoint Enhancement)!
