// src/App.tsx
import { useState } from 'react';
import { CustomerUpload } from './components/CustomerUpload';
import { BlacklistUpload } from './components/BlacklistUpload';
import { ScreeningControls } from './components/ScreeningControls';
import { ResultsGrid } from './components/ResultsGrid';
import { CustomerUploadResponse, BlacklistUploadResponse, ScreeningResponse } from './types';
import './App.css';

function App() {
  const [customerData, setCustomerData] = useState<CustomerUploadResponse | null>(null);
  const [blacklistData, setBlacklistData] = useState<BlacklistUploadResponse | null>(null);
  const [screeningResults, setScreeningResults] = useState<ScreeningResponse | null>(null);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔍 AML/KYC Name Screening System</h1>
        <p>Bulk import, fuzzy matching, and compliance screening</p>
      </header>

      <main className="app-main">
        <div className="upload-sections">
          <CustomerUpload
            onUploadComplete={(data) => {
              setCustomerData(data);
              setScreeningResults(null);
            }}
          />
          
          <BlacklistUpload
            onUploadComplete={(data) => {
              setBlacklistData(data);
              setScreeningResults(null);
            }}
          />
        </div>

        <ScreeningControls
          customerData={customerData?.rows || null}
          blacklistData={blacklistData?.rows || null}
          customerErrors={customerData?.errors.length || 0}
          blacklistErrors={blacklistData?.errors.length || 0}
          onScreeningComplete={setScreeningResults}
        />

        {screeningResults && (
          <ResultsGrid
            results={screeningResults.matches}
            processingTime={screeningResults.processingTime}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>Built for compliance and risk management | {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
