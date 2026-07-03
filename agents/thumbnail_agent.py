"""Thumbnail — fake-Reddit-post card, copied from the niche's top performer
(Reddit Family Tales, 582K/404K views: white rounded card, orange avatar,
channel name + blue check, award badges, full title in huge bold black text,
gray 99+ likes/comments footer). Pure Pillow, $0, no image APIs.
Verified against the real thumbnails in revenge-story-lab/thumbs/."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR, CHANNEL_NAME

W, H = 1280, 720


def _font(size, bold=True):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "Arial Bold.ttf" if bold else "Arial.ttf",
    ]
    for name in candidates:
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


def _avatar(d, cx, cy, r):
    """Orange circle mascot with x-eyes and a frown — evokes the niche's
    house style without copying the Reddit snoo outright."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 69, 0))
    # antenna
    d.line([cx, cy - r + 18, cx + r * 0.45, cy - r - 14], fill="white", width=10)
    d.ellipse([cx + r * 0.45 - 12, cy - r - 26, cx + r * 0.45 + 12, cy - r - 2], fill="white")
    # x eyes
    for ex in (cx - r * 0.38, cx + r * 0.38):
        s = r * 0.16
        ey = cy - r * 0.05
        d.line([ex - s, ey - s, ex + s, ey + s], fill="white", width=9)
        d.line([ex - s, ey + s, ex + s, ey - s], fill="white", width=9)
    # frown
    d.arc([cx - r * 0.4, cy + r * 0.25, cx + r * 0.4, cy + r * 0.85], start=200, end=340, fill="white", width=9)


def _verified(d, x, y, r=22):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(29, 155, 240))
    d.line([x - r * 0.45, y, x - r * 0.1, y + r * 0.35], fill="white", width=7)
    d.line([x - r * 0.1, y + r * 0.35, x + r * 0.5, y - r * 0.35], fill="white", width=7)


def _badges(d, x, y):
    """Award-badge row — simple gold/silver medallions instead of emoji
    (color-emoji fonts are unreliable across mac/linux runners)."""
    colors = [(46, 204, 113), (241, 196, 15), (149, 165, 166), (243, 156, 18),
              (236, 240, 241), (241, 196, 15), (149, 165, 166), (243, 156, 18), (241, 196, 15)]
    r = 20
    for i, c in enumerate(colors):
        cx = x + i * (r * 2 + 14) + r
        d.ellipse([cx - r, y - r, cx + r, y + r], fill=c, outline=(120, 120, 120), width=2)
        # star-ish dot core
        d.ellipse([cx - 7, y - 7, cx + 7, y + 7], fill=(255, 255, 255))


def generate_thumbnail(title_text, story_id):
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    # thin rounded card outline (matches the RFT look)
    d.rounded_rectangle([16, 12, W - 16, H - 12], radius=48, outline=(20, 20, 20), width=6, fill="white")

    # header: avatar + channel name + verified + badges
    _avatar(d, 145, 145, 95)
    name_font = _font(52)
    d.text((265, 88), CHANNEL_NAME, font=name_font, fill=(10, 10, 10))
    _verified(d, 265 + d.textlength(CHANNEL_NAME, font=name_font) + 42, 116)
    _badges(d, 268, 196)

    # title block — the whole card is the title, like the original
    size = 88
    while size > 40:
        font = _font(size)
        lines = _wrap(d, title_text, font, W - 190)
        line_h = size * 1.16
        if 262 + len(lines) * line_h <= H - 110:
            break
        size -= 6

    y = 268
    for line in lines:
        d.text((84, y), line, font=font, fill=(8, 8, 8))
        y += line_h

    # footer: gray heart 99+ / comment 99+
    gray = (170, 170, 170)
    fy = H - 92
    d.ellipse([84, fy, 112, fy + 28], outline=gray, width=6)      # heart approximation
    d.ellipse([104, fy, 132, fy + 28], outline=gray, width=6)
    d.polygon([(88, fy + 22), (108, fy + 44), (128, fy + 22)], fill="white", outline=None)
    d.line([(90, fy + 24), (108, fy + 42)], fill=gray, width=6)
    d.line([(108, fy + 42), (126, fy + 24)], fill=gray, width=6)
    foot_font = _font(40)
    d.text((150, fy - 6), "99+", font=foot_font, fill=gray)
    d.rounded_rectangle([260, fy - 2, 316, fy + 40], radius=10, outline=gray, width=6)
    d.text((330, fy - 6), "99+", font=foot_font, fill=gray)

    path = OUTPUT_DIR / "thumbs" / f"{story_id}.jpg"
    img.save(path, quality=92)
    return path
