# 📋 Review Management System - Complete Guide

## Overview
Comprehensive review system for managing flagged items with notes, reports, and email notifications.

---

## 🎯 API Endpoints

### Base URL: `/api/reviews`

### 1. Review Single Item
**POST** `/review/{item_id}`

Review a flagged item with decision and notes.

**Request Body:**
```json
{
  "decision": "approved",  // or "rejected", "escalated"
  "notes": "Confirmed match - entity is on sanctions list",
  "requires_escalation": false,
  "escalation_notes": null
}
```

**Response:**
```json
{
  "success": true,
  "message": "Item approved",
  "data": {
    "id": 1,
    "status": "approved",
    "reviewed_at": "2026-01-08T10:30:00",
    ...
  }
}
```

**Decisions:**
- `approved`: Confirm the flag (entity is truly a match)
- `rejected`: Clear the flag (false positive)
- `escalated`: Needs higher-level review

---

### 2. Bulk Review
**POST** `/review/bulk`

Review multiple items at once with the same decision.

**Request Body:**
```json
{
  "item_ids": [1, 2, 3, 4],
  "decision": "approved",
  "notes": "Bulk approval - all matches confirmed"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Reviewed 4 items",
  "data": {
    "updated_count": 4,
    "errors": []
  }
}
```

---

### 3. Get Item Report
**GET** `/report/item/{item_id}`

Get detailed report for a single flagged item.

**Response:**
```json
{
  "success": true,
  "data": {
    "item_id": 1,
    "report_generated_at": "2026-01-08T10:30:00",
    "generated_by": "john.doe",
    
    "match_details": {
      "kamco_name": "Mohammed Al-Rashid",
      "kamco_type": "clients",
      "blacklist_name": "Mohammed Al-Rashid",
      "match_score": 100.0,
      "severity": "high"
    },
    
    "kamco_entity": {
      "name": "Mohammed Al-Rashid",
      "type": "clients",
      "account_number": "ACC-2024-001",
      "date_opened": "2024-01-15",
      "country": "Kuwait"
    },
    
    "blacklist_details": {
      "name_english": "Mohammed Al-Rashid",
      "name_arabic": "محمد الراشد",
      "source": "UN Sanctions List",
      "civil_id": "287654321001",
      "nationality": "Kuwaiti",
      "notes": "High-risk individual"
    },
    
    "review_status": {
      "status": "pending",
      "flagged_at": "2026-01-08T09:00:00",
      "flagged_by": "system",
      "flag_reason": "Auto-flagged: Name match 100.0%",
      "checker_notes": null
    },
    
    "audit_trail": [
      {
        "action": "flag",
        "decision": null,
        "notes": "Auto-flagged",
        "reviewed_at": "2026-01-08T09:00:00"
      }
    ],
    
    "risk_assessment": {
      "match_score_level": "Exact Match",
      "severity": "high",
      "recommended_action": "Immediate review and escalation recommended"
    }
  }
}
```

---

### 4. Get Cumulative Report
**GET** `/report/cumulative`

Get summary report of all flagged items with statistics.

**Query Parameters:**
- `status` (optional): Filter by status (pending, approved, rejected, escalated)
- `severity` (optional): Filter by severity (low, medium, high, critical)
- `start_date` (optional): Start date filter (ISO format)
- `end_date` (optional): End date filter (ISO format)

**Response:**
```json
{
  "success": true,
  "data": {
    "report_generated_at": "2026-01-08T10:30:00",
    "generated_by": "john.doe",
    
    "summary": {
      "total_flagged_items": 12,
      "total_approved": 8,
      "total_rejected": 2,
      "total_pending": 2,
      "total_escalated": 0,
      "approval_rate": 66.67,
      "rejection_rate": 16.67
    },
    
    "breakdowns": {
      "by_status": {
        "approved": 8,
        "rejected": 2,
        "pending": 2
      },
      "by_severity": {
        "high": 9,
        "medium": 2,
        "low": 1
      },
      "by_entity_type": {
        "clients": 6,
        "vendors": 2,
        "staff": 3,
        "others": 1
      },
      "by_match_confidence": {
        "high": 9,
        "medium": 2,
        "low": 1
      }
    },
    
    "reviewer_stats": [
      {
        "reviewer_id": 2,
        "reviewer_name": "john.doe",
        "items_reviewed": 10
      }
    ],
    
    "top_matches": [
      {
        "id": 1,
        "kamco_name": "Mohammed Al-Rashid",
        "blacklist_name": "Mohammed Al-Rashid",
        "match_score": 100.0,
        "severity": "high",
        "status": "approved"
      }
    ],
    
    "items": [...]  // All items (summary)
  }
}
```

---

### 5. Email Report
**POST** `/email/report`

Email reports to specified recipients.

**Request Body:**
```json
{
  "item_ids": [1, 2, 3],  // Optional: specific items, or null for all
  "recipients": [
    "compliance@kamcoinvest.com",
    "management@kamcoinvest.com"
  ],
  "include_summary": true,
  "include_individual_reports": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Report emailed to 2 recipients",
  "data": {
    "recipients": [
      "compliance@kamcoinvest.com",
      "management@kamcoinvest.com"
    ],
    "items_included": 12,
    "timestamp": "2026-01-08T10:30:00"
  }
}
```

---

## 📧 Email Notifications

### 1. Escalation Notification
Automatically sent when an item is escalated.

**Recipients:** All users with `admin` or `finalizer` role

**Content:**
- Item details
- Match information
- Escalation reason
- Reviewer information

### 2. Screening Report
Sent manually via `/email/report` endpoint.

**Content:**
- Executive summary with statistics
- Status and severity breakdowns
- Individual item details (up to 10 items)
- Reviewer performance metrics

---

## 🔄 Workflow Example

### Complete Review Workflow:

1. **Upload Blacklist File** → Auto-screening runs → Items flagged
2. **Review Flagged Items**:
   ```bash
   POST /api/reviews/review/1
   {
     "decision": "approved",
     "notes": "Verified match against UN sanctions list"
   }
   ```
3. **Generate Reports**:
   ```bash
   GET /api/reviews/report/cumulative
   ```
4. **Email Reports to Team**:
   ```bash
   POST /api/reviews/email/report
   {
     "recipients": ["compliance@kamcoinvest.com"],
     "include_summary": true,
     "include_individual_reports": true
   }
   ```

---

## 📊 Report Types

### Individual Item Report
- **Purpose:** Detailed review of single flagged item
- **Contains:**
  - Match details and scores
  - Kamco entity full information
  - Blacklist entry complete details
  - Review status and notes
  - Complete audit trail
  - Risk assessment and recommendations

### Cumulative Report
- **Purpose:** Overview of all screening activities
- **Contains:**
  - Executive summary statistics
  - Status/severity/type breakdowns
  - Reviewer performance metrics
  - Top matches list
  - All items summary

---

## 🎯 Use Cases

### 1. Daily Review Process
```bash
# 1. Get pending items
GET /api/screening/queue

# 2. Review each item
POST /api/reviews/review/{item_id}
{
  "decision": "approved",
  "notes": "Match confirmed"
}

# 3. Generate daily report
GET /api/reviews/report/cumulative?status=pending

# 4. Email to management
POST /api/reviews/email/report
{
  "recipients": ["management@kamcoinvest.com"],
  "include_summary": true
}
```

### 2. Bulk Approval
```bash
# Review multiple low-risk items at once
POST /api/reviews/review/bulk
{
  "item_ids": [10, 11, 12, 13],
  "decision": "rejected",
  "notes": "Low match scores - false positives"
}
```

### 3. Escalation Workflow
```bash
# Escalate high-risk item
POST /api/reviews/review/5
{
  "decision": "escalated",
  "notes": "Requires senior management approval",
  "requires_escalation": true,
  "escalation_notes": "Match involves high-value client with complex profile"
}

# Email automatically sent to admins/finalizers
```

### 4. Monthly Compliance Report
```bash
# Generate monthly report
GET /api/reviews/report/cumulative?start_date=2026-01-01&end_date=2026-01-31

# Email to compliance team
POST /api/reviews/email/report
{
  "recipients": [
    "compliance@kamcoinvest.com",
    "audit@kamcoinvest.com",
    "legal@kamcoinvest.com"
  ],
  "include_summary": true,
  "include_individual_reports": false  // Just summary for monthly
}
```

---

## 🔐 Authentication
All endpoints require authentication with Bearer token:

```
Authorization: Bearer <access_token>
```

---

## 📝 Notes Best Practices

### Good Notes Examples:
- ✅ "Confirmed match - entity appears on UN Sanctions List under same civil ID"
- ✅ "False positive - different person with similar name, different nationality"
- ✅ "Escalating for legal review - complex case involving multiple jurisdictions"

### Poor Notes Examples:
- ❌ "OK"
- ❌ "Approved"
- ❌ "Match"

**Recommendation:** Include specific reasons, sources checked, and any relevant details.

---

## 🚀 Quick Start

1. **Review an item:**
   ```bash
   curl -X POST http://localhost:8000/api/reviews/review/1 \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"decision":"approved","notes":"Match confirmed"}'
   ```

2. **Get cumulative report:**
   ```bash
   curl http://localhost:8000/api/reviews/report/cumulative \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **Email report:**
   ```bash
   curl -X POST http://localhost:8000/api/reviews/email/report \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "recipients": ["compliance@kamcoinvest.com"],
       "include_summary": true,
       "include_individual_reports": true
     }'
   ```

---

## ✅ System Status

- ✅ Review API endpoints implemented
- ✅ Individual item reports with full details
- ✅ Cumulative reports with statistics
- ✅ Email notifications for escalations
- ✅ Bulk review functionality
- ✅ Audit trail tracking
- ✅ Risk assessment recommendations
- ✅ Multi-recipient email support

---

## 📧 Email Configuration

Emails are logged to file by default. To enable SMTP:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@kamcoinvest.com
```

---

## 🎉 You're All Set!

The complete review management system is ready to use. You can now:
1. Review flagged items with detailed notes
2. Generate individual and cumulative reports
3. Email reports to compliance teams
4. Track all actions in audit logs
5. Escalate high-risk items to management

Happy screening! 🚀
