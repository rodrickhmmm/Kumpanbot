import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

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
        
        # Get current track info
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(guild)
        
        vc.pause()
        
        embed = discord.Embed(
            title="⏸️ Hudba pozastavena",
            color=discord.Color.purple()
        )
        
        if gm.current:
            embed.description = f"**{gm.current.title}**"
            if gm.current.thumbnail:
                embed.set_thumbnail(url=gm.current.thumbnail)
            if gm.current.uploader:
                embed.add_field(name="Autor", value=gm.current.uploader, inline=True)
        
        embed.set_footer(text=f"Požádal {user.display_name}", icon_url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="pauzni")
    async def pause(self, ctx: commands.Context):
        vc = ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.reply("Není co pauznout.")
        if vc.is_paused():
            return await ctx.reply("Už je hudba pauzlá.")
        
        # Get current track info
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(ctx.guild)
        
        vc.pause()
        
        embed = discord.Embed(
            title="⏸️ Hudba pozastavena",
            color=discord.Color.purple()
        )
        
        if gm.current:
            embed.description = f"**{gm.current.title}**"
            if gm.current.thumbnail:
                embed.set_thumbnail(url=gm.current.thumbnail)
            if gm.current.uploader:
                embed.add_field(name="Autor", value=gm.current.uploader, inline=True)
        
        embed.set_footer(text=f"Požádal {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Pause(bot))
