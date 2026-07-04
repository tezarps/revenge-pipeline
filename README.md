# Revenge Pipeline

Full-auto YouTube channel: revenge/betrayal story narration (US audience, RPM ~$10-12).
Copy of the apophenia-pipeline architecture, simplified. **No approval gates, Telegram is notify-only.**

- Riset & skema konten: `~/Documents/revenge-story-lab/` (SCHEMA_COMPARISON.md = formula terkunci)
- Script: Claude **Sonnet 5** (~$0.11/video) · judul/tags/premis: Haiku
- TTS: **Kokoro lokal, suara am_michael, $0** (bukan ElevenLabs)
- Visual: slideshow Ken Burns dari `assets/bg/` (fallback: gradient gelap otomatis)
- Thumbnail: Pillow, teks besar formula niche (baris terakhir merah)
- Upload: dijadwalkan Tue/Thu/Sat 3 PM ET; render Mon/Wed/Fri via GitHub Actions cron
- State: `stories.json` di repo, di-commit balik oleh workflow

## Jalur produksi
`scheduler.py` → premis (auto top-up kalau habis) → script (schema 9-beat) → Kokoro TTS →
ffmpeg video → metadata+thumbnail → upload (scheduled publishAt) → Telegram notif tiap tahap.

## Setup sekali (manual, ~20 menit)
1. Buat channel YouTube baru (brand account).
2. Google Cloud Console: project baru → aktifkan YouTube Data API v3 → OAuth client (Desktop) → download `youtube_client_secret.json` ke folder ini.
3. `python3 setup_youtube_auth.py` di Mac (buka browser sekali) → menghasilkan `youtube_token.pickle`.
4. Buat repo GitHub **private** dari folder ini.
5. GitHub Secrets: `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`,
   `YOUTUBE_CLIENT_SECRET_B64` (`base64 -i youtube_client_secret.json`),
   `YOUTUBE_TOKEN_B64` (`base64 -i youtube_token.pickle`).
6. (Opsional) taruh 3-6 gambar moody 1920x1080 di `assets/bg/` + `assets/bg/thumb_base.jpg`.

## Test lokal
```bash
pip install -r requirements.txt
python3 scheduler.py --dry-run   # render sampai video, TIDAK upload
```
Run pertama download model Kokoro ~340MB ke `~/.cache/revenge-tts/`.

## Test cloud
Actions tab → "Revenge Pipeline" → Run workflow → centang dry_run.
