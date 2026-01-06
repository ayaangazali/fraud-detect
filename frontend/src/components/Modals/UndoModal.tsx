// src/components/Modals/UndoModal.tsx
import React, { useState } from 'react';
import './UndoModal.css';

interface UndoModalProps {
  item: any;
  onClose: () => void;
  onSuccess: () => void;
}

const REQUIRED_TEXT = 'I acknowledge I am undoing my action';

const UndoModal: React.FC<UndoModalProps> = ({ item, onClose, onSuccess }) => {
  const [acknowledged, setAcknowledged] = useState(false);
  const [confirmText, setConfirmText] = useState('');

  const isValid = acknowledged && confirmText.trim() === REQUIRED_TEXT;

  const handleUndo = () => {
    if (!isValid) {
      alert('Please complete both confirmation steps.');
      return;
    }

    // TODO: API call to undo flag
    console.log('Undoing flag for item:', item.id);
    alert('✅ Flag has been removed. Item returned to In Review queue.');
    onSuccess();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content undo-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header warning">
          <div className="warning-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div>
            <h2>Confirm Undo Action</h2>
            <p>This is a critical operation that will reverse your previous decision.</p>
          </div>
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
              <span className="flagged-info">
                Flagged on <strong>{item?.flaggedDate}</strong>
              </span>
            </div>
            <div className="flag-reason-summary">
              <strong>Original Flag Reason:</strong>
              <p>{item?.flagReason}</p>
            </div>
          </div>

          <div className="warning-box">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <div>
              <strong>What happens when you undo?</strong>
              <ul>
                <li>The flag will be removed from this item</li>
                <li>Item will return to the "In Review" queue</li>
                <li>This action will be logged in the audit trail</li>
                <li>You may need to provide justification to your supervisor</li>
              </ul>
            </div>
          </div>

          <div className="confirmation-steps">
            <h4>To proceed, you must:</h4>
            
            <div className="step">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={acknowledged}
                  onChange={(e) => setAcknowledged(e.target.checked)}
                />
                <span className="checkmark"></span>
                <span className="label-text">
                  I understand that this action is irreversible and will be audited
                </span>
              </label>
            </div>

            <div className="step">
              <label>
                Type the following text exactly to confirm:
                <div className="required-text">"{REQUIRED_TEXT}"</div>
              </label>
              <input
                type="text"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                placeholder="Type the confirmation text here..."
                className={confirmText && confirmText !== REQUIRED_TEXT ? 'invalid' : ''}
              />
              {confirmText && confirmText !== REQUIRED_TEXT && (
                <div className="validation-error">
                  ❌ Text does not match. Please type it exactly as shown.
                </div>
              )}
              {confirmText === REQUIRED_TEXT && (
                <div className="validation-success">
                  ✅ Text confirmed
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="cancel-btn" onClick={onClose}>
            Cancel
          </button>
          <button
            className="undo-btn"
            onClick={handleUndo}
            disabled={!isValid}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 7v6h6"/>
              <path d="M21 17a9 9 0 00-9-9 9 9 0 00-6 2.3L3 13"/>
            </svg>
            Confirm Undo
          </button>
        </div>
      </div>
    </div>
  );
};

export default UndoModal;
