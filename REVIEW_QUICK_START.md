# 🚀 Review System Quick Start Guide

## System Overview

Complete end-to-end review management system for flagged screening matches with:
- ✅ Backend API (FastAPI)
- ✅ Frontend UI (React + TypeScript)
- ✅ Database Models (SQLAlchemy)
- ✅ Email Notifications
- ✅ Complete Audit Trail

---

## 🏃‍♂️ Quick Start (5 minutes)

### 1. Start the Backend
```bash
cd backend
uvicorn main:app --reload
```
**Backend runs on:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```
**Frontend runs on:** http://localhost:5173

### 3. Login
**Default Credentials:**
- Username: `checker_test`
- Password: `password123`

### 4. Navigate to Screening Queue
- Click "Screening Queue" in sidebar
- You should see 12 flagged items ready for review

---

## 📋 Test the System

### ✅ Test 1: Review Single Item

1. Click **"Review"** button on any item
2. Select decision: **Approve**
3. Add notes: `"Match confirmed based on Civil ID and name similarity"`
4. Click **"Submit Review"**
5. ✅ Item should change status to "approved"

### ✅ Test 2: Bulk Review

1. **Check** 3-5 items using checkboxes
2. Click **"Bulk Review"** button
3. Select: **Reject**
4. Add notes: `"All are common name false positives"`
5. Click **"Review X Items"**
6. ✅ All selected items should be rejected

### ✅ Test 3: View Detailed Report

1. Click **eye icon (👁️)** on any item
2. Review all sections:
   - Match Details
   - Kamco Entity
   - Blacklist Entry
   - Review Status
   - Audit Trail
   - Risk Assessment
3. ✅ All information should display correctly

### ✅ Test 4: View Summary Report

1. Click **"Summary Report"** button (top right)
2. Review statistics:
   - Total items
   - Approval/Rejection rates
   - Breakdown by severity
   - Reviewer performance
3. ✅ Statistics should reflect your actions

### ✅ Test 5: Email Report

1. Click **"Email Report"** button (top right)
2. Add recipient: `test@example.com`
3. Check both report types:
   - ✅ Include Executive Summary
   - ✅ Include Individual Item Reports
4. Click **"Send Report"**
5. ✅ Check backend console for email simulation log

### ✅ Test 6: Escalation

1. Click **"Review"** on a high severity item
2. Select: **Escalate**
3. Add review notes: `"High severity match needs verification"`
4. Add escalation reason: `"Complex case with partial Civil ID match. Need senior analyst review."`
5. Click **"Submit Review"**
6. ✅ Item escalated + Admins auto-notified

---

## 🎯 Real Workflow Example

### Scenario: Daily Screening Review

**Morning: 09:00 AM**
1. Login as checker
2. Navigate to Screening Queue
3. See 12 pending items

**Review Process: 09:00 - 10:00 AM**
```
✅ Review Item #1: Approve (exact Civil ID match)
✅ Review Item #2: Approve (name + DOB match)
❌ Review Item #3: Reject (common name, no Civil ID)
❌ Review Item #4: Reject (different person)
⚠️ Review Item #5: Escalate (partial match, needs verification)
```

**Bulk Process: 10:00 - 10:15 AM**
- Select 5 similar false positives
- Bulk reject with note: "Common name variations, no identification matches"

**Reporting: 10:15 AM**
- Generate cumulative report
- Email to compliance team
- Include summary + individual reports

**Result:**
- 12 items processed
- 2 approved, 7 rejected, 1 escalated, 2 pending
- Reports sent to management
- Complete audit trail logged

---

## 📊 Available Reports

### Individual Report (Detailed)
**What it includes:**
- Full match details
- Kamco entity complete info
- Blacklist entry all fields
- Review status and notes
- Complete audit trail
- Risk assessment

**When to use:**
- Need detailed info for specific item
- Investigation required
- Documentation for records
- Legal compliance

**How to access:**
- Click eye icon on any item
- Download as JSON

### Cumulative Report (Summary)
**What it includes:**
- Executive summary (totals, rates)
- Breakdown by severity
- Breakdown by entity type
- Top 10 matches
- Reviewer performance stats

**When to use:**
- Daily/weekly management reports
- Performance monitoring
- Trend analysis
- Compliance reporting

**How to access:**
- Click "Summary Report" button
- Email to multiple recipients

---

## 🔐 User Roles & Permissions

### Screener
- ❌ Cannot review items
- ✅ Can view queue
- ✅ Can view reports

### Checker
- ✅ Can review items (approve/reject/escalate)
- ✅ Can bulk review
- ✅ Can view all reports
- ✅ Can email reports
- ⚠️ Escalated items go to finalizer

### Finalizer
- ✅ All checker permissions
- ✅ Can review escalated items
- ✅ Final decision authority
- ✅ Receives escalation notifications

### Admin
- ✅ All permissions
- ✅ System configuration
- ✅ User management
- ✅ Receives all escalation notifications

---

## 📧 Email Notifications

### Automatic Notifications:

**Escalation Notification** (Auto-sent when item escalated)
- **To:** All admins and finalizers
- **Subject:** "🚨 Item Escalated for Review"
- **Includes:**
  - Item details
  - Match score & severity
  - Escalation reason
  - Link to review

**Manual Reports** (User-initiated)
- **To:** User-specified recipients
- **Subject:** "Kamco Screening Report - [Date]"
- **Includes:**
  - Executive summary (optional)
  - Individual reports (optional)
  - Statistics grid
  - Breakdown tables

---

## 🛠️ Troubleshooting

### ❌ "No matches found"
**Solution:** Upload test data
```bash
# Use the ScreeningQueuePage upload button
# Upload: test_data/blacklist_with_matches.csv
# Should create 12 matches
```

### ❌ "Review button disabled"
**Reason:** Item already reviewed (status not "pending")
**Solution:** Only pending items can be reviewed

### ❌ "Bulk review not working"
**Check:**
1. Are items selected? (checkboxes checked)
2. Are any selected items already reviewed?
3. Is backend running?

### ❌ "Email not sending"
**Check:**
1. Is SMTP configured? (backend/utils/email_service.py)
2. Are recipients valid email addresses?
3. Check backend logs for errors

### ❌ "API errors (401/403)"
**Solution:**
1. Ensure you're logged in
2. Check token hasn't expired
3. Verify user has correct role

---

## 🎨 UI Components Reference

### Buttons
| Button | Icon | Action |
|--------|------|--------|
| Review | - | Open review modal |
| 👁️ (Eye) | Eye | View detailed report |
| Summary Report | BarChart3 | Open cumulative report |
| Email Report | Mail | Open email modal |
| Bulk Review | CheckSquare | Review multiple items |

### Status Badges
| Status | Color | Icon | Meaning |
|--------|-------|------|---------|
| Pending | Gray | Clock | Awaiting review |
| Approved | Green | CheckCircle | Match confirmed |
| Rejected | Red | FileText | False positive |
| Escalated | Orange | AlertTriangle | Needs senior review |

### Severity Badges
| Severity | Color | When Used |
|----------|-------|-----------|
| Critical | Red | 95-100% match |
| High | Orange | 85-94% match |
| Medium | Yellow | 75-84% match |
| Low | Blue | 70-74% match |

---

## 📝 Best Practices

### ✅ DO:
- Always add detailed notes (required)
- Review items individually when uncertain
- Use bulk review for obvious false positives
- Escalate complex cases
- Regular reporting to management
- Check audit trail when needed

### ❌ DON'T:
- Bulk approve without verification
- Skip adding notes
- Ignore high severity items
- Forget to check Civil ID matches
- Process items too quickly

---

## 📞 Support & Documentation

### Documentation Files:
- **Backend API:** `REVIEW_SYSTEM_GUIDE.md`
- **Frontend UI:** `FRONTEND_REVIEW_SYSTEM.md`
- **This Guide:** `REVIEW_QUICK_START.md`

### API Documentation:
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Contact:
- **Technical Support:** Kamco IT Team
- **Compliance Questions:** Compliance Department

---

## 🎉 You're Ready!

The review management system is now fully operational. Start by:

1. ✅ Reviewing a few items individually
2. ✅ Testing bulk review
3. ✅ Generating a report
4. ✅ Sending an email

**Happy Reviewing! 🚀**

---

**Last Updated:** January 8, 2026
**Version:** 1.0.0
**Status:** Production Ready ✅
