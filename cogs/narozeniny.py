import discord
from discord.ext import commands
from datetime import datetime

class Birthday(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="narozeniny", description="Popřej uživateli k narozeninám!")
    async def birthday_slash(self, interaction: discord.Interaction, uživatel: discord.Member, přání: str = None):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na serveru.", ephemeral=True)
            return
        
        # Default wish if none provided
        wish_text = přání if přání else "Hodně štěstí, zdraví, lásky a všeho nejlepšího do dalších let! 🥳"
        
        embed = discord.Embed(
            title=f"🎉🎂 Všechno nejlepší k narozeninám {uživatel.display_name}! 🎂🎉",
            description=f"**{user.mention}** přeje **{uživatel.mention}** krásné narozeniny!",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="🎁 Přání",
            value=wish_text,
            inline=False
        )
        
        # Birthday GIF
        embed.set_image(url="https://media.tenor.com/wTRjLBvlGQYAAAAd/birthday-nyx.gif")
        
        embed.set_footer(text=f"🎈 Oslavuj svůj den! • {datetime.now().strftime('%d.%m.%Y')}")
        
        await interaction.response.send_message(embed=embed)
    
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="narozeniny", aliases=["birthday", "bday"])
    async def birthday(self, ctx: commands.Context, member: discord.Member = None, *, wish: str = None):
        if not member:
            return await ctx.reply("Musíš označit uživatele! Použij: `k!narozeniny @uživatel [přání]`")
        
        # Default wish if none provided
        wish_text = wish if wish else "Hodně štěstí, zdraví, lásky a všeho nejlepšího do dalších let! 🥳"
        
        embed = discord.Embed(
            title="🎉🎂 Všechno nejlepší k narozeninám! 🎂🎉",
            description=f"**{ctx.author.mention}** přeje **{member.mention}** krásné narozeniny!",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="🎁 Přání",
            value=wish_text,
            inline=False
        )
        
        embed.set_image(url="https://media.tenor.com/wTRjLBvlGQYAAAAd/birthday-nyx.gif")
        embed.set_footer(text=f"🎈 Oslavuj svůj den! • {datetime.now().strftime('%d.%m.%Y')}")
        
        await ctx.send(f"{member.mention}", embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Birthday(bot))
