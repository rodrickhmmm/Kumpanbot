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
        results.append({
            "title": e.get("title"),
            "url": e.get("webpage_url") or e.get("url"),
            "duration": e.get("duration"),
            "uploader": e.get("uploader"),
            "id": e.get("id"),
            "thumbnail": e.get("thumbnail"),
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