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
        
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(guild)
        
        # Get info about what's next
        next_track = None
        if gm.queue:
            next_track = list(gm.queue)[0]
        
        await mgr.skip(interaction)
        
        # Use followup since we deferred
        try:
            embed = discord.Embed(
                title="⏭️ Skladba přeskočena",
                color=discord.Color.purple()
            )
            
            if next_track:
                embed.description = f"**Přehrávám další:**\n{next_track.title}"
                if next_track.thumbnail:
                    embed.set_thumbnail(url=next_track.thumbnail)
                if next_track.uploader:
                    embed.add_field(name="Autor", value=next_track.uploader, inline=True)
            else:
                embed.description = "*Fronta je prázdná*"
            
            embed.set_footer(text=f"Požádal {user.display_name}", icon_url=user.display_avatar.url)
            await interaction.followup.send(embed=embed)
        except Exception:
            pass  # Ignore if followup fails
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="preskocit", aliases=["s"])
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.reply("Řinčák není v chcallu.")
        
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(ctx.guild)
        
        # Get info about what's next
        next_track = None
        if gm.queue:
            next_track = list(gm.queue)[0]
        
        await mgr.skip(ctx)
        
        embed = discord.Embed(
            title="⏭️ Skladba přeskočena",
            color=discord.Color.purple()
        )
        
        if next_track:
            embed.description = f"**Přehrávám další:**\n{next_track.title}"
            if next_track.thumbnail:
                embed.set_thumbnail(url=next_track.thumbnail)
            if next_track.uploader:
                embed.add_field(name="Autor", value=next_track.uploader, inline=True)
        else:
            embed.description = "*Fronta je prázdná*"
        
        embed.set_footer(text=f"Požádal {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Skip(bot))
