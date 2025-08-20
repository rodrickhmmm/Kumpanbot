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
        self.url = url          # input link or id
        self.stream_url = stream_url
        self.requested_by = requested_by
        self.web_url = web_url  # webpage_url để mở
        self.thumbnail = thumbnail

class GuildMusic:
    def __init__(self, guild: discord.Guild):
        self.guild = guild
        self.queue: Deque[Track] = deque()
        self.current: Optional[Track] = None
        self.volume = 1.0
        self.player_task: Optional[asyncio.Task] = None

class MusicManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._guilds: Dict[int, GuildMusic] = {}

    def get_guild(self, guild: discord.Guild) -> GuildMusic:
        if guild.id not in self._guilds:
            self._guilds[guild.id] = GuildMusic(guild)
        return self._guilds[guild.id]

    async def ensure_voice(self, ctx: commands.Context, target_channel: Optional[discord.VoiceChannel] = None):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("Bạn cần vào một kênh voice trước.")
        channel = target_channel or ctx.author.voice.channel
        if ctx.voice_client:
            if ctx.voice_client.channel != channel:
                await ctx.voice_client.move_to(channel)
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

    async def add_track(self, ctx: commands.Context, track: Track, start_if_idle: bool = True):
        gm = self.get_guild(ctx.guild)
        gm.queue.append(track)
        if start_if_idle and not gm.player_task:
            gm.player_task = ctx.bot.loop.create_task(self._player_loop(ctx))

    async def skip(self, ctx: commands.Context):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.stop()

    async def stop(self, ctx: commands.Context):
        gm = self.get_guild(ctx.guild)
        gm.queue.clear()
        await self._cleanup(ctx)

    async def _player_loop(self, ctx: commands.Context):
        gm = self.get_guild(ctx.guild)
        vc = ctx.voice_client
        try:
            while True:
                if not gm.queue:
                    gm.player_task = None
                    break

                track = gm.queue.popleft()
                gm.current = track

                # Tạo source lần đầu
                source = self._create_source(track.stream_url)
                source.volume = gm.volume

                # Chạy với logic retry 1 lần nếu lỗi sớm
                attempts = 0
                while attempts < 2:
                    # Đảm bảo voice kết nối
                    vc = ctx.voice_client
                    if not vc or not vc.is_connected():
                        try:
                            await self.ensure_voice(ctx)
                            vc = ctx.voice_client
                        except Exception:
                            # Không thể kết nối voice => bỏ bài
                            break

                    vc.play(source)

                    # Theo dõi phát
                    start_ts = asyncio.get_event_loop().time()
                    while vc.is_playing() or vc.is_paused():
                        await asyncio.sleep(0.5)

                    # Nếu chơi < 10s coi như lỗi stream, refetch và thử lại
                    play_dur = asyncio.get_event_loop().time() - start_ts
                    if play_dur < 10 and attempts == 0:
                        # Refetch stream url
                        try:
                            from utils.ytdl import get_stream_url
                            new_url = await get_stream_url(track.web_url)
                            if new_url and new_url != track.stream_url:
                                track.stream_url = new_url
                                source = self._create_source(track.stream_url)
                                source.volume = gm.volume
                                attempts += 1
                                continue  # thử phát lại
                        except Exception:
                            pass
                    # Phát xong bình thường hoặc đã retry -> thoát vòng
                    break

                gm.current = None

        finally:
            # Auto-leave chỉ khi rảnh hoàn toàn trong IDLE_LEAVE_SECONDS
            vc = ctx.voice_client
            if not vc:
                return
            idle = 0
            while idle < IDLE_LEAVE_SECONDS:
                gm = self.get_guild(ctx.guild)
                if vc.is_playing() or vc.is_paused() or gm.queue or gm.current:
                    # Có hoạt động -> không rời
                    return
                await asyncio.sleep(1)
                idle += 1
            # Idle đủ lâu -> rời
            await self._cleanup(ctx)

    async def _cleanup(self, ctx: commands.Context):
        gm = self.get_guild(ctx.guild)
        gm.current = None
        gm.queue.clear()
        if ctx.voice_client:
            await ctx.voice_client.disconnect(force=True)
        gm.player_task = None
