NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

SEARCH_RESULTS = 5
REACT_TIMEOUT = 15  

FFMPEG_BEFORE_OPTS = (
    "-nostdin "
    "-reconnect 1 -reconnect_streamed 1 -reconnect_at_eof 1 "
    "-reconnect_delay_max 5 -rw_timeout 15000000"
)
FFMPEG_OPTS = "-vn -loglevel warning"  

IDLE_LEAVE_SECONDS = 300  
