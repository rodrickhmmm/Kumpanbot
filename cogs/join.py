from discord.ext import commands
from core.music_manager import MusicManager
import discord
from discord.ext import commands
from discord import app_commands

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pripoj")
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply("Nejdříve musíš být **v chcallu** ty voříšku!!!!")
        await get_manager(self.bot).ensure_voice(ctx)
        await ctx.reply("✅ Připojil se do chcallu.")
        
    @app_commands.command(name="pripoj", description="Řinčák se připojí do chcallu.")
    async def join(self, interaction: discord.Interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        if not user.voice or not user.voice.channel:
            await interaction.response.send_message("Nejdříve musíš být **v chcallu** ty voříšku!!!!", ephemeral=True)
            return
        await get_manager(self.bot).ensure_voice(interaction)
        await interaction.response.send_message("✅ Připojil se do chcallu.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Join(bot))
