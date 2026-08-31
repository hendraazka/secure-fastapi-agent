# Hari 11 — Desain Graph Pertama

## Tujuan
Bangun graph LangGraph: read_findings -> classify_severity ->
[conditional] -> summarize, terhubung ke data scan asli.

## Alur

```
                    ┌─────────────────────────────────--┐
                    │  Tools scan (Bandit, Trivy, dst)  │
                    │  ditulis oleh: security-scan job  │
                    └──────────────┬────────────────────┘
                                   │
                                   ▼
                    scan_results/*.json (5 file mentah,
                    format beda-beda per tool)
                                   │
                    ┌──────────────┴──────────────-┐
                    │                              │
                    ▼                              ▼
         [JALUR 1: CI/pipeline]          [JALUR 2: Agent/graph]
         scan_parsers.py dijalankan       security_triage_graph.py
         sebagai SCRIPT (__main__)        memanggil combine_all()
                    │                     SEBAGAI FUNGSI (import)
                    ▼                              │
         Tulis scan_results/                       ▼
         combined.json (FILE)              Hasilnya langsung jadi
                    │                       state["raw_findings"]
                    ▼                       DI MEMORI, tanpa nulis
         Step "Evaluate gates" baca         file combined.json baru
         combined.json, gagalkan CI
         kalau ada HIGH/CRITICAL

Ringkas

scan_results/*.json (mentah, per tool)
        │
        ├──> [dipakai standalone oleh CI]  scan_parsers.py (as script) → combined.json → Evaluate gates
        │
        └──> [dipakai standalone oleh Agent]  security_triage_graph.py (import combine_all()) → state di memori → Gemini → summary

```

Dua jalur ini SAMA-SAMA memanggil `combine_all()` dari modul yang
sama (`scan_parsers.py`), tapi terpisah -- jalur agent tidak
bergantung pada `combined.json` yang ditulis jalur CI, bisa jalan
standalone selama file mentah per tool tersedia di `scan_results/`.

## Yang dikerjakan
- `read_findings` dihubungkan ke `scan_parsers.combine_all()` (reuse
  parser yang sudah divalidasi sejak Hari 2-5), bukan baca ulang
  `combined.json` secara independen
- Diuji dengan data asli dari artifact GitHub Actions (32 temuan,
  13 MEDIUM + 19 LOW, semua dari trivy-image; 4 tool lain nol
  temuan -- diverifikasi bukan artifact rusak, dicek lewat `wc -c`)

## Kendala & fix
- Percobaan pertama: Gemini diminta meringkas SEKALIGUS menghitung
  breakdown severity dari data mentah -> hasilnya HALUSINASI angka
  (klaim 13 temuan padahal aslinya 32, diverifikasi manual pakai
  Python `Counter`). Pelajaran penting: LLM tidak boleh dipercaya
  untuk perhitungan presisi dari data terstruktur.
- Fix: pisahkan tanggung jawab -- hitung statistik pakai kode
  (`Counter`), kirim ke LLM sebagai fakta yang tidak boleh diubah,
  LLM cuma bertugas menulis narasi. Statistik akurat tetap
  ditampilkan eksplisit di luar hasil LLM sebagai jaring pengaman.
- Sempat salah jalankan file lama setelah update -- perlu verifikasi
  eksplisit (`grep` marker text) sebelum re-run, bukan asumsi file
  sudah ter-update otomatis.

## Kesimpulan
Graph berjalan, statistik akurat karena dihitung di kode bukan LLM.
Node conditional (`flag_for_review` vs `auto_note`) sudah ada di
desain sejak file ini pertama dibuat -- rencana Hari 12 (tambah
conditional edge) sudah terpenuhi, lanjut langsung ke Hari 13.