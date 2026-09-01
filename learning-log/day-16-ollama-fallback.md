# Hari 16 — Fallback ke Ollama

## Tujuan
Kalau Gemini gagal total (bukan cuma transient), pindah ke Ollama
lokal sebagai fallback, supaya agent tetap bisa menghasilkan ringkasan.

## Alur
```
summarize node
│
▼
invoke_with_fallback(prompt)
│
├─ coba Gemini (invoke_with_retry, sampai 4x, exponential backoff)
│ ├─ berhasil -> (teks, "gemini-3.6-flash")
│ └─ retry habis -> lanjut ke Ollama
│ ├─ Ollama berhasil -> (teks, "ollama (llama3.1:8b, fallback)")
│ │ -> ditandai eksplisit ⚠️ di output
│ └─ Ollama JUGA gagal -> RuntimeError
│ -> statistik tetap tampil, narasi di-skip
```

## Kendala & fix (bug signifikan, ditemukan lewat testing eksplisit)
- Percobaan test pertama (sengaja rusak API key): script CRASH TOTAL,
  tidak fallback ke Ollama sama sekali, tidak ada triage_output.md
  dihasilkan.
- Akar masalah: except clause menangkap `google.genai.errors.ClientError`,
  padahal `langchain_google_genai` MEMBUNGKUS ULANG error itu jadi
  exception class miliknya sendiri (`GoogleInvalidRequestError`) --
  bukan subclass ClientError, jadi except tidak pernah ke-trigger.
  Retry tidak jalan, fallback tidak kepicu.
- Fix: tangkap base class `GoogleGenerativeAIError` (dari
  `langchain_google_genai._common`), yang menaungi semua exception
  spesifik library ini (invalid request, model not found, auth,
  rate limit, dst). Trade-off: retry jadi kepicu juga untuk error
  non-transient (buang beberapa detik), tapi jauh lebih aman
  daripada tidak tertangkap sama sekali.
- Model fallback diganti dari qwen2.5-coder:7b (tidak terinstall)
  ke llama3.1:8b (sudah ada, general-purpose lebih cocok untuk
  merangkum teks, bukan tugas coding).

## Hasil akhir
Fallback terbukti bekerja end-to-end: statistik akurat tetap tampil,
narasi dihasilkan Ollama dengan penanda jelas provider yang dipakai.
Durasi lebih lama saat fallback (retry 3x backoff + generate Ollama
CPU-bound) -- wajar, bukan bug performa.
