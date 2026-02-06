
import discord
from discord.ext import commands


class NacistPrikazy(commands.Cog):
	from discord import app_commands

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="nacistprikazy", description="Znovu načte (sync) slash příkazy na tomto serveru.")
	@app_commands.default_permissions(administrator=True)
	async def nacistprikazy_slash(self, interaction: discord.Interaction, globalni: bool = False):
		# Must be used in a guild
		if interaction.guild is None:
			await interaction.response.send_message("Tenhle příkaz můžeš použít jen na serveru.", ephemeral=True)
			return

		# Extra runtime check (UI perms can lag)
		if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
			await interaction.response.send_message("Nemáš admin oprávnění.", ephemeral=True)
			return

		await interaction.response.defer(ephemeral=True)

		# 1) Smaž serverové (guild) příkazy – ty dělají duplicity vedle globálních
		try:
			self.bot.tree.clear_commands(guild=interaction.guild)
			await self.bot.tree.sync(guild=interaction.guild)
		except Exception as e:
			await interaction.followup.send(f"Nepodařilo se smazat serverové příkazy: {type(e).__name__}: {e}", ephemeral=True)
			return

		# 3) Sync globálních příkazů (bez vytváření guild kopií => žádné duplicity)
		try:
			synced = await self.bot.tree.sync()
			extra += "\nGlobální sync odeslán (může se propsat později)."
		except Exception as e:
			await interaction.followup.send(f"Globální sync se nepovedl: {type(e).__name__}: {e}", ephemeral=True)
			return

		names = ", ".join(sorted({cmd.name for cmd in synced}))
		await interaction.followup.send(
			f"✅ Serverové příkazy smazány + globální příkazy syncnuté.{extra}\nPříkazy: {names}",
			ephemeral=True,
		)


async def setup(bot: commands.Bot):
	await bot.add_cog(NacistPrikazy(bot))

