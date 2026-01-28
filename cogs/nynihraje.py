import discord
from discord.ext import commands
from core.music_manager import MusicManager
import asyncio

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

def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Create a progress bar like [████████░░░░░░░░░░░░]"""
    if total <= 0:
        return "[" + "░" * length + "]"
    
    filled = int((current / total) * length)
    filled = max(0, min(filled, length))
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}]"

class NowPlaying(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="nynihraje", description="Zobrazí aktuálně hranou skladbu.")
    async def nowplaying_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(interaction.guild)
        
        if not gm.current:
            await interaction.response.send_message("Teď nehraje žádná hudba.", ephemeral=True)
            return
        
        # Calculate current position
        current_pos = 0
        if gm.play_start_time and gm.current.duration:
            elapsed = asyncio.get_event_loop().time() - gm.play_start_time
            current_pos = int(elapsed)
        
        # Create embed
        embed = discord.Embed(
            title=f"{gm.current.title}",
            description="🎵 Nyní hraje",
            color=discord.Color.purple(),
            url=gm.current.web_url
        )
        
        if gm.current.thumbnail:
            embed.set_image(url=gm.current.thumbnail)
        
        # Add fields
        if gm.current.uploader:
            embed.add_field(name="Autor", value=gm.current.uploader, inline=True)
        
        # Progress bar and time
        if gm.current.duration and current_pos:
            progress_bar = create_progress_bar(current_pos, gm.current.duration)
            time_display = f"{fmt_duration(current_pos)} / {fmt_duration(gm.current.duration)}"
            embed.add_field(name="Čas", value=f"{progress_bar}\n{time_display}", inline=False)
        elif gm.current.duration:
            embed.add_field(name="Délka", value=fmt_duration(gm.current.duration), inline=True)
        
        # Next in queue
        if gm.queue:
            next_track = list(gm.queue)[0]
            embed.add_field(name="Další ve frontě", value=f"**{next_track.title}**", inline=False)
        else:
            embed.add_field(name="Další ve frontě", value="*Nic ve frontě*", inline=False)
        
        embed.set_footer(text=f"Požádal {gm.current.requested_by.display_name}", icon_url=gm.current.requested_by.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="nynihraje", aliases=["nowplaying"])
    async def nowplaying(self, ctx: commands.Context):
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(ctx.guild)
        
        if not gm.current:
            return await ctx.reply("Teď nehraje žádná hudba.")
        
        # Calculate current position
        current_pos = 0
        if gm.play_start_time and gm.current.duration:
            elapsed = asyncio.get_event_loop().time() - gm.play_start_time
            current_pos = int(elapsed)
        
        # Create embed
        embed = discord.Embed(
            title=f"{gm.current.title}",
            description="🎵 Nyní hraje",
            color=discord.Color.purple(),
            url=gm.current.web_url
        )
        
        if gm.current.thumbnail:
            embed.set_image(url=gm.current.thumbnail)
        
        # Add fields
        if gm.current.uploader:
            embed.add_field(name="Autor", value=gm.current.uploader, inline=True)
        
        # Progress bar and time
        if gm.current.duration and current_pos:
            progress_bar = create_progress_bar(current_pos, gm.current.duration)
            time_display = f"{fmt_duration(current_pos)} / {fmt_duration(gm.current.duration)}"
            embed.add_field(name="Čas", value=f"{progress_bar}\n{time_display}", inline=False)
        elif gm.current.duration:
            embed.add_field(name="Délka", value=fmt_duration(gm.current.duration), inline=True)
        
        # Next in queue
        if gm.queue:
            next_track = list(gm.queue)[0]
            embed.add_field(name="Další ve frontě", value=f"**{next_track.title}**", inline=False)
        else:
            embed.add_field(name="Další ve frontě", value="*Nic ve frontě*", inline=False)
        
        embed.set_footer(text=f"Požádal {gm.current.requested_by.display_name}", icon_url=gm.current.requested_by.display_avatar.url)
        
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(NowPlaying(bot))
