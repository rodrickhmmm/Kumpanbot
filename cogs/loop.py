# cogs/loop.py
import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Loop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="loop", aliases=["repeat"])
    async def loop(self, ctx: commands.Context):
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(ctx.guild)
        gm.loop = not gm.loop
        await ctx.reply(f"🔁 Loop is now **{'enabled' if gm.loop else 'disabled'}**.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Loop(bot))
