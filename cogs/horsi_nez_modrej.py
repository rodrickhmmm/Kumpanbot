
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


def _load_font(ImageFont, size: int):
	# Try common fonts on Linux (RPi) and Windows.
	candidates = [
		"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
		"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
		"/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
		"/usr/share/fonts/truetype/freefont/FreeSans.ttf",
		"C:/Windows/Fonts/arial.ttf",
		"C:/Windows/Fonts/Arial.ttf",
	]
	for path in candidates:
		try:
			return ImageFont.truetype(path, size=size)
		except Exception:
			pass
	return ImageFont.load_default()


def _fit_text(ImageDraw, ImageFont, text: str, box_w: int, box_h: int):
	# Returns (font, final_text)
	text = (text or "").strip()
	if not text:
		return None, ""

	min_size = 8
	max_size = max(min_size, box_h)  # start around box height
	# Leave tiny padding inside the box
	pad_w = 6
	pad_h = 4
	max_w = max(1, box_w - pad_w)
	max_h = max(1, box_h - pad_h)

	# Use a dummy draw for measurement
	dummy_img = __import__("PIL.Image").Image.new("RGBA", (1, 1), (0, 0, 0, 0))
	draw = ImageDraw.Draw(dummy_img)

	def text_fits(font_obj, s: str) -> bool:
		bbox = draw.textbbox((0, 0), s, font=font_obj)
		w = bbox[2] - bbox[0]
		h = bbox[3] - bbox[1]
		return w <= max_w and h <= max_h

	best_font = None
	for size in range(max_size, min_size - 1, -1):
		font_obj = _load_font(ImageFont, size)
		if text_fits(font_obj, text):
			best_font = font_obj
			return best_font, text

	# If nothing fits even at min font, truncate with ellipsis
	font_obj = _load_font(ImageFont, min_size)
	if text_fits(font_obj, text):
		return font_obj, text

	ellipsis = "…"
	base = text
	lo, hi = 0, len(base)
	best = ""
	while lo <= hi:
		mid = (lo + hi) // 2
		cand = (base[:mid].rstrip() + ellipsis) if mid < len(base) else base
		if text_fits(font_obj, cand):
			best = cand
			lo = mid + 1
		else:
			hi = mid - 1
	return font_obj, best or ellipsis


class HorsiNezModrej(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(
		name="horsinezmodrej",
		description="Přidá tvůj obrázek pod šablonu (PNG s transparencí).",
	)
	@app_commands.describe(
		obrazek="Obrázek, který se vloží pod šablonu",
		text="Text do boxu (automaticky zmenší font když je dlouhý)",
	)
	async def horsinezmodrej(self, interaction: discord.Interaction, obrazek: discord.Attachment, text: str = ""):
		# Lazy import so the bot can start even if Pillow isn't installed.
		try:
			from PIL import Image, ImageDraw, ImageFont  # type: ignore
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

		# Render text into box: top-left (136,518), size 216x37
		text_box = (136, 518, 136 + 216, 518 + 37)
		box_w = 216
		box_h = 37
		font_obj, final_text = _fit_text(ImageDraw, ImageFont, text, box_w, box_h)
		if final_text and font_obj is not None:
			draw = ImageDraw.Draw(result)
			bbox = draw.textbbox((0, 0), final_text, font=font_obj)
			tw = bbox[2] - bbox[0]
			th = bbox[3] - bbox[1]
			x = text_box[0] + (box_w - tw) // 2
			y = text_box[1] + (box_h - th) // 2
			# Simple black text (assumes template area is light)
			draw.text((x, y), final_text, font=font_obj, fill=(0, 0, 0, 255))

		out = io.BytesIO()
		out.name = "horsinezmodrej.png"
		result.save(out, format="PNG")
		out.seek(0)

		await interaction.followup.send(file=discord.File(out, filename="horsinezmodrej.png"))


async def setup(bot: commands.Bot):
	await bot.add_cog(HorsiNezModrej(bot))

