import asyncio
import contextlib
import discord
from discord.ext import commands
from typing import Optional
from utils.ytdl import search_yt, search_soundcloud, get_stream_url, get_track_info, is_soundcloud_url, is_playlist_url, get_playlist_tracks
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
    from discord import app_commands

    @app_commands.command(name="hraj", description="Přehraje skladbu podle názvu nebo odkazu (YouTube, SoundCloud).")
    async def play_slash(self, interaction: discord.Interaction, skladba: str):
        user = interaction.user
        await interaction.response.defer()
        
        # Check if user has the specific ID and send message
        if user.id == 1150085087451435102:
            await interaction.followup.send("Nemáš práva na používání tohoto příkazu!!", ephemeral=True)

        if not isinstance(user, discord.Member):
            await interaction.followup.send("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        mgr = get_manager(self.bot)
        
        # Direct link (YouTube or SoundCloud)
        if skladba.startswith(("http://", "https://")):
            await mgr.ensure_voice(interaction)
            
            # Check if it's a playlist
            if is_playlist_url(skladba):
                playlist_tracks = await get_playlist_tracks(skladba)
                if not playlist_tracks:
                    await interaction.followup.send("Nemůžu načíst playlist.", ephemeral=True)
                    return
                
                # Send initial message
                embed = discord.Embed(
                    title="📝 Přidávám playlist",
                    description=f"Načítám **{len(playlist_tracks)}** skladeb...",
                    color=discord.Color.purple()
                )
                await interaction.followup.send(embed=embed)
                
                # Add all tracks to queue
                added_count = 0
                for track_data in playlist_tracks:
                    try:
                        # Get stream URL for each track
                        track_info = await get_track_info(track_data["url"])
                        if not track_info or not track_info.get("stream_url"):
                            continue
                        
                        track = Track(
                            title=track_info.get("title") or track_data.get("title") or "Neznámá skladba",
                            url=track_data["url"],
                            stream_url=track_info["stream_url"],
                            requested_by=user,
                            web_url=track_info.get("url") or track_data["url"],
                            thumbnail=track_info.get("thumbnail") or track_data.get("thumbnail")
                        )
                        await mgr.add_track(interaction, track, start_if_idle=(added_count == 0))
                        added_count += 1
                    except Exception:
                        continue
                
                if added_count > 0 and user.id != 1150085087451435102:
                    embed = discord.Embed(
                        title="✅ Playlist přidán",
                        description=f"Přidáno **{added_count}** skladeb do fronty",
                        color=discord.Color.purple()
                    )
                    embed.set_footer(text=f"Požádal {user.display_name}", icon_url=user.display_avatar.url)
                    await interaction.channel.send(embed=embed)
                return
            
            # Single track
            # Get full track info (title, thumbnail, stream URL in one call)
            track_info = await get_track_info(skladba)
            if not track_info or not track_info.get("stream_url"):
                await interaction.followup.send("Nemůžu přehrát skladbu z tohoto odkazu.", ephemeral=True)
                return
            
            track = Track(
                title=track_info.get("title") or "Neznámá skladba",
                url=skladba,
                stream_url=track_info["stream_url"],
                requested_by=user,
                web_url=track_info.get("url") or skladba,
                thumbnail=track_info.get("thumbnail")
            )
            await mgr.add_track(interaction, track)
            # Don't send success message if it's the specific user
            if user.id != 1150085087451435102:
                is_sc = is_soundcloud_url(skladba)
                source_name = "SoundCloud" if is_sc else "YouTube"
                embed = discord.Embed(
                    title="🎵 Přidána skladba",
                    description=f"**{track.title}**",
                    color=discord.Color.purple(),
                    url=track.web_url
                )
                if track.thumbnail:
                    embed.set_thumbnail(url=track.thumbnail)
                embed.add_field(name="Zdroj", value=source_name, inline=True)
                embed.add_field(name="Požádal", value=user.mention, inline=True)
                await interaction.followup.send(embed=embed)
            return

        # Search - try SoundCloud if it looks like it might be from there, otherwise YouTube
        results = await search_yt(skladba, limit=1)
        if not results:
            await interaction.followup.send("Nenalezeny žádné výsledky.", ephemeral=True)
            return
        chosen = results[0]
        await mgr.ensure_voice(interaction)
        stream = await get_stream_url(chosen["url"])
        if not stream:
            await interaction.followup.send("Nemůžu přehrát skladbu z tohoto odkazu.", ephemeral=True)
            return
        track = Track(
            title=chosen["title"],
            url=chosen["url"],
            stream_url=stream,
            requested_by=user,
            web_url=chosen["url"],
            thumbnail=chosen.get("thumbnail")
        )
        await mgr.add_track(interaction, track)
        # Don't send success message if it's the specific user
        if user.id != 1150085087451435102:
            embed = discord.Embed(
                title="Skladba přidána do fronty",
                description=f"**{track.title}**",
                color=discord.Color.purple()
            )
            if track.thumbnail:
                embed.set_thumbnail(url=track.thumbnail)
            embed.add_field(name="Požádano od:", value=user.mention)
            await interaction.followup.send(embed=embed)

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Prefix k! command
    @commands.command(name="hraj", aliases=["h"])
    async def play(self, ctx: commands.Context, *, query: Optional[str] = None):
        # Check if user has the specific ID and send message
        if ctx.author.id == 1150085087451435102:
            await ctx.reply("Ty nemůžeš použít tento příkaz")
        
        if not query:
            return await ctx.reply("Použij: `k!hraj <název skladby>` nebo `k!hraj <YouTube/SoundCloud odkaz>`")

        mgr = get_manager(self.bot)

        # Direct link (YouTube or SoundCloud)
        if query.startswith(("http://", "https://")):
            await mgr.ensure_voice(ctx)
            
            # Get full track info (title, thumbnail, stream URL in one call)
            track_info = await get_track_info(query)
            if not track_info or not track_info.get("stream_url"):
                return await ctx.reply("Nemůžu získat stream z tohoto odkazu.")
            
            track = Track(
                title=track_info.get("title") or "Neznámá skladba",
                url=query,
                stream_url=track_info["stream_url"],
                requested_by=ctx.author,
                web_url=track_info.get("url") or query,
                thumbnail=track_info.get("thumbnail")
            )
            await mgr.add_track(ctx, track)
            # Don't send success message if it's the specific user
            if ctx.author.id != 1150085087451435102:
                is_sc = is_soundcloud_url(query)
                source_emoji = "🎵" if is_sc else "🎵"
                return await ctx.reply(f"{source_emoji} Přidána skladba: **{track.title}**")
            return

        # Search on YouTube by default
        results = await search_yt(query, limit=SEARCH_RESULTS)
        if not results:
            return await ctx.reply("Nenalezeny žádné výsledky.")

        embed = discord.Embed(
            title=f"Výsledky pro: {query}",
            description="\n".join(
                f"{i+1}. **{r['title']}** · `{'N/A' if r['duration'] is None else fmt_duration(r['duration'])}`"
                for i, r in enumerate(results)
            ),
            color=discord.Color.light_embed()
        )
        thumb = results[0].get("thumbnail")
        if thumb:
            embed.set_thumbnail(url=thumb)
        embed.set_footer(text=f"Počkej a reaguj s 1️⃣ až 5️⃣ do {REACT_TIMEOUT}s")

        # Don't show selection menu for specific user, just play first result
        if ctx.author.id == 1150085087451435102:
            chosen = results[0]
            await mgr.ensure_voice(ctx)
            stream = await get_stream_url(chosen["url"])
            if not stream:
                return await ctx.reply("Nemůžu získat stream z tohoto odkazu.")
            track = Track(
                title=chosen["title"],
                url=chosen["url"],
                stream_url=stream,
                requested_by=ctx.author,
                web_url=chosen["url"],
                thumbnail=chosen.get("thumbnail")
            )
            await mgr.add_track(ctx, track)
            return

        msg = await ctx.reply(embed=embed)

        add_tasks = [msg.add_reaction(NUMBER_EMOJIS[i]) for i in range(len(results))]
        await asyncio.gather(*add_tasks, return_exceptions=True)
        ready = True  

        def check(reaction: discord.Reaction, user: discord.User):
            return (
                ready
                and reaction.message.id == msg.id
                and str(reaction.emoji) in NUMBER_EMOJIS[:len(results)]
                and user.id == ctx.author.id
            )

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=REACT_TIMEOUT, check=check)
        except asyncio.TimeoutError:
            with contextlib.suppress(discord.Forbidden):
                await msg.clear_reactions()
            return await ctx.send("⏱️ Čas vypršel. Zkus to znovu.")

        index = NUMBER_EMOJIS.index(str(reaction.emoji))
        chosen = results[index]

        await mgr.ensure_voice(ctx)

        stream = await get_stream_url(chosen["url"])
        if not stream:
            return await ctx.reply("Nemůžu získat stream z tohoto odkazu.")

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
            title="Přidáno do fronty",
            description=f"**{track.title}**",
            color=discord.Color.light_embed()
        )
        if track.thumbnail:
            confirm.set_thumbnail(url=track.thumbnail)
        confirm.add_field(name="Požádal", value=ctx.author.mention)
        await ctx.reply(embed=confirm)

async def setup(bot: commands.Bot):
    await bot.add_cog(Play(bot))
