import type { Scan, ScanSummaryResponse } from '../types';

const API = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api';

export async function runRepoScan(repoPath: string): Promise<ScanSummaryResponse> {
  const res = await fetch(`${API}/scans/repository`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ repo_path: repoPath }),
  });
  if (!res.ok) throw new Error('Repository scan failed');
  return res.json();
}

export async function runDiffScan(diffText: string): Promise<ScanSummaryResponse> {
  const res = await fetch(`${API}/scans/diff`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ diff_text: diffText, source: 'frontend-diff-input' }),
  });
  if (!res.ok) throw new Error('Diff scan failed');
  return res.json();
}

export async function simulateWebhook(payload: object): Promise<ScanSummaryResponse> {
  const res = await fetch(`${API}/webhooks/github`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ payload }),
  });
  if (!res.ok) throw new Error('Webhook simulation failed');
  return res.json();
}

export async function fetchScans(): Promise<Scan[]> {
  const res = await fetch(`${API}/scans`);
  if (!res.ok) throw new Error('Unable to fetch scans');
  return res.json();
}

export async function fetchReport(scanId: number): Promise<{ markdown_report: string; json_report: object }> {
  const res = await fetch(`${API}/scans/${scanId}/report`);
  if (!res.ok) throw new Error('Unable to export report');
  return res.json();
}
