# OpenGuard Kids — Revised Team Implementation Plan (6-Week Schedule)

> **Course:** Computer Networks (*Mạng máy tính*) — Faculty of Information Technology, HCMUS  
> **STATUS / DISCLAIMER:**  
> **THIS IS A PROPOSAL BY THE DEVELOPMENT TEAM / TECH LEAD.**  
> It is **NOT** an official assignment requirement. The original assignment specifies a **07-week duration** (`docs/ASSIGNMENT.docx`, Table 1).  
> **Project Real-World Constraint:** The team has an actual development timeline of **06 weeks**. This revised plan compresses execution into 6 weeks, prioritizes **BẮT BUỘC (MANDATORY)** requirements, schedules testing early, establishes a strict Code Freeze in Week 6, and isolates technical risks without dropping any mandatory requirements or changing numerical thresholds.

---

## 1. Team Organization and Component Ownership

Work is structured across three student roles with explicit development ownership and cross-component integration responsibilities:

```
+---------------------------------------------------------------------------------------+
|                                TEAM ROLES & OWNERSHIP                                 |
+-----------------------------+----------------------------+----------------------------+
| Student A: System Engineer  | Student B: Network & Sec   | Student C: Backend & Web   |
+-----------------------------+----------------------------+----------------------------+
| Primary Modules:            | Primary Modules:           | Primary Modules:           |
| - Windows Service (SYSTEM)  | - DNS Proxy 127.0.0.1:53   | - FastAPI Server & SQLite  |
| - Screen-Time Counter & Idle| - SafeSearch Rewrites      | - Argon2id Auth & Sessions |
| - Process Monitor & SHA-256 | - DNS Adapter Safe Restore | - Multi-tenant API (1:n:m) |
| - Tray UI (User Session)    | - TLS Pinning & Cryptography- WebSocket & Heartbeat API  |
| - Service-to-Tray IPC       | - 50/60 Domain Datasets    | - Parent Dashboard (Web)   |
| - Clock Tamper Defense      | - 200+ Classification Table| - Audit Log & Data Purge   |
| Integration Duty:           | Integration Duty:          | Integration Duty:          |
| Host IPC server & Tray UI   | Packet pipeline to SQLite  | Endpoint schemas & events  |
+-----------------------------+----------------------------+----------------------------+
```

---

## 2. Component Dependency Map

```
  [Architecture & DB Schema (docs/ARCHITECTURE.md)]
          |                      |
          v                      v
  [FastAPI + SQLite DB]    [Local SQLite Cache (ProgramData)]
          |                      |
          +----------------------+
          |
    +-----+--------------------------------+
    |                                      |
    v                                      v
[Backend Auth & Enrollment]      [Windows Service Skeleton]
(Argon2id, Device Tokens)       (pywin32 SCM, LocalSystem)
    |                                      |
    v                                      v
[Policy & Event APIs]            [Service-to-Tray IPC Channel]
(HMAC-SHA256, 7-field schema)    (Named Pipe / Localhost HTTP)
    |                                      |
    +------------------+-------------------+
                       |
        +--------------+---------------+
        |                              |
        v                              v
[DNS Proxy 127.0.0.1:53]      [Screen-Time & Process Monitor]
- Wildcard Blocklist          - Idle Detection (>5 min)
- SafeSearch Rewriting        - Clock Tamper Detection
- Safe Adapter Restore        - SHA-256 Hash Matching
        |                              |
        +--------------+---------------+
                       |
                       v
         [Desktop Tray UI (User Session)]
         - Advance Warnings (10m, 5m, 1m)
         - 60s Grace Period Dialog (Demo D1)
         - Child Agency: 'Xin thêm giờ'
                       |
                       v
       [Real-Time Sync & Urgent Commands]
       - 60s Heartbeat
       - <5s WebSocket Urgent Dispatch
                       |
                       v
         [Parent Dashboard & Privacy]
         - Responsive Web UI (HTMX/Jinja2)
         - 90-day Purge & Atomic Dual-Delete
         - 50-Domain Test & 200+ Classification
                       |
                       v
          [WEEK 6: CODE FREEZE]
          - Verification against TEST_PLAN.md
          - Oral Defense Rehearsal & Final Report
```

---

## 3. Detailed Week-by-Week Schedule (Weeks 1 – 6)

### Week 1: Architecture, Core Foundations & High-Risk Spikes
* **Focus:** Resolve critical technical unknowns (Session 0 isolation, DNS binding safety, backend models).
* **Student A (System):**
  * Research and prototype Windows Service skeleton using `pywin32` (`win32serviceutil`).
  * Spike IPC mechanism across Session 0 (Service) and Session 1 (User Tray): evaluate Windows Named Pipe with security descriptors vs. local HTTP `127.0.0.1` with a secret local token file.
  * Implement system idle detection spike using `GetLastInputInfo` and session lock listener (`WTSRegisterSessionNotification`).
* **Student B (Network & Security):**
  * Prototype DNS Proxy UDP server on `127.0.0.1:53` (using `dnslib` or raw sockets).
  * Build and test safe Windows Network Adapter DNS configuration script using `netsh` / PowerShell, including a standalone emergency fallback script (`restore_dns.bat`) that restores DHCP DNS upon abnormal termination.
  * Implement DNS query parsing and wildcard subdomain matching algorithm.
* **Student C (Backend & Web):**
  * Initialize FastAPI server structure with SQLite in `WAL` mode.
  * Implement SQLAlchemy relational models: `Parent`, `Child`, `Device`, `Policy`, `Event`, `AuditLog`.
  * Implement password hashing utility with **Argon2id** (minimum 10 characters, lockout tracker).
* **Weekly Integration Milestone (End of Week 1):**
  * Authoritative `docs/ARCHITECTURE.md` completed and signed off.
  * Repository scaffolded (`README.md`, `.gitignore`, `requirements.txt`).
  * Standalone DNS restore script verified to prevent bricked network configurations.

---

### Week 2: Local Engines, Authentication & Policy Foundations
* **Focus:** Build isolated core enforcement engines and backend security foundation.
* **Student A (System):**
  * Implement Windows Service lifecycle with SCM auto-restart recovery options.
  * Build active screen-time tracking loop: exclude screen-locked state and user idle periods ($>5$ min); benchmark accuracy against $\le \pm 30$s/hour requirement.
  * Implement system clock rollback anti-tamper detection (detect backward time jumps $>60$s, prevent quota extension, log tamper event).
* **Student B (Network & Security):**
  * Integrate DNS blocklist/allowlist engine with local SQLite cache.
  * Implement SafeSearch DNS rewriting for Google and Bing (`forcesafesearch`).
  * Implement self-signed CA generation and TLS 1.2+ configuration; implement Agent certificate pinning client.
* **Student C (Backend & Web):**
  * Implement Parent Authentication endpoints (`/auth/register`, `/auth/login`, `/auth/logout`) with `HttpOnly; Secure; SameSite=Lax` cookies, 12h expiry, and CSRF protection.
  * Implement Device Enrollment API: generate 8-character pairing code (10-min TTL); exchange device fingerprint for `device_id` and token pair (15-min access token + refresh token).
  * Implement query-level ownership checks on all endpoints to prevent IDOR.
* **Weekly Integration Milestone (End of Week 2):**
  * Agent enrolls with Server using pairing code over TLS with pinned certificate.
  * DNS Proxy runs locally, successfully rewriting Google search to SafeSearch.

---

### Week 3: Process Enforcement, Sync Protocols & Event Ingestion
* **Focus:** Combine process monitoring with network synchronization.
* **Student A (System):**
  * Implement process scanner using `psutil`: inspect new processes, match executable name and compute SHA-256 binary hash.
  * Implement process termination for blacklisted applications and emit `blocked_app` events.
  * Verify acceptance criterion: renaming `notepad.exe` $\rightarrow$ `game.exe` is accurately detected via SHA-256 hash.
* **Student B (Network & Security):**
  * Curate and validate the safe 50/60-domain test suite (`data/test_domains.json`) per Appendix categories.
  * Begin compiling the mandatory $\ge 200$ domain classification table (`data/classification_dataset.json`).
  * Implement local DNS proxy event logger emitting `domain_query` and `blocked_domain` events according to the strict 7-field schema.
* **Student C (Backend & Web):**
  * Implement Policy Distribution API (`GET /policy` with monotonic versioning and HMAC-SHA256 integrity signature).
  * Implement 60-second Heartbeat API (`POST /heartbeat`) returning latest version and pending commands.
  * Implement WebSocket server endpoint for urgent commands (`khóa ngay`, `mở khóa`, `cộng thêm 15 phút`) with target latency $<5$s.
  * Implement Event Ingestion API (`POST /events`) with idempotency key deduplication.
* **Weekly Integration Milestone (End of Week 3):**
  * Agent synchronizes policy every 60s; server pushes WebSocket lock command executing on the agent within 5 seconds.
  * Blacklisted application is terminated by hash and event is buffered locally and synced to server.

---

### Week 4: Desktop Tray UI & Demo D1 Acceptance
* **Focus:** Build child-facing interactive interface and achieve Demo D1 readiness.
* **Student A (System):**
  * Build Desktop Tray UI running in the interactive user session.
  * Establish stable IPC connection to the Windows Service (Session 0).
  * Implement persistent notification icon and startup notification (NT1).
  * Implement anti-abuse auto-termination: if the tray icon fails to initialize or is terminated, the Agent service automatically halts (F5).
* **Student B (Network & Security):**
  * Execute DNS Proxy benchmarks against the 50-domain test suite; verify $\ge 95\%$ blocking and 0 false positives on 20 educational domains.
  * Finalize the $\ge 200$ domain classification dataset across all 6 required categories.
  * Conduct DoH endpoint detection testing using the 5 DoH endpoints from the Appendix.
* **Student C (Backend & Web):**
  * Implement Child Request APIs (`/requests/add-time`, `/requests/report-error`) to store requests in database.
  * Implement Parent Request Inbox API and notification push.
  * Implement advance warning notification triggers on Agent: 10 min, 5 min, 1 min, and 60-second grace period dialog before screen lock.
* **Weekly Integration Milestone (End of Week 4) — DEMO D1 READINESS:**
  * **Demo D1 Acceptance Verification:** Set quota to 3 minutes, observe warnings at 10m/5m/1m, trigger 60s grace period dialog, verify screen lock upon expiration.
  * Non-silent blocking dialog displays rule name and creator when apps/domains are blocked (NT4).

---

### Week 5: Parent Dashboard, Transparency Screens & Privacy Operations
* **Focus:** Build web dashboard, child transparency views, and data lifecycle management.
* **Student A (System):**
  * Implement Child Transparency Screen (`"Hôm nay em đã dùng gì"`) inside the Tray UI displaying usage duration and top apps/domains using child-friendly visuals (NT5, F3.3).
  * Implement Child Audit Log Viewer in Tray UI displaying history of rule modifications.
  * Implement Agent local cache purge handler responding to server dual-delete command.
* **Student B (Network & Security):**
  * Complete `data/classification_dataset.json` ($\ge 200$ items) and verify default rules for ages 6–11.
  * Draft `docs/USER_GUIDE.md` explicitly defining legitimate scope of use per F5 anti-abuse requirement.
  * Implement DNS adapter unbinding clean uninstall/stop routine.
* **Student C (Backend & Web):**
  * Build responsive Parent Dashboard (Jinja2 + HTMX):
    * Daily and weekly screen-time charts.
    * Top 10 applications and top 10 domains.
    * Weekly $7 \times 48$ schedule matrix editor (30-min resolution).
    * Child request approval/rejection interface.
    * Audit log view (who, when, IP, old value, new value).
  * Implement automated background worker for 90-day event retention purge (F3.4).
  * Implement `"Xóa toàn bộ dữ liệu của con tôi"` endpoint executing atomic dual-deletion on server DB and dispatching immediate purge command to Agent cache.
  * Author `PRIVACY.md` compliance table artifact (F3.5).
* **Weekly Integration Milestone (End of Week 5):**
  * Complete end-to-end user loop: parent modifies policy from mobile browser, agent receives update within 60s, child requests extra time from tray, parent approves, time is granted.
  * Dual-deletion tested and verified on server and local cache.

---

### Week 6: Code Freeze, Hardening, Full Verification & Defense Preparation
* **Focus:** Zero new features. Hardening, automated testing, documentation, and oral defense rehearsal.
* **All Students — Day 1: STRICT CODE FREEZE:**
  * No new features or refactoring permitted. Only bug fixes addressing test failures.
* **Student A (System):**
  * Execute all system test cases from `docs/TEST_PLAN.md` (TEST-F1.1 through TEST-F1.5, TEST-F2.1, TEST-F2.2, TEST-NT1–NT6).
  * Document fail-open vs. fail-closed disconnection handling and defense justification.
  * Prepare live Windows demo environment and fail-safe recovery procedures.
* **Student B (Network & Security):**
  * Run automated DNS test suite; document exact benchmark metrics ($\ge 95\%$ block rate, 0 educational false positives).
  * Verify TLS certificate pinning error handling and tamper rejection (TEST-F4.3, TEST-F5.3).
  * Review and finalize `PRIVACY.md` and `docs/USER_GUIDE.md`.
* **Student C (Backend & Web):**
  * Execute automated backend test suite (Argon2id lockout, CSRF, IDOR ownership, 90-day purge).
  * Co-author the official project report with mandatory Chapter 2.3 (*Vòng đời và giao thức*).
  * Conduct simulated defense questions on system architecture, network programming, and security design.
* **Final Deliverable (End of Week 6):**
  * Working software product packaged and verified.
  * Complete documentation suite (`README.md`, `REQUIREMENTS.md`, `ARCHITECTURE.md`, `TEST_PLAN.md`, `PRIVACY.md`, `USER_GUIDE.md`).
  * 50-domain test suite and 200+ domain classification table.
  * Oral defense slide deck and live demo script.

---

## 4. Risk Register and Mitigation Strategies

| # | Risk Description | Severity | Probability | Mitigation & Fallback Strategy |
| :- | :--- | :--- | :--- | :--- |
| **R1** | **Session 0 Isolation / Tray UI IPC Failure:** Windows Service runs in Session 0 and cannot show GUI; Named Pipe IPC across sessions requires elevated security descriptors. | **CRITICAL** | High | **Mitigation in Week 1:** Prototype IPC immediately. Fallback: If Named Pipe cross-session ACL proves brittle, fallback to loopback HTTP server (`127.0.0.1:<port>`) with a local random bearer token file in `%ProgramData%` restricted by NTFS ACL. |
| **R2** | **Network Adapter DNS Misconfiguration / Internet Brick:** Binding Windows DNS to `127.0.0.1:53` causes complete loss of connectivity if agent crashes or fails ungracefully. | **CRITICAL** | High | **Mitigation in Week 1:** Implement standalone `restore_dns.bat` script using `netsh interface ip set dns name="Wi-Fi" source=dhcp`. Service recovery options configure SCM to execute fallback cleanup upon failure. |
| **R3** | **Active Screen-Time Inaccuracy:** Windows idle tracking (`GetLastInputInfo`) may miscount if background media plays or input hooks fail. | **HIGH** | Medium | **Mitigation in Week 2:** Use simple, robust poll-based idle delta checking. Do not rely on invasive global keyboard/mouse hooks (violates NT2 data minimization). |
| **R4** | **WebSocket Urgent Command Reliability:** NAT or network drops could disconnect WebSocket, causing urgent commands (`khóa ngay`) to exceed the 5-second deadline. | **HIGH** | Medium | **Mitigation in Week 3:** Heartbeat fallback checks pending urgent commands every 60s. WebSocket auto-reconnects with exponential backoff; parent UI warns if WebSocket channel is degraded. |
| **R5** | **Classification Dataset Bottleneck ($\ge 200$ items):** Manually collecting and classifying 200 domains across 6 groups while strictly avoiding real adult domains is time-consuming. | **MEDIUM** | High | **Mitigation in Week 2–4:** Assign Student B to curate dataset incrementally (50 domains/week) using reputable educational, gaming, and news lists. |

---

## 5. De-Prioritized / Postponed Features

To protect the 6-week deadline and guarantee 100% completion of **BẮT BUỘC (MANDATORY)** requirements, the following non-mandatory features are formally postponed:

1. **F1.6 (NÊN CÓ) — Independent App Category Budgets:**
   * *Status:* Postponed until Week 5. Only implemented if Core F1 (daily quota + weekly matrix) is fully verified.
2. **F1.7 (CÓ THÌ TỐT) — Task Completion Bonus Time:**
   * *Status:* Postponed to bonus phase.
3. **F5 (Bonus) — TOTP Two-Factor Authentication:**
   * *Status:* Postponed. Username/Argon2id password with lockout and rate limiting satisfies all mandatory authentication criteria.
4. **Heuristic / Deep Packet Inspection DoH Blocking:**
   * *Status:* Postponed. System will rely on domain-level blocking and IP blocklists for DoH endpoints as specified in the Appendix.

---

## 6. Testing, Early Integration, and Code Freeze Policy

1. **Early Continuous Integration:**
   * Integration testing begins in **Week 2** (Agent enrollment over TLS) rather than being deferred to the final week.
   * Every Friday, the team performs a cross-component synchronization demo.
2. **Demo D1 Checkpoint (End of Week 4):**
   * Formal internal execution of Demo D1 criteria (10m, 5m, 1m warnings + 60s grace period + lock) to validate system integration two weeks before final submission.
3. **Week 6 Strict Code Freeze:**
   * On Monday of Week 6, code changes are restricted to critical bug fixes verified by tests.
   * No feature additions, schema modifications, or architectural rewrites are permitted during Week 6.
