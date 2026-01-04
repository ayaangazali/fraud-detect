# 🔍 AML/KYC Name Screening System

A comprehensive full-stack application for Anti-Money Laundering (AML) and Know Your Customer (KYC) compliance screening with bulk import, fuzzy name matching, and Excel export capabilities - optimized for Middle Eastern markets.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
cd frontend && npm install && cd ..
cd backend && npm install && cd ..
```

### 2. Start Application
```bash
npm run dev
```

This starts:
- **Backend** on http://localhost:5000
- **Frontend** on http://localhost:3000

### 3. Open Browser
Navigate to: **http://localhost:3000**

## 📁 Project Structure

```
Kamco/
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── services/      # API client
│   │   └── types/         # TypeScript types
│   └── package.json
│
├── backend/               # Node.js + Express backend
│   ├── src/
│   │   ├── routes/        # API endpoints
│   │   ├── utils/         # Business logic
│   │   └── types/         # TypeScript types
│   └── package.json
│
├── sample-data/           # Mock data files
│   ├── customers-middle-east.csv      # 50 Middle Eastern customers
│   └── blacklist-middle-east.csv      # 40 sanctioned entities
│
├── docs/                  # Documentation
│   ├── README.md
│   ├── QUICKSTART.md
│   └── IMPLEMENTATION.md
│
└── package.json           # Root workspace config
```

## 📊 Sample Data

### Customer Data (`customers-middle-east.csv`)
- **50 realistic entries** with mostly Arabic names
- Demographics: Kuwait, UAE, Saudi Arabia, Bahrain, Qatar, and other Middle Eastern countries
- Mix of:
  - 80% Arabic/Middle Eastern names (Mohammed, Fatima, Abdullah, etc.)
  - 20% Western names (John, David, Robert)
- Includes both individuals and corporate entities
- Realistic company registration numbers

### Blacklist Data (`blacklist-middle-east.csv`)
- **40 high-risk entities** based on real-world sanctioned lists
- Includes known terrorists, sanctioned individuals, and dangerous entities
- Multiple aliases for comprehensive matching
- Sources: Government, Regulator, Other
- Historical dates from actual sanctions

**⚠️ Note:** The blacklist contains real names of dangerous individuals for demonstration purposes. This is realistic data for AML/KYC systems.

## 🎯 Features

✅ **Bulk Import** - CSV/XLSX upload for customers & blacklists  
✅ **Smart Validation** - Real-time error detection  
✅ **Fuzzy Matching** - 0-100% similarity threshold  
✅ **Alias Support** - Match against alternate names  
✅ **Results Grid** - Sortable, filterable results  
✅ **Excel Export** - Generate compliance reports  
✅ **Middle East Focus** - Arabic name support  

## 🧪 Test the Application

1. **Upload Customer File**
   - Select `sample-data/customers-middle-east.csv`
   - Click "Upload & Validate"
   - ✅ Should show 50 customers

2. **Upload Blacklist File**
   - Select `sample-data/blacklist-middle-east.csv`
   - Click "Upload & Validate"
   - ✅ Should show 40 blacklist entries

3. **Run Screening**
   - Set threshold: **75** (recommended)
   - Enable "Include Aliases"
   - Click "Run Screening"
   - ✅ Should find matches (e.g., "Omar Abdullah Bin Laden")

4. **Export Results**
   - Review matches
   - Click "Export to Excel"
   - ✅ Downloads formatted report

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/customers` | POST | Upload customer file |
| `/api/upload/blacklist` | POST | Upload blacklist file |
| `/api/screen` | POST | Run fuzzy matching |
| `/api/export` | POST | Generate Excel report |
| `/api/health` | GET | Health check |

## 🛠️ Available Commands

```bash
npm run dev              # Start both frontend + backend
npm run dev:frontend     # Start frontend only (port 3000)
npm run dev:backend      # Start backend only (port 5000)
npm test                 # Run all tests
npm run build            # Build for production
```

## 📚 Documentation

- **docs/README.md** - Complete documentation
- **docs/QUICKSTART.md** - 3-minute setup guide
- **docs/IMPLEMENTATION.md** - Technical details

## 🔐 Security & Compliance

This system is designed for AML/KYC compliance with:
- Name normalization for Arabic and English names
- Multi-alias matching
- Configurable risk thresholds
- Comprehensive audit trails via Excel export

## 🌍 Middle East Optimization

- **Arabic Name Support** - Handles Arabic transliterations
- **Regional Demographics** - Gulf countries focus
- **Local Regulations** - Compliant with GCC standards
- **Realistic Data** - Based on actual naming patterns

## ⚠️ Important Notes

1. **Blacklist Data**: Contains real names of sanctioned individuals for demonstration
2. **Customer Data**: Fictional but realistic Middle Eastern names
3. **One Match Alert**: Customer C018 "Omar Abdullah Bin Laden" will match blacklist entry "Omar Bin Laden"
4. **Fuzzy Matching**: Adjust threshold based on false positive tolerance

## 📞 Support

For issues or questions:
1. Check `docs/QUICKSTART.md` for common issues
2. Review `docs/README.md` for detailed documentation
3. Run tests: `cd backend && npm test`

## 🎉 Ready to Use!

```bash
npm run dev
```

Then open: **http://localhost:3000**

---

**Built for AML/KYC compliance in the Middle East region** 🔍✨
