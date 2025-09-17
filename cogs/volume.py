import discord
import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Volume(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="hlasitost", description="Nastaví hlasitost bota (0-200).")
    async def volume_slash(self, interaction, vol: int):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        if not 0 <= vol <= 200:
            await interaction.response.send_message("Úroveň hlasitostí musí být mezi 0 a 200.", ephemeral=True)
            return
        guild = interaction.guild
        vc = guild.voice_client if guild else None
        if not vc:
            await interaction.response.send_message("Řinčák není v chcallu.", ephemeral=True)
            return
        get_manager(self.bot).set_volume(vc, vol / 100.0)
        await interaction.response.send_message(f"🔊 Hlasitost: {vol}%")
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="hlasitost", aliases=["hlas"])
    async def volume(self, ctx: commands.Context, vol: int = None):
        if vol is None:
            return await ctx.reply("Hlasitost: `o!vol <0-200>`")
        if not 0 <= vol <= 200:
            return await ctx.reply("Úroveň hlasitostí musí být mezi 0 a 200.")
        vc = ctx.voice_client
        if not vc:
            return await ctx.reply("The bot is not in a voice channel.")
        get_manager(self.bot).set_volume(vc, vol / 100.0)
        await ctx.reply(f"🔊 Hlasitost: {vol}%")

async def setup(bot: commands.Bot):
    await bot.add_cog(Volume(bot))
