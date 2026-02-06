
import io
import math
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands


def _cover_resize(img, size: tuple[int, int]):
	"""Resize+crop image to fully cover the target size (center crop)."""
	target_w, target_h = size
	src_w, src_h = img.size

	if src_w <= 0 or src_h <= 0:
		raise ValueError("Invalid image dimensions")

	scale = max(target_w / src_w, target_h / src_h)
	new_w = max(1, int(math.ceil(src_w * scale)))
	new_h = max(1, int(math.ceil(src_h * scale)))

	img = img.resize((new_w, new_h))
	left = max(0, (new_w - target_w) // 2)
	top = max(0, (new_h - target_h) // 2)
	return img.crop((left, top, left + target_w, top + target_h))


def _paste_cover(img, canvas, box: tuple[int, int, int, int]):
	"""Paste img into canvas filling box using a cover-resize (center-crop)."""
	left, top, right, bottom = box
	w = max(1, int(right - left))
	h = max(1, int(bottom - top))
	fitted = _cover_resize(img, (w, h)).convert("RGBA")
	canvas.paste(fitted, (int(left), int(top)))


class HorsiNezModrej(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(
		name="horsinezmodrej",
		description="Přidá tvůj obrázek pod šablonu (PNG s transparencí).",
	)
	@app_commands.describe(obrazek="Obrázek, který se vloží pod šablonu")
	async def horsinezmodrej(self, interaction: discord.Interaction, obrazek: discord.Attachment):
		# Lazy import so the bot can start even if Pillow isn't installed.
		try:
			from PIL import Image  # type: ignore
		except ModuleNotFoundError:
			await interaction.response.send_message(
				"Chybí knihovna Pillow (PIL). Admin musí doinstalovat `pillow` do venv: `pip install pillow`.",
				ephemeral=True,
			)
			return

		if not obrazek.content_type or not obrazek.content_type.startswith("image/"):
			await interaction.response.send_message("Pošli prosím obrázek (PNG/JPG/WebP…).", ephemeral=True)
			return

		await interaction.response.defer()

		# Load template (overlay) from repo root
		template_path = Path(__file__).resolve().parents[1] / "horsinezmodrejtemplate.png"
		if not template_path.exists():
			await interaction.followup.send("Nemůžu najít šablonu `horsinezmodrejtemplate.png` v rootu repa.")
			return
		try:
			overlay = Image.open(template_path).convert("RGBA")
			data = await obrazek.read()
			user_img = Image.open(io.BytesIO(data)).convert("RGBA")
		except Exception as e:
			await interaction.followup.send(f"Obrázek/šablona nejde načíst: {type(e).__name__}: {e}")
			return

		# Fit background to overlay size
		# Transparent rectangle (top-left): 452x479 at (0,0)
		# User image should be fitted ONLY into this region.
		bg = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
		_paste_cover(user_img, bg, (0, 0, 452, 479))

		# Composite overlay on top (uses overlay alpha)
		try:
			result = bg.copy()
			# Pillow >= 8 supports alpha_composite as method
			result.alpha_composite(overlay)
		except Exception:
			# Fallback for older versions
			result = bg.copy()
			result.paste(overlay, (0, 0), overlay)

		out = io.BytesIO()
		out.name = "horsinezmodrej.png"
		result.save(out, format="PNG")
		out.seek(0)

		await interaction.followup.send(file=discord.File(out, filename="horsinezmodrej.png"))


async def setup(bot: commands.Bot):
	await bot.add_cog(HorsiNezModrej(bot))

