# Hari 5 — Containerize App & Trivy Image Scan

## Tujuan
Buat Dockerfile, build image, tambah Gate 5 (Trivy image scan)
untuk memindai kerentanan di base image, bukan cuma kode aplikasi.

## Yang dikerjakan
- Dockerfile single-stage (python:3.12-slim base)
- .dockerignore terpisah dari .gitignore (venv/, tests/, .git/ dst
  tidak perlu ikut ke dalam image production)
- Gate 5 ditambahkan: build image di CI, scan dengan Trivy
- scan_parsers.py diperluas: parse_trivy_image() + update combine_all()

## Kendala & fix
- Percobaan pertama: 19 temuan HIGH/CRITICAL, semuanya CVE di paket
  OS bawaan base image (openssl, sqlite, ncurses, perl, dst) —
  bukan di kode aplikasi sendiri.
- Tambah `ignore-unfixed: true` -> turun ke 3 temuan (CVE yang
  sudah ada patch tapi base image belum pakai versi terbaru).
- Coba `docker build --pull --no-cache` untuk pastikan bukan
  masalah cache lokal -> hasil sama, base image terbaru dari
  registry memang masih bawa CVE-2026-14456 (openssl QUIC DoS).
- Keputusan: risk-acceptance via `.trivyignore` dengan alasan
  tertulis (app tidak pakai fitur QUIC OpenSSL), bukan dipaksa
  hilang tanpa dasar. Trivy otomatis baca file ini dari root,
  tidak perlu konfigurasi tambahan di workflow.

## Kesimpulan
Gate 5 aktif dan bekerja dengan temuan asli (bukan simulasi seperti
Hari 3). Belajar konsep risk-acceptance yang terdokumentasi —
bukan semua temuan security bisa/harus langsung "dihilangkan",
kadang keputusannya menerima risiko sementara dengan alasan jelas.
