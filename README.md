# AI Code Review + Secret Leakage Detection Platform

A production-style full-stack portfolio project that performs AI-assisted security code review for repositories, diffs, and GitHub-style webhook events.

## Why this project matters
Modern teams ship quickly, and security issues (hardcoded secrets, injection risks, unsafe AI-agent design) often slip into PRs. This platform demonstrates how to combine deterministic static analysis with policy scoring and AI-generated remediation in a safe, offline-first architecture.

## Resume-ready highlights
- Built an AI-assisted code review and secret detection platform integrating static analysis, policy-based severity classification, and GitHub-style PR review workflows.
- Implemented rule-based and AI-assisted detection for secret leakage, injection risks, insecure tool use, and prompt injection exposure across Python, JS/TS, and config files.
- Designed deterministic offline demo behavior with optional OpenAI-compatible provider for enhanced remediation narratives.

## Features
- **Repository scan** (local path)
- **Diff scan** (raw unified diff)
- **Webhook simulation** (`/api/webhooks/github`)
- **Secret detection** (AWS keys, GitHub/OpenAI/Slack/Stripe token patterns, JWT-like strings, private keys, generic credentials)
- **Static security rules**:
  - Python: `eval`, `exec`, `subprocess(... shell=True)`, unsafe pickle-like patterns, TLS verify disabled
  - JS/TS: `eval`, `new Function`, `child_process.exec`
  - Config: unsafe YAML load, broad CORS, hardcoded passwords
  - AI-agent security: prompt-injection phrase propagation, direct prompt concat with user input, over-permissioned tools, direct model-to-tool execution
- **Policy engine**: category + confidence => severity and merge recommendation
- **PR review artifacts**: grouped summary, mock review comments, merge decision
- **Report export**: JSON + Markdown
- **Persistent scan history** via SQLAlchemy
- **Frontend dashboard** with findings, details, policy panel, scan history, and severity chart

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Pydantic, pytest
- **Frontend**: React + TypeScript + Vite + Tailwind + Recharts
- **Storage**: SQLite by default (Postgres-compatible via `APP_DB_URL`)
- **AI Layer**: Mock provider (default) + OpenAI-compatible provider (optional)

## Architecture
See [docs/architecture.md](docs/architecture.md).

## Repository structure
```text
backend/
  app/
    api/ core/ llm/ models/ policies/ rules/ scanners/ schemas/ services/ utils/
  tests/
frontend/
  src/components src/lib src/pages src/types

demo/
  vulnerable_repo/
  sample_diffs/
  mock_webhooks/
  sample_reports/
docs/
scripts/
```

## Quickstart (offline-friendly)
### 1) Install dependencies
```bash
make install
```

### 2) Start backend + frontend
```bash
make backend
make frontend
```

### 3) Open dashboard
- `http://localhost:5173`

### 4) Demo with one command
```bash
make demo
```

## Docker
```bash
docker-compose up
```

## Environment variables
See `.env.example`.

## API overview
See [docs/api.md](docs/api.md).

## Demo flow
See [docs/demo.md](docs/demo.md).

## Security model
- Never executes scanned code.
- Core detection is deterministic and rules-based.
- Secrets are masked before persistence/reporting.
- LLM is used only for explanation/remediation assistance.

## Testing
```bash
make test
```
Includes:
- secret regex + entropy tests
- Python AST and JS risky-pattern rule tests
- policy severity tests
- repository/diff/webhook API integration tests

## Screenshots
- Add dashboard screenshots under `docs/screenshots/`.

## Design decisions
- Chose deterministic scanning to ensure offline reliability and avoid LLM hallucination risk.
- Kept extensible rule architecture (`BaseRule` + registry) for easy custom rule onboarding.
- Prioritized local demo realism over cloud dependencies.

## Limitations
- No deep taint/dataflow engine yet.
- Diff-to-line mapping is intentionally lightweight.
- Frontend uses a compact single-page workflow for demo speed.

## Roadmap
- SARIF export
- False-positive suppression UI
- Scan history comparison
- Slack/email notification mock
- Dark mode refinements + richer charts

## Interview talking points
- How deterministic scanning + policy engine improves trustworthiness.
- Tradeoff between high recall (regex heuristics) and false positives.
- Why secret masking and non-execution constraints matter in secure tooling.
- How webhook simulation enables offline demo without GitHub credentials.
