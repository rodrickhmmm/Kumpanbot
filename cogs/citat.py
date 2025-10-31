import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime

guild_id = 948315626131300402
test_guild = discord.Object(id=guild_id)

class CitatModal(discord.ui.Modal, title="Vytvoř citát"):
    autor1 = discord.ui.TextInput(label="Autor citátu", placeholder="Více autorů odděl čárkou", required=False)
    datum_input = discord.ui.TextInput(label="Datum (DD.MM.RRRR)", placeholder="Nech prázdné pro dnešní datum", required=False)
    cas_input = discord.ui.TextInput(label="Čas (HH:MM)", placeholder="Nech prázdné pro nynější čas", required=False)
    citat_text = discord.ui.TextInput(label="Citát", style=discord.TextStyle.paragraph, placeholder="Text citátu...", required=True)
    
    def __init__(self, mention_users: list[discord.Member] = None):
        super().__init__()
        self.mention_users = mention_users or []

    async def on_submit(self, interaction: discord.Interaction):
        # Parsování data - pokud je prázdné, použij dnešní datum
        if self.datum_input.value.strip():
            try:
                datum = datetime.strptime(self.datum_input.value, "%d.%m.%Y")
            except ValueError:
                await interaction.response.send_message("Neplatný formát data! Použij formát DD.MM.RRRR (např. 31.10.2025)", ephemeral=True)
                return
        else:
            datum = datetime.now()
        
        # Parsování času - pokud je prázdné, použij nynější čas
        if self.cas_input.value.strip():
            try:
                cas = datetime.strptime(self.cas_input.value, "%H:%M").time()
            except ValueError:
                await interaction.response.send_message("Neplatný formát času! Použij formát HH:MM (např. 14:30)", ephemeral=True)
                return
        else:
            cas = datetime.now().time()
        
        datum_text = datum.strftime("%d.%m.%Y")
        cas_text = cas.strftime("%H:%M")

        # Sestavení seznamu autorů
        autori = []
        
        # Pokud jsou zadáni mention_users, přidej je
        if self.mention_users:
            autori.extend([user.mention for user in self.mention_users])
        
        # Rozděl autory podle čárky z textového pole
        if self.autor1.value.strip():
            autori.extend([a.strip() for a in self.autor1.value.split(',') if a.strip()])
        
        autori_text = ", ".join(autori) if autori else "Neznámý"
        
        # Rozhodni, jestli "Autor" nebo "Autoři" na základě celkového počtu
        pocet_autoru = len(autori)

        # Vytvoření embedu
        embed = discord.Embed(
            title="Citát",
            color=discord.Color.purple()
        )
        
        # Pokud je pingnut uživatel, přidej jeho profilovku jako thumbnail
        if self.mention_users:
            embed.set_thumbnail(url=self.mention_users[0].display_avatar.url)
        
        embed.add_field(name="Autor" if pocet_autoru == 1 else "Autoři", value=autori_text, inline=True)
        embed.add_field(name="Datum a čas", value=f"{datum_text} {cas_text}", inline=True)
        embed.add_field(name="Citát", value=f"\"{self.citat_text.value}\"", inline=False)
        embed.set_footer(text=f"Vytvořil: {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)

class Citaty(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="citat", description="Udělej citát")
    async def citat_command(
        self, 
        interaction: discord.Interaction, 
        pingniautora1: Optional[discord.Member] = None,
        pingniautora2: Optional[discord.Member] = None,
        pingniautora3: Optional[discord.Member] = None
    ):
        # Sestavení seznamu uživatelů k pingu
        mention_users = [user for user in [pingniautora1, pingniautora2, pingniautora3] if user is not None]
        await interaction.response.send_modal(CitatModal(mention_users=mention_users))

async def setup(bot: commands.Bot):
    await bot.add_cog(Citaty(bot))