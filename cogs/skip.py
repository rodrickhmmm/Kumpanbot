from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Skip(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("Bot chưa ở trong voice.")
        await get_manager(self.bot).skip(ctx)
        await ctx.reply("⏭️ Đã bỏ qua.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Skip(bot))
