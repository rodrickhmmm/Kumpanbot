# core/music_manager.py
import asyncio
from typing import Optional, Deque, Dict
from collections import deque
import discord
from discord.ext import commands
from .constants import FFMPEG_BEFORE_OPTS, FFMPEG_OPTS, IDLE_LEAVE_SECONDS

class Track:
    def __init__(self, title: str, url: str, stream_url: str, requested_by: discord.Member,
                 web_url: str, thumbnail: Optional[str] = None):
        self.title = title
        self.url = url          
        self.stream_url = stream_url
        self.requested_by = requested_by
        self.web_url = web_url
        self.thumbnail = thumbnail

class GuildMusic:
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        self.queue: Deque[Track] = deque()
        self.current: Optional[Track] = None
        self.volume = 1.0
        self.player_task: Optional[asyncio.Task] = None
        self.loop = False 

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
            raise commands.CommandError("You need to join a voice channel first.")
        channel = target_channel or author.voice.channel
        if voice_client:
            if voice_client.channel != channel:
                await voice_client.move_to(channel)
        else:
            await channel.connect(self_deaf=True)

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
        if vc and vc.is_playing():
            vc.stop()
        # If nothing is queued and nothing is playing, clean up and disconnect
        if (not gm.queue) and (not vc or not vc.is_playing()):
            await self._cleanup(ctx_or_interaction)

    async def stop(self, ctx: commands.Context):
        gm = self.get_guild(ctx.guild)
        gm.queue.clear()
        await self._cleanup(ctx)

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

                    start_ts = asyncio.get_event_loop().time()
                    while vc and (vc.is_playing() or vc.is_paused()):
                        await asyncio.sleep(0.5)

                    play_dur = asyncio.get_event_loop().time() - start_ts
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

                if gm.loop:
                    gm.queue.appendleft(track)

                gm.current = None

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
        if voice_client:
            await voice_client.disconnect(force=True)
        gm.player_task = None
