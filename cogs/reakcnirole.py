import discord
from discord.ext import commands
from discord import app_commands

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Dictionary to store reaction role mappings: {message_id: {emoji: role_id}}
        self.reaction_roles = {}
    
    @app_commands.command(name="reakcnirole", description="Nastaví reakci na zprávu, která přidá roli")
    @app_commands.describe(
        message_id="ID zprávy (pravý klik na zprávu -> Kopírovat ID)",
        emoji="Emoji pro reakci",
        role="Role, která se přidá"
    )
    async def setup_reaction_role(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
        role: discord.Role
    ):
        # Check permissions
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("Nemáš oprávnění spravovat role!", ephemeral=True)
            return
        
        try:
            # Get the message
            message = None
            for channel in interaction.guild.text_channels:
                try:
                    message = await channel.fetch_message(int(message_id))
                    if message:
                        break
                except:
                    continue
            
            if not message:
                await interaction.response.send_message("Zprávu se nepodařilo najít!", ephemeral=True)
                return
            
            # Add reaction to the message
            await message.add_reaction(emoji)
            
            # Store the reaction role mapping
            if message.id not in self.reaction_roles:
                self.reaction_roles[message.id] = {}
            self.reaction_roles[message.id][str(emoji)] = role.id
            
            embed = discord.Embed(
                title="✅ Reakční role nastavena!",
                description=f"Reakce {emoji} na zprávu přidá roli {role.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message("Nemám oprávnění přidat reakci nebo upravit role!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Neplatné ID zprávy!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Chyba: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="odstranreakcnirole", description="Odstraní reakční role ze zprávy")
    @app_commands.describe(
        message_id="ID zprávy",
        emoji="Emoji reakce k odstranění"
    )
    async def remove_reaction_role(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str
    ):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("Nemáš oprávnění spravovat role!", ephemeral=True)
            return
        
        try:
            msg_id = int(message_id)
            if msg_id in self.reaction_roles and str(emoji) in self.reaction_roles[msg_id]:
                del self.reaction_roles[msg_id][str(emoji)]
                if not self.reaction_roles[msg_id]:
                    del self.reaction_roles[msg_id]
                await interaction.response.send_message(f"✅ Reakční role {emoji} byla odstraněna!", ephemeral=True)
            else:
                await interaction.response.send_message("Tato reakční role nebyla nalezena!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Neplatné ID zprávy!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Chyba: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="listreakcnichroli", description="Zobrazí všechny nastavené reakční role")
    async def list_reaction_roles(self, interaction: discord.Interaction):
        if not self.reaction_roles:
            await interaction.response.send_message("Žádné reakční role nejsou nastavené!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 Reakční role",
            color=discord.Color.purple()
        )
        
        for msg_id, reactions in self.reaction_roles.items():
            roles_text = []
            for emoji, role_id in reactions.items():
                role = interaction.guild.get_role(role_id)
                if role:
                    roles_text.append(f"{emoji} → {role.mention}")
            
            if roles_text:
                embed.add_field(
                    name=f"Zpráva ID: {msg_id}",
                    value="\n".join(roles_text),
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Ignore bot reactions
        if payload.member.bot:
            return
        
        # Check if this message has reaction roles set up
        if payload.message_id not in self.reaction_roles:
            return
        
        emoji_str = str(payload.emoji)
        if emoji_str not in self.reaction_roles[payload.message_id]:
            return
        
        # Get the role and add it to the user
        guild = self.bot.get_guild(payload.guild_id)
        role_id = self.reaction_roles[payload.message_id][emoji_str]
        role = guild.get_role(role_id)
        
        if role:
            try:
                await payload.member.add_roles(role, reason="Reakční role")
            except discord.Forbidden:
                print(f"Nemám oprávnění přidat roli {role.name} uživateli {payload.member.name}")
            except Exception as e:
                print(f"Chyba při přidávání role: {e}")
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # Check if this message has reaction roles set up
        if payload.message_id not in self.reaction_roles:
            return
        
        emoji_str = str(payload.emoji)
        if emoji_str not in self.reaction_roles[payload.message_id]:
            return
        
        # Get the role and remove it from the user
        guild = self.bot.get_guild(payload.guild_id)
        role_id = self.reaction_roles[payload.message_id][emoji_str]
        role = guild.get_role(role_id)
        member = guild.get_member(payload.user_id)
        
        if role and member and not member.bot:
            try:
                await member.remove_roles(role, reason="Reakční role odstraněna")
            except discord.Forbidden:
                print(f"Nemám oprávnění odebrat roli {role.name} uživateli {member.name}")
            except Exception as e:
                print(f"Chyba při odebírání role: {e}")

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
