"""
Hari 13 — Test graph dengan beberapa skenario data.

Menguji apakah routing (flag_for_review vs auto_note) berperilaku
benar untuk 3 kondisi berbeda, TANPA perlu menimpa file scan_results/
asli -- memanfaatkan perilaku read_findings yang skip baca file kalau
raw_findings sudah diisi manual (lihat security_triage_graph.py).
"""

from security_triage_graph import build_graph

app = build_graph()


SCENARIOS = {
    "semua_low": [
        {"tool": "bandit", "severity": "LOW", "title": "Contoh temuan LOW 1", "location": "app/main.py:1"},
        {"tool": "pip-audit", "severity": "MEDIUM", "title": "Contoh temuan MEDIUM 1", "location": "requirements.txt"},
    ],
    "ada_critical": [
        {"tool": "trivy-image", "severity": "CRITICAL", "title": "CVE-XXXX-0001: contoh critical", "location": "base image"},
        {"tool": "bandit", "severity": "LOW", "title": "Contoh temuan LOW", "location": "app/main.py:5"},
    ],
    "campuran": [
        {"tool": "gitleaks", "severity": "HIGH", "title": "Secret terdeteksi: contoh", "location": "app/config.py:3"},
        {"tool": "trivy", "severity": "MEDIUM", "title": "CVE-XXXX-0002: contoh medium", "location": "requirements.txt"},
        {"tool": "bandit", "severity": "LOW", "title": "Contoh temuan LOW", "location": "app/main.py:9"},
    ],
    "kosong": [],
}


def run_scenario(name: str, findings: list[dict]):
    print(f"\n{'=' * 60}")
    print(f"SKENARIO: {name}")
    print(f"{'=' * 60}")

    result = app.invoke({
        "raw_findings": findings,
        "severity": None,
        "flagged_findings": [],
        "noted_findings": [],
        "summary": "",
    })

    print(f"Severity terdeteksi : {result['severity']}")
    print(f"Masuk flagged?       : {bool(result['flagged_findings'])}")
    print(f"Masuk noted?         : {bool(result['noted_findings'])}")
    print(f"Summary:\n{result['summary']}")

    return result


if __name__ == "__main__":
    results = {}
    for name, findings in SCENARIOS.items():
        results[name] = run_scenario(name, findings)

    # Assertion sederhana -- verifikasi routing benar, bukan cuma "jalan tanpa error"
    print(f"\n{'=' * 60}")
    print("VERIFIKASI ROUTING")
    print(f"{'=' * 60}")

    checks = [
        ("semua_low routes to auto_note", results["semua_low"]["severity"] == "low"),
        ("ada_critical routes to flag_for_review", results["ada_critical"]["severity"] == "high"),
        ("campuran (ada HIGH) routes to flag_for_review", results["campuran"]["severity"] == "high"),
        ("kosong routes to auto_note", results["kosong"]["severity"] == "low"),
    ]

    for description, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {description}")

    if all(passed for _, passed in checks):
        print("\nSemua skenario routing sesuai ekspektasi.")
    else:
        print("\nADA SKENARIO YANG ROUTING-NYA SALAH -- cek route_by_severity.")

