# KAMCO Compliance Screening System - Implementation Guide

## 🎯 System Overview

A comprehensive compliance screening application with role-based authentication, workflow management, and audit trails.

### Key Features:
- ✅ Password-based authentication with JWT
- ✅ Role-based access control (Screener, Checker, Finalizer)
- ✅ Multi-sheet blacklist Excel scanning (including Actor fields)
- ✅ Logbook deduplication (avoid re-reviewing same matches)
- ✅ In Review queue for NEW matches only
- ✅ Flag/Undo workflow with strict confirmation UX
- ✅ Email notifications for scans and re-check requests
- ✅ Per-case and cumulative report generation
- ✅ Checker approval workflow
- ✅ Complete audit logging

---

## 🗄️ Database Schema

### Tables:

1. **users**
   - id, username, email, password_hash, role (screener/checker/finalizer)
   - created_at, last_login

2. **runs**
   - id, run_date, initiated_by (user_id)
   - accounts_scanned, matches_found, new_in_review
   - blacklist_file_hash, kamco_file_hash

3. **logbook** (historical confirmed matches)
   - id, kamco_name, blacklist_name, match_type (client/vendor/staff/tenant/other)
   - actor_name (if applicable), confirmed_date, confirmed_by (user_id)
   - match_score, match_reason

4. **in_review_queue**
   - id, run_id, kamco_name, blacklist_name, match_type
   - actor_name, match_score, match_reason, similarity_score
   - added_date, status (pending/reviewing/flagged/cleared)

5. **flagged_items**
   - id, in_review_id, flagged_by (user_id), flagged_date
   - reason, status (pending_checker/approved/needs_recheck)
   - checker_reviewed_by, checker_reviewed_date, checker_notes

6. **audit_log**
   - id, user_id, action (flag/undo/approve/request_recheck/scan_run/report_generated/report_sent)
   - entity_type, entity_id, timestamp, details (JSON)

7. **reports**
   - id, report_type (case/cumulative/selected), generated_by (user_id)
   - generated_date, file_path, sent_to_emails, entity_ids (JSON)

---

## 🔐 Authentication & Authorization

### Roles & Permissions:

| Action | Screener | Checker | Finalizer |
|--------|----------|---------|-----------|
| View Dashboard | ✅ | ✅ | ❌ (empty) |
| Upload Files | ✅ | ✅ (override) | ❌ |
| Run Scan | ✅ | ✅ (override) | ❌ |
| View Results | ✅ | ✅ | ❌ |
| Flag Items | ✅ | ✅ (override) | ❌ |
| Undo Flag | ✅ | ✅ (override) | ❌ |
| Generate Reports | ✅ | ✅ | ❌ |
| Approve Flags | ❌ | ✅ | ❌ |
| Request Re-check | ❌ | ✅ | ❌ |

### JWT Implementation:
- Login returns JWT token (24h expiry)
- Token contains: userId, username, role
- All protected routes verify JWT + role

---

## 📊 Blacklist Excel Structure

### Required Sheets:
1. **Clients** - with optional "Actor" column
2. **Vendors** - with optional "Actor" column  
3. **Staff**
4. **Tenants**
5. **Others**

### Columns (example):
- Clients: full_name, nationality, dob, actor (optional), source, effective_date
- Vendors: company_name, registration_no, actor (optional), country, source
- Staff/Tenants/Others: name, identifier, source, date

### Actor Field:
- Only in Clients and Vendors sheets
- Contains related party names (e.g., "Power of Attorney: John Smith")
- System extracts and screens Actor names separately
- Match results indicate if match was on primary name or actor

---

## 🔄 Screening Workflow

### Step 1: File Upload
- Screener uploads Kamco dataset (Excel)
- System validates file format and structure
- Stores file hash for run tracking

### Step 2: Scan Execution
1. Parse blacklist Excel (all 5 sheets)
2. Extract Actor names from Clients/Vendors
3. Compare Kamco data vs blacklist names
4. For each match found:
   - Check if exists in Logbook (historical)
   - If YES → skip (already reviewed)
   - If NO → add to In Review queue as NEW
5. Store run metadata
6. Send email notification with results

### Step 3: Review Queue
- Dashboard shows "In Review" tab
- Lists only NEW matches (not in Logbook)
- Filtered by type: All/Clients/Vendors/Staff/Tenants
- Each item shows: name, match details, score, reason

### Step 4: Flag Action
- Screener reviews item and clicks "Flag"
- Enters reason for flagging
- Item moves to "Flagged Items" view
- Immediately shows "UNDO" option
- Logs action to audit trail

### Step 5: Undo Action (Strict UX)
When user clicks Undo:
1. Modal appears with:
   - Checkbox: "I acknowledge I am undoing my action"
   - Text input: Must type EXACTLY "I acknowledge I am undoing my action"
2. Only if BOTH satisfied:
   - Remove from Flagged
   - Re-add to In Review queue
   - Log undo action with timestamp + user

### Step 6: Checker Review
- Checker views all Flagged Items
- For each item, can:
  - **Approve**: Confirms Screener was correct
  - **Request Re-check**: Sends email to Screener, item status = needs_recheck
  - **Override**: Jump into Screener mode to handle directly
- Logs all actions

### Step 7: Report Generation
- **Per-Case Report**: When viewing specific client, generates report for THAT client only
- **Cumulative Report**: Generates report for ALL flagged items
- **Send Report**: Email dropdown (Current Case, Cumulative, Selected Items)

---

## 📧 Email Notifications

### Scan Completion Email:
**To:** Configured email list (env: SCAN_NOTIFICATION_EMAILS)
**Subject:** Kamco Scan Completed - Run #[ID]
**Body:**
```
Scan Run Summary
================
Run ID: [ID]
Timestamp: [DATE TIME]
Initiated By: [USERNAME]

Results:
- Accounts Scanned: [COUNT]
- Total Matches Found: [COUNT]
- NEW In Review: [COUNT]
- Already in Logbook (skipped): [COUNT]

Files:
- Blacklist: [FILENAME] (hash: [HASH])
- Kamco Dataset: [FILENAME] (hash: [HASH])

View results: [LINK TO DASHBOARD]
```

### Re-check Request Email:
**To:** Screener email
**Subject:** Re-check Requested - [CLIENT NAME]
**Body:**
```
Re-check Request
================
Checker: [CHECKER NAME]
Date: [DATE TIME]

Client/Item: [NAME]
Match Type: [TYPE]
Original Flag Reason: [REASON]

Checker Notes:
[NOTES TEXT]

View item: [LINK TO ITEM]
```

---

## 📄 Report Generation

### Per-Case Report (PDF):
```
KAMCO COMPLIANCE SCREENING REPORT
Case Report
==================================

Client Details:
- Name: [NAME]
- Type: [Client/Vendor/Staff/Tenant]
- Match Score: [SCORE]%
- Actor Involved: [YES/NO - NAME]

Blacklist Match:
- Matched Name: [BLACKLIST NAME]
- Source: [SOURCE]
- Effective Date: [DATE]
- Match Reason: [REASON]

Screening Run:
- Run ID: [ID]
- Run Date: [DATE]
- Screened By: [USERNAME]

Flag Details:
- Flagged By: [USERNAME]
- Flagged Date: [DATE]
- Reason: [REASON TEXT]

Checker Review:
- Reviewed By: [USERNAME]
- Review Date: [DATE]
- Status: [Approved/Needs Re-check]
- Notes: [NOTES]

===================================
Generated: [TIMESTAMP]
By: [USERNAME]
```

### Cumulative Report (Excel + PDF):
- All flagged items in table format
- Grouped by type (Clients, Vendors, Staff, Tenants)
- Summary statistics at top
- Export as Excel or PDF

---

## 🎨 Frontend Structure

### Pages:
1. **Login** (`/login`) - Password authentication
2. **Dashboard** (`/dashboard`) - Main landing page (default after login)
3. **Scan Results** (`/dashboard` with tabs)
4. **In Review Queue** (`/in-review`)
5. **Flagged Items** (`/flagged`)
6. **Checker Review** (`/checker`) - Checker-only
7. **Reports** (`/reports`)

### Dashboard Layout:
```
┌─────────────────────────────────────────────────────┐
│ KAMCO Screening System        [Username] [Logout]   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  📊 Dashboard                                        │
│                                                      │
│  ┌─────────────────────────────────────────┐       │
│  │  Upload New Files                       │       │
│  │  [Drag & Drop or Click]                 │       │
│  │  [Run Scan Button]                      │       │
│  └─────────────────────────────────────────┘       │
│                                                      │
│  Tabs: [All] [Clients] [Vendors] [Staff] [Tenants] │
│                                                      │
│  ┌─────────────────────────────────────────┐       │
│  │  In Review Queue (15 new items)         │       │
│  │  ───────────────────────────────────────│       │
│  │  ☐ Ahmad Al-Mansour  [98% match]  [Flag]│       │
│  │  ☐ Sarah Holdings    [92% match]  [Flag]│       │
│  │  ☐ ...                                  │       │
│  └─────────────────────────────────────────┘       │
│                                                      │
│  ┌─────────────────────────────────────────┐       │
│  │  Flagged Items (5 pending review)       │       │
│  │  ───────────────────────────────────────│       │
│  │  🚩 Omar Trading Co  [Generate Report]  │       │
│  │  🚩 Layla Services   [Generate Report]  │       │
│  └─────────────────────────────────────────┘       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Flag Modal (with UNDO):
```
┌─────────────────────────────────────┐
│  Item Flagged Successfully          │
├─────────────────────────────────────┤
│                                     │
│  Ahmad Al-Mansour has been flagged │
│  for Checker review.                │
│                                     │
│  Reason: [Your entered reason]      │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  [UNDO]                     │   │
│  └─────────────────────────────┘   │
│                                     │
│  [ Close ]                          │
└─────────────────────────────────────┘
```

### Undo Confirmation Modal:
```
┌─────────────────────────────────────────────┐
│  Confirm Undo Action                        │
├─────────────────────────────────────────────┤
│                                             │
│  You are about to UNDO the flagging of:    │
│  Ahmad Al-Mansour                           │
│                                             │
│  ☐ I acknowledge I am undoing my action    │
│                                             │
│  Please type the exact phrase below:        │
│  ┌─────────────────────────────────────┐   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│  Required: "I acknowledge I am undoing my   │
│  action"                                    │
│                                             │
│  [ Cancel ]        [ Confirm Undo ]         │
│                      (disabled until valid) │
└─────────────────────────────────────────────┘
```

---

## 🔍 Actor Field Scanning Logic

### Example Blacklist Entry (Clients sheet):
| full_name | nationality | dob | actor | source |
|-----------|-------------|-----|-------|--------|
| Ahmad Holdings | Kuwait | 1980-01-15 | Power of Attorney: Sarah Al-Mansour | World-Check |

### Scanning Process:
1. **Primary Name Check**: Compare "Ahmad Holdings" vs Kamco dataset
2. **Actor Name Check**: Extract "Sarah Al-Mansour" from actor field → compare vs Kamco dataset
3. **Match Result**:
   - If Kamco has "Ahmad Holdings" → Match on primary name
   - If Kamco has "Sarah Al-Mansour" → Match on actor name
   - Match record stores: `actor_match: true, actor_name: "Sarah Al-Mansour"`

### Actor Extraction:
```typescript
function extractActorName(actorField: string): string[] {
  // Examples:
  // "Power of Attorney: John Smith" → ["John Smith"]
  // "POA: Sarah Jones, Trustee: Mike Brown" → ["Sarah Jones", "Mike Brown"]
  // Parse various formats and return array of names
}
```

---

## 🛠️ Environment Variables

Create `.env` file:
```env
# Server
PORT=5001
NODE_ENV=development

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRY=24h

# Database
DATABASE_PATH=./data/kamco.db

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Notification Emails (comma-separated)
SCAN_NOTIFICATION_EMAILS=compliance@kamco.com,screening@kamco.com
SCREENER_EMAIL=screener@kamco.com

# Frontend URL (for links in emails)
FRONTEND_URL=http://localhost:3000
```

---

## 🚀 API Endpoints

### Authentication:
- `POST /api/auth/register` - Create user (admin only)
- `POST /api/auth/login` - Login with password → JWT
- `POST /api/auth/logout` - Invalidate token
- `GET /api/auth/me` - Get current user info

### Screening:
- `POST /api/scan/upload-blacklist` - Upload blacklist Excel
- `POST /api/scan/upload-kamco` - Upload Kamco dataset
- `POST /api/scan/run` - Execute scan
- `GET /api/scan/runs` - List all runs
- `GET /api/scan/runs/:id` - Get run details

### Review Queue:
- `GET /api/review/in-review` - Get In Review queue (with filters)
- `POST /api/review/flag` - Flag an item
- `POST /api/review/undo` - Undo flag action
- `GET /api/review/flagged` - Get flagged items

### Checker:
- `GET /api/checker/flagged` - Get items pending checker review
- `POST /api/checker/approve/:id` - Approve flag
- `POST /api/checker/request-recheck/:id` - Request re-check from Screener

### Reports:
- `POST /api/reports/generate-case/:id` - Generate per-case report
- `POST /api/reports/generate-cumulative` - Generate cumulative report
- `POST /api/reports/send` - Email report
- `GET /api/reports/list` - List generated reports

### Audit:
- `GET /api/audit/logs` - Get audit logs (admin/checker)
- `GET /api/audit/logs/:userId` - Get logs for specific user

---

## 📝 Implementation Checklist

### Phase 1: Foundation
- [x] Install packages
- [ ] Create database schema & migrations
- [ ] Implement User model & auth routes
- [ ] Setup JWT middleware
- [ ] Create role-based access middleware

### Phase 2: Core Screening
- [ ] Multi-sheet blacklist Excel parser
- [ ] Actor field extraction logic
- [ ] Kamco dataset parser
- [ ] Matching algorithm (extend existing)
- [ ] Logbook deduplication
- [ ] In Review queue management

### Phase 3: Workflows
- [ ] Flag/Undo with strict UX
- [ ] Checker review workflow
- [ ] Email notification service
- [ ] Audit logging service

### Phase 4: Reports
- [ ] Per-case PDF generation
- [ ] Cumulative Excel/PDF generation
- [ ] Email report sending

### Phase 5: Frontend
- [ ] Login page
- [ ] Dashboard (main landing)
- [ ] File upload component
- [ ] In Review queue UI
- [ ] Flagged items UI
- [ ] Checker review UI
- [ ] Report generation UI
- [ ] Role-based navigation

---

## 🧪 Testing Scenarios

1. **Screener Login → Upload → Scan**
   - Login as Screener
   - Upload blacklist + Kamco files
   - Run scan
   - Verify email received
   - Check In Review queue has only NEW items

2. **Flag → Undo Workflow**
   - Flag an item with reason
   - Click Undo immediately
   - Verify modal requires checkbox + exact text
   - Confirm undo
   - Verify item back in In Review

3. **Checker Approval**
   - Login as Checker
   - View Flagged Items
   - Approve a flag
   - Verify status updated

4. **Checker Re-check Request**
   - Select flagged item
   - Request re-check with notes
   - Verify email sent to Screener
   - Verify item status = needs_recheck

5. **Actor Matching**
   - Blacklist has client with actor "John Smith"
   - Kamco dataset has "John Smith"
   - Verify match found with actor_match=true

6. **Logbook Deduplication**
   - Run scan #1 → Item A flagged → Add to Logbook
   - Run scan #2 → Item A found again
   - Verify Item A NOT in In Review (already in Logbook)

---

**Ready to implement!** This comprehensive system provides all requested features with proper architecture, security, and workflow management.
