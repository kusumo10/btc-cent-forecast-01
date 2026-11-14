# btc-cent-forecast-01 — CATATAN BUILD (koordinator, 15 Nov 2026)

## Entry akhir
- Metode: regresi OLS walk-forward (di dalam case sendiri) — return log 240 menit
  ke depan ~ return log 24 jam terakhir + intercept; prediksi di-shrink 0,6
  ke persistence dan di-clip ±60bp; harga = close checkpoint × exp(prediksi).
- File repo: `main.py` (3.795 byte), `LICENSE` (MIT + SPDX), `README.md`,
  `.makefun/owner.json`, `.gitignore`. Belum di-commit ke GitHub — JANGAN submit
  tanpa perintah Alvin (kuota HANYA 1: max_per_day 1, max_total 1).

## Data & jawaban practice (ditemukan sendiri)
- 6 case p00–p05, 4.320 close/menit (72 jam) per case, checkpoint 4 jam apart
  dari 2026-11-10T06:00Z. Jawaban = close 240 menit setelah checkpoint.
- Jawaban p00–p04 didapat dari OVERLAP: close terakhir case p0(i+1) = jawaban
  p0i. p00 −317,11 | p01 −766,97 | p02 −470,33 | p03 +566,85 | p04 −231,47 ($).
- Jawaban p05 TIDAK ada di input mana pun; tapi dari skor baseline resmi
  (44.521,576667 sen × 6 case − jumlah error p00–p04) → error persistence p05
  = 31.856,2 sen, jadi jawaban p05 = 73.545,88 ± 318,56 (73.227,32 atau 73.864,44).
- Return 240 menit: stdev 64bp, mean |ret| 46bp, median 28bp. Korelasi dengan
  return 24 jam sebelumnya: −0,594 (!), dengan return 240 menit sebelumnya:
  −0,324 — rezim ini SANGAT mean-reverting pada horizon 4 jam.

## Validasi lokal (MAE sen; baseline persistence: mid 42.545, eow 44.955, prac5 47.055)
- Set validasi: mid = checkpoint tiap 30 mnt, t 2160–4079, 6 file (384 sampel);
  eow = 8 jam terakhir jendela, t 3600–4079 (96 sampel, paling mirip tugas final);
  prac5 = 5 jawaban practice yang diketahui.
- persistence: mid 42.545 | eow 44.955 | prac5 47.055
- trend OLS (H=60/240/720, damp=1): JAUH lebih buruk (70k–120k) — jangan kejar tren.
- mean-reversion MA1440 k=0,25: mid 39.948 | eow — | prac5 49.139 (menang mid, kalah prac5).
- ridge multi-fitur (OLS/LAD, lam 1–10): prac5 ~29k TAPI mid 52–67k — TIDAK robust, ditolak.
- uni r1440 OLS shrink 0,5: mid 37.765 | eow 32.787 | prac5 36.301
- uni r1440 OLS shrink 0,6 cap 60bp (DIPILIH): mid 36.606 | eow 31.940 | prac5 34.087
- uni r1440 OLS shrink 0,65 cap 60bp: mid 36.658 | eow 31.729 | prac5 33.010
- multi (r1440,r240,r720) OLS 0,6: mid 41.668 | eow 31.756 | prac5 30.118 — prac5/eow
  terbaik tapi mid jauh lebih buruk (overfit); ditolak demi robustness.
- Model dipilih menang vs persistence di 63,5% checkpoint mid dan 79,2% eow.

## Skor practice resmi (dihitung manual, BUKAN grade-local)
- `grade-local` MENOLAK untuk kompetisi ini: "scorer and reference data are not
  published in the kit, so it is graded on the server only" (kit.json:
  dataset_sha256 null; tidak ada practice/reference/). Skor practice resmi HANYA
  didapat lewat submit.
- Prediksi entry vs 5 jawaban diketahui: p00 2.431 | p01 48.469 | p02 49.341 |
  p03 42.732 | p04 27.465 sen → prac5 MAE 34.087,4 sen.
- p05: prediksi 73.654,68 → error 42.736 ATAU 20.976 sen → skor 6-case practice
  = 35.529 ATAU 31.902 sen (keduanya < baseline 44.521,58).
- Perbandingan papan practice (live, 1.375 entri): peringkat 100 = 32.600;
  50 = 28.800; 10 = 21.200; 2 (nyata) = 13.400; 1 = 0 (placeholder, semua error
  0 — abaikan). 1.093 entri mengalahkan baseline di practice. Jadi skor practice
  model ini ≈ peringkat 85–130 — TIDAK masuk 10 besar practice, tapi aman di
  bawah baseline.

## Validasi teknis
- Determinisme: 2 run → output identik byte-per-byte (diff kosong).
- Runtime: 0,05 detik untuk 6 case (~0,01 dtk/case; batas 8 dtk/case).
- Semua 6 case valid (format output sesuai starter; harga di-grid 5 desimal).

## Keputusan & risiko (untuk laporan ke Alvin)
- REKOMENDASI: SUBMIT. Alasan: mengalahkan baseline di SEMUA set validasi
  (mid −14%, eow −29%, prac5 −28%), menang di mayoritas checkpoint, metode
  sederhana + stabil, dan adaptif per-case (fit di jendela case sendiri —
  bila rezim final berbalik arah, slope ikut berbalik).
- Risiko jujur: practice BUKAN final. Final 12 checkpoint di 15–17 Nov (rezim
  belum terlihat). Metode ini bertaruh pada mean-reversion 24 jam → 4 jam;
  bila final jadi tren searah yang kuat dan persisten, model bisa kalah dari
  baseline. Tidak ada cara menguji itu sebelum final direkam. Hadiah butuh skor
  final DI BAWAH baseline final + semua case valid; peringkat 100 final
  kemungkinan butuh skor jauh di bawah baseline (di practice, 100 besar
  ≤32.600 vs baseline 44.522).
- Yang masih bisa ditingkatkan bila ada waktu: (a) uji varian multi-fitur
  dengan regularisasi lebih kuat (mid-nya yang bermasalah); (b) kalibrasi cap
  per volatilitas; (c) ensemble median dari 2–3 prediktor univariat. Semua
  perbedaan di kisaran noise (±2%); tidak ada yang mengubah rekomendasi.
