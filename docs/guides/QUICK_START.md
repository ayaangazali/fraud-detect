# Quick Start Guide - Kamco Frontend

## 🚀 Start the App

```bash
cd /Users/ayaangazali/Documents/hackathons/Kamco/frontend
npm run dev
```

Visit: **http://localhost:3000/**

---

## 🔑 Login Credentials

| Username  | Password      | Role      | Permissions                          |
|-----------|---------------|-----------|--------------------------------------|
| screener  | screener123   | Screener  | Upload, Scan, Flag, Undo             |
| checker   | checker123    | Checker   | All Screener + Approve/Recheck       |
| finalizer | finalizer123  | Finalizer | View-only, Generate Reports          |

---

## 📍 Routes

| Route        | Component | Auth Required | Description                    |
|--------------|-----------|---------------|--------------------------------|
| `/`          | Login     | No            | Login page                     |
| `/dashboard` | Dashboard | Yes           | Main dashboard (landing page)  |
| `/*`         | -         | -             | Redirects to `/` (login)       |

---

## 🎯 Component Tree

```
AppRouter
├── Login (/)
└── Dashboard (/dashboard) [Protected]
    ├── Header (logo, user info, logout)
    ├── Tabs (All/Clients/Vendors/Staff/Tenants)
    ├── StatsCards (4 cards with counts)
    ├── FileUpload (blacklist + kamco dataset) [Screener/Checker only]
    ├── InReviewQueue (table of pending matches)
    │   └── FlagModal (reason textarea + immediate undo)
    └── FlaggedItems (card grid of flagged items)
        └── UndoModal (strict 2-step confirmation)
```

---

## 🧪 Testing Checklist

### ✅ Login Flow
- [ ] Visit `http://localhost:3000/`
- [ ] Enter `screener` / `screener123`
- [ ] Click "Sign In"
- [ ] Should redirect to `/dashboard`

### ✅ Dashboard
- [ ] See header with KAMCO logo
- [ ] See user info (username, role)
- [ ] See 4 stat cards (Total, In Review, Flagged, Cleared)
- [ ] Click tabs → Stats update
- [ ] Scroll to see all sections

### ✅ File Upload (Screener/Checker Only)
- [ ] Should see upload section
- [ ] Click upload zones (no actual upload)
- [ ] Click "Run Scan"
- [ ] Wait 2 seconds → Alert appears

### ✅ In Review Queue
- [ ] See table with 5 mock items
- [ ] Click checkbox to select item
- [ ] Click "Select All" checkbox
- [ ] Click "Flag" button → Opens modal

### ✅ Flag Modal
- [ ] See item summary
- [ ] Type < 10 characters → Button disabled
- [ ] Type 10+ characters → Button enabled
- [ ] Click "Flag Item"
- [ ] Success screen appears
- [ ] "Undo Flag" button visible
- [ ] Click "Continue" or wait 5 seconds

### ✅ Flagged Items
- [ ] Scroll to bottom
- [ ] See 3 flagged items in card layout
- [ ] Different status badges (Pending, Approved, Re-check)
- [ ] Click "Generate Report" → Alert
- [ ] Click "Undo Flag" → Opens modal

### ✅ Undo Modal
- [ ] Warning screen with icon
- [ ] Check the acknowledgment checkbox
- [ ] Type confirmation text (wrong) → Red highlight
- [ ] Type exact text: `I acknowledge I am undoing my action`
- [ ] Text turns green ✅
- [ ] "Confirm Undo" button enables
- [ ] Click → Alert appears

### ✅ Logout
- [ ] Click logout button
- [ ] localStorage cleared
- [ ] Redirects to login page

### ✅ Protected Route
- [ ] Logout
- [ ] Try `http://localhost:3000/dashboard`
- [ ] Should redirect to login

### ✅ Role-Based Visibility
- [ ] Login as `finalizer` / `finalizer123`
- [ ] Upload section should NOT be visible
- [ ] Can view queues and flagged items
- [ ] Logout and login as `screener`
- [ ] Upload section should be visible

### ✅ Tab Filtering
- [ ] Click "Clients" tab
- [ ] Stats show only client counts
- [ ] Queue shows only client items
- [ ] Flagged items show only clients
- [ ] Repeat for Vendors, Staff, Tenants

---

## 🐛 Troubleshooting

### TypeScript Errors:
```
Cannot find module '../components/Dashboard/...'
```
**Fix:** Files exist. Just reload VS Code or wait for auto-compile.

### Dev Server Not Starting:
```bash
# Kill any existing processes
lsof -ti:3000 | xargs kill -9
lsof -ti:5001 | xargs kill -9

# Restart
npm run dev
```

### Blank Page After Login:
- Check browser console for errors
- Clear localStorage: `localStorage.clear()`
- Refresh page
- Try login again

### Modal Not Closing:
- Click outside modal (on overlay)
- Click X button in top-right
- Press ESC key (if implemented)

---

## 📁 Key Files to Edit

### To modify mock data:
- **InReviewQueue.tsx** - Line 10-15 (mockData array)
- **FlaggedItems.tsx** - Line 10-30 (mockFlaggedData array)
- **StatsCards.tsx** - Line 8-14 (stats object)

### To change colors:
- **Dashboard.css** - KAMCO blue: `#0B5394`
- **StatsCards.css** - Gradient colors for cards
- **FlagModal.css** - Modal themes
- **Login.css** - Gradient background

### To add new roles:
- **Login.tsx** - Line 8-12 (validUsers object)
- **Dashboard.tsx** - Line 21-23 (canUpload check)

---

## 🔄 Next Integration Steps

### 1. Backend Auth API
```typescript
// Replace Login.tsx lines 14-28
const response = await fetch('http://localhost:5001/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});
const data = await response.json();
localStorage.setItem('kamco_auth', JSON.stringify(data));
```

### 2. File Upload API
```typescript
// Replace FileUpload.tsx handleRunScan
const formData = new FormData();
formData.append('blacklist', blacklistFile);
formData.append('kamco', kamcoFile);
const response = await fetch('http://localhost:5001/api/scan', {
  method: 'POST',
  body: formData
});
```

### 3. In Review Queue API
```typescript
// Replace InReviewQueue.tsx mockData
const response = await fetch('http://localhost:5001/api/review/queue');
const data = await response.json();
```

### 4. Flag Item API
```typescript
// Replace FlagModal.tsx handleFlag console.log
const response = await fetch('http://localhost:5001/api/review/flag', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ itemId: item.id, reason, flaggedBy: user.username })
});
```

---

## 📞 Support

**Documentation:**
- Full guide: `FRONTEND_SKELETON_COMPLETE.md`
- Implementation plan: `IMPLEMENTATION_GUIDE.md`

**Mock Data Examples:**
- InReviewQueue: 5 items (various match scores, types, actors)
- FlaggedItems: 3 items (different statuses: pending, approved, recheck)
- Stats: Counts per tab (all, clients, vendors, staff, tenants)

**Need Backend Work?**
All database schemas, API endpoints, and workflows are documented in `IMPLEMENTATION_GUIDE.md`.

---

**Happy Testing! 🎉**
