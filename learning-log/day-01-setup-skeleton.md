# Hari 1 — Setup Skeleton & Repository

## Tujuan
Membuat repo baru (terpisah dari project `devsecops-homelab` yang sudah ada),
dengan skeleton FastAPI minimal, terhubung ke GitHub.

## Kenapa proyek baru, bukan lanjut yang lama?
Sengaja dipisah dari `devsecops-homelab` (Spring Boot, 7-gate pipeline)
supaya belajar variasi stack (Python/FastAPI) dan mulai eksplorasi
agentic AI (LangGraph) tanpa mengganggu proyek yang sudah stabil.

## Yang dikerjakan
1. Diskusi penamaan — dipilih `secure-fastapi-agent`, alasannya deskriptif:
   - `secure` → menandakan fokus DevSecOps
   - `fastapi` → stack yang dipakai
   - `agent` → pembeda utama dari proyek lama, karena nanti fokus ke LangGraph
2. `git init` di WSL Ubuntu (`~/secure-fastapi-agent`)
3. Skeleton `app/main.py` — sengaja minimal, cuma 1 endpoint `/health`.
   Fokus latihan ada di pipeline & agent, bukan di kompleksitas aplikasinya.
4. `requirements.txt` dasar: `fastapi`, `uvicorn[standard]`
5. Buat repo GitHub: `github.com/hendraazka/secure-fastapi-agent`
6. `git remote add origin ...`, push pertama

## Kendala & fix
- **Error:** `git commit "pesan"` → `error: pathspec 'pesan' did not match any file(s)`
  **Penyebab:** lupa flag `-m`, git mengira teks itu nama file, bukan pesan commit.
  **Fix:** `git commit -m "pesan"`

## Hasil akhir
Repo `secure-fastapi-agent` ada di GitHub, skeleton FastAPI jalan,
workflow (dari Hari 2) mulai ke-trigger otomatis tiap push.
