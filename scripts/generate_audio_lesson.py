import asyncio
import re
import sys
import edge_tts

def markdown_to_spoken_text(md_content: str) -> str:
    """Chuyển đổi văn bản Markdown thành lời đọc tự nhiên cho TTS với chuẩn hóa phát âm thuật ngữ tiếng Anh."""
    text = md_content

    # Loại bỏ frontmatter hoặc comment metadata ở đầu file
    text = re.sub(r'> \*\*.*?\n', '', text)
    
    # Loại bỏ các alert box như > [!TIP]
    text = re.sub(r'>\s*\[!.*?\]', '', text)
    text = re.sub(r'>', '', text)

    # Chuyển đổi markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Chuyển đổi mã code inline `code` -> code
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Bỏ dấu định dạng đậm / nghiêng **text** -> text
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)

    # Bỏ các khối mã block ``` ... ```
    text = re.sub(r'```[\s\S]*?```', '', text)

    # Bỏ các ký tự tiêu đề markdown #, ##, ###
    text = re.sub(r'#+\s*', '', text)

    # Bỏ các đường kẻ ngang ---
    text = re.sub(r'---+', '', text)

    # Chuẩn hóa bảng Markdown: Bỏ dòng phân cách | :--- | :--- |
    text = re.sub(r'\|[\s\-:]+\|[\s\-:|]+', '', text)
    text = text.replace('|', ' . ')

    # Thay thế ký tự emoji / bullet points
    text = text.replace('❌', 'Không:')
    text = text.replace('🔹', '')
    text = text.replace('—', ' - ')
    text = text.replace('–', ' - ')
    text = re.sub(r'^[ \t]*[\*\-]\s+', '', text, flags=re.MULTILINE)

    # BẢNG TỪ ĐIỂN PHIÊN ÂM THUẬT NGỮ TIẾNG ANH CHO GIỌNG ĐỌC TIẾNG VIỆT
    phonetic_map = [
        # Hệ điều hành & Kiến trúc
        (r'\bSession 0 Isolation\b', 'cơ chế cô lập Phiên Không'),
        (r'\bSession 0\b', 'Phiên Không'),
        (r'\bSession 1\b', 'Phiên Một'),
        (r'\bSession\b', 'Phiên'),
        (r'\bNT AUTHORITY\\LocalSystem\b', 'tài khoản đặc quyền tối cao Lô-cồ Xít-từm'),
        (r'\bLocalSystem\b', 'Lô-cồ Xít-từm'),
        (r'\bWindows Service\b', 'dịch vụ chạy ngầm Uyn-đao Xơ-vít'),
        (r'\bService Control Manager\b', 'Trình quản lý dịch vụ S-C-M'),
        (r'\bSCM\b', 'S-C-M'),
        (r'\bTask Manager\b', 'trình quản lý tác vụ Tác Mê-nơ-giơ'),
        (r'\bTaskbar\b', 'thanh tác vụ Tác-ba'),
        (r'\bEnd Task\b', 'kết thúc tác vụ En Tát'),
        (r'\bShatter Attack\b', 'cuộc tấn công chiếm quyền Sát-tơ Ơ-tắc'),
        (r'\bSystem Tray Icon\b', 'biểu tượng khay hệ thống'),
        (r'\bTray UI\b', 'giao diện khay hệ thống Trei U-I'),
        (r'\bTray\b', 'khay hệ thống'),

        # Thư viện & Công cụ
        (r'\bpsutil\b', 'thư viện P-S-U-T-I-L'),
        (r'\bpywin32\b', 'thư viện Pai-Uyn-ba mươi hai'),
        (r'\bwin32serviceutil\b', 'mô-đun Uyn ba mươi hai Xơ-vít'),
        (r'\bSHA-256\b', 'mã băm S-H-A hai trăm năm mươi sáu'),
        (r'\bhashlib\.sha256\b', 'hàm băm S-H-A hai trăm năm mươi sáu'),
        (r'\bFastAPI\b', 'Pha-sờ-tơ A-P-I'),
        (r'\bSQLite WAL\b', 'cơ sở dữ liệu Éch-Q-L-Lai chế độ Van'),
        (r'\bSQLite\b', 'Éch-Q-L-Lai'),
        (r'\bWebSocket\b', 'kết nối Vép Sốc-két'),
        (r'\bHTMX\b', 'H-T-M-X'),

        # Giao tiếp IPC & Mạng
        (r'\bInter-Process Communication\b', 'giao tiếp liên tiến trình I-P-C'),
        (r'\bIPC\b', 'kênh giao tiếp I-P-C'),
        (r'\bNamed Pipe\b', 'đường ống định danh Nêm Pai'),
        (r'\bLoopback HTTP\b', 'giao thức Lúp-bách H-T-T-P nội bộ'),
        (r'\bBearer Token\b', 'mã xác thực Be-rơ Tô-kừn'),
        (r'\bToken\b', 'mã khóa Tô-kừn'),
        (r'\bUDP Port 53\b', 'cổng U-D-P năm mươi ba'),
        (r'\bDNS Proxy\b', 'máy chủ ủy quyền D-N-S Proxy'),
        (r'\bDNS\b', 'D-N-S'),
        (r'\b127\.0\.0\.1\b', 'một hai bảy chấm không chấm không chấm một'),

        # Giám sát & Chống gian lận
        (r'\bAnti-Tamper\b', 'chống gian lận'),
        (r'\bAnti-tamper\b', 'chống gian lận'),
        (r'\bClock Rollback Attack\b', 'chiêu trò gian lận lùi đồng hồ hệ thống'),
        (r'\bGetLastInputInfo\b', 'hàm Gét Lát In-pút In-pho'),
        (r'\bWTSRegisterSessionNotification\b', 'hàm theo dõi trạng thái khóa màn hình'),
        (r'\bWTS_SESSION_LOCK\b', 'sự kiện khóa màn hình'),
        (r'\bActive Time\b', 'thời gian sử dụng thực tế'),
        (r'\bIdle Time\b', 'thời gian nhàn rỗi'),
        (r'\bIdle Detection\b', 'nhận biết máy nhàn rỗi'),
        (r'\bIdle\b', 'nhàn rỗi'),
        (r'\bproc\.terminate\(\)\b', 'lệnh yêu cầu kết thúc tiến trình'),
        (r'\bproc\.kill\(\)\b', 'lệnh buộc dừng tiến trình'),
        (r'\bproc\.exe\(\)\b', 'lấy đường dẫn file thực thi'),
        (r'\bproc\.name\(\)\.lower\(\)\b', 'lấy tên file tiến trình'),

        # Số đặc biệt
        (r'\b111\b', 'một một một'),
    ]

    for pattern, replacement in phonetic_map:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Xóa các dòng trống thừa
    lines = [line.strip() for line in text.splitlines()]
    clean_text = '\n'.join([line for line in lines if line])

    return clean_text

async def synthesize_chunk(text: str, voice: str = "vi-VN-HoaiMyNeural", max_retries: int = 5) -> bytes:
    for attempt in range(max_retries):
        try:
            comm = edge_tts.Communicate(text, voice)
            data = b''
            async for chunk in comm.stream():
                if chunk['type'] == 'audio':
                    data += chunk['data']
            if data:
                return data
        except Exception as e:
            wait_time = 3 * (attempt + 1)
            print(f'Lần {attempt+1}/{max_retries} gặp lỗi ({e}). Đợi {wait_time}s rồi thử lại...')
            await asyncio.sleep(wait_time)
    raise RuntimeError('Không thể tổng hợp giọng đọc sau các lần thử lại.')

async def generate_lesson_audio(md_path: str, mp3_path: str, voice: str = "vi-VN-HoaiMyNeural"):
    print(f"Đang đọc nội dung bài học từ: {md_path}")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    spoken_text = markdown_to_spoken_text(md_content)
    
    # Chia thành các đoạn khoảng 800 - 1100 ký tự để giảm số lần gọi kết nối
    paragraphs = [p.strip() for p in spoken_text.split('\n') if p.strip()]
    sections = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) < 950:
            current += " " + p if current else p
        else:
            sections.append(current)
            current = p
    if current:
        sections.append(current)

    print(f"Tổng số phân đoạn cần đọc: {len(sections)}")
    audio_full = b''
    for idx, sec in enumerate(sections):
        print(f"Đang tổng hợp phân đoạn {idx+1}/{len(sections)} ({len(sec)} ký tự)...")
        chunk = await synthesize_chunk(sec, voice=voice)
        audio_full += chunk
        await asyncio.sleep(2.0)

    with open(mp3_path, 'wb') as f:
        f.write(audio_full)
    print(f"Đã tạo thành công file âm thanh bài giảng: {mp3_path}")

if __name__ == "__main__":
    md_file = sys.argv[1] if len(sys.argv) > 1 else "audio_lessons/hoc_phan_02.md"
    mp3_file = sys.argv[2] if len(sys.argv) > 2 else "audio_lessons/hoc_phan_02.mp3"
    asyncio.run(generate_lesson_audio(md_file, mp3_file))
