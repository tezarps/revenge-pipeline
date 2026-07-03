"""Video assembly — the niche standard is minimal visuals over the narration
(competitors use a static moody image or slow slideshow). V1: cycle the
images in assets/bg/ with a slow Ken Burns zoom, muxed with the narration.
If assets/bg/ is empty, a dark gradient card with the title is generated so
the pipeline never blocks on art."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR, ASSETS_BG_DIR, FFMPEG_BIN, FFPROBE_BIN

SEGMENT_SEC = 90  # how long each background image stays on screen


def audio_duration(path):
    out = subprocess.run(
        [FFPROBE_BIN, "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(out.stdout)["format"]["duration"])


def _fallback_bg(title_text):
    from PIL import Image, ImageDraw
    path = OUTPUT_DIR / "video" / "_fallback_bg.jpg"
    img = Image.new("RGB", (1920, 1080))
    d = ImageDraw.Draw(img)
    for y in range(1080):  # vertical dark-navy gradient
        shade = int(18 + (y / 1080) * 25)
        d.line([(0, y), (1920, y)], fill=(shade, shade, shade + 14))
    img.save(path, quality=90)
    return [path]


def create_video(audio_path, story_id, title_text=""):
    dur = audio_duration(audio_path)
    bgs = sorted(p for p in ASSETS_BG_DIR.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    if not bgs:
        print("    No images in assets/bg/ — using generated gradient background")
        bgs = _fallback_bg(title_text)

    # Build a looped slideshow long enough to cover the narration.
    n_segments = int(dur // SEGMENT_SEC) + 1
    concat_file = OUTPUT_DIR / "video" / f"{story_id}_concat.txt"
    lines = []
    for i in range(n_segments):
        bg = bgs[i % len(bgs)]
        lines.append(f"file '{bg.resolve()}'\nduration {SEGMENT_SEC}")
    lines.append(f"file '{bgs[(n_segments - 1) % len(bgs)].resolve()}'")
    concat_file.write_text("\n".join(lines))

    video_path = OUTPUT_DIR / "video" / f"{story_id}.mp4"
    # Slow push-in (Ken Burns) so the frame is never fully static — YouTube
    # flags dead-static "image + audio" uploads more readily than moving ones.
    vf = (
        "scale=2112:1188,"
        f"zoompan=z='min(zoom+0.00004,1.10)':d={SEGMENT_SEC * 25}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=25,"
        "format=yuv420p"
    )
    subprocess.run(
        [FFMPEG_BIN, "-y",
         "-f", "concat", "-safe", "0", "-i", str(concat_file),
         "-i", str(audio_path),
         "-vf", vf, "-t", f"{dur + 1.5:.2f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "23",
         "-c:a", "aac", "-b:a", "192k", "-shortest",
         str(video_path)],
        check=True, capture_output=True,
    )
    concat_file.unlink()
    return video_path, dur
