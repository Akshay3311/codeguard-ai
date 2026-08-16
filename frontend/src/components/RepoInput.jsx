import React, { useState } from 'react';
import { GitBranch, Search, Play, FolderGit2, AlertCircle } from 'lucide-react';

const PRESETS = [
  {
    label: 'Sample Vulnerable Code (Fixture)',
    url: 'C:\\Users\\aksha\\.gemini\\antigravity\\scratch\\codeguard-ai\\backend\\tests\\fixtures',
    branch: 'main'
  },
  {
    label: 'Flask (Pallets)',
    url: 'https://github.com/pallets/flask',
    branch: 'main'
  },
  {
    label: 'Requests (PSF)',
    url: 'https://github.com/psf/requests',
    branch: 'main'
  },
  {
    label: 'FastAPI (Tiangolo)',
    url: 'https://github.com/tiangolo/fastapi',
    branch: 'master'
  }
];

export default function RepoInput({ onAnalyze, loading }) {
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!repoUrl.trim()) {
      setError('Please enter a valid repository URL or path.');
      return;
    }
    setError('');
    onAnalyze(repoUrl.trim(), branch.trim() || 'main');
  };

  const handleSelectPreset = (preset) => {
    setRepoUrl(preset.url);
    setBranch(preset.branch);
    setError('');
  };

  return (
    <div className="card repo-input-card">
      <form onSubmit={handleSubmit} className="repo-form">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '4px' }}>Analyze Python Repository</h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Scan code with deterministic AST checks, complexity metrics, RAG knowledge retrieval, and multi-agent AI.
            </p>
          </div>
        </div>

        <div className="input-row">
          <div className="input-field-wrapper">
            <FolderGit2 className="input-icon" size={18} />
            <input
              type="text"
              className="text-input"
              placeholder="https://github.com/username/repository or local path"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="input-field-wrapper" style={{ flex: 'none' }}>
            <GitBranch className="input-icon" size={16} />
            <input
              type="text"
              className="text-input branch-input"
              placeholder="branch"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              disabled={loading}
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? (
              <>
                <span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>⟳</span>
                Analyzing...
              </>
            ) : (
              <>
                <Play size={16} fill="currentColor" />
                Analyze Repository
              </>
            )}
          </button>
        </div>

        {error && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--critical)', fontSize: '0.85rem' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <div className="quick-select-presets">
          <span>Quick Select:</span>
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-chip"
              onClick={() => handleSelectPreset(p)}
              disabled={loading}
            >
              {p.label}
            </button>
          ))}
        </div>
      </form>
    </div>
  );
}
