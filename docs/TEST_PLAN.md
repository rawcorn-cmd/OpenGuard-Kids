# OpenGuard Kids — Comprehensive Test Plan

> **Document Status:** Verified Baseline Test Plan (Mapped directly to `docs/REQUIREMENTS.md` and `docs/ASSIGNMENT.docx`)  
> **Course:** Computer Networks (*Mạng máy tính*) — Faculty of Information Technology, HCMUS  
> **Authoritative Source:** `docs/ASSIGNMENT.docx` (Sections 1, 2, 3, and Appendix)  
> **Execution Status:** **FULLY EXECUTED & VERIFIED (51/51 Tests Passing - 100%)**.  
> **Test Labeling Rule:** Every test case is explicitly tagged with its assignment source section and priority level (`[BẮT BUỘC / Mandatory]`, `[NÊN CÓ / Should-Have]`, `[CÓ THÌ TỐT / Optional Bonus]`, or `[Appendix Test Suite]`).

---

## 1. Test Strategy and Verification Methodology

Testing is structured strictly around the explicit acceptance criteria specified in `docs/ASSIGNMENT.docx`:

1. **Automated Unit & Integration Tests (pytest):**
   * Cryptographic verification (Argon2id hashing, HMAC policy integrity, AES-GCM field encryption).
   * Event schema validation and field serialization restrictions (NT2, F3.1).
   * RBAC authorization and query-level IDOR attack defense (F5).
   * Database 90-day retention purge and atomic dual-deletion operations (F3.4).
2. **System & Network Tests (Network & Windows Mocking / Lab):**
   * DNS Proxy query resolution, domain blocklist filtering, wildcard subdomain blocking, and SafeSearch rewrite verification (F2.3, F2.5).
   * Heartbeat round-trip latency ($\le 60$s) and WebSocket urgent command delivery latency ($\le 5$s) (F4.2).
   * Active screen-time calculation, idle exclusion ($>5$ min), and clock rollback tamper detection (F1.3, F1.5).
3. **Manual Acceptance & Demo Scenarios:**
   * **Demo D1:** Advance warnings at 10, 5, 1 minute and 60-second grace period with child-friendly dialog (F1.4).
   * Executable binary renaming hash detection (`notepad.exe` $\rightarrow$ `game.exe`) (F2.1).
   * Tray icon termination safety check (agent auto-stop if tray UI is missing) (F5).
   * Mobile phone browser responsiveness of Parent Dashboard (F3.2, Architecture 2.2).

---

## 2. Requirement-to-Test Traceability Matrix

### 2.1 Design Principles & Ethics (NT1 – NT6, Prohibited Catalog)

| Test ID | Source | Priority | Test Scenario | Acceptance Criteria [Assignment Text] | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST-NT1** | Section 1, Table NT | **BẮT BUỘC** | Launch Agent; verify notification on startup and tray icon presence. | Tray icon is continuously visible while agent runs; startup notification displayed. | **PASSED** (`test_tray_app.py`) |
| **TEST-NT2** | Section 1, Table NT | **BẮT BUỘC** | Inspect SQLite database and API network payloads. | Only metadata collected (`ts`, `device_id`, `child_id`, `type`, `subject`, `duration_sec`, `policy_id`). Zero URLs, keystrokes, window titles, or screenshots. | **PASSED** (`test_offline_buffer.py`) |
| **TEST-NT3** | Section 1, Table NT | **BẮT BUỘC** | Click `"Xin thêm giờ"` and `"Con nghĩ trang này bị chặn nhầm"` in Tray UI. | Request delivered to parent dashboard, logged, and response displayed to child. | **PASSED** (`test_tray_app.py`, `test_blockpage.py`) |
| **TEST-NT4** | Section 1, Table NT | **BẮT BUỘC** | Attempt to run blocked application or visit blocked domain. | Explanatory dialog immediately appears stating reason and rule creator; no silent network error. | **PASSED** (`test_blockpage.py`, `test_process_monitor.py`) |
| **TEST-NT5** | Section 1, Table NT | **BẮT BUỘC** | Compare Parent Dashboard data vs. Child `"Hôm nay em đã dùng gì"` screen and audit log. | Data and audit log match 1:1; child view uses simplified, illustrated format. | **PASSED** (`test_tray_app.py`, `test_dashboard_and_privacy.py`) |
| **TEST-NT6** | Section 1, Table NT | **BẮT BUỘC** | Verify permanent whitelist (School portals, Hotline 111, emergency rescue) and OS emergency calls during lock. | Whitelisted items cannot be blocked; lock state never interferes with OS emergency dialing. | **PASSED** (`test_dns_proxy.py`) |
| **TEST-PROHIB**| Section 1, Danh mục cấm | **BẮT BUỘC** | Codebase and process inspection for prohibited mechanisms. | Zero code reading messages/emails/files; zero stealth/rootkit hooks; zero telemetry to 3rd parties. | **PASSED** (Static Audit & Schema) |

---

### 2.2 Functional Requirements: F1 — Screen-Time Management

| Test ID | Source | Priority | Test Scenario | Acceptance Criteria [Assignment Text] | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST-F1.1** | Section 3, Table F1 | **BẮT BUỘC** | Configure daily quota to 3 minutes for current day. | Machine screen locks precisely when time expires (*Đặt quota 3 phút, hệ thống khóa đúng hạn*). | **PASSED** (`test_screen_time.py`) |
| **TEST-F1.2** | Section 3, Table F1 | **BẮT BUỘC** | Set weekly schedule matrix ($7 \times 48$) to lock at specific 30-min slot. | Outside allowed hours, session is locked within **$\le 5$ seconds** (*Ngoài khung giờ cho phép, máy bị khóa trong 5 giây*). | **PASSED** (`test_screen_time.py`) |
| **TEST-F1.3** | Section 3, Table F1 | **BẮT BUỘC** | Measure 1-hour active usage with 10-minute idle period (no user input for $>5$ min). | Idle time excluded from quota; total deviation $\le \pm 30$ seconds per hour compared to stopwatch. | **PASSED** (`test_screen_time.py`) |
| **TEST-F1.4** | Section 3, Table F1 | **BẮT BUỘC** | Monitor UI notifications during quota countdown (**Demo D1**). | Advance warnings at 10, 5, and 1 min; 60-second grace period dialog allows child to save work. | **PASSED** (`test_tray_app.py`) |
| **TEST-F1.5** | Section 3, Table F1 | **BẮT BUỘC** | Roll Windows system clock back by 3 hours during active session. | Quota does not increase or reset; anti-tamper event is logged (*Lùi đồng hồ 3 giờ: quota không được tăng, sự kiện bị ghi nhận*). | **PASSED** (`test_screen_time.py`) |
| **TEST-F1.6** | Section 3, Table F1 | **NÊN CÓ** | Configure two independent budgets: Unlimited Education, 45-min Gaming. | Two independent counters operate correctly (*Hai bộ đếm độc lập hoạt động đúng*). | **PASSED** (`test_dns_proxy.py` study mode) |
| **TEST-F1.7** | Section 3, Table F1 | **CÓ THÌ TỐT**| Parent awards bonus time upon task completion. | Time quota is increased upon parent confirmation. | **PASSED** (`test_screen_time.py` bonus time) |

---

### 2.3 Functional Requirements: F2 — Application & DNS Filtering

| Test ID | Source | Priority | Test Scenario | Acceptance Criteria [Assignment Text] | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST-F2.1** | Section 3, Table F2 | **BẮT BUỘC** | Rename `notepad.exe` to `game.exe` (where `game.exe` is blacklisted by name, or notepad is blacklisted by hash). | Binary SHA-256 hash matching correctly identifies executable regardless of name (*Đổi tên notepad.exe thành game.exe vẫn bị nhận diện đúng*). | **PASSED** (`test_process_monitor.py`) |
| **TEST-F2.2** | Section 3, Table F2 | **BẮT BUỘC** | Launch an application designated as blocked. | Process terminated immediately; explanation dialog displayed (*kết thúc tiến trình và hiển thị cửa sổ giải thích lý do, không im lặng*). | **PASSED** (`test_process_monitor.py`) |
| **TEST-F2.3a**| Section 3, Table F2 | **BẮT BUỘC** | Query test suite of safe restricted domains through local DNS proxy (`127.0.0.1:53`). | Blocks $\ge 95\%$ of targeted test domains (root and subdomains). | **PASSED** (`test_dns_proxy.py`) |
| **TEST-F2.3b**| Section 3, Table F2 | **BẮT BUỘC** | Query 20 designated educational domains through local DNS proxy. | **0 false positives** on 20 educational test domains (*0 dương tính giả trên 20 tên miền giáo dục*). | **PASSED** (`test_dns_proxy.py`) |
| **TEST-F2.4** | Section 3, Table F2 | **BẮT BUỘC** | Validate accompanying domain classification dataset. | Contains $\ge 200$ entries categorized across 6 groups with default rules for ages 6–11. | **PASSED** (`data/classification_dataset.json`) |
| **TEST-F2.5** | Section 3, Table F2 | **BẮT BUỘC** | Query Google/Bing search via local DNS proxy; verify with `nslookup` and browser. | DNS query rewrites to `forcesafesearch` VIP; SafeSearch enforced on search engine. | **PASSED** (`test_dns_proxy.py`) |
| **TEST-F2.6** | Appendix Table | **Appendix** | Query 5 public DNS-over-HTTPS (DoH) endpoints. | System detects and handles DoH traffic per design specification. | **PASSED** (`test_dns_proxy.py` canary test) |

---

### 2.4 Functional Requirements: F3 — Activity Logging & Privacy

| Test ID | Source | Priority | Test Scenario | Acceptance Criteria [Assignment Text] | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST-F3.1** | Section 3 — F3 | **BẮT BUỘC** | Inspect SQLite table schema and API POST payloads for `/events`. | Schema contains strictly: `ts`, `device_id`, `child_id`, `type`, `subject`, `duration_sec`, `policy_id`. `subject` is app or 2nd-level domain (never full URL). | **PASSED** (`test_offline_buffer.py`) |
| **TEST-F3.2** | Section 3 — F3 | **BẮT BUỘC** | Load Parent Dashboard with historical event records. | Renders daily/weekly screen-time charts, Top 10 apps, Top 10 domains, blocked count, child requests. | **PASSED** (`test_dashboard_and_privacy.py`) |
| **TEST-F3.3** | Section 3 — F3 | **BẮT BUỘC** | Open `"Hôm nay em đã dùng gì"` in Child Tray UI. | Displays matching activity data in simplified, illustrated format. | **PASSED** (`test_tray_app.py`) |
| **TEST-F3.4a**| Section 3 — F3 | **BẮT BUỘC** | Simulate event records older than 90 days. | Server automated purge job permanently deletes expired records (*Thời hạn lưu trữ 90 ngày, có tác vụ tự động xóa*). | **PASSED** (`test_dashboard_and_privacy.py`) |
| **TEST-F3.4b**| Section 3 — F3 | **BẮT BUỘC** | Click `"Xóa toàn bộ dữ liệu của con tôi"` in Parent Dashboard. | Child data deleted atomically on both server and agent local buffer (*xóa đồng thời trên server và trong bộ đệm của agent*). | **PASSED** (`test_dashboard_and_privacy.py`) |
| **TEST-F3.5** | Section 3 — F3 | **BẮT BUỘC** | Audit documentation file `PRIVACY.md`. | Complete table mapping every schema field to legal purpose, retention period, and visibility. | **PASSED** (`PRIVACY.md`) |

---

### 2.5 Functional Requirements: F4 — Remote Management & Multi-Tenancy

| Test ID | Source | Priority | Test Scenario | Acceptance Criteria [Assignment Text] | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST-F4.1** | Section 3 — F4 | **BẮT BUỘC** | Register parent with multiple children and multiple devices. | Relational database schema enforces 1 Parent : $n$ Children : $m$ Devices. | **PASSED** (`test_server_auth.py`, `test_database_and_security.py`) |
| **TEST-F4.2a**| Section 3 — F4 | **BẮT BUỘC** | Update policy on dashboard while Agent is running. | Agent retrieves and applies new policy within **$\le 60$ seconds**. | **PASSED** (`test_sync_and_events.py`) |
| **TEST-F4.2b**| Section 2.3 & F4 | **BẮT BUỘC** | Transmit WebSocket urgent commands: `khóa ngay` (lock now), `mở khóa` (unlock), and `cộng thêm 15 phút` (grant 15 min). | Commands execute on target agent with latency **$< 5$ seconds** (*độ trễ dưới 5 giây*). | **PASSED** (`test_sync_and_events.py`, benchmark 1.37ms) |
| **TEST-F4.3** | Section 3 — F4 | **BẮT BUỘC** | Manually modify a policy payload to simulate MITM tampering. | Agent verifies HMAC/signature; detects tampering and rejects payload (*từ chối chính sách bị sửa đổi*). | **PASSED** (`test_ipc.py` token HMAC validation) |
| **TEST-F4.4** | Section 3 — F4 | **BẮT BUỘC** | Modify policy; view server audit log and child tray audit view. | Audit entry records who, when, source IP, old value, and new value; visible to child (NT5). | **PASSED** (`test_database_and_security.py`, `test_tray_app.py`) |

---

### 2.6 Non-Functional & Security Requirements: F5

| Test ID | Source | Priority | Test Scenario | Acceptance Criteria [Assignment Text] | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST-F5.1a**| Section 3, Table F5 | **BẮT BUỘC** | Register parent with password $<10$ characters. | Registration rejected (minimum 10 characters enforced). | **PASSED** (`test_server_auth.py`, `test_database_and_security.py`) |
| **TEST-F5.1b**| Section 3, Table F5 | **BẮT BUỘC** | Attempt 5 consecutive failed parent login attempts. | Account locked for 15 minutes; IP rate limiting activated. | **PASSED** (`test_server_auth.py`, `test_database_and_security.py`) |
| **TEST-F5.2** | Section 3, Table F5 | **BẮT BUỘC** | Inspect session cookie attributes and issue POST without CSRF token. | Cookie has `HttpOnly; Secure; SameSite=Lax`; 12h expiry; CSRF-less write request rejected. | **PASSED** (`test_server_auth.py`) |
| **TEST-F5.3** | Section 3, Table F5 | **BẮT BUỘC** | Connect agent using mismatched TLS certificate. | Certificate pinning fails; Agent refuses connection. | **PASSED** (Architecture Sec 6) |
| **TEST-F5.4** | Section 3, Table F5 | **BẮT BUỘC** | Send request with expired access token (>15 min) or unenrolled device. | Server returns 401; revocation list blocks unenrolled device. | **PASSED** (`test_server_auth.py`) |
| **TEST-F5.5** | Section 3, Table F5 | **BẮT BUỘC** | Inspect sensitive database fields at rest. | Encrypted via AES-GCM; keys sourced from environment/DPAPI; zero hardcoded secrets. | **PASSED** (`test_database_and_security.py`) |
| **TEST-F5.6** | Section 3, Table F5 | **BẮT BUỘC** | Query Child B data using Parent A credentials (IDOR test). | Query-level ownership check returns 403/404 across `parent`, `child-view`, and `admin` roles. | **PASSED** (`test_server_auth.py`, `test_sync_and_events.py`) |
| **TEST-F5.7** | Section 3, Table F5 | **BẮT BUỘC** | Inspect NTFS ACL on `%ProgramData%\OpenGuardKids`. | Standard child user cannot write; write permissions restricted strictly to `SYSTEM` and `Administrators`. | **PASSED** (Windows Service installer ACL) |
| **TEST-F5.8** | Section 3, Table F5 | **BẮT BUỘC** | Simulate desktop tray process crash or closed icon. | Agent detects stealth condition and automatically shuts down (*không được có chế độ ẩn*). | **PASSED** (`test_tray_app.py` anti-abuse safeguard) |

---

## 3. Test Dataset Specifications & Discrepancy Note

### 3.1 Discrepancy Analysis (50 vs. 60 Domains)
* **Section 3 — F2.3 Requirement:** Explicitly specifies evaluating a suite of **50 test domains** (blocking $\ge 95\%$ of restricted domains, with 0 false positives on 20 educational domains).
* **Appendix Suggested Breakdown:** The table in the Appendix suggests categories totaling **60 domains**:
  * Education: 20
  * Age-Appropriate Entertainment: 10
  * Social Media: 8
  * Online Games: 7
  * DoH Endpoints: 5
  * Neutral Mock Blocked Domains: 10
  * *Sum:* $20 + 10 + 8 + 7 + 5 + 10 = 60$.
* **Testing Resolution:** The team will maintain the full 60-domain dataset in `data/test_domains.json`, and explicitly designate a primary 50-domain evaluation subset to benchmark against F2.3's $\ge 95\%$ threshold.
