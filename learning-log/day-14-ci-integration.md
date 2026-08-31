# Hari 14 — Sambungkan Graph ke Pipeline CI

## Tujuan
Job baru `ai-triage`, jalan otomatis setelah security-scan, non-blocking
(continue-on-error), hasil ditulis ke file untuk (nanti) jadi komentar PR.

## Alur
```
security-scan (5 gate + upload artifact "scan-results")
│
▼
ai-triage (needs: security-scan, if: always())

download artifact "scan-results" -> scan_results/
jalankan security_triage_graph.py
GOOGLE_API_KEY dari GitHub Secrets (bukan .env, CI gak akses itu)
tulis triage_output.md
upload artifact "ai-triage-output"
(continue-on-error: true -- gagal di sini TIDAK menggagalkan pipeline)

build-and-push tetap needs: [security-scan, unit-tests] SAJA
-- ai-triage sengaja TIDAK termasuk, supaya lambat/gagalnya AI
triage tidak menghambat image ter-push
```


## Desain kunci
- `if: always()` -- wajib, tanpa ini job skip kalau security-scan gagal,
  padahal justru saat ada temuan HIGH/CRITICAL itu momen paling
  penting buat di-summary
- `continue-on-error: true` -- non-blocking sesuai rencana awal
- Hasil ditulis ke triage_output.md (bukan cuma print), supaya bisa
  diambil step berikutnya (posting PR comment, rencana lanjutan)

## Hasil akhir
4 job jalan: security-scan (52s), unit-tests (15s), ai-triage (2m9s -
paling lama karena panggilan LLM), build-and-push (42s). Semua hijau.

