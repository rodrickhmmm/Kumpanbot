import discord
from discord.ext import commands

class BanMatyMythic(commands.Cog):
    from discord import app_commands

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="banmatymythic", description="Zabanuje matyho.")
    async def banmatymythic_slash(
        self, 
        interaction: discord.Interaction
    ):
        user = interaction.user
        
        # Check if user is on a server
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš použít jen na serveru.", ephemeral=True)
            return
        
        # Check if user has ban permissions
        if not user.guild_permissions.ban_members:
            await interaction.response.send_message("Nemáš oprávnění banovat matyho!", ephemeral=True)
            return
        
        # Hardcoded user ID to ban (replace with the actual user ID you want to ban)
        TARGET_USER_ID = 1150085087451435102  # Replace with the specific user ID
        
        # Try to get the member from the guild
        target_member = interaction.guild.get_member(TARGET_USER_ID)
        
        if not target_member:
            # User might not be in the server, try to fetch user object
            try:
                target_user = await self.bot.fetch_user(TARGET_USER_ID)
            except discord.NotFound:
                await interaction.response.send_message(
                    f"Maty nebyl nalezen!", 
                    ephemeral=True
                )
                return
            except Exception as e:
                await interaction.response.send_message(
                    f"Chyba při hledání uživatele: {str(e)}", 
                    ephemeral=True
                )
                return
        else:
            target_user = target_member
            
            # Don't ban yourself
            if target_member.id == user.id:
                await interaction.response.send_message("Nemůžeš zabanovat sám sebe!", ephemeral=True)
                return
            
            # Don't ban the bot
            if target_member.bot and target_member.id == self.bot.user.id:
                await interaction.response.send_message("Nemůžeš zabanovat mě!", ephemeral=True)
                return
            
            # Check role hierarchy
            if target_member.top_role >= user.top_role:
                await interaction.response.send_message(
                    "Nemůžeš zabanovat matyho s vyšší nebo stejnou rolí!", 
                    ephemeral=True
                )
                return
            
            bot_member = interaction.guild.get_member(self.bot.user.id)
            if target_member.top_role >= bot_member.top_role:
                await interaction.response.send_message(
                    "Nemohu zabanovat matyho s vyšší nebo stejnou rolí než já!", 
                    ephemeral=True
                )
                return
        
        # Perform the ban
        try:
            await interaction.guild.ban(
                target_user, 
                reason=f"BanMatyMythic příkaz použitý uživatelem {user.name}",
                delete_message_seconds=0  # Don't delete messages
            )
            
            embed = discord.Embed(
                title="🔨 Uživatel zabanován!",
                description=f"**{target_user.mention}** ({target_user.name}) byl/a zabanován/a!\n\n"
                           f"👤 ID: `{target_user.id}`",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Zabanoval/a: {user.name}")
            
            if hasattr(target_user, 'avatar') and target_user.avatar:
                embed.set_thumbnail(url=target_user.avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "Nemám oprávnění banovat uživatele na tomto serveru!", 
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"Nastala chyba při banování: {str(e)}", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Neočekávaná chyba: {str(e)}", 
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(BanMatyMythic(bot))
