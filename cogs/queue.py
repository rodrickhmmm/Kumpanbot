import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Queue(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="queue", description="Zobrazí frontu skladeb.")
    async def queue_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(interaction.guild)
        if gm.current is None and not gm.queue:
            await interaction.response.send_message("Queue is empty.", ephemeral=True)
            return
        desc = ""
        if gm.current:
            desc += f"**Now playing:** [{gm.current.title}]({gm.current.web_url}) (requested by {gm.current.requested_by.mention})\n\n"
        if gm.queue:
            for i, t in enumerate(list(gm.queue)[:10], start=1):
                desc += f"{i}. [{t.title}]({t.web_url}) • req: {t.requested_by.mention}\n"
            if len(gm.queue) > 10:
                desc += f"... and {len(gm.queue) - 10} more tracks.\n"
        embed = discord.Embed(title="Queue", description=desc, color=discord.Color.light_embed())
        await interaction.response.send_message(embed=embed)
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
