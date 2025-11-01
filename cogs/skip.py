import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Skip(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="preskocit", description="Přeskočí aktuální skladbu.")
    async def skip_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        guild = interaction.guild
        if not guild.voice_client:
            await interaction.response.send_message("Řinčák není v chcallu.", ephemeral=True)
            return
        
        # Defer the response first to avoid timeout issues
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        await get_manager(self.bot).skip(interaction)
        
        # Use followup since we deferred
        try:
            await interaction.followup.send("⏭️ Skladba přeskočena.")
        except Exception:
            pass  # Ignore if followup fails
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="preskocit", aliases=["s"])
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("Řinčák není v chcallu.")
        await get_manager(self.bot).skip(ctx)
        await ctx.reply("⏭️ Skladba přeskočena.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Skip(bot))
