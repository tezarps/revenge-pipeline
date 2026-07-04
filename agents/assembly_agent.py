"""Video assembly, Calm-Drama-style (full switch, 2026-07-04): a single
static character cutout on the left, looping drone/landscape stock footage
as background, caption cards synced to the narration via faster-whisper,
and an audio waveform strip along the bottom. Falls back to the old Ken
Burns image slideshow when no drone footage has been sourced yet, so the
pipeline keeps working while assets/drone/ is still empty."""
import json
import random
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR, ASSETS_BG_DIR, FFMPEG_BIN, FFPROBE_BIN
from agents.captions_agent import generate_captions

CHARACTER_DIR = ASSETS_BG_DIR.parent / "character"
DRONE_DIR = ASSETS_BG_DIR.parent / "drone"
CUTOUT_DIR = ASSETS_BG_DIR.parent / "character_cutout"
LOGO_PATH = ASSETS_BG_DIR.parent / "mascot_logo.jpg"
CHAR_WIDTH = 640
CHAR_HEIGHT = 820  # < 1080 on purpose: leaves headroom above her, not full-frame close-up
SEGMENT_SEC = 90  # fallback slideshow only


def _probe_duration(path):
    out = subprocess.run(
        [FFPROBE_BIN, "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


def audio_duration(path):
    return _probe_duration(path)


def _cutout_character(char_path):
    """Remove background once per character photo, cache the transparent
    PNG so every future video reusing this shot skips the model pass."""
    CUTOUT_DIR.mkdir(parents=True, exist_ok=True)
    cutout_path = CUTOUT_DIR / f"{char_path.stem}.png"
    if cutout_path.exists():
        return cutout_path
    print(f"    Cutting out character from {char_path.name} (rembg, cached after this)...")
    from rembg import remove, new_session
    from PIL import Image
    session = new_session("u2net_human_seg")
    img = Image.open(char_path).convert("RGB")
    out = remove(img, session=session)
    out.save(cutout_path)
    return cutout_path


def _pick_character(story_id):
    """One static shot for the WHOLE video (matches the reference channel:
    the same photo holds for the entire 30-45 min runtime), rotated
    deterministically across videos for variety."""
    chars = sorted((p for p in CHARACTER_DIR.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")))
    if not chars:
        return None
    chosen = chars[int(story_id) % len(chars)]
    return _cutout_character(chosen)


def _prepare_drone_concat(story_id, target_duration):
    clips = sorted(p for p in DRONE_DIR.glob("*") if p.suffix.lower() in (".mp4", ".mov", ".webm"))
    if not clips:
        return None
    rng = random.Random(story_id)
    rng.shuffle(clips)

    concat_file = OUTPUT_DIR / "video" / f"{story_id}_drone_concat.txt"
    lines, total, i = [], 0.0, 0
    while total < target_duration and i < 200:
        clip = clips[i % len(clips)]
        lines.append(f"file '{clip.resolve()}'")
        total += _probe_duration(clip)
        i += 1
    concat_file.write_text("\n".join(lines))
    return concat_file


def _fallback_bg_concat(story_id, dur):
    bgs = sorted(p for p in ASSETS_BG_DIR.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    if not bgs:
        from PIL import Image, ImageDraw
        path = OUTPUT_DIR / "video" / "_fallback_bg.jpg"
        img = Image.new("RGB", (1920, 1080))
        d = ImageDraw.Draw(img)
        for y in range(1080):
            shade = int(18 + (y / 1080) * 25)
            d.line([(0, y), (1920, y)], fill=(shade, shade, shade + 14))
        img.save(path, quality=90)
        bgs = [path]
    rng = random.Random(story_id)
    rng.shuffle(bgs)
    if len(bgs) > 10:
        bgs = bgs[:rng.randint(10, len(bgs))]

    n_segments = int(dur // SEGMENT_SEC) + 1
    concat_file = OUTPUT_DIR / "video" / f"{story_id}_img_concat.txt"
    lines = []
    for i in range(n_segments):
        bg = bgs[i % len(bgs)]
        lines.append(f"file '{bg.resolve()}'\nduration {SEGMENT_SEC}")
    lines.append(f"file '{bgs[(n_segments - 1) % len(bgs)].resolve()}'")
    concat_file.write_text("\n".join(lines))
    return concat_file


DISCLAIMER_SEC = 3
DISCLAIMER_TEXT = (
    "The stories featured on this channel are inspired by real-life experiences "
    "shared on public platforms such as Reddit and other online forums. We "
    "thoughtfully craft and reimagine these narratives, often incorporating "
    "fictional elements to enhance storytelling, build emotional resonance, "
    "and deliver a meaningful experience to our viewers. All content is created "
    "with the intent of providing entertainment and inspiration. Any "
    "similarities to actual persons, living or dead, names, or entities are "
    "purely coincidental."
)


def _render_disclaimer_card():
    """Legal/policy shield shown for a few seconds before the story starts,
    matching real monetized competitor channels (user showed a reference
    screenshot 2026-07-04: yellow card, warning emoji, red bold serif text,
    green title). Flashed briefly and never narrated on purpose: a longer or
    read-aloud disclaimer would hurt retention on the hook."""
    card_path = OUTPUT_DIR / "video" / "_disclaimer.png"
    if card_path.exists():
        return card_path
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (1920, 1080), (247, 216, 90))
    d = ImageDraw.Draw(img)
    title_font = _disclaimer_font(56)
    body_font = _disclaimer_font(34)

    def _warning_triangle(cx, cy, size):
        # Drawn shape, not a unicode emoji glyph — emoji rendering in a
        # serif font is unreliable cross-platform (same lesson learned with
        # the thumbnail's award-emoji row).
        h = size
        pts = [(cx, cy - h * 0.55), (cx - h * 0.55, cy + h * 0.4), (cx + h * 0.55, cy + h * 0.4)]
        d.polygon(pts, outline=(20, 20, 20), fill=(255, 214, 0), width=4)
        d.text((cx - 6, cy - 2), "!", font=_disclaimer_font(int(size * 0.5)), fill=(20, 20, 20))

    title = "Content Disclaimer"
    tw = d.textlength(title, font=title_font)
    tx = (1920 - tw) / 2
    d.text((tx, 60), title, font=title_font, fill=(30, 160, 130))
    _warning_triangle(tx - 55, 92, 60)
    _warning_triangle(tx + tw + 55, 92, 60)

    words, lines, cur, max_w = DISCLAIMER_TEXT.split(), [], "", 1760
    for w in words:
        test = f"{cur} {w}".strip()
        if d.textlength(test, font=body_font) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    y = 220
    for line in lines:
        lw = d.textlength(line, font=body_font)
        d.text(((1920 - lw) / 2, y), line, font=body_font, fill=(230, 60, 50))
        y += 54

    img.save(card_path)
    return card_path


def _disclaimer_font(size):
    for name in ("/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                 "Georgia Bold.ttf"):
        try:
            from PIL import ImageFont
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    from PIL import ImageFont
    return ImageFont.load_default(size)


def _render_disclaimer_clip():
    """Static disclaimer card muxed with DISCLAIMER_SEC of silence, encoded
    to match the main content clip so the two concat cleanly."""
    clip_path = OUTPUT_DIR / "video" / "_disclaimer_clip.mp4"
    if clip_path.exists():
        return clip_path
    card = _render_disclaimer_card()
    subprocess.run(
        [FFMPEG_BIN, "-y", "-loop", "1", "-i", str(card),
         "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", str(DISCLAIMER_SEC),
         "-vf", "scale=1920:1080,format=yuv420p",
         "-c:v", "libx264", "-preset", "medium", "-crf", "23",
         "-c:a", "aac", "-b:a", "192k",
         str(clip_path)],
        check=True, capture_output=True,
    )
    return clip_path


def create_video(audio_path, story_id):
    dur = audio_duration(audio_path)
    captions_path = generate_captions(audio_path, story_id)
    char_cutout = _pick_character(story_id)

    drone_concat = _prepare_drone_concat(story_id, dur)
    bg_is_video = drone_concat is not None
    if not bg_is_video:
        drone_concat = _fallback_bg_concat(story_id, dur)

    video_path = OUTPUT_DIR / "video" / f"{story_id}.mp4"

    inputs = ["-f", "concat", "-safe", "0", "-i", str(drone_concat)]
    idx = 0
    bg_in = idx; idx += 1
    char_in = logo_in = None
    if char_cutout:
        inputs += ["-loop", "1", "-i", str(char_cutout)]
        char_in = idx; idx += 1
    if LOGO_PATH.exists():
        inputs += ["-loop", "1", "-i", str(LOGO_PATH)]
        logo_in = idx; idx += 1
    inputs += ["-i", str(audio_path)]
    audio_in = idx

    filters = []
    if bg_is_video:
        filters.append(f"[{bg_in}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=25[bg]")
    else:
        filters.append(
            f"[{bg_in}:v]scale=2112:1188,"
            f"zoompan=z='min(zoom+0.00004,1.10)':d={SEGMENT_SEC * 25}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=25,"
            f"format=yuv420p,setsar=1[bg]"
        )

    last = "bg"
    if char_in is not None:
        # Smaller and bottom-anchored (not a full-height 0-1080 close-up
        # covering the whole frame) — matches the reference: background
        # visible above her head, she doesn't dominate the entire vertical
        # space. See user feedback 2026-07-04.
        filters.append(f"[{char_in}:v]scale={CHAR_WIDTH}:{CHAR_HEIGHT}:force_original_aspect_ratio=increase,crop={CHAR_WIDTH}:{CHAR_HEIGHT}[char]")
        filters.append(f"[{last}][char]overlay=x=0:y=H-h[bgchar]")
        last = "bgchar"
    if logo_in is not None:
        filters.append(f"[{logo_in}:v]scale=140:140[logo]")
        filters.append(f"[{last}][logo]overlay=x=40:y=40[bglogo]")
        last = "bglogo"

    filters.append(f"[{last}]subtitles={captions_path}[withtext]")
    # LIVE per-frame waveform (user confirmed: it must react to the actual
    # narration in real time, not a single static whole-track image — see
    # 2026-07-04 correction). colorkey punches out showwaves' near-black
    # background so only the white line composites; this is the color-safe
    # replacement for the earlier blend=all_mode=screen version, which
    # corrupted the entire frame magenta (root-caused and fixed separately).
    filters.append(f"[{audio_in}:a]showwaves=s=1920x100:mode=cline:colors=white[waveraw]")
    filters.append("[waveraw]format=rgba,colorkey=0x000000:0.15:0.1[wave]")
    filters.append("[withtext][wave]overlay=x=0:y=H-h[vout]")

    content_path = OUTPUT_DIR / "video" / f"{story_id}_content.mp4"
    cmd = [FFMPEG_BIN, "-y", *inputs,
           "-filter_complex", ";".join(filters),
           "-map", "[vout]", "-map", f"{audio_in}:a",
           "-t", f"{dur + 1.0:.2f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "23",
           "-c:a", "aac", "-b:a", "192k",
           str(content_path)]
    subprocess.run(cmd, check=True, capture_output=True)

    disclaimer_clip = _render_disclaimer_clip()
    concat_list = OUTPUT_DIR / "video" / f"{story_id}_final_concat.txt"
    concat_list.write_text(f"file '{disclaimer_clip.resolve()}'\nfile '{content_path.resolve()}'\n")
    subprocess.run(
        [FFMPEG_BIN, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c:v", "libx264", "-preset", "medium", "-crf", "23",
         "-c:a", "aac", "-b:a", "192k",
         str(video_path)],
        check=True, capture_output=True,
    )
    content_path.unlink()

    for f in (OUTPUT_DIR / "video").glob(f"{story_id}_*concat.txt"):
        f.unlink()
    return video_path, dur + DISCLAIMER_SEC
