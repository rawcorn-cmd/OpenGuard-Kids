"""
Unit tests for OpenGuard Kids Local Blockpage HTTP Server and DNS Proxy Integration.
"""

import httpx
from src.agent.blockpage import BlockpageManager
from src.agent.dns_proxy import DNSProxy
from dnslib import DNSRecord, QTYPE


def test_blockpage_status_and_html_rendering():
    # Use ephemeral port 0 for isolation
    manager = BlockpageManager(host="127.0.0.1", port=0)
    manager.start()

    try:
        base_url = f"http://127.0.0.1:{manager.port}"

        # 1. Test status endpoint
        with httpx.Client(base_url=base_url) as client:
            resp = client.get("/api/status")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"

            # 2. Test HTML rendering with query params
            resp_html = client.get("/?domain=gambling-test.com&reason=Co-bac-truc-tuyen")
            assert resp_html.status_code == 200
            assert "text/html" in resp_html.headers["content-type"]
            body = resp_html.text
            assert "gambling-test.com" in body
            assert "Co-bac-truc-tuyen" in body
            assert "111" in body  # Hotline 111 Cục Trẻ em (NT3/NT4)
            assert "Nội Dung Đang Được Giữ An Toàn" in body

    finally:
        manager.stop()


def test_blockpage_child_unblock_request_callback():
    captured_requests = []

    def on_request(domain: str, reason: str):
        captured_requests.append((domain, reason))

    manager = BlockpageManager(host="127.0.0.1", port=0, on_unblock_request=on_request)
    manager.start()

    try:
        base_url = f"http://127.0.0.1:{manager.port}"
        with httpx.Client(base_url=base_url) as client:
            payload = {
                "domain": "khanacademy.org",
                "child_message": "Em can vao hoc toan lop 8 a",
            }
            resp = client.post("/api/request-unblock", json=payload)
            assert resp.status_code == 200
            assert resp.json()["status"] == "success"

        assert len(captured_requests) == 1
        assert captured_requests[0][0] == "khanacademy.org"
        assert captured_requests[0][1] == "Em can vao hoc toan lop 8 a"

    finally:
        manager.stop()


def test_dns_proxy_integration_with_blockpage():
    # Verify that DNSProxy resolves blocked domains to the blockpage IP
    proxy = DNSProxy(
        listen_host="127.0.0.1",
        listen_port=0,
        blockpage_ip="127.0.0.1",
    )
    proxy.add_blocked_domains(["bad-gambling.com"])

    # Construct DNS query for bad-gambling.com
    query = DNSRecord.question("bad-gambling.com", "A")
    raw_response = proxy.handle_query(query.pack())
    response = DNSRecord.parse(raw_response)

    # Must return A record pointing to 127.0.0.1
    assert len(response.rr) == 1
    assert str(response.rr[0].rdata) == "127.0.0.1"
