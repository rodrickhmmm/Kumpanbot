import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class NowPlaying(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="nynihraje", description="Zobrazí aktuálně hranou skladbu.")
    async def nowplaying_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        gm = get_manager(self.bot).get_guild(interaction.guild)
        if not gm.current:
            await interaction.response.send_message("Teď nehraje žádná hudba.", ephemeral=True)
            return
        e = discord.Embed(
            title="Teď hraje",
            description=f"[{gm.current.title}]({gm.current.web_url})",
            color=0xa014e1
        )
        if gm.current.thumbnail:
            e.set_thumbnail(url=gm.current.thumbnail)
        e.add_field(name="Požadováno od", value=gm.current.requested_by.mention)
        await interaction.response.send_message(embed=e)
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="nynihraje", aliases=["nowplaying"])
    async def nowplaying(self, ctx: commands.Context):
        gm = get_manager(self.bot).get_guild(ctx.guild)
        if not gm.current:
            return await ctx.reply("Teď nehraje žádná hudba.")
        e = discord.Embed(
            title="Teď hraje",
            description=f"[{gm.current.title}]({gm.current.web_url})",
            color=0xa014e1
        )
        if gm.current.thumbnail:
            e.set_thumbnail(url=gm.current.thumbnail)
        e.add_field(name="Požadováno od", value=gm.current.requested_by.mention)
        await ctx.reply(embed=e)

async def setup(bot: commands.Bot):
    await bot.add_cog(NowPlaying(bot))
