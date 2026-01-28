import discord
from discord.ext import commands

class Hug(commands.Cog):
    from discord import app_commands

    @app_commands.command(name="obejmout", description="Obejme uživatele.")
    async def hug_slash(self, interaction: discord.Interaction, uživatel: discord.Member):
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message("Tenhle příkaz můžeš poslat jen na serveru.", ephemeral=True)
            return
        
        # Don't hug yourself
        if uživatel.id == user.id:
            await interaction.response.send_message("Nemůžeš obejmout sám sebe! 🤗", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="Awww miluji objetí!",
            description=f"**{user.mention}** objal/a **{uživatel.mention}**!",
            color=discord.Color.purple()
        )
        
        # Add a cute GIF
        embed.set_image(url="https://media.tenor.com/UHkGT1FKjPQAAAAd/group-hug.gif")
        
        embed.set_footer(text="Pošli někomu objetí! 💜")
        
        await interaction.response.send_message(embed=embed)
    
    def __init__(self, bot): 
        self.bot = bot

    @commands.command(name="obejmout", aliases=["hug"])
    async def hug(self, ctx: commands.Context, member: discord.Member = None):
        if not member:
            return await ctx.reply("Musíš označit uživatele! Použij: `k!obejmout @uživatel`")
        
        if member.id == ctx.author.id:
            return await ctx.reply("Nemůžeš obejmout sám sebe! 🤗")
        
        embed = discord.Embed(
            title="🤗 Objetí!",
            description=f"**{ctx.author.mention}** objal/a **{member.mention}**!",
            color=discord.Color.purple()
        )
        
        embed.set_image(url="https://media.tenor.com/UHkGT1FKjPQAAAAd/group-hug.gif")
        embed.set_footer(text="Pošli někomu objetí! 💜")
        
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Hug(bot))
