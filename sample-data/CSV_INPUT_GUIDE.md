# 📊 SAMPLE CSV INPUT FILE GUIDE

## 🎯 File: `kamco_entities_sample.csv`

### Overview
This is a **comprehensive sample input file** for testing the Kamco Compliance Screening System. It contains 40 realistic entities with both Arabic and English names, covering all entity types used in the system.

---

## 📋 File Structure

### Column Definitions

| Column Name | Description | Example |
|------------|-------------|---------|
| **Customer_ID** | Unique identifier with prefix | KCLI-2024-001, KVEN-2024-001 |
| **Name_English** | Entity name in English | Mohammed Ahmed Al-Rashid |
| **Name_Arabic** | Entity name in Arabic | محمد أحمد الراشد |
| **Entity_Type** | Type of entity | Client, Vendor, Staff, Other |
| **Entity_Category** | Sub-category | Individual, Corporate, Regulatory Authority |
| **ID_Number** | Registration/ID number | 123456789, EMP001, REG001 |
| **Registration_Date** | Date of registration | 2020-03-15 |
| **Contact_Person** | Primary contact | Mohammed Al-Rashid |
| **Type_Individual_Corporate** | Individual or Corporate | Individual, Corporate |
| **Nationality** | Nationality | Kuwaiti, Saudi, American, etc. |
| **Country_of_Origin** | Country of origin | Kuwait, UAE, USA, etc. |
| **Industry_Sector** | Business sector | Real Estate, Banking, IT Services |
| **Risk_Level** | Risk assessment | High, Medium, Low, N/A |
| **Account_Status** | Current status | Active, Inactive |
| **Phone** | Contact phone | +965-9999-1234 |
| **Email** | Contact email | name@email.com |
| **Address** | Physical address | Block 5, Street 10, Kuwait City |
| **Notes** | Additional information | High net worth individual |

---

## 🏢 Entity Types Breakdown

### 1. Clients (KCLI) - 10 entities
**Purpose:** Customer entities that use Kamco services

**Examples:**
- KCLI-2024-001: Mohammed Ahmed Al-Rashid (محمد أحمد الراشد) - Individual, Real Estate
- KCLI-2024-002: Sarah Investment Corporation (شركة سارة للاستثمار) - Corporate, Financial Services
- KCLI-2024-005: Al-Salam Holdings Company (شركة السلام القابضة) - Corporate, Saudi Arabia

**Mix:**
- 5 Individuals (high net worth, professionals)
- 5 Corporations (investment firms, trading companies)
- Countries: Kuwait, UAE, Saudi Arabia, Qatar, Bahrain, Oman
- Industries: Real Estate, Financial Services, Technology, Retail, Energy

### 2. Vendors (KVEN) - 10 entities
**Purpose:** Service providers and suppliers to Kamco

**Examples:**
- KVEN-2024-001: Tech Solutions International Ltd (الحلول التقنية الدولية) - IT Services, USA
- KVEN-2024-002: Office Supplies Kuwait Co. (مستلزمات المكاتب الكويتية) - Office Equipment
- KVEN-2024-005: Security Services Company (شركة الخدمات الأمنية) - Security

**Categories:**
- IT Services (software, hardware)
- Professional Services (legal, marketing)
- Facilities (maintenance, security, catering)
- Logistics (transport, education, construction materials)

### 3. Staff (KSTA) - 10 entities
**Purpose:** Kamco employees and internal personnel

**Examples:**
- KSTA-2024-001: Ahmed Mohammed Al-Sabah (أحمد محمد الصباح) - Senior Financial Analyst
- KSTA-2024-002: Mariam Hassan Al-Khaled (مريم حسن الخالد) - Compliance Officer
- KSTA-2024-007: Bader Ahmed Al-Rashidi (بدر أحمد الرشيدي) - Legal Counsel

**Departments:**
- Finance (analysts, controllers)
- Compliance (AML/KYC specialists)
- Operations, IT, Risk Management
- HR, Legal, Marketing, Customer Service

**Note:** All staff are Kuwaiti nationals, employed at Kamco HQ

### 4. Others (KOTH) - 10 entities
**Purpose:** Regulatory bodies, government entities, industry associations

**Examples:**
- KOTH-2024-001: Central Bank of Kuwait (البنك المركزي الكويتي) - Regulatory Authority
- KOTH-2024-002: Kuwait Stock Exchange (بورصة الكويت) - Market Infrastructure
- KOTH-2024-007: Kuwait Anti-Money Laundering Unit (وحدة التحريات المالية) - Financial Intelligence

**Categories:**
- Regulatory Authorities (Central Bank, CMA, AML Unit)
- Market Infrastructure (Stock Exchange, Clearing Company)
- Government Entities (Ministry of Commerce)
- Industry Associations (KFSA, Chamber of Commerce)
- Regional Organizations (GCC)
- Civil Society (Transparency Society)

---

## 🎯 Usage Instructions

### 1. Upload to System
```
1. Go to Kamco system upload page
2. Click "Upload File" or drag-and-drop
3. Select kamco_entities_sample.csv
4. System will automatically parse and screen against blacklist
```

### 2. Expected Behavior
- **Automatic parsing** of CSV columns
- **Arabic text support** (Name_Arabic column)
- **Entity type detection** (Client/Vendor/Staff/Other)
- **Fuzzy matching** against blacklist entries
- **Risk-based flagging** based on match scores

### 3. Testing Scenarios

**High-Risk Scenarios:**
- High-risk level clients (KCLI-2024-002, KCLI-2024-005, KCLI-2024-006, KCLI-2024-010)
- International vendors (KVEN-2024-001 USA, KVEN-2024-007 Lebanon, KVEN-2024-008 UAE)
- Regulatory entity screening (KOTH entities)

**Low-Risk Scenarios:**
- Staff members (all KSTA)
- Local service vendors (office supplies, catering)
- Individual clients with established history

**Arabic Matching:**
- Test fuzzy matching with Arabic names
- Verify bidirectional language support
- Check name variations and transliterations

---

## 📊 Data Quality Features

### Realistic Data
✅ Mix of Arabic and English names  
✅ Authentic GCC business structure  
✅ Real-world entity categories  
✅ Proper phone/email formats  
✅ Valid addresses and contact info  

### Comprehensive Coverage
✅ All 4 entity types represented  
✅ Individual and corporate entities  
✅ Multiple nationalities (7 countries)  
✅ Various industry sectors (15+)  
✅ Different risk levels  

### Testing Value
✅ Name matching variations  
✅ Arabic character handling  
✅ Cross-border entities  
✅ Regulatory compliance checks  
✅ Internal staff screening  

---

## 🔧 Customization

### Adding More Entities
1. Copy the CSV structure
2. Maintain all 18 columns
3. Follow ID prefix conventions:
   - KCLI: Clients
   - KVEN: Vendors
   - KSTA: Staff
   - KOTH: Others
4. Include both English and Arabic names
5. Set appropriate risk levels

### Modifying Entity Types
- Change `Entity_Type` to route to different workflows
- Update `Entity_Category` for sub-classification
- Adjust `Risk_Level` for testing different scenarios
- Set `Account_Status` to Active/Inactive for testing

---

## 🎓 Key Features Demonstrated

### Multilingual Support
- English: "Mohammed Ahmed Al-Rashid"
- Arabic: "محمد أحمد الراشد"
- System handles both seamlessly

### Entity Categorization
- Clients: Investment management, trading
- Vendors: Service providers across sectors
- Staff: Internal employees with departments
- Others: Regulatory and government entities

### Geographic Diversity
- Kuwait (primary)
- GCC countries (UAE, Saudi, Qatar, Bahrain, Oman)
- International (USA, Lebanon)

### Industry Coverage
- Financial Services, Banking, Investment
- Technology, IT Services
- Real Estate, Construction
- Retail, Trading
- Professional Services
- Government, Regulatory

---

## 🚀 Quick Start

### Test Upload
```bash
# Backend should be running on port 8000
# Frontend on port 5173

1. Login as screener_test
2. Navigate to upload page
3. Select kamco_entities_sample.csv
4. Click upload
5. System screens automatically
6. View results in screening queue
```

### Expected Results
- **Total entities:** 40
- **Parsed successfully:** 40
- **Auto-screened:** Yes
- **Potential matches:** Depends on blacklist
- **Time to process:** < 5 seconds

---

## 📝 Notes

- **File Format:** UTF-8 encoded CSV
- **Separator:** Comma (,)
- **Headers:** First row contains column names
- **Arabic Support:** Full RTL support
- **Date Format:** YYYY-MM-DD
- **Phone Format:** International (+country-code)
- **Email Format:** Standard email validation

---

## ✅ Validation Checklist

Before uploading:
- [ ] File is UTF-8 encoded
- [ ] All 18 columns present
- [ ] No empty required fields
- [ ] Dates in correct format
- [ ] Arabic text displays correctly
- [ ] Customer IDs unique
- [ ] Entity types valid (Client/Vendor/Staff/Other)

---

**Status:** ✅ Ready for Production Testing  
**Last Updated:** January 11, 2026  
**File Version:** 1.0.0
