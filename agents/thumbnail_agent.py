"""Thumbnail — fake-Reddit-post card, copied from the niche's top performer
(Reddit Family Tales, 582K/404K views: white rounded card, orange avatar,
channel name + blue check, award badges, full title in huge bold black text,
gray 99+ likes/comments footer). Pure Pillow, $0, no image APIs.
Verified against the real thumbnails in revenge-story-lab/thumbs/."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR, CHANNEL_NAME, ASSETS_BG_DIR

CHARACTER_DIR = ASSETS_BG_DIR.parent / "character"
FONTS_DIR = ASSETS_BG_DIR.parent / "fonts"

W, H = 1280, 720


def _font(size, bold=True):
    candidates = [
        FONTS_DIR / "Anton-Regular.ttf",  # bundled: identical on Mac + Ubuntu CI
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "Arial Bold.ttf" if bold else "Arial.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(str(name), size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def _font_condensed(size):
    """Style B specifically wants the bold-condensed impact look of the
    reference channel's thumbnails; Anton renders ~25% narrower than Arial
    Bold at the same pixel size, so callers sizing against it should expect
    tighter wraps (more words per line) than the Arial-based style A."""
    return _font(size)


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
# Sizes are bigger than a first glance at the reference suggests, because
# Anton is a condensed face (~25% narrower per character than Arial Bold at
# the same pixel size) so it needs more px to occupy the same visual weight.
LINE_STYLE = {
    "setup":   ((255, 214, 0), None, 62),
    "twist":   ((235, 25, 130), None, 76),
    "context": ((255, 255, 255), None, 50),
    "climax1": ((255, 255, 255), (196, 18, 18), 54),
    "climax2": ((255, 214, 0), (196, 18, 18), 54),
}
DEFAULT_ORDER = ["setup", "twist", "context", "climax1", "climax2"]


def generate_thumbnail_b(thumb_lines, story_id):
    """Style B, copied deliberately from the niche's top performers: a
    FULL-BLEED character photo covering the entire frame (not a cropped
    strip beside a solid black panel), with the caption stack (yellow
    setup, magenta twist, white context, red-highlight climax) and a
    "TRUE STORY" badge overlaid directly on top, darkened just enough on
    the left for legibility. Matches the reference layout exactly per
    user correction 2026-07-05 — the earlier photo-on-right/black-panel-
    on-left split was wrong. Character shots come from assets/character/
    (see assets/CHARACTER_PROMPTS.md). Photo is used as-is, no brightness/
    contrast/color enhancement (that read as an orange, overexposed
    "on fire" look — user feedback 2026-07-05, don't re-add it).

    `thumb_lines`: list of {"style": ..., "text": ...} dicts from
    story_agent.generate_metadata(), in the 5-segment order defined above.
    Not aesthetic-optimized on purpose: this format is copied because it is
    what the reference channel's data shows works, not because it looks good.
    """
    chars = sorted(p for p in CHARACTER_DIR.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")) if CHARACTER_DIR.exists() else []
    if not chars or not thumb_lines:
        return None  # caller falls back to style A

    shot = Image.open(chars[int(story_id) % len(chars)]).convert("RGB")
    scale = max(W / shot.width, H / shot.height)
    shot = shot.resize((int(shot.width * scale) + 1, int(shot.height * scale) + 1), Image.LANCZOS)
    left_crop = max(0, (shot.width - W) // 2)
    # Bias toward the top, not centered: these are portrait upper-body
    # shots, and a pure center crop chops the face off at the mouth
    # (found rendering the first real thumbnail with this layout).
    top_crop = max(0, int((shot.height - H) * 0.12))
    img = shot.crop((left_crop, top_crop, left_crop + W, top_crop + H))

    # Dark scrim over the left ~60% only, so the caption stack stays legible
    # while the photo itself (and the subject's face on the right) stays
    # untouched and visible, matching the reference thumbnails.
    scrim = Image.new("L", (W, H), 0)
    scrim_d = ImageDraw.Draw(scrim)
    scrim_w = int(W * 0.62)
    for x in range(scrim_w):
        alpha = 190 if x < scrim_w - 120 else int(190 * (scrim_w - x) / 120)
        scrim_d.line([(x, 0), (x, H)], fill=alpha)
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(dark, img, scrim)
    d = ImageDraw.Draw(img)

    # "TRUE STORY" badge, matching the niche's proven layout (user decision
    # 2026-07-05, kept despite content being AI-narrated/reimagined - already
    # disclosed via the in-video disclaimer card).
    badge_font = _font(38)
    badge_text = "TRUE STORY"
    badge_pad_x, badge_pad_y = 26, 12
    badge_w = d.textlength(badge_text, font=badge_font) + badge_pad_x * 2
    badge_h = 38 + badge_pad_y * 2
    badge_x0, badge_y0 = 36, 30
    d.rounded_rectangle(
        [badge_x0, badge_y0, badge_x0 + badge_w, badge_y0 + badge_h],
        radius=badge_h / 2, fill=(214, 24, 24),
    )
    d.text(
        (badge_x0 + badge_pad_x, badge_y0 + badge_pad_y - 2),
        badge_text, font=badge_font, fill=(255, 255, 255),
    )
    text_top = badge_y0 + badge_h + 22

    panel_w = int(W * 0.62) - 70
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
    # Gap is small and constant (the reference stacks blocks almost flush,
    # not our earlier generously-spaced version).
    top_margin, bottom_margin, gap = text_top, 14, 14
    raw_total = 0.0
    for seg in segments:
        line_h = seg["base_size"] * 1.18
        block_h = len(seg["wrapped"]) * line_h + (10 if seg["box"] else 0)
        raw_total += block_h + gap
    raw_total += top_margin + bottom_margin - gap

    scale = min(1.0, (H - top_margin - bottom_margin) / max(raw_total, 1))
    scale = max(scale, 0.35)  # legibility floor; LLM prompt caps line counts so this rarely triggers

    y = top_margin
    x0 = 36
    for seg in segments:
        size = max(18, int(seg["base_size"] * scale))
        font = _font(size)
        line_h = size * 1.18
        wrapped = seg["wrapped"]
        box, color = seg["box"], seg["color"]
        if box:
            block_w = max(d.textlength(l, font=font) for l in wrapped) + 30
            block_h = len(wrapped) * line_h + 10
            # Rounded, not sharp corners — user feedback 2026-07-05 comparing
            # against reference thumbnails: hard rectangle edges read as
            # "kasar" (harsh); a soft rounded pill matches the niche look.
            d.rounded_rectangle([x0 - 10, y - 4, x0 - 10 + block_w, y - 4 + block_h], radius=14, fill=box)
        for line in wrapped:
            # true stroke outline (not an offset duplicate) — matches the
            # reference's flat, clean look instead of a drop-shadow smear.
            d.text((x0, y), line, font=font, fill=color, stroke_width=3, stroke_fill=(0, 0, 0))
            y += line_h
        y += (10 if box else 0) + gap

    path = OUTPUT_DIR / "thumbs" / f"{story_id}_b.jpg"
    img.save(path, quality=92)
    return path


def generate_thumbnail_ab(title_text, thumb_lines, story_id):
    """Full switch to Calm-Drama-style (2026-07-04, user decision): every
    video uses style B (character + colored stack), no more odd/even A/B
    rotation with the Reddit-card style. Style A is kept ONLY as an
    emergency fallback for when assets/character/ is empty or thumb_lines
    is missing (e.g. older cached metadata) — not a deliberate design
    choice, just so the pipeline never blocks on missing assets."""
    b = generate_thumbnail_b(thumb_lines, story_id)
    if b:
        return b
    return generate_thumbnail(title_text, story_id)
