# Hari 8 — Otomasi Build+Push Image via CI/CD

## Tujuan
Job baru di GitHub Actions: build image + push ke GHCR otomatis,
tapi HANYA jika security-scan dan unit-tests lolos duluan.

## Desain kunci
- `needs: [security-scan, unit-tests]` — image tidak pernah ter-push
  kalau ada gate yang gagal
- `if: github.ref == 'refs/heads/main' && github.event_name == 'push'`
  — cegah job jalan di PR (termasuk dari fork), yang bisa dipicu
  siapa saja di repo publik
- Pakai `secrets.GITHUB_TOKEN` (otomatis, sekali pakai per run),
  BUKAN PAT manual seperti push Hari 7 — lebih aman, tidak perlu
  disimpan/diurus manual
- `permissions: packages: write` wajib dideklarasikan eksplisit
  di level job, defaultnya read-only
- 2 tag: `latest` (kemudahan) + `${{ github.sha }}` (traceability —
  tahu persis image mana berasal dari commit mana)

## Kendala & fix
- Run pertama: build sukses total (semua layer ke-push), tapi
  ditolak di step terakhir -- `denied: permission_denied: write_package`.
  Build image dan izin push ke registry adalah 2 hal terpisah,
  bisa gagal di titik berbeda.
- Dugaan penyebab: package sudah ada dari push manual Hari 7 (dibuat
  via PAT, terikat ke user), belum tentu otomatis ter-link akses
  Actions dari repo. Disarankan fix via "Manage Actions access" di
  package settings.
- Setelah re-run all jobs, berhasil. PENYEBAB PASTI belum terkonfirmasi
  -- apakah karena akses sempat diubah, atau run kedua otomatis
  berhasil link package. Perlu diperhatikan lagi kalau muncul error
  serupa di push berikutnya untuk memastikan pola sebenarnya.

## Hasil akhir
2 image version di GHCR: latest + tag SHA, ter-publish otomatis dari
CI setelah semua gate lolos.
