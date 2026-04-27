import discord
from discord.ext import commands
from discord import app_commands

from core.maso_nahoru_manager import get_manager

ROLE_ID = 1380992801348517958  # role to assign when someone is added


def _get_role(guild: discord.Guild) -> discord.Role | None:
    role = guild.get_role(int(ROLE_ID))
    return role

class MasoNahoruPridat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="masonahorupridat", description="Přidá někoho do masa nahoru")
    @app_commands.describe(member="Koho přidat")
    async def masonahorupridat_slash(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.guild is None:
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na serveru ty zabaglounče.", ephemeral=True)
            return

        mgr = get_manager(self.bot)
        added = mgr.add(interaction.guild, member.id)

        embed = mgr.build_embed(interaction.guild)
        if added:
            role = _get_role(interaction.guild)
            if role is not None:
                try:
                    await member.add_roles(role, reason="Maso nahoru: přidán do seznamu")
                except (discord.Forbidden, discord.HTTPException):
                    embed.add_field(
                        name="⚠️ Role",
                        value="Nepodařilo se přidat roli (chybí oprávnění nebo role neexistuje v hierarchii).",
                        inline=False,
                    )
            else:
                embed.add_field(
                    name="⚠️ Role",
                    value="Roli se nepodařilo najít (zkontroluj ROLE_ID v cog souboru).",
                    inline=False,
                )
            embed.title = "✅ Kumpán byl přidán do masa nahoru"
        else:
            embed.title = "ℹ️ Kumpán už je v seznamu"
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="masonahorupridat", aliases=["mnhadd"])
    async def masonahorupridat_prefix(self, ctx: commands.Context, member: discord.Member = None):
        if ctx.guild is None:
            return await ctx.reply("Tenhle příkaz můžeš poslat jen na serveru ty zabaglounče.")
        if member is None:
            return await ctx.reply("Musíš označit uživatele! Použij: `k!masonahorupridat @uživatel`")

        mgr = get_manager(self.bot)
        added = mgr.add(ctx.guild, member.id)

        embed = mgr.build_embed(ctx.guild)
        if added:
            role = _get_role(ctx.guild)
            if role is not None:
                try:
                    await member.add_roles(role, reason="Maso nahoru: přidán do seznamu")
                except (discord.Forbidden, discord.HTTPException):
                    embed.add_field(
                        name="⚠️ Role",
                        value="Nepodařilo se přidat roli (chybí oprávnění nebo role neexistuje v hierarchii).",
                        inline=False,
                    )
            else:
                embed.add_field(
                    name="⚠️ Role",
                    value="Roli se nepodařilo najít (zkontroluj ROLE_ID v cog souboru).",
                    inline=False,
                )
            embed.title = "✅ Kumpán přidán do masa nahoru"
        else:
            embed.title = "ℹ️ Kumpán už je v seznamu"
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MasoNahoruPridat(bot))
