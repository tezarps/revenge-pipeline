# Google Flow — Locked Thumbnail Character ("The Narrator")

Karakter terkunci = wajah sama di semua thumbnail style B (brand recognition ala Calm Drama).
Wanita — menyesuaikan audiens inti niche (wanita AS 25–45, empati wajah sesama wanita).

## STEP 1 — Master character (generate once, save as reference/ingredient)

```
Photorealistic portrait of a 31-year-old American woman, shoulder-length chestnut brown hair with soft waves, hazel eyes, minimal natural makeup, wearing a simple cream knit sweater. Warm relatable girl-next-door face with a hint of quiet strength, slightly tired around the eyes. Neutral expression, looking directly at camera. Soft cinematic lighting, muted desaturated color grading, blurred dim living-room background. Shot on 85mm, shallow depth of field, chest-up framing, 16:9.
```

> Simpan hasil terbaik → pakai sebagai **Ingredient/reference** di Flow untuk semua
> variasi di bawah, supaya wajahnya identik di tiap thumbnail.

## STEP 2 — 6 emotion variants (same woman, use the reference; tiap prompt siap copy utuh)

char_01:
```
The same woman from the reference image, identical face and hair. Shocked and hurt, eyes wide, lips parted, hand near her chest, wearing a cream knit sweater, dim family dining room background. Soft cinematic lighting, muted desaturated grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

char_02:
```
The same woman from the reference image, identical face and hair. Cold determined stare, jaw set, arms crossed, wearing a charcoal blazer, night office background with city lights. Soft cinematic lighting, muted desaturated grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

char_03:
```
The same woman from the reference image, identical face and hair. Quiet smirk of vindication, one eyebrow slightly raised, wearing a cream knit sweater, dusk living room background. Soft cinematic lighting, muted desaturated grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

char_04:
```
The same woman from the reference image, identical face and hair. Holding back tears, eyes glistening, looking slightly off-camera, wearing a gray cardigan, rainy window background. Soft cinematic lighting, muted desaturated grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

char_05:
```
The same woman from the reference image, identical face and hair. Calm confident half-smile, shoulders relaxed, wearing a light blue blouse, bright modern office background. Soft cinematic lighting, muted desaturated grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

char_06:
```
The same woman from the reference image, identical face and hair. Betrayed disbelief, brows furrowed, mouth slightly open, wearing a dark green sweater, dark hallway with family photos background. Soft cinematic lighting, muted desaturated grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

## STEP 3
Simpan 6 hasil sebagai `char_01.jpg` … `char_06.jpg` → taruh di
`~/Documents/revenge-pipeline/assets/character/`

Pipeline otomatis: video ber-ID genap pakai style B (karakter + panel teks bersih),
ID ganjil pakai style A (kartu Reddit). Teks di-render pipeline (bukan AI) — bersih,
konsisten, tanpa typo: baris hook putih + baris payoff kuning, maksimal 12 kata.

## Catatan suara (opsional, keputusan nanti)
Narator audio saat ini pria (am_michael). Mismatch wajah-wanita/suara-pria itu standar
di niche ini (kompetitor melakukannya), TAPI kalau data retention nanti lemah, opsi murah:
A/B suara wanita Kokoro (af_heart / af_bella) di beberapa video — $0, tinggal ganti config.
