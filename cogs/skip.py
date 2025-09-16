import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Skip(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="preskocit", description="Přeskočí aktuální skladbu.")
    async def skip_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        guild = interaction.guild
        if not guild.voice_client:
            await interaction.response.send_message("The bot is not in a voice channel.", ephemeral=True)
            return
        await get_manager(self.bot).skip(interaction)
        await interaction.response.send_message("⏭️ Skipped.")
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="preskocit", aliases=["s"])
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("The bot is not in a voice channel.")
        await get_manager(self.bot).skip(ctx)
        await ctx.reply("⏭️ Skipped.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Skip(bot))
