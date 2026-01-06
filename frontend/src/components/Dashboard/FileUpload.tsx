// src/components/Dashboard/FileUpload.tsx
import React, { useState, useRef } from 'react';
import './FileUpload.css';

const FileUpload: React.FC = () => {
  const [blacklistFile, setBlacklistFile] = useState<File | null>(null);
  const [scanning, setScanning] = useState(false);

  const blacklistInputRef = useRef<HTMLInputElement>(null);

  const handleBlacklistSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setBlacklistFile(e.target.files[0]);
    }
  };

  const handleRunScan = async () => {
    if (!blacklistFile) {
      alert('Please upload the Blacklist Excel file');
      return;
    }

    setScanning(true);
    try {
      // TODO: Replace with actual FastAPI call
      const formData = new FormData();
      formData.append('blacklist', blacklistFile);
      
      // await fetch('http://localhost:8000/api/scan/run', {
      //   method: 'POST',
      //   body: formData
      // });
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      alert('✅ Scan completed! Found new matches.');
    } catch (error) {
      alert('❌ Scan failed. Please try again.');
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="file-upload-section">
      <div className="section-header">
        <h2>Upload Blacklist & Scan</h2>
        <p>Upload the blacklist Excel file to scan against Kamco's database</p>
        <div className="info-note">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <span>Kamco dataset is pre-loaded in the backend database</span>
        </div>
      </div>

      <div className="upload-container">
        {/* Blacklist Upload */}
        <div className="upload-card">
          <div className="upload-header">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="12" y1="18" x2="12" y2="12"/>
              <line x1="9" y1="15" x2="15" y2="15"/>
            </svg>
            <h4>Blacklist Excel File</h4>
            <p>Multi-sheet Excel (Clients, Vendors, Staff, Others)</p>
          </div>

          <div
            className="drop-zone"
            onClick={() => blacklistInputRef.current?.click()}
          >
            <input
              ref={blacklistInputRef}
              type="file"
              accept=".xlsx,.xls"
              onChange={handleBlacklistSelect}
              style={{ display: 'none' }}
            />

            {blacklistFile ? (
              <div className="file-selected">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
                <p className="file-name">{blacklistFile.name}</p>
                <p className="file-size">{(blacklistFile.size / 1024).toFixed(2)} KB</p>
                <button
                  className="remove-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    setBlacklistFile(null);
                  }}
                >
                  Remove
                </button>
              </div>
            ) : (
              <div className="drop-placeholder">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <p>Click to upload or drag and drop</p>
                <p className="hint">Excel files (.xlsx, .xls)</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Scan Action */}
      <div className="scan-section">
        <div className="scan-info">
          {blacklistFile ? (
            <p>✅ Ready to scan <strong>{blacklistFile.name}</strong> against Kamco database</p>
          ) : (
            <p>Upload the blacklist Excel file to begin</p>
          )}
        </div>

        <button
          className="scan-btn"
          onClick={handleRunScan}
          disabled={!blacklistFile || scanning}
        >
          {scanning ? (
            <>
              <div className="spinner"></div>
              Scanning...
            </>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
              Run Scan
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default FileUpload;
