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
| 01 | [Setup Skeleton & Repository](./day-01-setup-skeleton.md) | ✅ Selesai |
| 02 | [Pilih Gate & Tulis Pipeline](./day-02-pipeline-4-gates.md) | ✅ Selesai |
| 03 | [Validasi Gate (Fail by Design)](./day-03-validate-gates.md) | ✅ Selesai |
| 04 | [Unit Test & Coverage Gate](./day-04-unit-tests.md) | ✅ Selesai |
| 05 | [Containerize App & Trivy Image Scan](./day-05-docker-trivy-image.md) | ✅ Selesai |
| 06 | [Setup Kind Cluster & Deploy Manual](./day-06-kind-deploy.md) | ✅ Selesai |
| 07 | [Push Image ke GHCR & Update Manifest](./day-07-ghcr-push.md) | ✅ Selesai |
| 08 | [Otomasi Build+Push via CI/CD](./day-08-cicd-automation.md) | ✅ Selesai |
| 09 | Review & Dokumentasi (penutup Fase 2) | 🔄 Berjalan |
| 10+ | Integrasi LangGraph (agentic AI) | 🔜 Belum mulai |

## Stack
- Python (FastAPI)
- Docker, `kind` (Kubernetes lokal)
- GitHub Actions, GHCR
- Bandit, pip-audit, Trivy (filesystem + image), Gitleaks
- Cline (VS Code + WSL) + Gemini API free tier, Ollama sebagai fallback lokal

## Isu terbuka
- Penyebab pasti error `write_package` di Hari 8 belum 100%
  terkonfirmasi (lihat catatan di day-08). Pantau kalau muncul lagi.
- `.trivyignore` untuk CVE-2026-14456 (openssl) perlu direview ulang
  tiap kali base image di-rebuild — hapus begitu patch upstream tersedia.
