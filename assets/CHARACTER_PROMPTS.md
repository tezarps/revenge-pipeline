# Google Flow: Character Pool (beda wanita tiap video)

**REVISI BESAR 2026-07-04**: dari "1 wajah terkunci, 6 ekspresi" jadi "kumpulan wanita
BERBEDA, satu foto per wanita". User lihat langsung video Calm Drama Stories: mereka
gonta-ganti wanita antar-video, bukan 1 karakter tetap. Kita ikuti pola ini.

Setiap video (thumbnail + overlay video) otomatis pilih SATU wanita dari kumpulan ini
secara rotasi (berdasarkan nomor cerita), jadi thumbnail dan video-nya selalu wanita
yang sama untuk video itu, tapi beda dari video sebelah.

Tidak perlu reference/ingredient chaining lagi (tiap wanita berdiri sendiri, gak perlu
wajah identik dengan yang lain) — lebih simpel digenerate.

## Instruksi gaya (berlaku semua foto)
```
Photorealistic commercial headshot, bright warm high-key studio lighting, vivid
saturated color grading like a professional lifestyle stock photo. Radiant glowing
skin, engaging warm expression, direct eye contact. Clean softly blurred bright
background. Shot on 85mm, shallow depth of field, chest-up framing, 16:9, no text,
no watermark.
```

## Generate 10 wanita berbeda (siap copy tiap prompt)

person_01:
```
A 28-year-old American woman with long straight dark brown hair, warm brown eyes, wearing a burgundy blouse, bright smile. Photorealistic commercial headshot, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, direct eye contact, clean softly blurred bright background, 85mm, chest-up framing, 16:9, no text, no watermark.
```

person_02:
```
A 34-year-old American woman with a chic shoulder-length auburn bob, green eyes, wearing teal medical scrubs with a stethoscope, warm confident smile. Photorealistic commercial headshot, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, direct eye contact, clean softly blurred bright background, 85mm, chest-up framing, 16:9, no text, no watermark.
```

person_03:
```
A 30-year-old American woman with long wavy blonde hair, blue eyes, wearing a cream cable-knit sweater, gentle warm smile. Photorealistic commercial headshot, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, direct eye contact, clean softly blurred bright background, 85mm, chest-up framing, 16:9, no text, no watermark.
```

person_04:
```
A 37-year-old American woman with shoulder-length black hair, dark eyes, wearing a navy blazer, confident composed expression. Photorealistic commercial headshot, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, direct eye contact, clean softly blurred bright background, 85mm, chest-up framing, 16:9, no text, no watermark.
```

person_05:
```
A 26-year-old American woman with curly reddish-brown hair, hazel eyes, wearing a mustard yellow top, bright energetic smile. Photorealistic commercial headshot, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, direct eye contact, clean softly blurred bright background, 85mm, chest-up framing, 16:9, no text, no watermark.
```

person_06:
```
A 41-year-old American woman with short stylish gray-blonde hair, blue-gray eyes, wearing a white blouse and pearl necklace, poised warm smile. Photorealistic commercial headshot, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, direct eye contact, clean softly blurred bright background, 85mm, chest-up framing, 16:9, no text, no watermark.
```

person_07:
```
A 32-year-old American woman with long dark hair with subtle highlights, brown eyes, wearing a rose pink cardigan, warm relatable smile. Photorealistic commercial headshot, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, direct eye contact, clean softly blurred bright background, 85mm, chest-up framing, 16:9, no text, no watermark.
```

person_08:
```
A 29-year-old American woman with a sleek dark brown ponytail, green eyes, wearing a charcoal blazer over a white top, confident professional smile. Photorealistic commercial headshot, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, direct eye contact, clean softly blurred bright background, 85mm, chest-up framing, 16:9, no text, no watermark.
```

person_09:
```
A 35-year-old American woman with long wavy chestnut hair, hazel eyes, wearing a soft lavender sweater, warm nurturing smile. Photorealistic commercial headshot, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, direct eye contact, clean softly blurred bright background, 85mm, chest-up framing, 16:9, no text, no watermark.
```

person_10:
```
A 27-year-old American woman with short curly dark hair, brown eyes, wearing a denim jacket over a striped top, bright cheerful smile. Photorealistic commercial headshot, bright warm high-key studio lighting, vivid saturated color grading, radiant glowing skin, direct eye contact, clean softly blurred bright background, 85mm, chest-up framing, 16:9, no text, no watermark.
```

## Setelah generate
Simpan sebagai `person_01.jpg` ... `person_10.jpg` -> taruh di
`~/Documents/revenge-pipeline/assets/character/` (HAPUS dulu file `char_*.jpg` lama
supaya tidak ikut ke-rotasi campur).

Mau nambah lebih banyak wanita kapan pun: generate lagi dengan pola sama, kasih nama
`person_11.jpg` dst, drop ke folder yang sama, otomatis ikut rotasi.

## Catatan teknis
- Pipeline otomatis pilih SATU foto per cerita (rotasi berdasar nomor cerita), dipakai
  konsisten untuk thumbnail DAN overlay video cerita itu. Video ke-11 balik lagi ke
  person_01, dst (nambah foto baru kapan pun memperpanjang jarak sebelum berulang).
- FULL Calm-Drama-style untuk SEMUA video (keputusan 2026-07-04): tidak ada lagi rotasi
  A/B dengan kartu Reddit. Kartu Reddit cuma jadi fallback darurat kalau folder
  character/ kosong, bukan gaya yang sengaja dipakai.
- Overlay video: karakter di-crop otomatis jadi ukuran lebih kecil (640x820), diposisikan
  nempel bawah kiri dengan ruang kosong di atas kepala (bukan menutupi seluruh frame).
- Foto akan otomatis dinaikkan brightness/contrast/saturation sedikit di kode (jaga-jaga),
  tapi prompt di atas sudah dirancang supaya foto asli sudah terang dari sono-nya.
