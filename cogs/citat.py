import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

guild_id = 948315626131300402
test_guild = discord.Object(id=guild_id)

class Citaty(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="citat", description="Udělej citát")
    async def citat_command(
        self, 
        interaction: discord.Interaction, 
        autorcitatu: str, 
        datum: str, 
        citat: str,
        autor2: Optional[str] = None,
        autor3: Optional[str] = None
    ):
        embed = discord.Embed(
            title="Citát",
            color=discord.Color.purple()
        )
        
        # Sestavení seznamu autorů
        autori = [autorcitatu]
        if autor2:
            autori.append(autor2)
        if autor3:
            autori.append(autor3)
        
        autori_text = ", ".join(autori)
        
        embed.add_field(name="Autor" if len(autori) == 1 else "Autoři", value=autori_text, inline=True)
        embed.add_field(name="Datum", value=datum, inline=True)
        embed.add_field(name="Citát", value=f"\"{citat}\"", inline=False)
        embed.set_footer(text=f"Vytvořil: {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Citaty(bot))