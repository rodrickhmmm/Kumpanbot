import discord
from discord.ext import commands
from discord import app_commands

from core.maso_nahoru_manager import get_manager


class MasoNahoruList(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="masonahorulist",
        description="Zobrazí seznam se založenými kumpány, kteří budou na maso nahoru",
    )
    async def masonahorulist_slash(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Tenhle příkaz můžeš poslat jen na serveru ty zabaglounče.",
                ephemeral=True,
            )
            return

        mgr = get_manager(self.bot)
        embed = mgr.build_embed(interaction.guild)
        await interaction.response.send_message(embed=embed)

    @commands.command(name="masonahorulist", aliases=["mnhlist"])
    async def masonahorulist_prefix(self, ctx: commands.Context):
        if ctx.guild is None:
            return await ctx.reply("Tenhle příkaz můžeš poslat jen na serveru ty zabaglounče.")

        mgr = get_manager(self.bot)
        embed = mgr.build_embed(ctx.guild)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MasoNahoruList(bot))
