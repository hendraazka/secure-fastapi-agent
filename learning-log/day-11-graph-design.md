# Hari 11 — Desain Graph Pertama

## Tujuan
Bangun graph LangGraph: read_findings -> classify_severity ->
[conditional] -> summarize, terhubung ke data scan asli.

## Yang dikerjakan
- read_findings dihubungkan ke scan_parsers.combine_all() (reuse
  parser yang sudah divalidasi sejak Hari 2-5), bukan baca ulang
  combined.json secara independen
- Diuji dengan data asli dari artifact GitHub Actions (32 temuan,
  13 MEDIUM + 19 LOW, semua dari trivy-image)

## Kendala & fix
- Percobaan pertama: Gemini diminta meringkas SEKALIGUS menghitung
  breakdown severity dari data mentah -> hasilnya HALUSINASI angka
  (klaim 13 temuan padahal aslinya 32, verifikasi manual pakai
  Python Counter membuktikan ini). Pelajaran penting: LLM tidak
  boleh dipercaya untuk perhitungan presisi dari data terstruktur.
- Fix: pisahkan tanggung jawab -- hitung statistik pakai kode
  (Counter), kirim ke LLM sebagai fakta yang tidak boleh diubah,
  LLM cuma bertugas menulis narasi. Statistik akurat tetap
  ditampilkan eksplisit di luar hasil LLM sebagai jaring pengaman.
- Sempat salah jalankan file lama setelah update -- perlu verifikasi
  eksplisit (grep marker text) sebelum re-run, bukan asumsi file
  sudah ter-update otomatis.

## Kesimpulan
Graph berjalan, statistik akurat karena dihitung di kode bukan LLM.
Node conditional (flag_for_review vs auto_note) sudah ada di desain
sejak awal file ini dibuat -- Hari 12 (rencana semula: tambah
conditional edge) sudah terpenuhi, bisa lanjut langsung ke Hari 13.
