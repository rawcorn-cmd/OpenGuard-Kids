# OpenGuard Kids — Project Progress Tracking

> **Course:** Computer Networks (*Mạng máy tính*) — Faculty of Information Technology, HCMUS  
> **Last Updated:** 2026-11-01  
> **Schedule Baseline:** 6-Week Execution Plan + Post-Freeze Desktop GUI Upgrade (M1/M2).  
> **Current Phase:** M1 (Tray UI Native Desktop GUI Realization) COMPLETED.

---

## 1. Overall Progress Summary (6-Week Roadmap)

| Phase / Week | Primary Focus | Status | Progress | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0** | Assignment Analysis & Requirements Verification | **COMPLETED** | 100% | Verified 1:1 against `ASSIGNMENT.docx` & teacher's copy in Downloads |
| **Phase 1** | Technical Architecture Design | **COMPLETED** | 100% | `docs/ARCHITECTURE.md` completed & signed off |
| **Week 1** | Scaffolding & High-Risk Technical Spikes | **COMPLETED** | 100% | 16/16 Unit tests passed across all 3 spikes (DNS, IPC, WAL/Argon2id) |
| **Week 2** | Local Engines, Auth & Policy Foundations | **COMPLETED** | 100% | 30/30 Unit & integration tests passed (Screen-time, Blockpage, Auth API) |
| **Week 3** | Process Enforcement, Sync & Event Ingestion | **COMPLETED** | 100% | 41/41 Tests passed (SHA-256 process monitor, Offline Buffer, WebSocket Hub) |
| **Week 4** | Desktop Tray UI & Demo D1 Readiness | **COMPLETED** | 100% | 46/46 Tests passed (StateListener, Warnings, 60s Grace, Lock, Demo D1) |
| **Week 5** | Parent Dashboard, Transparency & Privacy | **COMPLETED** | 100% | 51/51 Tests passed (HTMX Dashboard, 200+ dataset, PRIVACY.md, Dual Delete) |
| **Week 6** | Strict Code Freeze, Verification & Defense | **COMPLETED** | 100% | Strict Code Freeze, E2E acceptance runner, FINAL_REPORT (Sec 2.3), DEFENSE_GUIDE |
| **M1 Upgrade** | Native Desktop GUI for Tray UI (Session 1) | **COMPLETED** | 100% | 60/60 Tests passed, 6/6 E2E scenarios passed (Pystray, Pillow, Tkinter, WS_EX_NOACTIVATE) |

---

## 2. Completed Milestones & Deliverables

* [x] **Workspace Inspection:** Verified initial workspace state and reviewed [AGENTS.md](file:///home/cornar/Projects/OpenGuard-Kids/AGENTS.md).
* [x] **Authoritative Extraction & Verification:** Parsed full XML structure of [docs/ASSIGNMENT.docx](file:///home/cornar/Projects/OpenGuard-Kids/docs/ASSIGNMENT.docx) and verified 100% byte-level equivalence with teacher's original file in Downloads `MoTa_Doan_QLyViecSuDungPCCuaTre (1).docx`.
* [x] **Course Alignment:** Confirmed academic context: Computer Networks Course Project (*Đồ án môn học Mạng máy tính*), Faculty of Information Technology, HCMUS.
* [x] **Requirements Specification:** Authored and verified [docs/REQUIREMENTS.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/REQUIREMENTS.md) documenting explicit functional (F1–F4), non-functional/security (F5), design principles (NT1–NT6), and prohibited features.
* [x] **Traceability Test Plan:** Authored [docs/TEST_PLAN.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/TEST_PLAN.md) mapping all tests to explicit assignment criteria with priority labels (all marked as unexecuted).
* [x] **Requirements Verification Pass:** Re-checked all numerical thresholds, documented the 50 vs. 60 test domain discrepancy, confirmed the three explicit urgent commands, and audited for zero unsupported claims.
* [x] **6-Week Implementation Plan:** Revised [docs/TEAM_PLAN.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/TEAM_PLAN.md) to fit the real 6-week timeline across 3 students, incorporating early integration, risk mitigation, and a Week 6 code freeze.
* [x] **Technical Architecture Specification:** Authored [docs/ARCHITECTURE.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/ARCHITECTURE.md) covering all 10 mandated architectural sections (IPC contract, SQLite WAL schema, screen-time state machine, DNS safe recovery, security boundaries, and failure modes).
* [x] **Defense Guide & Architectural Overview:** Authored [docs/PROJECT_OVERVIEW.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/PROJECT_OVERVIEW.md) and root [README.md](file:///home/cornar/Projects/OpenGuard-Kids/README.md).
* [x] **Audio Lessons Scaffolding:** Synthesized Vietnamese Neural TTS audio lessons and Markdown study guides: [audio_lessons/hoc_phan_01.md](file:///home/cornar/Projects/OpenGuard-Kids/audio_lessons/hoc_phan_01.md) & [audio_lessons/hoc_phan_02.md](file:///home/cornar/Projects/OpenGuard-Kids/audio_lessons/hoc_phan_02.md).
* [x] **Network Knowledge Base Standardized:** Imported, classified, and converted all HCMUS course materials & Kurose Top-Down Approach files into clean Markdown library under [docs/network_curriculum/](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/README.md) (Theory notes, HCMUS lecture slides, 12 Wireshark labs, Python socket programming samples).
* [x] **Full 9th Edition Kurose & Ross Digitalization:** Extracted, cleaned, and standardized all 9 chapters (717 pages) of *Computer Networking: A Top-Down Approach (9th Edition, 2026)* directly into Markdown under [docs/network_curriculum/01_theory_notes/kurose_9th/](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/kurose_9th/README.md), complete with OpenGuard Kids application callouts for student defense.
* [x] **Comprehensive Course Study Notes Generated:** Compiled and structured 100% of all session dialogues, networking concepts, Windows Internals, and architectural decisions into modular Markdown notes under [notes/](file:///home/cornar/Projects/OpenGuard-Kids/notes/README.md) (10 specialized modules + Master Index, including Router hardware internals, 9Router AI, Port 53 mechanics, and loopback resolution).
* [x] **Week 1 Scaffolding & Technical Spikes Implemented (16/16 Unit Tests Passed):**
  - **Scaffolding:** Created modular source tree (`src/common/`, `src/agent/`, `src/server/`, `src/tray/`, `data/`, `tests/`), `.gitignore`, and installed dependencies into `.venv`.
  - **Spike TASK-04 (DNS Proxy & Recovery):** Implemented `restore_dns.bat` emergency restore script and `src/agent/dns_proxy.py` (`dnslib` UDP listener, Canary domain, SafeSearch CNAME, Heuristic regex, Whitelist, Upstream forwarder). Verified with 8 tests in `tests/test_dns_proxy.py`.
  - **Spike TASK-05 (SQLite WAL & Argon2id):** Implemented `src/server/database.py` with WAL & Foreign Keys pragma, relational models in `src/server/models.py`, and `src/server/security.py` with Argon2id password hashing, complexity validator, and 15-minute brute-force lockout. Verified with 5 tests in `tests/test_database_and_security.py`.
  - **Spike TASK-03 (Session 0 to Session 1 IPC):** Implemented `src/agent/ipc.py` (`IPCServer`, `IPCClient`, 64-hex token authentication). Verified with 3 tests in `tests/test_ipc.py`.
* [x] **Week 2 Local Enforcement Engines, Auth & Enrollment Implemented (30/30 Unit & Integration Tests Passed):**
  - **TASK-06 (Screen-Time Tracker & Anti-Tamper Engine):** Implemented `src/agent/screen_time.py` finite state machine (`ACTIVE_COUNTING`, `IDLE_PAUSED`, warning tiers 10m/5m/1m, `GRACE_PERIOD_60S`, `LOCKED_QUOTA`, `LOCKED_SCHEDULE`, `LOCKED_URGENT`). Features `GetLastInputInfo` idle detection (> 300s pause), clock rollback backdating detection (> 60s backward jump with locked quota preservation), weekly 7x48 schedule matrix, and hourly accuracy drift $\le \pm 30$s. Verified with 7 tests in `tests/test_screen_time.py`.
  - **TASK-07 (Local Blockpage HTTP Server):** Implemented lightweight HTTP blockpage server on `127.0.0.1:8080` in `src/agent/blockpage.py` adhering strictly to NT3/NT4 (non-punitive, polite explanation, Hotline 111 banner, and child unblock/study request submission endpoint). Verified with 3 integration tests in `tests/test_blockpage.py`.
  - **TASK-08 (Parent Authentication & Device Enrollment API):** Implemented FastAPI server in `src/server/app.py`, `src/server/auth.py`, and `src/server/schemas.py`. Features Argon2id password validation, 15-minute lockout on 5 failed attempts, session cookies (`HttpOnly; SameSite=Lax`), 8-character pairing codes with 10-minute TTL, agent enrollment endpoint, and query-level IDOR protection preventing cross-parent access. Verified with 4 integration tests in `tests/test_server_auth.py`.
* [x] **Week 3 Process Enforcement, Sync Protocols & Event Ingestion Implemented (41/41 Tests Passed):**
  - **TASK-09 (Process Monitor & SHA-256 Hash Scanner):** Implemented `src/agent/process_monitor.py` with `psutil` scanner, binary SHA-256 matching, in-memory `(mtime, size)` hash caching for zero CPU disk thrashing, renamed binary detection (F2.1), and process termination with event notifications (F2.2). Verified with 5 tests in `tests/test_process_monitor.py`.
  - **TASK-10 (50-Domain Test Suite & Offline Event Buffer):** Curated 50-domain test suite in `data/test_domains.json`. Implemented `src/agent/offline_buffer.py` using SQLite WAL mode for network disconnection resilience, enforcing strict 7-field privacy schema (NT2). Verified with 3 tests in `tests/test_offline_buffer.py`.
  - **TASK-11 (Batch Event Ingestion & Real-Time WebSocket Hub):** Implemented `/api/v1/events/batch` with idempotency deduplication, `/api/v1/heartbeat` 60s periodic sync, and `src/server/ws_manager.py` WebSocket connection hub dispatching urgent commands (`LOCK_URGENT`, `UNLOCK`, `ADD_TIME`) in $< 5$s (F4.1) with automatic heartbeat offline fallback. Verified with 3 tests in `tests/test_sync_and_events.py`.
* [x] **Week 4 Desktop Tray UI & Demo D1 Acceptance Implemented (46/46 Tests Passed):**
  - **TASK-12 (Desktop Tray UI & State Listener):** Implemented `src/tray/state_listener.py` with 1.0s IPC polling, 10s heartbeat to Session 0 Windows Service, and anti-abuse safeguard (NT1, F5) detecting lost service connection $> 15$ seconds.
  - **TASK-13 & TASK-14 (Dialogs, Warnings & Child Agency):** Implemented `src/tray/dialogs.py` and `src/tray/app.py` providing polite warning toasts (10m, 5m, 1m), 60-second grace period dialog with document save prompt, lock screen overlay, child extra time request ("Xin thêm 15 phút"), false positive domain unblock reporting, and Transparency screen (NT5).
  - **MILESTONE-W4 (Demo D1 Acceptance Verification):** Successfully verified complete Demo D1 sequence in `tests/test_tray_app.py` covering active counting $\rightarrow$ warnings $\rightarrow$ grace period $\rightarrow$ lock $\rightarrow$ agency request $\rightarrow$ unlock.
* [x] **Week 5 Parent Dashboard, Transparency Screens & Privacy Operations Implemented (51/51 Tests Passed):**
  - **TASK-15 & TASK-16 (Dataset, Privacy Doc & Transparency):** Curated 200-entry dataset in `data/classification_dataset.json` covering 6 taxonomies with age 6–11 default policies (F2.4). Authored `PRIVACY.md` compliance table (F3.5). Implemented `"Hôm nay em đã dùng gì"` transparency screen (NT5, F3.3).
  - **TASK-17 (Mobile-Friendly Parent Web Dashboard & Reports API):** Implemented `/api/v1/dashboard/summary/{child_id}` with screen-time duration, Top 10 apps, Top 10 domains, total blocked counts, and child request review (F3.2). Served responsive HTML dashboard at `GET /dashboard/{child_id}`.
  - **TASK-18 (90-Day Auto Purge & Atomic Dual-Deletion):** Implemented `/api/v1/maintenance/purge-expired` (90-day retention cleanup) and `/api/v1/children/{child_id}/purge-data` button executing simultaneous deletion on server database and local agent cache via WebSocket (F3.4). Verified with 5 tests in `tests/test_dashboard_and_privacy.py`.
* [x] **Week 6 Strict Code Freeze, Hardening & Turnkey Orchestration (100% Ready):**
  - **TASK-19 (Strict Code Freeze):** Formalized strict code freeze policy: zero feature additions, focused purely on robustness and security.
  - **TASK-20 (Full Test Verification & E2E Demo Runner):** Verified all 53 automated tests passing (100%). Updated `docs/TEST_PLAN.md` requirement traceability matrix with PASSED status for all tests. Built and verified autonomous acceptance demo runner `scripts/e2e_acceptance_verification.py` covering all 6 mandatory demo scenarios (Renamed binary SHA-256 detection, Clock rollback tamper protection, Demo D1 warning toasts & 60s grace period, DNS SafeSearch & blockpage resolution, WebSocket urgent latency benchmark [0.36 ms], and Atomic Dual Deletion).
  - **TASK-21 (Final Technical Report & Defense Guide):** Authored comprehensive `docs/FINAL_REPORT.md` with mandatory Section 2.3 (*Vòng đời và giao thức*). Authored `docs/DEFENSE_GUIDE.md` detailing 3-student presentation roles, live demo script, and model answers with code references for Top 10 defense questions. Authored study note `notes/16_week6_code_freeze_hardening_and_defense.md` and updated `notes/README.md`.
  - **TASK-22 (Turnkey Agent Service Orchestrator & CLI Runners):** Implemented `src/agent/service.py` (`AgentService` master orchestrator coordinating ScreenTime, DNS Proxy, Blockpage, Process Monitor, Offline Buffer, and IPC Server). Created standard entry points `src/server/main.py`, `src/agent/main.py`, `src/tray/main.py`, and interactive live defense showcase `scripts/run_demo.py`. Verified with 2 new unit tests in `tests/test_agent_service.py` (53/53 tests passing).
  - **TASK-23 (Comprehensive Networking Theory Knowledge Base):** Authored 3 specialized study notes: [chuyen_de_http_toan_dien.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/chuyen_de_http_toan_dien.md), [chuyen_de_dhcp_toan_dien.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/chuyen_de_dhcp_toan_dien.md), and [chuyen_de_dns_toan_dien.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/network_curriculum/01_theory_notes/chuyen_de_dns_toan_dien.md) mapping Chapter 2 networking theory directly into OpenGuard Kids defense questions.
* [x] **Comprehensive Technical Documentation & Component Specifications:**
  - **Publication-Grade PDF:** Generated 12-page high-end PDF report [OpenGuard_Kids_Toan_Bo_Co_Che_Thanh_Phan.pdf](file:///home/cornar/Projects/OpenGuard-Kids/OpenGuard_Kids_Toan_Bo_Co_Che_Thanh_Phan.pdf) with 5 full-page vector SVG diagrams, technical parameter cards, and test matrices.
  - **Master Architecture & Interconnection Markdown:** Authored [docs/SYSTEM_MECHANISMS_AND_INTEGRATION.md](file:///home/cornar/Projects/OpenGuard-Kids/docs/SYSTEM_MECHANISMS_AND_INTEGRATION.md) and [CO_CHE_VA_LIEN_KET_HE_THONG.md](file:///home/cornar/Projects/OpenGuard-Kids/CO_CHE_VA_LIEN_KET_HE_THONG.md) detailing all 15 core components, 4 communication channels, and 5 Mermaid sequence lifecycle flows.
  - **16 Modular Component Breakdowns:** Created dedicated deep-dive technical documents in [docs/components/](file:///home/cornar/Projects/OpenGuard-Kids/docs/components/README.md) (15 component files explaining underlying frameworks & Win32/Network internals, plus File 16 providing an end-to-end chronological case study of a family's typical day).
* [x] **Task Tracking Setup:** Synchronized [PROGRESS.md](file:///home/cornar/Projects/OpenGuard-Kids/PROGRESS.md) and [TODO.md](file:///home/cornar/Projects/OpenGuard-Kids/TODO.md).
* [x] **M1 Milestone — Native Desktop GUI Implementation (Session 1):**
  - Implemented `src/tray/gui.py` with `pystray` Taskbar icon, Pillow dynamic 64x64 minute badge (4 color tiers), NT1-compliant 6-item menu (strictly no Exit), 10m/5m/1m escalating toasts, 60s non-focus-stealing grace dialog (`WS_EX_NOACTIVATE`), fullscreen lock overlay, NT5 transparency window, and thread marshaling queue.
  - Implemented graceful headless fallback in `src/tray/main.py` routing to `default_ui_display` when GUI/DISPLAY is absent.
  - Enhanced `src/agent/service.py` to canonically accept `"ADD_TIME"` for child time extensions.
  - Added 7 comprehensive unit tests in `tests/test_tray_app.py`, bringing total tests to 60/60 passing (100%), and verified 6/6 E2E acceptance scenarios (100%).

---

## 3. Project Status & Defense Readiness

* **Code Status:** Production-ready & hardened. 60/60 tests passing (100%).
* **Demonstration Readiness:** Turnkey runners (`scripts/run_demo.py`, `scripts/e2e_acceptance_verification.py`, `src.server.main`, `src.agent.main`, `src.tray.main`) verified out-of-the-box.
* **Documentation Completeness:** 100% complete across assignment requirements, test plan, architectural specs, privacy charters, student defense guides, study notes, and modular component breakdowns.
