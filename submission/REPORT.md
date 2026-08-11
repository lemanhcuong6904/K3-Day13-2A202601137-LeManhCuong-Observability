# Day 13 Observability Report

## 1. Team Information

- Team name:
- Repository URL:
- Final commit SHA:
- Members and roles:

## 2. Technical Results

- `validate_logs.py` score: 100/100
- Total traces:
- Remaining PII leaks: 0
- Dashboard link/path:
- Evidence collection date: 2026-08-11

## 3. Logging and Tracing

- Correlation ID evidence: attached log lines show `correlation_id` and enrichment fields such as `user_id_hash`, `session_id`, `feature`, and `model`.
- PII redaction evidence: attached log lines show email/phone/card values redacted as `[REDACTED_...]`.
- Trace waterfall evidence:
- Notable span explanation:
- Waterfall trace ID:
- Attached evidence files:

## 4. Prompt Versioning

- Prompt name:
- Baseline version/label:
- Candidate version/label:
- Trace IDs for each version:
- Promote or rollback evidence:
- Production trace ID after promote:
- Production trace ID after rollback:
- Prompt/version evidence files:

## 5. Dashboard, SLO, and Alerts

- `validate_dashboard.py` result:
- Dashboard evidence:
- Chosen SLO and reason:
- Alert rules and runbook:
- Key dashboard thresholds:

## 6. Challenge Investigation

- Challenge ID:
- Symptoms from metrics:
- Related trace ID:
- Related log line/correlation ID:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Individual Contribution

For each member, list scope and commit/PR references.

| Member | Scope | Commit/PR | Key learning |
|---|---|---|---|
| | | | |

## 8. Role 2 Evidence Index

| Item | Suggested path | Notes |
|---|---|---|
| Validate logs | `submission/evidence/validate-logs.txt` | Final validator output for checkpoint 1 |
| Trace list >= 10 | `submission/evidence/traces-list.png` | Langfuse trace list |
| Waterfall | `submission/evidence/trace-waterfall.png` | One full waterfall trace |
| Prompt versions | `submission/evidence/prompt-versions.png` | Shows v1/v2 and labels |
| Baseline trace | `submission/evidence/trace-baseline.png` | Shows `prompt_name`, `prompt_label`, `prompt_version` |
| Candidate trace | `submission/evidence/trace-candidate.png` | Shows `prompt_name`, `prompt_label`, `prompt_version` |
| Promote | `submission/evidence/prompt-promote.png` | `production` moved to v2 |
| Rollback | `submission/evidence/prompt-rollback.png` | `production` moved back to v1 |
| Dashboard validator | `submission/evidence/validate-dashboard.txt` | Output of `python scripts/validate_dashboard.py` |
| Dashboard runtime | `submission/evidence/dashboard.png` | 6 panels with threshold/SLO |
