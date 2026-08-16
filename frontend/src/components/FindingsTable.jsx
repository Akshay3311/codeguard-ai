import React, { useState } from 'react';
import { Search, Filter, ShieldAlert, Bug, Sparkles, FileText, ChevronRight } from 'lucide-react';

export default function FindingsTable({ findings, onSelectFinding }) {
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const filtered = (findings || []).filter((f) => {
    if (categoryFilter !== 'all' && f.category !== categoryFilter) return false;
    if (severityFilter !== 'all' && f.severity !== severityFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchFile = f.file?.toLowerCase().includes(q);
      const matchTitle = f.title?.toLowerCase().includes(q);
      const matchDesc = f.description?.toLowerCase().includes(q);
      if (!matchFile && !matchTitle && !matchDesc) return false;
    }
    return true;
  });

  const getCategoryIcon = (cat) => {
    switch (cat) {
      case 'security': return <ShieldAlert size={14} />;
      case 'bug': return <Bug size={14} />;
      default: return <Sparkles size={14} />;
    }
  };

  return (
    <div className="card">
      <div className="findings-section-header">
        <div>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '2px' }}>
            Analysis Findings ({filtered.length})
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Detected code smells, vulnerabilities, and potential runtime bugs. Click any row to inspect code snippet and recommendations.
          </p>
        </div>
      </div>

      <div className="filter-bar">
        <select
          className="filter-select"
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
        >
          <option value="all">All Categories</option>
          <option value="security">Security</option>
          <option value="quality">Code Quality</option>
          <option value="bug">Bug Risks</option>
          <option value="debt">Technical Debt</option>
        </select>

        <select
          className="filter-select"
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
        >
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>

        <input
          type="text"
          className="filter-search"
          placeholder="Filter by file, title, or keyword..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          <FileText size={36} style={{ marginBottom: '12px', opacity: 0.5 }} />
          <p style={{ fontWeight: 600 }}>No matching findings</p>
          <p style={{ fontSize: '0.85rem' }}>No issues found matching the selected filters.</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="findings-table">
            <thead>
              <tr>
                <th>Severity</th>
                <th>Category</th>
                <th>Issue Title</th>
                <th>File Location</th>
                <th>Source</th>
                <th>Debt Impact</th>
                <th style={{ width: '40px' }}></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((f) => (
                <tr key={f.id} onClick={() => onSelectFinding(f)}>
                  <td>
                    <span className={`badge badge-${f.severity}`}>
                      {f.severity}
                    </span>
                  </td>
                  <td>
                    <span className={`badge badge-${f.category}`} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      {getCategoryIcon(f.category)}
                      {f.category}
                    </span>
                  </td>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                      {f.title}
                    </div>
                  </td>
                  <td>
                    <span className="file-code-link">
                      {f.file}{f.line ? `:${f.line}` : ''}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      {f.source}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 700, color: f.technical_debt_impact > 6 ? 'var(--critical)' : 'var(--text-secondary)' }}>
                      {f.technical_debt_impact}/10
                    </span>
                  </td>
                  <td>
                    <ChevronRight size={16} color="var(--text-muted)" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
