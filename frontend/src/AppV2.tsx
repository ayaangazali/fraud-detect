// src/AppV2.tsx - New workflow for screening list review
import { useState } from 'react';
import ScreeningListUpload from './components/ScreeningListUpload';
import { ResultsGrid } from './components/ResultsGrid';
import { DashboardStats } from './components/DashboardStats';
import { LanguageSwitcher } from './components/LanguageSwitcher';
import ReviewMode from './components/ReviewMode';
import ReviewComplete from './components/ReviewComplete';
import ViewDetailsModal from './components/ViewDetailsModal';
import FlaggedLogbookModal from './components/FlaggedLogbookModal';
import { useLanguage } from './hooks/useLanguage';
import { api } from './services/api';
import './App.css';

type ViewMode = 'upload' | 'results' | 'review' | 'complete';

interface ReviewSummary {
  total: number;
  flagged: number;
  safe: number;
  skipped: number;
}

function AppV2() {
  const [screeningListData, setScreeningListData] = useState<any | null>(null);
  const [screeningResults, setScreeningResults] = useState<any | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('upload');
  const [reviewSummary, setReviewSummary] = useState<ReviewSummary | null>(null);
  const [threshold, setThreshold] = useState(70);
  const [includeAliases, setIncludeAliases] = useState(true);
  const [screening, setScreening] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState<any | null>(null);
  const [showLogbookModal, setShowLogbookModal] = useState(false);
  
  const { t, toggleLanguage, isArabic } = useLanguage();

  const handleViewDetails = (match: any) => {
    setSelectedMatch(match);
  };

  const handleCloseModal = () => {
    setSelectedMatch(null);
  };

  const handleScreeningListUpload = (data: any) => {
    setScreeningListData(data);
    setScreeningResults(null);
    setViewMode('upload');
  };

  const handleScreening = async () => {
    if (!screeningListData) return;

    setScreening(true);
    try {
      const response = await api.screenList(
        screeningListData.rows,
        threshold,
        includeAliases
      );
      
      // Sort by similarity score (highest first)
      const sortedMatches = response.matches.sort(
        (a: any, b: any) => b.similarity_score - a.similarity_score
      );
      
      setScreeningResults({ ...response, matches: sortedMatches });
      setViewMode('results');
    } catch (error) {
      console.error('Screening error:', error);
      alert('Failed to screen list. Please try again.');
    } finally {
      setScreening(false);
    }
  };

  const handleEnterReviewMode = () => {
    setViewMode('review');
  };

  const handleExitReviewMode = () => {
    setViewMode('results');
  };

  const handleReviewComplete = (summary: ReviewSummary) => {
    setReviewSummary(summary);
    setViewMode('complete');
  };

  const handleUploadNew = () => {
    setScreeningListData(null);
    setScreeningResults(null);
    setReviewSummary(null);
    setViewMode('upload');
  };

  const handleViewLogbook = () => {
    setShowLogbookModal(true);
  };

  const handleReturnToDashboard = () => {
    setViewMode(screeningResults ? 'results' : 'upload');
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>🔍 KAMCO AML/KYC Screening System</h1>
            <p>Screen external lists against internal client database</p>
          </div>
          <LanguageSwitcher isArabic={isArabic} onToggle={toggleLanguage} t={t} />
        </div>
      </header>

      <main className="app-main">
        {viewMode === 'review' ? (
          <ReviewMode
            matches={screeningResults?.matches || []}
            onExit={handleExitReviewMode}
            onComplete={handleReviewComplete}
          />
        ) : viewMode === 'complete' && reviewSummary ? (
          <ReviewComplete
            summary={reviewSummary}
            onUploadNew={handleUploadNew}
            onViewLogbook={handleViewLogbook}
            onReturnToDashboard={handleReturnToDashboard}
          />
        ) : (
          <>
            {/* Dashboard Stats */}
            {screeningResults && (
              <DashboardStats 
                customerData={null}
                blacklistData={null}
                results={screeningResults.matches || []}
                t={t}
              />
            )}

            {/* Upload Section */}
            {!screeningResults && (
              <div className="upload-sections">
                <ScreeningListUpload onUploadComplete={handleScreeningListUpload} />
              </div>
            )}

            {/* Screening Controls */}
            {screeningListData && !screeningResults && (
              <div className="screening-controls-container">
                <div className="screening-info-card">
                  <div className="screening-header-with-back">
                    <h3>Ready to Screen</h3>
                    <button 
                      className="back-button"
                      onClick={() => setViewMode('upload')}
                      title="Back to upload"
                    >
                      ← Back
                    </button>
                  </div>
                  <p>{screeningListData.validRows} entries loaded</p>
                  <p className="info-text">
                    Will be compared against KAMCO's internal client database
                  </p>
                  
                  <div className="threshold-control">
                    <label>
                      Match Threshold: {threshold}%
                      <input
                        type="range"
                        min="50"
                        max="100"
                        value={threshold}
                        onChange={(e) => setThreshold(Number(e.target.value))}
                        style={{
                          background: `linear-gradient(to right, #1864ab 0%, #1864ab ${((threshold - 50) / 50) * 100}%, #d0d5dd ${((threshold - 50) / 50) * 100}%, #d0d5dd 100%)`
                        }}
                      />
                    </label>
                    
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={includeAliases}
                        onChange={(e) => setIncludeAliases(e.target.checked)}
                      />
                      Include alias matching
                    </label>
                  </div>

                  <button
                    className="screen-button"
                    onClick={handleScreening}
                    disabled={screening}
                  >
                    {screening ? 'Screening...' : '🔍 Start Screening'}
                  </button>
                </div>
              </div>
            )}

            {/* Results */}
            {screeningResults && viewMode === 'results' && (
              <>
                <div className="results-header">
                  <h2>Screening Results</h2>
                  <div className="results-actions">
                    <button
                      className="back-to-screening-btn"
                      onClick={() => {
                        setScreeningResults(null);
                        setViewMode('upload');
                      }}
                    >
                      ← Back to Screening
                    </button>
                    <button
                      className="enter-review-btn"
                      onClick={handleEnterReviewMode}
                    >
                      🎯 Enter Review Mode
                    </button>
                    <button
                      className="upload-new-btn"
                      onClick={handleUploadNew}
                    >
                      📋 Upload New List
                    </button>
                  </div>
                </div>

                <ResultsGrid
                  results={screeningResults.matches}
                  processingTime={screeningResults.processingTime || 0}
                  onViewDetails={handleViewDetails}
                  t={t}
                  isArabic={isArabic}
                />
              </>
            )}
          </>
        )}
      </main>

      {/* View Details Modal */}
      {selectedMatch && (
        <ViewDetailsModal match={selectedMatch} onClose={handleCloseModal} />
      )}

      {/* Flagged Logbook Modal */}
      {showLogbookModal && (
        <FlaggedLogbookModal onClose={() => setShowLogbookModal(false)} />
      )}

      <footer className="app-footer">
        <p>© 2026 KAMCO Investment Company. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default AppV2;
