import asyncio
import html
import re
import unicodedata
from difflib import SequenceMatcher
from urllib.parse import quote, urljoin

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


def _strip_diacritics(text: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch))


def _normalize(text: str) -> str:
    text = _strip_diacritics((text or "").strip().lower())
    text = re.sub(r"\(.*?\)", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _slugify(text: str) -> str:
    """Turn a name into the kebab-case slug format textypisni.youradio.cz uses in its URLs."""
    normalized = _normalize(text)
    return re.sub(r"\s+", "-", normalized).strip("-")


def _clean_name(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"\s*\((feat\.|ft\.|with)\b.*?\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*\[(feat\.|ft\.|with)\b.*?\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


def _duration_text(seconds: float | int | None) -> str:
    if seconds is None:
        return "N/A"
    try:
        total_seconds = int(float(seconds))
    except Exception:
        return "N/A"
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:d}:{seconds:02d}"


def _make_embed(title: str, description: str, color: discord.Color | int = discord.Color.purple()) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color)


_NO_ARTIST_TIP = (
    "Bez interpreta se prohledává jen **LRCLIB** (umí hledat podle názvu) a "
    "**KaraokeTexty.cz** (u kterého kvůli jejich ochraně proti botům skoro vždy "
    "selže vyhledání). **Youradio** a **lyrics.ovh** interpreta vyžadují, takže se "
    "teď vůbec nezkusily.\n\nZkus: `/lyrics Interpret - Píseň`"
)


def _html_to_text(source: str) -> str:
    """Flatten HTML into a single normalized-whitespace line. Good for locating markers,
    bad for preserving line breaks (use _html_to_lines for that)."""
    source = re.sub(r"(?is)<script.*?>.*?</script>", " ", source)
    source = re.sub(r"(?is)<style.*?>.*?</style>", " ", source)
    source = re.sub(r"(?is)<[^>]+>", " ", source)
    source = html.unescape(source)
    source = source.replace("\xa0", " ")
    return re.sub(r"\s+", " ", source).strip()


def _html_to_lines(source: str) -> str:
    """Flatten HTML into text but keep line breaks where the markup implies them
    (<br>, </p>, </div>, </li>, headings). Needed so multi-verse lyrics don't turn
    into a single unreadable paragraph."""
    source = re.sub(r"(?is)<script.*?>.*?</script>", " ", source)
    source = re.sub(r"(?is)<style.*?>.*?</style>", " ", source)
    source = re.sub(r"(?i)<br\s*/?>", "\n", source)
    source = re.sub(r"(?i)</(p|div|li|h[1-6])\s*>", "\n", source)
    source = re.sub(r"(?is)<[^>]+>", "", source)
    source = html.unescape(source)
    source = source.replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in source.splitlines()]
    return "\n".join(line for line in lines if line)


def _extract_karaoke_lyrics(source: str) -> str | None:
    text = _html_to_text(source)
    match = re.search(r"0:00\s*/\s*0:00\s*(.*?)\s*Ohodnoť karaoke text:", text, flags=re.IGNORECASE)
    if not match:
        return None
    lyrics = match.group(1).strip()
    return lyrics or None


def _extract_youradio_lyrics(source: str) -> str | None:
    """Youradio's song pages render: breadcrumb -> H1 title -> "Skrýt/Zobrazit
    překlad písně" toggle -> the lyrics -> an "Interpret" info box. We use the
    toggle text and the "Interpret" heading as start/end anchors.

    NOTE: this is based on the page structure as observed in July 2026. If
    Youradio changes their template, these two marker strings are the only
    things that should need updating.
    """
    text = _html_to_lines(source)

    start_match = re.search(r"(?:Skrýt|Zobrazit)\s+překlad\s+písně", text, flags=re.IGNORECASE)
    if not start_match:
        return None

    remainder = text[start_match.end():]
    end_match = re.search(r"\bInterpret\b", remainder)
    lyrics_block = remainder[: end_match.start()] if end_match else remainder
    lyrics_block = lyrics_block.strip("› \n")
    lyrics_block = "\n".join(line for line in lyrics_block.splitlines() if line.strip())

    return lyrics_block or None


def _chunk_text(text: str, limit: int = 3600) -> list[str]:
    chunks: list[str] = []
    current = ""
    for raw_line in (text or "").splitlines():
        line = raw_line.rstrip()
        candidate = line if not current else f"{current}\n{line}"
        if len(candidate) <= limit:
            current = candidate
            continue

        if current:
            chunks.append(current)

        while len(line) > limit:
            chunks.append(line[:limit])
            line = line[limit:]

        current = line

    if current:
        chunks.append(current)

    return chunks or [""]


def _score_match(requested_artist: str, requested_title: str, item: dict) -> float:
    item_artist = _normalize(str(item.get("artistName") or ""))
    item_title = _normalize(str(item.get("trackName") or item.get("name") or ""))
    requested_artist_norm = _normalize(requested_artist)
    requested_title_norm = _normalize(requested_title)

    score = 0.0
    if requested_artist_norm and item_artist:
        score += SequenceMatcher(None, requested_artist_norm, item_artist).ratio() * 2.0
    if requested_title_norm and item_title:
        score += SequenceMatcher(None, requested_title_norm, item_title).ratio() * 3.0

    if requested_artist_norm and item_artist and requested_artist_norm == item_artist:
        score += 2.0
    if requested_title_norm and item_title and requested_title_norm == item_title:
        score += 3.0
    if item.get("plainLyrics"):
        score += 0.5
    if item.get("instrumental"):
        score -= 1.0
    return score


async def _search_lrclib(session: aiohttp.ClientSession, artist: str, title: str) -> dict | None:
    params = {"artist_name": artist, "track_name": title}
    async with session.get("https://lrclib.net/api/search", params=params) as response:
        if response.status != 200:
            return None
        try:
            payload = await response.json(content_type=None)
        except Exception:
            return None

    if not isinstance(payload, list) or not payload:
        return None

    best_item = max(
        (item for item in payload if isinstance(item, dict)),
        key=lambda item: _score_match(artist, title, item),
        default=None,
    )
    if not best_item:
        return None

    lyrics = best_item.get("plainLyrics") or best_item.get("syncedLyrics")
    if not isinstance(lyrics, str) or not lyrics.strip():
        return None

    return {
        "source": "LRCLIB",
        "artist": str(best_item.get("artistName") or artist).strip() or artist,
        "title": str(best_item.get("trackName") or best_item.get("name") or title).strip() or title,
        "album": str(best_item.get("albumName") or "").strip() or None,
        "duration": best_item.get("duration"),
        "lyrics": html.unescape(lyrics).strip(),
    }


async def _search_lyrics_ovh(session: aiohttp.ClientSession, artist: str, title: str) -> dict | None:
    url = f"https://api.lyrics.ovh/v1/{quote(artist, safe='')}/{quote(title, safe='')}"
    async with session.get(url) as response:
        if response.status != 200:
            return None
        try:
            payload = await response.json(content_type=None)
        except Exception:
            return None

    lyrics = payload.get("lyrics") if isinstance(payload, dict) else None
    if not isinstance(lyrics, str) or not lyrics.strip():
        return None

    return {
        "source": "lyrics.ovh",
        "artist": artist,
        "title": title,
        "album": None,
        "duration": None,
        "lyrics": html.unescape(lyrics).strip(),
    }


_YOURADIO_BASE = "https://textypisni.youradio.cz"


async def _fetch_youradio_page(session: aiohttp.ClientSession, url: str) -> str | None:
    try:
        async with session.get(url, allow_redirects=True) as response:
            if response.status != 200:
                return None
            return await response.text(errors="ignore")
    except Exception:
        return None


async def _find_youradio_song_url(session: aiohttp.ClientSession, artist_slug: str, title: str) -> str | None:
    """Scan the artist's song-list page (first page only) for the closest matching
    song slug. Used as a fallback when the direct '/nezarazeno/' guess 404s,
    e.g. because the song sits under a real album slug instead."""
    artist_html = await _fetch_youradio_page(session, f"{_YOURADIO_BASE}/{artist_slug}")
    if not artist_html:
        return None

    title_slug = _slugify(title)
    if not title_slug:
        return None

    pattern = re.compile(rf'href="(/{re.escape(artist_slug)}/[^"]+?/([^"/]+))"', re.IGNORECASE)
    best_url, best_score = None, -1.0
    for href, song_slug in pattern.findall(artist_html):
        score = SequenceMatcher(None, title_slug, song_slug.lower()).ratio()
        if score > best_score:
            best_score, best_url = score, href

    if not best_url or best_score < 0.55:
        return None

    return urljoin(_YOURADIO_BASE + "/", best_url)


async def _search_youradio(session: aiohttp.ClientSession, artist: str, title: str) -> dict | None:
    """textypisni.youradio.cz has a large, non-blocked Czech/international lyrics
    database. It needs both artist and title to build a URL (no public search
    endpoint), so this source is skipped when the artist is unknown."""
    if not artist or not title:
        return None

    artist_slug = _slugify(artist)
    title_slug = _slugify(title)
    if not artist_slug or not title_slug:
        return None

    # Fast path: most standalone / lesser-known tracks sit in the "nezarazeno"
    # (uncategorized) bucket, so this alone resolves a lot of cases in one request.
    direct_url = f"{_YOURADIO_BASE}/{artist_slug}/nezarazeno/{title_slug}"
    page_html = await _fetch_youradio_page(session, direct_url)
    page_url = direct_url
    lyrics = _extract_youradio_lyrics(page_html) if page_html else None

    if not lyrics:
        # Slower path: the song is filed under a real album slug we can't guess,
        # so scan the artist's page for the closest matching link instead.
        found_url = await _find_youradio_song_url(session, artist_slug, title)
        if not found_url:
            return None
        page_html = await _fetch_youradio_page(session, found_url)
        if not page_html:
            return None
        lyrics = _extract_youradio_lyrics(page_html)
        page_url = found_url

    if not lyrics:
        return None

    return {
        "source": "Youradio texty písní",
        "artist": artist,
        "title": title,
        "album": None,
        "duration": None,
        "lyrics": lyrics,
        "url": page_url,
    }


async def _search_karaoketexty(session: aiohttp.ClientSession, artist: str, title: str) -> dict | None:
    """KaraokeTexty.cz sits behind an anti-bot "ověř, že nejsi robot" wall that a
    plain HTTP client can't pass, so this will almost always come back empty.
    Kept only as a cheap last-resort attempt in case that ever changes."""
    query = " ".join(part for part in [artist.strip(), title.strip()] if part)
    search_url = f"https://www.karaoketexty.cz/search?q={quote(query, safe='')}"

    async with session.get(search_url) as response:
        if response.status != 200:
            return None
        search_html = await response.text(errors="ignore")

    candidate_urls: list[str] = []
    for match in re.finditer(r'href="([^"]*?/texty-pisni/[^"]+)"', search_html, flags=re.IGNORECASE):
        candidate_urls.append(html.unescape(match.group(1)))

    if not candidate_urls:
        return None

    requested_artist_norm = _normalize(artist)
    requested_title_norm = _normalize(title)
    best_url = None
    best_score = -1.0

    for candidate_url in candidate_urls[:25]:
        candidate_text = _normalize(candidate_url.rsplit("/", 1)[-1].replace("-", " "))
        score = SequenceMatcher(None, requested_title_norm, candidate_text).ratio() * 3.0
        if requested_artist_norm and requested_artist_norm in candidate_url.lower():
            score += 2.0
        if requested_title_norm and requested_title_norm in candidate_text:
            score += 2.0
        if score > best_score:
            best_score = score
            best_url = candidate_url

    if not best_url:
        return None

    if "/texty-pisni/" in best_url:
        karaoke_url = best_url.replace("/texty-pisni/", "/karaoke/", 1)
    else:
        karaoke_url = best_url

    karaoke_url = urljoin("https://www.karaoketexty.cz/", karaoke_url)

    async with session.get(karaoke_url) as response:
        if response.status != 200:
            return None
        karaoke_html = await response.text(errors="ignore")

    lyrics = _extract_karaoke_lyrics(karaoke_html)
    if not lyrics:
        return None

    return {
        "source": "KaraokeTexty.cz",
        "artist": artist,
        "title": title,
        "album": None,
        "duration": None,
        "lyrics": lyrics,
        "url": karaoke_url,
    }


async def _find_lyrics(session: aiohttp.ClientSession, artist: str, title: str) -> dict | None:
    variants: list[tuple[str, str]] = []
    base_artist = _clean_name(artist)
    base_title = _clean_name(title)
    if base_artist:
        variants.append((base_artist, base_title))

        alt_artist = re.sub(r"\b(feat\.|ft\.|with)\b.*$", "", base_artist, flags=re.IGNORECASE).strip()
        alt_title = re.sub(r"\s*\([^)]*\)$", "", base_title).strip()
        if (alt_artist, alt_title) not in variants:
            variants.append((alt_artist, alt_title))

        swapped = (base_title, base_artist)
        if swapped not in variants:
            variants.append(swapped)
    else:
        variants.append(("", base_title))
        alt_title = re.sub(r"\s*\([^)]*\)$", "", base_title).strip()
        if alt_title and ("", alt_title) not in variants:
            variants.append(("", alt_title))

    for current_artist, current_title in variants:
        if not current_title:
            continue

        # LRCLIB is the only source that can meaningfully search on title alone,
        # so it's always worth trying even when we don't have an artist.
        result = await _search_lrclib(session, current_artist, current_title)
        if result:
            return result

        if not current_artist:
            continue

        result = await _search_youradio(session, current_artist, current_title)
        if result:
            return result

        result = await _search_lyrics_ovh(session, current_artist, current_title)
        if result:
            return result

    # KaraokeTexty.cz is a near-guaranteed miss (see _search_karaoketexty), so it
    # only gets a single attempt with the cleaned-up query instead of once per variant.
    fallback_artist, fallback_title = variants[0]
    if fallback_title:
        result = await _search_karaoketexty(session, fallback_artist, fallback_title)
        if result:
            return result

    return None


class Lyrics(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="lyrics", description="Vyhledá text písně a vypíše ho v embedu (piš nejlépe ve formátu Interpret - Píseň).")
    @app_commands.describe(
        song="Jedno pole pro hledání písně, ideálně ve formátu Interpret - Píseň.",
    )
    async def lyrics(self, interaction: discord.Interaction, song: str):
        await interaction.response.defer(thinking=True)

        search_query = (song or "").strip()
        if not search_query:
            await interaction.followup.send(
                embed=_make_embed(
                    "Chybí zadání",
                    "Napiš prosím název písně, ideálně ve formátu Interpret - Píseň.",
                    discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        interpret = ""
        pisen = search_query
        for separator in (" - ", " — ", " | ", " : "):
            if separator in search_query:
                interpret, pisen = search_query.split(separator, 1)
                interpret = interpret.strip()
                pisen = pisen.strip()
                break

        timeout = aiohttp.ClientTimeout(total=15)
        headers = {"User-Agent": "Kumpanbot/lyrics command"}

        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                result = await _find_lyrics(session, interpret, pisen)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                embed=_make_embed(
                    "Vypršel čas",
                    "Vyhledávání textu písně vypršelo. Zkus to prosím znovu.",
                    discord.Color.red(),
                ),
                ephemeral=True,
            )
            return
        except Exception as error:
            await interaction.followup.send(
                embed=_make_embed(
                    "Chyba při vyhledávání",
                    f"Nepodařilo se vyhledat lyrics: {type(error).__name__}: {error}",
                    discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        if not result:
            not_found_embed = _make_embed(
                "Text nenalezen",
                "Text písně jsem nenašel v žádném z dostupných zdrojů (LRCLIB, Youradio, "
                "lyrics.ovh, KaraokeTexty.cz). Zkus prosím přesnější zadání, "
                "ideálně ve formátu Interpret - Píseň.",
                discord.Color.orange(),
            )
            if not interpret:
                not_found_embed.add_field(name="⚠️ Chybí interpret", value=_NO_ARTIST_TIP, inline=False)
            await interaction.followup.send(embed=not_found_embed, ephemeral=True)
            return

        lyrics_text = result["lyrics"].strip()
        if not lyrics_text:
            await interaction.followup.send(
                embed=_make_embed(
                    "Prázdný výsledek",
                    "Nalezený text písně je prázdný.",
                    discord.Color.orange(),
                ),
                ephemeral=True,
            )
            return

        chunks = _chunk_text(lyrics_text)
        max_embeds = 10
        if len(chunks) > max_embeds:
            chunks = chunks[: max_embeds - 1] + ["Text je delší než limit Discordu, takže zobrazuju jen první část."]

        embeds: list[discord.Embed] = []
        total_chunks = len(chunks)
        for index, chunk in enumerate(chunks, start=1):
            title = f"🎵 {result['artist']} - {result['title']}"
            if total_chunks > 1:
                title = f"{title} ({index}/{total_chunks})"

            embed = discord.Embed(
                title=title,
                description=chunk,
                color=discord.Color.purple(),
            )

            if index == 1:
                embed.add_field(name="Autor", value=result["artist"], inline=True)
                embed.add_field(name="Skladba", value=result["title"], inline=True)
                embed.add_field(name="Zdroj textu skladby", value=result["source"], inline=True)
                if result.get("duration"):
                    embed.add_field(name="Délka skladby", value=_duration_text(result.get("duration")), inline=True)
                if not interpret:
                    embed.add_field(
                        name="💡 Tip",
                        value="Zadej i interpreta (`Interpret - Píseň`) — odemkne to další zdroje "
                        "(Youradio, lyrics.ovh) a hledání bude přesnější.",
                        inline=False,
                    )
                embed.set_footer(text=f"Hledáno z dotazu: {song}")
            else:
                embed.set_footer(text=f"Zdroj: {result['source']}")

            embeds.append(embed)

        await interaction.followup.send(embeds=embeds)


async def setup(bot: commands.Bot):
    await bot.add_cog(Lyrics(bot))