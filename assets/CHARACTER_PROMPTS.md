# Google Flow — Locked Thumbnail Character ("The Narrator")

Karakter terkunci = wajah sama di semua thumbnail style B (brand recognition ala Calm Drama).
Wanita — menyesuaikan audiens inti niche (wanita AS 25–45, empati wajah sesama wanita).

## STEP 1 — Master character (generate once, save as reference/ingredient)

```
Photorealistic portrait of a 31-year-old American woman, shoulder-length chestnut brown hair with soft waves, hazel eyes, minimal natural makeup, wearing a simple cream knit sweater. Warm relatable girl-next-door face with a hint of quiet strength, slightly tired around the eyes. Neutral expression, looking directly at camera. Soft cinematic lighting, muted desaturated color grading, blurred dim living-room background. Shot on 85mm, shallow depth of field, chest-up framing, 16:9.
```

> Simpan hasil terbaik → pakai sebagai **Ingredient/reference** di Flow untuk semua
> variasi di bawah, supaya wajahnya identik di tiap thumbnail.

## STEP 2 — 6 emotion variants (same woman, use the reference)

Template (ganti bagian [EXPRESSION + WARDROBE + BACKGROUND]):
```
The same woman from the reference image, identical face and hair. [EXPRESSION + WARDROBE + BACKGROUND]. Soft cinematic lighting, muted desaturated grading, 85mm, chest-up framing, 16:9, no text, no watermark.
```

1. `Shocked and hurt, eyes wide, lips parted, hand near her chest — cream knit sweater, dim family dining room background`
2. `Cold determined stare, jaw set, arms crossed — charcoal blazer, night office background with city lights`
3. `Quiet smirk of vindication, one eyebrow slightly raised — cream sweater, dusk living room background`
4. `Holding back tears, eyes glistening, looking slightly off-camera — gray cardigan, rainy window background`
5. `Calm confident half-smile, shoulders relaxed — light blue blouse, bright modern office background`
6. `Betrayed disbelief, brows furrowed, mouth slightly open — dark green sweater, dark hallway with family photos background`

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
