import discord
from discord.ext import commands

class Anti_gulag(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="anti_gulag", description="Odstraní Anti_gulag roli uživateli.")
    @app_commands.describe(
        uzivatel="Uživatel, kterého chceš dostat z Anti_gulagu"
    )
    async def Anti_gulag_slash(
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
        
        # Don't Anti_gulag yourself
        if uzivatel.id == user.id:
            await interaction.response.send_message("Nemůžeš poslat do Anti_gulagu sám sebe!", ephemeral=True)
            return
        
        # Don't Anti_gulag the bot
        if uzivatel.bot:
            await interaction.response.send_message("Nemůžeš dostat bota z Anti_gulagu!", ephemeral=True)
            return
        
        # Hardcoded role IDs
        ROLE_TO_REMOVE_ID = 1391857788019413032
        ROLE_TO_ADD_ID = 1368259286005841960
        
        # Find the roles
        role_to_remove = interaction.guild.get_role(ROLE_TO_REMOVE_ID)
        role_to_add = interaction.guild.get_role(ROLE_TO_ADD_ID)
        
        if not role_to_remove:
            await interaction.response.send_message(f"Roli s ID `{ROLE_TO_REMOVE_ID}` se nepodařilo najít na serveru!", ephemeral=True)
            return
        
        if not role_to_add:
            await interaction.response.send_message(f"Roli s ID `{ROLE_TO_ADD_ID}` se nepodařilo najít na serveru!", ephemeral=True)
            return
        
        # Check if user has the role to remove
        if role_to_remove not in uzivatel.roles:
            await interaction.response.send_message(
                f"Uživatel {uzivatel.mention} nemá roli {role_to_remove.mention}!", 
                ephemeral=True
            )
            return
        
        # Check bot's role hierarchy
        bot_member = interaction.guild.get_member(self.bot.user.id)
        if role_to_remove >= bot_member.top_role or role_to_add >= bot_member.top_role:
            await interaction.response.send_message(
                "Nemohu spravovat tyto role - jsou vyšší než moje nejvyšší role!", 
                ephemeral=True
            )
            return
        
        # Check user's role hierarchy
        if role_to_remove >= user.top_role or role_to_add >= user.top_role:
            await interaction.response.send_message(
                "Nemůžeš spravovat tyto role - jsou vyšší nebo stejné jako tvoje nejvyšší role!", 
                ephemeral=True
            )
            return
        
        # Perform the role changes
        try:
            await uzivatel.remove_roles(role_to_remove, reason=f"Anti_gulag od {user.name}")
            await uzivatel.add_roles(role_to_add, reason=f"Anti_gulag od {user.name}")
            
            embed = discord.Embed(
                title="🏴 Z Anti_gulagu!",
                description=f"**{uzivatel.mention}** se dostal/a z Anti_gulagu!\n\n"
                           f"❌ Odebrána role: {role_to_remove.mention}\n"
                           f"✅ Přidána role: {role_to_add.mention}",
                color=discord.Color.red()
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
    await bot.add_cog(Anti_gulag(bot))

