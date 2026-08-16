import React from 'react';
import { HeartPulse, Wrench, Shield, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';

export default function MetricsOverview({ scores, totalFiles, totalLines, stats }) {
  const health = scores?.overall_health_score ?? (stats ? Math.max(0, 100 - (stats.average_technical_debt || 0)) : 100);
  const debt = scores?.technical_debt_score ?? (stats?.average_technical_debt || 0);
  const secScore = scores?.security_score ?? 100;
  const qualScore = scores?.quality_score ?? 100;
  const remHours = scores?.debt_remediation_hours ?? 0;

  // Determine health color
  const getHealthColor = (val) => {
    if (val >= 80) return 'var(--success)';
    if (val >= 60) return 'var(--medium)';
    return 'var(--critical)';
  };

  return (
    <div className="scorecards-grid">
      <div className="scorecard">
        <div className="scorecard-header">
          <span className="scorecard-title">Code Health Score</span>
          <HeartPulse className="scorecard-icon" size={20} color={getHealthColor(health)} />
        </div>
        <div className="scorecard-value" style={{ color: getHealthColor(health) }}>
          {health}<span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/100</span>
        </div>
        <div className="scorecard-subtitle">
          {health >= 80 ? 'Grade A - Robust Architecture' : health >= 60 ? 'Grade B - Moderate Risk' : 'Grade C - Needs Refactoring'}
        </div>
      </div>

      <div className="scorecard">
        <div className="scorecard-header">
          <span className="scorecard-title">Technical Debt Score</span>
          <Wrench className="scorecard-icon" size={20} color={debt > 30 ? 'var(--critical)' : 'var(--text-muted)'} />
        </div>
        <div className="scorecard-value" style={{ color: debt > 40 ? 'var(--critical)' : debt > 20 ? 'var(--high)' : 'var(--text-primary)' }}>
          {debt}<span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>/100</span>
        </div>
        <div className="scorecard-subtitle">
          {remHours > 0 ? `Est. ${remHours}h remediation effort` : 'Zero estimated debt'}
        </div>
      </div>

      <div className="scorecard">
        <div className="scorecard-header">
          <span className="scorecard-title">Security Posture</span>
          <Shield className="scorecard-icon" size={20} color={secScore >= 90 ? 'var(--success)' : 'var(--critical)'} />
        </div>
        <div className="scorecard-value" style={{ color: secScore >= 90 ? 'var(--success)' : 'var(--critical)' }}>
          {secScore}<span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>%</span>
        </div>
        <div className="scorecard-subtitle">OWASP & Bandit checks</div>
      </div>

      <div className="scorecard">
        <div className="scorecard-header">
          <span className="scorecard-title">Maintainability</span>
          <CheckCircle2 className="scorecard-icon" size={20} color="var(--primary)" />
        </div>
        <div className="scorecard-value" style={{ color: 'var(--primary)' }}>
          {qualScore}<span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>%</span>
        </div>
        <div className="scorecard-subtitle">
          {totalFiles ? `${totalFiles} files (${totalLines} LOC)` : 'AST complexity index'}
        </div>
      </div>
    </div>
  );
}
