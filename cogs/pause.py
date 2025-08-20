from discord.ext import commands

class Pause(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.reply("Không có gì để tạm dừng.")
        if vc.is_paused():
            return await ctx.reply("Đang tạm dừng rồi.")
        vc.pause()
        await ctx.reply("⏸️ Tạm dừng.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Pause(bot))
