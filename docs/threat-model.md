# Threat Model

## Assets
- Source code and pull request diffs.
- Secrets accidentally committed to repositories.
- AI agent configuration and prompt templates.

## Primary Threats
- Secret leakage in code/config/docs.
- Command injection and insecure deserialization.
- Prompt injection propagation into tool execution.
- Over-permissioned autonomous agent tooling.

## Controls
- Deterministic pattern/rule-based detection (no LLM-only decisions).
- Secret masking before persistence and display.
- No execution of scanned code.
- Policy-driven merge recommendation.

## Limitations
- Static analysis only; no runtime dataflow engine.
- Regex and heuristics can still produce false positives/negatives.
