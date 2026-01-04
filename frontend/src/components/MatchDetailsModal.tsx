// src/components/MatchDetailsModal.tsx
import { MatchResult } from '../types';
import { TranslationKey } from '../i18n/translations';

interface MatchDetailsModalProps {
  match: MatchResult | null;
  onClose: () => void;
  t: (key: TranslationKey) => string;
  isArabic: boolean;
}

export function MatchDetailsModal({ match, onClose, t }: MatchDetailsModalProps) {
  if (!match) return null;

  const getRiskLevel = (score: number) => {
    if (score >= 95) return { label: t('critical'), color: '#d32f2f' };
    if (score >= 85) return { label: t('high'), color: '#ff7043' };
    if (score >= 75) return { label: t('medium'), color: '#ffa726' };
    if (score >= 65) return { label: t('low'), color: '#ffb74d' };
    return { label: t('minimal'), color: '#66bb6a' };
  };

  const risk = getRiskLevel(match.similarity_score);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{t('matchDetails')}</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* Customer Info */}
          <div className="detail-section">
            <h3>🎯 {t('customerName')}</h3>
            <div className="detail-value customer-name">{match.customer_name}</div>
            <div className="detail-meta">
              <span className="badge badge-type">{match.customer_type}</span>
              <span className="detail-id">{match.customer_id}</span>
            </div>
          </div>

          {/* Blacklist Match */}
          <div className="detail-section">
            <h3>⚠️ {t('blacklistMatch')}</h3>
            <div className="detail-value blacklist-name">{match.matched_blacklist_name}</div>
            <div className="detail-meta">
              {match.blacklist_type === 'police' ? (
                <span className="badge badge-police">🚔 {t('policeLabel')}</span>
              ) : (
                <span className="badge badge-user">📋 {t('userLabel')}</span>
              )}
              <span className="badge badge-source">{match.source}</span>
            </div>
          </div>

          {/* Match Reason */}
          <div className="detail-section highlight">
            <h3>💡 {t('matchExplanation')}</h3>
            <div className="match-reason-box">
              <div className="match-reason-icon">
                {match.match_type === 'direct' ? '🎯' : match.match_type === 'alias' ? '🔄' : '🔍'}
              </div>
              <div className="match-reason-text">
                <div className="match-reason-title">
                  {match.match_type === 'direct' && t('directMatch')}
                  {match.match_type === 'alias' && t('aliasMatch')}
                  {match.match_type === 'fuzzy' && t('fuzzyMatch')}
                </div>
                <div className="match-reason-desc">{match.match_reason}</div>
              </div>
            </div>
          </div>

          {/* Score Breakdown */}
          <div className="detail-section">
            <h3>📊 {t('scoreBreakdown')}</h3>
            <div className="score-container">
              <div className="score-main" style={{ borderColor: risk.color }}>
                <div className="score-value" style={{ color: risk.color }}>
                  {match.similarity_score}%
                </div>
                <div className="score-label">{risk.label}</div>
              </div>

              <div className="score-details">
                <div className="score-detail-item">
                  <div className="score-detail-label">{t('matchedVia')}</div>
                  <div className="score-detail-value">{match.matched_field}</div>
                </div>

                {match.score_breakdown.name_similarity > 0 && (
                  <div className="score-detail-item">
                    <div className="score-detail-label">Name Similarity</div>
                    <div className="score-progress">
                      <div 
                        className="score-progress-bar" 
                        style={{ width: `${match.score_breakdown.name_similarity}%` }}
                      ></div>
                      <span className="score-progress-value">
                        {match.score_breakdown.name_similarity}%
                      </span>
                    </div>
                  </div>
                )}

                {match.score_breakdown.alias_similarity > 0 && (
                  <div className="score-detail-item">
                    <div className="score-detail-label">Alias Similarity</div>
                    <div className="score-progress">
                      <div 
                        className="score-progress-bar alias" 
                        style={{ width: `${match.score_breakdown.alias_similarity}%` }}
                      ></div>
                      <span className="score-progress-value">
                        {match.score_breakdown.alias_similarity}%
                      </span>
                    </div>
                  </div>
                )}

                <div className="score-detail-item">
                  <div className="score-detail-label">Best Match</div>
                  <div className="score-detail-value best-match">
                    {match.score_breakdown.best_match}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="detail-section">
            <h3>📄 {t('details')}</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <div className="detail-label">{t('nationality')}</div>
                <div className="detail-value">{match.nationality_country}</div>
              </div>
              <div className="detail-item">
                <div className="detail-label">{t('dobRegNo')}</div>
                <div className="detail-value">{match.dob_or_reg_no || 'N/A'}</div>
              </div>
              <div className="detail-item">
                <div className="detail-label">{t('effectiveDateCol')}</div>
                <div className="detail-value">{match.effective_date}</div>
              </div>
              {match.matched_alias && (
                <div className="detail-item">
                  <div className="detail-label">{t('matchedVia')}</div>
                  <div className="detail-value alias-value">
                    <span className="badge badge-alias">🔄 {t('alias')}</span>
                    {match.matched_alias}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-close-modal" onClick={onClose}>
            {t('closeDetails')}
          </button>
        </div>
      </div>
    </div>
  );
}
