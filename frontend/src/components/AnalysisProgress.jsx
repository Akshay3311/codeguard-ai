import React from 'react';
import { GitPullRequest, Search, FileCode2, ShieldAlert, Cpu, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

const STAGES = [
  { id: 'cloning', label: 'Cloning Repo', icon: GitPullRequest, minProgress: 15 },
  { id: 'parsing', label: 'File Discovery', icon: Search, minProgress: 30 },
  { id: 'analyzing', label: 'AST & Metrics', icon: FileCode2, minProgress: 50 },
  { id: 'agent_evaluation', label: 'Multi-Agent AI', icon: Cpu, minProgress: 75 },
  { id: 'synthesizing', label: 'Review Coordinator', icon: Sparkles, minProgress: 90 },
  { id: 'completed', label: 'Report Ready', icon: CheckCircle2, minProgress: 100 }
];

export default function AnalysisProgress({ statusData }) {
  if (!statusData || statusData.status === 'idle') return null;

  const progress = statusData.progress_percentage || 0;
  const isFailed = statusData.status === 'failed';

  return (
    <div className="progress-container">
      <div className="progress-header">
        <div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Analysis Pipeline
          </span>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>{statusData.current_step || 'Processing repository...'}</h3>
        </div>
        <div style={{ fontSize: '1.1rem', fontWeight: 800, color: isFailed ? 'var(--critical)' : 'var(--primary)' }}>
          {progress}%
        </div>
      </div>

      <div className="progress-bar-bg">
        <div
          className="progress-bar-fill"
          style={{
            width: `${progress}%`,
            background: isFailed ? 'var(--critical)' : 'linear-gradient(90deg, #3b82f6, #60a5fa)'
          }}
        />
      </div>

      {isFailed && statusData.error_message && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--critical)', fontSize: '0.88rem', marginTop: '12px' }}>
          <AlertCircle size={18} />
          <span>Error: {statusData.error_message}</span>
        </div>
      )}

      <div className="stepper-steps">
        {STAGES.map((s, idx) => {
          const Icon = s.icon;
          const isCompleted = progress >= s.minProgress;
          const isActive = progress < s.minProgress && (idx === 0 || progress >= STAGES[idx - 1].minProgress);

          return (
            <div
              key={s.id}
              className={`step-item ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}`}
            >
              <div className="step-circle">
                <Icon size={14} />
              </div>
              <span>{s.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
