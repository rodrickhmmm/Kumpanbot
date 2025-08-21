from discord.ext import commands

class Pause(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.reply("Nothing to pause.")
        if vc.is_paused():
            return await ctx.reply("Already paused.")
        vc.pause()
        await ctx.reply("⏸️ Paused.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Pause(bot))
