# Google Flow — Locked Thumbnail Character ("The Narrator")

Karakter terkunci = wajah sama di semua thumbnail style B (brand recognition ala Calm Drama).
Suara channel = pria (am_michael) → karakter pria, biar wajah cocok dengan suara.

## STEP 1 — Master character (generate once, save as reference/ingredient)

```
Photorealistic portrait of a 32-year-old American man, short dark brown hair neatly cut, light stubble, hazel eyes, wearing a plain navy henley shirt. Trustworthy everyman face, slightly tired around the eyes. Neutral expression, looking directly at camera. Soft cinematic lighting, muted desaturated color grading, blurred dim living-room background. Shot on 85mm, shallow depth of field, chest-up framing, 16:9.
```

> Simpan hasil terbaik → pakai sebagai **Ingredient/reference** di Flow untuk semua variasi
> di bawah, supaya wajahnya identik.

## STEP 2 — 6 emotion variants (same man, use the reference)

Template (ganti bagian [EXPRESSION + WARDROBE]):
```
The same man from the reference image, identical face and hair. [EXPRESSION + WARDROBE]. Soft cinematic lighting, muted desaturated grading, blurred moody background matching the scene, 85mm, chest-up, 16:9, no text.
```

1. `Shocked and hurt, eyebrows raised, lips parted, hand slightly raised — wearing the navy henley, dim family dining room background`
2. `Cold determined stare, jaw set, arms crossed — wearing a charcoal suit, night office background with city lights`
3. `Quiet smirk of vindication, one eyebrow slightly raised — navy henley, dusk living room background`
4. `Exhausted and betrayed, eyes glistening, looking slightly off-camera — gray hoodie, rainy window background`
5. `Calm confident half-smile, arms relaxed — light blue dress shirt, bright modern office background`
6. `Serious warning look, leaning slightly toward camera — navy henley, dark hallway background`

## STEP 3
Simpan 6 hasil sebagai `char_01.jpg` … `char_06.jpg` → taruh di
`~/Documents/revenge-pipeline/assets/character/`

Pipeline otomatis: video ber-ID genap pakai style B (karakter + panel teks bersih),
ID ganjil pakai style A (kartu Reddit). Teks di-render pipeline (bukan AI) — bersih,
konsisten, tanpa typo: baris hook putih + baris payoff kuning, maksimal 12 kata.
