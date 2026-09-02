# secure-fastapi-agent

Proyek belajar DevSecOps + Agentic AI — pipeline security di sekitar
aplikasi FastAPI, dari kode sampai deploy ke Kubernetes, dengan agent
berbasis LangGraph yang mentriase temuan security secara otomatis.

Proyek ini terpisah dari [devsecops-homelab](https://github.com/hendraazka/devsecops-homelab)
(Spring Boot, 7-gate pipeline) — sengaja dibuat dengan stack berbeda
(Python/FastAPI) untuk memperluas pemahaman DevSecOps di ekosistem lain,
sekaligus jadi tempat eksplorasi agentic AI dengan budget $0.

## Status
✅ Fase 1-4 selesai (Hari 1-17). Lihat progres detail per tahap di
[`learning-log/`](./learning-log/README.md).

## Arsitektur Pipeline (Security Gates)

5 gate security + 1 gate testing berjalan otomatis via GitHub Actions
setiap push/PR ke `main`:

| Gate | Tool | Jenis |
|---|---|---|
| 1 | [Bandit](https://github.com/PyCQA/bandit) | SAST — analisis statis kode Python |
| 2 | [pip-audit](https://github.com/pypa/pip-audit) | SCA — kerentanan dependency Python |
| 3 | [Trivy](https://github.com/aquasecurity/trivy) | Filesystem & dependency scan |
| 4 | [Gitleaks](https://github.com/gitleaks/gitleaks) | Secret scanning |
| 5 | [Trivy (image)](https://github.com/aquasecurity/trivy) | Kerentanan di base image Docker |
| — | pytest + coverage | Kebenaran fungsional (job independen) |

Hasil ke-5 gate security digabungkan (`scan_parsers.py`) jadi satu
format, dievaluasi terpusat — pipeline gagal kalau ada temuan
`HIGH`/`CRITICAL` yang belum ada di `.trivyignore`.

## Arsitektur Deploy

```
Kode (push ke main)
      │
      ▼
┌───────────────────────────────────────────┐
│  GitHub Actions                             │
│  1. security-scan (5 gate)  ──┬──────────┐ │
│  2. unit-tests               ─┤          │ │
│                                ▼          ▼ │
│  3. build-and-push            4. ai-triage │
│     (needs: 1, 2)                (needs: 1)│
│     - build & push GHCR          (non-block│
│                                    if: always)│
└───────────────────────────────────────────┘
      │                              │
      ▼                              ▼
GHCR: ghcr.io/.../secure-      triage_output.md
fastapi-agent                  (artifact, komentar PR)
      │
      ▼ (manual)
kind cluster lokal (WSL)
```

`ai-triage` sengaja **tidak** termasuk `needs` milik `build-and-push`
— supaya lambat/gagalnya AI triage tidak menghambat image ter-push.

## Arsitektur Agent (LangGraph)

```
scan_results/*.json (mentah, per tool)
        │
        ├──> [JALUR CI] scan_parsers.py (as script) -> combined.json
        │                -> dibaca step "Evaluate gates"
        │
        └──> [JALUR AGENT] security_triage_graph.py
                            -> import combine_all() (fungsi yang sama)
                            -> state["raw_findings"] di memori
                            -> classify_severity
                            -> [conditional: high/low]
                                 |-> flag_for_review
                                 |-> auto_note
                            -> summarize:
                                 1. Statistik dihitung Python (Counter)
                                    -- BUKAN oleh LLM (LLM terbukti
                                    halusinasi angka saat diminta
                                    menghitung sendiri, lihat log Hari 11)
                                 2. invoke_with_fallback(prompt):
                                    - coba Gemini 3.6 Flash (retry 4x,
                                      exponential backoff, HANYA untuk
                                      GoogleGenerativeAIError)
                                    - retry habis -> fallback ke Ollama
                                      lokal (llama3.1:8b)
                                    - dua-duanya gagal -> statistik
                                      tetap tampil, narasi di-skip
                                 3. Provider yang benar-benar merespons
                                    ditandai eksplisit di output
                            -> Severity + Summary (triage_output.md)
```

### Keputusan desain penting
- **Statistik dihitung kode, bukan LLM.** Percobaan awal menyerahkan
  perhitungan ke Gemini menghasilkan angka yang salah total (32
  temuan asli dilaporkan jadi 13). LLM sekarang cuma menulis narasi
  dari angka yang sudah pasti benar.
- **Retry menangkap base exception class**, bukan class spesifik yang
  ditebak — percobaan awal menangkap `google.genai.errors.ClientError`
  ternyata tidak pernah ter-trigger karena `langchain_google_genai`
  membungkus ulang error jadi exception class miliknya sendiri
  (`GoogleGenerativeAIError` dan turunannya).
- **`read_findings` testable by design** — skip baca file kalau
  `raw_findings` sudah diisi manual (`is not None`, bukan truthy
  check biasa — list kosong `[]` itu falsy di Python, sempat jadi
  bug tersembunyi di Hari 13).
- **Fallback provider ditandai eksplisit** di output — transparansi
  penting: pembaca komentar PR harus tahu kalau ringkasan berasal
  dari model cadangan, bukan model utama.

## Menjalankan Secara Lokal

### Jalankan app langsung
```bash
git clone https://github.com/hendraazka/secure-fastapi-agent.git
cd secure-fastapi-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://localhost:8000/health
```

### Test + coverage
```bash
pip install -r requirements-dev.txt
pytest --cov=app --cov-report=term-missing
```

### Jalankan agent triage secara lokal
```bash
pip install -r requirements-agent.txt
cp .env.example .env   # isi GOOGLE_API_KEY kamu
python security_triage_graph.py
```

### Uji skenario agent (tanpa perlu data scan asli)
```bash
python test_scenarios.py
```

### Docker & Kubernetes
```bash
docker build -t secure-fastapi-agent:local .
kind create cluster --name secure-fastapi-agent
kind load docker-image secure-fastapi-agent:local --name secure-fastapi-agent
kubectl apply -f k8s/
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

## Roadmap
- [x] Pipeline 5-gate security + unit test/coverage
- [x] Containerize, deploy ke Kubernetes lokal (kind)
- [x] CI/CD otomatis (build+push GHCR, gated oleh security+test)
- [x] Agent LangGraph: triase otomatis, retry, fallback Ollama
- [x] Integrasi agent ke pipeline CI (non-blocking)
- [ ] (opsional, belum diputuskan) Posting hasil triage sebagai
      komentar PR asli, bukan cuma artifact
- [ ] (opsional, belum diputuskan) True-parallel job structure —
      disengaja ditunda, lihat catatan di `learning-log/day-*`

## Catatan Belajar
Proses, kendala, dan cara memperbaikinya didokumentasikan per tahap di
[`learning-log/`](./learning-log/README.md) — termasuk bug signifikan
yang ditemukan lewat testing eksplisit (halusinasi angka LLM Hari 11,
exception class salah tangkap Hari 16), bukan cuma hasil akhir yang
kelihatan mulus.
