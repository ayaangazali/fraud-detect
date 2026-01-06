// src/components/Dashboard/FlaggedItems.tsx
import React, { useState } from 'react';
import './FlaggedItems.css';
import UndoModal from '../Modals/UndoModal';

interface FlaggedItemsProps {
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
    status: 'approved',
    matchScore: 92,
    actorName: 'John Smith',
    approvedBy: 'checker',
    approvedDate: '2024-01-15 09:00',
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
    status: 'recheck_requested',
    matchScore: 87,
    requestedBy: 'checker',
    recheckReason: 'Need additional documentation on source of funds',
  },
];

const FlaggedItems: React.FC<FlaggedItemsProps> = ({ activeTab, userRole }) => {
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [showUndoModal, setShowUndoModal] = useState(false);

  // Filter data based on active tab
  const filteredData = activeTab === 'all'
    ? mockFlaggedData
    : mockFlaggedData.filter(item => item.type === activeTab.slice(0, -1));

  const handleUndo = (item: any) => {
    setSelectedItem(item);
    setShowUndoModal(true);
  };

  const handleGenerateReport = (item: any) => {
    alert(`Generating report for: ${item.name}\n\nThis will create a PDF with:\n- Match details\n- Flag reason\n- Screening history\n- Recommendation`);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: any = {
      pending_review: { label: 'Pending Review', class: 'pending' },
      approved: { label: 'Approved', class: 'approved' },
      recheck_requested: { label: 'Re-check Requested', class: 'recheck' },
      overridden: { label: 'Overridden', class: 'override' },
    };
    const config = statusConfig[status] || { label: status, class: 'default' };
    return <span className={`status-badge ${config.class}`}>{config.label}</span>;
  };

  const canUndo = userRole === 'screener' || userRole === 'checker';

  return (
    <>
      <div className="flagged-items-section">
        <div className="section-header">
          <div>
            <h2>Flagged Items</h2>
            <p>Items flagged for compliance review ({filteredData.length} items)</p>
          </div>
          <button className="generate-cumulative-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            Generate Cumulative Report
          </button>
        </div>

        <div className="flagged-cards">
          {filteredData.length === 0 ? (
            <div className="empty-state">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
                <line x1="4" y1="22" x2="4" y2="15"/>
              </svg>
              <p>No flagged items</p>
            </div>
          ) : (
            filteredData.map(item => (
              <div key={item.id} className="flagged-card">
                <div className="card-header">
                  <div className="card-title">
                    <h3>{item.name}</h3>
                    <span className={`type-badge ${item.type}`}>{item.type}</span>
                  </div>
                  {getStatusBadge(item.status)}
                </div>

                <div className="card-body">
                  <div className="info-grid">
                    <div className="info-item">
                      <label>Match Score</label>
                      <div className={`score-badge ${item.matchScore >= 90 ? 'high' : item.matchScore >= 80 ? 'medium' : 'low'}`}>
                        {item.matchScore}%
                      </div>
                    </div>
                    <div className="info-item">
                      <label>Blacklist Name</label>
                      <span>{item.blacklistName}</span>
                    </div>
                    <div className="info-item">
                      <label>Source</label>
                      <span className="source-badge">{item.source}</span>
                    </div>
                    {item.actorName && (
                      <div className="info-item">
                        <label>Actor</label>
                        <span className="actor-badge">👤 {item.actorName}</span>
                      </div>
                    )}
                  </div>

                  <div className="flag-reason">
                    <label>Flag Reason</label>
                    <p>{item.flagReason}</p>
                  </div>

                  <div className="meta-info">
                    <span>
                      <strong>Flagged by:</strong> {item.flaggedBy}
                    </span>
                    <span>
                      <strong>Date:</strong> {item.flaggedDate}
                    </span>
                  </div>

                  {item.status === 'approved' && (
                    <div className="approval-info">
                      ✅ Approved by <strong>{item.approvedBy}</strong> on {item.approvedDate}
                    </div>
                  )}

                  {item.status === 'recheck_requested' && (
                    <div className="recheck-info">
                      🔄 Re-check requested by <strong>{item.requestedBy}</strong>
                      <p>{item.recheckReason}</p>
                    </div>
                  )}
                </div>

                <div className="card-actions">
                  <button className="report-btn" onClick={() => handleGenerateReport(item)}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                    </svg>
                    Generate Report
                  </button>
                  {item.status !== 'approved' && (
                    <button
                      className="undo-btn"
                      onClick={() => handleUndo(item)}
                      disabled={!canUndo}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M3 7v6h6"/>
                        <path d="M21 17a9 9 0 00-9-9 9 9 0 00-6 2.3L3 13"/>
                      </svg>
                      Undo Flag
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showUndoModal && (
        <UndoModal
          item={selectedItem}
          onClose={() => setShowUndoModal(false)}
          onSuccess={() => {
            setShowUndoModal(false);
            // TODO: Refresh data
          }}
        />
      )}
    </>
  );
};

export default FlaggedItems;
