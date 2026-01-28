import discord
from discord.ext import commands
from core.music_manager import MusicManager
import asyncio

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Skip(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="preskocit", description="Přeskočí aktuální skladbu.")
    @app_commands.describe(pocet="Počet skladeb k přeskočení (výchozí: 1)")
    async def skip_slash(self, interaction, pocet: int = 1):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        guild = interaction.guild
        if not guild.voice_client:
            await interaction.response.send_message("Řinčák není v chcallu.", ephemeral=True)
            return
        
        # Validate count
        if pocet < 1:
            await interaction.response.send_message("Počet musí být alespoň 1.", ephemeral=True)
            return
        
        # Defer the response first to avoid timeout issues
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(guild)
        
        # Remove songs from queue (pocet - 1, because skip() will skip the current one)
        removed_count = 0
        for i in range(pocet - 1):
            if gm.queue:
                gm.queue.popleft()
                removed_count += 1
            else:
                break
        
        # Skip the current track
        await mgr.skip(interaction)
        skipped_count = removed_count + 1  # Total skipped = removed + current
        
        # Wait a bit for the next track to start
        await asyncio.sleep(0.5)
        
        # Get info about what's playing now
        next_track = None
        if guild.voice_client and guild.voice_client.is_playing():
            if hasattr(gm, 'current') and gm.current:
                next_track = gm.current
        
        # Use followup since we deferred
        try:
            embed = discord.Embed(
                title=f"⏭️ Přeskočeno skladeb: {skipped_count}",
                color=discord.Color.purple()
            )
            
            if next_track:
                embed.description = f"**Nyní hraje:**\n{next_track.title}"
                if next_track.thumbnail:
                    embed.set_thumbnail(url=next_track.thumbnail)
                if next_track.uploader:
                    embed.add_field(name="Autor", value=next_track.uploader, inline=True)
            else:
                embed.description = "*Fronta je prázdná*"
            
            embed.set_footer(text=f"Požádal {user.display_name}", icon_url=user.display_avatar.url)
            await interaction.followup.send(embed=embed)
        except Exception:
            pass  # Ignore if followup fails
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="preskocit", aliases=["s"])
    async def skip(self, ctx: commands.Context, pocet: int = 1):
        if not ctx.voice_client:
            return await ctx.reply("Řinčák není v chcallu.")
        
        # Validate count
        if pocet < 1:
            return await ctx.reply("Počet musí být alespoň 1.")
        
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(ctx.guild)
        
        # Remove songs from queue (pocet - 1, because skip() will skip the current one)
        removed_count = 0
        for i in range(pocet - 1):
            if gm.queue:
                gm.queue.popleft()
                removed_count += 1
            else:
                break
        
        # Skip the current track
        await mgr.skip(ctx)
        skipped_count = removed_count + 1  # Total skipped = removed + current
        
        # Wait a bit for the next track to start
        await asyncio.sleep(0.5)
        
        # Get info about what's playing now
        next_track = None
        if ctx.voice_client and ctx.voice_client.is_playing():
            if hasattr(gm, 'current') and gm.current:
                next_track = gm.current
        
        embed = discord.Embed(
            title=f"⏭️ Přeskočeno skladeb: {skipped_count}",
            color=discord.Color.purple()
        )
        
        if next_track:
            embed.description = f"**Nyní hraje:**\n{next_track.title}"
            if next_track.thumbnail:
                embed.set_thumbnail(url=next_track.thumbnail)
            if next_track.uploader:
                embed.add_field(name="Autor", value=next_track.uploader, inline=True)
        else:
            embed.description = "*Fronta je prázdná*"
        
        embed.set_footer(text=f"Požádal {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Skip(bot))
