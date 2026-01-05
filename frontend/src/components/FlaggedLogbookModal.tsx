import { useEffect, useState } from 'react';
import { api } from '../services/api';

interface FlaggedLogbookModalProps {
  onClose: () => void;
}

interface FlaggedEntry {
  flagged_id: string;
  customer_id: string;
  customer_name: string;
  screening_name: string;
  similarity_score: number;
  match_type: string;
  user_comments: string;
  flagged_date: string;
  flagged_by: string;
  screening_source: string;
}

export default function FlaggedLogbookModal({ onClose }: FlaggedLogbookModalProps) {
  const [entries, setEntries] = useState<FlaggedEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  useEffect(() => {
    loadLogbook();
  }, []);

  const loadLogbook = async () => {
    setLoading(true);
    try {
      const response = await api.getFlaggedLogbook(100, 0);
      setEntries(response.entries || []);
    } catch (error) {
      console.error('Error loading logbook:', error);
      alert('Failed to load flagged logbook');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const blob = await api.exportFlaggedCases();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const date = new Date().toISOString().split('T')[0];
      a.download = `KAMCO_Flagged_Cases_${date}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      alert('✅ Exported successfully!');
    } catch (error) {
      console.error('Export failed:', error);
      alert('❌ Export failed');
    } finally {
      setExporting(false);
    }
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 95) return '#ff6b6b';
    if (score >= 85) return '#fd7e14';
    if (score >= 75) return '#fab005';
    return '#51cf66';
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="logbook-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>📚 Flagged Log Book</h2>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="logbook-modal-body">
          {loading ? (
            <div className="logbook-loading">
              <div className="spinner"></div>
              <p>Loading flagged cases...</p>
            </div>
          ) : entries.length === 0 ? (
            <div className="logbook-empty">
              <p>📋 No flagged cases yet</p>
              <p className="logbook-empty-subtitle">Cases marked as flagged during review will appear here</p>
            </div>
          ) : (
            <>
              <div className="logbook-header-actions">
                <p className="logbook-count">
                  <strong>{entries.length}</strong> flagged {entries.length === 1 ? 'case' : 'cases'}
                </p>
                <button 
                  className="logbook-export-btn"
                  onClick={handleExport}
                  disabled={exporting}
                >
                  {exporting ? '⏳ Exporting...' : '📊 Export to Excel'}
                </button>
              </div>

              <div className="logbook-table-container">
                <table className="logbook-table">
                  <thead>
                    <tr>
                      <th>Flagged ID</th>
                      <th>Customer Name</th>
                      <th>Screening Match</th>
                      <th>Score</th>
                      <th>Type</th>
                      <th>Source</th>
                      <th>Comments</th>
                      <th>Date</th>
                      <th>Flagged By</th>
                    </tr>
                  </thead>
                  <tbody>
                    {entries.map((entry, idx) => (
                      <tr key={idx}>
                        <td className="logbook-id">{entry.flagged_id}</td>
                        <td className="logbook-name">{entry.customer_name}</td>
                        <td className="logbook-name">{entry.screening_name}</td>
                        <td>
                          <span 
                            className="logbook-score"
                            style={{ 
                              backgroundColor: getSimilarityColor(entry.similarity_score),
                              color: 'white'
                            }}
                          >
                            {entry.similarity_score}%
                          </span>
                        </td>
                        <td className="logbook-type">{entry.match_type.toUpperCase()}</td>
                        <td className="logbook-source">{entry.screening_source}</td>
                        <td className="logbook-comments">{entry.user_comments}</td>
                        <td className="logbook-date">
                          {new Date(entry.flagged_date).toLocaleString()}
                        </td>
                        <td className="logbook-by">{entry.flagged_by || 'System'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>

        <div className="modal-footer">
          <button className="modal-btn modal-btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
