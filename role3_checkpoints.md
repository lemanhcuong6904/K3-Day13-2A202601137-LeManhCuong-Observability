# Checkpoint vai trò 3 - Dashboard, SLO & Alert

Vai trò của bạn: **Dashboard, SLO & Alert**.

Phạm vi chính:

- Dựng dashboard đủ 6 panel từ `data/logs.jsonl`.
- Đảm bảo dashboard có time range 60 phút, refresh 30 giây, đơn vị và threshold/SLO rõ ràng.
- Kiểm tra `config/dashboard.yaml`, `config/slo.yaml`, `config/alert_rules.yaml`.
- Chuẩn bị evidence: validator dashboard, ảnh dashboard baseline, ảnh dashboard incident.
- Hỗ trợ nhóm Incident/Report bằng số liệu metrics và evidence SLO/alert.

Ngoài phạm vi chính của bạn:

- Không phụ trách sửa correlation ID, metadata log, PII redaction. Đây là phần của vai trò Logging & PII.
- Không phụ trách tạo prompt v1/v2, label/rollback. Đây là phần của vai trò Tracing & Prompt Version.
- Không phụ trách chạy challenge chính thức và viết root cause cuối cùng, nhưng bạn cần cung cấp dashboard evidence cho người làm Incident/Report.

---

## Checkpoint 0 - Setup và baseline

### Mục tiêu

Xác nhận môi trường đã chạy được, API sinh log, validator baseline có kết quả để ghi vào báo cáo.

### Việc bạn cần làm

1. Đảm bảo virtual environment đang active:

```powershell
.\.venv\Scripts\Activate.ps1
```

2. Chạy API ở terminal 1:

```powershell
uvicorn app.main:app --reload --env-file .env
```

3. Chạy load test ở terminal 2:

```powershell
python scripts/load_test.py
```

4. Kiểm tra `data/logs.jsonl` đã được tạo:

```powershell
Get-Content data\logs.jsonl -TotalCount 3
```

5. Chạy validator baseline:

```powershell
python scripts/validate_logs.py
python scripts/validate_dashboard.py
python -m pytest -q
```

### Giải thích

Ở bước setup, điểm log có thể thấp vì starter code chưa có correlation ID và enrichment. Đây là baseline để chứng minh trạng thái trước khi sửa, không phải lỗi của phần dashboard.

### Đầu ra cần có

- API load test trả HTTP 200.
- `data/logs.jsonl` tồn tại và đọc được.
- Baseline `validate_logs.py` được ghi lại, ví dụ `30/100`.
- Kết quả `validate_dashboard.py` được ghi lại.
- Nếu có thể, chụp ảnh terminal cho:
  - load test 200;
  - 3 dòng đầu của `data/logs.jsonl`;
  - baseline validator.

### Cần từ thành viên khác

- Logging & PII: chưa cần sửa ngay, nhưng cần thông báo baseline đang thiếu `correlation_id` và enrichment.
- Tracing & Prompt Version: xác nhận Langfuse key đã đúng; nếu prompt chưa có thì có thể thấy warning fallback prompt.
- Incident/Report & Demo: ghi baseline vào report.

---

## Checkpoint 1 - Logging & PII

### Mục tiêu của checkpoint

Team Logging & PII hoàn thiện log để dashboard có đủ dữ liệu đầu vào.

### Việc bạn cần làm

1. Đọc và xác nhận các field dashboard cần từ log:

```powershell
Get-Content config\dashboard.yaml
Get-Content docs\DASHBOARD_SETUP.md
```

2. Sau khi Logging & PII sửa code, chạy lại load test:

```powershell
python scripts/load_test.py
python scripts/validate_logs.py
```

3. Kiểm tra log mới có các field cần thiết:

```powershell
Get-Content data\logs.jsonl -Tail 10
```

4. Nếu cần tìm nhanh field trong log:

```powershell
Select-String -Path data\logs.jsonl -Pattern "correlation_id"
Select-String -Path data\logs.jsonl -Pattern "latency_ms"
Select-String -Path data\logs.jsonl -Pattern "tokens_in"
Select-String -Path data\logs.jsonl -Pattern "cost_usd"
Select-String -Path data\logs.jsonl -Pattern "quality_score"
```

### Giải thích

Dashboard của bạn không đọc `/metrics` làm nguồn chính. Dashboard bắt buộc đọc `data/logs.jsonl`, nên nếu log thiếu field thì dashboard sẽ không chứng minh được 6 panel.

### Các field bạn cần yêu cầu Logging & PII bàn giao

Bắt buộc cho dashboard:

- `ts`
- `event`
- `level`
- `service`
- `correlation_id`
- `latency_ms` trong event `response_sent`
- `tokens_in` trong event `response_sent`
- `tokens_out` trong event `response_sent`
- `cost_usd` trong event `response_sent`
- `quality_score` trong event `response_sent`
- `error_type` nếu có event `request_failed`

Nên có để trace/report tốt hơn:

- `user_id_hash`
- `session_id`
- `feature`
- `model`
- `env`

### Đầu ra cần có

- `validate_logs.py` đạt ít nhất `80/100`.
- Một đoạn log có `correlation_id` hợp lệ, không còn `MISSING`.
- Một đoạn log `response_sent` có `latency_ms`, token, cost và quality.
- Evidence cho thấy PII đã bị redact, ví dụ `[REDACTED_EMAIL]`.

### Cần từ thành viên khác

- Logging & PII:
  - Sửa `app/middleware.py` để có correlation ID.
  - Sửa `app/main.py` để bind metadata.
  - Sửa `app/logging_config.py` để bật PII scrubber trước khi ghi file.
  - Bàn giao log hợp lệ và điểm validator.
- Tracing & Prompt Version:
  - Chưa phụ thuộc mạnh ở checkpoint này.
- Incident/Report & Demo:
  - Lưu evidence log hợp lệ vào report.

---

## Checkpoint 2 - Metrics, traces và dashboard

### Mục tiêu của bạn

Hoàn thiện phần chính của vai trò 3: dashboard 6 panel, SLO threshold và alert/runbook.

### Việc bạn cần làm

1. Chạy load test để có đủ dữ liệu baseline:

```powershell
python scripts/load_test.py --concurrency 5
```

2. Kiểm tra dashboard contract:

```powershell
python scripts/validate_dashboard.py
```

Kết quả mong đợi:

```text
HỢP LỆ: 6/6 panel
```

Nếu output tiếng Việt bị lỗi font thì vẫn đọc ý nghĩa từ số `6/6 panel`.

3. Kiểm tra `config/dashboard.yaml` có đúng 6 panel:

- `latency`
- `traffic`
- `errors`
- `cost`
- `tokens`
- `quality`

4. Kiểm tra mỗi panel dùng đúng source:

```text
data/logs.jsonl
```

5. Kiểm tra time range và refresh:

```yaml
time_range_minutes: 60
refresh_seconds: 30
```

6. Kiểm tra threshold:

| Panel | Chỉ số | Threshold |
|---|---|---:|
| Latency | P95 latency | <= 3000 ms |
| Traffic | rate/minute | >= 1 request/minute |
| Errors | error rate | <= 2% |
| Cost | total cost | <= 2.5 USD |
| Tokens | total tokens | <= 50000 tokens |
| Quality | mean quality | >= 0.75 |

7. Kiểm tra `config/slo.yaml`:

```powershell
Get-Content config\slo.yaml
```

SLO cần khớp dashboard:

- `latency_p95_ms.objective: 3000`
- `error_rate_pct.objective: 2`
- `daily_cost_usd.objective: 2.5`
- `quality_score_avg.objective: 0.75`

8. Hoàn thiện alert rules nếu được phân công sửa file:

```powershell
Get-Content config\alert_rules.yaml
Get-Content docs\alerts.md
```

Gợi ý 3 alert hợp lý:

- High latency: P95 latency > 3000 ms.
- High error rate: error rate > 2%.
- Quality degradation: average quality < 0.75.

9. Dựng dashboard runtime theo công cụ nhóm chọn.

Chấp nhận một trong các cách:

- Streamlit local.
- Notebook.
- Grafana.
- Công cụ tương đương.

Điều quan trọng: dashboard phải đọc từ `data/logs.jsonl`, không lấy `/metrics` làm nguồn chính.

### Giải thích

Validator chỉ kiểm tra contract trong YAML. Ảnh dashboard runtime mới là bằng chứng rằng bạn thật sự dùng dữ liệu log để tính latency, traffic, error, cost, token và quality.

### Đầu ra cần có

- `python scripts/validate_dashboard.py` pass `6/6 panel`.
- Ảnh dashboard baseline trong `submission/evidence/`, nên đặt tên:
  - `11-dashboard-validator.png`
  - `12-dashboard-baseline.png`
- Ảnh dashboard phải thấy rõ:
  - tên panel;
  - time range 60 phút;
  - đơn vị;
  - threshold/SLO line hoặc threshold value.
- `config/alert_rules.yaml` không còn TODO nếu vai trò 3 được giao phần alert.
- `docs/alerts.md` có runbook ngắn cho từng alert nếu nhóm yêu cầu.

### Cần từ thành viên khác

- Logging & PII:
  - Bàn giao log đúng field dashboard.
  - Xác nhận `validate_logs.py >= 80/100`.
- Tracing & Prompt Version:
  - Bàn giao trace IDs và prompt metadata để nếu dashboard có liên kết sang investigation thì dùng được.
- Incident/Report & Demo:
  - Thống nhất tên file evidence và nội dung cần đưa vào report.

---

## Checkpoint 3 - Challenge chính thức

### Mục tiêu của bạn

Dùng dashboard để phát hiện triệu chứng incident, cung cấp metric evidence cho chuỗi điều tra Metrics -> Traces -> Logs.

### Việc bạn cần làm

1. Chỉ chạy challenge khi Lab Coach release `config/challenge.json`.

Kiểm tra file:

```powershell
Test-Path config\challenge.json
```

Nếu trả `False`, không tự tạo file này.

2. Khi đã có file challenge, chạy:

```powershell
python scripts/inject_incident.py
python scripts/load_test.py --challenge --concurrency 5
```

3. Quan sát dashboard và ghi lại triệu chứng:

- P95 latency có tăng không?
- Error rate có vượt 2% không?
- Cost có tăng bất thường không?
- Token input/output có tăng bất thường không?
- Quality average có giảm dưới 0.75 không?

4. Chụp ảnh dashboard incident:

```text
submission/evidence/13-dashboard-incident.png
submission/evidence/14-challenge-metrics.png
```

5. Ghi lại số liệu cụ thể cho Incident/Report:

```text
Metric evidence:
- Time window:
- Panel:
- Baseline value:
- Incident value:
- Threshold:
- Status: violated / not violated
```

### Giải thích

Vai trò của bạn trong challenge là bắt đầu từ metrics/dashboard. Không nên đọc code và đoán incident trước. Bài lab chấm khả năng phát hiện triệu chứng bằng observability evidence.

### Đầu ra cần có

- Ảnh dashboard lúc incident.
- Bảng số liệu baseline vs incident.
- Kết luận SLO nào bị vi phạm, nếu có.
- Input cho người Incident/Report để tiếp tục mở trace và tìm log theo correlation ID.

### Cần từ thành viên khác

- Tracing & Prompt Version:
  - Cung cấp trace chậm hoặc trace lỗi từ Langfuse.
  - Cung cấp trace ID, prompt label/version liên quan.
- Logging & PII:
  - Hỗ trợ tìm log theo `correlation_id`.
  - Xác nhận log không lộ PII.
- Incident/Report & Demo:
  - Dùng metric evidence của bạn để viết symptom và metric evidence trong report.

---

## Hoàn tất - Report và demo

### Mục tiêu của bạn

Bàn giao trọn gói phần dashboard/SLO/alert để đưa vào `submission/REPORT.md`.

### Việc bạn cần làm

1. Tổng hợp evidence dashboard:

```text
submission/evidence/11-dashboard-validator.png
submission/evidence/12-dashboard-baseline.png
submission/evidence/13-dashboard-incident.png
submission/evidence/14-challenge-metrics.png
```

2. Ghi nội dung ngắn cho report:

```text
Dashboard source: data/logs.jsonl
Time range: 60 minutes
Refresh: 30 seconds
Panels: latency, traffic, errors, cost, tokens, quality
SLO thresholds:
- P95 latency <= 3000 ms
- Error rate <= 2%
- Daily/total cost <= 2.5 USD
- Average quality >= 0.75
Validator result: 6/6 panel
```

3. Nếu đã sửa alert/runbook, ghi:

```text
Alerts:
- High latency alert
- High error rate alert
- Quality degradation alert
Runbook: docs/alerts.md
```

4. Chạy kiểm tra cuối:

```powershell
python scripts/validate_dashboard.py
python -m pytest -q
git status --short
```

### Đầu ra cần có

- Phần Dashboard/SLO/Alert trong report được điền đầy đủ.
- Evidence ảnh có trong `submission/evidence/`.
- Validator dashboard pass.
- Không commit `.env`, secret key, `.venv/`.

### Cần từ thành viên khác

- Incident/Report & Demo:
  - Gắn link evidence dashboard vào report.
  - Đưa số liệu dashboard vào phần symptom và metric evidence.
- Logging & PII:
  - Xác nhận log source hợp lệ và không lộ PII.
- Tracing & Prompt Version:
  - Xác nhận trace evidence khớp với thời điểm dashboard incident.

---

## Checklist nhanh của vai trò 3

- [ ] Đã đọc `config/dashboard.yaml`.
- [ ] Đã đọc `docs/DASHBOARD_SETUP.md`.
- [ ] Đã xác nhận source là `data/logs.jsonl`.
- [ ] Đã chạy `python scripts/validate_dashboard.py`.
- [ ] Đã xác nhận dashboard có 6 panel.
- [ ] Đã xác nhận threshold/SLO đúng contract.
- [ ] Đã xác nhận log có đủ field sau khi Logging & PII sửa xong.
- [ ] Đã tạo/chụp dashboard baseline.
- [ ] Đã tạo/chụp dashboard incident.
- [ ] Đã hoàn thiện alert rules nếu được phân công.
- [ ] Đã cung cấp metric evidence cho Incident/Report.
- [ ] Đã kiểm tra không commit secret.
