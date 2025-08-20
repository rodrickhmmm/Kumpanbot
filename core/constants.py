# core/constants.py

# Emojis chọn kết quả
NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

# Số lượng kết quả search & timeout chọn
SEARCH_RESULTS = 5
REACT_TIMEOUT = 20  # giây

# FFmpeg options: tăng độ bền khi stream
FFMPEG_BEFORE_OPTS = (
    "-nostdin "
    "-reconnect 1 -reconnect_streamed 1 -reconnect_at_eof 1 "
    "-reconnect_delay_max 5 -rw_timeout 15000000"
)
FFMPEG_OPTS = "-vn -loglevel warning"  # đổi 'error' nếu muốn yên tĩnh hơn

# Thời gian idle liên tục trước khi auto rời (chỉ khi KHÔNG còn nhạc & queue trống)
IDLE_LEAVE_SECONDS = 300  # 5 phút
