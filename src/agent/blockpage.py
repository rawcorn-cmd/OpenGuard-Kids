"""
OpenGuard Kids — Local Blockpage HTTP Server
Serves a polite, educational, non-punitive block notice (NT3/NT4)
and provides a child agency interface for reporting false positives or requesting access.
"""

from __future__ import annotations

import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Callable, Optional
from urllib.parse import urlparse, parse_qs

from src.common.constants import DEFAULT_BLOCKPAGE_HOST, DEFAULT_BLOCKPAGE_PORT

logger = logging.getLogger("OpenGuardKids.Blockpage")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenGuard Kids — Thông Báo Điều Hướng An Toàn</title>
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --accent: #f59e0b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: var(--bg); color: var(--text-main); display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 20px; }
        .card { background: var(--card-bg); border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01); border: 1px solid var(--border); max-width: 520px; width: 100%; padding: 32px; text-align: center; }
        .icon-shield { width: 64px; height: 64px; margin: 0 auto 16px; background: #eff6ff; color: var(--primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; }
        h1 { font-size: 22px; font-weight: 700; margin-bottom: 8px; color: #0f172a; }
        p.subtitle { color: var(--text-muted); font-size: 14px; margin-bottom: 24px; line-height: 1.5; }
        .domain-box { background: #f1f5f9; padding: 12px 16px; border-radius: 8px; font-family: monospace; font-size: 15px; color: #334155; margin-bottom: 20px; word-break: break-all; border: 1px solid #cbd5e1; }
        .reason-badge { display: inline-block; background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600; margin-bottom: 24px; }
        .form-group { text-align: left; margin-bottom: 16px; }
        label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: #475569; }
        textarea { width: 100%; border: 1px solid var(--border); border-radius: 8px; padding: 10px; font-size: 14px; resize: vertical; min-height: 80px; }
        textarea:focus { outline: none; border-color: var(--primary); ring: 2px solid #bfdbfe; }
        button.btn-submit { background: var(--primary); color: white; border: none; padding: 12px 20px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; width: 100%; transition: background 0.2s; }
        button.btn-submit:hover { background: var(--primary-hover); }
        .footer-hotline { margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border); font-size: 12px; color: var(--text-muted); }
        .hotline-highlight { color: #dc2626; font-weight: 700; }
        .success-message { display: none; background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; padding: 14px; border-radius: 8px; font-size: 14px; line-height: 1.4; margin-top: 16px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon-shield">&#128737;</div>
        <h1>Nội Dung Đang Được Giữ An Toàn</h1>
        <p class="subtitle">Trang web này nằm trong danh mục hạn chế theo thỏa thuận sử dụng Internet gia đình nhằm đảm bảo không gian học tập và an toàn cho bạn.</p>

        <div class="domain-box" id="domain-display">{domain}</div>
        <div class="reason-badge">{reason}</div>

        <form id="requestForm" onsubmit="submitRequest(event)">
            <div class="form-group">
                <label for="reasonInput">Bạn cần truy cập trang này để học tập hoặc cho rằng bị chặn nhầm?</label>
                <textarea id="reasonInput" placeholder="Ví dụ: Em cần tìm tài liệu cho môn Lịch sử..."></textarea>
            </div>
            <button type="submit" class="btn-submit" id="btnSubmit">Gửi yêu cầu cho Phụ huynh</button>
        </form>

        <div class="success-message" id="successMsg">
            &#10004; Yêu cầu của bạn đã được gửi tới ứng dụng của Cha/Mẹ. Bạn hãy đợi một chút nhé!
        </div>

        <div class="footer-hotline">
            Đồng hành cùng sự an toàn của trẻ em &bull; Tổng đài Quốc gia Bảo vệ Trẻ em: <span class="hotline-highlight">111</span>
        </div>
    </div>

    <script>
        function submitRequest(e) {
            e.preventDefault();
            const reason = document.getElementById("reasonInput").value.trim();
            const domain = document.getElementById("domain-display").innerText;
            const btn = document.getElementById("btnSubmit");

            btn.disabled = true;
            btn.innerText = "Đang gửi...";

            fetch("/api/request-unblock", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ domain: domain, child_message: reason || "Yêu cầu mở trang web phục vụ học tập" })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById("requestForm").style.display = "none";
                document.getElementById("successMsg").style.display = "block";
            })
            .catch(err => {
                alert("Không thể gửi yêu cầu lúc này. Vui lòng thử lại sau.");
                btn.disabled = false;
                btn.innerText = "Gửi yêu cầu cho Phụ huynh";
            });
        }
    </script>
</body>
</html>
"""


class BlockpageRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        # Suppress noisy standard HTTP access logs
        return

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "service": "OpenGuardKids-Blockpage"}')
            return

        # Extract domain from Host header or query param
        query_params = parse_qs(parsed_url.query)
        target_domain = query_params.get("domain", [None])[0]
        if not target_domain:
            host_header = self.headers.get("Host", "trang-web-bi-chan.com")
            target_domain = host_header.split(":")[0]

        reason = query_params.get("reason", ["Nội dung không phù hợp với lứa tuổi"])[0]

        html = HTML_TEMPLATE.replace("{domain}", target_domain).replace("{reason}", reason)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/request-unblock":
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length)

            try:
                data = json.loads(post_body.decode("utf-8"))
                domain = data.get("domain", "unknown")
                child_message = data.get("child_message", "")

                server: BlockpageServer = self.server  # type: ignore
                if server.on_unblock_request:
                    server.on_unblock_request(domain, child_message)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status": "success", "message": "Request submitted"}')
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


class BlockpageServer(HTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        RequestHandlerClass,
        on_unblock_request: Optional[Callable[[str, str], None]] = None,
    ):
        self.allow_reuse_address = True
        self.on_unblock_request = on_unblock_request
        super().__init__(server_address, RequestHandlerClass)


class BlockpageManager:
    """
    Manages the lifecycle of the local Blockpage HTTP server.
    """

    def __init__(
        self,
        host: str = DEFAULT_BLOCKPAGE_HOST,
        port: int = DEFAULT_BLOCKPAGE_PORT,
        on_unblock_request: Optional[Callable[[str, str], None]] = None,
    ):
        self.host = host
        self.port = port
        self.on_unblock_request = on_unblock_request
        self.server: Optional[BlockpageServer] = None
        self._thread: Optional[threading.Thread] = None
        self.is_running = False

    def start(self) -> None:
        if self.is_running:
            return

        self.server = BlockpageServer(
            (self.host, self.port),
            BlockpageRequestHandler,
            on_unblock_request=self.on_unblock_request,
        )
        self.port = self.server.server_address[1]  # In case port 0 was passed

        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()
        self.is_running = True
        logger.info("Blockpage HTTP Server running at http://%s:%d", self.host, self.port)

    def stop(self) -> None:
        if not self.is_running or not self.server:
            return

        self.server.shutdown()
        self.server.server_close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self.is_running = False
        logger.info("Blockpage HTTP Server stopped.")


LocalBlockPageServer = BlockpageManager


