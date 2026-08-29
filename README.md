# secure-fastapi-agent

Proyek belajar DevSecOps + Agentic AI — pipeline security di sekitar
aplikasi FastAPI, dari kode sampai deploy ke Kubernetes, dengan rencana
integrasi agent (LangGraph) untuk triase temuan security secara otomatis.

Proyek ini terpisah dari [devsecops-homelab](https://github.com/hendraazka/devsecops-homelab)
(Spring Boot, 7-gate pipeline) — sengaja dibuat dengan stack berbeda
(Python/FastAPI) untuk memperluas pemahaman DevSecOps di ekosistem lain,
sekaligus jadi tempat eksplorasi agentic AI.

## Status
🚧 Dalam pengembangan aktif — Fase 2 (testing, container, Kubernetes)
selesai. Lihat progres detail per tahap di [`learning-log/`](./learning-log/README.md).

## Arsitektur Pipeline

5 gate security + 1 gate testing berjalan otomatis via GitHub Actions
setiap push/PR ke `main`:

| Gate | Tool | Jenis | Output |
|---|---|---|---|
| 1 | [Bandit](https://github.com/PyCQA/bandit) | SAST — analisis statis kode Python | `scan_results/bandit.json` |
| 2 | [pip-audit](https://github.com/pypa/pip-audit) | SCA — kerentanan dependency Python | `scan_results/pip-audit.json` |
| 3 | [Trivy](https://github.com/aquasecurity/trivy) | Filesystem & dependency scan | `scan_results/trivy.json` |
| 4 | [Gitleaks](https://github.com/gitleaks/gitleaks) | Secret scanning | `scan_results/gitleaks.json` |
| 5 | [Trivy (image)](https://github.com/aquasecurity/trivy) | Kerentanan di base image Docker | `scan_results/trivy-image.json` |
| — | pytest + coverage | Kebenaran fungsional (job terpisah, independen) | — |

Hasil ke-5 gate security digabungkan (`scan_parsers.py`) jadi satu
format, lalu dievaluasi terpusat — pipeline gagal kalau ada temuan
`HIGH`/`CRITICAL` yang belum ada di `.trivyignore`.

```
scan_results/
├── bandit.json
├── pip-audit.json
├── trivy.json
├── trivy-image.json
├── gitleaks.json
└── combined.json      <- hasil normalisasi, dipakai step evaluasi & (nanti) agent
```

## Arsitektur Deploy

```
Kode (push ke main)
      │
      ▼
┌─────────────────────────────────────┐
│  GitHub Actions                       │
│  1. security-scan (5 gate)  ──┐       │
│  2. unit-tests            ──┤       │
│                              ▼       │
│  3. build-and-push (needs: 1 & 2)     │
│     - build image                     │
│     - push ke GHCR (2 tag: latest,    │
│       SHA commit)                     │
└─────────────────────────────────────┘
      │
      ▼
GHCR: ghcr.io/hendraazka/secure-fastapi-agent
      │
      ▼ (manual, belum otomatis)
kind cluster lokal (WSL)
  - imagePullPolicy: Always
  - deployment.yaml + service.yaml
```

**Catatan penting:** deploy ke `kind` masih **manual** (`kubectl apply`),
bukan otomatis dari CI — cluster ini jalan di laptop lokal (WSL), GitHub
Actions (cloud) tidak punya akses ke situ. Auto-deploy baru masuk akal
kalau cluster-nya juga selalu-online di cloud.

## Menjalankan Secara Lokal

### Jalankan app langsung (tanpa container)
```bash
git clone https://github.com/hendraazka/secure-fastapi-agent.git
cd secure-fastapi-agent

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # kalau mau jalankan test juga

uvicorn app.main:app --reload
# cek di http://localhost:8000/health
```

### Jalankan test + coverage
```bash
pytest --cov=app --cov-report=term-missing
```

### Build & jalankan via Docker
```bash
docker build -t secure-fastapi-agent:local .
docker run -d -p 8000:8000 secure-fastapi-agent:local
```

### Deploy ke Kubernetes lokal (kind)
```bash
kind create cluster --name secure-fastapi-agent
kind load docker-image secure-fastapi-agent:local --name secure-fastapi-agent

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

kubectl port-forward svc/secure-fastapi-agent 8000:8000
```

### Uji pipeline sebelum push (opsional, butuh Docker)
```bash
act push -j security-scan
```

## Risk Acceptance
Beberapa temuan security diterima sementara dengan alasan
terdokumentasi di `.trivyignore` — lihat isi file tersebut untuk
detail dan kapan harus ditinjau ulang.

## Rencana Selanjutnya
- [x] Perkuat pipeline: unit test, coverage gate, artifact report
- [x] Containerize (Dockerfile, Trivy image scan)
- [x] Deploy ke Kubernetes lokal (kind)
- [x] Push image ke GHCR
- [x] Otomasi build+push via CI/CD
- [ ] Integrasi agent berbasis **LangGraph** untuk triase otomatis hasil scan
      (baca `combined.json` → klasifikasi severity → ringkasan komentar PR)
- [ ] Model: Gemini 2.5 Flash (free tier) sebagai default, Ollama lokal sebagai fallback

## Catatan Belajar
Proses, kendala, dan cara memperbaikinya didokumentasikan per tahap di
[`learning-log/`](./learning-log/README.md) — termasuk kesalahan yang
terjadi di sepanjang jalan (dan ada cukup banyak, terutama di Fase 2),
bukan cuma hasil akhirnya.