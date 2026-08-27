# Hari 6 — Setup Kind Cluster & Deploy Manual

## Tujuan
Deploy FastAPI app ke kind cluster baru (terpisah dari devsecops-homelab),
verifikasi jalan lewat port-forward.

## Yang dikerjakan
- kind create cluster --name secure-fastapi-agent (cluster terpisah,
  supaya tidak tercampur dengan cluster devsecops-homelab yang lama)
- kind load docker-image — image lokal di-load manual ke cluster,
  karena kind tidak otomatis bisa lihat image Docker lokal
- Manifest deployment.yaml (imagePullPolicy: Never — wajib supaya
  k8s tidak coba pull dari registry publik) + service.yaml
- Verifikasi via port-forward -> /health balas {"status":"ok"}

## Kesimpulan
Pod jalan, service bisa diakses. Image masih pakai tag :local
(belum dari registry) — jadi ini deploy manual, belum otomatis dari CI.
