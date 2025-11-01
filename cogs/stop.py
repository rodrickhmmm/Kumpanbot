import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Stop(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="prestat", description="Zastaví hudbu a opustí chcall.")
    async def stop_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        guild = interaction.guild
        if not guild.voice_client:
            await interaction.response.send_message("Řinčák není v chcallu.", ephemeral=True)
            return
        
        # Defer the response first
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(guild)
        gm.skip_current = True  # Don't re-queue current track when stopping
        await mgr.stop(interaction)
        
        # Use followup since we deferred
        try:
            await interaction.followup.send("⏹️ Hudba je zastavena a opustil jsem chcall.")
        except Exception:
            pass  # Ignore if followup fails
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="prestat")
    async def stop(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("Řinčák není v chcallu..")
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(ctx.guild)
        gm.skip_current = True  # Don't re-queue current track when stopping
        await mgr.stop(ctx)
        await ctx.reply("⏹️ Hudba je zastavena a opustil jsem chcall.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Stop(bot))
