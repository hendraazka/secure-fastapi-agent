# Hari 13 — Test Graph dengan Beberapa Skenario Data

## Tujuan
Uji routing graph (flag_for_review vs auto_note) untuk beberapa
kondisi berbeda, tanpa perlu menimpa scan_results/ asli tiap kali.

## Alur
test_scenarios.py
│
├─ scenario "semua_low" ─┐
├─ scenario "ada_critical" ├─> build_graph().invoke() dengan
├─ scenario "campuran" │ raw_findings diisi manual
└─ scenario "kosong" ─┘
│
▼
read_findings: skip baca file KALAU raw_findings != None
(None = belum diisi, baca file asli;
[] = sengaja kosong, jangan baca file)
│
▼
classify_severity -> routing -> summarize
│
▼
Assertion: severity yang terdeteksi dibandingkan ekspektasi


## Yang dikerjakan
- read_findings dibuat "testable": skip baca file kalau raw_findings
  sudah diisi manual di state awal
- 4 skenario diuji: semua LOW, ada CRITICAL, campuran (ada HIGH),
  dan kosong (0 temuan)
- Assertion eksplisit membandingkan severity hasil vs ekspektasi,
  bukan cuma "jalan tanpa error"

## Kendala & fix
- BUG SIGNIFIKAN ditemukan lewat testing ini: kondisi awal
  `if state.get("raw_findings"):` salah -- list kosong ([]) itu
  falsy di Python, sama seperti None. Skenario "kosong" akhirnya
  malah membaca file scan_results/ asli (32 temuan), bukan benar-
  benar kosong. Test tetap [PASS] karena severity kebetulan sama
  ("low"), padahal alasannya salah total -- bug tersembunyi di
  balik hasil yang kelihatan benar.
- Fix: ganti ke `is not None` untuk membedakan "belum diisi" dari
  "sengaja kosong". __main__ block (run normal) diubah kirim None,
  bukan [], sebagai initial state.

## Kesimpulan
Ini pembuktian nyata kenapa test dengan assertion eksplisit penting --
tanpa skenario edge case "kosong", bug ini akan tetap tersembunyi
selamanya karena run normal (data asli) tidak pernah mengalami
kondisi list kosong secara natural.
