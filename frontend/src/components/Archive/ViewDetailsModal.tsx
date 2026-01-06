import { useEffect } from 'react';

interface ViewDetailsModalProps {
  match: any;
  onClose: () => void;
}

export default function ViewDetailsModal({ match, onClose }: ViewDetailsModalProps) {
  // Close on ESC key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  const getSimilarityColor = (score: number) => {
    if (score >= 95) return 'critical';
    if (score >= 85) return 'high';
    if (score >= 75) return 'medium';
    return 'low';
  };

  const getSimilarityLabel = (score: number) => {
    if (score >= 95) return 'Critical Match';
    if (score >= 85) return 'High Risk';
    if (score >= 75) return 'Medium Risk';
    return 'Low Risk';
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🔍 Match Details</h2>
          <button className="modal-close-btn" onClick={onClose} title="Close (ESC)">
            ✕
          </button>
        </div>

        <div className="modal-body">
          {/* Similarity Score Badge */}
          <div className={`similarity-badge-large ${getSimilarityColor(match.similarity_score)}`}>
            <div className="similarity-percentage">{match.similarity_score}%</div>
            <div className="similarity-label">{getSimilarityLabel(match.similarity_score)}</div>
          </div>

          {/* Split Screen Comparison */}
          <div className="modal-split-view">
            {/* KAMCO Client Side (Blue) */}
            <div className="modal-side kamco-side">
              <div className="modal-side-header">
                <h3>📋 KAMCO Client Data</h3>
              </div>
              <div className="modal-details">
                <div className="detail-row">
                  <span className="detail-label">Client ID:</span>
                  <span className="detail-value">{match.customer_id}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Full Name:</span>
                  <span className="detail-value highlight-name">{match.customer_name}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Type:</span>
                  <span className="detail-value capitalize">{match.customer_type}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">DOB / Reg No:</span>
                  <span className="detail-value">{match.customer_dob}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Nationality:</span>
                  <span className="detail-value">{match.customer_nationality}</span>
                </div>
                {match.customer_department && (
                  <div className="detail-row">
                    <span className="detail-label">Department:</span>
                    <span className="detail-value">{match.customer_department}</span>
                  </div>
                )}
                {match.customer_position && (
                  <div className="detail-row">
                    <span className="detail-label">Position:</span>
                    <span className="detail-value">{match.customer_position}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Screening List Side (Purple) */}
            <div className="modal-side screening-side">
              <div className="modal-side-header">
                <h3>⚠️ Screening List Match</h3>
              </div>
              <div className="modal-details">
                <div className="detail-row">
                  <span className="detail-label">Full Name:</span>
                  <span className="detail-value highlight-name">{match.screening_name}</span>
                </div>
                {match.screening_aliases && (
                  <div className="detail-row">
                    <span className="detail-label">Aliases:</span>
                    <span className="detail-value aliases">{match.screening_aliases}</span>
                  </div>
                )}
                <div className="detail-row">
                  <span className="detail-label">DOB / Reg No:</span>
                  <span className="detail-value">{match.screening_dob || 'Not provided'}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Nationality:</span>
                  <span className="detail-value">{match.screening_nationality || 'Not provided'}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Source:</span>
                  <span className="detail-value source-badge">{match.screening_source}</span>
                </div>
                {match.screening_date && (
                  <div className="detail-row">
                    <span className="detail-label">Effective Date:</span>
                    <span className="detail-value">{match.screening_date}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Match Information */}
          <div className="match-info-section">
            <h4>Match Analysis</h4>
            <div className="match-info-grid">
              <div className="match-info-item">
                <span className="info-label">Match Type:</span>
                <span className={`match-type-badge ${match.match_type}`}>
                  {match.match_type.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              <div className="match-info-item">
                <span className="info-label">Match Reason:</span>
                <span className="info-value">{match.match_reason}</span>
              </div>
            </div>
          </div>
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
