// src/components/Modals/FlagModal.tsx
import React, { useState } from 'react';
import './FlagModal.css';

interface FlagModalProps {
  item: any;
  onClose: () => void;
  onSuccess: () => void;
}

const FlagModal: React.FC<FlagModalProps> = ({ item, onClose, onSuccess }) => {
  const [reason, setReason] = useState('');
  const [showUndo, setShowUndo] = useState(false);

  const handleFlag = () => {
    if (reason.trim().length < 10) {
      alert('Please provide a reason with at least 10 characters.');
      return;
    }

    // TODO: API call to flag item
    console.log('Flagging item:', { itemId: item.id, reason });

    // Show immediate undo option
    setShowUndo(true);

    // Auto-close after 5 seconds if no undo
    setTimeout(() => {
      if (showUndo) {
        onSuccess();
      }
    }, 5000);
  };

  const handleUndo = () => {
    // TODO: API call to undo flag
    console.log('Undoing flag for item:', item.id);
    alert('✅ Flag action undone');
    onClose();
  };

  if (showUndo) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content undo-confirmation" onClick={(e) => e.stopPropagation()}>
          <div className="success-icon">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <h2>Item Flagged Successfully!</h2>
          <p>The item has been moved to your flagged items list.</p>
          
          <div className="undo-prompt">
            <p>Made a mistake?</p>
            <button className="undo-btn" onClick={handleUndo}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 7v6h6"/>
                <path d="M21 17a9 9 0 00-9-9 9 9 0 00-6 2.3L3 13"/>
              </svg>
              Undo Flag
            </button>
          </div>

          <button className="continue-btn" onClick={onSuccess}>
            Continue
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content flag-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Flag Item for Review</h2>
          <button className="close-btn" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div className="modal-body">
          <div className="item-summary">
            <h3>{item?.name}</h3>
            <div className="summary-details">
              <span className={`type-badge ${item?.type}`}>{item?.type}</span>
              <span className="match-info">
                Match: <strong>{item?.matchScore}%</strong> with {item?.blacklistName}
              </span>
            </div>
          </div>

          <div className="form-group">
            <label>
              Flag Reason <span className="required">*</span>
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Provide a detailed reason for flagging this item (minimum 10 characters)..."
              rows={5}
            />
            <div className="char-count">
              {reason.length} / 10 characters minimum
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
              <p>This item will be moved to your Flagged Items list and can be reviewed by a Checker. You'll have an immediate option to undo this action.</p>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="cancel-btn" onClick={onClose}>
            Cancel
          </button>
          <button
            className="flag-btn"
            onClick={handleFlag}
            disabled={reason.trim().length < 10}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
              <line x1="4" y1="22" x2="4" y2="15"/>
            </svg>
            Flag Item
          </button>
        </div>
      </div>
    </div>
  );
};

export default FlagModal;
