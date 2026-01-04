// src/App.tsx
import { useState } from 'react';
import { CustomerUpload } from './components/CustomerUpload';
import { BlacklistUpload } from './components/BlacklistUpload';
import { ScreeningControls } from './components/ScreeningControls';
import { ResultsGrid } from './components/ResultsGrid';
import { DashboardStats } from './components/DashboardStats';
import { LanguageSwitcher } from './components/LanguageSwitcher';
import { MatchDetailsModal } from './components/MatchDetailsModal';
import { useLanguage } from './hooks/useLanguage';
import { CustomerUploadResponse, BlacklistUploadResponse, ScreeningResponse, MatchResult } from './types';
import './App.css';

function App() {
  const [customerData, setCustomerData] = useState<CustomerUploadResponse | null>(null);
  const [blacklistData, setBlacklistData] = useState<BlacklistUploadResponse | null>(null);
  const [screeningResults, setScreeningResults] = useState<ScreeningResponse | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<MatchResult | null>(null);
  
  const { t, toggleLanguage, isArabic } = useLanguage();

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>🔍 {t('appTitle')}</h1>
            <p>{t('appSubtitle')}</p>
          </div>
          <LanguageSwitcher isArabic={isArabic} onToggle={toggleLanguage} t={t} />
        </div>
      </header>

      <main className="app-main">
        {/* Dashboard Stats */}
        <DashboardStats 
          customerData={customerData}
          blacklistData={blacklistData}
          results={screeningResults?.matches || []}
          t={t}
        />

        <div className="upload-sections">
          <CustomerUpload
            onUploadComplete={(data) => {
              setCustomerData(data);
              setScreeningResults(null);
            }}
            t={t}
          />
          
          <BlacklistUpload
            onUploadComplete={(data) => {
              setBlacklistData(data);
              setScreeningResults(null);
            }}
            t={t}
          />
        </div>

        <ScreeningControls
          customerData={customerData?.rows || null}
          blacklistData={blacklistData?.rows || null}
          customerErrors={customerData?.errors.length || 0}
          blacklistErrors={blacklistData?.errors.length || 0}
          onScreeningComplete={setScreeningResults}
          t={t}
        />

        {screeningResults && (
          <ResultsGrid
            results={screeningResults.matches}
            processingTime={screeningResults.processingTime}
            onViewDetails={setSelectedMatch}
            t={t}
            isArabic={isArabic}
          />
        )}
      </main>

      {/* Match Details Modal */}
      <MatchDetailsModal 
        match={selectedMatch}
        onClose={() => setSelectedMatch(null)}
        t={t}
        isArabic={isArabic}
      />
      
      <footer className="app-footer">
        <p>Built for compliance and risk management | {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
