"""Thumbnail, fake-Reddit-post card, copied from the niche's top performer
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
PANEL_MASK_PATH = ASSETS_BG_DIR.parent / "panel_gradient_mask.png"

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
    """Snoo-style mascot: white head on orange circle, x-eyes, frown,
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

    # title block, the whole card is the title, like the original
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
# Rebuilt 2026-07-06 to match a manually-built reference the user sent:
# white/yellow alternating lines (was white/cyan), Baloo2 rounded-bold
# font, top-left yellow/blue "TRUE STORY" badge (was a bottom green bar).
YELLOW = (255, 245, 0)
WHITE = (255, 255, 255)
LINE_STYLE = {
    "setup":   (WHITE, None, 46),
    "twist":   (YELLOW, None, 46),
    "context": (WHITE, None, 46),
    "climax1": (YELLOW, None, 46),
    "climax2": (WHITE, None, 46),
}
DEFAULT_ORDER = ["setup", "twist", "context", "climax1", "climax2"]


THUMB_HTML_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  @font-face {{ font-family: 'Baloo2'; src: url('{font_uri}') format('truetype'); }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: 1280px; height: 720px; overflow: hidden; background: #1c1e26; font-family: 'Baloo2', Arial, sans-serif; }}
  .frame {{ position: relative; width: 1280px; height: 720px; background: #1c1e26; }}
  /* Full-bleed backdrop: the SAME photo, heavily blurred and zoomed so it
     reads as a soft out-of-focus color wash, not a second recognizable
     face competing with the text (an earlier sharp-backdrop attempt looked
     like a distracting ghosted duplicate portrait). The mask below darkens
     this instead of sitting over a flat solid color, so there is no
     separate solid-black panel anywhere (feedback 2026-07-06). */
  .backdrop {{ position: absolute; inset: 0; overflow: hidden; z-index: 0; }}
  .backdrop img {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 15%;
    filter: blur(45px) brightness(0.8); transform: scale(1.15); }}
  .photo-box {{ position: absolute; top: 0; right: 0; width: 560px; height: 720px; overflow: hidden; z-index: 1; }}
  .photo-box img {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 12%; }}
  /* User-supplied alpha mask (assets/panel_gradient_mask.png): opaque
     black at the left edge easing to fully transparent by ~75% width,
     sized exactly 1280x720. Opacity capped below 100% so even the
     darkest zone still shows photo through it, not a flat solid block. */
  .panel-fade {{ position: absolute; inset: 0; z-index: 2; opacity: 0.82;
    background-image: url('{mask_uri}'); background-size: 1280px 720px; }}
  /* Badge moved to top-left, yellow/blue, per a manually-built reference
     the user sent 2026-07-06 to replace the earlier bottom green bar. */
  .badge {{ position: absolute; left: 42px; top: 46px; z-index: 4;
    background: #fff500; border: 6px solid white; border-radius: 22px;
    padding: 14px 34px; display: inline-block; }}
  .badge span {{ font-family: 'Baloo2', Arial, sans-serif; font-variation-settings: 'wght' 800;
    color: #376ec3; font-size: 62px; letter-spacing: 1px;
    -webkit-text-stroke: 2px #1f4162; paint-order: stroke fill; }}
  .text-stack {{ position: absolute; top: 200px; left: 42px; width: 660px; bottom: 30px;
    z-index: 3; display: flex; flex-direction: column; justify-content: flex-start; gap: 10px;
    transform-origin: top left; }}
  .line {{ font-size: 50px; line-height: 1.16; letter-spacing: 0.5px;
    font-variation-settings: 'wght' 800;
    -webkit-text-stroke: 2.5px #1f4162; paint-order: stroke fill; text-transform: uppercase; }}
  .white {{ color: #ffffff; }}
  .yellow {{ color: #fff500; }}
</style></head>
<body>
  <div class="frame">
    <div class="backdrop"><img src="{photo_uri}"></div>
    <div class="photo-box"><img src="{photo_uri}"></div>
    <div class="panel-fade"></div>
    <div class="badge"><span>TRUE STORY</span></div>
    <div class="text-stack" id="stack">{lines_html}</div>
  </div>
<script>
  function fitStack() {{
    const stack = document.getElementById('stack');
    stack.style.transform = 'scale(1)';
    const available = stack.clientHeight;
    const contentHeight = stack.scrollHeight;
    if (contentHeight > available) {{
      const scale = Math.max(0.5, available / contentHeight);
      stack.style.transform = `scale(${{scale}})`;
    }}
  }}
  window.onload = fitStack;
</script>
</body></html>"""


def generate_thumbnail_b(thumb_lines, story_id):
    """Style B: exact copy of Calm Dad Stories / Calm Drama Stories layout,
    rendered as real HTML/CSS via a headless Chromium (Playwright) instead
    of hand-computed Pillow pixel math. Verified visually against the
    reference thumbnail 2026-07-05 (photo right ~40%, dark bg left ~60%,
    white/cyan Anton stack, full-width green TRUE STORY pill) before being
    wired in here - HTML/CSS gives exact flexbox/gradient/font-stroke
    control that blind Pillow coordinate math kept getting wrong.
    """
    import base64
    from playwright.sync_api import sync_playwright

    chars = sorted(p for p in CHARACTER_DIR.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")) if CHARACTER_DIR.exists() else []
    if not chars or not thumb_lines:
        return None

    photo_path = chars[int(story_id) % len(chars)]
    font_path = FONTS_DIR / "Baloo2-Variable.ttf"

    def _data_uri(path, mime):
        return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"

    photo_uri = _data_uri(photo_path, "image/jpeg")
    font_uri = _data_uri(font_path, "font/ttf") if font_path.exists() else ""
    mask_uri = _data_uri(PANEL_MASK_PATH, "image/png") if PANEL_MASK_PATH.exists() else ""

    lines_by_style = {ln.get("style"): ln.get("text", "") for ln in thumb_lines}
    lines_html = ""
    for style in DEFAULT_ORDER:
        text = lines_by_style.get(style, "").strip().upper()
        if not text:
            continue
        color_rgb, _box, _size = LINE_STYLE[style]
        css_class = "yellow" if color_rgb == YELLOW else "white"
        lines_html += f'<div class="line {css_class}">{text}</div>'

    if not lines_html:
        return None

    html = THUMB_HTML_TEMPLATE.format(photo_uri=photo_uri, font_uri=font_uri, mask_uri=mask_uri, lines_html=lines_html)

    path = OUTPUT_DIR / "thumbs" / f"{story_id}_b.jpg"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        page.set_content(html)
        page.wait_for_timeout(150)  # let the fitStack() onload scale settle
        png_path = path.with_suffix(".png")
        page.screenshot(path=str(png_path))
        browser.close()

    Image.open(png_path).convert("RGB").save(path, quality=92)
    png_path.unlink(missing_ok=True)
    return path


def generate_thumbnail_ab(title_text, thumb_lines, story_id):
    """Full switch to Calm-Drama-style (2026-07-04, user decision): every
    video uses style B (character + colored stack), no more odd/even A/B
    rotation with the Reddit-card style. Style A is kept ONLY as an
    emergency fallback for when assets/character/ is empty or thumb_lines
    is missing (e.g. older cached metadata), not a deliberate design
    choice, just so the pipeline never blocks on missing assets."""
    b = generate_thumbnail_b(thumb_lines, story_id)
    if b:
        return b
    return generate_thumbnail(title_text, story_id)
