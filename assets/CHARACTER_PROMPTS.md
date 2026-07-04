# Google Flow: Character Pool (beda wanita tiap video)

**REVISI 2026-07-04 (v2)**: dari "1 wajah terkunci, 6 ekspresi" jadi "kumpulan wanita
BERBEDA, satu foto per wanita". User lihat langsung video Calm Drama Stories: mereka
gonta-ganti wanita antar-video, bukan 1 karakter tetap. Kita ikuti pola ini.

**Fix framing (v2)**: v1 kemarin "chest-up" (headshot ketat) masih terlalu close-up
dibanding referensi. Referensi: setengah badan (waist-up), sedikit pose (tangan
bersedekap / satu tangan di pinggang / sedikit menyamping), bukan foto pas foto diam.
Semua prompt di bawah sudah direvisi ke framing itu.

Setiap video (thumbnail + overlay video) otomatis pilih SATU wanita dari kumpulan ini
secara rotasi (berdasarkan nomor cerita), jadi thumbnail dan video-nya selalu wanita
yang sama untuk video itu, tapi beda dari video sebelah. Full Calm-Drama-style untuk
semua video, tidak ada lagi kartu Reddit (lihat catatan teknis di bawah).

Tidak perlu reference/ingredient chaining (tiap wanita berdiri sendiri, gak perlu wajah
identik dengan yang lain) — lebih simpel digenerate. Generate dengan background biasa
(BUKAN transparan) — pipeline motong background otomatis (rembg).

## Generate 10 wanita berbeda (siap copy tiap prompt)

person_01:
```
A 28-year-old American woman with long straight dark brown hair, warm brown eyes, wearing a burgundy blouse, standing with arms crossed casually, slight three-quarter turn, bright warm smile. Photorealistic commercial photo, half-body waist-up framing, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, clean softly blurred bright background, 85mm, 16:9, no text, no watermark.
```

person_02:
```
A 34-year-old American woman with a chic shoulder-length auburn bob, green eyes, wearing teal medical scrubs with a stethoscope, one hand resting on her hip, confident relaxed stance, warm confident smile. Photorealistic commercial photo, half-body waist-up framing, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, clean softly blurred bright background, 85mm, 16:9, no text, no watermark.
```

person_03:
```
A 30-year-old American woman with long wavy blonde hair, blue eyes, wearing a cream cable-knit sweater, arms loosely crossed, gentle natural pose, warm smile. Photorealistic commercial photo, half-body waist-up framing, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, clean softly blurred bright background, 85mm, 16:9, no text, no watermark.
```

person_04:
```
A 37-year-old American woman with shoulder-length black hair, dark eyes, wearing a navy blazer, one hand tucked in blazer pocket, confident composed stance. Photorealistic commercial photo, half-body waist-up framing, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, clean softly blurred bright background, 85mm, 16:9, no text, no watermark.
```

person_05:
```
A 26-year-old American woman with curly reddish-brown hair, hazel eyes, wearing a mustard yellow top, hands clasped loosely in front of her, slight playful lean, bright energetic smile. Photorealistic commercial photo, half-body waist-up framing, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, clean softly blurred bright background, 85mm, 16:9, no text, no watermark.
```

person_06:
```
A 41-year-old American woman with short stylish gray-blonde hair, blue-gray eyes, wearing a white blouse and pearl necklace, arms crossed elegantly, poised warm smile. Photorealistic commercial photo, half-body waist-up framing, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, clean softly blurred bright background, 85mm, 16:9, no text, no watermark.
```

person_07:
```
A 32-year-old American woman with long dark hair with subtle highlights, brown eyes, wearing a rose pink cardigan, one hand gently touching her necklace, slight head tilt, warm relatable smile. Photorealistic commercial photo, half-body waist-up framing, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, clean softly blurred bright background, 85mm, 16:9, no text, no watermark.
```

person_08:
```
A 29-year-old American woman with a sleek dark brown ponytail, green eyes, wearing a charcoal blazer over a white top, arms crossed confidently, slight forward lean, professional smile. Photorealistic commercial photo, half-body waist-up framing, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, clean softly blurred bright background, 85mm, 16:9, no text, no watermark.
```

person_09:
```
A 35-year-old American woman with long wavy chestnut hair, hazel eyes, wearing a soft lavender sweater, one hand resting over her chest, warm nurturing expression. Photorealistic commercial photo, half-body waist-up framing, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, clean softly blurred bright background, 85mm, 16:9, no text, no watermark.
```

person_10:
```
A 27-year-old American woman with short curly dark hair, brown eyes, wearing a denim jacket over a striped top, one hand on her hip, slight playful three-quarter turn, bright cheerful smile. Photorealistic commercial photo, half-body waist-up framing, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, clean softly blurred bright background, 85mm, 16:9, no text, no watermark.
```

## Setelah generate
Simpan sebagai `person_01.jpg` ... `person_10.jpg` -> taruh di
`~/Documents/revenge-pipeline/assets/character/` (HAPUS dulu file `char_*.jpg` lama
supaya tidak ikut ke-rotasi campur).

Mau nambah lebih banyak wanita kapan pun: generate lagi dengan pola sama (framing
waist-up + pose natural), kasih nama `person_11.jpg` dst, drop ke folder yang sama,
otomatis ikut rotasi.

## Catatan teknis
- Pipeline otomatis pilih SATU foto per cerita (rotasi berdasar nomor cerita), dipakai
  konsisten untuk thumbnail DAN overlay video cerita itu. Video ke-11 balik lagi ke
  person_01, dst.
- FULL Calm-Drama-style untuk SEMUA video (keputusan 2026-07-04): tidak ada lagi rotasi
  A/B dengan kartu Reddit. Kartu Reddit cuma jadi fallback darurat kalau folder
  character/ kosong, bukan gaya yang sengaja dipakai.
- Overlay video: karakter di-crop otomatis jadi ukuran lebih kecil (640x820), diposisikan
  nempel bawah kiri dengan ruang kosong di atas kepala (bukan menutupi seluruh frame).
  Foto waist-up (bukan headshot ketat) memberi kode ruang crop lebih baik untuk ini.
- Foto akan otomatis dinaikkan brightness/contrast/saturation sedikit di kode (jaga-jaga),
  tapi prompt di atas sudah dirancang supaya foto asli sudah terang dari sono-nya.
