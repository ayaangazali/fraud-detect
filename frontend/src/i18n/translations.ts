// src/i18n/translations.ts

export const translations = {
  en: {
    // Header
    appTitle: "AML/KYC Name Screening",
    appSubtitle: "Advanced Compliance & Risk Management System",
    
    // Language
    language: "Language",
    switchToArabic: "العربية",
    switchToEnglish: "English",
    
    // Dashboard
    dashboard: "Dashboard",
    overview: "Overview",
    statistics: "Statistics",
    
    // Upload Section
    customerUpload: "Customer Upload",
    blacklistUpload: "Blacklist Upload",
    chooseFile: "Choose File",
    upload: "Upload",
    uploading: "Uploading...",
    
    // Customer Info
    supportedFormats: "Supported formats",
    requiredColumns: "Required columns",
    customerId: "customer_id",
    type: "type",
    fullNameEn: "full_name_en",
    dateOfBirth: "date_of_birth",
    companyRegNo: "company_reg_no",
    nationalityCountry: "nationality_country",
    
    // Blacklist Info
    blacklistName: "full_name",
    aliases: "alias_alternate_names",
    source: "source",
    effectiveDate: "effective_date",
    
    // Stats
    totalRows: "Total Rows",
    validRows: "Valid Rows",
    errors: "Errors",
    preview: "Preview",
    firstRows: "First 20 rows",
    
    // Screening Controls
    screeningControls: "Screening Controls",
    similarityThreshold: "Similarity Threshold",
    thresholdHelp: "Minimum match score (0-100). Recommended: 70-85",
    includeAliases: "Include Aliases",
    aliasesHelp: "Check alternate names and aliases",
    runScreening: "Run Screening",
    running: "Running...",
    
    // Results
    results: "Screening Results",
    noResults: "No results yet. Run screening to see matches.",
    totalMatches: "Total Matches",
    policeMatches: "Police Blacklist",
    userMatches: "User Blacklist",
    highRisk: "High Risk",
    mediumRisk: "Medium Risk",
    lowRisk: "Low Risk",
    filteredMatches: "Filtered Matches",
    processingTime: "Processing Time",
    
    // Filters
    filters: "Filters",
    minScore: "Min Similarity Score",
    sourceFilter: "Source",
    allSources: "All Sources",
    government: "Government",
    regulator: "Regulator",
    other: "Other",
    police: "Police",
    filterBy: "Filter By",
    all: "All",
    policeBlacklist: "Police Blacklist",
    userBlacklist: "User Blacklist",
    individual: "Individual",
    corporate: "Corporate",
    
    // Table Headers
    customerIdCol: "Customer ID",
    customerName: "Customer Name",
    customerType: "Customer Type",
    dobRegNo: "DOB/Reg No",
    nationality: "Nationality",
    blacklistMatch: "Blacklist Match",
    matchedVia: "Matched Via",
    sourceCol: "Source",
    blacklistType: "Blacklist Type",
    effectiveDateCol: "Effective Date",
    score: "Score",
    reason: "Reason",
    details: "Details",
    
    // Match Details
    matchDetails: "Match Details",
    viewDetails: "View Details",
    closeDetails: "Close",
    matchReason: "Match Reason",
    matchExplanation: "Why This Match?",
    directMatch: "Direct name match",
    aliasMatch: "Matched via alias",
    fuzzyMatch: "Fuzzy name matching",
    scoreBreakdown: "Score Breakdown",
    
    // Badges
    direct: "Direct",
    alias: "Alias",
    policeLabel: "Police",
    userLabel: "User",
    
    // Export
    exportToExcel: "Export to Excel",
    exporting: "Exporting...",
    
    // Messages
    uploadSuccess: "File uploaded successfully",
    uploadError: "Upload failed. Please try again.",
    screeningComplete: "Screening completed",
    noMatches: "No matches found with current filters.",
    
    // Risk Levels
    critical: "Critical Risk",
    high: "High Risk",
    medium: "Medium Risk",
    low: "Low Risk",
    minimal: "Minimal Risk",
    
    // Dashboard Cards
    totalCustomers: "Total Customers",
    totalBlacklist: "Total Blacklist",
    matchRate: "Match Rate",
    avgScore: "Avg Score",
    
    // Time
    ms: "ms",
    
    // Warnings
    warning: "Warning",
    pleaseUploadCustomers: "Please upload customer data first",
    pleaseUploadBlacklist: "Please upload blacklist data (or screening will use police blacklist only)",
  },
  
  ar: {
    // Header
    appTitle: "فحص أسماء مكافحة غسل الأموال",
    appSubtitle: "نظام متقدم للامتثال وإدارة المخاطر",
    
    // Language
    language: "اللغة",
    switchToArabic: "العربية",
    switchToEnglish: "English",
    
    // Dashboard
    dashboard: "لوحة التحكم",
    overview: "نظرة عامة",
    statistics: "الإحصائيات",
    
    // Upload Section
    customerUpload: "تحميل بيانات العملاء",
    blacklistUpload: "تحميل القائمة السوداء",
    chooseFile: "اختر ملف",
    upload: "تحميل",
    uploading: "جاري التحميل...",
    
    // Customer Info
    supportedFormats: "التنسيقات المدعومة",
    requiredColumns: "الأعمدة المطلوبة",
    customerId: "رقم_العميل",
    type: "النوع",
    fullNameEn: "الاسم_الكامل",
    dateOfBirth: "تاريخ_الميلاد",
    companyRegNo: "رقم_تسجيل_الشركة",
    nationalityCountry: "الجنسية_البلد",
    
    // Blacklist Info
    blacklistName: "الاسم_الكامل",
    aliases: "الأسماء_البديلة",
    source: "المصدر",
    effectiveDate: "تاريخ_السريان",
    
    // Stats
    totalRows: "إجمالي الصفوف",
    validRows: "الصفوف الصحيحة",
    errors: "الأخطاء",
    preview: "معاينة",
    firstRows: "أول 20 صف",
    
    // Screening Controls
    screeningControls: "ضوابط الفحص",
    similarityThreshold: "عتبة التشابه",
    thresholdHelp: "الحد الأدنى لدرجة التطابق (0-100). الموصى به: 70-85",
    includeAliases: "تضمين الأسماء البديلة",
    aliasesHelp: "التحقق من الأسماء البديلة والمستعارة",
    runScreening: "تشغيل الفحص",
    running: "جاري التشغيل...",
    
    // Results
    results: "نتائج الفحص",
    noResults: "لا توجد نتائج بعد. قم بتشغيل الفحص لرؤية التطابقات.",
    totalMatches: "إجمالي التطابقات",
    policeMatches: "القائمة السوداء للشرطة",
    userMatches: "القائمة السوداء للمستخدم",
    highRisk: "مخاطر عالية",
    mediumRisk: "مخاطر متوسطة",
    lowRisk: "مخاطر منخفضة",
    filteredMatches: "التطابقات المفلترة",
    processingTime: "وقت المعالجة",
    
    // Filters
    filters: "الفلاتر",
    minScore: "الحد الأدنى لدرجة التشابه",
    sourceFilter: "المصدر",
    allSources: "جميع المصادر",
    government: "حكومي",
    regulator: "تنظيمي",
    other: "آخر",
    police: "شرطة",
    filterBy: "تصفية حسب",
    all: "الكل",
    policeBlacklist: "القائمة السوداء للشرطة",
    userBlacklist: "القائمة السوداء للمستخدم",
    individual: "فرد",
    corporate: "شركة",
    
    // Table Headers
    customerIdCol: "رقم العميل",
    customerName: "اسم العميل",
    customerType: "نوع العميل",
    dobRegNo: "تاريخ الميلاد/رقم التسجيل",
    nationality: "الجنسية",
    blacklistMatch: "تطابق القائمة السوداء",
    matchedVia: "تطابق عبر",
    sourceCol: "المصدر",
    blacklistType: "نوع القائمة",
    effectiveDateCol: "تاريخ السريان",
    score: "الدرجة",
    reason: "السبب",
    details: "التفاصيل",
    
    // Match Details
    matchDetails: "تفاصيل التطابق",
    viewDetails: "عرض التفاصيل",
    closeDetails: "إغلاق",
    matchReason: "سبب التطابق",
    matchExplanation: "لماذا حدث هذا التطابق؟",
    directMatch: "تطابق مباشر في الاسم",
    aliasMatch: "تطابق عبر اسم مستعار",
    fuzzyMatch: "تطابق غامض في الاسم",
    scoreBreakdown: "تفاصيل الدرجة",
    
    // Badges
    direct: "مباشر",
    alias: "مستعار",
    policeLabel: "شرطة",
    userLabel: "مستخدم",
    
    // Export
    exportToExcel: "تصدير إلى Excel",
    exporting: "جاري التصدير...",
    
    // Messages
    uploadSuccess: "تم تحميل الملف بنجاح",
    uploadError: "فشل التحميل. يرجى المحاولة مرة أخرى.",
    screeningComplete: "اكتمل الفحص",
    noMatches: "لم يتم العثور على تطابقات مع الفلاتر الحالية.",
    
    // Risk Levels
    critical: "مخاطر حرجة",
    high: "مخاطر عالية",
    medium: "مخاطر متوسطة",
    low: "مخاطر منخفضة",
    minimal: "مخاطر ضئيلة",
    
    // Dashboard Cards
    totalCustomers: "إجمالي العملاء",
    totalBlacklist: "إجمالي القائمة السوداء",
    matchRate: "معدل التطابق",
    avgScore: "متوسط ​​الدرجة",
    
    // Time
    ms: "مللي ثانية",
    
    // Warnings
    warning: "تحذير",
    pleaseUploadCustomers: "يرجى تحميل بيانات العملاء أولاً",
    pleaseUploadBlacklist: "يرجى تحميل القائمة السوداء (أو سيستخدم الفحص قائمة الشرطة فقط)",
  },
};

export type Language = 'en' | 'ar';
export type TranslationKey = keyof typeof translations.en;
