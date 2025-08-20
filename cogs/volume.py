from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Volume(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="volume", aliases=["vol"])
    async def volume(self, ctx: commands.Context, vol: int = None):
        if vol is None:
            return await ctx.reply("Dùng: `o!vol <0-200>`")
        if not 0 <= vol <= 200:
            return await ctx.reply("Âm lượng phải từ 0 đến 200.")
        vc = ctx.voice_client
        if not vc:
            return await ctx.reply("Bot chưa ở trong voice.")
        get_manager(self.bot).set_volume(vc, vol / 100.0)
        await ctx.reply(f"🔊 Volume: {vol}%")

async def setup(bot: commands.Bot):
    await bot.add_cog(Volume(bot))
