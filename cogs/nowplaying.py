import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class NowPlaying(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="np", aliases=["nowplaying"])
    async def nowplaying(self, ctx: commands.Context):
        gm = get_manager(self.bot).get_guild(ctx.guild)
        if not gm.current:
            return await ctx.reply("Không có bài nào đang phát.")
        e = discord.Embed(
            title="Đang phát",
            description=f"[{gm.current.title}]({gm.current.web_url})",
            color=discord.Color.purple()
        )
        if gm.current.thumbnail:
            e.set_thumbnail(url=gm.current.thumbnail)
        e.add_field(name="Yêu cầu bởi", value=gm.current.requested_by.mention)
        await ctx.reply(embed=e)

async def setup(bot: commands.Bot):
    await bot.add_cog(NowPlaying(bot))
