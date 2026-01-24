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
            invite_url = None
            try:
                # Create a single-use invite so you can share it even if DM fails
                channel_for_invite = interaction.guild.system_channel
                if channel_for_invite is None:
                    for ch in interaction.guild.text_channels:
                        perms = ch.permissions_for(interaction.guild.me)
                        if perms.create_instant_invite:
                            channel_for_invite = ch
                            break

                if channel_for_invite is not None:
                    invite = await channel_for_invite.create_invite(
                        max_age=60 * 60 * 24,
                        max_uses=1,
                        unique=True,
                        reason=f"UnbanMatyMythic invite pro {target_user}"
                    )
                    invite_url = str(invite.url)
            except Exception:
                invite_url = None

            await interaction.guild.unban(
                target_user, 
                reason=f"UnbanMatyMythic příkaz použitý uživatelem {user.name}"
            )
            
            # Try to send DM to the unbanned user
            dm_sent = False
            dm_error = None
            try:
                dm = await target_user.create_dm()
                message = (
                    f"Ahoj! Byl/a jsi odbanován/a na **{interaction.guild.name}**.\n"
                    f"Pozvánka: {invite_url if invite_url else 'požádej admina o invite (nepodařilo se ho vytvořit)'}"
                )
                await dm.send(message, allowed_mentions=discord.AllowedMentions.none())
                dm_sent = True
            except discord.Forbidden as e:
                dm_error = f"Forbidden (DM zavřené / bez mutual serveru): {e}"
            except discord.HTTPException as e:
                dm_error = f"HTTPException: {e}"
            except Exception as e:
                dm_error = f"{type(e).__name__}: {e}"
            
            embed = discord.Embed(
                title="✅ Uživatel odbanován!",
                description=f"**{target_user.mention}** ({target_user.name}) byl/a odbanován/a!\n\n"
                           f"👤 ID: `{target_user.id}`\n"
                           f"💬 DM zpráva: {'✅ Odeslána' if dm_sent else '❌ Nepodařilo se odeslat'}\n"
                           f"🔗 Invite: {invite_url if invite_url else 'Nepodařilo se vytvořit'}",
                color=discord.Color.green()
            )
            if (not dm_sent) and dm_error:
                embed.add_field(name="Proč DM nešlo", value=dm_error[:1024], inline=False)
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


