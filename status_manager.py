"""Live per-stage status, committed to git after every stage transition so
the dashboard can poll status.json and show near-real-time progress without
needing a database (repo is public, git push is the only persistence layer).
Best-effort: a failed git push here never breaks the pipeline itself."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

STATUS_FILE = Path(__file__).parent / "status.json"

STAGES = {
    "script":   {"label": "Writing script",       "icon": "pen"},
    "audio":    {"label": "Kokoro narration",     "icon": "mic"},
    "captions": {"label": "Syncing captions",     "icon": "text"},
    "assembly": {"label": "Assembling video",     "icon": "film"},
    "thumb":    {"label": "Thumbnail + metadata", "icon": "image"},
    "upload":   {"label": "Uploading to YouTube", "icon": "upload"},
}


def _read():
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text())
        except Exception:
            pass
    return {"story_id": None, "premise": None, "stage": None, "stages": {}, "updated_at": None}


def _ensure_git_identity():
    # Defensive backstop: the workflow now sets this up-front too (fixed
    # 2026-07-05), but every mid-run commit silently failed for months before
    # that without it, so self-configuring here means this module never
    # depends on the caller getting the order right.
    subprocess.run(["git", "config", "user.name", "revenge-pipeline-bot"], capture_output=True)
    subprocess.run(["git", "config", "user.email", "bot@users.noreply.github.com"], capture_output=True)


def _write_and_push(data, attempts=3):
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    STATUS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    _ensure_git_identity()
    for attempt in range(attempts):
        try:
            subprocess.run(["git", "add", "status.json"], check=True, capture_output=True)
            diff = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
            if diff.returncode == 0:
                return  # nothing changed
            subprocess.run(["git", "commit", "-m", "status: live progress [skip ci]"], check=True, capture_output=True)
            # Reset onto latest origin/main instead of rebasing — status.json
            # is disposable scratch state, so there's nothing worth a real
            # rebase conflict resolution over; a plain fast-forward retry is
            # both simpler and can't get stuck mid-rebase.
            subprocess.run(["git", "fetch", "origin", "main", "--quiet"], check=True, capture_output=True)
            subprocess.run(["git", "reset", "--mixed", "origin/main", "--quiet"], check=True, capture_output=True)
            STATUS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            subprocess.run(["git", "add", "status.json"], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "status: live progress [skip ci]"], check=True, capture_output=True)
            subprocess.run(["git", "push", "--quiet"], check=True, capture_output=True)
            return
        except Exception as e:
            if attempt == attempts - 1:
                print(f"    (status push skipped after {attempts} attempts: {e})")


def run_start(story_id, premise):
    _write_and_push({"story_id": story_id, "premise": premise, "stage": None, "stages": {}, "run_state": "running"})


def stage_start(key, detail=""):
    data = _read()
    data["stage"] = key
    data.setdefault("stages", {})[key] = {**STAGES[key], "status": "running", "detail": detail}
    _write_and_push(data)


def stage_done(key, detail=""):
    data = _read()
    data.setdefault("stages", {})[key] = {**STAGES[key], "status": "done", "detail": detail}
    _write_and_push(data)


def run_done(video_id=None):
    data = _read()
    data["run_state"] = "done"
    data["video_id"] = video_id
    _write_and_push(data)


def run_failed(stage_key, error):
    data = _read()
    data["run_state"] = "failed"
    data.setdefault("stages", {})[stage_key] = {**STAGES.get(stage_key, {"label": stage_key, "icon": "x"}), "status": "error", "detail": str(error)[:300]}
    _write_and_push(data)
