# core/music_manager.py
import asyncio
from typing import Optional, Deque, Dict
from collections import deque
import discord
from discord.ext import commands
from .constants import FFMPEG_BEFORE_OPTS, FFMPEG_OPTS, IDLE_LEAVE_SECONDS

class Track:
    def __init__(self, title: str, url: str, stream_url: str, requested_by: discord.Member,
                 web_url: str, thumbnail: Optional[str] = None, uploader: Optional[str] = None, 
                 duration: Optional[int] = None):
        self.title = title
        self.url = url          
        self.stream_url = stream_url
        self.requested_by = requested_by
        self.web_url = web_url
        self.thumbnail = thumbnail
        self.uploader = uploader
        self.duration = duration

class GuildMusic:
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        self.queue: Deque[Track] = deque()
        self.current: Optional[Track] = None
        self.volume = 1.0
        self.player_task: Optional[asyncio.Task] = None
        self.loop = False
        self.skip_current = False  # Flag for skipping without re-queuing 
        self.play_start_time: Optional[float] = None  # Timestamp when current track started 

class MusicManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._guilds: Dict[int, GuildMusic] = {}

    def get_guild(self, guild: discord.Guild) -> GuildMusic:
        if guild.id not in self._guilds:
            self._guilds[guild.id] = GuildMusic(guild)
        return self._guilds[guild.id]

    async def ensure_voice(self, ctx_or_interaction, target_channel: Optional[discord.VoiceChannel] = None):
        # Support both commands.Context and discord.Interaction
        if isinstance(ctx_or_interaction, commands.Context):
            author = ctx_or_interaction.author
            guild = ctx_or_interaction.guild
            voice_client = ctx_or_interaction.voice_client
        elif isinstance(ctx_or_interaction, discord.Interaction):
            author = ctx_or_interaction.user
            guild = ctx_or_interaction.guild
            # Get voice client from bot
            voice_client = guild.voice_client if guild else None
        else:
            raise TypeError("ctx_or_interaction must be commands.Context or discord.Interaction")

        if not author or not isinstance(author, discord.Member) or not author.voice or not author.voice.channel:
            raise commands.CommandError("Nejdříve musíš být v chcallu ty voříšku!!!!")
        channel = target_channel or author.voice.channel
        
        # If already connected to the right channel, do nothing
        if voice_client and voice_client.is_connected():
            if voice_client.channel.id == channel.id:
                return
            # Move to new channel
            try:
                await voice_client.move_to(channel)
            except Exception as e:
                # If move fails, disconnect and reconnect
                try:
                    await voice_client.disconnect(force=False)
                except Exception:
                    pass
                await asyncio.sleep(0.5)
                await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
        else:
            # Not connected, try to connect with retry
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    await channel.connect(timeout=60.0, reconnect=True, self_deaf=True)
                    break
                except discord.errors.ConnectionClosed as e:
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(1.0 * (attempt + 1))
                        continue
                    else:
                        raise commands.CommandError(f"Nemůžu se připojit do voice channelu. Zkus to znovu.")

    def _create_source(self, stream_url: str) -> discord.PCMVolumeTransformer:
        audio = discord.FFmpegPCMAudio(
            stream_url,
            before_options=FFMPEG_BEFORE_OPTS,
            options=FFMPEG_OPTS
        )
        src = discord.PCMVolumeTransformer(audio)
        return src

    def set_volume(self, vc: discord.VoiceClient, vol: float):
        gm = self.get_guild(vc.guild)
        gm.volume = vol
        if vc.source and isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = vol

    async def add_track(self, ctx_or_interaction, track: Track, start_if_idle: bool = True):
        # Support both commands.Context and discord.Interaction
        if isinstance(ctx_or_interaction, commands.Context):
            guild = ctx_or_interaction.guild
        elif isinstance(ctx_or_interaction, discord.Interaction):
            guild = ctx_or_interaction.guild
        else:
            raise TypeError("ctx_or_interaction must be commands.Context or discord.Interaction")
        gm = self.get_guild(guild)
        gm.queue.append(track)
        if start_if_idle and not gm.player_task:
            gm.player_task = self.bot.loop.create_task(self._player_loop(ctx_or_interaction))

    async def skip(self, ctx_or_interaction):
        if isinstance(ctx_or_interaction, commands.Context):
            guild = ctx_or_interaction.guild
            vc = ctx_or_interaction.voice_client
        elif isinstance(ctx_or_interaction, discord.Interaction):
            guild = ctx_or_interaction.guild
            vc = guild.voice_client if guild else None
        else:
            raise TypeError("ctx_or_interaction must be commands.Context or discord.Interaction")
        gm = self.get_guild(guild)
        gm.skip_current = True  # Mark that we're skipping (don't re-queue if loop is on)
        if vc and vc.is_playing():
            vc.stop()
        # Don't call _cleanup here - let the player loop handle it

    async def stop(self, ctx_or_interaction):
        if isinstance(ctx_or_interaction, commands.Context):
            guild = ctx_or_interaction.guild
        elif isinstance(ctx_or_interaction, discord.Interaction):
            guild = ctx_or_interaction.guild
        else:
            raise TypeError("ctx_or_interaction must be commands.Context or discord.Interaction")
        gm = self.get_guild(guild)
        gm.queue.clear()
        gm.skip_current = True  # Don't re-queue when stopping
        await self._cleanup(ctx_or_interaction)

    async def _player_loop(self, ctx_or_interaction):
        # Support both commands.Context and discord.Interaction
        if isinstance(ctx_or_interaction, commands.Context):
            guild = ctx_or_interaction.guild
            voice_client = ctx_or_interaction.voice_client
        elif isinstance(ctx_or_interaction, discord.Interaction):
            guild = ctx_or_interaction.guild
            voice_client = guild.voice_client if guild else None
        else:
            raise TypeError("ctx_or_interaction must be commands.Context or discord.Interaction")
        gm = self.get_guild(guild)
        try:
            while True:
                if not gm.queue:
                    gm.player_task = None
                    break

                track = gm.queue.popleft()
                gm.current = track

                source = self._create_source(track.stream_url)
                source.volume = gm.volume

                attempts = 0
                while attempts < 2:
                    vc = voice_client
                    if not vc or not vc.is_connected():
                        try:
                            await self.ensure_voice(ctx_or_interaction)
                            vc = guild.voice_client if guild else None
                        except Exception:
                            break

                    if vc:
                        vc.play(source)
                        gm.play_start_time = asyncio.get_event_loop().time()  # Save when playback started
                        
                        # Set voice channel status to current song
                        try:
                            await vc.channel.edit(status=f"🎵 {track.title}")
                        except Exception:
                            pass  # Ignore if status setting fails

                    start_ts = asyncio.get_event_loop().time()
                    while vc and (vc.is_playing() or vc.is_paused()):
                        await asyncio.sleep(0.5)

                    play_dur = asyncio.get_event_loop().time() - start_ts
                    
                    # Don't retry if we're skipping - just move to next track
                    if gm.skip_current:
                        break
                    
                    if play_dur < 10 and attempts == 0:
                        try:
                            from utils.ytdl import get_stream_url
                            new_url = await get_stream_url(track.web_url)
                            if new_url and new_url != track.stream_url:
                                track.stream_url = new_url
                                source = self._create_source(track.stream_url)
                                source.volume = gm.volume
                                attempts += 1
                                continue
                        except Exception:
                            pass
                    break  

                # Re-queue if loop is enabled AND we're not skipping
                if gm.loop and not gm.skip_current:
                    gm.queue.appendleft(track)
                
                # Reset skip flag AFTER re-queue check
                # This way if we skipped, the flag prevents re-queue, then gets reset for next track
                gm.skip_current = False

                gm.current = None
                
                # Clear voice channel status when no song is playing
                if vc and vc.is_connected():
                    try:
                        await vc.channel.edit(status=None)
                    except Exception:
                        pass

        finally:
            vc = voice_client
            if not vc:
                return
            idle = 0
            while idle < IDLE_LEAVE_SECONDS:
                gm = self.get_guild(guild)
                if vc.is_playing() or vc.is_paused() or gm.queue or gm.current:
                    return  
                await asyncio.sleep(1)
                idle += 1
            await self._cleanup(ctx_or_interaction)  

    async def _cleanup(self, ctx_or_interaction):
        if isinstance(ctx_or_interaction, commands.Context):
            guild = ctx_or_interaction.guild
            voice_client = ctx_or_interaction.voice_client
        elif isinstance(ctx_or_interaction, discord.Interaction):
            guild = ctx_or_interaction.guild
            voice_client = guild.voice_client if guild else None
        else:
            raise TypeError("ctx_or_interaction must be commands.Context or discord.Interaction")
        gm = self.get_guild(guild)
        gm.current = None
        gm.queue.clear()
        if voice_client and voice_client.is_connected():
            try:
                await voice_client.disconnect(force=False)
            except Exception:
                # If normal disconnect fails, try force disconnect
                try:
                    await voice_client.disconnect(force=True)
                except Exception:
                    pass
        gm.player_task = None
