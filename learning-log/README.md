# Learning Log — secure-fastapi-agent

Catatan proses belajar DevSecOps + agentic AI, proyek terpisah dari
[devsecops-homelab](https://github.com/hendraazka/devsecops-homelab).

Bukan log per hari kalender secara ketat — tiap file merepresentasikan
1 tahap/unit belajar dari roadmap, meskipun waktu pengerjaannya bisa
lebih dari 1 hari kalender atau sebaliknya beberapa tahap selesai
dalam 1 sesi.

## Daftar isi

| # | Judul | Status |
|---|---|---|
| 01 | [Setup Skeleton & Repository](./day-01-setup-skeleton.md) | ✅ |
| 02 | [Pilih Gate & Tulis Pipeline](./day-02-pipeline-4-gates.md) | ✅ |
| 03 | [Validasi Gate (Fail by Design)](./day-03-validate-gates.md) | ✅ |
| 04 | [Unit Test & Coverage Gate](./day-04-unit-tests.md) | ✅ |
| 05 | [Containerize App & Trivy Image Scan](./day-05-docker-trivy-image.md) | ✅ |
| 06 | [Setup Kind Cluster & Deploy Manual](./day-06-kind-deploy.md) | ✅ |
| 07 | [Push Image ke GHCR & Update Manifest](./day-07-ghcr-push.md) | ✅ |
| 08 | [Otomasi Build+Push via CI/CD](./day-08-cicd-automation.md) | ✅ |
| 09 | Review & Dokumentasi (penutup Fase 2) | ✅ |
| 10 | [Setup LangGraph & Koneksi Gemini](./day-10-langgraph-setup.md) | ✅ |
| 11 | [Desain Graph Pertama](./day-11-graph-design.md) | ✅ |
| 12 | [Conditional Edge (digabung ke Hari 11)](./day-12-conditional-edge.md) | ✅ |
| 13 | [Test Graph dengan Beberapa Skenario Data](./day-13-test-scenarios.md) | ✅ |
| 14 | [Sambungkan Graph ke Pipeline CI](./day-14-ci-integration.md) | ✅ |
| 15 | [Rate Limit Handling](./day-15-rate-limit.md) | ✅ |
| 16 | [Fallback ke Ollama](./day-16-ollama-fallback.md) | ✅ |
| 17 | Dokumentasi Arsitektur Lengkap | ✅ |
| 18 | [Review Total & Portofolio](./day-18-final-review.md) | ✅ |

## Stack
- Python (FastAPI)
- Docker, `kind` (Kubernetes lokal)
- GitHub Actions, GHCR
- Bandit, pip-audit, Trivy (filesystem + image), Gitleaks
- LangGraph, Gemini 3.6 Flash (free tier), Ollama (llama3.1:8b, fallback)
- Cline (VS Code + WSL) untuk pengembangan interaktif

## Bug signifikan yang ditemukan (highlight)
- **Hari 11**: LLM diminta menghitung breakdown severity sendiri dari
  data mentah -> hasilnya halusinasi (32 temuan asli dilaporkan jadi
  13). Fix: statistik dihitung Python, LLM cuma menulis narasi.
- **Hari 13**: `if state.get("raw_findings"):` salah membedakan
  "belum diisi" dari "sengaja kosong" (list kosong itu falsy di
  Python). Fix: pakai `is not None`.
- **Hari 16**: exception handler menangkap class yang salah
  (`ClientError` bukan `GoogleGenerativeAIError`), retry/fallback
  tidak pernah ter-trigger, script crash total. Fix: tangkap base
  class yang benar setelah verifikasi ke dokumentasi library.

## Isu terbuka
- `.trivyignore` untuk CVE-2026-14456 (openssl) perlu direview ulang
  tiap kali base image di-rebuild — hapus begitu patch upstream tersedia.
- True-parallel job structure sengaja ditunda (bukan lupa) — lihat
  keputusan di percakapan sekitar Hari 4, mau dipraktikkan di
  konteks kerja nyata, bukan di proyek belajar ini.
- Posting hasil triage sebagai komentar PR asli (bukan cuma artifact)
  belum diputuskan apakah akan dikerjakan.