# 🔍 AML/KYC Name Screening System

A comprehensive full-stack application for Anti-Money Laundering (AML) and Know Your Customer (KYC) compliance screening with bulk import, fuzzy name matching, and Excel export capabilities.

## 🎯 Features

- **Bulk Import**: Upload customer and blacklist data via CSV/XLSX files
- **Smart Validation**: Real-time data validation with detailed error reporting
- **Fuzzy Matching**: Advanced name matching algorithm with configurable similarity threshold
- **Alias Support**: Match against alternate names and aliases
- **Results Grid**: Sortable, filterable results with visual risk indicators
- **Excel Export**: Generate compliance reports in .xlsx format
- **Responsive UI**: Modern, intuitive interface with loading states and error handling

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- React 18 with TypeScript
- Vite for fast development
- Axios for API communication
- CSS3 for styling

**Backend:**
- Node.js with Express
- TypeScript for type safety
- Multer for file uploads
- XLSX & PapaParse for file parsing
- Fuse.js for fuzzy matching
- ExcelJS for report generation

### Project Structure

```
Kamco/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── CustomerUpload.tsx
│   │   │   ├── BlacklistUpload.tsx
│   │   │   ├── ScreeningControls.tsx
│   │   │   └── ResultsGrid.tsx
│   │   ├── services/      # API client
│   │   ├── types/         # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
├── server/                # Express backend
│   ├── src/
│   │   ├── routes/        # API endpoints
│   │   ├── utils/         # Business logic
│   │   │   ├── fileParser.ts
│   │   │   ├── validator.ts
│   │   │   ├── fuzzyMatcher.ts
│   │   │   ├── nameNormalizer.ts
│   │   │   └── excelExporter.ts
│   │   ├── types/         # TypeScript interfaces
│   │   └── index.ts
│   └── package.json
├── sample-data/           # Example files
└── package.json           # Workspace root
```

## 🚀 Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Git

### Installation

1. **Clone the repository:**
   ```bash
   cd /Users/ayaangazali/Documents/hackathons/Kamco
   ```

2. **Install root dependencies:**
   ```bash
   npm install
   ```

3. **Install server dependencies:**
   ```bash
   cd server
   npm install
   cd ..
   ```

4. **Install client dependencies:**
   ```bash
   cd client
   npm install
   cd ..
   ```

### Running the Application

**Development Mode (recommended):**
```bash
# From root directory
npm run dev
```

This starts both frontend (port 3000) and backend (port 5000) concurrently.

**Or run separately:**

```bash
# Terminal 1 - Backend
cd server
npm run dev

# Terminal 2 - Frontend
cd client
npm run dev
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api

### Running Tests

```bash
# Backend tests
cd server
npm test

# Client tests (if added)
cd client
npm test
```

## 📖 Usage Guide

### 1. Upload Customer Data

**Required columns:**
- `customer_id` - Unique identifier
- `type` - "individual" or "corporate"
- `full_name_en` - Full name in English
- `date_of_birth` - For individuals (YYYY-MM-DD format)
- `company_reg_no` - For corporates
- `nationality_country` - Nationality or country of registration

**Example:**
```csv
customer_id,type,full_name_en,date_of_birth,company_reg_no,nationality_country
C001,individual,John Smith,1990-05-15,,USA
C002,corporate,ABC Corporation,,REG-2024-001,UK
```

### 2. Upload Blacklist Data

**Required columns:**
- `full_name` - Full name of blacklisted entity
- `alias_alternate_names` - Comma-separated aliases (optional)
- `source` - "government", "regulator", or "other"
- `effective_date` - When listing became effective

**Example:**
```csv
full_name,alias_alternate_names,source,effective_date
Jon Smith,Johnny Smith,government,2023-01-15
ABC Corp,ABC Company Ltd,regulator,2022-12-01
```

### 3. Configure Screening

- **Similarity Threshold (0-100)**: Higher values = stricter matching
  - 90-100: Exact or near-exact matches only
  - 75-89: High similarity (recommended)
  - 50-74: Moderate similarity
  - Below 50: Loose matching (many false positives)

- **Include Aliases**: Enable to match against alternate names in blacklist

### 4. Review Results

Results are sorted by similarity score (highest first) and include:
- Customer details
- Matched blacklist entry
- Whether match was via alias or direct
- Source and effective date
- Similarity score with color coding

**Risk indicators:**
- 🔴 Red (90-100%): High risk - immediate review
- 🟠 Orange (80-89%): Elevated risk
- 🟡 Yellow (70-79%): Moderate risk
- 🟢 Green (<70%): Lower risk

### 5. Filter and Export

- Apply filters by minimum score, source, or customer type
- Sort by any column (click header)
- Export filtered results to Excel for reporting

## 🔧 API Documentation

### Endpoints

#### POST /api/upload/customers
Upload and validate customer file.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (CSV or XLSX)

**Response:**
```json
{
  "rows": [...],
  "preview": [...],
  "errors": [...],
  "totalRows": 100,
  "validRows": 95
}
```

#### POST /api/upload/blacklist
Upload and validate blacklist file.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (CSV or XLSX)

**Response:**
```json
{
  "rows": [...],
  "preview": [...],
  "errors": [...],
  "totalRows": 50,
  "validRows": 50
}
```

#### POST /api/screen
Run fuzzy name matching.

**Request:**
```json
{
  "customers": [...],
  "blacklist": [...],
  "threshold": 75,
  "includeAliases": true
}
```

**Response:**
```json
{
  "matches": [...],
  "totalCustomers": 100,
  "totalBlacklist": 50,
  "matchesFound": 12,
  "processingTime": 342
}
```

#### POST /api/export
Generate Excel report.

**Request:**
```json
{
  "matches": [...]
}
```

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Binary XLSX file

## 🧪 Fuzzy Matching Algorithm

### Name Normalization

Before matching, all names are normalized:
1. Convert to lowercase
2. Remove punctuation (.,!?;:etc.)
3. Collapse multiple spaces
4. Remove common titles (Mr, Mrs, Dr, Prof)

**Example:**
- Input: `"Dr. O'Brien-Smith, Jr."`
- Normalized: `"o brien smith jr"`

### Matching Process

1. **Build search index**: Create normalized entries for all blacklist names and aliases
2. **Fuse.js configuration**:
   - Token-based matching for word order flexibility
   - Character-level similarity scoring
   - Configurable threshold (0-100)
3. **Scoring**: Convert Fuse.js score to percentage (0-100)
4. **Filtering**: Return only matches >= threshold

### Performance

- **Small datasets** (<1,000 customers): <1 second
- **Medium datasets** (1,000-10,000): 1-5 seconds
- **Large datasets** (10,000-100,000): 5-30 seconds

For very large datasets, consider:
- Increasing threshold to reduce matches
- Processing in batches
- Running on backend with more resources

## ⚠️ Error Handling

### File Upload Errors

- **Missing required columns**: Clear error message listing missing columns
- **Invalid file format**: Only CSV and XLSX accepted
- **File too large**: 10MB limit (configurable)
- **Empty files**: Validation error

### Data Validation Errors

- **Per-row errors**: Displayed in table with row number, field, and message
- **Preview continues**: Can review all data even with errors
- **Warning before screening**: Alert if errors exist

### Runtime Errors

- **Network failures**: Retry suggestions
- **Timeout**: For very large datasets
- **Memory issues**: Reduce dataset size or threshold

## 🎨 UX Features

### Loading States
- Upload buttons show "Uploading..."
- Screening button shows "🔄 Running Screening..."
- Export button shows "📥 Exporting..."

### Empty States
- "Upload files to begin" message
- "No results yet" when screening not run
- "No matches found" when filters exclude all results

### Visual Feedback
- ✅ Green badges for success
- ⚠️ Yellow for warnings
- ❌ Red for errors
- Color-coded similarity scores

### Responsive Design
- Mobile-friendly layout
- Horizontal scrolling for tables
- Stacked layout on small screens

## 🧪 Testing

### Unit Tests Included

1. **nameNormalizer.test.ts**: Name normalization and alias parsing
2. **validator.test.ts**: Customer and blacklist data validation
3. **fuzzyMatcher.test.ts**: Fuzzy matching algorithm

**Run tests:**
```bash
cd server
npm test
```

### Manual Testing Checklist

- [ ] Upload valid CSV file
- [ ] Upload valid XLSX file
- [ ] Upload file with missing columns
- [ ] Upload file with validation errors
- [ ] Run screening with different thresholds
- [ ] Toggle alias matching
- [ ] Filter results by score/source/type
- [ ] Sort by different columns
- [ ] Export to Excel
- [ ] Test with large files (1000+ rows)

## 🚀 Production Deployment

### Build for Production

```bash
# Build both client and server
npm run build

# Or separately
cd server && npm run build
cd client && npm run build
```

### Environment Variables

Create `.env` file in server/:
```env
PORT=5000
NODE_ENV=production
MAX_FILE_SIZE=10485760
```

### Deployment Options

**Option 1: Single server (recommended for small scale)**
- Serve client build from Express static middleware
- Deploy to Heroku, Railway, or DigitalOcean

**Option 2: Separate services**
- Frontend: Vercel, Netlify
- Backend: Heroku, AWS Lambda, Google Cloud Run

**Option 3: Docker**
```bash
# Build images
docker build -t aml-kyc-server ./server
docker build -t aml-kyc-client ./client

# Run with docker-compose (create docker-compose.yml)
docker-compose up
```

## 📊 Performance Notes

### Optimization Strategies

1. **File Size Limits**: Default 10MB, adjust based on needs
2. **Pagination**: Consider paginating results grid for 10,000+ matches
3. **Lazy Loading**: Load preview on scroll for large files
4. **Web Workers**: Move fuzzy matching to worker threads (future enhancement)
5. **Caching**: Cache normalized names to avoid re-processing

### Benchmarks

| Dataset Size | Processing Time | Memory Usage |
|--------------|----------------|--------------|
| 100 x 50     | <1s            | ~50MB        |
| 1,000 x 500  | 2-5s           | ~200MB       |
| 10,000 x 1000| 15-30s         | ~500MB       |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is created for compliance and risk management purposes.

## 🆘 Support

For issues or questions:
1. Check the [Usage Guide](#-usage-guide)
2. Review [Error Handling](#️-error-handling)
3. Run tests to verify setup
4. Check browser console for errors

---

**Built with ❤️ for compliance teams**
