import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import RepoInput from './components/RepoInput';
import MetricsOverview from './components/MetricsOverview';
import AnalysisProgress from './components/AnalysisProgress';
import FindingsTable from './components/FindingsTable';
import FindingDrawer from './components/FindingDrawer';
import TechDebtBreakdown from './components/TechDebtBreakdown';
import ReportExport from './components/ReportExport';
import {
  fetchHealth,
  fetchOverviewStats,
  startAnalysis,
  fetchAnalysisStatus,
  fetchFullReport,
  fetchRepositories
} from './services/api';
import { History, LayoutDashboard, Layers, AlertCircle, CheckCircle } from 'lucide-react';

export default function App() {
  const [healthData, setHealthData] = useState(null);
  const [statsData, setStatsData] = useState(null);
  const [reposHistory, setReposHistory] = useState([]);
  
  const [loading, setLoading] = useState(false);
  const [activeAnalysisId, setActiveAnalysisId] = useState(null);
  const [statusData, setStatusData] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [selectedFinding, setSelectedFinding] = useState(null);
  
  const [activeTab, setActiveTab] = useState('findings'); // 'findings' | 'debt' | 'history'
  const pollIntervalRef = useRef(null);

  // Load initial health, stats, and historical repositories
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [health, stats, repos] = await Promise.all([
        fetchHealth().catch(() => null),
        fetchOverviewStats().catch(() => null),
        fetchRepositories().catch(() => [])
      ]);
      setHealthData(health);
      setStatsData(stats);
      setReposHistory(repos || []);
    } catch (err) {
      console.error('Error loading initial data:', err);
    }
  };

  // Poll analysis status
  useEffect(() => {
    if (!activeAnalysisId) return;

    const checkStatus = async () => {
      try {
        const status = await fetchAnalysisStatus(activeAnalysisId);
        setStatusData(status);

        if (status.status === 'completed') {
          clearInterval(pollIntervalRef.current);
          setLoading(false);
          // Fetch full comprehensive report
          const fullReport = await fetchFullReport(activeAnalysisId);
          setReportData(fullReport);
          loadInitialData(); // Refresh global stats
        } else if (status.status === 'failed') {
          clearInterval(pollIntervalRef.current);
          setLoading(false);
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };

    // Run immediate check then poll every 1.5s
    checkStatus();
    pollIntervalRef.current = setInterval(checkStatus, 1500);

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [activeAnalysisId]);

  const handleStartAnalysis = async (url, branch) => {
    try {
      setLoading(true);
      setReportData(null);
      setSelectedFinding(null);
      setStatusData({
        status: 'queued',
        progress_percentage: 5,
        current_step: 'Submitting repository to queue...'
      });

      const res = await startAnalysis(url, branch);
      setActiveAnalysisId(res.analysis_id);
    } catch (err) {
      setLoading(false);
      setStatusData({
        status: 'failed',
        progress_percentage: 100,
        current_step: 'Analysis request failed',
        error_message: err.message
      });
    }
  };

  const handleSelectHistoricalRepo = async (analysisId) => {
    if (!analysisId) return;
    try {
      setLoading(true);
      setActiveAnalysisId(analysisId);
      const fullReport = await fetchFullReport(analysisId);
      setReportData(fullReport);
      setStatusData({
        status: 'completed',
        progress_percentage: 100,
        current_step: 'Analysis loaded from history'
      });
      setActiveTab('findings');
    } catch (err) {
      console.error('Failed to load historical report:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Navbar
        healthData={healthData}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <main className="main-content">
        {/* Top Metric Scorecards */}
        <MetricsOverview
          scores={reportData?.scores}
          totalFiles={reportData?.total_files_analyzed}
          totalLines={reportData?.total_lines_of_code}
          stats={statsData}
        />

        {/* Repository Input Section */}
        <RepoInput onAnalyze={handleStartAnalysis} loading={loading} />

        {/* Live Stepper & Progress */}
        <AnalysisProgress statusData={statusData} />

        {/* Main Content Area */}
        {reportData && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
              <div className="tab-group" style={{ marginBottom: 0 }}>
                <button
                  className={`tab-btn ${activeTab === 'findings' ? 'active' : ''}`}
                  onClick={() => setActiveTab('findings')}
                >
                  Findings ({reportData.findings?.length || 0})
                </button>
                <button
                  className={`tab-btn ${activeTab === 'debt' ? 'active' : ''}`}
                  onClick={() => setActiveTab('debt')}
                >
                  Technical Debt & Roadmap
                </button>
                <button
                  className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                  onClick={() => setActiveTab('history')}
                >
                  Repositories ({reposHistory.length})
                </button>
              </div>

              <ReportExport reportData={reportData} />
            </div>

            {/* Executive Summary Card */}
            {reportData.executive_summary && (
              <div className="card" style={{ marginBottom: '24px', backgroundColor: 'rgba(59, 130, 246, 0.05)', borderColor: 'rgba(59, 130, 246, 0.2)' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Review Coordinator Executive Summary
                </h4>
                <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>
                  {reportData.executive_summary}
                </p>
              </div>
            )}

            {/* Tab Views */}
            {activeTab === 'findings' && (
              <FindingsTable
                findings={reportData.findings}
                onSelectFinding={setSelectedFinding}
              />
            )}

            {activeTab === 'debt' && (
              <TechDebtBreakdown reportData={reportData} />
            )}

            {activeTab === 'history' && (
              <div className="card">
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '16px' }}>
                  Previously Analyzed Repositories
                </h3>
                <div className="table-container">
                  <table className="findings-table">
                    <thead>
                      <tr>
                        <th>Repository</th>
                        <th>Default Branch</th>
                        <th>Health Score</th>
                        <th>Technical Debt</th>
                        <th>Last Analysis</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reposHistory.map((r) => (
                        <tr key={r.id}>
                          <td>
                            <div style={{ fontWeight: 600 }}>{r.name}</div>
                            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{r.url}</span>
                          </td>
                          <td>{r.default_branch}</td>
                          <td>
                            <span style={{ fontWeight: 700, color: (r.latest_analysis?.health_score || 0) >= 80 ? 'var(--success)' : 'var(--medium)' }}>
                              {r.latest_analysis?.health_score ?? 'N/A'}
                            </span>
                          </td>
                          <td>
                            <span style={{ fontWeight: 700, color: (r.latest_analysis?.technical_debt_score || 0) > 30 ? 'var(--critical)' : 'var(--text-primary)' }}>
                              {r.latest_analysis?.technical_debt_score ?? 'N/A'}
                            </span>
                          </td>
                          <td>
                            {r.latest_analysis?.created_at ? new Date(r.latest_analysis.created_at).toLocaleString() : 'N/A'}
                          </td>
                          <td>
                            {r.latest_analysis && (
                              <button
                                type="button"
                                className="preset-chip"
                                onClick={() => handleSelectHistoricalRepo(r.latest_analysis.analysis_id)}
                              >
                                View Report
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Finding Detail Slide-out Drawer */}
      <FindingDrawer
        finding={selectedFinding}
        onClose={() => setSelectedFinding(null)}
      />
    </div>
  );
}
