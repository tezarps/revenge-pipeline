"""Word-level caption timing via faster-whisper, grouped into short caption
cards and written as an ASS subtitle file (matches the Calm Drama Stories
caption-card look: dark rounded box, white text, 2 lines, synced to speech)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR

WORDS_PER_CARD = 8
_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        # tiny.en: switched from base.en 2026-07-04 after run #3 hit 139.6 min
        # total (vs ~50-70 min pre-Calm-Drama), pushing close to GitHub's free
        # 2,000 min/month private-repo ceiling at 3 videos/week. Clean
        # single-speaker TTS audio (not noisy/accented) doesn't need base's
        # extra accuracy for word-level caption timing.
        _model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
    return _model


def _transcribe_words(audio_path):
    model = _get_model()
    segments, _ = model.transcribe(str(audio_path), word_timestamps=True)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append((w.start, w.end, w.word.strip()))
    return words


def _group_cards(words, per_card=WORDS_PER_CARD):
    cards = []
    for i in range(0, len(words), per_card):
        chunk = words[i:i + per_card]
        if not chunk:
            continue
        start = chunk[0][0]
        end = chunk[-1][1]
        text = " ".join(w[2] for w in chunk)
        cards.append((start, end, text))
    return cards


def _ass_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Card,Arial,56,&H00FFFFFF,&H000000FF,&H00000000,&HD8000000,1,0,0,0,100,100,0,0,3,14,0,5,620,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def build_ass(cards, out_path):
    lines = [ASS_HEADER]
    for start, end, text in cards:
        words = text.split()
        mid = (len(words) + 1) // 2
        line1, line2 = " ".join(words[:mid]), " ".join(words[mid:])
        body = f"{line1}\\N{line2}" if line2 else line1
        lines.append(
            f"Dialogue: 0,{_ass_time(start)},{_ass_time(end)},Card,,0,0,0,,{body}\n"
        )
    out_path.write_text("".join(lines))
    return out_path


def generate_captions(audio_path, story_id):
    """Transcribe audio and write an .ass caption file. Cached: skips
    transcription if the .ass already exists for this story."""
    ass_path = OUTPUT_DIR / "captions" / f"{story_id}.ass"
    ass_path.parent.mkdir(exist_ok=True)
    if ass_path.exists():
        return ass_path
    print("    Transcribing narration for caption sync (faster-whisper)...")
    words = _transcribe_words(audio_path)
    cards = _group_cards(words)
    build_ass(cards, ass_path)
    print(f"    {len(cards)} caption cards written")
    return ass_path
