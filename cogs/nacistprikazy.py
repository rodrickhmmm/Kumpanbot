
import discord
from discord.ext import commands


class NacistPrikazy(commands.Cog):
	from discord import app_commands

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="nacistprikazy", description="Znovu načte (sync) slash příkazy na tomto serveru.")
	@app_commands.default_permissions(administrator=True)
	@app_commands.describe(globalni="Když True, syncne i globálně (může se propsat až za delší dobu)")
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

		# Fast path: sync commands to this guild so changes appear instantly
		try:
			self.bot.tree.copy_global_to(guild=interaction.guild)
			synced = await self.bot.tree.sync(guild=interaction.guild)
		except Exception as e:
			await interaction.followup.send(f"Nepodařilo se syncnout příkazy: {type(e).__name__}: {e}", ephemeral=True)
			return

		extra = ""
		if globalni:
			try:
				await self.bot.tree.sync()
				extra = "\nGlobální sync odeslán (může se propsat později)."
			except Exception as e:
				extra = f"\nGlobální sync se nepovedl: {type(e).__name__}: {e}"

		names = ", ".join(sorted({cmd.name for cmd in synced}))
		await interaction.followup.send(
			f"✅ Synced {len(synced)} příkazů pro server **{interaction.guild.name}**.{extra}\n"
			f"Příkazy: {names}",
			ephemeral=True,
		)


async def setup(bot: commands.Bot):
	await bot.add_cog(NacistPrikazy(bot))

