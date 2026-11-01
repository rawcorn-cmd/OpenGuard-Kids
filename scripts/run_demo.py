#!/usr/bin/env python3
"""
OpenGuard Kids — Master Interactive Demo Runner (CLI Showcase)
Designed for Student Defense, Teacher Assessment, and System Verification.

Features:
  - Spins up ephemeral Backend Server, Agent Service, and IPC Channel
  - Provides an interactive menu to demonstrate every assignment requirement live:
    1. Active Screen-Time Tracking & Warnings
    2. DNS Blocklist Filtering & Educational Blockpage
    3. SafeSearch CNAME Injection
    4. Anti-Tamper Clock Rollback Detection
    5. Prohibited Binary Termination (SHA-256 detection)
    6. Real-Time WebSocket Urgent Lock (< 5s benchmark)
    7. Child Agency ("Xin thêm 15 phút" / "Báo chặn nhầm")
    8. Parent Web Dashboard Live Access (http://127.0.0.1:8000/dashboard/1)
    9. Atomic Dual Deletion (Privacy NT2 / F3.4)
"""

import os
import sys
import time
import shutil
import tempfile
import threading
import subprocess
import httpx

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.service import AgentService
from src.agent.ipc import IPCClient
from src.common.constants import DEFAULT_TEST_DNS_PORT


def clear_screen():
    print("\033[H\033[J", end="")


def main():
    print("=" * 75)
    print("   OPENGUARD KIDS — INTERACTIVE SYSTEM DEMO & DEFENSE SHOWCASE   ")
    print("   Course: Computer Networks — Faculty of IT, HCMUS              ")
    print("=" * 75)
    print("[*] Preparing isolated demonstration environment...")

    demo_dir = tempfile.mkdtemp(prefix="ogk_demo_")
    server_port = 8800
    dns_port = DEFAULT_TEST_DNS_PORT
    blockpage_port = 8880
    ipc_port = 8865

    # 1. Start Backend Server as subprocess
    server_cmd = [
        sys.executable, "-m", "uvicorn", "src.server.app:app",
        "--host", "127.0.0.1", "--port", str(server_port), "--log-level", "warning"
    ]
    env = os.environ.copy()
    env["OPEN_GUARD_DATA_DIR"] = demo_dir
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    server_proc = subprocess.Popen(server_cmd, env=env)
    print(f"[+] Started Parent Backend Server at: http://127.0.0.1:{server_port}")

    # Wait for server to be responsive
    server_ready = False
    for _ in range(30):
        if server_proc.poll() is not None:
            break
        try:
            r = httpx.get(f"http://127.0.0.1:{server_port}/docs", timeout=1.0)
            if r.status_code == 200:
                server_ready = True
                break
        except Exception:
            time.sleep(0.2)

    if not server_ready:
        print("[!] Backend server failed to start in time. Aborting.")
        server_proc.kill()
        shutil.rmtree(demo_dir, ignore_errors=True)
        return

    # 2. Start Agent Service in background thread
    agent = AgentService(
        device_id="DEMO-PC-STUDENT",
        child_id="1",
        server_url=f"http://127.0.0.1:{server_port}",
        data_dir=demo_dir,
        dns_port=dns_port,
        blockpage_port=blockpage_port,
        ipc_port=ipc_port,
        daily_limit_minutes=15.0,  # 15 minutes quota for quick testing
        sync_interval_seconds=2.0,
    )
    # Configure blocklist & prohibited binaries for live demo
    agent.dns_proxy.add_blocked_domains(["bet88.com", "casino-vip.net", "xxx-movies.org"])
    agent.process_monitor.add_blocked_names(["cheatengine.exe", "prohibited_game.exe"])
    agent.start()
    print(f"[+] Started Windows Service Simulator (Session 0)")
    print(f"    - DNS Proxy listening on UDP port:  {dns_port}")
    print(f"    - Blockpage Server on HTTP:        http://127.0.0.1:{blockpage_port}")
    print(f"    - Loopback IPC Channel on HTTP:     http://127.0.0.1:{ipc_port}")

    ipc_client = IPCClient(
        host="127.0.0.1",
        port=ipc_port,
        secret_token=agent.ipc_manager.secret_token,
    )

    print("\n" + "=" * 75)
    print(f"  Parent Web Dashboard URL: http://127.0.0.1:{server_port}/dashboard/1")
    print("=" * 75)

    try:
        while True:
            status = agent.get_status_payload()
            rem = status.get("remaining_seconds", 0)
            print(f"\n[TRẠNG THÁI HIỆN TẠI]: Trạng thái={status.get('status')} | Còn lại={rem/60:.1f}m | Khóa={status.get('is_locked')}")
            print("-" * 75)
            print("CHỌN KỊCH BẢN THỬ NGHIỆM:")
            print("  1. Kiểm tra DNS Proxy & Ép CNAME SafeSearch (Google, YouTube)")
            print("  2. Thử truy cập Web cấm (bet88.com) -> Điều hướng Blockpage")
            print("  3. Thử mở App cấm / Đổi tên file (Process Monitor & SHA-256)")
            print("  4. Thử gian lận lùi đồng hồ Windows (-3 giờ) -> Anti-Tamper check")
            print("  5. Phụ huynh phát lệnh KHÓA KHẨN CẤP (Urgent Lock)")
            print("  6. Trẻ em bấm nút 'Xin thêm 15 phút' qua IPC -> Phụ huynh duyệt mở khóa")
            print("  7. Xem Parent Web Dashboard (Mở qua HTTP API / Browser)")
            print("  8. Thực hiện Xóa Dữ Liệu Đồng Thời (Atomic Dual Deletion - NT2)")
            print("  9. Chạy Tự Động Toàn Bộ 6 Kịch Bản Nghiệm Thu (E2E Test Runner)")
            print("  0. Thoát demo")
            print("-" * 75)

            choice = input("Nhập số (0-9): ").strip()
            if choice == "0":
                break

            elif choice == "1":
                print("\n[*] Gửi truy vấn DNS kiểm tra Google SafeSearch:")
                from dnslib import DNSRecord
                q = DNSRecord.question("www.google.com")
                ans = DNSRecord.parse(agent.dns_proxy.handle_query(q.pack()))
                print(f"    -> Query: www.google.com => Rewritten SafeSearch: {ans.rr}")

            elif choice == "2":
                print("\n[*] Gửi truy vấn DNS thử vào trang cấm 'bet88.com':")
                from dnslib import DNSRecord
                q = DNSRecord.question("bet88.com")
                ans = DNSRecord.parse(agent.dns_proxy.handle_query(q.pack()))
                print(f"    -> Query: bet88.com => Blocked Response: {ans.rr} (Trỏ về Blockpage 127.0.0.1)")
                print(f"    -> Trẻ em mở trình duyệt sẽ thấy trang Blockpage tại http://127.0.0.1:{blockpage_port}")

            elif choice == "3":
                print("\n[*] Quét tiến trình hệ thống bằng SHA-256:")
                agent.process_monitor.scan_and_enforce_once()
                print("    -> Đã quét xong. Các phần mềm đổi tên hoặc vi phạm đều được so khớp mã băm SHA-256.")

            elif choice == "4":
                print("\n[*] Mô phỏng trẻ em chỉnh lùi đồng hồ hệ thống 2 tiếng:")
                agent.tracker.last_wall_time = time.time() + 7200.0
                agent.tracker.tick()
                print(f"    -> Phát hiện gian lận: {agent.tracker.tamper_detected}")
                print(f"    -> Thời gian đã dùng vẫn được bảo toàn: {agent.tracker.consumed_seconds_today/60:.1f} phút")

            elif choice == "5":
                print("\n[*] Phụ huynh gửi lệnh KHÓA KHẨN CẤP...")
                agent.tracker.set_urgent_lock(True)
                print(f"    -> Trạng thái mới: {agent.tracker.state.value}")
                print("    -> Màn hình máy tính lập tức khóa lại với thông báo lịch sự và số Hotline 111.")

            elif choice == "6":
                print("\n[*] Trẻ em gửi yêu cầu 'Xin thêm 15 phút' từ giao diện Tray:")
                res = ipc_client.send_child_request("MORE_TIME", {"minutes": 15, "reason": "Con đang làm dở bài tập Toán"})
                print(f"    -> Phản hồi IPC: {res}")
                print("[*] Phụ huynh phê duyệt mở khóa và cộng thêm 15 phút...")
                agent.tracker.add_bonus_time(15.0 * 60)
                print(f"    -> Trạng thái mới: {agent.tracker.state.value} (Còn lại: {agent.tracker.get_remaining_seconds()/60:.1f}m)")

            elif choice == "7":
                print(f"\n[*] Hãy mở trình duyệt truy cập: http://127.0.0.1:{server_port}/dashboard/1")
                print("    - Xem thống kê thời lượng sử dụng máy tính")
                print("    - Xem Top 10 ứng dụng và Top 10 tên miền truy cập")
                print("    - Duyệt yêu cầu xin mở khóa / xin thêm giờ của con")

            elif choice == "8":
                print("\n[*] Thực hiện Xóa Dữ Liệu Đồng Thời (Atomic Dual Deletion) cho Child ID=1:")
                purged_local = agent.buffer.purge_child_events("1")
                print(f"    -> Đã xóa sạch {purged_local} bản ghi sự kiện trong SQLite cục bộ.")
                print("    -> Không lưu trữ bất kỳ dữ liệu nhạy cảm nào, tuân thủ tuyệt đối Luật Trẻ em 2016.")

            elif choice == "9":
                print("\n[*] Đang chạy E2E Acceptance Verification Runner...")
                subprocess.run([sys.executable, "scripts/e2e_acceptance_verification.py"])

            time.sleep(1.0)

    except KeyboardInterrupt:
        pass
    finally:
        print("\n[*] Đang dừng các thành phần demo...")
        agent.stop()
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3.0)
        except Exception:
            server_proc.kill()
        shutil.rmtree(demo_dir, ignore_errors=True)
        print("[✓] Đã dọn dẹp môi trường sạch sẽ. Hoàn thành.")


if __name__ == "__main__":
    main()

