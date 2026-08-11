# Evidence Checklist

Put Role 2 evidence files in this folder and reference them from `submission/REPORT.md`.

Suggested filenames:

- `validate-logs.txt`
- `traces-list.png`
- `trace-waterfall.png`
- `prompt-versions.png`
- `trace-baseline.png`
- `trace-candidate.png`
- `prompt-promote.png`
- `prompt-rollback.png`
- `validate-dashboard.txt`
- `dashboard.png`

Required contents:

- `trace-baseline.png` and `trace-candidate.png` should show `prompt_name`, `prompt_label`, and `prompt_version`.
- `prompt-promote.png` and `prompt-rollback.png` should prove the `production` label changed versions.
- `dashboard.png` should show all 6 panels and the threshold/SLO line.
- `validate-logs.txt` and `validate-dashboard.txt` should keep the raw validator outputs.
