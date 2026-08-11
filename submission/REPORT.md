# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (Baseline ban đầu: 30/100)
- Tổng số traces:
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID: *(Đã đính kèm log line minh chứng có chứa `correlation_id` và các trường enrichment như `user_id_hash`, `session_id`, `feature`, `model`)*
- Evidence PII redaction: *(Đã đính kèm log line minh chứng email/sđt bị ẩn thành `[REDACTED_...]`)*
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

**Câu hỏi phản biện (Checkpoint 1):**
- *Sự khác biệt lớn nhất giữa log baseline (CP0) và log CP1:* Log CP0 thiếu `correlation_id` nên không thể gom nhóm các sự kiện của cùng 1 request, thiếu metadata (ngữ cảnh) và để lộ nguyên văn dữ liệu nhạy cảm (PII). Log CP1 đã tự động che PII, đồng thời gắn `correlation_id` và các metadata (`user_id_hash`, v.v.) xuyên suốt mọi dòng log của request, giúp dễ dàng truy vết và phân tích.
- *Tại sao phải gọi `clear_contextvars()` ở đầu middleware?* Vì FastAPI/Uvicorn xử lý bất đồng bộ (async), môi trường context (như `structlog.contextvars`) có thể bị dùng lại hoặc chia sẻ giữa các request. Nếu không xóa (clear) context cũ, dữ liệu (ví dụ ID, email) của request trước đó có thể bị rò rỉ (leak) và ghi nhầm vào log của request hiện tại.

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

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
| | | | |
