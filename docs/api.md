# API Reference

## Endpoints
- `GET /api/health`
- `POST /api/scans/repository` `{ repo_path }`
- `POST /api/scans/diff` `{ diff_text, source }`
- `POST /api/webhooks/github` `{ payload }`
- `GET /api/scans`
- `GET /api/scans/{id}`
- `GET /api/scans/{id}/report`

## Response Notes
Each scan response includes:
- stored scan object
- findings list
- `pr_summary`
- mock PR comment suggestions
