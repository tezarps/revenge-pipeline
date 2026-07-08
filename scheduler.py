#!/usr/bin/env python3
"""Revenge-pipeline orchestrator — copy of the Apophenia flow, simplified:
state lives in stories.json (committed back by the GitHub Actions workflow),
Telegram is NOTIFY-ONLY (no approval gates — user decision 2026-07-03),
TTS is local Kokoro ($0), scripts are Sonnet 5 (~$0.11/video)."""
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import status_manager as sm
from agents import story_agent
from agents.tts_agent import generate_audio
from agents.assembly_agent import create_video
from agents.thumbnail_agent import generate_thumbnail_ab
from agents.upload_agent import upload_video
from config import OUTPUT_DIR, SCRIPT_MIN_WORDS
from telegram_notify import notify


def run(dry_run=False):
    print(f"\n{'='*52}\n  Revenge Pipeline — {datetime.now():%Y-%m-%d %H:%M}\n{'='*52}\n")

    story = story_agent.next_pending()
    if not story:
        print("No pending stories and queue top-up failed.")
        notify("⚠️ Revenge pipeline — no pending stories, top-up failed")
        sys.exit(1)

    sid = story["id"]
    print(f"Story #{sid}: {story['premise']}\n")
    notify(f"🎬 Revenge pipeline — started\nStory #{sid}: {story['premise'][:200]}")
    sm.run_start(sid, story["premise"])

    stage = "script"
    try:
        # [1/6] Script — cache-aware so a failed later stage never re-pays the LLM
        sm.stage_start("script", "Sonnet 5 writing...")
        script_path = OUTPUT_DIR / "scripts" / f"{sid}.txt"
        cached_wc = len(script_path.read_text().split()) if script_path.exists() else 0
        if cached_wc >= SCRIPT_MIN_WORDS:
            script = script_path.read_text()
            print(f"[1/6] Script: cached ({cached_wc:,} words)")
        else:
            if cached_wc:
                # Stale cache from before a word-count target bump — a short
                # cached script would otherwise be reused forever and silently
                # ignore any SCRIPT_MIN_WORDS increase (bit us 2026-07-05).
                print(f"[1/6] Script: cached copy is stale ({cached_wc:,} < {SCRIPT_MIN_WORDS:,} target), regenerating...")
                (OUTPUT_DIR / "metadata" / f"{sid}.json").unlink(missing_ok=True)
            else:
                print("[1/6] Script: writing with Sonnet 5...")
            script = story_agent.generate_script(story)
            script_path.write_text(script)
            print(f"      {len(script.split()):,} words")
        sm.stage_done("script", f"{len(script.split()):,} words")
        notify(f"✍️ #{sid} script ready — {len(script.split()):,} kata")

        # [2/6] TTS — Kokoro local. Never auto-delete finished audio
        # (feedback_narava_no_autocleanup).
        stage = "audio"
        sm.stage_start("audio", "Kokoro af_bella narrating...")
        audio_path = OUTPUT_DIR / "audio" / f"{sid}.mp3"
        if audio_path.exists():
            print("[2/6] Audio: cached")
        else:
            print("[2/6] Audio: Kokoro TTS (af_bella)...")
            audio_path = generate_audio(script, sid)
        sm.stage_done("audio")
        notify(f"🎙️ #{sid} audio ready")

        # [3/6] Metadata + thumbnail
        stage = "thumb"
        sm.stage_start("thumb", "Writing title/tags + rendering thumbnail...")
        print("[3/6] Metadata + thumbnail...")
        meta_path = OUTPUT_DIR / "metadata" / f"{sid}.json"
        if meta_path.exists():
            metadata = json.loads(meta_path.read_text())
        else:
            metadata = story_agent.generate_metadata(story, script)
            meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
        # Style B (character + colored stack) always tried first; style A
        # (Reddit-card) is an emergency fallback only, see thumbnail_ab docstring.
        thumb_path = generate_thumbnail_ab(metadata["title"], metadata.get("thumb_lines"), sid)
        print(f"      Title: {metadata['title']}")
        sm.stage_done("thumb", metadata["title"][:80])

        # [4/6] Captions + Video assembly
        stage = "assembly"
        sm.stage_start("assembly", "ffmpeg: character + drone + captions + waveform...")
        print("[4/6] Assembling video (ffmpeg)...")
        video_path, dur = create_video(audio_path, sid)
        print(f"      {dur/60:.1f} min, {video_path.stat().st_size/1e6:.0f}MB")
        sm.stage_done("assembly", f"{dur/60:.1f} min, {video_path.stat().st_size/1e6:.0f}MB")

        if dry_run:
            print(f"\n⏸ DRY RUN — stopping before upload.\n  Video: {video_path}\n  Thumb: {thumb_path}")
            notify(f"🧪 #{sid} dry run selesai — {dur/60:.1f} mnt, belum diupload")
            sm.run_done()
            return

        # [5/6] Upload
        stage = "upload"
        sm.stage_start("upload")
        print("[5/6] Uploading to YouTube...")
        video_id, publish_at = upload_video(video_path, thumb_path, metadata)
        story_agent.mark(sid, "done", video_id=video_id, publish_at=publish_at)
        sm.stage_done("upload", f"youtube.com/watch?v={video_id}")
        sm.run_done(video_id=video_id)
        print(f"\n✓ Complete — youtube.com/watch?v={video_id}")
        notify(
            f"✅ Revenge pipeline — published\n#{sid}: {metadata['title']}\n"
            f"youtube.com/watch?v={video_id}\nTayang: {publish_at} UTC"
        )

    except Exception as e:
        print(f"\n✗ Failed at [{stage}]: {e}")
        traceback.print_exc()
        story_agent.mark(sid, "failed")
        sm.run_failed(stage, e)
        notify(f"❌ Revenge pipeline — failed at [{stage}]\n#{sid}\n{str(e)[:300]}")
        # Exit non-zero so GitHub Actions shows red (Apophenia lesson 2026-06-21).
        sys.exit(1)


if __name__ == "__main__":
    run(dry_run="--dry-run" in sys.argv)
