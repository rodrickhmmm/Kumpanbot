import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Leave(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="odpoj", description="Řinčák se odpojí ze chcallu.")
    async def leave_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        guild = interaction.guild
        if not guild or not guild.voice_client:
            await interaction.response.send_message("Nejsem ve chcallu ty kaštane.", ephemeral=True)
            return
        
        # Defer the response first
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        # Clear queue and stop playback properly
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(guild)
        gm.queue.clear()
        gm.skip_current = True  # Don't re-queue current track
        
        if guild.voice_client and guild.voice_client.is_playing():
            guild.voice_client.stop()
        
        await guild.voice_client.disconnect(force=False)
        
        # Use followup since we deferred
        try:
            embed = discord.Embed(
                title="👋 Odpojeno",
                description="Vyčistil jsem frontu a odpojil se z hlasového kanálu.",
                color=discord.Color.purple()
            )
            await interaction.followup.send(embed=embed)
        except Exception:
            pass  # Ignore if followup fails

    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="odpoj", aliases=["disconnect"])
    async def leave(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("Nejsem ve chcallu ty kaštane.")
        
        # Clear queue and stop playback properly
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(ctx.guild)
        gm.queue.clear()
        gm.skip_current = True  # Don't re-queue current track
        
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
        
        await ctx.voice_client.disconnect(force=False)
        await ctx.reply("👋 Odpojil jsem se z chcallu.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Leave(bot))
