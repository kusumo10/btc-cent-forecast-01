# btc-cent-forecast-01 — Walk-forward OLS mean-reversion forecaster

Entry untuk bounty make.fun [btc-cent-forecast-01](https://make.fun/bounty/btc-cent-forecast-01)
(total $250; juara 1 $40; 100 tempat dibayar; tenggat 15 Nov 2026 15:00 WIB).

## Cara kerja

`main.py` (Python 3.13, stdlib saja) membaca satu case: 4.320 close 1-menit
BTC/USDC selama 72 jam sampai checkpoint, lalu menebak harga 240 menit
(4 jam) setelah checkpoint.

Metode — regresi OLS walk-forward yang di-fit di dalam case itu sendiri:

- Kerja di log harga. Return 240 menit ke depan diregresi (OLS, dengan
  intercept) terhadap return 24 jam terakhir, memakai semua checkpoint masa
  lalu di jendela case yang hasil 240-menitnya sudah teramati
  (s dari 1440 s.d. t−240, tiap 5 menit).
- Gerakan hasil fit di-shrink 0,6 ke arah persistence (tidak bergerak) dan
  di-clip ke ±60bp, lalu diterapkan ke close checkpoint.
- Return 24 jam sangat mean-reverting pada horizon 4 jam di rezim practice
  (korelasi −0,59 dengan return 240 menit ke depan), jadi model melawan
  arah gerakan hari terakhir; shrinkage + clip membatasi kasus terburuk.

Deterministik (aritmetika float murni, tanpa random), tanpa network.
Baca `$MAKEFUN_INPUT_DIR` (atau `/input`), tulis `$MAKEFUN_OUTPUT_DIR`
(atau `/output`): satu `<id>.out` per `<id>.in`.

## Verifikasi lokal

- Grade lokal (kit `grade-local`, driver process): lihat CATATAN.md
- Determinisme: 2 run → output identik byte-per-byte
- Runtime: <0,1 detik per case (batas 8 detik)
- Baseline persistence practice: 44.521,576667 sen; model ini jauh di bawahnya di semua set validasi lokal (lihat CATATAN.md)
