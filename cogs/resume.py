from discord.ext import commands

class Resume(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="resume", aliases=["unpause", "continue"])
    async def resume(self, ctx: commands.Context):
        vc = ctx.voice_client
        if not vc:
            return await ctx.reply("The bot is not in a voice channel.")
        if not vc.is_paused():
            return await ctx.reply("The music is not paused.")
        vc.resume()
        await ctx.reply("▶️ Resumed playing.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Resume(bot))
