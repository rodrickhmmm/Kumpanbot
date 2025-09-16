from discord.ext import commands
from core.music_manager import MusicManager
import discord
from discord.ext import commands
from discord import app_commands

guild_id = 948315626131300402
test_guild = discord.Object(id=guild_id)

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pripoj")
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply("You need to **join a voice channel** first.")
        await get_manager(self.bot).ensure_voice(ctx)
        await ctx.reply("✅ Joined your voice channel.")
        
    @app_commands.command(name="pripoj", description="Bot se joine do chcallu.")
    async def join(self, interaction: discord.Interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        if not user.voice or not user.voice.channel:
            await interaction.response.send_message("You need to **join a voice channel** first.", ephemeral=True)
            return
        await get_manager(self.bot).ensure_voice(interaction)
        await interaction.response.send_message("✅ Joined your voice channel.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Join(bot))
