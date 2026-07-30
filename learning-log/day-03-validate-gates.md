# Hari 3 — Validasi Gate (Fail by Design)

## Tujuan
Membuktikan pipeline 4-gate benar-benar mendeteksi temuan nyata,
bukan cuma hijau karena repo-nya masih kosong/belum ada apa-apa untuk
ditemukan.

## Kenapa ini penting
Pipeline yang selalu hijau itu ambigu: bisa berarti "aman", bisa juga
berarti "gate-nya rusak/gak pernah beneran mendeteksi apa-apa". Tanpa
pernah lihat pipeline gagal karena sebab yang benar, dua kemungkinan
itu gak bisa dibedakan.

## Yang dilakukan
1. Sengaja menambahkan 2 pemicu temuan:
   - Pattern shell injection (`subprocess.call(... shell=True)`) — untuk trigger Bandit
   - `requests==2.6.0` (versi lama, ada CVE) di `requirements.txt` — untuk trigger Trivy/pip-audit

## Kendala & fix

- **Kesalahan pertama:** kode shell injection ditaruh langsung di
  `scan_parsers.py` — file yang benar-benar **dieksekusi** saat
  workflow jalan (`python scan_parsers.py`). Karena variabel
  `user_input` tidak pernah didefinisikan, Python crash duluan
  (`NameError`) sebelum sempat sampai ke gate manapun.

  **Pelajaran kunci:** Bandit itu *static analysis* — dia membaca pola
  kode tanpa menjalankannya. Kode uji coba harus ditaruh di file yang
  **dibaca** (`app/main.py`), di dalam function yang tidak pernah
  dipanggil saat runtime — bukan di file yang dieksekusi pipeline.

  **Fix:** pindahkan ke `app/main.py`, bungkus dalam function terpisah:
  ```python
  def debug_list_files(user_input: str):
      import subprocess
      subprocess.call("ls " + user_input, shell=True)  # sengaja: uji Bandit
  ```

## Hasil
`Evaluate gates` berhasil gagal dengan pesan jelas:
```
2 temuan HIGH/CRITICAL ditemukan:
  [bandit] subprocess call with shell=True identified, security issue. (./app/main.py:12)
  [trivy] CVE-2018-18074: python-requests: Redirect from HTTPS to HTTP does not remove Authorization header (requirements.txt)
```
Dua gate berbeda (Bandit & Trivy) sama-sama mendeteksi masalah yang
sengaja ditaruh, dan step evaluasi terpusat berhasil menghentikan
pipeline karena itu.

## Cleanup setelah validasi
- Hapus function `debug_list_files` dari `app/main.py`
- Kembalikan `requests` ke versi aman terbaru di `requirements.txt`
- Commit: `chore: remove intentional test vulnerabilities after validating gates`

## Kesimpulan
Pipeline terbukti bisa gagal saat ada temuan HIGH/CRITICAL asli, bukan
cuma hijau karena kosong. Kode uji coba sudah dibersihkan sebelum
lanjut ke fase berikutnya.
