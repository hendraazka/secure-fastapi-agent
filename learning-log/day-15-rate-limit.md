# Hari 15 — Rate Limit Handling

## Tujuan
Tambah retry logic ke pemanggilan Gemini API, supaya gangguan
rate limit sesaat tidak langsung menggagalkan graph.

## Alur
```
summarize node
│
▼
invoke_with_retry(llm, prompt)
│
├─ percobaan 1 (langsung)
├─ percobaan 2 (tunggu ~2s) ─┐ retry HANYA untuk ClientError
├─ percobaan 3 (tunggu ~4s) │ (rate limit/overload),
└─ percobaan 4 (tunggu ~8s) ─┘ bukan semua jenis error
│
├─ berhasil -> lanjut normal
└─ semua gagal -> graceful degradation:
statistik akurat tetap tampil,
narasi AI diganti pesan error jelas
```


## Yang dikerjakan
- `invoke_with_retry()` pakai `tenacity` (sudah jadi dependency
  transitive dari google-genai, dideklarasikan eksplisit di
  requirements-agent.txt)
- Retry dibatasi ke `ClientError` saja -- error soal API key salah
  atau model tidak ada TIDAK di-retry (percuma, tidak akan membantu)
- Exponential backoff (2s/4s/8s), bukan interval tetap
- Graceful degradation: kalau retry habis, statistik dari Counter
  tetap tampil, cuma narasi AI yang di-skip dengan pesan jelas

## Kendala & fix
- Sempat lupa aktifkan venv di sesi terminal baru -> ModuleNotFoundError
  langgraph. Bukan bug kode, cuma environment belum di-source.

## Hasil akhir
4 skenario test masih PASS semua -- tidak ada regresi. Rate limit
tidak ter-trigger di praktik (limit free tier cukup longgar untuk
testing solo), jadi retry logic ini defensive untuk kondisi yang
mungkin tapi belum tentu terjadi, bukan dibuktikan lewat kegagalan nyata.
