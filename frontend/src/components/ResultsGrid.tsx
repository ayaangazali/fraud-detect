// src/components/ResultsGrid.tsx
import React, { useState, useMemo } from 'react';
import { MatchResult } from '../types';
import { api } from '../services/api';

interface Props {
  results: MatchResult[];
  processingTime?: number;
}

export const ResultsGrid: React.FC<Props> = ({ results, processingTime }) => {
  const [minScore, setMinScore] = useState<number>(0);
  const [sourceFilter, setSourceFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<keyof MatchResult>('similarity_score');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [exporting, setExporting] = useState(false);

  // Filter and sort results
  const filteredResults = useMemo(() => {
    let filtered = results.filter(r => {
      if (r.similarity_score < minScore) return false;
      if (sourceFilter !== 'all' && r.source !== sourceFilter) return false;
      if (typeFilter === 'police' && r.blacklist_type !== 'police') return false;
      if (typeFilter === 'user' && r.blacklist_type !== 'user') return false;
      if (typeFilter === 'individual' && r.customer_type !== 'individual') return false;
      if (typeFilter === 'corporate' && r.customer_type !== 'corporate') return false;
      return true;
    });

    // Sort
    filtered.sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      const aStr = String(aVal || '');
      const bStr = String(bVal || '');
      return sortDirection === 'asc' 
        ? aStr.localeCompare(bStr)
        : bStr.localeCompare(aStr);
    });

    return filtered;
  }, [results, minScore, sourceFilter, typeFilter, sortField, sortDirection]);

  const handleSort = (field: keyof MatchResult) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const blob = await api.exportToExcel(filteredResults);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `screening_results_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  if (results.length === 0) {
    return (
      <div className="results-section">
        <h2>📊 Screening Results</h2>
        <div className="empty-state">
          <p>No results yet. Run screening to see matches.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="results-section">
      <h2>📊 Screening Results</h2>

      <div className="results-stats">
        <div className="stat-item">
          <strong>Total Matches:</strong> {results.length}
        </div>
        <div className="stat-item">
          <strong>Filtered Matches:</strong> {filteredResults.length}
        </div>
        {processingTime && (
          <div className="stat-item">
            <strong>Processing Time:</strong> {processingTime}ms
          </div>
        )}
      </div>

      <div className="results-filters">
        <div className="filter-item">
          <label htmlFor="minScore">Min Similarity Score:</label>
          <input
            id="minScore"
            type="number"
            min="0"
            max="100"
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
          />
        </div>

        <div className="filter-item">
          <label htmlFor="sourceFilter">Source:</label>
          <select
            id="sourceFilter"
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
          >
            <option value="all">All Sources</option>
            <option value="government">Government</option>
            <option value="regulator">Regulator</option>
            <option value="other">Other</option>
            <option value="POLICE">Police</option>
          </select>
        </div>

        <div className="filter-item">
          <label htmlFor="typeFilter">Filter By:</label>
          <select
            id="typeFilter"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="all">All</option>
            <optgroup label="Blacklist Type">
              <option value="police">🚔 Police Blacklist</option>
              <option value="user">📋 User Blacklist</option>
            </optgroup>
            <optgroup label="Customer Type">
              <option value="individual">Individual</option>
              <option value="corporate">Corporate</option>
            </optgroup>
          </select>
        </div>

        <button 
          className="export-button" 
          onClick={handleExport}
          disabled={exporting || filteredResults.length === 0}
        >
          {exporting ? '📥 Exporting...' : '📥 Export to Excel'}
        </button>
      </div>

      <div className="table-wrapper">
        <table className="results-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('customer_id')}>
                Customer ID {sortField === 'customer_id' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('customer_name')}>
                Customer Name {sortField === 'customer_name' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('customer_type')}>
                Type {sortField === 'customer_type' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th>DOB/Reg No</th>
              <th>Nationality</th>
              <th onClick={() => handleSort('matched_blacklist_name')}>
                Blacklist Match {sortField === 'matched_blacklist_name' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th>Matched Via</th>
              <th onClick={() => handleSort('source')}>
                Source {sortField === 'source' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th>Blacklist Type</th>
              <th>Effective Date</th>
              <th onClick={() => handleSort('similarity_score')}>
                Score {sortField === 'similarity_score' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredResults.map((match, idx) => (
              <tr key={idx} className={match.similarity_score >= 90 ? 'high-risk' : ''}>
                <td>{match.customer_id}</td>
                <td>{match.customer_name}</td>
                <td>{match.customer_type}</td>
                <td>{match.dob_or_reg_no}</td>
                <td>{match.nationality_country}</td>
                <td>{match.matched_blacklist_name}</td>
                <td>
                  {match.matched_alias ? (
                    <span className="alias-badge">Alias: {match.matched_alias}</span>
                  ) : (
                    <span className="direct-badge">Direct</span>
                  )}
                </td>
                <td>{match.source}</td>
                <td>
                  {match.blacklist_type === 'police' ? (
                    <span className="police-badge" title="Match from hardcoded police blacklist">
                      🚔 Police
                    </span>
                  ) : (
                    <span className="user-badge" title="Match from user-uploaded blacklist">
                      📋 User
                    </span>
                  )}
                </td>
                <td>{match.effective_date}</td>
                <td>
                  <span className={`score-badge score-${Math.floor(match.similarity_score / 10) * 10}`}>
                    {match.similarity_score}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredResults.length === 0 && (
        <div className="empty-state">
          <p>No matches found with current filters.</p>
        </div>
      )}
    </div>
  );
};
