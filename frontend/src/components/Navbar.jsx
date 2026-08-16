import React from 'react';
import { ShieldAlert, Cpu, Activity } from 'lucide-react';

export default function Navbar({ healthData, activeTab, setActiveTab }) {
  return (
    <header className="navbar">
      <div className="navbar-inner">
        <div className="brand-logo">
          <div className="brand-icon">
            <ShieldAlert size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <span className="brand-name">CodeGuard AI</span>
              <span className="brand-badge">Multi-Agent</span>
            </div>
          </div>
        </div>

        <div className="nav-actions">
          <div className="system-status-pill">
            <span className="status-dot" style={{ backgroundColor: healthData?.status === 'healthy' ? 'var(--success)' : 'var(--medium)' }} />
            <span>LLM: {healthData?.llm_provider || 'Heuristic AI'}</span>
            <span style={{ color: 'var(--border-subtle)' }}>|</span>
            <span>RAG: {healthData?.rag_knowledge_base?.chunks_loaded || 0} docs</span>
          </div>
        </div>
      </div>
    </header>
  );
}
