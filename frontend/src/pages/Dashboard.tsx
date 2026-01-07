// src/pages/Dashboard.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';
import FileUpload from '../components/Dashboard/FileUpload.tsx';
import InReviewQueue from '../components/Dashboard/InReviewQueue.tsx';
import FlaggedItems from '../components/Dashboard/FlaggedItems.tsx';
import StatsCards from '../components/Dashboard/StatsCards.tsx';
import CheckerReview from '../components/Dashboard/CheckerReview.tsx';

type TabType = 'all' | 'clients' | 'vendors' | 'staff' | 'others';
type ViewMode = 'overview' | 'checker-review';

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('all');
  const [userRole, setUserRole] = useState<string>('');
  const [username, setUsername] = useState<string>('');
  const [viewMode, setViewMode] = useState<ViewMode>('overview');
  const navigate = useNavigate();

  useEffect(() => {
    // Get user info from localStorage
    const authData = localStorage.getItem('auth');
    if (authData) {
      const { username: user, role } = JSON.parse(authData);
      setUsername(user);
      setUserRole(role);
    } else {
      // Redirect to login if not authenticated
      navigate('/');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('auth');
    navigate('/');
  };

  const canUploadAndScan = userRole === 'screener' || userRole === 'checker';

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <div className="logo-small">
            <svg width="40" height="40" viewBox="0 0 50 50" fill="none">
              <rect width="50" height="50" rx="10" fill="#0B5394"/>
              <path d="M15 25L22 32L35 18" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div>
            <h1 className="app-title">KAMCO Screening System</h1>
            <p className="app-subtitle">Compliance Dashboard</p>
          </div>
        </div>

        <div className="header-right">
          <div className="user-info">
            <div className="user-avatar">
              {username.charAt(0).toUpperCase()}
            </div>
            <div className="user-details">
              <p className="user-name">{username}</p>
              <p className="user-role">{userRole.charAt(0).toUpperCase() + userRole.slice(1)}</p>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            Logout
          </button>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="dashboard-nav">
        {userRole === 'checker' && (
          <div className="view-mode-toggle">
            <button
              className={viewMode === 'overview' ? 'mode-btn active' : 'mode-btn'}
              onClick={() => setViewMode('overview')}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="7" height="7"/>
                <rect x="14" y="3" width="7" height="7"/>
                <rect x="14" y="14" width="7" height="7"/>
                <rect x="3" y="14" width="7" height="7"/>
              </svg>
              Overview
            </button>
            <button
              className={viewMode === 'checker-review' ? 'mode-btn active' : 'mode-btn'}
              onClick={() => setViewMode('checker-review')}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 11l3 3L22 4"/>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
              </svg>
              Checker Review
            </button>
          </div>
        )}
        <button
          className={activeTab === 'all' ? 'active' : ''}
          onClick={() => setActiveTab('all')}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="7" height="7"/>
            <rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/>
            <rect x="3" y="14" width="7" height="7"/>
          </svg>
          All
        </button>
        <button
          className={activeTab === 'clients' ? 'active' : ''}
          onClick={() => setActiveTab('clients')}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          Clients
        </button>
        <button
          className={activeTab === 'vendors' ? 'active' : ''}
          onClick={() => setActiveTab('vendors')}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
          </svg>
          Vendors
        </button>
        <button
          className={activeTab === 'staff' ? 'active' : ''}
          onClick={() => setActiveTab('staff')}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          Staff
        </button>
        <button
          className={activeTab === 'others' ? 'active' : ''}
          onClick={() => setActiveTab('others')}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="1"/>
            <circle cx="19" cy="12" r="1"/>
            <circle cx="5" cy="12" r="1"/>
          </svg>
          Others
        </button>
      </nav>

      {/* Main Content */}
      <main className="dashboard-content">
        {viewMode === 'overview' ? (
          <>
            {/* Stats Cards */}
            <StatsCards activeTab={activeTab} />

            {/* File Upload Section (Screener/Checker only) */}
            {canUploadAndScan && (
              <FileUpload />
            )}

            {/* In Review Queue */}
            <InReviewQueue activeTab={activeTab} userRole={userRole} />

            {/* Flagged Items */}
            <FlaggedItems activeTab={activeTab} userRole={userRole} />
          </>
        ) : (
          <>
            {/* Checker Review Console */}
            <CheckerReview activeTab={activeTab} userRole={userRole} />
          </>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
