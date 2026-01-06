// src/components/ReviewComplete.tsx
import React, { useState } from 'react';
import { api } from '../services/api';

interface ReviewCompleteProps {
  summary: {
    total: number;
    flagged: number;
    safe: number;
    skipped: number;
  };
  onUploadNew: () => void;
  onViewLogbook: () => void;
  onReturnToDashboard: () => void;
}

const ReviewComplete: React.FC<ReviewCompleteProps> = ({
  summary,
  onUploadNew,
  onViewLogbook,
  onReturnToDashboard,
}) => {
  const [exporting, setExporting] = useState(false);
  const [generatingPDF, setGeneratingPDF] = useState(false);

  const handleExportFlagged = async () => {
    if (summary.flagged === 0) {
      alert('No flagged cases to export');
      return;
    }

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
      
      // Show success notification
      alert('✅ Flagged cases exported successfully!');
    } catch (error) {
      console.error('Export failed:', error);
      alert('❌ Failed to export flagged cases. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const handleGeneratePDFReport = async () => {
    setGeneratingPDF(true);
    try {
      const reviewData = {
        summary: summary,
        matches: [], // We'll pass empty for completed review
        flaggedMatches: [], // The backend will read from logbook
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

      alert('✅ PDF report generated successfully!');
    } catch (error) {
      console.error('PDF generation failed:', error);
      alert('❌ Failed to generate PDF report. Please try again.');
    } finally {
      setGeneratingPDF(false);
    }
  };

  return (
    <div className="review-complete">
      <div className="review-complete-card">
        {/* Success Icon */}
        <div className="complete-icon-wrapper">
          <div className="complete-icon">✓</div>
        </div>

        {/* Title */}
        <h1 className="complete-title">Review Complete!</h1>
        <p className="complete-subtitle">
          You've finished reviewing all {summary.total} matches
        </p>

        {/* Summary Stats */}
        <div className="complete-stats">
          <div className="stat-card flagged">
            <div className="stat-icon">⚠️</div>
            <div className="stat-number">{summary.flagged}</div>
            <div className="stat-label">Cases Flagged</div>
          </div>

          <div className="stat-card safe">
            <div className="stat-icon">✓</div>
            <div className="stat-number">{summary.safe}</div>
            <div className="stat-label">Marked Safe</div>
          </div>

          {summary.skipped > 0 && (
            <div className="stat-card skipped">
              <div className="stat-icon">→</div>
              <div className="stat-number">{summary.skipped}</div>
              <div className="stat-label">Skipped</div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="complete-actions">
          {summary.flagged > 0 && (
            <>
              <button 
                className="complete-btn pdf-report" 
                onClick={handleGeneratePDFReport}
                disabled={generatingPDF}
              >
                <span>📄</span>
                {generatingPDF ? 'Generating...' : 'Download PDF Report'}
              </button>

              <button 
                className="complete-btn excel-export" 
                onClick={handleExportFlagged}
                disabled={exporting}
              >
                <span>📊</span>
                {exporting ? 'Exporting...' : 'Download Flagged Cases (Excel)'}
              </button>
            </>
          )}

          <button className="complete-btn primary" onClick={onUploadNew}>
            <span>📋</span>
            Upload New Screening List
          </button>

          <button className="complete-btn secondary" onClick={onViewLogbook}>
            <span>📚</span>
            View Flagged Log Book
          </button>

          <button className="complete-btn secondary" onClick={onReturnToDashboard}>
            <span>🏠</span>
            Return to Dashboard
          </button>
        </div>

        {/* Additional Info */}
        {summary.flagged > 0 && (
          <div className="complete-info">
            <p>
              {summary.flagged} {summary.flagged === 1 ? 'case has' : 'cases have'} been added to the 
              permanent log book and can be reviewed at any time.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewComplete;
