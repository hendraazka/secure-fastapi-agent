#!/bin/bash
# dev-up.sh — Startup script untuk secure-fastapi-agent
#
# PENTING: jalankan dengan SOURCE, bukan ./ atau bash biasa!
#   source dev-up.sh
#   . dev-up.sh          (alternatif lebih pendek, artinya sama)
#
# Kenapa harus source: bagian aktivasi venv butuh mengubah shell
# yang sedang kamu pakai. Kalau dijalankan sebagai ./dev-up.sh atau
# bash dev-up.sh, itu jalan di subprocess terpisah -- venv-nya aktif
# di subprocess itu doang, lalu hilang begitu script selesai. Ini
# bukan bug script, ini cara kerja shell di Linux/bash.

set -uo pipefail   # TIDAK pakai -e -- script ini harus lanjut cek
                    # semua service meski salah satu gagal, bukan
                    # berhenti di kegagalan pertama.

PROJECT_DIR="$HOME/secure-fastapi-agent"
CLUSTER_NAME="secure-fastapi-agent"

echo "======================================================"
echo " secure-fastapi-agent — Dev Environment Startup"
echo "======================================================"

# ---------------------------------------------------------------
# 0. Pastikan di direktori yang benar
# ---------------------------------------------------------------
if [ "$PWD" != "$PROJECT_DIR" ]; then
    echo "[i] Pindah ke $PROJECT_DIR"
    cd "$PROJECT_DIR" || { echo "[X] Direktori tidak ditemukan: $PROJECT_DIR"; return 1; }
fi

# ---------------------------------------------------------------
# 1. Docker Desktop
# ---------------------------------------------------------------
echo ""
echo "--- 1. Docker Desktop ---"
if docker info >/dev/null 2>&1; then
    echo "[OK] Docker sudah jalan."
else
    echo "[!] Docker belum jalan. Mencoba start dari WSL..."
    # Best-effort: coba start Docker Desktop di Windows dari WSL.
    # Ini TIDAK dijamin selalu berhasil (tergantung instalasi Docker
    # Desktop kamu) -- kalau gagal, buka manual dari Start Menu Windows.
    powershell.exe -Command "Start-Process 'Docker Desktop'" 2>/dev/null

    echo "    Menunggu Docker siap (maks 60 detik)..."
    for i in $(seq 1 30); do
        if docker info >/dev/null 2>&1; then
            echo "[OK] Docker sudah jalan."
            break
        fi
        sleep 2
    done

    if ! docker info >/dev/null 2>&1; then
        echo "[X] Docker belum siap juga setelah 60 detik."
        echo "    Buka Docker Desktop manual dari Windows, lalu jalankan ulang: source dev-up.sh"
    fi
fi

# ---------------------------------------------------------------
# 2. kind cluster
# ---------------------------------------------------------------
echo ""
echo "--- 2. Kind cluster ($CLUSTER_NAME) ---"
if docker info >/dev/null 2>&1; then
    if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
        if kubectl config current-context 2>/dev/null | grep -q "$CLUSTER_NAME"; then
            :
        else
            kubectl config use-context "kind-${CLUSTER_NAME}" >/dev/null 2>&1
        fi

        POD_STATUS=$(kubectl get pods --no-headers 2>/dev/null | awk '{print $3}' | head -1)
        if [ "$POD_STATUS" = "Running" ]; then
            echo "[OK] Cluster ada, pod status: Running."
        else
            echo "[!] Cluster ada tapi pod belum Running (status: ${POD_STATUS:-tidak ada pod}). Cek manual: kubectl get pods"
        fi
    else
        echo "[!] Cluster '$CLUSTER_NAME' tidak ditemukan."
        echo "    Buat baru dengan: kind create cluster --name $CLUSTER_NAME"
    fi
else
    echo "[X] Skip -- Docker belum siap."
fi

# ---------------------------------------------------------------
# 3. Ollama
# ---------------------------------------------------------------
echo ""
echo "--- 3. Ollama ---"
if pgrep -x "ollama" >/dev/null 2>&1; then
    echo "[OK] Ollama sudah jalan."
else
    echo "[!] Ollama belum jalan. Menjalankan di background..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    disown
    sleep 2
    if pgrep -x "ollama" >/dev/null 2>&1; then
        echo "[OK] Ollama berhasil di-start (log: /tmp/ollama.log)."
    else
        echo "[X] Ollama gagal di-start. Cek /tmp/ollama.log untuk detail."
    fi
fi

# ---------------------------------------------------------------
# 4. Virtual environment (INI SEBABNYA HARUS 'source', BUKAN './')
# ---------------------------------------------------------------
echo ""
echo "--- 4. Python venv ---"
if [ -f "venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
    echo "[OK] venv diaktifkan: $(which python)"
else
    echo "[X] venv tidak ditemukan di $PROJECT_DIR/venv"
fi

# ---------------------------------------------------------------
# 5. Cek env var yang nyasar dari sesi debug sebelumnya
# ---------------------------------------------------------------
echo ""
echo "--- 5. Environment variables ---"
if [ -n "${GOOGLE_API_KEY:-}" ]; then
    echo "[!] GOOGLE_API_KEY sudah ter-set di shell ini (kemungkinan sisa"
    echo "    sesi debug sebelumnya) -- ini akan OVERRIDE isi .env kamu."
    echo "    Kalau ini tidak disengaja, jalankan: unset GOOGLE_API_KEY"
else
    echo "[OK] GOOGLE_API_KEY tidak ter-set manual, .env akan dipakai otomatis."
fi

echo ""
echo "======================================================"
echo " Selesai. Siap kerja."
echo "======================================================"
