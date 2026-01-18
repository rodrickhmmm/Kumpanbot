import discord
from discord.ext import commands

class obnovityMaty(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="obnovitymaty", description="Přidáš uživateli role který měl maty.")
    @app_commands.describe(
        uzivatel="Uživatel, kterého chceš poslat do gulagu"
    )
    
    async def obnovitymaty_slash(
        self, 
        interaction: discord.Interaction, 
        uzivatel: discord.Member
    ):
        user = interaction.user
        
        # Check if user is admin or has manage roles permission
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na serveru.", ephemeral=True)
            return
        
        if not user.guild_permissions.manage_roles:
            await interaction.response.send_message("Nemáš oprávnění spravovat role!", ephemeral=True)
            return
        
        # Don't gulag yourself
        if uzivatel.id == user.id:
            await interaction.response.send_message("Nemůžeš dát tyhle role sám sobě!", ephemeral=True)
            return
        
        # Don't gulag the bot
        if uzivatel.bot:
            await interaction.response.send_message("Nemůžeš dát tyhle role botovi!", ephemeral=True)
            return
        
        # Find the roles
        role_ids = [1414610117751476254, 1368282943096750231, 1404468232823242886, 1368268277146452009, 1462518506728718357]
        roles_to_add = [interaction.guild.get_role(role_id) for role_id in role_ids]
        roles_to_add = [role for role in roles_to_add if role is not None]
        
        if not roles_to_add:
            await interaction.response.send_message(f"Žádná z rolí se nepodařilo najít na serveru!", ephemeral=True)
            return
        
        # Perform the role changes
        try:
            await uzivatel.add_roles(*roles_to_add, reason=f"Obnovení Matyho od {user.name}")
            
            role_mentions = ", ".join([role.mention for role in roles_to_add])
            
            embed = discord.Embed(
                title="✅ Obnoveny Matyho role!",
                description=f"**{uzivatel.mention}** dostal zpět své role!\n\n"
                           f"✅ Přidané role: {role_mentions}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Provedl/a: {user.name}")
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "Nemám oprávnění měnit role tohoto uživatele!", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Nastala chyba při změně rolí: {str(e)}", 
                ephemeral=True
            )
    
    def __init__(self, bot): 
        self.bot = bot

async def setup(bot):
    await bot.add_cog(obnovityMaty(bot))
