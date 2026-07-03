"""Thumbnail — niche formula: high-contrast dark card, huge emotional text.
(Cake Lovers / Reddit Family Tales pattern: text IS the thumbnail.)
Pure Pillow, no image-gen API cost. Drop a custom 1280x720 base image at
assets/bg/thumb_base.jpg to replace the gradient."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR, ASSETS_BG_DIR

W, H = 1280, 720


def _font(size):
    for name in ("Impact.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/System/Library/Fonts/Supplemental/Impact.ttf",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def generate_thumbnail(thumb_text, story_id):
    base = ASSETS_BG_DIR / "thumb_base.jpg"
    if base.exists():
        img = Image.open(base).convert("RGB").resize((W, H))
        # darken so the text carries
        overlay = Image.new("RGB", (W, H), (0, 0, 0))
        img = Image.blend(img, overlay, 0.45)
    else:
        img = Image.new("RGB", (W, H))
        d0 = ImageDraw.Draw(img)
        for y in range(H):
            shade = int(15 + (y / H) * 30)
            d0.line([(0, y), (W, y)], fill=(shade + 10, shade, shade))

    d = ImageDraw.Draw(img)
    size = 110
    while size > 48:
        font = _font(size)
        lines = _wrap(d, thumb_text.upper(), font, W - 120)
        line_h = size * 1.18
        if len(lines) * line_h <= H - 140:
            break
        size -= 8

    total_h = len(lines) * line_h
    y = (H - total_h) / 2
    for i, line in enumerate(lines):
        x = (W - d.textlength(line, font=font)) / 2
        # last line in red — the niche's emotional-punch convention
        fill = (255, 70, 60) if i == len(lines) - 1 else (255, 255, 255)
        d.text((x + 4, y + 4), line, font=font, fill=(0, 0, 0))  # drop shadow
        d.text((x, y), line, font=font, fill=fill)
        y += line_h

    path = OUTPUT_DIR / "thumbs" / f"{story_id}.jpg"
    img.save(path, quality=92)
    return path
