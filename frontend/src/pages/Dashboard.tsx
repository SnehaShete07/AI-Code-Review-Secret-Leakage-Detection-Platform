import { useEffect, useMemo, useState } from 'react';

import { FindingTable } from '../components/FindingTable';
import { SeverityChart } from '../components/SeverityChart';
import { fetchReport, fetchScans, runDiffScan, runRepoScan, simulateWebhook } from '../lib/api';
import type { Finding, Scan, ScanSummaryResponse } from '../types';

const SAMPLE_REPO = '../demo/vulnerable_repo';
const SAMPLE_DIFF = `diff --git a/app.py b/app.py\n+++ b/app.py\n@@ -1,1 +1,1 @@\n+token = \"ghp_abcdabcdabcdabcdabcdabcd\"\n+subprocess.run(cmd, shell=True)`;

export default function Dashboard() {
  const [repoPath, setRepoPath] = useState(SAMPLE_REPO);
  const [diffText, setDiffText] = useState(SAMPLE_DIFF);
  const [scans, setScans] = useState<Scan[]>([]);
  const [activeScan, setActiveScan] = useState<Scan | null>(null);
  const [activeFinding, setActiveFinding] = useState<Finding | null>(null);
  const [prSummary, setPrSummary] = useState('');
  const [prComments, setPrComments] = useState<string[]>([]);
  const [reportMarkdown, setReportMarkdown] = useState('');

  async function refreshScans() {
    const data = await fetchScans();
    setScans(data);
    if (!activeScan && data.length > 0) setActiveScan(data[0]);
  }

  useEffect(() => { refreshScans(); }, []);

  async function handleRun(action: Promise<ScanSummaryResponse>) {
    const res = await action;
    setActiveScan(res.scan);
    setActiveFinding(res.scan.findings[0] ?? null);
    setPrSummary(res.pr_summary);
    setPrComments(res.comments);
    await refreshScans();
  }

  async function exportReport() {
    if (!activeScan) return;
    const report = await fetchReport(activeScan.id);
    setReportMarkdown(report.markdown_report);
  }

  const policyData = useMemo(() => activeScan?.summary.categories ?? {}, [activeScan]);

  return (
    <main className="max-w-7xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">AI Code Review + Secret Leakage Detection Platform</h1>
      <section className="grid md:grid-cols-3 gap-4">
        <div className="card space-y-2">
          <h2 className="font-semibold">Repository Scan</h2>
          <input className="input" value={repoPath} onChange={(e) => setRepoPath(e.target.value)} />
          <button className="btn" onClick={() => handleRun(runRepoScan(repoPath))}>Run Repo Scan</button>
        </div>
        <div className="card space-y-2">
          <h2 className="font-semibold">Diff / PR Scan</h2>
          <textarea className="input h-24" value={diffText} onChange={(e) => setDiffText(e.target.value)} />
          <button className="btn" onClick={() => handleRun(runDiffScan(diffText))}>Run Diff Scan</button>
        </div>
        <div className="card space-y-2">
          <h2 className="font-semibold">Webhook Simulation</h2>
          <button className="btn" onClick={() => handleRun(simulateWebhook({ action: 'opened', pull_request: { html_url: 'https://example/pr/demo', diff_text: diffText } }))}>Simulate GitHub Webhook</button>
          <button className="btn" onClick={exportReport}>Export Report</button>
        </div>
      </section>

      {activeScan && (
        <section className="grid lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 space-y-4">
            <FindingTable findings={activeScan.findings} onSelect={setActiveFinding} />
            <div className="card">
              <h3 className="font-semibold">Mock PR Review Comments</h3>
              <p className="text-cyan-300 my-2">{prSummary}</p>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {prComments.map((c, idx) => <li key={idx}>{c}</li>)}
              </ul>
            </div>
          </div>
          <div className="space-y-4">
            <SeverityChart severity={activeScan.summary.severity} />
            <div className="card">
              <h3 className="font-semibold">Policy Dashboard</h3>
              <ul>{Object.entries(policyData).map(([k,v]) => <li key={k}>{k}: {v}</li>)}</ul>
            </div>
          </div>
        </section>
      )}

      {activeFinding && (
        <section className="card">
          <h2 className="font-semibold">Finding Details</h2>
          <p><b>{activeFinding.title}</b> [{activeFinding.severity}]</p>
          <p className="text-sm">{activeFinding.file_path}:{activeFinding.line_number}</p>
          <pre className="bg-slate-950 p-3 rounded mt-2 whitespace-pre-wrap">{activeFinding.snippet}</pre>
          <p className="mt-2">{activeFinding.explanation}</p>
          <p className="mt-2 text-cyan-300">Remediation: {activeFinding.remediation}</p>
        </section>
      )}

      <section className="card">
        <h3 className="font-semibold">Scan History</h3>
        <ul className="text-sm space-y-1">
          {scans.map((s) => (
            <li key={s.id} className="cursor-pointer" onClick={() => setActiveScan(s)}>
              #{s.id} {s.scan_type} - {s.source} - {s.summary?.total ?? 0} findings
            </li>
          ))}
        </ul>
      </section>

      {reportMarkdown && (
        <section className="card">
          <h3 className="font-semibold">Markdown Report Preview</h3>
          <pre className="text-xs whitespace-pre-wrap">{reportMarkdown}</pre>
        </section>
      )}
    </main>
  );
}
