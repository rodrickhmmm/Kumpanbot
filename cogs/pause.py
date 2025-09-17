import discord
from discord.ext import commands

class Pause(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="pauzni", description="Pozastaví aktuální hudbu.")
    async def pause_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc or not vc.is_playing():
            await interaction.response.send_message("Není co pauznout.", ephemeral=True)
            return
        if vc.is_paused():
            await interaction.response.send_message("Už je hudba pauzlá.", ephemeral=True)
            return
        vc.pause()
        await interaction.response.send_message("⏸️ Pauznuto.")
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="pauzni")
    async def pause(self, ctx: commands.Context):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.reply("Není co pauznout.")
        if vc.is_paused():
            return await ctx.reply("Už je hudba pauzlá.")
        vc.pause()
        await ctx.reply("⏸️ Pauznuto.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Pause(bot))
