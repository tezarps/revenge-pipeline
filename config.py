import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

# Sonnet for the 6-7K word story (long-form coherence is the channel's only
# moat vs the dead clone farms — see revenge-story-lab/SCHEMA_COMPARISON.md),
# Haiku for cheap short jobs (titles, tags, premise ideas).
SONNET_MODEL = "claude-sonnet-5"
HAIKU_MODEL = "claude-haiku-4-5"

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_BG_DIR = BASE_DIR / "assets" / "bg"
STORIES_FILE = BASE_DIR / "stories.json"
TOKEN_FILE = BASE_DIR / "youtube_token.pickle"
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET_PATH", "youtube_client_secret.json")

# Kokoro TTS — local, $0/video. am_michael picked by user 2026-07-03 after
# A/B against am_adam (revenge-story-lab/pilot/). Model files are fetched to
# ~/.cache/revenge-tts/ on first run (~340MB, cached across GH Actions runs).
KOKORO_VOICE = "am_michael"
KOKORO_SPEED = 1.0
KOKORO_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
KOKORO_VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
KOKORO_CACHE = Path(os.environ.get("KOKORO_CACHE", Path.home() / ".cache" / "revenge-tts"))

# Target script length. 6000-7500 words ≈ 33-40 min narration — the niche's
# sweet spot (mid-rolls every ~8 min, matches Reddit Family Tales durations).
SCRIPT_MIN_WORDS = 5500
SCRIPT_MAX_WORDS = 7500

FFMPEG_BIN = os.environ.get("FFMPEG_BIN", "ffmpeg")
FFPROBE_BIN = os.environ.get("FFPROBE_BIN", "ffprobe")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
for sub in ("scripts", "audio", "video", "thumbs", "metadata"):
    (OUTPUT_DIR / sub).mkdir(exist_ok=True)
