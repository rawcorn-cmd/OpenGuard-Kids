"""
Unit Tests for OpenGuard Kids DNS Proxy
Tests all policy rules, SafeSearch CNAME rewriting, Canary Domain, and Heuristics.
"""

import socket
import time
import pytest
from dnslib import DNSRecord, QTYPE, RCODE

from src.agent.dns_proxy import DNSProxy
from src.common.constants import (
    CANARY_DOMAIN,
    DEFAULT_TEST_DNS_PORT,
    DEFAULT_BLOCKPAGE_HOST,
)


@pytest.fixture
def dns_proxy():
    """Create a DNSProxy instance with sample blocklists and callback."""
    blocked_events = []

    def on_blocked(domain: str, reason: str):
        blocked_events.append((domain, reason))

    proxy = DNSProxy(
        listen_host="127.0.0.1",
        listen_port=DEFAULT_TEST_DNS_PORT,
        blockpage_ip=DEFAULT_BLOCKPAGE_HOST,
        on_blocked_callback=on_blocked,
    )
    proxy.add_blocked_domains(["badgame.com", "gamblingportal.net", "*.evilsub.org"])
    proxy.blocked_events = blocked_events
    return proxy


def test_canary_domain_returns_nxdomain(dns_proxy):
    """Canary Domain use-application-dns.net must return NXDOMAIN to disable browser DoH."""
    query = DNSRecord.question(CANARY_DOMAIN)
    raw_response = dns_proxy.handle_query(query.pack())
    response = DNSRecord.parse(raw_response)

    assert response.header.rcode == RCODE.NXDOMAIN
    assert len(response.rr) == 0


def test_blocklist_redirection_to_blockpage(dns_proxy):
    """Explicitly blacklisted domain must be redirected to the local Blockpage IP."""
    query = DNSRecord.question("badgame.com")
    raw_response = dns_proxy.handle_query(query.pack())
    response = DNSRecord.parse(raw_response)

    assert response.header.rcode == RCODE.NOERROR
    assert len(response.rr) == 1
    assert str(response.rr[0].rdata) == DEFAULT_BLOCKPAGE_HOST
    assert len(dns_proxy.blocked_events) == 1
    assert dns_proxy.blocked_events[0] == ("badgame.com", "POLICY_BLOCKLIST")


def test_wildcard_subdomain_blocking(dns_proxy):
    """Subdomains of a wildcard blocklist rule must also be intercepted."""
    query = DNSRecord.question("play.evilsub.org")
    raw_response = dns_proxy.handle_query(query.pack())
    response = DNSRecord.parse(raw_response)

    assert len(response.rr) == 1
    assert str(response.rr[0].rdata) == DEFAULT_BLOCKPAGE_HOST


def test_heuristic_keyword_blocking(dns_proxy):
    """Unknown domain containing gambling or adult keywords must be blocked via heuristics."""
    query = DNSRecord.question("tai-xiu-online-2026.net")
    raw_response = dns_proxy.handle_query(query.pack())
    response = DNSRecord.parse(raw_response)

    assert len(response.rr) == 1
    assert str(response.rr[0].rdata) == DEFAULT_BLOCKPAGE_HOST
    assert any(ev[1] == "HEURISTIC_KEYWORD" for ev in dns_proxy.blocked_events)


def test_safesearch_cname_rewriting(dns_proxy):
    """Google and Bing searches must have CNAME rewritten to forcesafesearch."""
    query = DNSRecord.question("google.com")
    raw_response = dns_proxy.handle_query(query.pack())
    response = DNSRecord.parse(raw_response)

    # First record should be CNAME to forcesafesearch.google.com
    cname_found = False
    for rr in response.rr:
        if rr.rtype == QTYPE.CNAME and "forcesafesearch" in str(rr.rdata):
            cname_found = True
            break
    assert cname_found, "Google SafeSearch CNAME record was not found in response"


def test_permanent_whitelist(dns_proxy):
    """Child protection hotline (treem.gov.vn) must never be blocked."""
    query = DNSRecord.question("treem.gov.vn")
    # Even if accidentally added to blocklist
    dns_proxy.add_blocked_domains(["treem.gov.vn"])
    raw_response = dns_proxy.handle_query(query.pack())
    response = DNSRecord.parse(raw_response)

    # Permanent whitelist bypasses blocklist and does not point to blockpage
    if response.rr:
        assert str(response.rr[0].rdata) != DEFAULT_BLOCKPAGE_HOST


def test_study_mode_whitelist_only(dns_proxy):
    """In Study Mode, any domain not explicitly whitelisted must be blocked."""
    dns_proxy.set_study_mode(True)
    dns_proxy.add_whitelisted_domains(["khanacademy.org"])

    # Permitted domain
    q_safe = DNSRecord.question("khanacademy.org")
    raw_safe = dns_proxy.handle_query(q_safe.pack())
    # Should not trigger block callback
    assert not any(ev[0] == "khanacademy.org" for ev in dns_proxy.blocked_events)

    # Unlisted random domain
    q_random = DNSRecord.question("random-entertainment-portal.xyz")
    raw_random = dns_proxy.handle_query(q_random.pack())
    resp_random = DNSRecord.parse(raw_random)

    assert len(resp_random.rr) == 1
    assert str(resp_random.rr[0].rdata) == DEFAULT_BLOCKPAGE_HOST
    assert any(ev[0] == "random-entertainment-portal.xyz" and ev[1] == "STUDY_MODE_UNLISTED" for ev in dns_proxy.blocked_events)


def test_live_udp_socket_resolution():
    """Start the proxy server on port 1053 and send live UDP DNS queries."""
    proxy = DNSProxy(listen_host="127.0.0.1", listen_port=1053)
    proxy.add_blocked_domains(["blockme.local"])

    proxy.start()
    try:
        # Give thread a moment to bind
        time.sleep(0.1)

        # Create client socket and send query
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(2.0)

        query = DNSRecord.question("blockme.local")
        client.sendto(query.pack(), ("127.0.0.1", 1053))

        resp_data, _ = client.recvfrom(512)
        resp = DNSRecord.parse(resp_data)

        assert len(resp.rr) == 1
        assert str(resp.rr[0].rdata) == "127.0.0.1"
        client.close()
    finally:
        proxy.stop()

