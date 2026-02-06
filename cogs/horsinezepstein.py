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

def _load_font(ImageFont, size: int, *, debug: bool = False):
    # Try YouTube Sans in repo root first
    import os
    yt_sans_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "YouTubeSansBold.otf"),
    ]
    font_debug = []
    for path in yt_sans_paths:
        if debug:
            font_debug.append(f"Trying font: {path}")
        if os.path.isfile(path):
            try:
                if debug:
                    font_debug.append(f"File exists: {path}")
                font = ImageFont.truetype(path, size=size)
                return (font, font_debug) if debug else font
            except Exception as e:
                if debug:
                    font_debug.append(f"Failed to load {path}: {e}")
    if debug:
        font_debug.append("Falling back to default font")
    font = ImageFont.load_default()
    return (font, font_debug) if debug else font

def _fit_text(ImageDraw, ImageFont, text: str, box_w: int, box_h: int):
    # Returns (font, final_text)
    text = (text or "").strip()
    if not text:
        return None, ""
    min_size = 8
    # Allow font to be up to 1.5× box height for maximum visibility
    max_size = max(min_size, int(box_h * 1.5))
    pad_w = 6
    pad_h = 4
    max_w = max(1, box_w - pad_w)
    max_h = max(1, box_h - pad_h)
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

class HorsiNezEpstein(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="horsinezepstein",
        description="Worse than Epstein meme generátor (obrázek+text NEBO ping uživatele)",
    )
    @app_commands.describe(
        obrazek="Obrázek (nepoužívej, pokud nezadáš uživatele, jestli používáš, musí být spolu s textem)",
        text="Text (nepoužívej, pokud nezadáš uživatele, jestli používáš, musí být spolu s obrázkem)",
        uzivatel="Discord uživatel (použije se jeho profilovka a jméno, nesmíš zadat obrázek a text)",
    )
    async def horsinezepstein(
        self,
        interaction: discord.Interaction,
        obrazek: discord.Attachment = None,
        text: str = None,
        uzivatel: discord.User = None
    ):
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
        await interaction.response.defer()
        # Input validation: exactly one mode must be used
        user_img = None
        final_text = None
        font_debug_msg = ""
        if (obrazek and text) and not uzivatel:
            # Obrázek + text
            if not obrazek.content_type or not obrazek.content_type.startswith("image/"):
                await interaction.followup.send("Pošli prosím obrázek (PNG/JPG/WebP…).")
                return
            try:
                data = await obrazek.read()
                user_img = Image.open(io.BytesIO(data)).convert("RGBA")
            except Exception as e:
                await interaction.followup.send(f"Obrázek nejde načíst: {type(e).__name__}: {e}")
                return
            final_text = text
            if not final_text:
                await interaction.followup.send("Text nesmí být prázdný.")
                return
        elif uzivatel and not (obrazek or text):
            # Jen uživatel
            avatar_url = uzivatel.display_avatar.replace(format="png", size=512).url
            import aiohttp
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(avatar_url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            user_img = Image.open(io.BytesIO(data)).convert("RGBA")
                        else:
                            await interaction.followup.send("Nepodařilo se stáhnout profilovku uživatele.")
                            return
            except Exception as e:
                await interaction.followup.send(f"Chyba při stahování profilovky: {type(e).__name__}: {e}")
                return
            final_text = uzivatel.display_name
        else:
            await interaction.followup.send("Zadej buď obrázek a text, NEBO pouze uživatele (ping). Nelze kombinovat ani nechat prázdné.")
            return

        template_path = Path(__file__).resolve().parents[1] / "horsinezepstein.png"
        try:
            overlay = Image.open(template_path).convert("RGBA")
        except Exception as e:
            await interaction.followup.send(f"Nepodařilo se načíst šablonu: {type(e).__name__}: {e}")
            return
        bg = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
        _paste_cover(user_img, bg, (0, 0, 452, 479))
        text_box = (136, 518, 136 + 216, 518 + 37)
        box_w = 216
        box_h = 37
        # Patch: debug font loading
        def _fit_text_debug(ImageDraw, ImageFont, text: str, box_w: int, box_h: int):
            text = (text or "").strip()
            if not text:
                return None, "", []
            min_size = 8
            max_size = max(min_size, int(box_h * 1.5))
            pad_w = 6
            pad_h = 4
            max_w = max(1, box_w - pad_w)
            max_h = max(1, box_h - pad_h)
            dummy_img = __import__("PIL.Image").Image.new("RGBA", (1, 1), (0, 0, 0, 0))
            draw = ImageDraw.Draw(dummy_img)
            def text_fits(font_obj, s: str) -> bool:
                bbox = draw.textbbox((0, 0), s, font=font_obj)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                return w <= max_w and h <= max_h
            best_font = None
            font_debug = []
            for size in range(max_size, min_size - 1, -1):
                font_obj, debug_lines = _load_font(ImageFont, size, debug=True)
                font_debug.extend(debug_lines)
                if text_fits(font_obj, text):
                    best_font = font_obj
                    return best_font, text, font_debug
            font_obj, debug_lines = _load_font(ImageFont, min_size, debug=True)
            font_debug.extend(debug_lines)
            if text_fits(font_obj, text):
                return font_obj, text, font_debug
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
            return font_obj, best or ellipsis, font_debug

        font_obj, final_text2, font_debug = _fit_text_debug(ImageDraw, ImageFont, final_text, box_w, box_h)
        font_debug_msg = '\n'.join(font_debug)
        if font_obj is not None:
            overlay_with_text = overlay.copy()
            draw = ImageDraw.Draw(overlay_with_text)
            # Center of the text box
            center_x = text_box[0] + box_w // 2
            center_y = text_box[1] + box_h // 2
            # Draw white text, centered
            draw.text((center_x, center_y), final_text2, font=font_obj, fill=(255,255,255,255), anchor="mm")
        else:
            overlay_with_text = overlay
        try:
            result = bg.copy()
            result.alpha_composite(overlay_with_text)
        except Exception:
            result = bg.copy()
            result.paste(overlay_with_text, (0, 0), overlay_with_text)
        out = io.BytesIO()
        out.name = "horsinezsteinerout.png"
        result.save(out, format="PNG")
        out.seek(0)
        await interaction.followup.send(file=discord.File(out, filename="horsinezsteinerout.png"))

async def setup(bot: commands.Bot):
    await bot.add_cog(HorsiNezEpstein(bot))