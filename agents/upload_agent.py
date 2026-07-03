"""YouTube upload — lean adaptation of apophenia-pipeline's upload_agent.
Keeps the IPv4 fix and the live publishAt collision check; drops playlists,
Shorts and analytics for v1. Publishes on a fixed weekday cadence at 3 PM US
Eastern (audience: US women 25-45; evening peak ~7-9 PM ET, publish ahead of
it — same principle as Apophenia's AU timing)."""
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

PUBLISH_HOUR_ET = 15          # 3 PM Eastern
PUBLISH_WEEKDAYS = {1, 3, 5}  # Tue / Thu / Sat (Mon=0)


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

    target = anchor.replace(hour=PUBLISH_HOUR_ET, minute=0, second=0, microsecond=0)
    while target <= anchor or target.weekday() not in PUBLISH_WEEKDAYS:
        target += timedelta(days=1)
        target = target.replace(hour=PUBLISH_HOUR_ET)
    return target.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


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
