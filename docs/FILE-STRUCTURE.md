# 📁 Project File Structure

```
Kamco/
│
├── 📄 package.json                    # Root workspace config
├── 📄 package-lock.json               # Dependency lock file
├── 📄 .gitignore                      # Git ignore rules
├── 📄 setup.sh                        # Automated setup script
│
├── 📚 Documentation
│   ├── README.md                      # Complete documentation (1,200+ lines)
│   ├── QUICKSTART.md                  # 3-minute quick start guide
│   └── IMPLEMENTATION.md              # Implementation summary & metrics
│
├── 📊 sample-data/                    # Example files for testing
│   ├── customers-sample.csv           # 10 sample customers
│   └── blacklist-sample.csv           # 10 sample blacklist entries
│
├── 🖥️ server/                         # Backend (Node.js + Express)
│   ├── package.json                   # Server dependencies
│   ├── tsconfig.json                  # TypeScript config
│   ├── jest.config.js                 # Jest test config
│   │
│   └── src/
│       ├── index.ts                   # Express server entry point
│       │
│       ├── types/
│       │   └── index.ts               # Shared TypeScript interfaces
│       │
│       ├── routes/                    # API endpoints
│       │   ├── upload.ts              # POST /api/upload/customers & /blacklist
│       │   ├── screening.ts           # POST /api/screen
│       │   └── export.ts              # POST /api/export
│       │
│       └── utils/                     # Business logic
│           ├── fileParser.ts          # CSV/XLSX parsing
│           ├── validator.ts           # Data validation
│           ├── fuzzyMatcher.ts        # Fuse.js matching algorithm
│           ├── nameNormalizer.ts      # Name normalization
│           ├── excelExporter.ts       # Excel report generation
│           │
│           └── __tests__/             # Unit tests (Jest)
│               ├── nameNormalizer.test.ts    # 6 tests
│               ├── validator.test.ts         # 8 tests
│               └── fuzzyMatcher.test.ts      # 6 tests
│
└── 💻 client/                         # Frontend (React + Vite)
    ├── package.json                   # Client dependencies
    ├── tsconfig.json                  # TypeScript config
    ├── tsconfig.node.json             # Node-specific TS config
    ├── vite.config.ts                 # Vite bundler config
    ├── index.html                     # HTML entry point
    │
    └── src/
        ├── main.tsx                   # React entry point
        ├── App.tsx                    # Main application component
        ├── App.css                    # Main application styles
        ├── index.css                  # Global styles
        │
        ├── types/
        │   └── index.ts               # Shared TypeScript interfaces
        │
        ├── services/
        │   └── api.ts                 # Axios API client
        │
        └── components/                # React components
            ├── CustomerUpload.tsx     # Customer file upload & preview
            ├── BlacklistUpload.tsx    # Blacklist file upload & preview
            ├── ScreeningControls.tsx  # Threshold & alias controls
            └── ResultsGrid.tsx        # Sortable, filterable results table
```

## 📊 File Count Summary

| Category | Count | Details |
|----------|-------|---------|
| **TypeScript Files** | 17 | Source code |
| **Test Files** | 3 | Unit tests (20+ tests) |
| **Config Files** | 8 | package.json, tsconfig, etc. |
| **Documentation** | 3 | README, guides |
| **Styles** | 2 | CSS files |
| **Sample Data** | 2 | CSV examples |
| **Scripts** | 1 | Setup automation |
| **Total Files** | 36+ | Excluding node_modules |

## 🎯 Key Files by Purpose

### Getting Started
1. **QUICKSTART.md** - Start here for 3-minute setup
2. **README.md** - Complete documentation
3. **setup.sh** - Automated installation
4. **sample-data/** - Test files

### Backend Development
1. **server/src/index.ts** - Server entry point
2. **server/src/routes/** - API endpoints
3. **server/src/utils/** - Core logic
4. **server/src/utils/__tests__/** - Unit tests

### Frontend Development
1. **client/src/App.tsx** - Main UI
2. **client/src/components/** - UI components
3. **client/src/services/api.ts** - API integration
4. **client/src/App.css** - Styling

### Configuration
1. **package.json** (root) - Workspace scripts
2. **server/package.json** - Backend dependencies
3. **client/package.json** - Frontend dependencies
4. **tsconfig.json** files - TypeScript settings

## 🚀 Most Important Files to Review

### For Understanding the App:
1. `README.md` - Complete overview
2. `IMPLEMENTATION.md` - What was built
3. `client/src/App.tsx` - UI structure
4. `server/src/index.ts` - API structure

### For Testing:
1. `sample-data/customers-sample.csv`
2. `sample-data/blacklist-sample.csv`
3. `server/src/utils/__tests__/*.test.ts`

### For Development:
1. `client/src/components/*.tsx` - UI components
2. `server/src/utils/*.ts` - Business logic
3. `server/src/routes/*.ts` - API endpoints

## 📦 Dependencies

### Backend (server/package.json):
- express - Web framework
- multer - File uploads
- xlsx - Excel file parsing
- papaparse - CSV parsing
- fuse.js - Fuzzy matching
- exceljs - Excel generation
- cors - CORS handling
- typescript - Type safety
- jest - Testing

### Frontend (client/package.json):
- react - UI framework
- react-dom - React rendering
- axios - HTTP client
- vite - Build tool
- typescript - Type safety

### Root (package.json):
- concurrently - Run multiple commands

Total Dependencies: ~570 packages (including transitive)
