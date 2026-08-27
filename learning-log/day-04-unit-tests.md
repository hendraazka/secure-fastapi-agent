# Hari 4 — Unit Test & Coverage Gate

## Tujuan
Menambahkan test fungsional pertama + coverage gate,
terpisah dari 4 gate security yang sudah ada.

## Yang dikerjakan
- Setup pytest + httpx + pytest-cov, dipisah ke requirements-dev.txt
- Test dasar untuk endpoint /health (status code + response body)
- Coverage 100% (wajar, app masih minimal — bukan pencapaian besar)
- Job baru `unit-tests` ditambahkan sejajar dengan `security-scan`,
  independen (tidak pakai `needs:`)

## Kendala & fix
- Lupa buat .gitignore dari awal — venv/, .pytest_cache/, .coverage
  berisiko ke-commit. Dibuat sebelum commit apa pun lagi.
- Salah tempel job unit-tests: nyasar masuk ke dalam `steps:` job
  security-scan (job nested di dalam steps, tidak valid YAML).
  Pelajaran: job baru harus sejajar dengan job lain di bawah `jobs:`,
  bukan di dalam step manapun.
- Ternyata masih ada sisa AWS key palsu (AKIAIOSFODNN7EXAMPLE) dari
  test Gitleaks di Hari 3 yang belum dihapus — lolos dari Gitleaks
  (dikenali sebagai contoh resmi AWS, ada di allowlist), tapi
  terdeteksi Bandit (severity LOW, karena pola "variabel *_KEY diisi
  string literal"). Pelajaran: 1 tool tidak mendeteksi bukan berarti
  aman dari semua tool — itu gunanya banyak lapis gate.

## Hasil akhir
2 job jalan independen: security-scan (4 gate) dan unit-tests,
keduanya lolos tanpa temuan HIGH/CRITICAL maupun test gagal.
