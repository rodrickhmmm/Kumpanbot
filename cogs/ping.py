import discord
from discord.ext import commands
from discord import app_commands

guild_id = 948315626131300402
test_guild = discord.Object(id=guild_id)

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Zkontroluje řinčákovu rychlost.")
    async def ping(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Rychlost řinčáka: **{latency_ms}ms**")

async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))