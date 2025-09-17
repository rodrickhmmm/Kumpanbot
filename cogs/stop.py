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
        await get_manager(self.bot).stop(interaction)
        await interaction.response.send_message("⏹️ Hudba je zastavena a opustil jsem chcall.")
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="prestat")
    async def stop(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("Řinčák není v chcallu..")
        await get_manager(self.bot).stop(ctx)
        await ctx.reply("⏹️ Hudba je zastavena a opustil jsem chcall.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Stop(bot))
