import discord
from discord.ext import commands
from discord import app_commands

from core.maso_nahoru_manager import get_manager

ROLE_ID = 1380992801348517958  # role to remove when someone is removed


def _get_role(guild: discord.Guild) -> discord.Role | None:
    role = guild.get_role(int(ROLE_ID))
    return role

class MasoNahoruOdebrat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="masonahoruodebrat", description="Odebere někoho z masa nahoru")
    @app_commands.describe(member="Koho odebrat")
    async def masonahoruodebrat_slash(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.guild is None:
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na serveru.", ephemeral=True)
            return

        mgr = get_manager(self.bot)
        removed = mgr.remove(interaction.guild, member.id)

        embed = mgr.build_embed(interaction.guild)
        if removed:
            role = _get_role(interaction.guild)
            if role is not None:
                try:
                    await member.remove_roles(role, reason="Maso nahoru: odebrán ze seznamu")
                except (discord.Forbidden, discord.HTTPException):
                    embed.add_field(
                        name="⚠️ Role",
                        value="Nepodařilo se odebrat roli (chybí oprávnění nebo role je výš v hierarchii).",
                        inline=False,
                    )
            else:
                embed.add_field(
                    name="⚠️ Role",
                    value="Roli se nepodařilo najít (zkontroluj ROLE_ID v cog souboru).",
                    inline=False,
                )
            embed.title = "✅ Kumpán byl odebrán z maso nahoru seznamu"
        else:
            embed.title = "ℹ️ Kumpán nebyl v seznamu"
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="masonahoruodebrat", aliases=["mnhremove", "mnhdel"])
    async def masonahoruodebrat_prefix(self, ctx: commands.Context, member: discord.Member = None):
        if ctx.guild is None:
            return await ctx.reply("Tenhle příkaz můžeš poslat jen na serveru.")
        if member is None:
            return await ctx.reply("Musíš označit uživatele! Použij: `k!masonahoruodebrat @uživatel`")

        mgr = get_manager(self.bot)
        removed = mgr.remove(ctx.guild, member.id)

        embed = mgr.build_embed(ctx.guild)
        if removed:
            role = _get_role(ctx.guild)
            if role is not None:
                try:
                    await member.remove_roles(role, reason="Maso nahoru: odebrán ze seznamu")
                except (discord.Forbidden, discord.HTTPException):
                    embed.add_field(
                        name="⚠️ Role",
                        value="Nepodařilo se odebrat roli (chybí oprávnění nebo role je výš v hierarchii).",
                        inline=False,
                    )
            else:
                embed.add_field(
                    name="⚠️ Role",
                    value="Roli se nepodařilo najít (zkontroluj ROLE_ID v cog souboru).",
                    inline=False,
                )
            embed.title = "✅ Kumpán byl odebrán z maso nahoru seznamu"
        else:
            embed.title = "ℹ️ Kumpán nebyl v seznamu"
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MasoNahoruOdebrat(bot))
