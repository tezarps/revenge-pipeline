import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

# All content generation (script, premises, metadata) runs on DeepSeek's
# top tier now (user decision 2026-07-07, own API key): moved off Sonnet
# 2026-07-06 to cut the ~$1.25/video script cost, then off Haiku too after
# a run failed on an empty Anthropic credit balance, no reason to still
# depend on a second billing account for the cheap calls once the
# expensive one was already gone. deepseek-v4-pro is a reasoning model
# (see agents/llm.py's call_deepseek), so it needs a generous max_tokens
# to leave room for both the hidden reasoning pass and the actual output.
DEEPSEEK_MODEL = "deepseek-v4-pro"

# Shown on the fake-Reddit-card thumbnail (niche house style).
CHANNEL_NAME = os.environ.get("CHANNEL_NAME", "Golden Child Stories")

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_BG_DIR = BASE_DIR / "assets" / "bg"
STORIES_FILE = BASE_DIR / "stories.json"
TOKEN_FILE = BASE_DIR / "youtube_token.pickle"
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET_PATH", "youtube_client_secret.json")

# Kokoro TTS, local, $0/video. af_bella picked by user 2026-07-04 (switched
# from am_michael after locking a female thumbnail character; audience is
# women 25-45, so voice+story+face now align female). Model files are fetched
# to ~/.cache/revenge-tts/ on first run (~340MB, cached across GH Actions runs).
KOKORO_VOICE = "af_bella"
KOKORO_SPEED = 1.0
KOKORO_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
KOKORO_VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
KOKORO_CACHE = Path(os.environ.get("KOKORO_CACHE", Path.home() / ".cache" / "revenge-tts"))

# Target script length. Bumped 2026-07-04 (user decision, "hajar aja"):
# ~18,000-21,000 words ~ 100-120 min narration at Kokoro/af_bella's calibrated
# ~175 wpm (measured from story #2: 5,869 words / 33.3 min). Matches
# Calm Dad Stories' real 2+ hour runtime (7,500-9,300s observed). Longer
# videos accumulate watch-time hours (4,000h YPP threshold) and mid-roll
# slots much faster per upload. NOTE: this multiplies Kokoro/whisper/ffmpeg
# render time roughly 3x per video (see project memory for the GH Actions
# minutes math), decide the compute lever (self-hosted runner / public
# repo) before also cranking upload cadence, or the free 2,000 min/month
# ceiling blows past quickly.
SCRIPT_MIN_WORDS = 17000
SCRIPT_MAX_WORDS = 21000

FFMPEG_BIN = os.environ.get("FFMPEG_BIN", "ffmpeg")
FFPROBE_BIN = os.environ.get("FFPROBE_BIN", "ffprobe")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
for sub in ("scripts", "audio", "video", "thumbs", "metadata"):
    (OUTPUT_DIR / sub).mkdir(exist_ok=True)

# Character numbers 1-7: the user supplies matched pairs, assets/character/
# person_0{N}.jpg (video cutout) and assets/thumb_templates/{N}.png
# (thumbnail background), same woman in both so the thumbnail never shows
# a different person than the video (root-caused 2026-07-06: story #3 and
# #4 published with mismatched thumbnail/video characters because the two
# assets were being picked by two different, uncoordinated rotations).
# Story #2 used character 1 (the original template), so the rotation
# anchors there: story N -> character ((N - 2) % 7) + 1.
CHARACTER_COUNT = 7


def character_number_for_story(story_id):
    return ((int(story_id) - 2) % CHARACTER_COUNT) + 1
