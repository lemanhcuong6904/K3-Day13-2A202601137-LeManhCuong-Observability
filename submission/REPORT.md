# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: [Điền tên nhóm]
- Repository URL: `https://github.com/lengockhanh-code/Day13-K3-Observability-Flash`
- Commit SHA cuối: `8352785b8ce37386264bcd81a9555d403ac3b8a0`
- Thành viên và vai trò:
  - Nguyễn Tuấn Anh - 2A202601775 - Dashboard, SLO & Alert
  - Lê Mạnh Cương - 2A202601137 - Tracing & Prompt Version
  - Lê Ngọc Khánh - 2A202601487 - Incident, Report & Demo
  - Vũ Ngọc Thiện - 2A202601793 - Logging & PII

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
- Tổng số traces: `22`
- Link/đường dẫn dashboard: [Đính kèm ảnh dashboard runtime hoặc link dashboard nếu nhóm có share link]

## 3. Logging và tracing

- Evidence correlation ID: đã có log line minh chứng chứa `correlation_id` và các trường enrichment như `user_id_hash`, `session_id`, `feature`, `model`, `env`. Ví dụ challenge có các correlation ID: `req-c3144354`, `req-247b7289`, `req-be702446`, `req-33f8e10c`, `req-d8cf6798`.
- Evidence PII redaction: đã có log line minh chứng email, số điện thoại và số thẻ thử nghiệm bị ẩn thành `[REDACTED_...]`. Kết quả `validate_logs.py` báo `Potential PII leaks detected: 0`.
- Evidence trace waterfall: Langfuse trace view `https://cloud.langfuse.com/project/cmso2wtpx03rlad0ieop468ww/traces?searchType=id&searchType=content`. Tại đây có `Total 22` traces trong 1 ngày gần nhất. Khi điều tra challenge, lọc theo `feature=refund` hoặc `session_id` trong khung thời gian `2026-08-11 03:45Z`, sau đó mở trace để xem waterfall.
- Giải thích một span đáng chú ý: span retrieve/RAG là span đáng chú ý nhất vì incident `rag_slow` xảy ra trước bước generation, làm toàn bộ request tăng latency nhưng không sinh lỗi 500.

**Câu hỏi phản biện (Checkpoint 1):**
- *Sự khác biệt lớn nhất giữa log baseline (CP0) và log CP1:* log CP0 thiếu `correlation_id` nên không thể gom nhóm các sự kiện của cùng một request, thiếu metadata ngữ cảnh và còn rủi ro lộ dữ liệu nhạy cảm. Log CP1 đã che PII, đồng thời gắn `correlation_id` và các metadata như `user_id_hash`, `session_id`, `feature`, `model` xuyên suốt request, nên dễ truy vết và phân tích hơn.
- *Tại sao phải gọi `clear_contextvars()` ở đầu middleware?* Vì FastAPI/Uvicorn xử lý bất đồng bộ, context của request trước có thể bị giữ lại và chảy sang request sau. Nếu không xóa context cũ, log của request hiện tại có thể bị lẫn `correlation_id` hoặc metadata của request trước đó.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: `production`
- Version/label candidate: [Điền version/label đã tạo trên Langfuse]
- Trace ID của mỗi version: [Điền trace ID thực tế]
- Bằng chứng đổi label hoặc rollback: [Đính kèm ảnh hoặc trace evidence trên Langfuse]
- Ghi chú: phần code đã sẵn sàng để ghi `prompt_name`, `prompt_label`, `prompt_version`, `prompt_source` vào trace metadata và generation metadata.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: `submission/evidence/dashboard-validator.png`, `submission/evidence/validate-dashboard.txt`, và [Đính kèm ảnh dashboard runtime].
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

- Challenge ID: `day13-k3-observability-v1` (`incident=rag_slow`, `affected_feature=refund`, `latency_threshold_ms=2000`)
- Evidence metrics/dashboard: `submission/evidence/checkpoint3_role3_dashboard-incident.png`, `submission/evidence/challenge-metrics.txt`, `submission/evidence/challenge-log-evidence.txt`.
- Triệu chứng từ metrics: Sau khi chạy `python scripts/load_test.py --challenge --concurrency 5` trong lượt điều tra ngày `2026-08-11`, cả 5 request đều `200 OK` nhưng latency tăng vọt. Snapshot từ `/metrics` khi đó là: `traffic=5`, `latency_p50=3380ms`, `latency_p95=3397ms`, `latency_p99=3397ms`, `error_breakdown={}`. So với baseline trước incident khoảng `0.8-0.9s/request` trong log, đây là latency spike chứ không phải error spike.
- Evidence dashboard role 3 ghi nhận cùng loại triệu chứng: baseline `latency_p95=1143ms`; sau challenge `latency_p95=3594ms`, `latency_p99=3664ms`, `error_breakdown={}`, `quality_avg=0.8778`. Dashboard incident hiển thị latency P95 vượt SLO `3000ms`, còn traffic/error/cost/tokens/quality không vi phạm.
- Trace ID liên quan: Trên Langfuse, lọc traces theo `feature=refund` hoặc `session_id` trong khung `2026-08-11 03:45Z`. Các session của challenge: `k3-challenge-s01` → `req-c3144354`, `k3-challenge-s02` → `req-247b7289`, `k3-challenge-s03` → `req-be702446`, `k3-challenge-s04` → `req-33f8e10c`, `k3-challenge-s05` → `req-d8cf6798`. Trace waterfall kỳ vọng span chậm nằm ở bước retrieve/RAG, không phải generation.
- Log line/correlation ID liên quan: `req-be702446` (`2026-08-11T03:45:26Z` → `03:45:30Z`, `latency_ms=3388`), `req-c3144354` (`latency_ms=3380`), `req-d8cf6798` (`latency_ms=3397`), `req-33f8e10c` (`latency_ms=3354`), `req-247b7289` (`latency_ms=3361`). Tất cả đều cùng `feature=refund`, model `claude-sonnet-4-5`, env `dev`, và xuất hiện sau log `incident_enabled` với payload `rag_slow`.
- Root cause: incident `rag_slow` được bơm vào layer retrieval. Bằng chứng ở `app/mock_rag.py`: khi `STATE["rag_slow"] = True`, hàm `retrieve()` chủ động `time.sleep(2.5)`. Vì `app/agent.py` gọi `retrieve(message)` trước LLM generate, toàn bộ request bị đội latency thêm khoảng 2.5 giây.
- Fix action: tắt incident bằng `python scripts/inject_incident.py --disable` hoặc `POST /incidents/rag_slow/disable`, sau đó chạy lại load test để xác nhận latency quay về baseline. Nếu đây là production thật, cách fix kỹ thuật là timeout retrieval, cache hot queries `refund`, và fallback gracefully khi vector store chậm.
- Preventive measure: đặt alert cho p95 latency theo feature `refund` vượt `2000ms`; thêm sub-component tracing cho span `retrieve`; ghi metadata nguồn docs/cache-hit; thêm circuit breaker/timeout cho RAG; và chuẩn hóa runbook `metrics → trace waterfall → correlation ID → logs`.

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Tuấn Anh - 2A202601775 | Dashboard, SLO & Alert: dựng dashboard, cấu hình SLO và alert rule | `f1a02e5` | Biết cách chọn chỉ số quan trọng và biến chúng thành dashboard/alert hữu ích |
| Lê Mạnh Cương - 2A202601137 | Tracing & Prompt Version: cấu hình trace, theo dõi prompt version và evidence trên Langfuse | `f1a02e5` | Hiểu cách trace giúp khoanh vùng bottleneck và liên kết prompt version với request |
| Lê Ngọc Khánh - 2A202601487 | Incident, Report & Demo: chạy challenge, nối metrics → traces → logs, xác định root cause `rag_slow`, hoàn thiện báo cáo và demo | `8352785b8ce37386264bcd81a9555d403ac3b8a0` | Biết cách điều tra incident theo flow metrics → traces → logs và dùng correlation ID để chứng minh root cause |
| Vũ Ngọc Thiện - 2A202601793 | Logging & PII: chuẩn hóa JSON log, correlation ID, enrichment và PII redaction | `7a57bfb` | Hiểu vai trò của structured logging và cách giảm rủi ro lộ dữ liệu nhạy cảm |

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
