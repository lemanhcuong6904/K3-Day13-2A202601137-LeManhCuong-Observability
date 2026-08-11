# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: `100/100` (baseline ban đầu: `30/100`)
- Chi tiết `validate_logs.py`:
  - Tổng số log đã phân tích: `11`
  - Số record thiếu required fields: `0`
  - Số record thiếu enrichment: `0`
  - Số correlation ID duy nhất: `3`
  - Số PII leak còn lại: `0`
- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Kết quả test đã chạy: `14 passed`
- Tổng số traces:
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID: đã có log line minh chứng chứa `correlation_id` và các trường enrichment như `user_id_hash`, `session_id`, `feature`, `model`, `env`.
- Evidence PII redaction: đã có log line minh chứng email, số điện thoại và số thẻ thử nghiệm bị ẩn thành `[REDACTED_...]`.
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

**Câu hỏi phản biện (Checkpoint 1):**
- *Sự khác biệt lớn nhất giữa log baseline (CP0) và log CP1:* log CP0 thiếu `correlation_id` nên không thể gom nhóm các sự kiện của cùng một request, thiếu metadata ngữ cảnh và còn rủi ro lộ dữ liệu nhạy cảm. Log CP1 đã che PII, đồng thời gắn `correlation_id` và các metadata như `user_id_hash`, `session_id`, `feature`, `model` xuyên suốt request, nên dễ truy vết và phân tích hơn.
- *Tại sao phải gọi `clear_contextvars()` ở đầu middleware?* Vì FastAPI/Uvicorn xử lý bất đồng bộ, context của request trước có thể bị giữ lại và chảy sang request sau. Nếu không xóa context cũ, log của request hiện tại có thể bị lẫn `correlation_id` hoặc metadata của request trước đó.

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:
- Ghi chú: phần code đã sẵn sàng để ghi `prompt_name`, `prompt_label`, `prompt_version`, `prompt_source` vào trace metadata và generation metadata.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: hợp lệ, đủ `6/6 panel`.
- Evidence dashboard: `submission/evidence/dashboard-validator.png` và `submission/evidence/validate-dashboard.txt`. Cần bổ sung ảnh dashboard runtime baseline sau khi nhóm dựng dashboard bằng công cụ đã chọn.
- SLO đã chọn và lý do:
  - `latency_p95_ms <= 3000`: giữ P95 dưới 3 giây để người dùng không thấy phản hồi chat bị chậm rõ rệt.
  - `error_rate_pct <= 2`: giữ tỷ lệ lỗi thấp để đa số request `/chat` trả lời thành công.
  - `daily_cost_usd <= 2.5`: kiểm soát ngân sách vận hành trong phạm vi lab.
  - `quality_score_avg >= 0.75`: đảm bảo chất lượng trung bình không tụt dưới mức chấp nhận được.
- Alert rules và runbook: đã hoàn thiện `config/alert_rules.yaml` với 3 alert symptom-based (`high_latency_p95`, `elevated_error_rate`, `quality_degradation`) và runbook xử lý tại `docs/alerts.md`.
- Các panel theo contract đã có trong `config/dashboard.yaml`: `latency`, `traffic`, `errors`, `cost`, `tokens`, `quality`.

**Câu hỏi phản biện (Checkpoint 2):**
- Alert nên được thiết kế dựa trên triệu chứng người dùng thấy hoặc SLO vì đây là tín hiệu phản ánh tác động thật của sự cố, ví dụ phản hồi chậm, tỷ lệ lỗi cao hoặc chất lượng giảm. Nếu alert dựa trên tên hàm, tên span hoặc chi tiết implementation, cảnh báo dễ bị lỗi thời khi code refactor, khó hiểu với người trực vận hành và có thể bỏ sót sự cố xảy ra ở tầng khác. Symptom-based alert giúp nhóm ưu tiên đúng tác động, sau đó dùng metrics, traces và logs để khoanh vùng root cause.

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Role 2 | Hoàn thiện checkpoint 1 về correlation ID, log enrichment, PII-safe logging | `38d41d9` | Cần bind context ở đúng cả middleware và request handler để log/tracing khớp nhau |
| Role 2 | Hoàn thiện checkpoint 2 về báo cáo, evidence validator và hợp nhất lại trên nền `group/main` | `132eaea` | Khi làm việc song song nhiều role, rebase và giải quyết conflict theo từng checkpoint giúp giữ lịch sử rõ ràng |
| Role 3 | Hoàn thiện dashboard spec, SLO note, alert rules và alert runbook cho checkpoint 2 | TBD | Alert nên bám triệu chứng/SLO trước, rồi dùng trace và log để điều tra nguyên nhân cụ thể |

## 8. File evidence đã có trong repo

- `submission/evidence/validate-logs.txt`
- `submission/evidence/validate-dashboard.txt`
- `submission/evidence/README.md`

## 9. Việc còn lại để nộp đầy đủ

- Bổ sung ảnh danh sách traces trên Langfuse với tối thiểu `10 traces`.
- Bổ sung ảnh trace waterfall.
- Bổ sung ảnh hai prompt version và trace tương ứng cho `baseline` và `candidate`.
- Bổ sung ảnh thao tác promote/rollback label `production`.
- Điền link dashboard runtime và các trace ID thực tế vào các mục còn trống ở trên.
