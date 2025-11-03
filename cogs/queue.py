import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class Queue(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="fronta", description="Zobrazí frontu skladeb.")
    async def queue_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(interaction.guild)
        if gm.current is None and not gm.queue:
            await interaction.response.send_message("Fronta skladeb je prázdná.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 Fronta skladeb",
            color=discord.Color.purple()
        )
        
        # Currently playing
        if gm.current:
            current_text = f"**{gm.current.title}**"
            if gm.current.uploader:
                current_text += f"\n*{gm.current.uploader}*"
            embed.add_field(name="🎵 Teď hraje", value=current_text, inline=False)
        
        # Queue
        if gm.queue:
            queue_text = ""
            for i, t in enumerate(list(gm.queue)[:10], start=1):
                queue_text += f"`{i}.` **{t.title}**"
                if t.uploader:
                    queue_text += f" • *{t.uploader}*"
                queue_text += f"\n"
            
            if len(gm.queue) > 10:
                queue_text += f"\n*...a ještě {len(gm.queue) - 10} skladeb*"
            
            embed.add_field(name="📑 Další ve frontě", value=queue_text, inline=False)
            embed.set_footer(text=f"Celkem skladeb ve frontě: {len(gm.queue)}")
        else:
            embed.add_field(name="📑 Další ve frontě", value="*Fronta je prázdná*", inline=False)
        
        # Add thumbnail from current track
        if gm.current and gm.current.thumbnail:
            embed.set_thumbnail(url=gm.current.thumbnail)
        
        await interaction.response.send_message(embed=embed)
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="fronta", aliases=["f"])
    async def queue(self, ctx: commands.Context):
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(ctx.guild)

        if gm.current is None and not gm.queue:
            return await ctx.reply("Fronta je prázdná.")

        embed = discord.Embed(
            title="📋 Fronta skladeb",
            color=discord.Color.purple()
        )
        
        # Currently playing
        if gm.current:
            current_text = f"**{gm.current.title}**"
            if gm.current.uploader:
                current_text += f"\n*{gm.current.uploader}*"
            embed.add_field(name="🎵 Teď hraje", value=current_text, inline=False)
        
        # Queue
        if gm.queue:
            queue_text = ""
            for i, t in enumerate(list(gm.queue)[:10], start=1):
                queue_text += f"`{i}.` **{t.title}**"
                if t.uploader:
                    queue_text += f" • *{t.uploader}*"
                queue_text += f"\n"
            
            if len(gm.queue) > 10:
                queue_text += f"\n*...a ještě {len(gm.queue) - 10} skladeb*"
            
            embed.add_field(name="📑 Další ve frontě", value=queue_text, inline=False)
            embed.set_footer(text=f"Celkem skladeb ve frontě: {len(gm.queue)}")
        else:
            embed.add_field(name="📑 Další ve frontě", value="*Fronta je prázdná*", inline=False)
        
        # Add thumbnail from current track
        if gm.current and gm.current.thumbnail:
            embed.set_thumbnail(url=gm.current.thumbnail)
        
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Queue(bot))
