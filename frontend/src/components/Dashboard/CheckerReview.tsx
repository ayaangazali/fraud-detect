// src/components/Dashboard/CheckerReview.tsx
import React, { useState } from 'react';
import './CheckerReview.css';

interface CheckerReviewProps {
  activeTab: string;
  userRole: string;
}

// TODO: Replace with actual API data
const mockFlaggedData = [
  {
    id: 1,
    name: 'Ahmad Al-Mansour',
    type: 'client',
    blacklistName: 'Ahmad Al-Mansour',
    source: 'World-Check',
    flaggedBy: 'screener',
    flagReason: 'Exact name match with high-risk PEP. Customer has same DOB as blacklisted individual.',
    flaggedDate: '2024-01-15 14:30',
    status: 'pending_review',
    matchScore: 98,
    actorName: null,
    kamcoData: {
      accountNumber: 'KC-2024-0001',
      dateOpened: '2023-05-10',
      accountType: 'Investment Account',
      balance: '$2,500,000',
    },
  },
  {
    id: 2,
    name: 'Sarah Holdings LLC',
    type: 'vendor',
    blacklistName: 'Sarah Holdings',
    source: 'OFAC',
    flaggedBy: 'screener',
    flagReason: 'Company name matches OFAC sanctions list. Actor "John Smith" has past involvement with sanctioned entities.',
    flaggedDate: '2024-01-14 11:20',
    status: 'pending_review',
    matchScore: 92,
    actorName: 'John Smith',
    kamcoData: {
      vendorId: 'VEN-5678',
      dateRegistered: '2022-08-20',
      serviceType: 'Financial Advisory',
      totalContracts: '15 active contracts',
    },
  },
  {
    id: 3,
    name: 'Omar Khalifa',
    type: 'client',
    blacklistName: 'Omar Al-Khalifa',
    source: 'EU Sanctions',
    flaggedBy: 'checker',
    flagReason: 'Name variation with known terrorist affiliate. Recommend immediate escalation.',
    flaggedDate: '2024-01-13 16:45',
    status: 'pending_review',
    matchScore: 87,
    actorName: null,
    kamcoData: {
      accountNumber: 'KC-2024-0052',
      dateOpened: '2024-01-05',
      accountType: 'Brokerage Account',
      balance: '$850,000',
    },
  },
];

const CheckerReview: React.FC<CheckerReviewProps> = ({ activeTab, userRole }) => {
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [recheckReason, setRecheckReason] = useState('');
  const [showRecheckModal, setShowRecheckModal] = useState(false);

  // Only Checker can access this component
  if (userRole !== 'checker') {
    return (
      <div className="checker-review-section">
        <div className="access-denied">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          <h3>Access Denied</h3>
          <p>Only Checker role can access the review console.</p>
        </div>
      </div>
    );
  }

  // Filter data based on active tab
  const filteredData = activeTab === 'all'
    ? mockFlaggedData
    : mockFlaggedData.filter(item => item.type === activeTab.slice(0, -1));

  const handleViewDetails = (item: any) => {
    setSelectedItem(item);
    setShowDetails(true);
  };

  const handleApprove = (item: any) => {
    if (confirm(`Are you sure you want to APPROVE this flagged item?\n\n${item.name} - ${item.type}\n\nThis will mark it as cleared and add to logbook.`)) {
      // TODO: API call to approve
      console.log('Approving item:', item.id);
      alert('✅ Item approved and added to logbook.');
    }
  };

  const handleRequestRecheck = (item: any) => {
    setSelectedItem(item);
    setShowRecheckModal(true);
  };

  const handleOverride = (item: any) => {
    if (confirm(`⚠️ OVERRIDE ACTION\n\nAre you sure you want to override this flag?\n\n${item.name} - ${item.type}\n\nThis is a critical action that will be audited and may require supervisor approval.`)) {
      const overrideReason = prompt('Enter override reason (required):');
      if (overrideReason && overrideReason.trim().length >= 20) {
        // TODO: API call to override
        console.log('Overriding item:', item.id, 'Reason:', overrideReason);
        alert('✅ Override recorded. Item marked as cleared with override status.');
      } else {
        alert('Override reason must be at least 20 characters.');
      }
    }
  };

  const submitRecheck = () => {
    if (recheckReason.trim().length < 15) {
      alert('Re-check reason must be at least 15 characters.');
      return;
    }

    // TODO: API call to request re-check
    console.log('Requesting re-check for:', selectedItem.id, 'Reason:', recheckReason);
    alert(`✅ Re-check request sent!\n\nEmail notification sent to: ${selectedItem.flaggedBy}\n\nReason: ${recheckReason}`);
    setShowRecheckModal(false);
    setRecheckReason('');
  };

  return (
    <>
      <div className="checker-review-section">
        <div className="section-header">
          <div className="header-content">
            <div className="title-badge">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 11l3 3L22 4"/>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
              </svg>
              <span className="role-badge">CHECKER CONSOLE</span>
            </div>
            <h2>Review Flagged Items</h2>
            <p>Review and make decisions on flagged compliance items ({filteredData.length} pending)</p>
          </div>
        </div>

        {filteredData.length === 0 ? (
          <div className="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 11l3 3L22 4"/>
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
            </svg>
            <h3>No Items Pending Review</h3>
            <p>All flagged items have been processed.</p>
          </div>
        ) : (
          <div className="review-items">
            {filteredData.map(item => (
              <div key={item.id} className="review-card">
                <div className="card-header">
                  <div className="item-info">
                    <h3>{item.name}</h3>
                    <div className="badges">
                      <span className={`type-badge ${item.type}`}>{item.type}</span>
                      <span className={`score-badge ${item.matchScore >= 90 ? 'high' : item.matchScore >= 80 ? 'medium' : 'low'}`}>
                        {item.matchScore}% Match
                      </span>
                    </div>
                  </div>
                  <button className="details-btn" onClick={() => handleViewDetails(item)}>
                    View Full Details
                  </button>
                </div>

                <div className="card-body">
                  <div className="info-section">
                    <div className="info-row">
                      <span className="label">Blacklist Name:</span>
                      <span className="value">{item.blacklistName}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Source:</span>
                      <span className="value source-badge">{item.source}</span>
                    </div>
                    {item.actorName && (
                      <div className="info-row">
                        <span className="label">Actor:</span>
                        <span className="value actor-badge">👤 {item.actorName}</span>
                      </div>
                    )}
                    <div className="info-row">
                      <span className="label">Flagged By:</span>
                      <span className="value">{item.flaggedBy} on {item.flaggedDate}</span>
                    </div>
                  </div>

                  <div className="flag-reason-box">
                    <label>Flag Reason:</label>
                    <p>{item.flagReason}</p>
                  </div>

                  <div className="kamco-data-preview">
                    <label>Kamco Data Preview:</label>
                    <div className="data-grid">
                      {Object.entries(item.kamcoData).map(([key, value]) => (
                        <div key={key} className="data-item">
                          <span className="data-label">{key.replace(/([A-Z])/g, ' $1').trim()}:</span>
                          <span className="data-value">{value as string}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="card-actions">
                  <button className="action-btn approve-btn" onClick={() => handleApprove(item)}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                      <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                    Approve
                  </button>
                  <button className="action-btn recheck-btn" onClick={() => handleRequestRecheck(item)}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
                    </svg>
                    Request Re-check
                  </button>
                  <button className="action-btn override-btn" onClick={() => handleOverride(item)}>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                      <path d="M9 12l2 2 4-4"/>
                    </svg>
                    Override
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Re-check Modal */}
      {showRecheckModal && (
        <div className="modal-overlay" onClick={() => setShowRecheckModal(false)}>
          <div className="modal-content recheck-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Request Re-check</h2>
              <button className="close-btn" onClick={() => setShowRecheckModal(false)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>

            <div className="modal-body">
              <div className="item-summary">
                <h3>{selectedItem?.name}</h3>
                <div className="summary-badges">
                  <span className={`type-badge ${selectedItem?.type}`}>{selectedItem?.type}</span>
                  <span className="match-score">{selectedItem?.matchScore}% Match</span>
                </div>
              </div>

              <div className="info-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="16" x2="12" y2="12"/>
                  <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
                <div>
                  <strong>What happens next?</strong>
                  <p>An email notification will be sent to <strong>{selectedItem?.flaggedBy}</strong> requesting additional investigation or documentation.</p>
                </div>
              </div>

              <div className="form-group">
                <label>
                  Re-check Reason <span className="required">*</span>
                </label>
                <textarea
                  value={recheckReason}
                  onChange={(e) => setRecheckReason(e.target.value)}
                  placeholder="Explain what additional information or investigation is needed (minimum 15 characters)..."
                  rows={5}
                />
                <div className="char-count">
                  {recheckReason.length} / 15 characters minimum
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="cancel-btn" onClick={() => setShowRecheckModal(false)}>
                Cancel
              </button>
              <button
                className="recheck-submit-btn"
                onClick={submitRecheck}
                disabled={recheckReason.trim().length < 15}
              >
                Send Re-check Request
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Details Modal */}
      {showDetails && selectedItem && (
        <div className="modal-overlay" onClick={() => setShowDetails(false)}>
          <div className="modal-content details-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Complete Item Details</h2>
              <button className="close-btn" onClick={() => setShowDetails(false)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>

            <div className="modal-body">
              <div className="details-grid">
                <div className="detail-section">
                  <h4>Match Information</h4>
                  <div className="detail-item">
                    <span>Kamco Name:</span>
                    <strong>{selectedItem.name}</strong>
                  </div>
                  <div className="detail-item">
                    <span>Blacklist Name:</span>
                    <strong>{selectedItem.blacklistName}</strong>
                  </div>
                  <div className="detail-item">
                    <span>Match Score:</span>
                    <strong className={`score-${selectedItem.matchScore >= 90 ? 'high' : 'medium'}`}>
                      {selectedItem.matchScore}%
                    </strong>
                  </div>
                  <div className="detail-item">
                    <span>Source:</span>
                    <strong>{selectedItem.source}</strong>
                  </div>
                  {selectedItem.actorName && (
                    <div className="detail-item">
                      <span>Actor:</span>
                      <strong>👤 {selectedItem.actorName}</strong>
                    </div>
                  )}
                </div>

                <div className="detail-section">
                  <h4>Kamco Data</h4>
                  {Object.entries(selectedItem.kamcoData).map(([key, value]) => (
                    <div key={key} className="detail-item">
                      <span>{key.replace(/([A-Z])/g, ' $1').trim()}:</span>
                      <strong>{value as string}</strong>
                    </div>
                  ))}
                </div>

                <div className="detail-section full-width">
                  <h4>Flag Information</h4>
                  <div className="detail-item">
                    <span>Flagged By:</span>
                    <strong>{selectedItem.flaggedBy}</strong>
                  </div>
                  <div className="detail-item">
                    <span>Flagged Date:</span>
                    <strong>{selectedItem.flaggedDate}</strong>
                  </div>
                  <div className="detail-item">
                    <span>Reason:</span>
                    <div className="reason-text">{selectedItem.flagReason}</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="cancel-btn" onClick={() => setShowDetails(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default CheckerReview;
