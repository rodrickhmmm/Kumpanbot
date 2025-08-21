import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Queue(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx: commands.Context):
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(ctx.guild)

        if gm.current is None and not gm.queue:
            return await ctx.reply("Queue is empty.")

        desc = ""
        if gm.current:
            desc += f"**Now playing:** [{gm.current.title}]({gm.current.web_url}) (requested by {gm.current.requested_by.mention})\n\n"

        if gm.queue:
            for i, t in enumerate(list(gm.queue)[:10], start=1):
                desc += f"{i}. [{t.title}]({t.web_url}) • req: {t.requested_by.mention}\n"
            if len(gm.queue) > 10:
                desc += f"... and {len(gm.queue) - 10} more tracks.\n"

        embed = discord.Embed(title="Queue", description=desc, color=discord.Color.light_embed())
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Queue(bot))
