---
name: qa-orchestrator
description: Orchestrate multi-tier software quality assurance, risk-based test planning, and automated quality gate enforcement.
---

# QA Orchestrator Skill

## Mục đích
Điều phối toàn diện quá trình đảm bảo chất lượng phần mềm trong môi trường Agentic AI. Ngăn chặn triệt để hiện tượng "Agent tự báo cáo PASS giả mạo" (False PASS) khi chưa thực sự chạy test hoặc khi test case quá yếu.

## Nguyên tắc cốt lõi
1. **Evidence-Based Acceptance (Chấp thuận dựa trên bằng chứng thực nghiệm):** Không chấp nhận kết luận PASS nếu không có mã thoát (exit code 0), log stdout/stderr, và snapshot/artifact kiểm chứng.
2. **Multi-Tier Quality Gate (Cổng chất lượng đa tầng):** Kiểm thử phải đi từ thấp lên cao:
   - Tầng 1: Static Analysis & Type Checking (`svelte-check`, `cargo check`).
   - Tầng 2: Unit & State Logic Testing (`vitest`).
   - Tầng 3: Backend & Native Systems Testing (`cargo test`).
   - Tầng 4: Database Persistence & Schema Integrity (SQLite checks).
   - Tầng 5: Real-DOM E2E Reality Testing (Headless Browser / Playwright).
   - Tầng 6: Adversarial & Regression Scenarios (Edge cases, race conditions).
3. **Fail-Fast & Zero-Tolerance:** Bất kỳ tầng nào thất bại, toàn bộ quá trình nghiệm thu bị đình chỉ ngay lập tức; không cho phép bỏ qua (ignore/skip) mà không có lý do được ghi nhận rõ ràng.

## Quy trình điều phối chuẩn
```
[Yêu cầu tính năng / Sửa lỗi]
             │
             ▼
    [1. Developer Agent] ──> Viết mã & tự kiểm thử cơ bản
             │
             ▼
   [2. Test Engineer Agent] ──> Bổ sung unit & integration tests
             │
             ▼
   [3. QA Challenger Agent] ──> Kiểm thử phản kháng & phá hoại
             │
             ▼
  [4. Unified Quality Gate] ──> Chạy `npm run qa`
             │
       ┌─────┴─────┐
     FAIL        PASS
       │           │
       ▼           ▼
[Trả lại Dev] [5. Release Auditor Agent] ──> Ký duyệt nghiệm thu
```

## Các lệnh điều phối
- Chạy toàn bộ Quality Gate: `npm run qa`
- Kiểm tra báo cáo máy đọc: `cat test-results/reports/test-summary.json`
- Xem báo cáo nghiệm thu chi tiết: `cat test-results/reports/acceptance-report.md`
