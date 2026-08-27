# Hari 7 — Push Image ke GHCR & Update Manifest

## Tujuan
Push image dari :local ke GHCR, update manifest supaya pull dari
registry, bukan image lokal yang di-load manual.

## Kendala & fix (proses debug terpanjang sejauh ini)
1. Push pertama gagal: "permission_denied: token tidak match scope"
   -> PAT lama tidak punya scope write:packages. Generate token baru
   dengan expiry 90 hari + scope write:packages.

2. Setelah update manifest ke image GHCR, pod ImagePullBackOff dengan
   error DNS: "lookup ghcr.io: no such host"
   -> Diselidiki lewat beberapa lapis: WSL bisa resolve ghcr.io normal
      (getent, curl berhasil), tapi containerd di dalam node kind gagal.
   -> Sempat coba restart node, cek resolv.conf -- semua terlihat normal.
   -> Test dengan crictl pull langsung ke containerd -> ternyata errornya
      BUKAN DNS, tapi 401 Unauthorized ("failed to fetch anonymous token").
      Pelajaran: pesan error dari kubelet/ImagePullBackOff bisa
      menyesatkan -- perlu test lebih dekat ke sumbernya (crictl,
      bukan cuma kubectl describe) untuk dapat pesan error yang akurat.

3. Ternyata akar masalahnya sederhana: package GHCR belum pernah
   ke-push berhasil sama sekali (baru sukses di percobaan push kedua
   setelah token diperbaiki) -- push pertama yang gagal itu tidak
   sempat dicek ulang, sempat dikira sudah beres.

4. Package default private -> diubah ke Public via package settings.

## Kesimpulan
Pod berhasil jalan dengan image dari GHCR. Pelajaran utama: saat
debug, jangan percaya asumsi dari langkah sebelumnya tanpa verifikasi
ulang (push yang "sepertinya berhasil" ternyata belum), dan test
paling dekat ke komponen yang benar-benar error (containerd via
crictl) lebih akurat daripada membaca lapisan di atasnya (kubectl
describe pod).
