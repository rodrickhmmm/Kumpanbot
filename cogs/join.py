from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join")
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply("You need to **join a voice channel** first.")
        await get_manager(self.bot).ensure_voice(ctx)
        await ctx.reply("✅ Joined your voice channel.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Join(bot))
