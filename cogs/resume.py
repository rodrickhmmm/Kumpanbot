from discord.ext import commands

class Resume(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="resume", aliases=["unpause", "continue"])
    async def resume(self, ctx: commands.Context):
        vc = ctx.voice_client
        if not vc:
            return await ctx.reply("Bot chưa ở trong voice.")
        if not vc.is_paused():
            return await ctx.reply("Nhạc không ở trạng thái tạm dừng.")
        vc.resume()
        await ctx.reply("▶️ Tiếp tục phát.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Resume(bot))
