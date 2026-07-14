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
CHARACTER_V2_DIR = ASSETS_BG_DIR.parent / "character_v2"
DRONE_DIR = ASSETS_BG_DIR.parent / "drone"
# Driving-POV loop background for the RealDadRevenge experiment (2026-07-14,
# user reference: a windshield/dashboard driving clip, looped for the whole
# video instead of drone/landscape footage). Free stock libraries only offer
# short clips (seconds, not a single continuous 9min+ file), so this reuses
# the same shuffle-and-repeat-to-target-duration technique as
# _prepare_drone_concat below, just pointed at a different clip pool.
DRIVING_DIR = ASSETS_BG_DIR.parent / "driving"
CUTOUT_DIR = ASSETS_BG_DIR.parent / "character_cutout"
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


def _cutout_character(char_path, tight_crop=False):
    """Remove background once per character photo, cache the transparent
    PNG so every future video reusing this shot skips the model pass.

    tight_crop=True (v2 pool only, see _pick_character below): the
    user-supplied v2 photos are full-body waist-up shots on a plain white
    background with a lot of empty headroom above her (portrait
    1536x2752), so after rembg strips the white, the transparent PNG still
    carries that empty margin. Cropping to the alpha channel's bounding box
    removes it, so a top-anchored overlay actually starts at her head
    instead of a blank gap (verified 2026-07-14 against the new asset
    batch). v1's photos are already tightly framed, so this stays off for
    them to avoid changing the locked look."""
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
    if tight_crop:
        bbox = out.getbbox()
        if bbox:
            out = out.crop(bbox)
    out.save(cutout_path)
    return cutout_path


def _pick_character(story_id):
    """One static shot for the WHOLE video (matches the reference channel:
    the same photo holds for the entire 30-45 min runtime). Uses the shared
    character_number_for_story() mapping (config.py) so the video cutout
    and the thumbnail template always show the same person (fixed
    2026-07-06 after story #3/#4 published with mismatched characters).

    When config.THUMBNAIL_EXPERIMENT is on (2026-07-14 RealDadRevenge-cadence
    experiment), pulls from the separate character_v2/ pool instead, using
    character_v2_number_for_story() so this stays in sync with
    thumbnail_agent.generate_thumbnail_c's character choice for the same
    story_id. v2 photos (2nd batch, 2026-07-14) are user-supplied, ALREADY
    transparent PNGs pre-positioned on a 1280x720 canvas (right-anchored,
    small top margin) - no rembg cutout needed, used as-is. (The first v2
    batch needed rembg; that path stayed for v1 back-compat but is dead for
    v2 now.)"""
    from config import character_number_for_story, character_v2_number_for_story, THUMBNAIL_EXPERIMENT
    if THUMBNAIL_EXPERIMENT:
        num = character_v2_number_for_story(story_id)
        chosen = CHARACTER_V2_DIR / f"person_v2_{num:02d}.png"
        if chosen.exists():
            return chosen
    num = character_number_for_story(story_id)
    chosen = CHARACTER_DIR / f"person_{num:02d}.jpg"
    if not chosen.exists():
        chars = sorted((p for p in CHARACTER_DIR.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")))
        if not chars:
            return None
        chosen = chars[int(story_id) % len(chars)]
    return _cutout_character(chosen)


def _prepare_drone_concat(story_id, target_duration, bg_dir=None):
    bg_dir = bg_dir or DRONE_DIR
    clips = sorted(p for p in bg_dir.glob("*") if p.suffix.lower() in (".mp4", ".mov", ".webm"))
    if not clips:
        return None
    rng = random.Random(story_id)
    rng.shuffle(clips)

    concat_file = OUTPUT_DIR / "video" / f"{story_id}_{bg_dir.name}_concat.txt"
    # Cap must scale with target_duration, not be a flat number: with only 6
    # clips averaging ~18s, a flat 200-clip cap tops out around 60 minutes of
    # background and silently runs out mid-video for the 2hr target (found
    # inspecting the first full-length render, which ran out of background
    # around 60% through - the concat demuxer just ends early, so the tail
    # of the narration would play over nothing). Cap is now generous relative
    # to how much runway is actually needed, plus a hard sanity ceiling.
    clip_durations = [_probe_duration(c) for c in clips]
    avg_clip = sum(clip_durations) / len(clip_durations)
    max_iters = min(5000, int(target_duration / avg_clip) + len(clips) + 10)
    lines, total, i = [], 0.0, 0
    while total < target_duration and i < max_iters:
        clip = clips[i % len(clips)]
        lines.append(f"file '{clip.resolve()}'")
        total += clip_durations[i % len(clips)]
        i += 1
    if total < target_duration:
        print(f"    Warning: drone background ({total:.0f}s) still short of target ({target_duration:.0f}s) after {i} clips")
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


# Shown only 1 second (down from 3, feedback 2026-07-06): long enough to
# register as a real disclaimer card, short enough not to cost any watch
# time on the hook.
DISCLAIMER_SEC = 1
# Reworded from scratch 2026-07-06 (own phrasing, not the reference
# channel's wording), same legal substance (fictionalized, inspired by
# real posts, no factual claim, no real-person resemblance), different
# sentence structure and word choice throughout.
DISCLAIMER_TEXT = (
    "This channel dramatizes stories inspired by posts shared across "
    "online communities. Names, details, and dialogue are altered or "
    "invented for narrative purposes, and nothing presented here is a "
    "factual account of real events. Any resemblance to a specific "
    "living or deceased person is unintentional and coincidental."
)


def _render_disclaimer_card():
    """Legal/policy shield shown briefly before the story starts, matching
    real monetized competitor channels (user showed a reference screenshot
    2026-07-04: yellow card, warning emoji). Reworded and restyled
    2026-07-06 per feedback: too close to the reference channel's own
    wording, empty space below the text block, single flat color hurt
    readability. Now uses the channel's own bundled fonts (Fredoka title,
    Open Sans body) instead of a system serif, the whole block is
    vertically centered instead of anchored near the top, and body lines
    alternate two dark, high-contrast colors against the yellow card."""
    card_path = OUTPUT_DIR / "video" / "_disclaimer.png"
    if card_path.exists():
        return card_path
    from PIL import Image, ImageDraw, ImageFont

    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), (247, 216, 90))
    d = ImageDraw.Draw(img)
    title_font = _disclaimer_font(_FREDOKA_PATH, 72)
    body_font = _disclaimer_font(_OPENSANS_PATH, 40)
    BODY_COLORS = [(31, 58, 95), (122, 31, 43)]  # dark navy / dark maroon, alternating per line

    def _warning_triangle(cx, cy, size):
        # Drawn shape, not a unicode emoji glyph. Emoji rendering in a
        # serif font is unreliable cross-platform (same lesson learned with
        # the thumbnail's award-emoji row).
        h = size
        pts = [(cx, cy - h * 0.55), (cx - h * 0.55, cy + h * 0.4), (cx + h * 0.55, cy + h * 0.4)]
        d.polygon(pts, outline=(20, 20, 20), fill=(255, 214, 0), width=4)
        d.text((cx - 7, cy - 4), "!", font=_disclaimer_font(_OPENSANS_PATH, int(size * 0.55)), fill=(20, 20, 20))

    title = "Content Disclaimer"
    title_w = d.textlength(title, font=title_font)
    title_h = 90  # includes the warning triangles' vertical footprint

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

    gap = 50
    line_h = 58
    body_h = len(lines) * line_h
    total_h = title_h + gap + body_h
    y = (H - total_h) / 2  # vertically center the whole block, no dead space below

    tx = (W - title_w) / 2
    d.text((tx, y), title, font=title_font, fill=(30, 160, 130))
    _warning_triangle(tx - 60, y + 34, 66)
    _warning_triangle(tx + title_w + 60, y + 34, 66)

    y += title_h + gap
    for i, line in enumerate(lines):
        lw = d.textlength(line, font=body_font)
        d.text(((W - lw) / 2, y), line, font=body_font, fill=BODY_COLORS[i % 2])
        y += line_h

    img.save(card_path)
    return card_path


_FREDOKA_PATH = ASSETS_BG_DIR.parent / "fonts" / "Fredoka-Variable.ttf"
_OPENSANS_PATH = ASSETS_BG_DIR.parent / "fonts" / "OpenSans-Variable.ttf"


def _disclaimer_font(path, size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
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
         "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
         str(clip_path)],
        check=True, capture_output=True,
    )
    return clip_path


def create_video(audio_path, story_id):
    dur = audio_duration(audio_path)
    captions_path = generate_captions(audio_path, story_id)
    char_cutout = _pick_character(story_id)

    from config import THUMBNAIL_EXPERIMENT
    bg_dir = DRIVING_DIR if THUMBNAIL_EXPERIMENT and DRIVING_DIR.exists() else DRONE_DIR
    drone_concat = _prepare_drone_concat(story_id, dur, bg_dir=bg_dir)
    bg_is_video = drone_concat is not None
    if not bg_is_video:
        drone_concat = _fallback_bg_concat(story_id, dur)

    video_path = OUTPUT_DIR / "video" / f"{story_id}.mp4"

    inputs = ["-f", "concat", "-safe", "0", "-i", str(drone_concat)]
    idx = 0
    bg_in = idx; idx += 1
    char_in = None
    if char_cutout:
        inputs += ["-loop", "1", "-i", str(char_cutout)]
        char_in = idx; idx += 1
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
        # covering the whole frame), matches the reference: background
        # visible above her head, she doesn't dominate the entire vertical
        # space. See user feedback 2026-07-04.
        if char_cutout.stem.startswith("person_v2_"):
            # character_v2/ sources (2nd batch, 2026-07-14) are user-supplied
            # transparent PNGs already composed on a 1280x720 canvas with
            # her final position/headroom baked in by the user. Just scale
            # that whole canvas up 1.5x to the 1920x1080 video frame and
            # overlay at the origin, no cropping or anchoring math needed.
            char_filter = f"[{char_in}:v]scale=1920:1080[char]"
            overlay_x, overlay_y = "0", "0"
        else:
            char_filter = f"[{char_in}:v]scale={CHAR_WIDTH}:{CHAR_HEIGHT}:force_original_aspect_ratio=increase,crop={CHAR_WIDTH}:{CHAR_HEIGHT}[char]"
            overlay_x, overlay_y = "0", "H-h"
        filters.append(char_filter)
        filters.append(f"[{last}][char]overlay=x={overlay_x}:y={overlay_y}[bgchar]")
        last = "bgchar"

    filters.append(f"[{last}]subtitles={captions_path}[withtext]")
    # LIVE per-frame waveform (user confirmed: it must react to the actual
    # narration in real time, not a single static whole-track image, see
    # 2026-07-04 correction). colorkey punches out showwaves' near-black
    # background so only the white line composites; this is the color-safe
    # replacement for the earlier blend=all_mode=screen version, which
    # corrupted the entire frame magenta (root-caused and fixed separately).
    filters.append(f"[{audio_in}:a]showwaves=s=1920x100:mode=cline:colors=white[waveraw]")
    filters.append("[waveraw]format=rgba,colorkey=0x000000:0.15:0.1[wave]")
    filters.append("[withtext][wave]overlay=x=0:y=H-h[vout]")

    content_path = OUTPUT_DIR / "video" / f"{story_id}_content.mp4"
    # -ar 44100 -ac 2 explicit on every audio encode in this function (here
    # and the disclaimer clip): Kokoro's tts_agent.py output was left at its
    # native 24000Hz mono with nothing downstream pinning rate/channels, so
    # each encode pass was implicitly resampling by a different amount and
    # the mismatches compounded into audio/caption drift that grew across
    # the video (root-caused 2026-07-05: captions in sync at 5s, ~2s ahead
    # of the actual words by 30s). One consistent rate/channel layout
    # everywhere removes it, and as a side effect also makes the two clips
    # byte-identical enough on the audio side for a stream-copy concat below.
    #
    # -preset veryfast (was medium): this is the one full-length encode of
    # the whole video (the other two ffmpeg calls in this function are a
    # 3-second disclaimer card and, as of this fix, a stream copy) so preset
    # is the single biggest lever on total render time. crf holds quality
    # constant; veryfast trades a bit of compression efficiency (mildly
    # larger file) for a large cut in encode time, worth it for a 2-hour
    # target video on a free CPU-only GitHub Actions runner.
    cmd = [FFMPEG_BIN, "-y", *inputs,
           "-filter_complex", ";".join(filters),
           "-map", "[vout]", "-map", f"{audio_in}:a",
           "-t", f"{dur + 1.0:.2f}",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
           str(content_path)]
    subprocess.run(cmd, check=True, capture_output=True)

    disclaimer_clip = _render_disclaimer_clip()
    concat_list = OUTPUT_DIR / "video" / f"{story_id}_final_concat.txt"
    concat_list.write_text(f"file '{disclaimer_clip.resolve()}'\nfile '{content_path.resolve()}'\n")
    # Stream copy, not a re-encode: this used to re-encode the ENTIRE
    # multi-hour content clip a second time just to prepend a 3-second
    # disclaimer card, roughly doubling total render time for no visual
    # benefit. Both clips now share identical video (libx264/yuv420p/1080p)
    # and audio (aac/44100/stereo) parameters, so the concat demuxer can
    # just remux them, which takes seconds instead of hours.
    subprocess.run(
        [FFMPEG_BIN, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c", "copy",
         str(video_path)],
        check=True, capture_output=True,
    )
    content_path.unlink()

    for f in (OUTPUT_DIR / "video").glob(f"{story_id}_*concat.txt"):
        f.unlink()
    return video_path, dur + DISCLAIMER_SEC
