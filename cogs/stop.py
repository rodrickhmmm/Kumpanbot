from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Stop(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="stop")
    async def stop(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("The bot is not in a voice channel.")
        await get_manager(self.bot).stop(ctx)
        await ctx.reply("⏹️ Stopped playing and left the channel.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Stop(bot))
