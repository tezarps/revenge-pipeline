"""Kokoro TTS, local/CPU, $0 per video. Replaces ElevenLabs entirely
(user decision 2026-07-03: script cost stays, TTS cost goes to zero).
Chunks the script by sentence groups, synthesizes each, concatenates with
short pauses, writes mp3 via ffmpeg."""
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    OUTPUT_DIR, FFMPEG_BIN,
    KOKORO_VOICE, KOKORO_VOICE_ALT, KOKORO_SPEED, KOKORO_CACHE, KOKORO_MODEL_URL, KOKORO_VOICES_URL,
)

MAX_CHUNK_CHARS = 900  # keeps Kokoro prosody stable; same idea as Narava's MAX_CHUNK_CHARS
PAUSE_SEC = 0.45       # breath between chunks


def voice_for_story(story_id):
    """Alternates KOKORO_VOICE/KOKORO_VOICE_ALT every other video (user
    decision 2026-07-15: af_bella stays primary, bf_isabella as an
    occasional change of pace, not a full swap)."""
    return KOKORO_VOICE_ALT if int(story_id) % 2 == 0 else KOKORO_VOICE


def _ensure_models():
    KOKORO_CACHE.mkdir(parents=True, exist_ok=True)
    model = KOKORO_CACHE / "kokoro-v1.0.onnx"
    voices = KOKORO_CACHE / "voices-v1.0.bin"
    for path, url in ((model, KOKORO_MODEL_URL), (voices, KOKORO_VOICES_URL)):
        if not path.exists():
            print(f"    Downloading {path.name} (first run only)...")
            tmp = path.with_suffix(".tmp")
            urllib.request.urlretrieve(url, tmp)
            tmp.rename(path)
    return model, voices


def _chunks(text):
    sentences = re.split(r"(?<=[.!?])\s+", text.replace("\n", " ").strip())
    buf = ""
    for s in sentences:
        if buf and len(buf) + len(s) + 1 > MAX_CHUNK_CHARS:
            yield buf
            buf = s
        else:
            buf = f"{buf} {s}".strip()
    if buf:
        yield buf


def generate_audio(script, story_id):
    from kokoro_onnx import Kokoro

    model, voices = _ensure_models()
    kokoro = Kokoro(str(model), str(voices))

    voice = voice_for_story(story_id)
    parts = list(_chunks(script))
    print(f"    {len(parts)} chunks, voice={voice}")
    audio, sr = [], 24000
    for i, chunk in enumerate(parts, 1):
        samples, sr = kokoro.create(chunk, voice=voice, speed=KOKORO_SPEED, lang="en-us")
        audio.append(samples)
        audio.append(np.zeros(int(sr * PAUSE_SEC), dtype=samples.dtype))
        if i % 10 == 0 or i == len(parts):
            print(f"    chunk {i}/{len(parts)}")

    wav_path = OUTPUT_DIR / "audio" / f"{story_id}.wav"
    sf.write(wav_path, np.concatenate(audio), sr)

    # Single loudnorm pass (lesson from narava-pipeline: double-normalizing
    # audibly pumps), then mp3 for the video mux. Explicit -ar 44100: Kokoro
    # outputs 24000Hz and nothing downstream pinned a rate, so ffmpeg's
    # encoders were implicitly resampling at different points in the
    # pipeline (mp3 encode, then again at the mp3->AAC mux, then again at
    # the final disclaimer+content concat re-encode), and each implicit
    # resample is a separate clock-rate approximation. They compounded
    # into audio/caption drift that grew over the length of the video
    # (confirmed 2026-07-05: captions synced at the 5s mark, ~2s ahead of
    # the actual words by the 30s mark). Pinning one consistent rate here,
    # matching the disclaimer clip's anullsrc=r=44100, removes the mismatch
    # at its source instead of re-deriving captions after the fact.
    mp3_path = OUTPUT_DIR / "audio" / f"{story_id}.mp3"
    subprocess.run(
        [FFMPEG_BIN, "-y", "-i", str(wav_path), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
         "-ar", "44100", "-b:a", "192k", str(mp3_path)],
        check=True, capture_output=True,
    )
    wav_path.unlink()
    return mp3_path
