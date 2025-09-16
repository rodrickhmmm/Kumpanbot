# cogs/loop.py
import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Loop(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="smycka", description="Zapne/vypne opakování aktuální skladby.")
    async def loop_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(interaction.guild)
        gm.loop = not gm.loop
        await interaction.response.send_message(f"🔁 Loop is now **{'enabled' if gm.loop else 'disabled'}**.")
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="smycka", aliases=["repeat"])
    async def loop(self, ctx: commands.Context):
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(ctx.guild)
        gm.loop = not gm.loop
        await ctx.reply(f"🔁 Loop is now **{'enabled' if gm.loop else 'disabled'}**.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Loop(bot))
