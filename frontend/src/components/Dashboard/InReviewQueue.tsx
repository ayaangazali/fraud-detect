// src/components/Dashboard/InReviewQueue.tsx
import React, { useState } from 'react';
import './InReviewQueue.css';
import FlagModal from '../Modals/FlagModal';

interface InReviewQueueProps {
  activeTab: string;
  userRole: string;
}

// TODO: Replace with actual API data
const mockData = [
  { id: 1, name: 'Ahmad Al-Mansour', type: 'client', matchScore: 98, matchReason: 'Exact name match', actorName: null, blacklistName: 'Ahmad Al-Mansour', source: 'World-Check' },
  { id: 2, name: 'Sarah Holdings LLC', type: 'vendor', matchScore: 92, matchReason: 'High similarity match', actorName: 'John Smith', blacklistName: 'Sarah Holdings', source: 'OFAC' },
  { id: 3, name: 'Omar Khalifa', type: 'client', matchScore: 87, matchReason: 'Name variation match', actorName: null, blacklistName: 'Omar Al-Khalifa', source: 'EU Sanctions' },
  { id: 4, name: 'Tech Solutions Inc', type: 'vendor', matchScore: 85, matchReason: 'Company name match', actorName: 'Mike Johnson', blacklistName: 'Tech Solutions', source: 'UN List' },
  { id: 5, name: 'Mohammed Hassan', type: 'staff', matchScore: 82, matchReason: 'Fuzzy name match', actorName: null, blacklistName: 'Muhammad Hassan', source: 'PEP Database' },
];

const InReviewQueue: React.FC<InReviewQueueProps> = ({ activeTab, userRole }) => {
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [showFlagModal, setShowFlagModal] = useState(false);
  const [selectedItems, setSelectedItems] = useState<number[]>([]);

  // Filter data based on active tab
  const filteredData = activeTab === 'all'
    ? mockData
    : mockData.filter(item => item.type === activeTab.slice(0, -1)); // Remove 's' from 'clients', 'vendors', etc.

  const handleFlag = (item: any) => {
    setSelectedItem(item);
    setShowFlagModal(true);
  };

  const handleCheckbox = (id: number) => {
    setSelectedItems(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const canFlag = userRole === 'screener' || userRole === 'checker';

  return (
    <>
      <div className="in-review-section">
        <div className="section-header">
          <div>
            <h2>In Review Queue</h2>
            <p>New matches not yet in logbook ({filteredData.length} items)</p>
          </div>
          {selectedItems.length > 0 && (
            <div className="bulk-actions">
              <span>{selectedItems.length} selected</span>
              <button className="bulk-flag-btn" disabled={!canFlag}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
                  <line x1="4" y1="22" x2="4" y2="15"/>
                </svg>
                Flag Selected
              </button>
            </div>
          )}
        </div>

        <div className="review-table">
          <table>
            <thead>
              <tr>
                <th style={{ width: '40px' }}>
                  <input
                    type="checkbox"
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedItems(filteredData.map(item => item.id));
                      } else {
                        setSelectedItems([]);
                      }
                    }}
                    checked={selectedItems.length === filteredData.length && filteredData.length > 0}
                  />
                </th>
                <th>Name</th>
                <th>Type</th>
                <th>Match Score</th>
                <th>Blacklist Name</th>
                <th>Actor</th>
                <th>Source</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredData.length === 0 ? (
                <tr>
                  <td colSpan={8} className="empty-state">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <path d="M12 6v6l4 2"/>
                    </svg>
                    <p>No items in review queue</p>
                  </td>
                </tr>
              ) : (
                filteredData.map(item => (
                  <tr key={item.id} className={selectedItems.includes(item.id) ? 'selected' : ''}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedItems.includes(item.id)}
                        onChange={() => handleCheckbox(item.id)}
                      />
                    </td>
                    <td>
                      <strong>{item.name}</strong>
                      <br />
                      <small>{item.matchReason}</small>
                    </td>
                    <td>
                      <span className={`type-badge ${item.type}`}>
                        {item.type}
                      </span>
                    </td>
                    <td>
                      <div className="match-score">
                        <div className={`score-badge ${item.matchScore >= 90 ? 'high' : item.matchScore >= 80 ? 'medium' : 'low'}`}>
                          {item.matchScore}%
                        </div>
                      </div>
                    </td>
                    <td>{item.blacklistName}</td>
                    <td>{item.actorName ? <span className="actor-badge">👤 {item.actorName}</span> : '—'}</td>
                    <td>
                      <span className="source-badge">{item.source}</span>
                    </td>
                    <td>
                      <button
                        className="flag-btn"
                        onClick={() => handleFlag(item)}
                        disabled={!canFlag}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
                          <line x1="4" y1="22" x2="4" y2="15"/>
                        </svg>
                        Flag
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showFlagModal && (
        <FlagModal
          item={selectedItem}
          onClose={() => setShowFlagModal(false)}
          onSuccess={() => {
            setShowFlagModal(false);
            // TODO: Refresh data
          }}
        />
      )}
    </>
  );
};

export default InReviewQueue;
