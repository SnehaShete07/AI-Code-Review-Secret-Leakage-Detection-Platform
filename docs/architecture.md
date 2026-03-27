# Architecture

```mermaid
flowchart LR
  UI[React Dashboard] --> API[FastAPI API Layer]
  API --> SCAN[ScanService]
  SCAN --> SECRET[SecretScanner]
  SCAN --> RULE[RuleScanner + AST/Regex Rules]
  SCAN --> DEP[DependencyScanner]
  SCAN --> POLICY[PolicyEngine]
  SCAN --> LLM[Mock/OpenAI LLM Provider]
  API --> DB[(SQLite/PostgreSQL via SQLAlchemy)]
  API --> REPORT[Report + PR Summary Services]
```

## Components
- Intake: repository path, diff text, webhook simulation payload.
- Detection: deterministic rule engine + secret regex + entropy + dependency indicators.
- Classification: category-weighted policy engine with confidence normalization.
- Output: findings, PR comments, merge recommendation, report export.


## Risk Enrichment
- Findings include CWE identifiers and friendly CWE titles for triage context.
- Policy classification computes a CVSS-like score (0.0-10.0) and qualitative level to prioritize remediation.
