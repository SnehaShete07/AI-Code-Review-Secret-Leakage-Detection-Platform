# Demo Guide

1. Start backend: `make backend`
2. Start frontend: `make frontend`
3. Open dashboard on `http://localhost:5173`
4. Click:
   - Run Repo Scan
   - Run Diff Scan
   - Simulate GitHub Webhook
   - Export Report
5. Run scripted flow: `make demo`

Demo assets:
- Vulnerable repo: `demo/vulnerable_repo`
- Sample diff: `demo/sample_diffs/pr_unsafe.diff`
- Mock webhook: `demo/mock_webhooks/pr_opened.json`
