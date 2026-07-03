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

from agents import story_agent
from agents.tts_agent import generate_audio
from agents.assembly_agent import create_video
from agents.thumbnail_agent import generate_thumbnail
from agents.upload_agent import upload_video
from config import OUTPUT_DIR
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

    stage = "script"
    try:
        # [1/5] Script — cache-aware so a failed later stage never re-pays the LLM
        script_path = OUTPUT_DIR / "scripts" / f"{sid}.txt"
        if script_path.exists():
            script = script_path.read_text()
            print(f"[1/5] Script: cached ({len(script.split()):,} words)")
        else:
            print("[1/5] Script: writing with Sonnet 5...")
            script = story_agent.generate_script(story)
            script_path.write_text(script)
            print(f"      {len(script.split()):,} words")
        notify(f"✍️ #{sid} script ready — {len(script.split()):,} kata")

        # [2/5] TTS — Kokoro local. Never auto-delete finished audio
        # (feedback_narava_no_autocleanup).
        stage = "tts"
        audio_path = OUTPUT_DIR / "audio" / f"{sid}.mp3"
        if audio_path.exists():
            print("[2/5] Audio: cached")
        else:
            print("[2/5] Audio: Kokoro TTS (am_michael)...")
            audio_path = generate_audio(script, sid)
        notify(f"🎙️ #{sid} audio ready")

        # [3/5] Metadata + thumbnail
        stage = "metadata"
        print("[3/5] Metadata + thumbnail...")
        meta_path = OUTPUT_DIR / "metadata" / f"{sid}.json"
        if meta_path.exists():
            metadata = json.loads(meta_path.read_text())
        else:
            metadata = story_agent.generate_metadata(story, script)
            meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
        # RFT-style card uses the FULL title as the thumbnail text
        thumb_path = generate_thumbnail(metadata["title"], sid)
        print(f"      Title: {metadata['title']}")

        # [4/5] Video
        stage = "assembly"
        print("[4/5] Assembling video (ffmpeg)...")
        video_path, dur = create_video(audio_path, sid, title_text=metadata["title"])
        print(f"      {dur/60:.1f} min, {video_path.stat().st_size/1e6:.0f}MB")

        if dry_run:
            print(f"\n⏸ DRY RUN — stopping before upload.\n  Video: {video_path}\n  Thumb: {thumb_path}")
            notify(f"🧪 #{sid} dry run selesai — {dur/60:.1f} mnt, belum diupload")
            return

        # [5/5] Upload
        stage = "upload"
        print("[5/5] Uploading to YouTube...")
        video_id, publish_at = upload_video(video_path, thumb_path, metadata)
        story_agent.mark(sid, "done", video_id=video_id)
        print(f"\n✓ Complete — youtube.com/watch?v={video_id}")
        notify(
            f"✅ Revenge pipeline — published\n#{sid}: {metadata['title']}\n"
            f"youtube.com/watch?v={video_id}\nTayang: {publish_at} UTC"
        )

    except Exception as e:
        print(f"\n✗ Failed at [{stage}]: {e}")
        traceback.print_exc()
        story_agent.mark(sid, "failed")
        notify(f"❌ Revenge pipeline — failed at [{stage}]\n#{sid}\n{str(e)[:300]}")
        # Exit non-zero so GitHub Actions shows red (Apophenia lesson 2026-06-21).
        sys.exit(1)


if __name__ == "__main__":
    run(dry_run="--dry-run" in sys.argv)
