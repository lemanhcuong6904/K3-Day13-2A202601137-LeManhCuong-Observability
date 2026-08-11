# Alert và runbook

Mỗi alert bên dưới dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên hàm hay implementation nội bộ. Khi có cảnh báo, nhóm điều tra theo chuỗi Metrics -> Traces -> Logs -> Root cause -> Fix -> Preventive measure.

## Alert 1

- Tên: `high_latency_p95`
- Severity: warning
- SLI/SLO liên quan: `latency_p95_ms`, objective `<= 3000 ms`
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000 for 5 minutes`
- Ảnh hưởng tới người dùng: người dùng thấy API phản hồi chậm, trải nghiệm chat bị trễ, demo hoặc workflow điều tra incident khó theo dõi đúng thời gian thực.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard Latency panel, so sánh P50/P95/P99 trong 60 phút gần nhất với ngưỡng 3000 ms.
  2. Mở Langfuse traces trong cùng khoảng thời gian, chọn một trace chậm và kiểm tra waterfall/span nào chiếm thời gian lớn nhất.
  3. Dùng `correlation_id` của trace chậm để tìm trong `data/logs.jsonl`, đối chiếu `latency_ms`, `feature`, `model`, `session_id` và các log request/response cùng request.
- Mitigation tạm thời: giảm concurrency hoặc traffic test, tắt incident practice nếu đang bật, rollback thay đổi prompt/config gần nhất nếu nó làm tăng latency, sau đó chạy lại load test để xác nhận P95 giảm.
- Owner: on-call-engineer

## Alert 2

- Tên: `elevated_error_rate`
- Severity: critical
- SLI/SLO liên quan: `error_rate_pct`, objective `<= 2%`
- Điều kiện và thời gian duy trì: `error_rate_pct > 2 for 3 minutes`
- Ảnh hưởng tới người dùng: một phần request `/chat` thất bại, người dùng nhận lỗi thay vì câu trả lời, dữ liệu trace/log có thể thiếu nếu lỗi xảy ra trước khi response hoàn tất.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard Errors panel, xác nhận error rate và breakdown theo `error_type`.
  2. Lọc `data/logs.jsonl` theo `event == "request_failed"` hoặc dùng `Select-String -Path data\logs.jsonl -Pattern "request_failed"` để lấy `correlation_id` và `error_type`.
  3. Mở trace tương ứng trên Langfuse, kiểm tra input, metadata, prompt label/version và generation/span gần điểm lỗi.
- Mitigation tạm thời: rollback prompt label hoặc config vừa thay đổi, tắt incident injection nếu đang bật, trả về fallback an toàn cho lỗi đã biết, sau đó chạy lại validator/load test để xác nhận error rate giảm.
- Owner: on-call-engineer

## Alert 3

- Tên: `quality_degradation`
- Severity: warning
- SLI/SLO liên quan: `quality_score_avg`, objective `>= 0.75`
- Điều kiện và thời gian duy trì: `quality_score_avg < 0.75 for 5 minutes`
- Ảnh hưởng tới người dùng: hệ thống vẫn trả lời nhưng chất lượng thấp, câu trả lời có thể thiếu thông tin, không bám tài liệu, hoặc không phù hợp với feature đang gọi.
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard Quality panel, xác nhận mean `quality_score` trong 60 phút gần nhất có thấp hơn 0.75 không.
  2. So sánh traces theo `prompt_label` và `prompt_version` để xem chất lượng giảm có trùng với candidate/promotion/rollback prompt không.
  3. Tìm log theo `correlation_id` của request chất lượng thấp, kiểm tra `feature`, `tokens_in`, `tokens_out`, `cost_usd` và answer preview đã được redact.
- Mitigation tạm thời: rollback `production` prompt về version baseline đã ổn định, giảm phạm vi thay đổi prompt, hoặc tạm chuyển traffic về label cũ; sau đó chạy cùng input để so sánh trace và quality score.
- Owner: team-lead
