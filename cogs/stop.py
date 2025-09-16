import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Stop(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="prestat", description="Zastaví hudbu a opustí voice channel.")
    async def stop_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        guild = interaction.guild
        if not guild.voice_client:
            await interaction.response.send_message("The bot is not in a voice channel.", ephemeral=True)
            return
        await get_manager(self.bot).stop(interaction)
        await interaction.response.send_message("⏹️ Stopped playing and left the channel.")
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="prestat")
    async def stop(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("The bot is not in a voice channel.")
        await get_manager(self.bot).stop(ctx)
        await ctx.reply("⏹️ Stopped playing and left the channel.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Stop(bot))
