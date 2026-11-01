# OpenGuard Kids — Task Priority List (TODO)

> **Last Updated:** 2026-11-01  
> **Schedule Baseline:** 6-Week Compressed Plan + Milestone M1 Upgrade.

---

## Priority 1: Week 1 — Repository Scaffolding & High-Risk Technical Spikes (COMPLETED - 100%)

- [x] **TASK-01: Author Technical Architecture Specification (`docs/ARCHITECTURE.md`)**
  - Architecture overview, component boundaries, IPC transport (loopback HTTP + token), SQLite WAL schema, screen-time state machine, DNS safe recovery, and 6-week roadmap.
- [x] **TASK-02: Project Scaffolding & CI Tooling**
  - Create [README.md](file:///home/cornar/Projects/OpenGuard-Kids/README.md) with architecture overview, requirements, and instructions.
  - Create `.gitignore` (Python, virtual environments, SQLite, Windows build files).
  - Create `requirements.txt` (`fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `psutil`, `pywin32`, `passlib`, `argon2-cffi`, `dnslib`, `pytest`, `httpx`).
  - Create modular directory skeleton: `src/server/`, `src/agent/`, `src/tray/`, `src/common/`, `data/`, `tests/`.
- [x] **TASK-03: Spike — Windows Service & Session 0 IPC Prototype (Student A)**
  - Implemented `src/agent/ipc.py` with `IPCServer`, `IPCClient`, and dynamic secret token verification.
  - Verified with 3 unit tests in `tests/test_ipc.py` (token auth, 403 rejection, heartbeat, child agency request).
- [x] **TASK-04: Spike — Safe DNS Adapter Configuration & Emergency Restore Script (Student B)**
  - Implemented and verified `restore_dns.bat` (`netsh` DHCP restore) to ensure zero internet-bricking risk.
  - Implemented `src/agent/dns_proxy.py` with `dnslib` (UDP listener, Canary domain NXDOMAIN, SafeSearch CNAME, Heuristic keyword regex, Study mode, Upstream forwarder).
  - Verified with 8 unit tests in `tests/test_dns_proxy.py`.
- [x] **TASK-05: Spike — Backend SQLite WAL & Argon2id Hashing (Student C)**
  - Set up SQLite WAL mode and foreign key enforcement in `src/server/database.py`.
  - Implemented relational models in `src/server/models.py` (`Parent`, `Child`, `Device`, `Policy`, `Event`, `AuditLog`, `ChildRequest`).
  - Implemented Argon2id password hashing, complexity validator, and 15-minute lockout after 5 failed attempts in `src/server/security.py`.
  - Verified with 5 unit tests in `tests/test_database_and_security.py`.

---

## Priority 2: Week 2 — Local Enforcement Engines, Auth & Policy Foundations (COMPLETED - 100%)

- [x] **TASK-06: Windows Screen-Time Tracker & Anti-Tamper Engine (Student A)**
  - Active time tracking loop with idle pause ($>5$ min via `GetLastInputInfo`) and lock detection implemented in `src/agent/screen_time.py`.
  - Clock rollback anti-tamper detection ($>60$s backward jump) preserving consumed quota.
  - State machine covering `ACTIVE_COUNTING`, `IDLE_PAUSED`, warning tiers (10m, 5m, 1m), `GRACE_PERIOD_60S`, `LOCKED_QUOTA`, `LOCKED_SCHEDULE`, `LOCKED_URGENT`.
  - Benchmark accuracy verified ($\le \pm 30$s per simulated hour).
  - Verified with 7 unit tests in `tests/test_screen_time.py`.
- [x] **TASK-07: Local DNS Proxy Engine, SafeSearch & Educational Blockpage (Student B)**
  - Wildcard domain blocklist matching and CNAME SafeSearch rewriting.
  - Implemented polite, educational HTTP blockpage server on `127.0.0.1:8080` in `src/agent/blockpage.py` (NT3/NT4 compliance with Hotline 111 banner and child unblock request form).
  - Verified with 3 integration tests in `tests/test_blockpage.py`.
- [x] **TASK-08: Parent Authentication & Device Enrollment API (Student C)**
  - Endpoints `/api/v1/auth/register`, `/api/v1/auth/login`, `/api/v1/auth/logout`, `/api/v1/auth/me` with `HttpOnly; SameSite=Lax` cookies, 12h expiry, and Argon2id complexity.
  - 15-minute brute-force lockout after 5 consecutive failed attempts.
  - Device enrollment API with 8-character pairing code (10-minute TTL) in `src/server/app.py`.
  - Strict query-level ownership checks (IDOR defense) preventing cross-tenant child access.
  - Verified with 4 integration tests in `tests/test_server_auth.py`.
- [x] **MILESTONE-W2: Week 2 Integration Verification**
  - Full test suite passing: 30/30 tests verified across agent, DNS proxy, screen-time tracker, blockpage, and server auth.

---

## Priority 3: Week 3 — Process Enforcement, Sync Protocols & Event Ingestion (COMPLETED - 100%)

- [x] **TASK-09: Process Monitor & SHA-256 Hash Scanner (Student A)**
  - Process monitor with `psutil` in `src/agent/process_monitor.py`.
  - Binary SHA-256 hash matching on process launch with in-memory `(mtime, size)` caching.
  - Verified renamed binary detection (e.g. `notepad.exe` running a prohibited game binary is blocked by hash per F2.1).
  - Termination of prohibited processes with event callback (F2.2).
  - Verified with 5 unit tests in `tests/test_process_monitor.py`.
- [x] **TASK-10: 50-Domain Test Suite & Offline Event Buffer (Student B)**
  - Curated 50-domain test suite in `data/test_domains.json` per Appendix breakdown (20 education, 15 inappropriate, 10 entertainment/social, 5 uncategorized).
  - Implemented local persistent event queue in SQLite WAL mode in `src/agent/offline_buffer.py` enforcing strict 7-field privacy schema (NT2).
  - Verified with 3 unit tests in `tests/test_offline_buffer.py`.
- [x] **TASK-11: Sync Protocols, Event Ingestion & WebSocket Hub (Student C)**
  - Batch event ingestion endpoint `/api/v1/events/batch` with idempotency deduplication in `src/server/app.py`.
  - Periodic 60s heartbeat endpoint `/api/v1/heartbeat`.
  - WebSocket hub and urgent command dispatcher (`LOCK_URGENT`, `UNLOCK`, `ADD_TIME`) in `src/server/ws_manager.py` with offline heartbeat fallback (< 5s benchmark F4.1).
  - Strict IDOR defense on command dispatch.
  - Verified with 3 integration tests in `tests/test_sync_and_events.py`.
- [x] **MILESTONE-W3: Week 3 Integration Verification**
  - Server pushes WebSocket urgent lock command; Agent locks within 5 seconds.
  - Process blocking emits `process_blocked` event to local SQLite and syncs to server.
  - 41/41 tests passing across full codebase.

---

## Priority 4: Week 4 — Desktop Tray UI & Demo D1 Readiness (COMPLETED - 100%)

- [x] **TASK-12: Desktop Tray UI & Windows IPC Integration (Student A)**
  - Implemented `src/tray/state_listener.py` connecting Tray UI to Windows Service via IPC.
  - Status polling (1.0s) and periodic 10s heartbeat.
  - Anti-abuse auto-shutdown/alert if connection to service is lost $> 15$ seconds (NT1, F5).
  - Verified in `tests/test_tray_app.py`.
- [x] **TASK-13: DNS Proxy Benchmark & DoH Verification (Student B)**
  - Benchmarked DNS proxy with 50 test domains in `data/test_domains.json` ($\ge 95\%$ block rate, 0 educational false positives).
  - Canary domain `use-application-dns.net` disabling browser DoH fallback.
- [x] **TASK-14: Advance Warning Sequence & Child Agency Buttons (Student C & Student A)**
  - Advance warning toasts at 10m, 5m, 1m in `src/tray/dialogs.py`.
  - 60-second grace period dialog with document save prompt before lock.
  - Child agency buttons: "Xin thêm 15 phút" and "Báo chặn nhầm" via IPC in `src/tray/app.py`.
  - Child Transparency screen (NT5) and Hotline 111 banner.
- [x] **MILESTONE-W4: Demo D1 Acceptance Verification**
  - Verified complete Demo D1 sequence in `test_complete_demo_d1_acceptance_sequence`:
    Active usage $\rightarrow$ 10m/5m/1m warnings $\rightarrow$ 60s grace dialog $\rightarrow$ Lock screen overlay $\rightarrow$ Child agency request $\rightarrow$ Parent approves $\rightarrow$ Screen unlocks back to Active!
  - 46/46 tests passing across full codebase.

---

## Priority 5: Week 5 — Parent Dashboard, Transparency Screens & Privacy Operations (COMPLETED - 100%)

- [x] **TASK-15: Child Transparency Screen & Audit Log in Tray UI (Student A)**
  - Implemented `"Hôm nay em đã dùng gì"` transparency model (NT5, F3.3) and child rights in `src/tray/dialogs.py` & `src/tray/app.py`.
- [x] **TASK-16: Finalize Datasets, Privacy Doc & User Guide (Student B)**
  - Curated 200-entry classification table in `data/classification_dataset.json` covering all 6 taxonomies with default rules for ages 6–11 (F2.4).
  - Authored authoritative `PRIVACY.md` compliance table artifact (F3.5): Field $\leftrightarrow$ Purpose $\leftrightarrow$ Retention Period $\leftrightarrow$ Visibility.
- [x] **TASK-17: Mobile-Friendly Parent Web Dashboard & Reporting (Student C)**
  - Implemented summary report endpoint `/api/v1/dashboard/summary/{child_id}` with screen-time charts, Top 10 apps, Top 10 domains, total blocked count, and child requests inbox (F3.2).
  - Implemented responsive mobile-first Parent Web Dashboard in `src/server/templates/dashboard.html` and `GET /dashboard/{child_id}`.
  - Implemented child request review endpoint `/api/v1/dashboard/requests/{request_id}/review`.
- [x] **TASK-18: 90-Day Purge Worker & Atomic Dual-Deletion (Student C & Student A)**
  - Implemented Atomic Dual-Deletion button `/api/v1/children/{child_id}/purge-data` deleting simultaneously on server and local agent cache via WebSocket (F3.4).
  - Implemented 90-day retention automated cleanup worker `/api/v1/maintenance/purge-expired` (F3.4).
  - Verified with 5 unit & integration tests in `tests/test_dashboard_and_privacy.py`.
- [x] **MILESTONE-W5: Full End-to-End System Loop Verification**
  - Verified complete end-to-end loop: reports generation, request approval, atomic dual deletion, and 90-day retention purge.
  - 51/51 tests passing across full codebase.

---

## Priority 6: Week 6 — Strict Code Freeze, Hardening, Full Verification & Defense Preparation (COMPLETED - 100%)

- [x] **TASK-19: Strict Code Freeze (Day 1 of Week 6)**
  - Formal code freeze enacted (zero new features, focused solely on reliability and security).
- [x] **TASK-20: Full Test Suite Execution, Hardening & E2E Acceptance Runner**
  - Executed full test suite: 51/51 automated tests passed (100%).
  - Updated `docs/TEST_PLAN.md` with complete requirement traceability matrix (all tests marked PASSED).
  - Built autonomous acceptance demo runner `scripts/e2e_acceptance_verification.py` verifying all 6 key scenarios (renamed binary hash, clock rollback anti-tamper, advance warning sequence & 60s grace, SafeSearch DNS rewrite, WebSocket <5s latency [1.37ms], and atomic dual deletion).
- [x] **TASK-21: Project Report & Defense Preparation**
  - Authored authoritative `docs/FINAL_REPORT.md` featuring mandatory Section 2.3 (*Vòng đời và giao thức* per assignment requirements).
  - Authored comprehensive `docs/DEFENSE_GUIDE.md` containing 3-student presentation plan, live demo guide, and Top 10 defense questions with exact code line references.
  - Authored study note `notes/16_week6_code_freeze_hardening_and_defense.md` and updated `notes/README.md`.
- [x] **TASK-22: Complete Architectural Specification & Modular Component Documentation**
  - Generated publication-grade 12-page PDF [OpenGuard_Kids_Toan_Bo_Co_Che_Thanh_Phan.pdf](file:///home/cornar/Projects/OpenGuard-Kids/OpenGuard_Kids_Toan_Bo_Co_Che_Thanh_Phan.pdf) with 5 vector SVG diagrams.
  - Authored master architecture & mechanism documents [docs/SYSTEM_MECHANISMS_AND_INTEGRATION.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/SYSTEM_MECHANISMS_AND_INTEGRATION.md) and [CO_CHE_VA_LIEN_KET_HE_THONG.md](file:///home/cornar/Projects/OpenGuard-Kids/CO_CHE_VA_LIEN_KET_HE_THONG.md).
  - Created 16 modular deep-dive technical documents in [docs/components/](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/README.md) (15 files for individual components and underlying frameworks, File 16 for full E2E generalized chronological family case study).
- [x] **TASK-23: Turnkey Agent Service Orchestrator & CLI Runners**
  - Implemented `src/agent/service.py` (`AgentService` master orchestrator coordinating ScreenTime, DNS Proxy, Blockpage, Process Monitor, Offline Buffer, and IPC Server).
  - Authored CLI entrypoints: `src/server/main.py`, `src/agent/main.py`, `src/tray/main.py`, and interactive live defense showcase `scripts/run_demo.py`.
  - Added unit tests in `tests/test_agent_service.py` (53/53 tests passing, 100%).
- [x] **TASK-24: Comprehensive Networking Theory Knowledge Base**
  - Authored specialized study notes directly mapped to Chapter 2 networking curriculum:
    - [chuyen_de_http_toan_dien.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/chuyen_de_http_toan_dien.md)
    - [chuyen_de_dhcp_toan_dien.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/chuyen_de_dhcp_toan_dien.md)
    - [chuyen_de_dns_toan_dien.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/chuyen_de_dns_toan_dien.md)

---

## Priority 7: Milestone M1 — Native Desktop GUI Implementation for Tray UI (COMPLETED - 100%)

- [x] **TASK-25: Native Desktop GUI Implementation for Tray UI (Session 1)**
  - Added `pystray>=0.19.5` and `Pillow>=10.2.0` to `requirements.txt` and installed into `.venv`.
  - Implemented `src/tray/gui.py` Presenter and Views:
    - Dynamic Pillow 64x64 RGBA badge rendering remaining minutes in white, with 4 background color thresholds (>10m sky blue `#0284c7`, 5-10m amber `#f59e0b`, <5m deep orange `#ea580c`, locked/offline red `#dc2626`).
    - Pystray System Tray icon with exact 6-item context menu, strictly excluding Exit/Quit (NT1 anti-tamper).
    - Escalating real-time toasts: 10m (6s auto-dismiss), 5m (8s auto-dismiss), 1m (10s auto-dismiss + optional beep).
    - 60-second grace dialog with Win32 `WS_EX_NOACTIVATE` & `WS_EX_TOPMOST`, without focus stealing, digital countdown, progress bar, "Khóa ngay" and "Xin thêm 15 phút" buttons.
    - Fullscreen lock overlay with `overrideredirect`, `topmost`, `grab_set`, `Alt+F4`/`Esc` interception, transparent lock reason, and National Child Protection Hotline 111 banner.
    - Transparency window ("Hôm nay em đã dùng gì" - NT5) mirroring parental dashboard statistics and child rights charter.
    - Thread-safe event queue marshaling from background `OGK-Tray-Listener` to Tkinter mainloop.
  - Implemented `src/tray/main.py` entrypoint with `is_gui_environment_available()` and graceful fallback to `default_ui_display`.
  - Updated `src/agent/service.py` to canonically support `"ADD_TIME"` for child time extensions.
  - Added 7 comprehensive unit tests in `tests/test_tray_app.py`, maintaining 100% test pass (60/60 unit tests, 6/6 E2E acceptance scenarios).

