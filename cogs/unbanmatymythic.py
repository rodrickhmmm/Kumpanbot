import discord
from discord.ext import commands

class UnbanMatyMythic(commands.Cog):
    from discord import app_commands

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="unbanmatymythic", description="Odbanuje matyho.")
    async def unbanmatymythic_slash(
        self, 
        interaction: discord.Interaction
    ):
        # Defer the response immediately to prevent timeout
        await interaction.response.defer()
        
        user = interaction.user
        
        # Check if user is on a server
        if not isinstance(user, discord.Member):
            await interaction.followup.send("Tenhle příkaz můžeš použít jen na serveru.", ephemeral=True)
            return
        
        # Check if user has ban permissions
        if not user.guild_permissions.ban_members:
            await interaction.followup.send("Nemáš oprávnění odbanovat matyho!", ephemeral=True)
            return
        
        # Hardcoded user ID to unban
        TARGET_USER_ID = 1150085087451435102  # Same user ID as in banmatymythic
        
        # Try to fetch the user
        try:
            target_user = await self.bot.fetch_user(TARGET_USER_ID)
        except discord.NotFound:
            await interaction.followup.send(
                f"Maty nebyl nalezen!", 
                ephemeral=True
            )
            return
        except Exception as e:
            await interaction.followup.send(
                f"Chyba při hledání uživatele: {str(e)}", 
                ephemeral=True
            )
            return
        
        # Perform the unban
        try:
            await interaction.guild.unban(
                target_user, 
                reason=f"UnbanMatyMythic příkaz použitý uživatelem {user.name}"
            )
            
            # Try to send DM to the unbanned user
            dm_sent = False
            try:
                await target_user.send(f"Magic je kretén a Ocasník nebo Rodrick tě pozval zpátky na **{interaction.guild.name}**!\n\nMTady máš invite:\nhttps://dsc.gg/mymkumpanum")
                print(f"Poslal jsem zprávu konince {target_user.name}")
                dm_sent = True
            except Exception:
                # User has DMs disabled or any other error sending DM
                pass
            
            embed = discord.Embed(
                title="✅ Uživatel odbanován!",
                description=f"**{target_user.mention}** ({target_user.name}) byl/a odbanován/a!\n\n"
                           f"👤 ID: `{target_user.id}`\n"
                           f"💬 DM zpráva: {'✅ Odeslána' if dm_sent else '❌ Nepodařilo se odeslat, pošli mu to manuálně: https://dsc.gg/mymkumpanum'}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Odbanoval/a: {user.name}")
            
            if hasattr(target_user, 'avatar') and target_user.avatar:
                embed.set_thumbnail(url=target_user.avatar.url)
            
            await interaction.followup.send(embed=embed)
            
        except discord.Forbidden:
            await interaction.followup.send(
                "Nemám oprávnění odbanovat uživatele na tomto serveru!", 
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"Nastala chyba při odbanování: {str(e)}", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"Neočekávaná chyba: {str(e)}", 
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(UnbanMatyMythic(bot))


