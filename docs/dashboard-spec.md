# Yêu cầu dashboard

Contract có thể kiểm tra bằng máy nằm tại `config/dashboard.yaml`. Hướng dẫn dựng và kiểm tra runtime nằm tại [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md).

Dashboard chính dùng nguồn chuẩn là `data/logs.jsonl`. Endpoint `/metrics` có thể dùng để đối chiếu nhanh khi chạy API, nhưng evidence dashboard của lab phải khớp contract trong `config/dashboard.yaml`.

## Cấu hình chung

- Tên dashboard: Day 13 AI Observability.
- Data source: `data/logs.jsonl`.
- Time range mặc định: 60 phút.
- Refresh: 30 giây.
- Cách trình bày: 6 panel chính, mỗi panel hiển thị tên, đơn vị và threshold/SLO rõ ràng.

## Sáu panel bắt buộc

| Panel | Nguồn dữ liệu | Phép tính | Đơn vị | Threshold/SLO |
|---|---|---|---|---|
| Latency percentiles | `event == "response_sent"`, field `latency_ms` | P50, P95, P99 | ms | P95 <= 3000 ms |
| Request traffic | `event == "request_received"` | count, requests/minute | requests/minute | >= 1 request/minute |
| Error rate and breakdown | `request_received`, `request_failed`, field `error_type` | error rate %, count by error type | percent | error rate <= 2% |
| Cost over time | `event == "response_sent"`, field `cost_usd` | cost/minute, total cost | USD | total cost <= 2.5 USD |
| Input and output tokens | `event == "response_sent"`, fields `tokens_in`, `tokens_out` | sum input tokens, sum output tokens | tokens | total tokens <= 50000 |
| Quality proxy | `event == "response_sent"`, field `quality_score` | mean quality score | score 0..1 | mean >= 0.75 |

## Runtime evidence

Ảnh dashboard baseline cần nhìn được:

- đủ 6 panel ở trên;
- time range 60 phút;
- đơn vị của từng panel;
- threshold hoặc SLO line/value;
- dữ liệu được tạo sau khi chạy `python scripts/load_test.py --concurrency 5`.

Kiểm tra contract trước khi chụp evidence:

```bash
python scripts/validate_dashboard.py
```

Kết quả mong đợi:

```text
HỢP LỆ: 6/6 panel có trong dashboard contract.
```
