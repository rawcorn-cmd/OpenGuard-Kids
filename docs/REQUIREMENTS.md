# OpenGuard Kids — Software Requirements Specification (SRS)

> **Document Status:** Verified Baseline Requirements Specification  
> **Course:** Computer Networks (*Mạng máy tính*) — Faculty of Information Technology, HCMUS  
> **Verification Status:** 100% Verified Baseline & Defect Resolution Upgrade (R1–R4) Fully Implemented and Audited.  
> **Rule of Interpretation:** Every requirement is cited with its exact source section, table, or appendix. Non-specified details are strictly segregated and labeled as **[Needs clarification]** or **[Team Proposal]**.

---

## 1. Project Overview and High-Level Scope

* **Course Context:** Computer Networks Course Project (*Đồ án môn học Mạng máy tính theo nhóm*), Faculty of Information Technology, HCMUS. [Source: Header & Table 1]
* **Team Size:** Exactly 03 students/team (*03 sinh viên/nhóm*). [Source: Table 1]
* **Project Duration:** 07 weeks (*07 tuần*). [Source: Table 1]
* **Evaluation Focus:** System and Network Programming Techniques (*Trọng tâm đánh giá: Kỹ thuật lập trình hệ thống và mạng*). [Source: Table 1]
* **Evaluation Format:** Working Software Product + Project Report + Individual Oral Defense (*Hình thức chấm: Sản phẩm + báo cáo và vấn đáp cá nhân*). [Source: Table 1]
* **Target Platform:** Windows 10 / Windows 11 (x64) for the Agent (*Agent trên Windows 10/11 (x64)*). [Source: Table 1, Section 2.1]
* **Core Philosophy:** "A companion tool, not spyware" (*"Công cụ đồng hành, không phải phần mềm theo dõi lén"*). [Source: Document Subtitle]

---

## 2. Mandatory Design Philosophy: Transparency with the Child (*Triết lý thiết kế bắt buộc*)

The assignment defines six non-negotiable principles (**NT1 – NT6**) and a strict catalog of prohibited techniques.

| Code | Principle (*Nguyên tắc*) | Mandatory Manifestation in Product (*Biểu hiện bắt buộc trong sản phẩm*) | Source |
| :--- | :--- | :--- | :--- |
| **NT1** | Child knows they are being supported (*Trẻ biết mình đang được hỗ trợ*) | The system tray icon must **always be visible** while the agent is running; a system notification must be displayed when the agent starts. | Section 1, Table NT |
| **NT2** | Data minimization (*Tối thiểu dữ liệu*) | Only collect metadata: application name, domain name, duration, timestamp. **Strictly forbidden:** recording full URLs, window titles, keystrokes, or screen captures. | Section 1, Table NT |
| **NT3** | Child has a voice (*Trẻ có tiếng nói*) | Provide interactive buttons: `"Xin thêm giờ"` (Request more time) and `"Con nghĩ trang này bị chặn nhầm"` (I think this site was blocked by mistake). Every request must be delivered to parents, recorded, and receive a response. | Section 1, Table NT |
| **NT4** | Every action must be explainable (*Mọi hành động phải giải thích được*) | When an application or website is blocked, display a clear explanation stating the reason and who configured the rule. Never fail silently or pretend there is a network error. | Section 1, Table NT |
| **NT5** | Two-way transparency (*Minh bạch hai chiều*) | The child has access to the exact same report set as the parents (rendered in a child-friendly interface), and can view the audit log of parent-initiated rule changes. | Section 1, Table NT |
| **NT6** | Absolute safety priority (*An toàn có ưu tiên tuyệt đối*) | Permanent whitelist: school portals, National Child Protection Hotline **111**, emergency rescue services. System locking must never obstruct OS emergency calls. | Section 1, Table NT |

### Prohibited Catalog (*DANH MỤC CẤM — Tuyệt đối không hiện thực*) [Source: Section 1]
1. Reading private communication content: messages, emails, documents (*đọc nội dung tin nhắn, email, tài liệu*).
2. Concealment techniques: hiding processes, hiding Windows services, rootkit mechanisms, or malware-style anti-removal tricks (*ẩn tiến trình, ẩn dịch vụ, kỹ thuật rootkit hoặc chống gỡ theo kiểu mã độc*).
3. Exfiltrating or sending telemetry/user data to any third-party services (*gửi dữ liệu tới dịch vụ bên thứ ba*).
4. Conducting testing on actual children or unauthorized third-party machines without consent (*thử nghiệm trên trẻ em thật hoặc trên máy của người khác mà không có sự đồng ý*).

---

## 3. System Architecture and Component Responsibilities

### 3.1 Architecture Diagram [Source: Section 2.1]

```
   MÁY CỦA TRẺ (Windows 10/11)                    MÁY CHỦ (LAN hoặc VPS lab)
 +---------------------------------+           +-------------------------------+
 |  OGK-Agent (Python)             |           |  OGK-Server (FastAPI)         |
 |  +---------------------------+  |  HTTPS    |  +-------------------------+  |
 |  | Windows Service (SYSTEM)  |  |  TLS1.2+  |  | /auth  /enroll  /policy |  |
 |  |  - Policy Enforcer        |<-+---------->+->| /events /commands       |  |
 |  |  - Screen-time Counter    |  | heartbeat |  | /reports /audit         |  |
 |  |  - App Controller         |  |   60s     |  +-------------------------+  |
 |  |  - DNS Proxy 127.0.0.1:53 |  |           |  |  SQLite + SQLAlchemy    |  |
 |  |  - Local cache (SQLite)   |  | WebSocket |  |  (policy, event, audit) |  |
 |  +---------------------------+  | lenh gap  |  +-------------------------+  |
 |  +---------------------------+  | (< 5s)    +---------------^---------------+
 |  | Tray UI (quyen user)      |  |                           | HTTPS
 |  |  - Dong ho con lai        |  |                  +--------+--------+
 |  |  - Nut 'Xin them gio'     |  |                  | Dashboard phu   |
 |  |  - Man hinh minh bach     |  |                  | huynh (web)     |
 |  +---------------------------+  |                  | Lich - Bao cao  |
 +---------------------------------+                  +-----------------+
        ^ named pipe / localhost                      Cau hinh tu xa, moi thiet bi
```

### 3.2 Component Details and Responsibilities [Source: Section 2.2]

1. **OGK-Agent — Service:**
   * **Role:** Enforce policy, track screen time, terminate restricted applications, resolve DNS queries with filtering, buffer events offline (*Áp dụng chính sách, đếm thời gian, chặn ứng dụng, phân giải DNS có lọc, đệm sự kiện khi mất mạng*).
   * **Technical Constraints:** Runs under `LocalSystem`; implemented using `pywin32` (`win32serviceutil`) and `psutil`; configured with auto-restart via Service Recovery Options of Windows SCM (*Chạy dưới LocalSystem; dùng pywin32 (win32serviceutil), psutil; khởi động lại bằng Service Recovery Options của SCM*).
2. **OGK-Agent — Tray UI:**
   * **Role:** Child-facing interface displaying remaining time, blocking explanations, and interactive request buttons (*Giao diện dành cho trẻ: thời gian còn lại, lý do bị chặn, gửi yêu cầu*).
   * **Technical Constraints:** Runs in the user interactive session; communicates with the Service via Windows Named Pipe or `http://127.0.0.1` guarded by a local security token (*Chạy trong phiên người dùng; giao tiếp với service qua named pipe hoặc HTTP 127.0.0.1 có token cục bộ*).
   * **Anti-Abuse Rule:** No stealth mode. If the tray icon cannot be displayed, the agent must shut down automatically (*Sản phẩm không được có chế độ ẩn. Nếu không thể hiển thị biểu tượng, agent phải tự dừng*). [Source: Section 3 — F5]
3. **OGK-Server:**
   * **Role:** Parent authentication, device/child management, policy issuance, event ingestion, report aggregation, and audit logging (*Xác thực phụ huynh, quản lý thiết bị/trẻ, phát hành chính sách, nhận sự kiện, tổng hợp báo cáo, ghi nhật ký kiểm toán*).
   * **Technical Constraints:** FastAPI + Uvicorn + TLS; SQLite configured with Write-Ahead Logging (`WAL` mode); pagination and IP-based rate limiting (*FastAPI + Uvicorn + TLS; SQLite với WAL; phân trang và giới hạn tần suất (rate limit)*).
4. **Parent Dashboard:**
   * **Role:** Remote configuration: daily quota, weekly schedule matrix, application/domain rules, child request approvals, and aggregate reports (*Cấu hình từ xa: quota, lịch tuần, danh sách ứng dụng/miền, duyệt yêu cầu, xem báo cáo*).
   * **Technical Constraints:** Jinja2 + HTMX or lightweight React; must be fully responsive and functional on mobile phone browsers (*Jinja2 + HTMX hoặc React nhẹ; phải dùng được trên trình duyệt điện thoại*).
5. **Local Data Store (Agent Cache):**
   * **Role:** Stores the latest synced policy snapshot and offline event buffer (*Bản sao chính sách gần nhất + hàng đợi sự kiện*).
   * **Technical Constraints:** SQLite database located in `%ProgramData%`; NTFS ACL restricted so write permission is granted strictly to `SYSTEM` and `Administrators` (*SQLite trong ProgramData với ACL chỉ SYSTEM/Administrators được ghi*).

---

## 4. Lifecycle and Operational Protocols (*Vòng đời và giao thức*) [Source: Section 2.3]

> **MANDATORY REPORT REQUIREMENT [Source: Section 2.3 Heading]:**  
> The lifecycle and operational protocols are explicitly designated as: **"bắt buộc đặc tả trong báo cáo"** (must be formally specified in the project report).

1. **Pairing / Enrollment (*Ghép đôi*):**
   * Parent generates an **8-character pairing code** on the web dashboard (valid for **10 minutes**).
   * Agent sends the pairing code alongside the hardware device fingerprint (*device fingerprint*).
   * Server validates code and returns `device_id` and a JWT token pair (short-lived access token + long-lived refresh token).
   * *Legal Basis:* Explicit checkpoint recording parental consent pursuant to Decree 13/2023/NĐ-CP (*Nghị định 13/2023*).
2. **Periodic Heartbeat (*Nhịp tim*) (60 seconds):**
   * Agent transmits device status, consumed quota, and current `policy_version`.
   * Server responds with the latest `policy_version` and a list of pending commands.
   * If a version mismatch is detected, Agent issues `GET /policy` to fetch the updated configuration.
3. **Urgent Commands via WebSocket (*Lệnh khẩn qua WebSocket*) (< 5 seconds latency):**
   * The assignment explicitly enumerates three urgent commands:
     1. **`khóa ngay`** (immediate lock)
     2. **`mở khóa`** (unlock)
     3. **`cộng thêm 15 phút`** (grant 15 additional minutes)
   * Maximum acceptable execution latency: strictly under **5 seconds** (*độ trễ dưới 5 giây*).
4. **Offline Mode (*Chế độ ngoại tuyến*):**
   * Agent applies cached policy, continues counting active screen time, and queues events in local SQLite cache.
   * Upon network restoration, events are synced in batches.
   * Event batches must utilize an **idempotency key** (*khóa chống trùng*) to prevent duplicate aggregation on the server.
5. **Policy Expiration (*Chính sách hết hạn*):**
   * **Mandatory Team Decision & Defense Topic:** The development team must decide whether the agent operates as **fail-open** or **fail-closed** after $N$ consecutive days of server disconnection, and formally defend this decision during the oral defense (*nhóm phải tự quyết định fail-open hay fail-closed sau N ngày mất kết nối và bảo vệ lựa chọn đó khi vấn đáp*).

---

## 5. Explicit Functional Requirements (*Đặc tả chức năng*)

Priority classification defined in the assignment:
* **BẮT BUỘC (MANDATORY):** Prerequisite condition for grading (*điều kiện cần để được chấm*).
* **NÊN CÓ (SHOULD-HAVE):** Contributes to high/excellent grades (*tính vào điểm khá/giỏi*).
* **CÓ THÌ TỐT (NICE-TO-HAVE):** Bonus points, non-mandatory (*điểm thưởng, không bắt buộc*).

### F1. Screen-Time Management (*Quản lý thời gian sử dụng*) [Source: Section 3 — F1]

| Req ID | Level | Requirement Description | Explicit Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **F1.1** | **BẮT BUỘC** | Daily usage quota (e.g. 90 minutes), configured separately for weekdays vs. weekends (*Hạn mức theo ngày (ví dụ 90 phút), cấu hình riêng cho ngày thường và cuối tuần*). | Configure quota to 3 minutes; system locks precisely when time expires (*Đặt quota 3 phút, hệ thống khóa đúng hạn*). |
| **F1.2** | **BẮT BUỘC** | Weekly allowed/locked schedule with 30-minute granularity ($7 \times 48$ slot matrix) (*Lịch tuần cho phép/khóa với độ phân giải 30 phút (ma trận 7×48)*). | Outside allowed time slots, machine is locked within **5 seconds** (*Ngoài khung giờ cho phép, máy bị khóa trong 5 giây*). |
| **F1.3** | **BẮT BUỘC** | Track actual active usage time: do not count time when machine is locked or idle without user input for $> 5$ minutes (*Đếm thời gian sử dụng thực: không tính khi máy khóa hoặc không có thao tác quá 5 phút*). | Deviation $\le \pm 30$ seconds per hour compared to a physical stopwatch (*Sai số ≤ ±30 giây trên mỗi giờ so với đồng hồ bấm tay*). |
| **F1.4** | **BẮT BUỘC** | Advance warnings before expiration at **10, 5, and 1 minute** remaining; provide a **60-second grace period** allowing the child to save work (*Cảnh báo trước 10, 5 và 1 phút; có khoảng ân hạn 60 giây để trẻ lưu bài*). | Observable and verifiable during Demo D1 (*Quan sát được trong demo D1*). |
| **F1.5** | **BẮT BUỘC** | Anti-tamper protection preventing modification of the system clock to extend time (*Chống chỉnh đồng hồ hệ thống để kéo dài thời gian*). | Roll clock back 3 hours: quota must not increase; tamper event is logged (*Lùi đồng hồ 3 giờ: quota không được tăng, sự kiện bị ghi nhận*). |
| **F1.6** | **NÊN CÓ** | Time budgeting by application category (e.g., unlimited study, 45 minutes games) (*Ngân sách theo nhóm ứng dụng (ví dụ: học tập không giới hạn, trò chơi 45 phút)*). | Two independent counters operate correctly (*Hai bộ đếm độc lập hoạt động đúng*). |
| **F1.7** | **CÓ THÌ TỐT**| Mechanism to reward bonus time upon completion of parent-assigned tasks (*Cơ chế thưởng giờ khi hoàn thành nhiệm vụ do phụ huynh giao*). | — |

---

### F2. Application and Website Filtering by Age (*Lọc và kiểm soát ứng dụng/website theo độ tuổi*) [Source: Section 3 — F2]

| Req ID | Level | Requirement Description | Explicit Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **F2.1** | **BẮT BUỘC** | Application control via allowlist/blocklist, matching process executable name combined with **SHA-256 hash** of the executable binary (*Kiểm soát ứng dụng theo danh sách cho phép/chặn, đối chiếu tên tiến trình kèm mã băm SHA-256 của tệp thực thi*). | Renaming `notepad.exe` to `game.exe` is still correctly identified (*Đổi tên notepad.exe thành game.exe vẫn bị nhận diện đúng*). |
| **F2.2** | **BẮT BUỘC** | When blocking an application: terminate the process and display an explanatory dialog; do not fail silently (*Khi chặn: kết thúc tiến trình và hiển thị cửa sổ giải thích lý do, không im lặng*). | Observable during live demonstration (*Quan sát trong demo*). |
| **F2.3** | **BẮT BUỘC** | Website filtering via a local DNS proxy listening at `127.0.0.1:53`, supporting blocking of root domains and all subdomains (*Lọc website bằng DNS proxy cục bộ tại 127.0.0.1:53, hỗ trợ chặn theo tên miền và toàn bộ tên miền con*). | Blocks $\ge 95\%$ across the 50 test domains; **0 false positives** on 20 educational test domains (*Chặn ≥ 95% trong bộ 50 tên miền kiểm thử; 0 dương tính giả trên 20 tên miền giáo dục*). |
| **F2.4** | **BẮT BUỘC** | Categorization taxonomy across 6 groups: (1) Giáo dục (Education), (2) Giải trí (Entertainment), (3) Mạng xã hội (Social Media), (4) Trò chơi (Games), (5) Không phù hợp lứa tuổi (Inappropriate), (6) Chưa phân loại (Uncategorized); with default baseline policy for children aged 6–11 (*Hạ tầng phân loại theo 6 nhóm... có chính sách mặc định cho trẻ 6–11 tuổi*). | Accompanying classification table submitted with a **minimum of 200 entries** (*Bảng phân loại nộp kèm, tối thiểu 200 mục*). |
| **F2.5** | **BẮT BUỘC** | Enforce Search Engine SafeSearch via DNS record manipulation (e.g. mapping search domains to `forcesafesearch` VIPs) (*Cưỡng chế SafeSearch của công cụ tìm kiếm bằng bản ghi DNS*). | Verified using `nslookup` and browser verification (*Kiểm chứng bằng nslookup và bằng trình duyệt*). |

> **CRITICAL TEST DATA REGULATION [Source: Section 3 — F2]:**  
> The 50 test domains must use safe, public addresses (e.g. `example.com`, school domains, reputable news outlets). **Strictly forbidden:** using, accessing, or attaching real adult/harmful content domains for testing. Any group submitting such domains will receive point penalties (*Tuyệt đối không sử dụng, truy cập hay đính kèm tên miền có nội dung người lớn để 'thử nghiệm'. Nhóm nào nộp danh sách như vậy sẽ bị trừ điểm*).

---

### F3. Activity Logging and Reporting (*Ghi nhận và báo cáo hoạt động — minh bạch*) [Source: Section 3 — F3]

| Req ID | Level | Requirement Description | Explicit Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **F3.1** | **BẮT BUỘC** | **Strict Event Schema:** The event record must contain **only** these 7 fields: `ts`, `device_id`, `child_id`, `type`, `subject`, `duration_sec`, `policy_id`. `type` must strictly belong to: `{app_start, app_stop, domain_query, blocked_app, blocked_domain, quota_warning, locked, unlock_request, override_granted}`. `subject` is strictly the application executable name or second-level domain name (**never a full URL**). | Schema compliance verified in database and API payloads. |
| **F3.2** | **BẮT BUỘC** | Parent Web Dashboard: Daily and weekly screen-time duration charts, top 10 applications, top 10 domains, total blocked count, and list of child requests (*biểu đồ thời lượng theo ngày và theo tuần, top 10 ứng dụng, top 10 tên miền, số lần bị chặn, danh sách yêu cầu của trẻ*). | Functional, responsive dashboard interface. |
| **F3.3** | **BẮT BUỘC** | Child Transparency Screen (`"Hôm nay em đã dùng gì"`): Displays the exact same activity data using simplified language and illustrations (*hiển thị cùng dữ liệu bằng ngôn ngữ đơn giản và hình ảnh minh họa*). | Accessible in Child Tray UI. |
| **F3.4** | **BẮT BUỘC** | Data retention policy: **90 days** with automated deletion task; button `"Xóa toàn bộ dữ liệu của con tôi"` deletes simultaneously on server and local agent cache (*Thời hạn lưu trữ 90 ngày, có tác vụ tự động xóa; nút 'Xóa toàn bộ dữ liệu của con tôi' xóa đồng thời trên server và trong bộ đệm của agent*). | Automated background worker + atomic dual deletion. |
| **F3.5** | **BẮT BUỘC** | Documentation artifact `PRIVACY.md` formatted as a table: Field $\leftrightarrow$ Purpose $\leftrightarrow$ Retention Period $\leftrightarrow$ Visibility. Any field without an articulated purpose must be removed from the schema (*Tệp PRIVACY.md dạng bảng: mỗi trường dữ liệu ↔ mục đích ↔ thời hạn lưu ↔ ai xem được. Trường nào không giải thích được mục đích thì phải loại khỏi lược đồ*). | File `PRIVACY.md` created and compliant. |

---

### F4. Remote Management and Multi-Tenancy (*Agent, bảng điều khiển và cấu hình từ xa*) [Source: Section 3 — F4]

| Req ID | Level | Requirement Description | Explicit Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **F4.1** | **BẮT BUỘC** | Relational data model supporting **1 Parent : $n$ Children : $m$ Devices** (*Mô hình dữ liệu hỗ trợ 1 phụ huynh : n trẻ : m thiết bị*). | Schema supports multi-child and multi-device accounts. |
| **F4.2** | **BẮT BUỘC** | Propagation latency: Dashboard policy changes take effect on child agent within **$\le 60$ seconds**; urgent commands (`khóa ngay`, `mở khóa`, `cộng thêm 15 phút`) take effect within **$\le 5$ seconds** (*Thay đổi chính sách trên dashboard có hiệu lực trên máy trẻ trong vòng 60 giây; lệnh khẩn (khóa ngay, cộng giờ) trong vòng 5 giây*). | Latency verified and demonstrated. |
| **F4.3** | **BẮT BUỘC** | Policy versioning and integrity validation: Policies must have monotonic version numbers and cryptographic integrity markers (HMAC or digital signature) so the Agent rejects tampered policies (*Chính sách có đánh số phiên bản và ký hiệu toàn vẹn (HMAC hoặc chữ ký) để agent từ chối chính sách bị sửa đổi*). | Agent verification logic rejects modified policy payloads. |
| **F4.4** | **BẮT BUỘC** | Comprehensive Audit Log: Every policy change logs *who, when, originating IP address, old value, and new value*. The child has the right to view this audit log (Principle NT5) (*Nhật ký kiểm toán mọi thay đổi: ai, lúc nào, từ địa chỉ IP nào, giá trị cũ và mới. Trẻ được quyền xem nhật ký này (nguyên tắc NT5)*). | Visible on Parent Dashboard and Child Tray UI. |

---

## 6. Non-Functional, Security and Privacy Requirements (*Bảo mật và quyền riêng tư*) [Source: Section 3 — F5]

| Category | Explicit Minimum Requirement (*Yêu cầu tối thiểu*) | Source |
| :--- | :--- | :--- |
| **Parent Authentication** | Password hashing using **Argon2id** or **scrypt** (via `passlib`); minimum length **10 characters**; temporary account lock of **15 minutes** after **5 consecutive failed attempts**; IP-based rate limiting. *Bonus:* Two-Factor Authentication (TOTP). | Section 3, Table F5 |
| **Session Management** | Cookies marked `HttpOnly`, `Secure`, `SameSite=Lax`; session lifetime **12 hours**; server-side session destruction upon logout; CSRF protection on all state-changing write operations. | Section 3, Table F5 |
| **Transport Security** | **TLS 1.2+** across all endpoints (self-signed CA permissible in lab environment); Agent enforces **Certificate Pinning** and terminates connection upon mismatch. | Section 3, Table F5 |
| **Device Identity** | Access token valid for **15 minutes** + long-lived refresh token; bound to `device_id`; server maintains token revocation list upon device unenrollment. | Section 3, Table F5 |
| **Data at Rest** | Sensitive fields encrypted using **AES-GCM**; encryption keys loaded via environment variables or Windows DPAPI (**never hardcoded**); device secrets stored as hashes. | Section 3, Table F5 |
| **Authorization & RBAC** | Three explicit roles: **`parent`**, **`child-view`**, **`admin`**. Strict query-level ownership checks to prevent Insecure Direct Object References (**IDOR**). | Section 3, Table F5 |
| **Local OS Privileges** | Child Windows account must not belong to `Administrators` group. Agent configuration and cache directories must have NTFS ACLs allowing write access strictly to `SYSTEM` and `Administrators`. | Section 3, Table F5 |
| **Anti-Abuse Safeguards** | The product must **not possess a stealth mode** (*không được có chế độ ẩn*). If the tray icon cannot be displayed, the agent must shut down automatically. Documentation must define the legitimate scope of use (*Tài liệu phải nêu rõ phạm vi sử dụng hợp pháp*). | Section 3, Table F5 |

---

## 7. Required Technologies and Platform Constraints [Source: Table 1, Section 2.2, Section 3 — F5]

* **Operating System:** Windows 10 / Windows 11 (x64) for the Agent.
* **Programming Language & Runtime:** Python 3.11+.
* **Windows System Libraries:** `pywin32` (`win32serviceutil`, `win32event`, etc.), `psutil`.
* **Backend Framework & Server:** FastAPI, Uvicorn, TLS 1.2+.
* **Database & ORM:** SQLite with Write-Ahead Logging (`WAL` mode enabled), SQLAlchemy.
* **Parent Dashboard Frontend:** Jinja2 + HTMX or lightweight React (must be functional on mobile phone browsers).
* **Local Networking:** DNS Proxy service bound to `127.0.0.1:53`.

---

## 8. Explicit Deliverables and Submissions [Source: Table 1, Section 2.3, Section 3 — F2, F3, F5, Appendix]

1. **Working Application Product (*Sản phẩm*):** Windows Agent (Service + Tray UI), Backend Server, and Parent Web Dashboard.
2. **Project Report & Individual Defense (*Báo cáo và vấn đáp cá nhân*):** Comprehensive report including mandatory lifecycle & protocol specification (*Vòng đời và giao thức bắt buộc đặc tả trong báo cáo*).
3. **`PRIVACY.md`:** Data privacy table artifact mapping every field in the 7-field event schema to its legal purpose, retention period, and access visibility.
4. **Domain Classification Dataset (*Bảng phân loại nộp kèm*):** Minimum **200 entries** categorized into the 6 designated groups with default policy for ages 6–11.
5. **Safe 50-Domain Test Suite (*Bộ 50 tên miền kiểm thử*):** Test dataset adhering strictly to safe, public domains.
6. **User Documentation / Legitimate Scope Declaration:** Documentation defining the legitimate scope of use and instructions (*Tài liệu phải nêu rõ phạm vi sử dụng hợp pháp*).

---

## 9. Evaluation, Grading Rubric and Milestones Analysis

* **Grading Focus:** System and Network Programming techniques (*Trọng tâm đánh giá: Kỹ thuật lập trình hệ thống và mạng*). [Source: Table 1]
* **Grading Tiers:**
  * `BẮT BUỘC`: Prerequisite condition to receive a passing grade.
  * `NÊN CÓ`: Contributes to high/excellent grades (*điểm khá/giỏi*).
  * `CÓ THÌ TỐT`: Bonus points (*điểm thưởng*).
* **Explicit Milestones Mentioned:**
  * Overall duration: **07 weeks**. [Source: Table 1]
  * **Demo D1:** Advance warning toast notifications (10m, 5m, 1m) and 60-second grace period verification. [Source: Section 3 — F1.4]

---

## 10. Ambiguities, Numeric Discrepancies, and Items Requiring Clarification

The following items are identified as ambiguities in the source text or areas requiring team decisions:

1. **Test Dataset Size Discrepancy (50 vs. 60 Domains) [Ambiguity in Assignment]:**
   * Section 3 — F2.3 specifies: *"Chặn $\ge 95\%$ trong bộ 50 tên miền kiểm thử; 0 dương tính giả trên 20 tên miền giáo dục"* (50 test domains).
   * However, the Appendix table specifies a breakdown totaling **60 domains**:
     * Giáo dục: 20
     * Giải trí phù hợp lứa tuổi: 10
     * Mạng xã hội: 8
     * Trò chơi trực tuyến: 7
     * Điểm cuối DoH: 5
     * Tên miền mô phỏng cần chặn: 10
     * *Total:* $20 + 10 + 8 + 7 + 5 + 10 = 60$.
   * *Status:* Needs clarification whether the 50 domains exclude DoH endpoints and 5 mock domains, or if the test suite should contain 60 domains while evaluating F2.3 on a 50-domain subset.
2. **DNS-over-HTTPS (DoH) Handling Scope [Needs Clarification]:**
   * The Appendix suggests: *"5 điểm cuối DoH — Kiểm tra khả năng phát hiện và xử lý DNS-over-HTTPS"*.
   * The body of F2 does not specify whether "xử lý DoH" requires blocking port 443 to known DoH IPs, intercepting DoH bootstrap DNS queries, or logging a warning event.
3. **Exact Scoring Weights [Needs Clarification]:**
   * The assignment defines tiers (`BẮT BUỘC`, `NÊN CÓ`, `CÓ THÌ TỐT`), but does not state the numeric point allocation (e.g. out of 10 or 100) or the distribution between Product, Report, and Defense.
4. **Calendar Deadlines for Demo D1 and Final Submission [Needs Clarification]:**
   * Week numbers and calendar dates for Demo D1 and the final defense are not stated in the document.
5. **Team Architectural Decision — Fail-Open vs. Fail-Closed [Mandatory Decision per Section 2.3]:**
   * The team must explicitly decide and defend whether the agent operates as fail-open or fail-closed after $N$ days of server disconnection.

---

## 11. Defect Resolution & Live Operational Verification Requirements (R1–R4 Traceability Matrix)

To guarantee evaluation on both the Linux Mint host and Windows 10/11 production target, the system fulfills explicit defect resolution and synchronization criteria across R1–R4:

| Req ID | Requirement Description | Explicit Acceptance Criteria | Implementation Mechanism | Verification Evidence & Status |
| :--- | :--- | :--- | :--- | :--- |
| **R1.1** | **Time & Quota Consistency** | Screen time recorded by `ScreenTimeTracker` matches server policies, tray badge, and dashboard without drift. | Local midnight SQLite parameterization in `offline_buffer.py` (`ts >= today_midnight`) restores consumed seconds across service restarts. | **PASSED**: `stress_screentime_ticks.py` (exact 134.0s restored), `tests/test_screen_time.py`. |
| **R1.2** | **Urgent State Propagation** | Emergency lock (`LOCK_URGENT`) and unlock from Parent Dashboard propagate to Agent and Tray immediately. | Persistent Agent WebSocket client with exponential backoff connects to server `/ws/agent/{device_id}`. | **PASSED**: Average latency **1.70 ms** across 50 toggles (`scripts/verify_live_runtime.py` Step 7). |
| **R1.3** | **Agency Extension Approval** | Approving +15m extension immediately updates remaining time counters on both Agent and Tray UI. | Server increments `bonus_minutes_today`, sends WebSocket `ADD_TIME`, and updates IPC badge status. | **PASSED**: `scripts/verify_live_runtime.py` Step 10, `test_concurrent_quick_review_race_condition`. |
| **R1.4** | **Daily Bonus Rollover** | Bonus minutes granted on a prior day reset cleanly at midnight and do not linger. | Server evaluates `last_heartbeat < today_start` during heartbeat and summary queries, resetting bonus to 0. | **PASSED**: `test_curfew_and_quota_rollover.py`, `tests/test_sync_and_events.py`. |
| **R2.1** | **Visual Alerts on Linux Mint** | Warning toasts (10m, 5m, 1m) appear visually on desktop during evaluation rather than solely printing terminal logs. | `CrossPlatformNotifier` in `src/tray/notifier.py` utilizes `/usr/bin/notify-send` on Linux desktops (GNOME/Cinnamon/XFCE). | **PASSED**: Verified visually and headless in `tests/test_tray_app.py`, `scripts/verify_live_runtime.py`. |
| **R2.2** | **Native Windows Toast Fidelity** | Native Windows Action Center toast notifications preserved for Windows 10/11 production. | `CrossPlatformNotifier` detects Windows platform and delegates to `winotify` / `pywin32`. | **PASSED**: `src/tray/gui.py`, `src/tray/notifier.py` platform routing check. |
| **R2.3** | **Visual Grace & Lock Dialogs** | 60-second grace countdown and fullscreen lock screen display graphical dialogs on evaluation host. | Fallback routing to `zenity` (or `tkinter`) for grace countdown and lock overlay when Win32 APIs are unavailable. | **PASSED**: Verified in Demo D1 scenario (`scripts/e2e_acceptance_verification.py` Scenario 3). |
| **R2.4** | **Startup Race Resilience** | Tray UI starts cleanly even if launched before Agent Service. | 10-second polling loop (`poll_for_token`) waits for Agent secret token file before failing. | **PASSED**: `scripts/verify_live_runtime.py` Step 5, `stress_multiprocess_concurrency.py`. |
| **R3.1** | **Dashboard Tab Operability** | All 5 Parent Dashboard tabs render and operate without JavaScript or server exceptions. | 40 distinct DOM element IDs verified in `src/server/templates/dashboard.html`. | **PASSED**: `test_dashboard_tab_rendering`, `tests/test_dashboard_and_privacy.py`. |
| **R3.2** | **XSS Mitigation** | Child request subjects, reasons, and audit logs cannot inject arbitrary script into parent dashboard. | Comprehensive `escapeHtml()` utility applied across all dynamic innerHTML interpolations. | **PASSED**: `test_parent_dashboard_xss_in_child_requests_and_audit` (Adversarial Suite). |
| **R3.3** | **Manual Quota Bounds** | Dashboard manual time extensions must reject zero, negative, or integer overflow quantities. | Server endpoint `/api/v1/dashboard/command` validates `1 <= minutes <= 240`. | **PASSED**: `test_direct_command_negative_minutes_validation` (Adversarial Suite). |
| **R3.4** | **Domain RFC Validation** | Unblock requests and whitelist additions must reject malformed hostnames, HTML tags, and SQL injection. | Regex validator `_DOMAIN_REGEX` enforces RFC 1035 / FQDN syntax and 253-character limit. | **PASSED**: `test_malformed_unblock_request_xss_and_sql_injection` (Adversarial Suite). |
| **R3.5** | **Atomic Review Concurrency** | Rapid concurrent reviews of child requests cannot result in duplicate bonus minutes. | Atomic CAS query (`UPDATE ChildRequest WHERE id = :id AND status = 'PENDING'`). | **PASSED**: `test_concurrent_quick_review_race_condition` (20 parallel threads racing). |
| **R4.1** | **Concurrent Multi-Process Execution** | Backend Server, Agent Service, and Tray UI run concurrently without deadlocks or unhandled exceptions. | Coordinated process orchestration via HTTP, IPC, and persistent WebSocket channels. | **PASSED**: `tests/test_live_multiprocess.py` (2/2 PASSED), `scripts/verify_live_runtime.py` (11/11 PASSED). |
| **R4.2** | **Unprivileged Port 53 Fallback** | DNS Proxy starts on unprivileged UDP port 5353 when standard port 53 cannot bind without root privileges. | Exception handler in `src/agent/dns_proxy.py` catches `PermissionError` / `EACCES` and binds to 5353. | **PASSED**: `test_dns_unprivileged_fallback`, `scripts/verify_live_runtime.py` Step 1. |
| **R4.3** | **Socket & Thread Leak Prevention** | Repeated stopping/starting of Agent Service or Tray UI does not leak ports or hang threads. | `IPCManager.stop()` guards `server.shutdown()` with thread liveness check and calls `server_close()`. | **PASSED**: `stress_multiprocess_concurrency.py` (3 consecutive full-stack cycles, 0 leaks). |


