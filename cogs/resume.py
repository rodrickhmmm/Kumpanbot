import discord
from discord.ext import commands

class Resume(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="pokracuj", description="Pokračuje v přehrávání hudby.")
    async def resume_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc:
            await interaction.response.send_message("The bot is not in a voice channel.", ephemeral=True)
            return
        if not vc.is_paused():
            await interaction.response.send_message("The music is not paused.", ephemeral=True)
            return
        vc.resume()
        await interaction.response.send_message("▶️ Resumed playing.")
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="pokracuj", aliases=["unpause", "continue"])
    async def resume(self, ctx: commands.Context):
        vc = ctx.voice_client
        if not vc:
            return await ctx.reply("The bot is not in a voice channel.")
        if not vc.is_paused():
            return await ctx.reply("The music is not paused.")
        vc.resume()
        await ctx.reply("▶️ Resumed playing.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Resume(bot))
