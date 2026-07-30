# Hari 2 — Pilih Gate & Tulis Pipeline

## Tujuan
Menentukan 4 gate security untuk pipeline ringan (beda dari 7-gate di
`devsecops-homelab`, sengaja lebih sedikit tapi variasi tool baru),
lalu menulis workflow GitHub Actions-nya.

## Gate yang dipilih
| Gate | Tool | Jenis |
|---|---|---|
| 1 | Bandit | SAST — analisis statis kode Python |
| 2 | pip-audit | SCA — kerentanan dependency Python |
| 3 | Trivy | Filesystem/dependency scan |
| 4 | Gitleaks | Secret scanning |

## Komponen yang dibuat
- **`scan_parsers.py`** — normalizer untuk menyatukan 4 format output
  berbeda ke satu skema `{tool, severity, title, location}`.
  - Bandit & Trivy punya field severity native.
  - Gitleaks & pip-audit **tidak** punya severity sama sekali →
    keputusan desain manual: Gitleaks selalu `HIGH` (karena secret
    yang bocor selalu serius), pip-audit default `MEDIUM`.
- **`security-pipeline.yml`** — desain utama: tiap gate scan pakai
  `continue-on-error: true` / `exit-code: 0`, supaya ke-4 gate tetap
  sempat jalan semua meski salah satu ada temuan. Keputusan lulus/gagal
  pipeline dipusatkan di 1 step terakhir (`Evaluate gates`), bukan
  tersebar per gate.

## Kendala & fix (bagian paling berharga)

1. **`aquasecurity/trivy-action@0.28.0` tidak ditemukan**
   Penyebab: versi itu tidak eksis. Tag asli pakai prefix `v`
   (`v0.36.0`), sekaligus ketahuan proyek Trivy-action pernah
   mengalami supply chain attack, makanya format tag dimigrasikan.
   Fix: ganti ke `aquasecurity/trivy-action@v0.36.0`.

2. **`Unexpected input(s) 'config-path'`**
   Penyebab: `config-path` bukan input valid untuk `gitleaks-action@v2`.
   Fix: hapus baris `with: config-path: .gitleaks.toml`.

3. **`scan_parsers.py: No such file or directory`**
   Penyebab: file itu masih ada di lokal WSL saja, belum pernah
   `git add` + push ke GitHub. GitHub Actions jalan dari state repo
   di GitHub, bukan dari folder lokal.
   Fix: `git add scan_parsers.py`, commit, push.

4. **`AttributeError: 'str' object has no attribute 'get'`** di `parse_gitleaks`
   Penyebab: asumsi awal salah — dikira output Gitleaks itu list JSON
   datar, padahal aslinya format **SARIF** (dict dengan key `runs`).
   `for item in data` yang dijalankan di atas dict malah looping ke
   *keys*-nya (string), bukan ke isi temuan.
   Fix: refactor `parse_gitleaks` untuk membaca struktur SARIF yang
   benar (`data["runs"][x]["results"]`), sekaligus tetap aman kalau
   filenya kosong (`[]`, tidak ada leak).

## Hasil akhir
Pipeline berhasil jalan tanpa crash — tapi di titik ini masih hijau
karena **belum ada temuan nyata**, bukan karena terbukti bekerja.
Ini jadi fokus validasi di Hari 3.
