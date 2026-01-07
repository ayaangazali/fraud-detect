# Sample Data Guide - Kamco Fraud Detection System

## 📋 Overview
This guide shows you exactly what data to send to each endpoint and what gets stored in the database.

---

## 🔐 Phase 1: Authentication

### 1. Register a User
**Endpoint:** `POST /auth/register`

**Sample Input:**
```json
{
  "email": "screener1@kamco.com",
  "password": "SecurePass123!",
  "username": "screener_john",
  "full_name": "John Smith",
  "role": "screener"
}
```

**What Gets Stored in `users` table:**
| Field | Value | Notes |
|-------|-------|-------|
| id | 1 (auto) | Primary key |
| email | screener1@kamco.com | Unique |
| username | screener_john | Unique |
| full_name | John Smith | Display name |
| role | screener | enum: screener/checker/finalizer |
| hashed_password | $2b$12$... | Bcrypt hash |
| is_active | true | Account status |
| created_at | 2026-01-07 10:30:00 | Timestamp |
| updated_at | 2026-01-07 10:30:00 | Timestamp |

---

### 2. Login
**Endpoint:** `POST /auth/login`

**Sample Input:**
```json
{
  "email": "screener1@kamco.com",
  "password": "SecurePass123!"
}
```

**Response (save this token!):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "screener1@kamco.com",
    "username": "screener_john",
    "full_name": "John Smith",
    "role": "screener"
  }
}
```

**Use token in all subsequent requests:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📤 Phase 2: Document Scanning

### 3. Upload Document for Scanning
**Endpoint:** `POST /scan/upload`

**Sample Input (multipart/form-data):**
```
file: [Select PDF/Image file]
document_type: "invoice"
customer_name: "ABC Corporation"
transaction_amount: 50000.00
```

**What Gets Stored in `flagged_items` table:**
| Field | Value | Notes |
|-------|-------|-------|
| id | 1 (auto) | Primary key |
| file_path | uploads/invoice_abc_20260107.pdf | Stored location |
| file_name | invoice_abc_20260107.pdf | Original name |
| document_type | invoice | Type of document |
| customer_name | ABC Corporation | From form |
| transaction_amount | 50000.00 | From form |
| flag_reason | Document uploaded for review | Auto-generated |
| risk_score | 0.00 | Initially 0 |
| status | pending | Initial status |
| flagged_at | 2026-01-07 10:35:00 | Upload timestamp |
| created_at | 2026-01-07 10:35:00 | Creation timestamp |

**Response:**
```json
{
  "id": 1,
  "file_name": "invoice_abc_20260107.pdf",
  "document_type": "invoice",
  "customer_name": "ABC Corporation",
  "transaction_amount": 50000.0,
  "status": "pending",
  "message": "Document uploaded successfully and queued for scanning"
}
```

---

### 4. Run OCR Scan
**Endpoint:** `POST /scan/ocr/{item_id}`

**Sample Input:**
```
URL: /scan/ocr/1
Headers: Authorization: Bearer <token>
Body: (none needed)
```

**What Gets Updated in `flagged_items`:**
| Field | Before | After |
|-------|--------|-------|
| extracted_text | NULL | "INVOICE\nABC Corporation\nAmount: $50,000..." |
| risk_score | 0.00 | 45.5 |
| flag_reason | Document uploaded... | Multiple formatting inconsistencies detected |
| status | pending | flagged |
| flagged_at | 2026-01-07 10:35:00 | 2026-01-07 10:40:00 |

**What Gets Created in `logbook`:**
| Field | Value |
|-------|-------|
| id | 1 (auto) |
| flagged_item_id | 1 |
| action | scan_completed |
| performed_by | system |
| details | OCR scan completed. Risk score: 45.5 |
| timestamp | 2026-01-07 10:40:00 |

---

## 🔍 Phase 3: Review Workflow

### 5. Screener: Escalate to Review
**Endpoint:** `POST /review/escalate/{item_id}`

**Sample Input:**
```json
{
  "notes": "Suspicious invoice formatting and amount discrepancies detected",
  "priority": "high"
}
```

**What Gets Created in `cases` table:**
| Field | Value |
|-------|-------|
| id | 1 (auto) |
| case_number | CASE-2026-0001 |
| flagged_item_id | 1 |
| status | open |
| priority | high |
| assigned_to | NULL |
| opened_by | 1 (screener's user_id) |
| opened_at | 2026-01-07 10:45:00 |

**What Gets Created in `case_notes` table:**
| Field | Value |
|-------|-------|
| id | 1 (auto) |
| case_id | 1 |
| user_id | 1 (screener) |
| note_type | escalation |
| content | Suspicious invoice formatting and amount discrepancies detected |
| created_at | 2026-01-07 10:45:00 |

**What Gets Updated in `flagged_items`:**
| Field | Before | After |
|-------|--------|-------|
| status | flagged | in_review |
| case_id | NULL | 1 |

**What Gets Created in `in_review_queue`:**
| Field | Value |
|-------|-------|
| id | 1 (auto) |
| case_id | 1 |
| flagged_item_id | 1 |
| current_stage | checker_review |
| priority | high |
| assigned_checker_id | NULL |
| assigned_finalizer_id | NULL |
| entered_queue_at | 2026-01-07 10:45:00 |

**Logbook Entry Created:**
```
action: escalated_to_review
performed_by: screener_john
details: Case CASE-2026-0001 created with high priority
```

---

### 6. Checker: Assign Case to Self
**Endpoint:** `POST /checker/assign/{item_id}`

**Sample Input:**
```
URL: /checker/assign/1
Headers: Authorization: Bearer <checker_token>
Body: (none)
```

**What Gets Updated in `in_review_queue`:**
| Field | Before | After |
|-------|--------|-------|
| assigned_checker_id | NULL | 2 (checker's user_id) |
| checker_assigned_at | NULL | 2026-01-07 11:00:00 |

**What Gets Updated in `flagged_items`:**
| Field | Before | After |
|-------|--------|-------|
| checker_id | NULL | 2 |
| checker_assigned_at | NULL | 2026-01-07 11:00:00 |
| status | in_review | checker_review |

**What Gets Updated in `cases`:**
| Field | Before | After |
|-------|--------|-------|
| assigned_to | NULL | 2 (checker) |
| status | open | in_review |

---

### 7. Checker: Approve Item
**Endpoint:** `POST /checker/approve/{item_id}`

**Sample Input:**
```json
{
  "notes": "After thorough review, discrepancies are within acceptable tolerance. Document appears legitimate.",
  "recommend_close": false
}
```

**What Gets Updated in `flagged_items`:**
| Field | Before | After |
|-------|--------|-------|
| checker_notes | NULL | After thorough review, discrepancies... |
| checker_reviewed_at | NULL | 2026-01-07 11:30:00 |
| status | checker_review | finalizer_review |

**What Gets Updated in `in_review_queue`:**
| Field | Before | After |
|-------|--------|-------|
| current_stage | checker_review | finalizer_review |
| checker_reviewed_at | NULL | 2026-01-07 11:30:00 |
| checker_decision | NULL | approved |

**What Gets Created in `case_notes`:**
```
note_type: review
content: Checker approved: After thorough review, discrepancies are within acceptable tolerance...
user_id: 2 (checker)
```

---

### 8. Finalizer: Assign Case
**Endpoint:** `POST /finalizer/assign/{item_id}`

**Sample Input:**
```
URL: /finalizer/assign/1
Headers: Authorization: Bearer <finalizer_token>
Body: (none)
```

**What Gets Updated in `in_review_queue`:**
| Field | Before | After |
|-------|--------|-------|
| assigned_finalizer_id | NULL | 3 (finalizer's user_id) |
| finalizer_assigned_at | NULL | 2026-01-07 12:00:00 |

**What Gets Updated in `flagged_items`:**
| Field | Before | After |
|-------|--------|-------|
| finalizer_id | NULL | 3 |

---

### 9. Finalizer: Approve and Close
**Endpoint:** `POST /finalizer/approve/{item_id}`

**Sample Input:**
```json
{
  "notes": "Final review complete. Document verified as legitimate. Closing case.",
  "close_case": true
}
```

**What Gets Updated in `flagged_items`:**
| Field | Before | After |
|-------|--------|-------|
| finalizer_notes | NULL | Final review complete. Document verified... |
| finalizer_reviewed_at | NULL | 2026-01-07 12:30:00 |
| resolution_date | NULL | 2026-01-07 12:30:00 |
| status | finalizer_review | approved |

**What Gets Updated in `cases`:**
| Field | Before | After |
|-------|--------|-------|
| status | in_review | closed |
| resolution | approved | 
| closed_at | NULL | 2026-01-07 12:30:00 |
| closed_by | 3 (finalizer) |

**What Gets Updated in `in_review_queue`:**
| Field | Before | After |
|-------|--------|-------|
| finalizer_reviewed_at | NULL | 2026-01-07 12:30:00 |
| finalizer_decision | NULL | approved |
| completed_at | NULL | 2026-01-07 12:30:00 |

---

## 🚨 Alternative Flow: Rejection

### 10. Checker: Request Recheck
**Endpoint:** `POST /checker/recheck/{item_id}`

**Sample Input:**
```json
{
  "notes": "Document has suspicious signatures. Need verification from original source.",
  "new_priority": "urgent"
}
```

**What Gets Updated:**
- `flagged_items.status`: checker_review → pending_recheck
- `cases.priority`: high → urgent
- `in_review_queue.current_stage`: checker_review → pending_recheck
- New case note created with recheck request

---

### 11. Finalizer: Override and Reject
**Endpoint:** `POST /finalizer/override/{item_id}`

**Sample Input:**
```json
{
  "notes": "Evidence of document forgery detected. Rejecting despite checker approval.",
  "new_decision": "rejected",
  "close_case": true
}
```

**What Gets Updated:**
- `flagged_items.status`: finalizer_review → rejected
- `flagged_items.finalizer_notes`: Updated with override reason
- `cases.status`: in_review → closed
- `cases.resolution`: rejected
- Override logged in case_notes and logbook

---

### 12. Finalizer: Escalate to Management
**Endpoint:** `POST /finalizer/escalate/{item_id}`

**Sample Input:**
```json
{
  "notes": "Case involves high-value transaction with legal implications. Requires executive review.",
  "escalation_level": "executive",
  "new_priority": "critical"
}
```

**What Gets Updated in `flagged_items`:**
| Field | Before | After |
|-------|--------|-------|
| escalation_level | NULL | executive |
| status | finalizer_review | escalated |

**What Gets Updated in `cases`:**
| Field | Before | After |
|-------|--------|-------|
| priority | high | critical |
| status | in_review | escalated |

**What Gets Created in `email_notifications`:**
| Field | Value |
|-------|-------|
| id | 1 (auto) |
| case_id | 1 |
| recipient_email | executives@kamco.com |
| subject | URGENT: Case CASE-2026-0001 Escalated to Executive Level |
| body | Case involves high-value transaction with legal implications... |
| status | pending |
| created_at | 2026-01-07 13:00:00 |

---

## 📊 Database Schema Summary

### Main Tables and Their Relationships

```
users (Authentication)
  ↓
flagged_items (Documents)
  ↓
cases (Case Management)
  ↓
in_review_queue (Workflow)
  ↓
case_notes (Audit Trail)
  ↓
logbook (System Logs)
  ↓
email_notifications (Alerts)
```

### Key Relationships

1. **User → FlaggedItem**: screener_id, checker_id, finalizer_id
2. **FlaggedItem → Case**: case_id (one-to-one when escalated)
3. **Case → InReviewQueue**: case_id (one-to-one)
4. **Case → CaseNotes**: case_id (one-to-many)
5. **FlaggedItem → Logbook**: flagged_item_id (one-to-many)

---

## 🔧 How to Check Data in Backend

### Option 1: SQLite Browser
```bash
# Install SQLite browser
brew install sqlitebrowser  # macOS

# Open database
sqlitebrowser backend/fraud_detection.db
```

### Option 2: Command Line
```bash
cd backend
sqlite3 fraud_detection.db

# View all tables
.tables

# Check users
SELECT * FROM users;

# Check flagged items
SELECT id, file_name, status, risk_score FROM flagged_items;

# Check cases
SELECT case_number, status, priority FROM cases;

# Check review queue
SELECT case_id, current_stage, checker_decision FROM in_review_queue;

# Exit
.quit
```

### Option 3: Python Script
```python
# Run this in backend directory
python3 -c "
from models.database import SessionLocal, FlaggedItem, Case, InReviewQueue
from models.auth import User

db = SessionLocal()

print('=== USERS ===')
for user in db.query(User).all():
    print(f'{user.id}: {user.username} ({user.role})')

print('\n=== FLAGGED ITEMS ===')
for item in db.query(FlaggedItem).all():
    print(f'{item.id}: {item.file_name} - Status: {item.status}')

print('\n=== CASES ===')
for case in db.query(Case).all():
    print(f'{case.case_number}: {case.status} (Priority: {case.priority})')

print('\n=== REVIEW QUEUE ===')
for queue in db.query(InReviewQueue).all():
    print(f'Case {queue.case_id}: {queue.current_stage}')

db.close()
"
```

---

## 🧪 Complete Test Scenario

### Step-by-Step Test Flow

1. **Register 3 Users** (screener, checker, finalizer)
2. **Login as Screener** → Get token
3. **Upload Document** → Get item_id
4. **Run OCR Scan** → Document flagged with risk score
5. **Escalate to Review** → Case created
6. **Login as Checker** → Get checker token
7. **Assign Case** → Checker assigned
8. **Approve Case** → Moves to finalizer
9. **Login as Finalizer** → Get finalizer token
10. **Assign Case** → Finalizer assigned
11. **Approve & Close** → Case closed

### Expected Final State

**flagged_items:**
```
status: approved
checker_id: 2
finalizer_id: 3
case_id: 1
```

**cases:**
```
case_number: CASE-2026-0001
status: closed
resolution: approved
```

**in_review_queue:**
```
current_stage: finalizer_review
checker_decision: approved
finalizer_decision: approved
completed_at: <timestamp>
```

---

## 📝 Quick Reference: All Sample Inputs

### Authentication
```json
// Register
POST /auth/register
{"email": "user@kamco.com", "password": "Pass123!", "username": "john_doe", "full_name": "John Doe", "role": "screener"}

// Login
POST /auth/login
{"email": "user@kamco.com", "password": "Pass123!"}
```

### Scanning
```json
// Upload
POST /scan/upload
multipart: {file, document_type, customer_name, transaction_amount}

// OCR
POST /scan/ocr/1
(no body)
```

### Review Workflow
```json
// Escalate
POST /review/escalate/1
{"notes": "Issue description", "priority": "high"}

// Checker Assign
POST /checker/assign/1
(no body)

// Checker Approve
POST /checker/approve/1
{"notes": "Review notes", "recommend_close": false}

// Checker Recheck
POST /checker/recheck/1
{"notes": "Reason for recheck", "new_priority": "urgent"}

// Finalizer Assign
POST /finalizer/assign/1
(no body)

// Finalizer Approve
POST /finalizer/approve/1
{"notes": "Final decision", "close_case": true}

// Finalizer Override
POST /finalizer/override/1
{"notes": "Override reason", "new_decision": "rejected", "close_case": true}

// Finalizer Escalate
POST /finalizer/escalate/1
{"notes": "Escalation reason", "escalation_level": "executive", "new_priority": "critical"}
```

---

## 🎯 Status Flow Chart

```
pending → flagged → in_review → checker_review → finalizer_review → approved/rejected
                         ↓              ↓                ↓
                    escalated    pending_recheck    escalated
```

---

## ✅ Verification Checklist

- [ ] User registered successfully
- [ ] User can login and receive token
- [ ] Document uploads to `/uploads` folder
- [ ] OCR extracts text and updates risk_score
- [ ] Case number follows CASE-YYYY-NNNN format
- [ ] Checker can only assign unassigned cases
- [ ] Finalizer only sees checker-approved cases
- [ ] Status transitions follow workflow rules
- [ ] All actions logged in logbook
- [ ] Case notes created for each review step
- [ ] Email notifications created for escalations

