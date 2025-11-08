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

class Vratahosek(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="vratahosek", description="Přehraje již vybraný playlist všech oblíbených písniček od Vráti Hoška.")
    async def play_slash(self, interaction: discord.Interaction):
        skladba = "https://www.youtube.com/watch?v=CMyUnSOQWks&list=PLvdoPwZAF6-dE3qcldZxSex6vlgbMULYy&index=1"
        user = interaction.user
        await interaction.response.defer()
        
        # Check if user has the specific ID and send message
        if user.id == 1150085087451435102:
            await interaction.followup.send("Nemáš práva na používání tohoto příkazu!!", ephemeral=True)
            return  # IMPORTANT: Stop execution here

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
                            thumbnail=track_info.get("thumbnail") or track_data.get("thumbnail"),
                            uploader=track_info.get("uploader") or track_data.get("uploader"),
                            duration=track_info.get("duration") or track_data.get("duration")
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
            
            print(f"[DEBUG] Track info: title={track_info.get('title')}, thumbnail={track_info.get('thumbnail')}, uploader={track_info.get('uploader')}, duration={track_info.get('duration')}")
            
            track = Track(
                title=track_info.get("title") or "Neznámá skladba",
                url=skladba,
                stream_url=track_info["stream_url"],
                requested_by=user,
                web_url=track_info.get("url") or skladba,
                thumbnail=track_info.get("thumbnail"),
                uploader=track_info.get("uploader"),
                duration=track_info.get("duration")
            )
            await mgr.add_track(interaction, track)
            # Don't send success message if it's the specific user
            if user.id != 1150085087451435102:
                is_sc = is_soundcloud_url(skladba)
                source_name = "SoundCloud" if is_sc else "YouTube"
                print(f"[DEBUG] Creating embed with thumbnail: {track.thumbnail}")
                embed = discord.Embed(
                    title=f"{track.title}",
                    description=f"🎵 Přidána skladba do fronty",
                    color=discord.Color.purple(),
                    url=track.web_url
                )
                if track.thumbnail:
                    print(f"[DEBUG] Setting image: {track.thumbnail}")
                    embed.set_image(url=track.thumbnail)
                else:
                    print("[DEBUG] No thumbnail available!")
                if track.uploader:
                    embed.add_field(name="Autor", value=track.uploader, inline=True)
                if track.duration:
                    embed.add_field(name="Délka", value=fmt_duration(track.duration), inline=False)
                embed.add_field(name="Zdroj", value=source_name, inline=True)
                embed.set_footer(text=f"Požádal {user.display_name}", icon_url=user.display_avatar.url)
                await interaction.followup.send(embed=embed)
            return

        # Search - try SoundCloud if it looks like it might be from there, otherwise YouTube
        results = await search_yt(skladba, limit=1)
        if not results:
            await interaction.followup.send("Nenalezeny žádné výsledky.", ephemeral=True)
            return
        chosen = results[0]
        print(f"[DEBUG SEARCH] Chosen result: title={chosen.get('title')}, thumbnail={chosen.get('thumbnail')}, uploader={chosen.get('uploader')}")
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
            thumbnail=chosen.get("thumbnail"),
            uploader=chosen.get("uploader"),
            duration=chosen.get("duration")
        )
        print(f"[DEBUG SEARCH] Created track with thumbnail: {track.thumbnail}")
        await mgr.add_track(interaction, track)
        # Don't send success message if it's the specific user
        if user.id != 1150085087451435102:
            embed = discord.Embed(
                title=f"{track.title}",
                description="🎵 Přidána skladba do fronty",
                color=discord.Color.purple()
            )
            if track.thumbnail:
                print(f"[DEBUG SEARCH] Setting image: {track.thumbnail}")
                embed.set_image(url=track.thumbnail)
            else:
                print("[DEBUG SEARCH] No thumbnail!")
            if track.uploader:
                embed.add_field(name="Autor", value=track.uploader, inline=True)
            if track.duration:
                embed.add_field(name="Délka", value=fmt_duration(track.duration), inline=False)
            embed.set_footer(text=f"Požádal {user.display_name}", icon_url=user.display_avatar.url)
            await interaction.followup.send(embed=embed)

    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(Vratahosek(bot))
