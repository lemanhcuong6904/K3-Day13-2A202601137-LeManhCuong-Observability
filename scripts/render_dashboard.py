from __future__ import annotations

import json
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
OUTPUT_PATH = REPO_ROOT / "submission" / "evidence" / "dashboard.html"


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def percentile(values: list[float], pct: int) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * pct / 100
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def status_badge(ok: bool) -> str:
    return "OK" if ok else "VIOLATED"


def format_number(value: float, digits: int = 2) -> str:
    if value == int(value):
        return str(int(value))
    return f"{value:.{digits}f}"


def main() -> None:
    records = load_records(LOG_PATH)
    responses = [r for r in records if r.get("event") == "response_sent"]
    requests = [r for r in records if r.get("event") == "request_received"]
    failures = [r for r in records if r.get("event") == "request_failed"]

    latencies = [float(r.get("latency_ms", 0)) for r in responses if isinstance(r.get("latency_ms"), int | float)]
    p50 = percentile(latencies, 50)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)

    total_requests = len(requests)
    traffic_per_minute = total_requests / 60
    error_rate = (len(failures) / total_requests * 100) if total_requests else 0.0
    error_breakdown = Counter(str(r.get("error_type", "unknown")) for r in failures)

    total_cost = sum(float(r.get("cost_usd", 0)) for r in responses)
    cost_per_minute = total_cost / 60
    tokens_in = sum(int(r.get("tokens_in", 0)) for r in responses)
    tokens_out = sum(int(r.get("tokens_out", 0)) for r in responses)
    total_tokens = tokens_in + tokens_out
    quality_scores = [float(r.get("quality_score", 0)) for r in responses if isinstance(r.get("quality_score"), int | float)]
    quality_avg = statistics.mean(quality_scores) if quality_scores else 0.0

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    cards = [
        {
            "title": "Latency percentiles",
            "metric": f"P50 {format_number(p50)} ms | P95 {format_number(p95)} ms | P99 {format_number(p99)} ms",
            "unit": "ms",
            "threshold": "SLO: P95 <= 3000 ms",
            "status": status_badge(p95 <= 3000),
        },
        {
            "title": "Request traffic",
            "metric": f"{total_requests} requests | {traffic_per_minute:.2f} req/min",
            "unit": "requests_per_minute",
            "threshold": "SLO: >= 1 request/minute",
            "status": status_badge(traffic_per_minute >= 1),
        },
        {
            "title": "Error rate and breakdown",
            "metric": f"{error_rate:.2f}% | {dict(error_breakdown) if error_breakdown else 'no errors'}",
            "unit": "percent",
            "threshold": "SLO: error rate <= 2%",
            "status": status_badge(error_rate <= 2),
        },
        {
            "title": "Cost over time",
            "metric": f"${total_cost:.4f} total | ${cost_per_minute:.4f}/min",
            "unit": "usd",
            "threshold": "SLO: total <= 2.5 USD",
            "status": status_badge(total_cost <= 2.5),
        },
        {
            "title": "Input and output tokens",
            "metric": f"{tokens_in} input | {tokens_out} output | {total_tokens} total",
            "unit": "tokens",
            "threshold": "SLO: total tokens <= 50000",
            "status": status_badge(total_tokens <= 50000),
        },
        {
            "title": "Quality proxy",
            "metric": f"Mean quality {quality_avg:.2f}",
            "unit": "score_0_to_1",
            "threshold": "SLO: mean >= 0.75",
            "status": status_badge(quality_avg >= 0.75),
        },
    ]

    card_html = "\n".join(
        f"""
        <section class="panel">
          <div class="panel-top">
            <h2>{card["title"]}</h2>
            <span class="badge {card["status"].lower()}">{card["status"]}</span>
          </div>
          <p class="metric">{card["metric"]}</p>
          <p class="meta">Unit: {card["unit"]}</p>
          <p class="threshold">{card["threshold"]}</p>
        </section>
        """
        for card in cards
    )

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Day 13 AI Observability Dashboard</title>
  <style>
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: #f6f7f9;
      color: #1f2937;
    }}
    .wrap {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px;
    }}
    header {{
      margin-bottom: 22px;
    }}
    h1 {{
      font-size: 30px;
      margin: 0 0 8px;
      letter-spacing: 0;
    }}
    .sub {{
      color: #4b5563;
      margin: 0;
      line-height: 1.5;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }}
    .panel {{
      background: white;
      border: 1px solid #d7dce2;
      border-radius: 8px;
      padding: 16px;
      min-height: 150px;
      box-sizing: border-box;
    }}
    .panel-top {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }}
    h2 {{
      font-size: 16px;
      margin: 0;
      letter-spacing: 0;
    }}
    .metric {{
      font-size: 22px;
      line-height: 1.25;
      margin: 18px 0 12px;
      font-weight: 700;
    }}
    .meta, .threshold {{
      font-size: 13px;
      color: #4b5563;
      margin: 6px 0 0;
    }}
    .badge {{
      font-size: 12px;
      font-weight: 700;
      padding: 4px 7px;
      border-radius: 999px;
      white-space: nowrap;
    }}
    .ok {{
      color: #065f46;
      background: #d1fae5;
    }}
    .violated {{
      color: #991b1b;
      background: #fee2e2;
    }}
    @media (max-width: 900px) {{
      .grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main class="wrap">
    <header>
      <h1>Day 13 AI Observability Dashboard</h1>
      <p class="sub">Source: data/logs.jsonl | Time range: 60 minutes | Refresh: 30 seconds | Generated: {generated_at}</p>
    </header>
    <div class="grid">
      {card_html}
    </div>
  </main>
</body>
</html>
"""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
