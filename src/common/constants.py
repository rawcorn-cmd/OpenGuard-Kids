"""
OpenGuard Kids — Common System Constants
"""

# DNS Defaults
DEFAULT_DNS_HOST = "127.0.0.1"
DEFAULT_DNS_PORT = 53
DEFAULT_TEST_DNS_PORT = 1053

# Upstream Clean DNS (Cloudflare 1.1.1.1 for Families: malware + adult blocking)
DEFAULT_UPSTREAM_DNS = "1.1.1.3"
DEFAULT_UPSTREAM_PORT = 53
FALLBACK_UPSTREAM_DNS = "8.8.8.8"

# IETF & Browser Canary Domain (triggers DoH disablement in Firefox / Chromium)
CANARY_DOMAIN = "use-application-dns.net"

# SafeSearch CNAME Virtual IPs / Targets
SAFESEARCH_MAP = {
    "google.com": "forcesafesearch.google.com",
    "www.google.com": "forcesafesearch.google.com",
    "bing.com": "strict.bing.com",
    "www.bing.com": "strict.bing.com",
    "duckduckgo.com": "safe.duckduckgo.com",
    "www.duckduckgo.com": "safe.duckduckgo.com",
}

# Blockpage HTTP Server
DEFAULT_BLOCKPAGE_HOST = "127.0.0.1"
DEFAULT_BLOCKPAGE_PORT = 8080

# Service-to-Tray IPC
DEFAULT_IPC_HOST = "127.0.0.1"
DEFAULT_IPC_PORT = 8765
TOKEN_FILE_NAME = "ipc_secret.token"

# Default Heuristic Keywords (Suspicious gambling, adult, piracy)
HEURISTIC_KEYWORDS = [
    "bet88", "casino", "tai-xiu", "nohu", "kubet", "thabet",
    "phimsex", "xxx", "porn", "xnxx", "xvideos",
    "hack-game", "free-robux", "crack-full",
]

# Permanent Whitelist (Emergency hotlines, school portals)
PERMANENT_WHITELIST = {
    "treem.gov.vn",      # Cục Trẻ em - Hotline 111
    "tongdai111.vn",     # Tổng đài Quốc gia Bảo vệ Trẻ em 111
    "edu.vn",            # Mạng giáo dục Việt Nam
    "hcmus.edu.vn",      # Trường ĐH Khoa học Tự nhiên
    "vnuhcm.edu.vn",     # ĐHQG TP.HCM
}

