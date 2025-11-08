import asyncio
from typing import List, Dict, Optional
import yt_dlp

class _SilentLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

YTDL_BASE_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "logger": _SilentLogger(),
    "default_search": "auto",
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "noplaylist": True,
    "source_address": "0.0.0.0",
    "extract_flat": False,
    "extractor_args": {
        "youtube": {
            "player_client": ["android"],  # fallback
        }
    },
    "format_sort": ["asr", "abr", "tbr", "acodec", "ext"],
}

def _opts_with_player_client(player: str) -> Dict:
    opts = dict(YTDL_BASE_OPTS)
    ea = dict(opts.get("extractor_args", {}))
    yt = dict(ea.get("youtube", {}))
    yt["player_client"] = [player]
    ea["youtube"] = yt
    opts["extractor_args"] = ea
    return opts

YTDL_SEARCH_OPTS = {
    **YTDL_BASE_OPTS,
    "extract_flat": "discard_in_playlist",
}

def _is_url(query: str) -> bool:
    return query.startswith("http://") or query.startswith("https://")

async def _extract_info_with_opts(query: str, opts: Dict, download: bool = False) -> Dict:
    def _runner():
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(query, download=download)
    return await asyncio.to_thread(_runner)

async def extract_info(query: str, download: bool = False) -> Dict:
    try:
        info = await _extract_info_with_opts(query, _opts_with_player_client("web_creator"), download)
        if info:
            fmts = info.get("formats") or []
            if any(f.get("acodec") not in (None, "none") and f.get("url") for f in fmts):
                return info
    except Exception:
        pass
    try:
        return await _extract_info_with_opts(query, _opts_with_player_client("android"), download)
    except Exception:
        return {}

async def search_yt(query: str, limit: int = 5) -> List[Dict]:
    q = f"ytsearch{limit}:{query}"
    def _runner():
        with yt_dlp.YoutubeDL(YTDL_SEARCH_OPTS) as ydl:
            return ydl.extract_info(q, download=False)
    data = await asyncio.to_thread(_runner)
    entries = data.get("entries", []) if data else []
    results = []
    for e in entries:
        if not e:
            continue
        
        # Get thumbnail - try multiple sources
        thumbnail = e.get("thumbnail")
        if not thumbnail:
            thumbnails = e.get("thumbnails", [])
            if thumbnails:
                # Get highest quality thumbnail
                thumbnail = thumbnails[-1].get("url") if thumbnails else None
        
        # If still no thumbnail, construct YouTube thumbnail URL
        if not thumbnail and e.get("id"):
            thumbnail = f"https://i.ytimg.com/vi/{e.get('id')}/maxresdefault.jpg"
        
        results.append({
            "title": e.get("title"),
            "url": e.get("webpage_url") or e.get("url"),
            "duration": e.get("duration"),
            "uploader": e.get("uploader"),
            "id": e.get("id"),
            "thumbnail": thumbnail,
        })
    return results

async def search_soundcloud(query: str, limit: int = 5) -> List[Dict]:
    """Search SoundCloud for tracks"""
    q = f"scsearch{limit}:{query}"
    def _runner():
        with yt_dlp.YoutubeDL(YTDL_SEARCH_OPTS) as ydl:
            return ydl.extract_info(q, download=False)
    data = await asyncio.to_thread(_runner)
    entries = data.get("entries", []) if data else []
    results = []
    for e in entries:
        if not e:
            continue
        results.append({
            "title": e.get("title"),
            "url": e.get("webpage_url") or e.get("url"),
            "duration": e.get("duration"),
            "uploader": e.get("uploader"),
            "id": e.get("id"),
            "thumbnail": e.get("thumbnail"),
        })
    return results

def is_soundcloud_url(url: str) -> bool:
    """Check if URL is from SoundCloud"""
    return "soundcloud.com" in url.lower()

def is_playlist_url(url: str) -> bool:
    """Check if URL is a playlist"""
    url_lower = url.lower()
    return ("list=" in url_lower or 
            "/playlist" in url_lower or 
            "/sets/" in url_lower)  # SoundCloud playlists

async def get_playlist_tracks(url: str) -> List[Dict]:
    """Extract all tracks from a playlist URL"""
    import re
    
    # If URL has &list= parameter, extract playlist ID and create clean playlist URL
    if "list=" in url:
        match = re.search(r'[?&]list=([^&]+)', url)
        if match:
            playlist_id = match.group(1)
            # Create clean playlist URL
            url = f"https://www.youtube.com/playlist?list={playlist_id}"
            print(f"[PLAYLIST DEBUG] Converted to playlist URL: {url}")
    
    # Use extract_flat to get playlist items without downloading full info
    opts = dict(YTDL_BASE_OPTS)
    opts["extract_flat"] = True  # Get basic info quickly
    opts["noplaylist"] = False  # Allow playlists!
    opts["yes_playlist"] = True  # Force playlist extraction
    
    def _runner():
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    
    try:
        data = await asyncio.to_thread(_runner)
    except Exception as e:
        print(f"[PLAYLIST ERROR] Failed to extract playlist: {e}")
        return []
    
    if not data:
        print("[PLAYLIST ERROR] No data returned from extraction")
        return []
    
    # If it's a playlist, get entries
    entries = data.get("entries", [])
    print(f"[PLAYLIST DEBUG] Got {len(entries)} entries, type: {data.get('_type')}")
    
    if not entries and data.get("_type") != "playlist":
        # Not a playlist, just a single video
        print("[PLAYLIST ERROR] Not a playlist or no entries found")
        return []
    
    tracks = []
    for entry in entries:
        if not entry:
            continue
        
        # Build proper YouTube URL
        video_id = entry.get("id")
        if video_id and "youtube.com" in url.lower():
            video_url = f"https://www.youtube.com/watch?v={video_id}"
        else:
            video_url = entry.get("url") or entry.get("webpage_url") or entry.get("id")
        
        if not video_url:
            continue
            
        # Build track info from flat extraction
        track = {
            "title": entry.get("title") or "Unknown",
            "url": video_url,
            "duration": entry.get("duration"),
            "uploader": entry.get("uploader") or entry.get("channel"),
            "thumbnail": entry.get("thumbnail") or (entry.get("thumbnails", [{}])[0].get("url") if entry.get("thumbnails") else None),
            "id": video_id,
        }
        tracks.append(track)
    
    print(f"[PLAYLIST DEBUG] Successfully extracted {len(tracks)} tracks")
    
    return tracks

async def get_track_info(link_or_id: str) -> Optional[Dict]:
    """Get full track info including title, thumbnail, stream URL, etc."""
    info = await extract_info(link_or_id, download=False)
    if not info:
        return None
    if "entries" in info:
        info = next((e for e in info["entries"] if e), None)
        if not info:
            return None
    
    # Get best audio format
    fmts = info.get("formats") or []
    audio_formats = [f for f in fmts if f.get("acodec") not in (None, "none") and f.get("url")]
    stream_url = None
    if audio_formats:
        def keyfmt(f):
            return (f.get("abr") or 0, f.get("asr") or 0, f.get("tbr") or 0)
        best = max(audio_formats, key=keyfmt)
        stream_url = best.get("url")
    else:
        stream_url = info.get("url")
    
    return {
        "title": info.get("title"),
        "url": info.get("webpage_url") or link_or_id,
        "stream_url": stream_url,
        "duration": info.get("duration"),
        "uploader": info.get("uploader"),
        "thumbnail": info.get("thumbnail"),
        "id": info.get("id"),
    }

async def get_stream_url(link_or_id: str) -> Optional[str]:
    info = await extract_info(link_or_id, download=False)
    if not info:
        return None
    if "entries" in info:
        info = next((e for e in info["entries"] if e), None)
        if not info:
            return None
    fmts = info.get("formats") or []
    audio_formats = [f for f in fmts if f.get("acodec") not in (None, "none") and f.get("url")]
    if audio_formats:
        def keyfmt(f):
            return (f.get("abr") or 0, f.get("asr") or 0, f.get("tbr") or 0)
        best = max(audio_formats, key=keyfmt)
        return best.get("url")
    return info.get("url")