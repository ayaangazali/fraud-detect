// src/components/ScreeningListUpload.tsx
import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../services/api';

interface ScreeningListUploadProps {
  onUploadComplete: (data: any) => void;
}

const ScreeningListUpload: React.FC<ScreeningListUploadProps> = ({ onUploadComplete }) => {
  const { t } = useTranslation();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string>('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile: File) => {
    if (!selectedFile.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }

    setFile(selectedFile);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      const response = await api.uploadScreeningList(file);
      onUploadComplete(response);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to upload screening list');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-card">
      <div className="upload-header">
        <span className="upload-icon">📋</span>
        <h3>{t('uploadScreeningList') || 'Upload Screening List'}</h3>
      </div>

      <div
        className={`upload-drop-zone ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={(e) => e.target.files && handleFileSelect(e.target.files[0])}
          style={{ display: 'none' }}
        />

        {file ? (
          <div className="file-selected">
            <span className="file-icon">📄</span>
            <div className="file-info">
              <p className="file-name">{file.name}</p>
              <p className="file-size">{(file.size / 1024).toFixed(2)} KB</p>
            </div>
            <button
              className="remove-file-btn"
              onClick={(e) => {
                e.stopPropagation();
                setFile(null);
              }}
            >
              ✕
            </button>
          </div>
        ) : (
          <div className="drop-zone-content">
            <svg
              className="upload-cloud-icon"
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <p className="drop-zone-text">
              <span className="drop-zone-highlight">Click to upload</span> or drag and drop
            </p>
            <p className="drop-zone-hint">CSV file with screening entries</p>
          </div>
        )}
      </div>

      {error && (
        <div className="upload-error">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <button
        className="upload-button"
        onClick={handleUpload}
        disabled={!file || uploading}
      >
        {uploading ? (
          <>
            <span className="spinner"></span>
            {t('uploading') || 'Uploading...'}
          </>
        ) : (
          <>
            <span>⬆️</span>
            {t('uploadFile') || 'Upload File'}
          </>
        )}
      </button>

      <div className="upload-info">
        <p className="info-title">Required columns:</p>
        <ul className="info-list">
          <li>full_name (required)</li>
          <li>alias_alternate_names (optional)</li>
          <li>dob_or_reg_no (optional)</li>
          <li>nationality_country (optional)</li>
          <li>source (optional)</li>
        </ul>
      </div>
    </div>
  );
};

export default ScreeningListUpload;
