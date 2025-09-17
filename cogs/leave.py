import discord
from discord.ext import commands

class Leave(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="odpoj", description="Řinčák se odpojí ze chcallu.")
    async def leave_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        guild = interaction.guild
        if not guild or not guild.voice_client:
            await interaction.response.send_message("Nejsem ve chcallu ty kaštane.", ephemeral=True)
            return
        await guild.voice_client.disconnect(force=True)
        await interaction.response.send_message("👋 Odpojil jsem se z chcallu.")

    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="odpoj", aliases=["disconnect"])
    async def leave(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("Nejsem ve chcallu ty kaštane.")
        await ctx.voice_client.disconnect(force=True)
        await ctx.reply("👋 Odpojil jsem se z chcallu.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Leave(bot))
