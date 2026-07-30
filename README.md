# secure-fastapi-agent

Proyek belajar DevSecOps + Agentic AI — pipeline security ringan di
sekitar aplikasi FastAPI, dengan rencana integrasi agent (LangGraph)
untuk triase temuan security secara otomatis.

Proyek ini terpisah dari [devsecops-homelab](https://github.com/hendraazka/devsecops-homelab)
(Spring Boot, 7-gate pipeline) — sengaja dibuat dengan stack berbeda
(Python/FastAPI) untuk memperluas pemahaman DevSecOps di ekosistem lain,
sekaligus jadi tempat eksplorasi agentic AI.

## Status
🚧 Dalam pengembangan aktif. Lihat progres detail di [`learning-log/`](./learning-log/README.md).

## Arsitektur Pipeline

4 gate security berjalan otomatis via GitHub Actions setiap push/PR ke `main`:

| Gate | Tool | Jenis | Output |
|---|---|---|---|
| 1 | [Bandit](https://github.com/PyCQA/bandit) | SAST — analisis statis kode Python | `scan_results/bandit.json` |
| 2 | [pip-audit](https://github.com/pypa/pip-audit) | SCA — kerentanan dependency Python | `scan_results/pip-audit.json` |
| 3 | [Trivy](https://github.com/aquasecurity/trivy) | Filesystem & dependency scan | `scan_results/trivy.json` |
| 4 | [Gitleaks](https://github.com/gitleaks/gitleaks) | Secret scanning | `scan_results/gitleaks.json` |

Hasil ke-4 gate digabungkan (`scan_parsers.py`) jadi satu format, lalu
dievaluasi terpusat — pipeline gagal kalau ada temuan `HIGH`/`CRITICAL`.

```
scan_results/
├── bandit.json
├── pip-audit.json
├── trivy.json
├── gitleaks.json
└── combined.json      <- hasil normalisasi, dipakai step evaluasi & (nanti) agent
```

## Menjalankan Secara Lokal

```bash
# clone & masuk
git clone https://github.com/hendraazka/secure-fastapi-agent.git
cd secure-fastapi-agent

# setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# jalankan app
uvicorn app.main:app --reload
# cek di http://localhost:8000/health
```

### Uji pipeline sebelum push (opsional, butuh Docker)
```bash
act push -j security-scan
```

## Rencana Selanjutnya
- [ ] Perkuat pipeline: unit test, coverage gate, artifact report
- [ ] Integrasi agent berbasis **LangGraph** untuk triase otomatis hasil scan
      (baca `combined.json` → klasifikasi severity → ringkasan komentar PR)
- [ ] Model: Gemini 2.5 Flash (free tier) sebagai default, Ollama lokal sebagai fallback

## Catatan Belajar
Proses, kendala, dan cara memperbaikinya didokumentasikan per tahap di
[`learning-log/`](./learning-log/README.md) — termasuk kesalahan yang
terjadi di sepanjang jalan, bukan cuma hasil akhirnya.

