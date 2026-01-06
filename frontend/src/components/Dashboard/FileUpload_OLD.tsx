// src/components/Dashboard/FileUpload.tsx
import React, { useState, useRef } from 'react';
import './FileUpload.css';

const FileUpload: React.FC = () => {
  const [blacklistFile, setBlacklistFile] = useState<File | null>(null);
  const [kamcoFile, setKamcoFile] = useState<File | null>(null);
  const [scanning, setScanning] = useState(false);

  const blacklistInputRef = useRef<HTMLInputElement>(null);
  const kamcoInputRef = useRef<HTMLInputElement>(null);

  const handleBlacklistSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setBlacklistFile(e.target.files[0]);
    }
  };

  const handleKamcoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setKamcoFile(e.target.files[0]);
    }
  };

  const handleRunScan = async () => {
    if (!blacklistFile || !kamcoFile) {
      alert('Please upload both Blacklist and Kamco dataset files');
      return;
    }

    setScanning(true);
    try {
      // TODO: Replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      alert('✅ Scan completed! Check In Review queue for new matches.');
    } catch (error) {
      alert('❌ Scan failed. Please try again.');
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="file-upload-section">
      <div className="section-header">
        <h2>Upload & Scan</h2>
        <p>Upload blacklist Excel and Kamco dataset to run screening</p>
      </div>

      <div className="upload-grid">
        {/* Blacklist Upload */}
        <div className="upload-card">
          <div className="upload-header">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="12" y1="18" x2="12" y2="12"/>
              <line x1="9" y1="15" x2="15" y2="15"/>
            </svg>
            <h3>Blacklist Excel</h3>
          </div>

          <div
            className="drop-zone"
            onClick={() => blacklistInputRef.current?.click()}
          >
            <input
              ref={blacklistInputRef}
              type="file"
              accept=".xlsx"
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
                <p className="hint">Excel file (.xlsx)</p>
              </div>
            )}
          </div>
        </div>

        {/* Kamco Dataset Upload */}
        <div className="upload-card">
          <div className="upload-header">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
              <polyline points="13 2 13 9 20 9"/>
            </svg>
            <h3>Kamco Dataset</h3>
          </div>

          <div
            className="drop-zone"
            onClick={() => kamcoInputRef.current?.click()}
          >
            <input
              ref={kamcoInputRef}
              type="file"
              accept=".xlsx"
              onChange={handleKamcoSelect}
              style={{ display: 'none' }}
            />

            {kamcoFile ? (
              <div className="file-selected">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
                <p className="file-name">{kamcoFile.name}</p>
                <p className="file-size">{(kamcoFile.size / 1024).toFixed(2)} KB</p>
                <button
                  className="remove-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    setKamcoFile(null);
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
                <p className="hint">Excel file (.xlsx)</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Run Scan Button */}
      <div className="scan-action">
        <button
          className="scan-btn"
          onClick={handleRunScan}
          disabled={!blacklistFile || !kamcoFile || scanning}
        >
          {scanning ? (
            <>
              <span className="spinner"></span>
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
