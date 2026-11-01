"""
OpenGuard Kids — Quick DNS Proxy Tester
Kiểm tra nhanh kết quả phân giải của DNS Proxy (hỗ trợ cả port 53 và port 5353).
Cách dùng:
    python scripts/test_dns.py [tên_miền] [--port 5353|53]
Ví dụ:
    python scripts/test_dns.py bet88.com
    python scripts/test_dns.py www.google.com
    python scripts/test_dns.py use-application-dns.net
    python scripts/test_dns.py hcmus.edu.vn
"""

import sys
import socket

# Đảm bảo in tiếng Việt mượt mà trên console Windows (tránh lỗi CP1252)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from dnslib import DNSRecord, RCODE, QTYPE

def test_dns(domain: str, host: str = "127.0.0.1", port: int = 5353):
    # Tự động thử port 5353 trước, nếu không phản hồi thì thử port 53
    ports_to_try = [port] if port != 5353 else [5353, 53]
    
    for p in ports_to_try:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2.0)
            q = DNSRecord.question(domain)
            s.sendto(q.pack(), (host, p))
            raw_data, _ = s.recvfrom(4096)
            resp = DNSRecord.parse(raw_data)
            s.close()
            
            print(f"\n=======================================================")
            print(f"  KẾT QUẢ PHÂN GIẢI CHO: {domain}")
            print(f"  DNS Server Đang Test:  {host}:{p}")
            print(f"=======================================================")
            
            rcode_name = RCODE.get(resp.header.rcode, str(resp.header.rcode))
            if rcode_name == "NXDOMAIN":
                print("  Trạng thái: NXDOMAIN (Tên miền không tồn tại / Bị vô hiệu hóa)")
                print("  Ý nghĩa:    Đạt chuẩn Canary DoH (ép trình duyệt tắt DNS mã hóa).")
                return

            if not resp.rr:
                print("  Trạng thái: Trả về rỗng (NOERROR, không có bản ghi)")
                return

            for rr in resp.rr:
                rtype = QTYPE.get(rr.rtype, str(rr.rtype))
                rdata = str(rr.rdata)
                print(f"  Loại bản ghi: {rtype:<6} | Giá trị: {rdata}")
                
                if rdata == "127.0.0.1":
                    print("  => KẾT LUẬN: ĐÃ CHẶN THÀNH CÔNG! Bẻ hướng về Blockpage nội bộ 127.0.0.1.")
                elif "forcesafesearch" in rdata:
                    print("  => KẾT LUẬN: ÉP BUỘC SAFESEARCH THÀNH CÔNG! Trỏ sang forcesafesearch.")
                else:
                    print("  => KẾT LUẬN: TÊN MIỀN HỢP LỆ! Phân giải IP thực tế thông suốt.")
            return
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Lỗi khi gửi query tới port {p}: {e}")
            return
            
    print(f"\n[LỖI] Không nhận được phản hồi từ DNS Proxy tại 127.0.0.1 trên các cổng {ports_to_try}!")
    print("Vui lòng kiểm tra xem Terminal 2 (Agent Service) đã được bật chưa.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "play.sub.bet88.com"
    port_arg = 5353
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port_arg = int(sys.argv[idx + 1])
    test_dns(target, port=port_arg)
