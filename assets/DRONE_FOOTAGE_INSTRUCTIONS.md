# Drone/landscape stock footage (free, no API key, no account needed)

Sama seperti 16 gambar bg: kamu download SEKALI, disimpan, dipakai ulang selamanya
di semua video (rotasi otomatis per video, sama seperti mekanisme bg image).

## Sumber (pilih salah satu atau campur)
- **Mixkit** https://mixkit.co/free-stock-video/drone/ — gratis, tanpa akun, tombol Download langsung.
- **Pexels Video** https://www.pexels.com/search/videos/drone/ — gratis, perlu akun (bisa pakai akun Google), tombol Download.
- **Coverr** https://coverr.co/search?q=aerial — gratis, tanpa akun.

## Kata kunci pencarian yang cocok mood channel
aerial suburb, drone forest autumn, aerial small town, drone highway sunset,
aerial neighborhood rain, drone countryside, aerial city night, drone empty road

## Kriteria pilih klip
- Resolusi minimal 1080p
- Durasi 10-30 detik per klip (klip pendek lebih gampang di-loop, dan lebih variatif)
- Gerakan KAMERA LAMBAT (bukan drone kecepatan tinggi/FPV) — mood-nya harus tenang, melankolis
- Warna netral/musim gugur/langit mendung lebih cocok daripada langit cerah biru terang
- Ambil 8-10 klip

## Simpan di
```
~/Documents/revenge-pipeline/assets/drone/
```
Nama file bebas (mp4/mov/webm semua didukung). Begitu ada minimal 1 file di sini,
pipeline otomatis pakai drone footage; sebelum itu otomatis fallback ke slideshow
16-gambar Ken Burns yang sudah ada (jadi tidak ada yang macet menunggu).

## Setelah download
Bilang aku, aku commit ke repo (video < 20MB masing-masing disarankan biar repo
tidak bengkak; kalau klip Full HD kegedean, aku bisa compress dulu sebelum commit).
