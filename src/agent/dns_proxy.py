"""
OpenGuard Kids — Local DNS Proxy Engine (UDP)
Implements Requirements:
  - F2.3: Local DNS proxy on 127.0.0.1:53, root domain & wildcard subdomain blocking
  - F2.4: 6-Group taxonomy & study mode whitelist
  - F2.5: SafeSearch CNAME rewriting (forcesafesearch.google.com, strict.bing.com)
Architecture Specification: docs/ARCHITECTURE.md Section 6.1
"""

import errno
import socket
import threading
import time
import logging
from typing import Set, Dict, Optional, Callable

from dnslib import DNSRecord, RR, QTYPE, RCODE, A, CNAME

from src.common.constants import (
    DEFAULT_DNS_HOST,
    DEFAULT_DNS_PORT,
    DEFAULT_UPSTREAM_DNS,
    DEFAULT_UPSTREAM_PORT,
    FALLBACK_UPSTREAM_DNS,
    CANARY_DOMAIN,
    SAFESEARCH_MAP,
    DEFAULT_BLOCKPAGE_HOST,
    HEURISTIC_KEYWORDS,
    PERMANENT_WHITELIST,
)

logger = logging.getLogger("OGK.DNSProxy")


class DNSProxy:
    """
    Local DNS Proxy listening on UDP (default 127.0.0.1:53).
    Acts as the primary network-level filter for OpenGuard Kids.
    """

    def __init__(
        self,
        listen_host: str = DEFAULT_DNS_HOST,
        listen_port: int = DEFAULT_DNS_PORT,
        upstream_host: str = DEFAULT_UPSTREAM_DNS,
        upstream_port: int = DEFAULT_UPSTREAM_PORT,
        blockpage_ip: str = DEFAULT_BLOCKPAGE_HOST,
        on_blocked_callback: Optional[Callable[[str, str], None]] = None,
        fallback_port: int = 5353,
    ):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.fallback_port = fallback_port
        self.port = listen_port
        self.upstream_host = upstream_host
        self.upstream_port = upstream_port
        self.blockpage_ip = blockpage_ip
        self.on_blocked_callback = on_blocked_callback

        # Dynamic Rule Sets (thread-safe reads/writes)
        self._lock = threading.Lock()
        self.blocklist: Set[str] = set()
        self.whitelist: Set[str] = set()
        self.study_mode: bool = False  # If True, only whitelist is permitted

        # In-memory DNS Cache: { (domain, qtype): (response_bytes, expire_timestamp) }
        self._cache: Dict[tuple, tuple] = {}

        # Sockets and thread control
        self._server_socket: Optional[socket.socket] = None
        self._is_running = False
        self._thread: Optional[threading.Thread] = None

    def add_blocked_domains(self, domains: list[str]) -> None:
        """Add domains to the local blocklist."""
        with self._lock:
            for d in domains:
                self.blocklist.add(d.strip().lower().rstrip("."))

    def remove_blocked_domains(self, domains: list[str]) -> None:
        """Remove domains from the local blocklist."""
        with self._lock:
            for d in domains:
                self.blocklist.discard(d.strip().lower().rstrip("."))

    def add_whitelisted_domains(self, domains: list[str]) -> None:
        """Add domains to the whitelist."""
        with self._lock:
            for d in domains:
                self.whitelist.add(d.strip().lower().rstrip("."))

    def set_study_mode(self, enabled: bool) -> None:
        """Enable or disable Strict Study Mode (Whitelist-only)."""
        with self._lock:
            self.study_mode = enabled

    def _matches_domain_set(self, domain: str, target_set: Set[str]) -> bool:
        """
        Check if domain matches exact or parent domain in target_set.
        e.g., 'sub.game.com' matches 'game.com' or '*.game.com'.
        """
        if domain in target_set or f"*.{domain}" in target_set:
            return True
        parts = domain.split(".")
        for i in range(1, len(parts)):
            parent = ".".join(parts[i:])
            if parent in target_set or f"*.{parent}" in target_set:
                return True
        return False

    def _matches_heuristics(self, domain: str) -> bool:
        """Check if domain contains any blacklisted suspicious keywords."""
        for kw in HEURISTIC_KEYWORDS:
            if kw in domain:
                return True
        return False

    def handle_query(self, raw_data: bytes) -> bytes:
        """
        Process a single raw DNS request payload and produce a DNS response payload.
        """
        try:
            request = DNSRecord.parse(raw_data)
        except Exception as e:
            logger.warning(f"Malformed DNS request: {e}")
            reply = DNSRecord()
            reply.header.rcode = RCODE.FORMERR
            return reply.pack()

        qname = str(request.q.qname).rstrip(".").lower()
        qtype = request.q.qtype

        # -------------------------------------------------------------
        # 1. Canary Domain Probe (IETF standard: use-application-dns.net)
        # Instructs browsers to disable DoH and fallback to OS DNS
        # -------------------------------------------------------------
        if qname == CANARY_DOMAIN:
            reply = request.reply()
            reply.header.rcode = RCODE.NXDOMAIN
            return reply.pack()

        # -------------------------------------------------------------
        # 2. Permanent Whitelist (Emergency hotline 111, Education portals)
        # -------------------------------------------------------------
        if self._matches_domain_set(qname, PERMANENT_WHITELIST):
            return self._forward_to_upstream(raw_data, qname, qtype)

        # -------------------------------------------------------------
        # 3. Google / Bing / DuckDuckGo SafeSearch CNAME Rewriting
        # -------------------------------------------------------------
        if qname in SAFESEARCH_MAP and qtype in (QTYPE.A, QTYPE.AAAA):
            target_vip = SAFESEARCH_MAP[qname]
            reply = request.reply()
            reply.add_answer(
                RR(
                    qname,
                    QTYPE.CNAME,
                    rdata=CNAME(f"{target_vip}."),
                    ttl=300,
                )
            )
            # Resolve target VIP to ensure browser gets immediate A record
            try:
                vip_ips = socket.gethostbyname_ex(target_vip)[2]
                for ip in vip_ips:
                    reply.add_answer(
                        RR(target_vip, QTYPE.A, rdata=A(ip), ttl=300)
                    )
            except Exception:
                pass
            return reply.pack()

        # -------------------------------------------------------------
        # 4. Strict Study Mode (Whitelist-only enforcement)
        # -------------------------------------------------------------
        with self._lock:
            in_study_mode = self.study_mode
            is_whitelisted = self._matches_domain_set(qname, self.whitelist)
            is_blocked = self._matches_domain_set(qname, self.blocklist)

        if in_study_mode and not is_whitelisted:
            if self.on_blocked_callback:
                self.on_blocked_callback(qname, "STUDY_MODE_UNLISTED")
            return self._create_blocked_response(request, qname, qtype)

        # -------------------------------------------------------------
        # 5. Explicit Policy Blocklist Check
        # -------------------------------------------------------------
        if is_blocked:
            if self.on_blocked_callback:
                self.on_blocked_callback(qname, "POLICY_BLOCKLIST")
            return self._create_blocked_response(request, qname, qtype)

        # -------------------------------------------------------------
        # 6. Heuristic Keyword Matching (Suspicious/Gambling/Adult)
        # -------------------------------------------------------------
        if not is_whitelisted and self._matches_heuristics(qname):
            if self.on_blocked_callback:
                self.on_blocked_callback(qname, "HEURISTIC_KEYWORD")
            return self._create_blocked_response(request, qname, qtype)

        # -------------------------------------------------------------
        # 7. Permitted Domain: Forward to Protective Upstream (1.1.1.3)
        # -------------------------------------------------------------
        return self._forward_to_upstream(raw_data, qname, qtype)

    def _create_blocked_response(
        self, request: DNSRecord, qname: str, qtype: int
    ) -> bytes:
        """Generate response redirecting blocked domain to the local blockpage."""
        reply = request.reply()
        if qtype == QTYPE.A:
            reply.add_answer(
                RR(qname, QTYPE.A, rdata=A(self.blockpage_ip), ttl=60)
            )
        else:
            reply.header.rcode = RCODE.NXDOMAIN
        return reply.pack()

    def _forward_to_upstream(
        self, raw_data: bytes, qname: str, qtype: int
    ) -> bytes:
        """
        Forward query to upstream DNS resolver (Cloudflare Family 1.1.1.3 or Google 8.8.8.8).
        Uses in-memory cache to reduce latency and bandwidth.
        """
        cache_key = (qname, qtype)
        now = time.time()

        # Check Cache
        with self._lock:
            if cache_key in self._cache:
                cached_bytes, expire_at = self._cache[cache_key]
                if now < expire_at:
                    # Update transaction ID to match current query
                    try:
                        resp = DNSRecord.parse(cached_bytes)
                        req = DNSRecord.parse(raw_data)
                        resp.header.id = req.header.id
                        return resp.pack()
                    except Exception:
                        pass

        # Forward query to Upstream
        for upstream in (self.upstream_host, FALLBACK_UPSTREAM_DNS):
            try:
                client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                client_sock.settimeout(2.0)
                client_sock.sendto(raw_data, (upstream, self.upstream_port))
                response_bytes, _ = client_sock.recvfrom(4096)
                client_sock.close()

                # Cache response for 60 seconds
                with self._lock:
                    self._cache[cache_key] = (response_bytes, now + 60.0)

                return response_bytes
            except Exception as e:
                logger.debug(f"Upstream query to {upstream} failed: {e}")
                continue

        # If all upstreams fail, return SERVFAIL
        try:
            req = DNSRecord.parse(raw_data)
            reply = req.reply()
            reply.header.rcode = RCODE.SERVFAIL
            return reply.pack()
        except Exception:
            return b""

    def start(self) -> None:
        """Start the DNS Proxy server in a background thread."""
        if self._is_running:
            return

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._server_socket.bind((self.listen_host, self.listen_port))
            self.port = self.listen_port
        except (PermissionError, OSError) as e:
            is_perm = (
                isinstance(e, PermissionError)
                or (isinstance(e, OSError) and getattr(e, "errno", None) == errno.EACCES)
                or getattr(e, "winerror", None) == 10013
            )
            if is_perm and self.listen_port != self.fallback_port:
                logger.warning(
                    f"[WARN] Permission denied binding UDP port {self.listen_port}; "
                    f"falling back to unprivileged port {self.fallback_port} for local testing"
                )
                try:
                    self._server_socket.close()
                except Exception:
                    pass
                self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.listen_port = self.fallback_port
                self.port = self.fallback_port
                self._server_socket.bind((self.listen_host, self.listen_port))
            else:
                try:
                    self._server_socket.close()
                except Exception:
                    pass
                self._server_socket = None
                raise

        self._server_socket.settimeout(1.0)
        self._is_running = True

        self._thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="OGK-DNSProxy-Worker"
        )
        self._thread.start()
        logger.info(
            f"OpenGuard Kids DNS Proxy started on {self.listen_host}:{self.listen_port}"
        )

    def _listen_loop(self) -> None:
        while self._is_running:
            try:
                data, client_addr = self._server_socket.recvfrom(4096)
                # Dispatch handler in worker thread or handle synchronously
                reply_bytes = self.handle_query(data)
                if reply_bytes and self._server_socket:
                    self._server_socket.sendto(reply_bytes, client_addr)
            except socket.timeout:
                continue
            except Exception as e:
                if self._is_running:
                    logger.error(f"Error in DNS listen loop: {e}")

    def stop(self) -> None:
        """Stop the DNS Proxy server cleanly."""
        self._is_running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("OpenGuard Kids DNS Proxy stopped cleanly.")

