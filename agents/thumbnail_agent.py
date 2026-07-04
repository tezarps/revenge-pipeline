"""Thumbnail — fake-Reddit-post card, copied from the niche's top performer
(Reddit Family Tales, 582K/404K views: white rounded card, orange avatar,
channel name + blue check, award badges, full title in huge bold black text,
gray 99+ likes/comments footer). Pure Pillow, $0, no image APIs.
Verified against the real thumbnails in revenge-story-lab/thumbs/."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR, CHANNEL_NAME, ASSETS_BG_DIR

CHARACTER_DIR = ASSETS_BG_DIR.parent / "character"

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
    """Snoo-style mascot: white head on orange circle, x-eyes, frown —
    matches the niche house style (see revenge-story-lab/thumbs/)."""
    ORANGE = (255, 69, 0)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ORANGE)
    # ears
    for ex in (cx - r * 0.52, cx + r * 0.52):
        d.ellipse([ex - r * 0.18, cy - r * 0.62, ex + r * 0.18, cy - r * 0.28], fill="white")
    # head (wide white ellipse)
    d.ellipse([cx - r * 0.62, cy - r * 0.5, cx + r * 0.62, cy + r * 0.55], fill="white")
    # antenna
    d.line([cx, cy - r * 0.48, cx + r * 0.28, cy - r * 0.82], fill="white", width=int(r * 0.11))
    d.ellipse([cx + r * 0.28 - r * 0.12, cy - r * 0.95, cx + r * 0.28 + r * 0.12, cy - r * 0.71], fill="white")
    # x eyes (orange on white)
    for ex in (cx - r * 0.28, cx + r * 0.28):
        s = r * 0.11
        ey = cy - r * 0.05
        d.line([ex - s, ey - s, ex + s, ey + s], fill=ORANGE, width=int(r * 0.08))
        d.line([ex - s, ey + s, ex + s, ey - s], fill=ORANGE, width=int(r * 0.08))
    # frown
    d.arc([cx - r * 0.3, cy + r * 0.12, cx + r * 0.3, cy + r * 0.48], start=200, end=340, fill=ORANGE, width=int(r * 0.08))


def _verified(d, x, y, r=22):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(29, 155, 240))
    d.line([x - r * 0.45, y, x - r * 0.1, y + r * 0.35], fill="white", width=7)
    d.line([x - r * 0.1, y + r * 0.35, x + r * 0.5, y - r * 0.35], fill="white", width=7)


EMOJI_ROW = "🛡️🏆💀😂😮👏💀⭐⭐"


def _emoji_row(img, x, y, size=44):
    """Real color-emoji award row (like the original thumbnails). Bitmap emoji
    fonts only render at their native strike size, so render there and resize.
    Falls back to drawn medallions if no emoji font is available."""
    for font_path, strike in (
        ("/System/Library/Fonts/Apple Color Emoji.ttc", 160),
        ("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109),
    ):
        try:
            f = ImageFont.truetype(font_path, strike)
            tmp = Image.new("RGBA", (strike * (len(EMOJI_ROW) + 2), int(strike * 1.4)), (0, 0, 0, 0))
            ImageDraw.Draw(tmp).text((0, 0), EMOJI_ROW, font=f, embedded_color=True)
            box = tmp.getbbox()
            if not box:
                continue
            tmp = tmp.crop(box)
            scale = size / tmp.height
            tmp = tmp.resize((int(tmp.width * scale), size), Image.LANCZOS)
            img.paste(tmp, (x, y), tmp)
            return
        except OSError:
            continue
    # fallback: drawn medallions
    d = ImageDraw.Draw(img)
    colors = [(46, 204, 113), (241, 196, 15), (149, 165, 166), (243, 156, 18),
              (236, 240, 241), (241, 196, 15), (149, 165, 166), (243, 156, 18), (241, 196, 15)]
    r = size // 2
    for i, c in enumerate(colors):
        cx = x + i * (r * 2 + 14) + r
        d.ellipse([cx - r, y, cx + r, y + 2 * r], fill=c, outline=(120, 120, 120), width=2)
        d.ellipse([cx - 7, y + r - 7, cx + 7, y + r + 7], fill=(255, 255, 255))


def generate_thumbnail(title_text, story_id):
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    # thin rounded card outline (matches the RFT look)
    d.rounded_rectangle([16, 12, W - 16, H - 12], radius=48, outline=(20, 20, 20), width=6, fill="white")

    # header: avatar + channel name + verified + badges
    logo_path = ASSETS_BG_DIR.parent / "mascot_logo.jpg"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGB").resize((190, 190))
        mask = Image.new("L", (190, 190), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, 190, 190], fill=255)
        img.paste(logo, (50, 50), mask)
    else:
        _avatar(d, 145, 145, 95)
    name_font = _font(52)
    d.text((265, 88), CHANNEL_NAME, font=name_font, fill=(10, 10, 10))
    _verified(d, 265 + d.textlength(CHANNEL_NAME, font=name_font) + 42, 116)
    _emoji_row(img, 268, 172, size=48)

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


# style -> (text color, bg box color or None, base font size in px)
LINE_STYLE = {
    "setup":   ((255, 214, 0), None, 54),
    "twist":   ((235, 25, 130), None, 66),
    "context": ((255, 255, 255), None, 44),
    "climax1": ((255, 255, 255), (196, 18, 18), 48),
    "climax2": ((255, 214, 0), (196, 18, 18), 48),
}
DEFAULT_ORDER = ["setup", "twist", "context", "climax1", "climax2"]


def generate_thumbnail_b(thumb_lines, story_id):
    """Style B, copied deliberately from the niche's top performer
    (Calm Drama Stories): full-width character photo on the right, and on
    the left a stacked, multi-color, multi-size caption block (yellow setup,
    magenta twist, white context, red-highlight climax) exactly matching
    their proven eye-catching layout. Character shots come from
    assets/character/ (see assets/CHARACTER_PROMPTS.md).

    `thumb_lines`: list of {"style": ..., "text": ...} dicts from
    story_agent.generate_metadata(), in the 5-segment order defined above.
    Not aesthetic-optimized on purpose: this format is copied because it is
    what the reference channel's data shows works, not because it looks good.
    """
    chars = sorted(CHARACTER_DIR.glob("char_*.jpg")) if CHARACTER_DIR.exists() else []
    if not chars or not thumb_lines:
        return None  # caller falls back to style A

    img = Image.new("RGB", (W, H), (8, 8, 8))
    shot = Image.open(chars[int(story_id) % len(chars)]).convert("RGB")
    target_w = int(W * 0.42)
    scale = H / shot.height
    shot = shot.resize((int(shot.width * scale), H), Image.LANCZOS)
    left_crop = max(0, (shot.width - target_w) // 2)
    shot = shot.crop((left_crop, 0, left_crop + target_w, H))
    img.paste(shot, (W - target_w, 0))
    d = ImageDraw.Draw(img)

    panel_w = W - target_w - 60
    lines_by_style = {ln.get("style"): ln.get("text", "") for ln in thumb_lines}

    # Pass 1: wrap every segment at its BASE size to get line counts (word
    # wrap only depends on width, so this is a safe upper bound on line
    # count at any scale <= 1).
    segments = []
    for style in DEFAULT_ORDER:
        text = lines_by_style.get(style, "").strip().upper()
        if not text:
            continue
        color, box, base_size = LINE_STYLE[style]
        base_font = _font(base_size)
        wrapped = _wrap(d, text, base_font, panel_w - (24 if box else 0))
        segments.append({"wrapped": wrapped, "color": color, "box": box, "base_size": base_size})

    if not segments:
        return None

    # Pass 2: compute the scale factor that makes the WHOLE stack fit the
    # frame height exactly, instead of an iterative loop that can stop short
    # (bug: content clipped off-screen top/bottom in the first version).
    top_margin, bottom_margin, gap = 28, 28, 16
    raw_total = 0.0
    for seg in segments:
        line_h = seg["base_size"] * 1.15
        block_h = len(seg["wrapped"]) * line_h + (16 if seg["box"] else 0)
        raw_total += block_h + gap
    raw_total += top_margin + bottom_margin - gap

    scale = min(1.0, (H - top_margin - bottom_margin) / max(raw_total, 1))
    scale = max(scale, 0.35)  # legibility floor; LLM prompt caps line counts so this rarely triggers

    y = top_margin
    x0 = 40
    for seg in segments:
        size = max(18, int(seg["base_size"] * scale))
        font = _font(size)
        line_h = size * 1.15
        wrapped = seg["wrapped"]
        box, color = seg["box"], seg["color"]
        if box:
            block_w = max(d.textlength(l, font=font) for l in wrapped) + 36
            block_h = len(wrapped) * line_h + 14
            d.rectangle([x0 - 12, y - 6, x0 - 12 + block_w, y - 6 + block_h], fill=box)
        for line in wrapped:
            d.text((x0 + 3, y + 3), line, font=font, fill=(0, 0, 0))
            d.text((x0, y), line, font=font, fill=color)
            y += line_h
        y += (16 if box else 0) + gap

    path = OUTPUT_DIR / "thumbs" / f"{story_id}_b.jpg"
    img.save(path, quality=92)
    return path


def generate_thumbnail_ab(title_text, thumb_lines, story_id):
    """A/B rotation: even story ids try style B (character + colored stack),
    odd use style A (Reddit card). Falls back to A when no character shots
    exist yet or thumb_lines is missing (older cached metadata)."""
    if int(story_id) % 2 == 0:
        b = generate_thumbnail_b(thumb_lines, story_id)
        if b:
            return b
    return generate_thumbnail(title_text, story_id)
