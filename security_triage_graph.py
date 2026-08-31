"""
Security Triage Agent — LangGraph
Fase 3 (Hari 11+) proyek secure-fastapi-agent.

Alur:
  read_findings -> classify_severity -> [conditional]
                                          |-> flag_for_review (severity tinggi)
                                          |-> auto_note        (severity rendah)
  keduanya -> summarize -> END

Model: Gemini 3.6 Flash (free tier, no card)
Catatan Hari 10: temperature diabaikan model ini (fixed sampling
defaults) -- output tidak dijamin 100% deterministik antar run.
"""

import os
from typing import TypedDict, Literal

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

from scan_parsers import combine_all

load_dotenv()


# ---------------------------------------------------------------------------
# 1. STATE — data yang mengalir dan terakumulasi di sepanjang graph
# ---------------------------------------------------------------------------
class TriageState(TypedDict):
    raw_findings: list[dict]       # hasil gabungan dari scan_parsers.combine_all
    severity: Literal["high", "low", None]
    flagged_findings: list[dict]   # perlu review manusia
    noted_findings: list[dict]     # cukup dicatat, tidak blocking
    summary: str                   # ringkasan bahasa manusia buat komentar PR


# ---------------------------------------------------------------------------
# 2. LLM CLIENT
# ---------------------------------------------------------------------------
llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")


def extract_text(response) -> str:
    """
    Helper wajib untuk model ini (temuan Hari 10):
    response.content BUKAN string polos, tapi list of dict
    ([{"type": "text", "text": ..., "extras": {...}}]).
    Fungsi ini menangani dua kemungkinan bentuk supaya aman
    dipakai di mana pun response di-invoke.
    """
    content = response.content
    if isinstance(content, str):
        return content
    if isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict):
            return first.get("text", "")
    return str(content)


# ---------------------------------------------------------------------------
# 3. NODES
# ---------------------------------------------------------------------------
def read_findings(state: TriageState) -> dict:
    """
    Ambil hasil scan dari 5 gate lewat scan_parsers.combine_all --
    reuse parser yang sudah divalidasi sejak Hari 2-5, bukan baca
    ulang combined.json secara independen.

    Testable by design: kalau raw_findings SUDAH diisi manual di state
    awal (dipakai test_scenarios.py di Hari 13), node ini skip baca
    file dan langsung pakai data yang diberikan -- supaya skenario
    palsu bisa diuji tanpa perlu menimpa file scan_results/ asli.

    PENTING: pakai `is not None`, BUKAN truthy check biasa (`if x:`).
    List kosong ([]) itu falsy di Python, jadi `if state.get(...)`
    akan salah mengira skenario "kosong" sebagai "belum diisi" dan
    tetap baca file asli -- persis bug yang ditemukan waktu testing
    skenario "kosong" di Hari 13 (hasilnya 32 temuan dari file asli,
    padahal seharusnya 0).
    """
    if state.get("raw_findings") is not None:
        return {"raw_findings": state["raw_findings"]}

    findings = combine_all(
        bandit_path="scan_results/bandit.json",
        trivy_path="scan_results/trivy.json",
        gitleaks_path="scan_results/gitleaks.json",
        pip_audit_path="scan_results/pip-audit.json",
        trivy_image_path="scan_results/trivy-image.json",
    )
    return {"raw_findings": findings}


def classify_severity(state: TriageState) -> dict:
    """Severity keseluruhan -- rule-based, konsisten dengan Evaluate gates di CI."""
    findings = state["raw_findings"]
    has_critical = any(f.get("severity") in ("CRITICAL", "HIGH") for f in findings)
    return {"severity": "high" if has_critical else "low"}


def route_by_severity(state: TriageState) -> str:
    """Conditional edge -- return NAMA NODE tujuan, bukan update state."""
    return "flag_for_review" if state["severity"] == "high" else "auto_note"


def flag_for_review(state: TriageState) -> dict:
    return {"flagged_findings": state["raw_findings"]}


def auto_note(state: TriageState) -> dict:
    return {"noted_findings": state["raw_findings"]}


def summarize(state: TriageState) -> dict:
    """Node terakhir -- LLM merangkum jadi komentar PR yang bisa dibaca manusia."""
    findings = state.get("flagged_findings") or state.get("noted_findings") or []

    if not findings:
        return {"summary": "Tidak ada temuan security dari pipeline."}

    import json
    from collections import Counter

    # Hitung pakai kode, BUKAN diserahkan ke LLM -- percobaan Hari 11
    # membuktikan LLM menghitung dengan salah (19 LOW/13 MEDIUM asli
    # dilaporkan jadi cuma 6 LOW/7 MEDIUM). Angka harus akurat,
    # LLM tugasnya cuma merangkum kalimat, bukan berhitung.
    severity_count = Counter(f["severity"] for f in findings)
    tool_count = Counter(f["tool"] for f in findings)

    stats_text = (
        f"Total temuan: {len(findings)}\n"
        f"Per severity: {dict(severity_count)}\n"
        f"Per tool: {dict(tool_count)}"
    )

    prompt = (
        "Berikut statistik temuan security yang SUDAH DIHITUNG DENGAN BENAR "
        "(jangan hitung ulang atau ubah angkanya):\n\n"
        f"{stats_text}\n\n"
        "Buat ringkasan naratif untuk komentar Pull Request dalam Bahasa "
        "Indonesia, singkat, actionable, maksimal 5 poin. Boleh sebutkan "
        "contoh 2-3 temuan paling kritis dari data mentah berikut sebagai "
        "ilustrasi, tapi JANGAN membuat breakdown angka baru selain yang "
        "sudah diberikan di atas:\n\n"
        f"{json.dumps(findings[:10], indent=2)}"
    )
    response = llm.invoke(prompt)
    llm_narrative = extract_text(response)

    # Statistik akurat tetap disertakan eksplisit di luar hasil LLM,
    # sebagai jaring pengaman kalau LLM tetap mengarang angka lagi.
    return {"summary": f"**Statistik (dihitung langsung, bukan oleh AI):**\n{stats_text}\n\n**Ringkasan AI:**\n{llm_narrative}"}


# ---------------------------------------------------------------------------
# 4. BUILD GRAPH
# ---------------------------------------------------------------------------
def build_graph():
    graph = StateGraph(TriageState)

    graph.add_node("read_findings", read_findings)
    graph.add_node("classify_severity", classify_severity)
    graph.add_node("flag_for_review", flag_for_review)
    graph.add_node("auto_note", auto_note)
    graph.add_node("summarize", summarize)

    graph.set_entry_point("read_findings")
    graph.add_edge("read_findings", "classify_severity")

    graph.add_conditional_edges(
        "classify_severity",
        route_by_severity,
        {"flag_for_review": "flag_for_review", "auto_note": "auto_note"},
    )

    graph.add_edge("flag_for_review", "summarize")
    graph.add_edge("auto_note", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()


# ---------------------------------------------------------------------------
# 5. ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        raise SystemExit("GOOGLE_API_KEY tidak ditemukan. Cek .env kamu.")

    app = build_graph()
    result = app.invoke({
        "raw_findings": None, "severity": None,
        "flagged_findings": [], "noted_findings": [], "summary": "",
    })
    print("Severity:", result["severity"])
    print("Summary:\n", result["summary"])