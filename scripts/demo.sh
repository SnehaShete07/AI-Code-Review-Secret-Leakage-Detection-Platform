#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[1/4] Running repository scan against demo/vulnerable_repo"
curl -s -X POST http://localhost:8000/api/scans/repository \
  -H 'Content-Type: application/json' \
  -d '{"repo_path":"demo/vulnerable_repo"}' | tee demo/sample_reports/repo_scan.json

echo "\n[2/4] Running diff scan"
curl -s -X POST http://localhost:8000/api/scans/diff \
  -H 'Content-Type: application/json' \
  -d "$(jq -Rs --arg source 'demo-diff' '{diff_text: ., source: $source}' < demo/sample_diffs/pr_unsafe.diff)" | tee demo/sample_reports/diff_scan.json

echo "\n[3/4] Simulating webhook"
curl -s -X POST http://localhost:8000/api/webhooks/github \
  -H 'Content-Type: application/json' \
  -d "$(jq -c '{payload: .}' demo/mock_webhooks/pr_opened.json)" | tee demo/sample_reports/webhook_scan.json

echo "\n[4/4] Export latest report"
LATEST=$(curl -s http://localhost:8000/api/scans | jq '.[0].id')
curl -s http://localhost:8000/api/scans/${LATEST}/report | tee demo/sample_reports/latest_report.json

echo "Demo complete. Reports in demo/sample_reports/*.json"
