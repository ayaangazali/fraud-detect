// src/components/ReviewMode.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

interface ReviewModeProps {
  matches: any[];
  onExit: () => void;
  onComplete: (summary: ReviewSummary) => void;
}

interface ReviewSummary {
  total: number;
  flagged: number;
  safe: number;
  skipped: number;
}

const ReviewMode: React.FC<ReviewModeProps> = ({ matches, onExit, onComplete }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [comments, setComments] = useState('');
  const [processing, setProcessing] = useState(false);
  const [generatingPDF, setGeneratingPDF] = useState(false);
  const [reviewedMatches, setReviewedMatches] = useState<any[]>([]);
  const [flaggedMatches, setFlaggedMatches] = useState<any[]>([]);
  const [flaggedCount, setFlaggedCount] = useState(0);
  const [safeCount, setSafeCount] = useState(0);
  const [skippedCount, setSkippedCount] = useState(0);

  const currentMatch = matches[currentIndex];
  const progress = ((currentIndex + 1) / matches.length) * 100;
  const isLastMatch = currentIndex === matches.length - 1;

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (processing) return;
      
      // Don't trigger shortcuts when typing in textarea
      const target = e.target as HTMLElement;
      if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') {
        return;
      }
      
      if (e.key === 'f' || e.key === 'F') {
        if (comments.trim().length >= 10) {
          handleFlag();
        }
      } else if (e.key === 's' || e.key === 'S') {
        handleSafe();
      } else if (e.key === 'ArrowRight') {
        handleSkip();
      } else if (e.key === 'ArrowLeft' && currentIndex > 0) {
        handlePrevious();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentIndex, comments, processing]);

  const moveToNext = useCallback(() => {
    if (isLastMatch) {
      // Complete review
      onComplete({
        total: matches.length,
        flagged: flaggedCount,
        safe: safeCount,
        skipped: skippedCount,
      });
    } else {
      setCurrentIndex(currentIndex + 1);
      setComments('');
    }
  }, [currentIndex, isLastMatch, flaggedCount, safeCount, skippedCount, matches.length, onComplete]);

  const handleFlag = async () => {
    if (comments.trim().length < 10) {
      alert('Please provide investigation notes (minimum 10 characters)');
      return;
    }

    setProcessing(true);
    try {
      await api.flagCase(currentMatch, comments);
      
      const flaggedMatch = { ...currentMatch, status: 'flagged', user_comments: comments };
      setReviewedMatches([...reviewedMatches, flaggedMatch]);
      setFlaggedMatches([...flaggedMatches, flaggedMatch]);
      setFlaggedCount(flaggedCount + 1);
      
      showToast('Case flagged and added to log book', 'success');
      moveToNext();
    } catch (error: any) {
      showToast(error.response?.data?.error || 'Failed to flag case', 'error');
    } finally {
      setProcessing(false);
    }
  };

  const handleSafe = async () => {
    setProcessing(true);
    try {
      await api.markSafe(currentMatch.customer_id, currentMatch.matched_blacklist_name);
      
      setReviewedMatches([...reviewedMatches, { ...currentMatch, status: 'safe' }]);
      setSafeCount(safeCount + 1);
      
      showToast('Case marked as safe', 'success');
      moveToNext();
    } catch (error: any) {
      showToast(error.response?.data?.error || 'Failed to mark as safe', 'error');
    } finally {
      setProcessing(false);
    }
  };

  const handleSkip = () => {
    setSkippedCount(skippedCount + 1);
    moveToNext();
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setComments('');
    }
  };

  const handleGeneratePDF = async () => {
    setGeneratingPDF(true);
    try {
      const reviewData = {
        summary: {
          total: matches.length,
          flagged: flaggedCount,
          safe: safeCount,
          skipped: skippedCount,
        },
        matches: matches,
        flaggedMatches: flaggedMatches,
      };

      const blob = await api.generatePDF(reviewData);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const date = new Date().toISOString().split('T')[0];
      a.download = `KAMCO_Screening_Report_${date}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      showToast('✅ PDF report generated successfully!', 'success');
    } catch (error) {
      console.error('PDF generation failed:', error);
      showToast('❌ Failed to generate PDF report', 'error');
    } finally {
      setGeneratingPDF(false);
    }
  };

  const showToast = (message: string, type: 'success' | 'error') => {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  };

  const getSimilarityColor = (score: number) => {
    if (score >= 90) return '#ef4444'; // red
    if (score >= 75) return '#f59e0b'; // orange
    return '#3b82f6'; // blue
  };

  if (!currentMatch) return null;

  return (
    <div className="review-mode">
      {/* Header */}
      <div className="review-header">
        <button className="exit-review-btn" onClick={onExit}>
          ← Exit Review Mode
        </button>
        
        <div className="review-progress-info">
          <span className="progress-text">
            Reviewing {currentIndex + 1} of {matches.length}
          </span>
          <div className="review-stats">
            <span className="stat flagged">⚠️ Flagged: {flaggedCount}</span>
            <span className="stat safe">✓ Safe: {safeCount}</span>
            {skippedCount > 0 && <span className="stat skipped">→ Skipped: {skippedCount}</span>}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="review-progress-bar">
        <div 
          className="review-progress-fill" 
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Main Card */}
      <div className="review-card">
        {/* Similarity Score Badge */}
        <div 
          className="similarity-badge"
          style={{ backgroundColor: getSimilarityColor(currentMatch.similarity_score) }}
        >
          <div className="similarity-score">{currentMatch.similarity_score}%</div>
          <div className="similarity-label">Match</div>
        </div>

        {/* Split Screen Comparison */}
        <div className="comparison-container">
          {/* LEFT: KAMCO Client (Blue) */}
          <div className="comparison-panel kamco-panel">
            <div className="panel-header">
              <span className="panel-icon">👤</span>
              <h3>KAMCO Client</h3>
              <span className="panel-badge">Internal Database</span>
            </div>
            
            <div className="panel-content">
              <div className="info-grid">
                <div className="info-item">
                  <label>Client ID</label>
                  <span className="info-value">{currentMatch.customer_id}</span>
                </div>
                <div className="info-item">
                  <label>Full Name</label>
                  <span className="highlight-name">{currentMatch.customer_name}</span>
                </div>
                <div className="info-item">
                  <label>Type</label>
                  <span className="info-value">{currentMatch.customer_type}</span>
                </div>
                <div className="info-item">
                  <label>DOB / Reg No</label>
                  <span className="info-value">{currentMatch.dob_or_reg_no}</span>
                </div>
                <div className="info-item">
                  <label>Nationality</label>
                  <span className="info-value">{currentMatch.nationality_country}</span>
                </div>
                {currentMatch.kamco_client?.department && (
                  <div className="info-item">
                    <label>Department</label>
                    <span className="info-value">{currentMatch.kamco_client.department}</span>
                  </div>
                )}
                {currentMatch.kamco_client?.position && (
                  <div className="info-item">
                    <label>Position</label>
                    <span className="info-value">{currentMatch.kamco_client.position}</span>
                  </div>
                )}
                {currentMatch.kamco_client?.hire_date && (
                  <div className="info-item">
                    <label>Hire Date</label>
                    <span className="info-value">{currentMatch.kamco_client.hire_date}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="comparison-divider">
            <div className="divider-line"></div>
            <div className="divider-icon">↔</div>
            <div className="divider-line"></div>
          </div>

          {/* RIGHT: Screening Entry (Purple) */}
          <div className="comparison-panel screening-panel">
            <div className="panel-header">
              <span className="panel-icon">⚠️</span>
              <h3>Screening Match</h3>
              <span className="panel-badge">External Source</span>
            </div>
            
            <div className="panel-content">
              <div className="info-grid">
                <div className="info-item">
                  <label>Matched Name</label>
                  <span className="highlight-name">{currentMatch.matched_blacklist_name}</span>
                </div>
                {currentMatch.matched_alias && (
                  <div className="info-item">
                    <label>Aliases</label>
                    <span className="info-value">{currentMatch.matched_alias}</span>
                  </div>
                )}
                <div className="info-item">
                  <label>Source</label>
                  <span className="info-value">{currentMatch.source}</span>
                </div>
                <div className="info-item">
                  <label>Effective Date</label>
                  <span className="info-value">{currentMatch.effective_date}</span>
                </div>
                <div className="info-item">
                  <label>Match Type</label>
                  <span className="info-value">
                    <span className={`match-type-badge ${currentMatch.match_type}`}>
                      {currentMatch.match_type}
                    </span>
                  </span>
                </div>
                <div className="info-item full-width">
                  <label>Match Reason</label>
                  <span className="info-value">{currentMatch.match_reason}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Investigation Notes */}
        <div className="investigation-section">
          <label htmlFor="comments" className="investigation-label">
            Investigation Notes
            <span className="char-count">
              {comments.length} / 500 {comments.length < 10 && '(min 10 chars for flagging)'}
            </span>
          </label>
          <textarea
            id="comments"
            className="investigation-textarea"
            value={comments}
            onChange={(e) => setComments(e.target.value.slice(0, 500))}
            placeholder="Describe your investigation findings, reasons for flagging, or relevant observations..."
            rows={4}
          />
        </div>

        {/* Action Buttons */}
        <div className="review-actions">
          <button
            className="action-btn flag-btn"
            onClick={handleFlag}
            disabled={processing || comments.trim().length < 10}
          >
            {processing ? (
              <>
                <span className="btn-spinner"></span>
                Processing...
              </>
            ) : (
              <>
                <span>⚠️</span>
                FLAG
              </>
            )}
          </button>

          <button
            className="action-btn safe-btn"
            onClick={handleSafe}
            disabled={processing}
          >
            <span>✓</span>
            SAFE
          </button>

          <button
            className="action-btn report-btn"
            onClick={handleGeneratePDF}
            disabled={generatingPDF}
            title="Generate comprehensive PDF screening report"
          >
            <span>📄</span>
            {generatingPDF ? 'Generating...' : 'Generate Report'}
          </button>
        </div>

        {/* Navigation */}
        <div className="review-navigation">
          <button
            className="nav-btn"
            onClick={handlePrevious}
            disabled={currentIndex === 0 || processing}
          >
            ← Previous
          </button>

          <button
            className="nav-btn"
            onClick={handleSkip}
            disabled={processing}
          >
            Skip for Now →
          </button>
        </div>
      </div>

      {/* Keyboard Shortcuts Hint */}
      <div className="keyboard-hints">
        <span><kbd>F</kbd> Flag</span>
        <span><kbd>S</kbd> Safe</span>
        <span><kbd>←</kbd> Previous</span>
        <span><kbd>→</kbd> Skip</span>
      </div>
    </div>
  );
};

export default ReviewMode;
