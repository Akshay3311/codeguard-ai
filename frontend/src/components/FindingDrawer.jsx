import React from 'react';
import { X, BookOpen, AlertTriangle, Lightbulb, Code2, ShieldAlert } from 'lucide-react';

export default function FindingDrawer({ finding, onClose }) {
  if (!finding) return null;

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
              <span className={`badge badge-${finding.severity}`}>{finding.severity}</span>
              <span className={`badge badge-${finding.category}`}>{finding.category}</span>
              <span className="badge badge-info">Confidence: {Math.round(finding.confidence * 100)}%</span>
            </div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 800 }}>{finding.title}</h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '6px'
            }}
          >
            <X size={20} />
          </button>
        </div>

        <div className="drawer-body">
          <div className="detail-section">
            <span className="detail-label">File Location</span>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.88rem', color: 'var(--primary)' }}>
              {finding.file} {finding.line ? `(Line ${finding.line}${finding.end_line ? `-${finding.end_line}` : ''})` : ''}
            </div>
          </div>

          <div className="detail-section">
            <span className="detail-label">Description & Exploit Impact</span>
            <p style={{ fontSize: '0.92rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
              {finding.description}
            </p>
          </div>

          {finding.evidence && (
            <div className="detail-section">
              <span className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Code2 size={14} /> Syntactic Evidence / Code Snippet
              </span>
              <pre className="code-snippet-box">
                <code>{finding.evidence}</code>
              </pre>
            </div>
          )}

          <div className="detail-section">
            <span className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Lightbulb size={14} /> Actionable Remediation Recommendation
            </span>
            <div className="recommendation-box">
              {finding.recommendation}
            </div>
          </div>

          {finding.rag_source && (
            <div className="detail-section">
              <span className="detail-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <BookOpen size={14} /> RAG Knowledge Base Reference Citation
              </span>
              <div className="rag-citation-box">
                Referenced standard: <strong>{finding.rag_source}</strong>
              </div>
            </div>
          )}

          <div className="detail-section">
            <span className="detail-label">Technical Debt Contribution</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ flex: 1, height: '8px', backgroundColor: 'var(--bg-surface-raised)', borderRadius: '999px', overflow: 'hidden' }}>
                <div
                  style={{
                    width: `${finding.technical_debt_impact * 10}%`,
                    height: '100%',
                    backgroundColor: finding.technical_debt_impact > 6 ? 'var(--critical)' : 'var(--primary)'
                  }}
                />
              </div>
              <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>{finding.technical_debt_impact} / 10</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
