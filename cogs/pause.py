import discord
from discord.ext import commands

class Pause(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="pause", description="Pozastaví aktuální hudbu.")
    async def pause_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc or not vc.is_playing():
            await interaction.response.send_message("Nothing to pause.", ephemeral=True)
            return
        if vc.is_paused():
            await interaction.response.send_message("Already paused.", ephemeral=True)
            return
        vc.pause()
        await interaction.response.send_message("⏸️ Paused.")
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.reply("Nothing to pause.")
        if vc.is_paused():
            return await ctx.reply("Already paused.")
        vc.pause()
        await ctx.reply("⏸️ Paused.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Pause(bot))
