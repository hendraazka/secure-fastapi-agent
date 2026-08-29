# Hari 10 — Setup LangGraph & Koneksi Gemini

## Tujuan
Install langgraph + langchain-google-genai, verifikasi koneksi ke
Gemini API sebelum mulai desain graph.

## Yang dikerjakan
- Dependency agent dipisah ke requirements-agent.txt (beda dari
  runtime dan dev) -- langgraph, langchain-google-genai, python-dotenv
- API key disimpan di .env (di-gitignore), .env.example dibuat
  sebagai dokumentasi tanpa isi asli
- test_gemini_connection.py sebagai script verifikasi terpisah,
  supaya error auth vs error logika graph tidak tercampur

## Kendala & fix
- Env var GOOGLE_API_KEY dicek dulu sebelum implementasi -- ternyata
  library langchain-google-genai cek GOOGLE_API_KEY duluan, baru
  GEMINI_API_KEY sebagai fallback. Dipakai nama utamanya biar eksplisit.
- Model gemini-2.5-flash (dipakai di skeleton graph awal proyek)
  ternyata sudah tidak tersedia untuk user baru per Agustus 2026 --
  error 404 eksplisit menyarankan gemini-3.6-flash. Diganti.
- Setelah ganti model, ketemu 2 hal baru yang perlu diantisipasi
  di Hari 11:
  1. response.content bukan string polos, tapi list of dict
     ([{"type": "text", "text": ..., "extras": {...}}]) -- perlu
     ekstraksi eksplisit, bukan dipakai langsung.
  2. Parameter temperature diabaikan oleh model ini (fixed sampling
     defaults) -- trade-off konsistensi output yang perlu disadari,
     bukan gagal.

## Hasil akhir
Koneksi ke Gemini 3.6 Flash berhasil, dapat respons "OK". Rate limit
free tier dicatat: 15 RPM, 1500 RPD -- relevan untuk Hari 15
(rate limit handling).
