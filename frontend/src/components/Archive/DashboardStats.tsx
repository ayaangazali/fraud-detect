// src/components/DashboardStats.tsx
import { CustomerUploadResponse, BlacklistUploadResponse, MatchResult } from '../types';
import { TranslationKey } from '../i18n/translations';

interface DashboardStatsProps {
  customerData: CustomerUploadResponse | null;
  blacklistData: BlacklistUploadResponse | null;
  results: MatchResult[];
  t: (key: TranslationKey) => string;
}

export function DashboardStats({ customerData, blacklistData, results, t }: DashboardStatsProps) {
  const totalCustomers = customerData?.validRows || 0;
  const totalBlacklist = (blacklistData?.validRows || 0) + 30; // Include police blacklist
  const matchRate = totalCustomers > 0 ? ((results.length / totalCustomers) * 100).toFixed(1) : '0';
  const avgScore = results.length > 0 
    ? (results.reduce((sum, r) => sum + r.similarity_score, 0) / results.length).toFixed(1)
    : '0';

  const regulatorMatches = results.filter(r => r.blacklist_type === 'regulator').length;
  const userMatches = results.filter(r => r.blacklist_type === 'user').length;
  const highRisk = results.filter(r => r.similarity_score >= 90).length;
  const mediumRisk = results.filter(r => r.similarity_score >= 75 && r.similarity_score < 90).length;
  const lowRisk = results.filter(r => r.similarity_score < 75).length;

  return (
    <div className="dashboard-stats">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-value">{totalCustomers.toLocaleString()}</div>
            <div className="stat-label">{t('totalCustomers')}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <div className="stat-value">{totalBlacklist.toLocaleString()}</div>
            <div className="stat-label">{t('totalBlacklist')}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <div className="stat-value">{results.length.toLocaleString()}</div>
            <div className="stat-label">{t('totalMatches')}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">{matchRate}%</div>
            <div className="stat-label">{t('matchRate')}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⭐</div>
          <div className="stat-content">
            <div className="stat-value">{avgScore}%</div>
            <div className="stat-label">{t('avgScore')}</div>
          </div>
        </div>

        <div className="stat-card highlight-regulator">
          <div className="stat-icon">⚖️</div>
          <div className="stat-content">
            <div className="stat-value">{regulatorMatches.toLocaleString()}</div>
            <div className="stat-label">{t('regulatorMatches')}</div>
          </div>
        </div>

        <div className="stat-card highlight-user">
          <div className="stat-icon">📁</div>
          <div className="stat-content">
            <div className="stat-value">{userMatches.toLocaleString()}</div>
            <div className="stat-label">{t('userMatches')}</div>
          </div>
        </div>

        <div className="stat-card risk-breakdown">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <div className="risk-levels">
              <div className="risk-item high">
                <span className="risk-count">{highRisk}</span>
                <span className="risk-label">{t('highRisk')}</span>
              </div>
              <div className="risk-item medium">
                <span className="risk-count">{mediumRisk}</span>
                <span className="risk-label">{t('mediumRisk')}</span>
              </div>
              <div className="risk-item low">
                <span className="risk-count">{lowRisk}</span>
                <span className="risk-label">{t('lowRisk')}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
