import React from 'react';
import { Layers, Clock, AlertTriangle, ShieldCheck, Flame, ListOrdered } from 'lucide-react';

export default function TechDebtBreakdown({ reportData }) {
  if (!reportData) return null;

  const { scores, recommendations, metrics, findings_summary } = reportData;
  const remHours = scores?.debt_remediation_hours || 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Debt Factor Metrics */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Technical Debt Analysis & Remediation Estimation</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Measurable signals derived from static analysis, cyclomatic complexity, Halstead metrics, and agent findings.
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Estimated Effort</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--primary)' }}>
              {remHours} <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>Hours</span>
            </div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px' }}>
          <div style={{ padding: '14px', backgroundColor: 'var(--bg-surface-raised)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Critical Defects</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--critical)' }}>
              {findings_summary?.by_severity?.critical || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>4.0h remediation / issue</div>
          </div>

          <div style={{ padding: '14px', backgroundColor: 'var(--bg-surface-raised)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>High Severity Risks</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--high)' }}>
              {findings_summary?.by_severity?.high || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>2.0h remediation / issue</div>
          </div>

          <div style={{ padding: '14px', backgroundColor: 'var(--bg-surface-raised)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Medium Smells</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--medium)' }}>
              {findings_summary?.by_severity?.medium || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>1.0h remediation / issue</div>
          </div>

          <div style={{ padding: '14px', backgroundColor: 'var(--bg-surface-raised)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Files Analyzed</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              {metrics?.length || 0}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>AST code metrics parsed</div>
          </div>
        </div>
      </div>

      {/* Prioritized Recommendations Roadmap */}
      <div className="card">
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '4px' }}>
          Prioritized Remediation Roadmap
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '18px' }}>
          Action items synthesized by the Review Coordinator to systematically reduce technical debt.
        </p>

        <div className="roadmap-list">
          {recommendations && recommendations.length > 0 ? (
            recommendations.map((rec) => (
              <div key={rec.id} className="roadmap-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <div>
                    <span className="roadmap-priority">Priority {rec.priority} • {rec.category}</span>
                    <h4 style={{ fontSize: '1.05rem', fontWeight: 700 }}>{rec.title}</h4>
                  </div>
                  <span className="badge badge-info" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <Clock size={12} /> {rec.estimated_effort_hours}h est.
                  </span>
                </div>

                {rec.rationale && (
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '10px' }}>
                    {rec.rationale}
                  </p>
                )}

                {rec.action_items && rec.action_items.length > 0 && (
                  <ul style={{ paddingLeft: '20px', fontSize: '0.85rem', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    {rec.action_items.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))
          ) : (
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>No recommendations needed.</p>
          )}
        </div>
      </div>

      {/* File Complexity Breakdown Table */}
      {metrics && metrics.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '4px' }}>
            Source File Metrics Breakdown
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
            Cyclomatic Complexity (McCabe), Maintainability Index (MI), and Halstead Volume per module.
          </p>

          <div className="table-container">
            <table className="findings-table">
              <thead>
                <tr>
                  <th>File</th>
                  <th>LOC</th>
                  <th>SLOC</th>
                  <th>Cyclomatic (CC)</th>
                  <th>Cognitive</th>
                  <th>Maintainability (MI)</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map((m, idx) => (
                  <tr key={idx}>
                    <td><span className="file-code-link">{m.file_path}</span></td>
                    <td>{m.loc}</td>
                    <td>{m.sloc}</td>
                    <td>
                      <span style={{ fontWeight: 600, color: m.cyclomatic_complexity > 10 ? 'var(--critical)' : 'var(--text-primary)' }}>
                        {m.cyclomatic_complexity}
                      </span>
                    </td>
                    <td>{m.cognitive_complexity}</td>
                    <td>
                      <span style={{ fontWeight: 700, color: m.maintainability_index >= 75 ? 'var(--success)' : m.maintainability_index >= 50 ? 'var(--medium)' : 'var(--critical)' }}>
                        {m.maintainability_index} / 100
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
