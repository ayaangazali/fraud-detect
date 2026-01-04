// src/components/ScreeningControls.tsx
import React, { useState } from 'react';
import { api } from '../services/api';
import { CustomerRow, BlacklistRow, ScreeningResponse } from '../types';
import { TranslationKey } from '../i18n/translations';

interface Props {
  customerData: CustomerRow[] | null;
  blacklistData: BlacklistRow[] | null;
  customerErrors: number;
  blacklistErrors: number;
  onScreeningComplete: (results: ScreeningResponse) => void;
  t: (key: TranslationKey) => string;
}

export const ScreeningControls: React.FC<Props> = ({
  customerData,
  blacklistData,
  customerErrors,
  blacklistErrors,
  onScreeningComplete,
  t: _t,
}) => {
  const [threshold, setThreshold] = useState<number>(75);
  const [includeAliases, setIncludeAliases] = useState<boolean>(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasErrors = customerErrors > 0 || blacklistErrors > 0;
  const canRun = customerData && blacklistData && customerData.length > 0 && blacklistData.length > 0;

  const handleRunScreening = async () => {
    if (!canRun) return;

    setLoading(true);
    setError(null);

    try {
      const results = await api.runScreening(
        customerData,
        blacklistData,
        threshold,
        includeAliases
      );
      onScreeningComplete(results);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Screening failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="screening-controls">
      <h2>⚙️ Screening Configuration</h2>

      <div className="controls-grid">
        <div className="control-item">
          <label htmlFor="threshold">
            Similarity Threshold (0-100):
            <span className="help-text">
              Only show matches with similarity ≥ this value. Higher = stricter matching.
            </span>
          </label>
          <input
            id="threshold"
            type="number"
            min="0"
            max="100"
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            disabled={loading}
          />
        </div>

        <div className="control-item">
          <label>
            <input
              type="checkbox"
              checked={includeAliases}
              onChange={(e) => setIncludeAliases(e.target.checked)}
              disabled={loading}
            />
            Include Aliases in Matching
            <span className="help-text">
              When enabled, also matches against alternate names in blacklist
            </span>
          </label>
        </div>
      </div>

      {hasErrors && (
        <div className="warning-message">
          ⚠️ There are validation errors in your uploaded files. 
          Some records may be skipped during screening.
        </div>
      )}

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      <button
        className="run-button"
        onClick={handleRunScreening}
        disabled={!canRun || loading}
      >
        {loading ? '🔄 Running Screening...' : '▶️ Run Screening'}
      </button>

      {!canRun && (
        <p className="info-text">
          Please upload both customer and blacklist files to run screening.
        </p>
      )}
    </div>
  );
};
