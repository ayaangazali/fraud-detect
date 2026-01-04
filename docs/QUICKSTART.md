# 🚀 Quick Start Guide

## Get Started in 3 Minutes

### 1. Install Dependencies (if not done)

```bash
# From project root
npm install
cd server && npm install && cd ..
cd client && npm install && cd ..
```

### 2. Start the Application

```bash
# From project root - starts both frontend and backend
npm run dev
```

Or run separately:
```bash
# Terminal 1 - Backend (port 5000)
cd server
npm run dev

# Terminal 2 - Frontend (port 3000)
cd client
npm run dev
```

### 3. Open Your Browser

Navigate to: **http://localhost:3000**

## 📝 Test with Sample Data

Sample files are provided in `sample-data/`:

1. **Upload Customer File**
   - Click "Load Customer Names" section
   - Select `sample-data/customers-sample.csv`
   - Click "Upload & Validate"
   - Review the 10 sample customers

2. **Upload Blacklist File**
   - Click "Load Blacklisted Names" section
   - Select `sample-data/blacklist-sample.csv`
   - Click "Upload & Validate"
   - Review the 10 sample blacklist entries

3. **Run Screening**
   - Set similarity threshold to 75 (recommended)
   - Keep "Include Aliases" checked
   - Click "▶️ Run Screening"
   - View matches sorted by similarity score

4. **Export Results**
   - Review the matches in the results grid
   - Filter by minimum score, source, or type
   - Click "📥 Export to Excel"
   - Open the downloaded file in Excel

## 🎯 Expected Results with Sample Data

You should see several matches:
- **John Smith** ↔ Jon Smith (90%+ similarity)
- **Ahmed Hassan** ↔ Ahmed Al Hassan (85%+ similarity)
- **ABC Corporation** ↔ ABC Corp (90%+ similarity)
- **Global Trading Ltd** ↔ Global Trade Limited (85%+ similarity)

## 🔧 Troubleshooting

### Backend won't start
```bash
cd server
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Frontend won't start
```bash
cd client
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Port already in use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### TypeScript errors
These are compile-time warnings that will resolve once dependencies are installed. The application will still run.

## 📚 Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Create your own CSV files following the column format
3. Adjust the similarity threshold based on your needs
4. Explore the filtering and sorting options
5. Run the unit tests: `cd server && npm test`

## 💡 Tips

- **Start with high threshold (75-85)** to reduce false positives
- **Enable aliases** for comprehensive screening
- **Export early and often** to save results
- **Use filters** to focus on specific risk categories
- **Sort by score** to prioritize high-risk matches

## 🎨 UI Overview

```
┌─────────────────────────────────────────────┐
│   🔍 AML/KYC Name Screening System          │
├─────────────────────────────────────────────┤
│ ┌─────────────────┐ ┌───────────────────┐  │
│ │ Load Customers  │ │ Load Blacklist    │  │
│ │ • Upload file   │ │ • Upload file     │  │
│ │ • Preview       │ │ • Preview         │  │
│ │ • Validation    │ │ • Validation      │  │
│ └─────────────────┘ └───────────────────┘  │
├─────────────────────────────────────────────┤
│ ⚙️ Screening Configuration                  │
│ • Threshold: [___75___]                     │
│ • [✓] Include Aliases                       │
│ • [▶️ Run Screening]                        │
├─────────────────────────────────────────────┤
│ 📊 Results (sorted by score)                │
│ • Filters: Score | Source | Type            │
│ • [📥 Export to Excel]                      │
│ • Interactive table with sorting            │
└─────────────────────────────────────────────┘
```

---

**Ready to start? Run `npm run dev` and open http://localhost:3000** 🚀
