// src/components/Dashboard/StatsCards.tsx
import React from 'react';
import './StatsCards.css';

interface StatsCardsProps {
  activeTab: string;
}

const StatsCards: React.FC<StatsCardsProps> = ({ activeTab }) => {
  // TODO: Replace with actual data from API
  const stats = {
    all: { inReview: 22, flagged: 8, cleared: 150, total: 180 },
    clients: { inReview: 12, flagged: 5, cleared: 89, total: 106 },
    vendors: { inReview: 7, flagged: 2, cleared: 45, total: 54 },
    staff: { inReview: 3, flagged: 1, cleared: 16, total: 20 },
    others: { inReview: 0, flagged: 0, cleared: 0, total: 0 },
  };

  const currentStats = stats[activeTab as keyof typeof stats] || stats.all;

  return (
    <div className="stats-cards">
      <div className="stat-card stat-total">
        <div className="stat-icon total-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <line x1="9" y1="3" x2="9" y2="21"/>
          </svg>
        </div>
        <div className="stat-content">
          <p className="stat-label">Total Scanned</p>
          <p className="stat-value">{currentStats.total}</p>
        </div>
      </div>

      <div className="stat-card stat-review">
        <div className="stat-icon review-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div className="stat-content">
          <p className="stat-label">In Review</p>
          <p className="stat-value">{currentStats.inReview}</p>
        </div>
      </div>

      <div className="stat-card stat-flagged">
        <div className="stat-icon flagged-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
            <line x1="4" y1="22" x2="4" y2="15"/>
          </svg>
        </div>
        <div className="stat-content">
          <p className="stat-label">Flagged</p>
          <p className="stat-value">{currentStats.flagged}</p>
        </div>
      </div>

      <div className="stat-card stat-cleared">
        <div className="stat-icon cleared-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <div className="stat-content">
          <p className="stat-label">Cleared</p>
          <p className="stat-value">{currentStats.cleared}</p>
        </div>
      </div>
    </div>
  );
};

export default StatsCards;
