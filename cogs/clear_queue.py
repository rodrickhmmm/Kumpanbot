import discord
from discord.ext import commands
from core.music_manager import MusicManager

def get_manager(bot: commands.Bot) -> MusicManager:
    if not hasattr(bot, "music"):
        bot.music = MusicManager(bot)
    return bot.music

class ClearQueue(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="vycistitfrontu", description="Vyčistí frontu skladeb (aktuální skladba pokračuje).")
    async def clear_queue_slash(self, interaction):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na Mým Kumpánům.", ephemeral=True)
            return
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Tento příkaz nelze použít v DM.", ephemeral=True)
            return
        
        # Defer the response first
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        # Clear queue but keep current track playing
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(guild)
        queue_size = len(gm.queue)
        gm.queue.clear()
        
        # Use followup since we deferred
        try:
            if queue_size > 0:
                embed = discord.Embed(
                    title="🗑️ Fronta vyčištěna",
                    description=f"Odstraněno **{queue_size}** skladeb z fronty.",
                    color=discord.Color.purple()
                )
                embed.set_footer(text=f"Požádal {user.display_name}", icon_url=user.display_avatar.url)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("Fronta je už prázdná.", ephemeral=True)
        except Exception:
            pass  # Ignore if followup fails

    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="vycistitfrontu", aliases=["clearqueue", "cq"])
    async def clear_queue(self, ctx: commands.Context):
        mgr = get_manager(self.bot)
        gm = mgr.get_guild(ctx.guild)
        queue_size = len(gm.queue)
        gm.queue.clear()
        
        if queue_size > 0:
            await ctx.reply(f"🗑️ Fronta vyčištěna! Odstraněno **{queue_size}** skladeb.")
        else:
            await ctx.reply("Fronta je už prázdná.")

async def setup(bot: commands.Bot):
    await bot.add_cog(ClearQueue(bot))
