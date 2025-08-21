from discord.ext import commands

class Leave(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="leave", aliases=["disconnect"])
    async def leave(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("The bot is not in a voice channel.")
        await ctx.voice_client.disconnect(force=True)
        await ctx.reply("👋 Left the voice channel.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Leave(bot))
