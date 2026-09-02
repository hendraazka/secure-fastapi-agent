# Hari 18 — Review Total & Portofolio

## Tujuan
Audit akhir terhadap devsecops-startup-checklist.md, susun narasi
portofolio yang membandingkan proyek ini dengan devsecops-homelab.

## Audit checklist
Semua kategori utama terpenuhi: repo & VC, secrets management, SAST,
SCA, container scan, CI/CD design, policy/risk-acceptance, testing
lokal, dokumentasi. Satu item belum dicek eksplisit: branch protection
di `main` -- dicatat sebagai isu terbuka, bukan diasumsikan selesai.

## Perbandingan dengan devsecops-homelab
| | devsecops-homelab | secure-fastapi-agent |
|---|---|---|
| Stack | Spring Boot, Java | Python, FastAPI |
| Pipeline | 7-gate, Jenkins+Semaphore | 5-gate + agent, GitHub Actions |
| Orkestrasi | kind + OPA/Gatekeeper | kind (lebih sederhana) |
| Fitur unik | Admission control policy | Agentic AI triase (LangGraph) |
| Budget | (tidak dibatasi eksplisit) | $0 (Gemini free tier + Ollama) |

## Insight utama seluruh proyek (bukan cuma hari ini)
- Testing eksplisit dengan skenario edge case (Hari 13, 16) menemukan
  bug yang tersembunyi di balik hasil yang "kelihatan benar" --
  pelajaran paling berulang di proyek ini.
- LLM tidak bisa dipercaya untuk perhitungan presisi dari data
  terstruktur (Hari 11) -- pemisahan tanggung jawab (kode menghitung,
  LLM menulis narasi) jadi pola desain yang dipakai berulang.
- Debugging infrastruktur (DNS kind, GHCR permission Hari 7-8) lebih
  banyak makan waktu daripada menulis kode itu sendiri -- representatif
  dengan kerja DevSecOps sungguhan, bukan cuma proyek belajar yang mulus.

## Status akhir
Roadmap 18 hari selesai. Proyek siap dipakai sebagai bahan portofolio,
dengan learning-log sebagai bukti proses (bukan cuma hasil akhir).

