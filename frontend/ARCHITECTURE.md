# Phase 9: Modern Frontend Architecture

## Technology Stack

### Core
- **React 18.2** - UI library with concurrent features
- **TypeScript 5.3** - Type safety
- **Vite 5.0** - Fast build tool

### Styling & UI
- **Tailwind CSS 3.4** - Utility-first CSS
- **shadcn/ui** - Accessible component library
- **Lucide React** - Icon library

### State Management
- **Zustand** - Lightweight global state
- **React Query (TanStack Query)** - Server state management
- **React Context** - Auth & Theme context

### Forms & Validation
- **React Hook Form** - Performant forms
- **Zod** - Schema validation

### Data Visualization
- **Recharts** - Charts and graphs

### Internationalization
- **React i18next** - Multi-language support (EN/AR)

### Other Libraries
- **Axios** - HTTP client with interceptors
- **React Router DOM** - Navigation
- **React Dropzone** - File uploads
- **React Hot Toast** - Notifications
- **date-fns** - Date utilities

## Folder Structure

```
frontend/src/
├── components/
│   ├── ui/                  # shadcn/ui base components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── select.tsx
│   │   ├── table.tsx
│   │   ├── toast.tsx
│   │   └── ...
│   ├── layout/              # Layout components
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── MainLayout.tsx
│   │   └── Footer.tsx
│   ├── auth/                # Auth components
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── ProtectedRoute.tsx
│   ├── screening/           # Screening workflow
│   │   ├── FileUpload.tsx
│   │   ├── InReviewQueue.tsx
│   │   ├── MatchDetailModal.tsx
│   │   └── BulkActions.tsx
│   ├── review/              # Review components
│   │   ├── ReviewQueue.tsx
│   │   ├── ReviewCard.tsx
│   │   ├── ApprovalActions.tsx
│   │   └── ReviewNotes.tsx
│   ├── reports/             # Reports components
│   │   ├── ReportBuilder.tsx
│   │   ├── ReportPreview.tsx
│   │   ├── ReportHistory.tsx
│   │   └── Charts/
│   ├── audit/               # Audit log viewer
│   │   ├── AuditLogTable.tsx
│   │   ├── AuditFilters.tsx
│   │   ├── UserActivityTimeline.tsx
│   │   └── SecurityDashboard.tsx
│   └── shared/              # Shared components
│       ├── LoadingSkeleton.tsx
│       ├── EmptyState.tsx
│       ├── ErrorBoundary.tsx
│       ├── ConfirmDialog.tsx
│       └── DataTable.tsx
├── pages/
│   ├── auth/
│   │   ├── LoginPage.tsx
│   │   └── RegisterPage.tsx
│   ├── dashboard/
│   │   ├── ScreenerDashboard.tsx
│   │   ├── CheckerDashboard.tsx
│   │   ├── FinalizerDashboard.tsx
│   │   └── AdminDashboard.tsx
│   ├── screening/
│   │   ├── UploadPage.tsx
│   │   ├── QueuePage.tsx
│   │   └── ReviewPage.tsx
│   ├── reports/
│   │   ├── ReportsPage.tsx
│   │   └── ReportDetailPage.tsx
│   ├── audit/
│   │   └── AuditLogsPage.tsx
│   └── settings/
│       └── SettingsPage.tsx
├── hooks/
│   ├── useAuth.ts           # Auth hook
│   ├── useApi.ts            # API hook
│   ├── useDebounce.ts       # Debounce hook
│   ├── useLocalStorage.ts   # Local storage hook
│   └── useMediaQuery.ts     # Responsive hook
├── contexts/
│   ├── AuthContext.tsx      # Auth state
│   └── ThemeContext.tsx     # Theme state
├── stores/
│   ├── authStore.ts         # Auth Zustand store
│   └── uiStore.ts           # UI state store
├── services/
│   ├── api.ts               # Axios instance
│   ├── authService.ts       # Auth API calls
│   ├── screeningService.ts  # Screening API calls
│   ├── reviewService.ts     # Review API calls
│   ├── reportService.ts     # Report API calls
│   └── auditService.ts      # Audit API calls
├── lib/
│   ├── utils.ts             # Utility functions
│   ├── cn.ts                # Class name utility
│   └── validators.ts        # Validation schemas
├── types/
│   ├── index.ts             # All TypeScript types
│   ├── api.ts               # API response types
│   └── models.ts            # Data models
├── i18n/
│   ├── config.ts            # i18n configuration
│   ├── translations.ts      # Translations
│   └── locales/
│       ├── en.json
│       └── ar.json
├── styles/
│   └── globals.css          # Global styles
├── main.tsx                 # Entry point
└── App.tsx                  # Main app component
```

## Key Design Patterns

### 1. Component Architecture
- **Atomic Design**: ui → shared → features → pages
- **Composition over Inheritance**: Reusable, composable components
- **Single Responsibility**: Each component has one job

### 2. State Management Strategy
```typescript
// Global state (Zustand)
- Auth state (user, tokens)
- UI state (sidebar, theme, language)

// Server state (React Query)
- API data fetching
- Cache management
- Automatic refetching

// Local state (useState)
- Form inputs
- Component-specific state
```

### 3. API Integration
```typescript
// services/api.ts - Axios instance with interceptors
- Request interceptor: Add auth token
- Response interceptor: Handle 401, refresh token
- Error handling: Centralized error messages
```

### 4. Routing Strategy
```typescript
// AppRouter.tsx
- Public routes: /login, /register
- Protected routes: All dashboard routes
- Role-based routes: Admin-only routes
- 404 fallback
```

### 5. Form Handling
```typescript
// React Hook Form + Zod
- Schema validation
- Type-safe forms
- Automatic error messages
- Optimized re-renders
```

## Component Patterns

### 1. Protected Route
```typescript
<ProtectedRoute requireRole="admin">
  <AuditLogsPage />
</ProtectedRoute>
```

### 2. Data Fetching
```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['queue'],
  queryFn: screeningService.getQueue
});
```

### 3. Form with Validation
```typescript
const form = useForm({
  resolver: zodResolver(loginSchema)
});
```

### 4. API Service
```typescript
export const authService = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout')
};
```

## Styling Guidelines

### 1. Tailwind CSS Utility Classes
```typescript
<div className="flex items-center gap-4 p-6 bg-white rounded-lg shadow-sm">
```

### 2. Component Variants (shadcn/ui pattern)
```typescript
const buttonVariants = cva("base-classes", {
  variants: {
    variant: { default: "", destructive: "", outline: "" },
    size: { default: "", sm: "", lg: "" }
  }
});
```

### 3. Dark Mode Support
```typescript
<div className="bg-white dark:bg-gray-900">
```

### 4. Responsive Design
```typescript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

## Accessibility Requirements

### WCAG 2.1 AA Compliance
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ ARIA labels
- ✅ Focus indicators
- ✅ Color contrast (4.5:1 minimum)
- ✅ Skip navigation links

## Performance Optimization

### 1. Code Splitting
```typescript
const AuditLogsPage = lazy(() => import('./pages/audit/AuditLogsPage'));
```

### 2. React Query Caching
```typescript
queryClient.setDefaultOptions({
  queries: { staleTime: 5 * 60 * 1000 } // 5 minutes
});
```

### 3. Optimized Images
- Use WebP format
- Lazy loading
- Responsive images

### 4. Bundle Optimization
- Tree shaking
- Vite code splitting
- Dynamic imports

## Security Best Practices

### 1. XSS Prevention
- Sanitize user input
- Use React's built-in escaping
- No dangerouslySetInnerHTML

### 2. Token Management
- HttpOnly cookies (if possible)
- Secure storage
- Auto-refresh tokens
- Clear on logout

### 3. CSRF Protection
- CSRF tokens in headers
- SameSite cookies

### 4. Input Validation
- Client-side: Zod schemas
- Server-side: Always validate

## Testing Strategy

### 1. Unit Tests (Vitest)
- Component logic
- Utility functions
- Custom hooks

### 2. Integration Tests
- API service calls
- Form submissions
- Auth flows

### 3. E2E Tests (Optional - Playwright)
- Critical user journeys
- Multi-step workflows

## Internationalization (i18n)

### Setup
```typescript
i18n.use(initReactI18next).init({
  resources: { en: { translation: enTranslations } },
  lng: 'en',
  fallbackLng: 'en'
});
```

### Usage
```typescript
const { t } = useTranslation();
<h1>{t('dashboard.title')}</h1>
```

### RTL Support
```css
[dir="rtl"] .sidebar { right: 0; left: auto; }
```

## Implementation Phases

### Phase 1: Foundation (Tasks 48-49)
- Architecture planning ✅
- Install dependencies
- Configure Tailwind + shadcn/ui
- Setup TypeScript strict mode

### Phase 2: Core Features (Tasks 50-51)
- Authentication system
- Dashboard layouts
- Navigation

### Phase 3: Workflows (Tasks 52-53)
- Screening UI
- Review interface

### Phase 4: Advanced Features (Tasks 54-56)
- Reports module
- Audit viewer
- Real-time updates

### Phase 5: Polish (Task 57)
- Loading states
- Error handling
- Testing
- Documentation

## Next Steps

1. ✅ Architecture documentation complete
2. → Install dependencies (Tailwind, shadcn/ui, etc.)
3. → Setup base UI components
4. → Build authentication system
5. → Implement role-based dashboards
