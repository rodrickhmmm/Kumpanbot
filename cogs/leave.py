import discord
from discord.ext import commands

class Leave(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="leave", description="Bot opustí voice channel.")
    async def leave_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        guild = interaction.guild
        if not guild or not guild.voice_client:
            await interaction.response.send_message("The bot is not in a voice channel.", ephemeral=True)
            return
        await guild.voice_client.disconnect(force=True)
        await interaction.response.send_message("👋 Left the voice channel.")

    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="leave", aliases=["disconnect"])
    async def leave(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("The bot is not in a voice channel.")
        await ctx.voice_client.disconnect(force=True)
        await ctx.reply("👋 Left the voice channel.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Leave(bot))
