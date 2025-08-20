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
        await get_manager(self.bot).ensure_voice(ctx)
        await ctx.reply("✅ Đã vào kênh voice của bạn.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Join(bot))
