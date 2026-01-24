import discord
from discord.ext import commands


class Grok(commands.Cog):
	from discord import app_commands

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="grok", description="Grok, je to pravda?")
	@app_commands.describe(text="Text který má Grok napsat")

	async def grok_slash(self, interaction: discord.Interaction, text: str):
		if not text or not text.strip():
			await interaction.response.send_message("Tak co mám říct ty kokote?", ephemeral=True)
			return

		# discord je mldka a neumi dlouhy embedy
		safe_text = text.strip()
		if len(safe_text) > 4096:
			safe_text = safe_text[:4093] + "..."

		icon_url = "https://i.redd.it/kuwycuuzjsoe1.jpeg"

		embed = discord.Embed(description=safe_text, color=discord.Color.purple())
		embed.set_author(name="Grok", icon_url=icon_url if icon_url else discord.Embed.Empty)

		await interaction.response.send_message(
			embed=embed,
			allowed_mentions=discord.AllowedMentions.none(),
		)


async def setup(bot: commands.Bot):
	await bot.add_cog(Grok(bot))

