import discord
from discord.ext import commands
from discord import app_commands

guild_id = 948315626131300402
test_guild = discord.Object(id=guild_id)

class Citaty(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="citat", description="Udělej citát")
    async def citat_command(self, interaction: discord.Interaction, autorcitatu: str, datum: str, citat: str):
        await interaction.response.send_message(f"{autorcitatu} {datum} - \"{citat}\"")

async def setup(bot: commands.Bot):
    await bot.add_cog(Citaty(bot))