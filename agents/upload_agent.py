"""YouTube upload, lean adaptation of apophenia-pipeline's upload_agent.
Keeps the IPv4 fix and the live publishAt collision check; drops playlists,
Shorts and analytics for v1. Publish cadence: 1 video/day at 10:30 ET
(user correction 2026-07-08: the original 3-slots/day design, matching
Calm Drama Stories' measured cadence, only makes sense if production
actually keeps pace at 3 videos/day. Real production is 1/day via the
daily cron, so 3 slots just meant multiple videos landing on the same
day whenever more than one run happened close together, e.g. during a
bug-fix session, instead of spreading one per day as intended)."""
import pickle
import socket
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Force IPv4 — upload.googleapis.com resolves IPv6-first but IPv6 is broken on
# some networks; Python/httplib2 doesn't fall back like curl does (confirmed
# root cause in apophenia-pipeline 2026-06-24).
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_only(host, port, *args, **kwargs):
    results = _orig_getaddrinfo(host, port, *args, **kwargs)
    ipv4 = [r for r in results if r[0] == socket.AF_INET]
    return ipv4 if ipv4 else results
socket.getaddrinfo = _ipv4_only

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import TOKEN_FILE, YOUTUBE_CLIENT_SECRET

SCOPES = ["https://www.googleapis.com/auth/youtube"]

# One slot/day (was 3, see module docstring), all 7 days.
PUBLISH_SLOTS_ET = [(10, 30)]
PUBLISH_WEEKDAYS = {0, 1, 2, 3, 4, 5, 6}


def _get_service():
    creds = None
    if Path(TOKEN_FILE).exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    elif not creds:
        # First-time auth — opens a browser, needs youtube_client_secret.json.
        flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRET, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)


def _et_zone():
    # EDT (Mar-Nov) = UTC-4, EST = UTC-5. Coarse DST check is fine at this cadence.
    month = datetime.now(timezone.utc).month
    return timezone(timedelta(hours=-4 if 3 < month < 11 else -5))


def _latest_scheduled_utc(yt):
    """Live check against the channel so automated uploads never collide with
    a manually rescheduled video (stale-cache bug confirmed in Apophenia)."""
    try:
        res = yt.search().list(part="id", forMine=True, type="video", maxResults=50).execute()
        ids = [i["id"]["videoId"] for i in res.get("items", [])]
        if not ids:
            return None
        det = yt.videos().list(part="status", id=",".join(ids)).execute()
        now = datetime.now(timezone.utc)
        future = [
            datetime.strptime(v["status"]["publishAt"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            for v in det["items"]
            if v["status"].get("publishAt")
            and datetime.strptime(v["status"]["publishAt"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) >= now
        ]
        return max(future) if future else None
    except Exception as e:
        print(f"    Warning: live publishAt check failed ({e}) — scheduling from now")
        return None


def _next_publish_time(yt):
    et = _et_zone()
    anchor = datetime.now(et)
    latest = _latest_scheduled_utc(yt)
    if latest and latest.astimezone(et) > anchor:
        anchor = latest.astimezone(et)

    # Walk forward day by day, checking each of today's remaining slots (or
    # tomorrow's, etc.) in order, until we pass one that's after anchor and
    # on a valid weekday.
    day = anchor
    for _ in range(14):  # generous cap, cadence is daily so this resolves fast
        if day.weekday() in PUBLISH_WEEKDAYS:
            for hour, minute in PUBLISH_SLOTS_ET:
                target = day.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if target > anchor:
                    return target.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        day = (day + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    raise RuntimeError("_next_publish_time: no valid slot found in 14 days — check PUBLISH_WEEKDAYS")


def upload_video(video_path, thumb_path, metadata):
    yt = _get_service()
    publish_at = _next_publish_time(yt)
    body = {
        "snippet": {
            "title": metadata["title"][:100],
            "description": metadata["description"],
            "tags": metadata.get("tags", [])[:15],
            "categoryId": "24",  # Entertainment
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at,
            "selfDeclaredMadeForKids": False,
            # "Altered content" disclosure — AI narration + AI imagery.
            # Set per-video via API so there's nothing to toggle in Studio.
            "containsSyntheticMedia": True,
        },
    }
    media = MediaFileUpload(str(video_path), chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"    upload {int(status.progress() * 100)}%")
    video_id = resp["id"]

    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumb_path))).execute()
    except Exception as e:
        print(f"    Warning: thumbnail set failed: {e}")

    print(f"    Scheduled for {publish_at} UTC")
    return video_id, publish_at
