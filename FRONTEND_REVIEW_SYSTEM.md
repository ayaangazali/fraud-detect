# Frontend Review System Documentation

## Overview

The frontend review management system provides a complete interface for reviewing flagged screening matches. It integrates with the backend review API to enable:

- Individual item reviews with decision making
- Bulk review of multiple items
- Detailed item reports
- Cumulative statistics and analytics
- Email report distribution

## Components

### 1. ReviewModal

**Location:** `/frontend/src/components/review/ReviewModal.tsx`

**Purpose:** Modal for reviewing individual flagged items with decision making and notes.

**Features:**
- ✅ Three decision types: Approve, Reject, Escalate
- ✅ Required review notes field
- ✅ Escalation reason field (when escalating)
- ✅ Visual severity indicators
- ✅ Match score display
- ✅ Decision guidance for reviewers
- ✅ Real-time form validation

**Usage:**
```tsx
<ReviewModal
  isOpen={reviewModalOpen}
  onClose={() => setReviewModalOpen(false)}
  item={selectedItem}
  onReviewComplete={handleRefresh}
/>
```

**Decision Types:**
- **Approve**: Confirm the match is valid (turns green)
- **Reject**: Mark as false positive (turns red)
- **Escalate**: Send to finalizer for senior review (turns orange)

**API Integration:**
- POST `/api/reviews/review/{item_id}`
- Payload: `{ decision, notes, escalate_to_finalizer?, escalation_notes? }`

---

### 2. BulkReviewModal

**Location:** `/frontend/src/components/review/BulkReviewModal.tsx`

**Purpose:** Modal for applying the same decision to multiple flagged items.

**Features:**
- ✅ Approve or reject multiple items at once
- ✅ Single notes field applied to all
- ✅ Warning message about bulk actions
- ✅ Summary of affected items
- ✅ No escalation option (must review individually)

**Usage:**
```tsx
<BulkReviewModal
  isOpen={bulkReviewModalOpen}
  onClose={() => setBulkReviewModalOpen(false)}
  selectedItems={[1, 2, 3, 4]}
  onReviewComplete={handleRefresh}
/>
```

**API Integration:**
- POST `/api/reviews/review/bulk`
- Payload: `{ item_ids: number[], decision, notes }`

**Limitations:**
- No escalation option (requires individual review)
- Same decision applied to all selected items

---

### 3. ItemDetailReport

**Location:** `/frontend/src/components/review/ItemDetailReport.tsx`

**Purpose:** Display comprehensive details about a specific flagged item.

**Features:**
- ✅ Match details with severity and score
- ✅ Complete Kamco entity information
- ✅ Full blacklist entry details
- ✅ Review status and notes
- ✅ Complete audit trail
- ✅ Risk assessment with recommended actions
- ✅ Download report as JSON

**Sections:**
1. **Match Details**: Score, type, severity, who flagged, when flagged
2. **Kamco Entity**: Name, type, Civil ID, all additional fields
3. **Blacklist Entry**: English/Arabic names, Civil ID, decree info
4. **Review Status**: Current status, reviewer, notes from checker/finalizer
5. **Risk Assessment**: Risk level, recommended action, risk factors
6. **Audit Trail**: Complete history of all actions

**Usage:**
```tsx
<ItemDetailReport
  isOpen={detailReportModalOpen}
  onClose={() => setDetailReportModalOpen(false)}
  itemId={12}
/>
```

**API Integration:**
- GET `/api/reviews/report/item/{item_id}`
- Returns full detailed report object

---

### 4. CumulativeReport

**Location:** `/frontend/src/components/review/CumulativeReport.tsx`

**Purpose:** Display aggregate statistics and analytics across all flagged items.

**Features:**
- ✅ Executive summary dashboard
- ✅ Breakdown by severity (Critical/High/Medium/Low)
- ✅ Breakdown by entity type (Client/Vendor/Staff/Other)
- ✅ Top matches list
- ✅ Reviewer performance statistics
- ✅ Approval/Rejection rates
- ✅ Download report as JSON
- ✅ Quick access to email report

**Metrics Displayed:**
- Total items flagged
- Pending, Approved, Rejected, Escalated counts
- Approval rate percentage
- Rejection rate percentage
- Distribution by severity level
- Distribution by entity type
- Top 10 highest matches
- Per-reviewer statistics (reviewed, approved, rejected, escalated)

**Usage:**
```tsx
<CumulativeReport
  isOpen={cumulativeReportModalOpen}
  onClose={() => setCumulativeReportModalOpen(false)}
  onEmailReport={() => openEmailModal()}
/>
```

**API Integration:**
- GET `/api/reviews/report/cumulative`
- Returns aggregated statistics

---

### 5. EmailReportModal

**Location:** `/frontend/src/components/review/EmailReportModal.tsx`

**Purpose:** Send screening reports via email to compliance and management teams.

**Features:**
- ✅ Multiple recipient management
- ✅ Quick add recipient groups (Compliance, Risk, Management)
- ✅ Email validation
- ✅ Choose report contents:
  - Executive summary
  - Individual item reports
  - Both
- ✅ Email preview before sending
- ✅ Predefined recipient groups

**Recipient Groups:**
- **Compliance Team**: `compliance@kamcoinvest.com`
- **Risk Management**: `risk@kamcoinvest.com`
- **Management**: `management@kamcoinvest.com`

**Usage:**
```tsx
<EmailReportModal
  isOpen={emailModalOpen}
  onClose={() => setEmailModalOpen(false)}
/>
```

**API Integration:**
- POST `/api/reviews/email/report`
- Payload: `{ recipients: string[], include_summary: boolean, include_individual_reports: boolean }`

---

## Updated ScreeningQueuePage

**Location:** `/frontend/src/pages/screening/ScreeningQueuePage.tsx`

### New Features Added:

#### 1. Bulk Selection
- Checkbox for each item in the queue
- "Select All" / "Deselect All" button
- Selection counter with bulk actions panel

#### 2. Action Buttons
- **Eye icon**: View detailed report for item
- **Review button**: Open review modal for item
- **Summary Report**: View cumulative statistics
- **Email Report**: Send reports to teams

#### 3. Status Indicators
- Visual badges for status (pending/approved/rejected/escalated)
- Icon indicators (Clock/CheckCircle/AlertTriangle)
- Severity color coding

#### 4. Bulk Actions Panel
Shows when items are selected:
- Selection count display
- Clear Selection button
- Bulk Review button

### UI Flow:

```
Screening Queue Page
│
├── Header Actions
│   ├── Summary Report Button → Opens CumulativeReport
│   └── Email Report Button → Opens EmailReportModal
│
├── Search Bar
│   └── Real-time filtering by name
│
├── Bulk Actions Panel (conditional)
│   ├── Selection count
│   ├── Clear Selection
│   └── Bulk Review → Opens BulkReviewModal
│
└── Results List
    └── For each item:
        ├── Checkbox (for bulk selection)
        ├── Item details (names, scores, severity)
        ├── Status badge
        ├── Eye icon → Opens ItemDetailReport
        └── Review button → Opens ReviewModal
```

---

## Installation & Setup

### Prerequisites
```bash
# Ensure Radix UI dependencies are installed
npm install @radix-ui/react-dialog @radix-ui/react-checkbox
```

### Dependencies Added:
- `@radix-ui/react-dialog` - Modal/Dialog component
- `@radix-ui/react-checkbox` - Checkbox component

### UI Components Used:
- Dialog (dialog.tsx) - Modal wrapper
- Textarea (textarea.tsx) - Multi-line text input
- Checkbox (checkbox.tsx) - Selection control
- Button, Input, Label, Card, Badge - Existing UI components

---

## Workflow Examples

### Daily Review Workflow

1. **View Queue**
   - Navigate to Screening Queue page
   - See all pending flagged items

2. **Review Individual Items**
   - Click "Review" button on item
   - Read match details
   - Make decision (Approve/Reject/Escalate)
   - Add detailed notes
   - Submit

3. **Bulk Process Similar Items**
   - Select multiple items with checkboxes
   - Click "Bulk Review"
   - Choose decision
   - Add notes
   - Submit

4. **View Details When Needed**
   - Click eye icon for detailed report
   - Review all information
   - Check audit trail
   - Download if needed

### Weekly Reporting Workflow

1. **Generate Summary**
   - Click "Summary Report"
   - Review statistics
   - Check approval rates
   - See top matches

2. **Email to Management**
   - Click "Email Report" from summary
   - Add recipient groups
   - Choose report contents
   - Send

### Escalation Workflow

1. **Complex Case Found**
   - Click "Review" on item
   - Click "Escalate" decision
   - Add detailed escalation reason
   - Submit

2. **Automatic Notifications**
   - System emails admins automatically
   - Escalation appears in finalizer queue
   - Audit trail updated

---

## API Endpoints Used

All endpoints are prefixed with `/api/reviews`:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/review/{item_id}` | Review single item |
| POST | `/review/bulk` | Bulk review multiple items |
| GET | `/report/item/{item_id}` | Get detailed item report |
| GET | `/report/cumulative` | Get cumulative statistics |
| POST | `/email/report` | Email reports to recipients |

---

## State Management

### Modal States
```tsx
const [reviewModalOpen, setReviewModalOpen] = useState(false);
const [bulkReviewModalOpen, setBulkReviewModalOpen] = useState(false);
const [detailReportModalOpen, setDetailReportModalOpen] = useState(false);
const [cumulativeReportModalOpen, setCumulativeReportModalOpen] = useState(false);
const [emailModalOpen, setEmailModalOpen] = useState(false);
```

### Selection State
```tsx
const [selectedItems, setSelectedItems] = useState<number[]>([]);
const [selectedItemForReview, setSelectedItemForReview] = useState<QueueItem | null>(null);
const [selectedItemForDetail, setSelectedItemForDetail] = useState<number | null>(null);
```

---

## Error Handling

All components include comprehensive error handling:

1. **API Errors**: Displayed as toast notifications
2. **Validation Errors**: Inline form validation
3. **Network Errors**: User-friendly error messages
4. **Loading States**: Spinner indicators during async operations

---

## Styling & Theme

All components use:
- **Tailwind CSS** for styling
- **shadcn/ui** component library
- **Lucide React** icons
- Consistent color scheme:
  - Green: Approved/Success
  - Red: Rejected/Error
  - Orange: Escalated/Warning
  - Blue: Info/Pending
  - Gray: Neutral/Default

---

## Testing

To test the review system:

1. **Start Backend**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Data**:
   - Upload `test_data/blacklist_with_matches.csv`
   - Should create 12 flagged items
   - Test all review workflows

4. **Test Scenarios**:
   - Single item review (approve)
   - Single item review (reject)
   - Single item escalation
   - Bulk review multiple items
   - View detailed report
   - View cumulative report
   - Send email report

---

## Production Deployment

### Build for Production:
```bash
cd frontend
npm run build
```

### Environment Variables:
Ensure API base URL is configured in `apiClient.ts`:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
```

### Deployment Checklist:
- ✅ All modals tested
- ✅ API endpoints verified
- ✅ Email configuration confirmed
- ✅ Authentication working
- ✅ Error handling tested
- ✅ Mobile responsive
- ✅ Build successful

---

## Troubleshooting

### Common Issues:

1. **Modal not opening**
   - Check state management
   - Verify modal component is imported
   - Check if isOpen prop is set correctly

2. **API calls failing**
   - Verify backend is running
   - Check authentication token
   - Verify API endpoint URLs
   - Check network tab for errors

3. **Bulk review not working**
   - Ensure items are selected (selectedItems array not empty)
   - Check if all selected items are in "pending" status
   - Verify bulk endpoint is accessible

4. **Email not sending**
   - Check SMTP configuration in backend
   - Verify email addresses are valid
   - Check backend logs for email errors
   - Ensure email service is running

---

## Best Practices

### For Reviewers:

1. **Always add detailed notes** - Required for audit trail
2. **Review individual items carefully** - Don't bulk approve without verification
3. **Escalate when uncertain** - Better safe than sorry
4. **Use detailed reports** - Check all information before deciding
5. **Regular reporting** - Send weekly summaries to management

### For Developers:

1. **Test all modals** - Ensure proper state management
2. **Handle errors gracefully** - Show user-friendly messages
3. **Validate input** - Both client and server side
4. **Log actions** - Complete audit trail
5. **Optimize performance** - Lazy load components when possible

---

## Future Enhancements

Potential improvements:

- [ ] Export reports as PDF
- [ ] Advanced filtering (by severity, date range, reviewer)
- [ ] Real-time notifications for escalations
- [ ] Dashboard analytics with charts
- [ ] Search within audit trail
- [ ] Batch operations history
- [ ] Mobile app version
- [ ] Integration with external systems

---

## Support

For issues or questions:
- Check backend logs: `backend/logs/`
- Check browser console for errors
- Review API documentation: `REVIEW_SYSTEM_GUIDE.md`
- Contact: Kamco IT Support

---

**Last Updated:** January 8, 2026
**Version:** 1.0.0
**Status:** Production Ready ✅
