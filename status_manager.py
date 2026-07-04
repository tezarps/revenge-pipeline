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


def _write_and_push(data):
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    STATUS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    try:
        subprocess.run(["git", "add", "status.json"], check=True, capture_output=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if diff.returncode == 0:
            return  # nothing changed
        subprocess.run(["git", "commit", "-m", "status: live progress [skip ci]"], check=True, capture_output=True)
        subprocess.run(["git", "pull", "--rebase", "--quiet"], check=True, capture_output=True)
        subprocess.run(["git", "push", "--quiet"], check=True, capture_output=True)
    except Exception as e:
        print(f"    (status push skipped: {e})")


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
