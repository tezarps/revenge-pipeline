# Google Flow: Locked Thumbnail Character ("The Narrator")

Karakter terkunci = wajah sama di semua thumbnail style B (brand recognition ala Calm Drama).
Wanita, menyesuaikan audiens inti niche (wanita AS 25-45, empati wajah sesama wanita).

**REVISI 2026-07-04**: batch pertama (moody/cinematic/desaturated) terlalu redup dan kurang
photogenic dibanding referensi (Calm Drama pakai foto model komersial: pencahayaan studio
terang, kulit glowy, ekspresi hangat/enerjik). Prompt di bawah sudah direvisi ke arah itu.
Kalau kamu regenerasi ulang, timpa file `char_01-06.jpg` yang lama.

## STEP 1: Master character (generate once, save as reference/ingredient)

```
Photorealistic commercial headshot of a 30-year-old American woman, shoulder-length chestnut brown hair styled in soft glossy waves, warm hazel eyes, radiant glowing skin, soft natural makeup with a warm-toned lip. Bright, warm, high-key studio lighting, vivid saturated color grading like a professional lifestyle stock photo. Engaging warm smile, direct eye contact, confident and approachable. Clean softly blurred bright background. Shot on 85mm, shallow depth of field, chest-up framing, 16:9.
```

> Simpan hasil terbaik -> pakai sebagai **Ingredient/reference** di Flow untuk semua
> variasi di bawah, supaya wajahnya identik di tiap thumbnail. Kunci kata yang beda dari
> versi lama: "commercial headshot", "bright high-key studio lighting", "vivid saturated",
> "radiant glowing skin", "engaging warm smile" (bukan "muted desaturated cinematic").

## STEP 2: 6 emotion variants (same woman, use the reference; tiap prompt siap copy utuh)

char_01:
```
The same woman from the reference image, identical face and hair. Shocked expression, eyes wide, lips parted, hand near her chest, wearing a cream knit sweater, bright warm home background softly blurred. Bright high-key studio lighting, vivid saturated color grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

char_02:
```
The same woman from the reference image, identical face and hair. Confident determined stare, slight smirk, arms crossed, wearing a smart charcoal blazer, bright modern office background with soft bokeh city lights. Bright high-key studio lighting, vivid saturated color grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

char_03:
```
The same woman from the reference image, identical face and hair. Warm knowing smirk of vindication, one eyebrow slightly raised, wearing a cream knit sweater, bright cozy living room background softly blurred. Bright high-key studio lighting, vivid saturated color grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

char_04:
```
The same woman from the reference image, identical face and hair. Emotional, eyes glistening with a single tear, looking slightly off-camera, wearing a soft gray cardigan, bright window light background softly blurred. Bright high-key studio lighting, vivid saturated color grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

char_05:
```
The same woman from the reference image, identical face and hair. Calm confident bright smile, shoulders relaxed, wearing a light blue blouse, bright modern office background softly blurred. Bright high-key studio lighting, vivid saturated color grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

char_06:
```
The same woman from the reference image, identical face and hair. Wide-eyed betrayed disbelief, brows raised, mouth slightly open, wearing a dark green sweater, bright hallway with family photos background softly blurred. Bright high-key studio lighting, vivid saturated color grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

## STEP 3
Simpan 6 hasil sebagai `char_01.jpg` ... `char_06.jpg` -> taruh di
`~/Documents/revenge-pipeline/assets/character/` (timpa file lama).

Pipeline otomatis: video ber-ID genap pakai style B (karakter + panel teks bersih,
sekarang ikut skema warna persis Calm Drama), ID ganjil pakai style A (kartu Reddit).
Semua teks di-render pipeline (bukan AI), font Anton (bold-condensed) bundled di
`assets/fonts/`, konsisten di Mac maupun cloud render, tanpa typo.

Sambil menunggu regenerasi: pipeline sudah otomatis menaikkan brightness/contrast/saturation
foto lama di kode (`thumbnail_agent.py`) supaya sementara lebih dekat ke referensi.

## Catatan suara (opsional, keputusan nanti)
Narator audio saat ini wanita (af_bella). Sudah selaras dengan karakter thumbnail wanita.
