# Google Flow — Channel Branding (karakter sebagai wajah brand)

Semua prompt pakai reference/ingredient karakter yang sama dengan thumbnail
(master dari CHARACTER_PROMPTS.md Step 1). TANPA teks — teks banner
di-composite pipeline/aku (zero typo, tipografi konsisten).

## PROMPT — Profile photo / channel avatar (square, circle-crop safe)

```
The same woman from the reference image, identical face and hair. Warm subtle smile with quiet confidence, direct eye contact, wearing the cream knit sweater. Head-and-shoulders portrait, perfectly centered with comfortable headroom, square 1:1 composition, plain dark warm-gray studio background with a soft vignette. Soft cinematic lighting, muted desaturated color grading, 85mm, shallow depth of field, no text, no watermark.
```

> Simpan sebagai `profile.jpg` → upload langsung di Studio → Customization →
> Branding → Picture. (Wajah di tengah — aman untuk crop lingkaran.)

## PROMPT — Banner RAW (tanpa teks, 16:9 lebar)

```
Wide cinematic scene, 16:9 composition. The same woman from the reference image, identical face and hair, standing on the right third of the frame inside a dim moody American living room at dusk, rain streaking the window behind her, warm lamp glow on her face, arms softly crossed, calm knowing expression looking at camera. The left two thirds of the frame: the dim living room fading into soft darkness — open empty space. Muted desaturated color grading, soft cinematic lighting, photorealistic, no text, no watermark.
```

> Simpan sebagai `banner_raw.jpg` → taruh di `~/Documents/revenge-pipeline/assets/`
> → bilang aku. Aku composite teks "Golden Child Stories" + tagline + jadwal di
> area aman tengah (1546x423) pakai Pillow, lalu hasil `banner_final.jpg` tinggal
> diupload di Studio → Customization → Branding → Banner image.

## Alur upload akhir (sekali)
1. Studio → Customization → Branding
2. Picture = `profile.jpg` | Banner = `banner_final.jpg` (hasil composite-ku)
