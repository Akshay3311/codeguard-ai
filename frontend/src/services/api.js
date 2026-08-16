const BASE_URL = '';

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchOverviewStats() {
  const res = await fetch(`${BASE_URL}/api/v1/overview/stats`);
  if (!res.ok) throw new Error('Failed to fetch dashboard stats');
  return res.json();
}

export async function startAnalysis(repositoryUrl, branch = 'main') {
  const res = await fetch(`${BASE_URL}/api/v1/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ repository_url: repositoryUrl, branch })
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to trigger repository analysis');
  }
  return res.json();
}

export async function fetchAnalysisStatus(analysisId) {
  const res = await fetch(`${BASE_URL}/api/v1/analysis/${analysisId}`);
  if (!res.ok) throw new Error('Failed to fetch analysis status');
  return res.json();
}

export async function fetchAnalysisFindings(analysisId, { category, severity, filePath } = {}) {
  const params = new URLSearchParams();
  if (category && category !== 'all') params.append('category', category);
  if (severity && severity !== 'all') params.append('severity', severity);
  if (filePath) params.append('file_path', filePath);

  const res = await fetch(`${BASE_URL}/api/v1/analysis/${analysisId}/findings?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch findings');
  return res.json();
}

export async function fetchFullReport(analysisId) {
  const res = await fetch(`${BASE_URL}/api/v1/analysis/${analysisId}/report`);
  if (!res.ok) throw new Error('Failed to fetch full report');
  return res.json();
}

export async function fetchRepositories() {
  const res = await fetch(`${BASE_URL}/api/v1/repositories`);
  if (!res.ok) throw new Error('Failed to fetch repository history');
  return res.json();
}
