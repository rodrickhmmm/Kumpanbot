# cogs/play.py
import asyncio
import contextlib
import discord
from discord.ext import commands
from typing import Optional
from utils.ytdl import search_yt, get_stream_url
from core.music_manager import MusicManager, Track
from core.constants import NUMBER_EMOJIS, SEARCH_RESULTS, REACT_TIMEOUT

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

def fmt_duration(seconds) -> str:
    if seconds is None:
        return "N/A"
    try:
        seconds = int(float(seconds))
    except Exception:
        return "N/A"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"

class Play(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx: commands.Context, *, query: Optional[str] = None):
        """o!play <tên bài> -> gợi ý top 5 + chọn bằng reaction
           o!play <link YouTube> -> phát ngay"""
        if not query:
            return await ctx.reply("Dùng: `o!play <tên bài hát>` hoặc `o!play <link YouTube>`")

        mgr = get_manager(self.bot)
        await mgr.ensure_voice(ctx)

        # Nếu là link -> phát luôn
        if query.startswith(("http://", "https://")):
            stream = await get_stream_url(query)
            if not stream:
                return await ctx.reply("Không lấy được stream từ link này.")
            # Lấy meta để hiển thị
            results = await search_yt(query, limit=1)
            meta = results[0] if results else {"title": "Unknown", "thumbnail": None, "url": query}
            track = Track(
                title=meta.get("title") or "Unknown",
                url=query,
                stream_url=stream,
                requested_by=ctx.author,
                web_url=meta.get("url") or query,
                thumbnail=meta.get("thumbnail")
            )
            await mgr.add_track(ctx, track)
            return await ctx.reply(f"🎵 Đã thêm: **{track.title}**")

        # Tìm kiếm top 5
        results = await search_yt(query, limit=SEARCH_RESULTS)
        if not results:
            return await ctx.reply("Không tìm thấy kết quả nào.")

        embed = discord.Embed(
            title=f"Kết quả cho: {query}",
            description="\n".join(
                f"{i+1}. **{r['title']}** · `{'N/A' if r['duration'] is None else fmt_duration(r['duration'])}`"
                for i, r in enumerate(results)
            ),
            color=discord.Color.green()
        )
        thumb = results[0].get("thumbnail")
        if thumb:
            embed.set_thumbnail(url=thumb)
        embed.set_footer(text=f"Chọn bằng reaction 1️⃣–{len(results)} trong {REACT_TIMEOUT}s")

        msg = await ctx.reply(embed=embed)
        for i in range(len(results)):
            await msg.add_reaction(NUMBER_EMOJIS[i])

        def check(reaction: discord.Reaction, user: discord.User):
            return (
                reaction.message.id == msg.id
                and str(reaction.emoji) in NUMBER_EMOJIS[:len(results)]
                and user.id == ctx.author.id
            )

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=REACT_TIMEOUT, check=check)
        except asyncio.TimeoutError:
            with contextlib.suppress(discord.Forbidden):
                await msg.clear_reactions()
            return await ctx.send("⏱️ Hết thời gian chọn.")

        index = NUMBER_EMOJIS.index(str(reaction.emoji))
        chosen = results[index]
        stream = await get_stream_url(chosen["url"])
        if not stream:
            return await ctx.reply("Không lấy được stream từ video này.")

        track = Track(
            title=chosen["title"],
            url=chosen["url"],
            stream_url=stream,
            requested_by=ctx.author,
            web_url=chosen["url"],
            thumbnail=chosen.get("thumbnail")
        )
        await mgr.add_track(ctx, track)

        confirm = discord.Embed(
            title="Đã thêm vào hàng đợi",
            description=f"**{track.title}**",
            color=discord.Color.blurple()
        )
        if track.thumbnail:
            confirm.set_thumbnail(url=track.thumbnail)
        confirm.add_field(name="Yêu cầu bởi", value=ctx.author.mention)
        await ctx.reply(embed=confirm)

async def setup(bot: commands.Bot):
    await bot.add_cog(Play(bot))
