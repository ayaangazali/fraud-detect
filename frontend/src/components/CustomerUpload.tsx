// src/components/CustomerUpload.tsx
import React, { useState } from 'react';
import { api } from '../services/api';
import { CustomerUploadResponse } from '../types';

interface Props {
  onUploadComplete: (data: CustomerUploadResponse) => void;
}

export const CustomerUpload: React.FC<Props> = ({ onUploadComplete }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<CustomerUploadResponse | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setData(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await api.uploadCustomers(file);
      setData(result);
      onUploadComplete(result);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-section">
      <h2>📋 Load Customer Names</h2>
      <div className="upload-info">
        <p><strong>Expected columns:</strong></p>
        <ul>
          <li><code>customer_id</code> - Unique identifier</li>
          <li><code>type</code> - individual or corporate</li>
          <li><code>full_name_en</code> - Full name in English</li>
          <li><code>date_of_birth</code> - For individuals (YYYY-MM-DD)</li>
          <li><code>company_reg_no</code> - For corporates</li>
          <li><code>nationality_country</code> - Nationality or country</li>
        </ul>
      </div>

      <div className="upload-controls">
        <input
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileChange}
          disabled={loading}
        />
        <button onClick={handleUpload} disabled={loading || !file}>
          {loading ? 'Uploading...' : 'Upload & Validate'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {data && (
        <div className="upload-results">
          <div className="stats">
            <span>Total rows: {data.totalRows}</span>
            <span className={data.validRows === data.totalRows ? 'success' : 'warning'}>
              Valid rows: {data.validRows}
            </span>
            {data.errors.length > 0 && (
              <span className="error">Errors: {data.errors.length}</span>
            )}
          </div>

          {data.errors.length > 0 && (
            <div className="validation-errors">
              <h4>⚠️ Validation Errors:</h4>
              <table>
                <thead>
                  <tr>
                    <th>Row</th>
                    <th>Field</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {data.errors.slice(0, 20).map((err, idx) => (
                    <tr key={idx}>
                      <td>{err.row}</td>
                      <td><code>{err.field}</code></td>
                      <td>{err.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {data.errors.length > 20 && (
                <p className="more-errors">
                  ... and {data.errors.length - 20} more errors
                </p>
              )}
            </div>
          )}

          <div className="preview-table">
            <h4>Preview (first 20 rows):</h4>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Customer ID</th>
                    <th>Type</th>
                    <th>Full Name</th>
                    <th>DOB/Reg No</th>
                    <th>Nationality</th>
                  </tr>
                </thead>
                <tbody>
                  {data.preview.map((row, idx) => (
                    <tr key={idx}>
                      <td>{row.customer_id}</td>
                      <td>{row.type}</td>
                      <td>{row.full_name_en}</td>
                      <td>
                        {row.type === 'individual'
                          ? row.date_of_birth
                          : row.company_reg_no}
                      </td>
                      <td>{row.nationality_country}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
