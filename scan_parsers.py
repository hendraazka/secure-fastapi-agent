"""
Parser & normalizer untuk 4 gate proyek FastAPI DevSecOps baru.
Menyatukan output Bandit, Trivy, Gitleaks, pip-audit ke satu skema:

    {
        "tool": str,
        "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
        "title": str,
        "location": str,   # file:line kalau ada
    }

Dipakai oleh node `read_findings` di security_triage_graph.py
"""

import json
from pathlib import Path


def parse_bandit(path: str) -> list[dict]:
    """Bandit punya field severity native — tinggal mapping langsung."""
    data = json.loads(Path(path).read_text())
    findings = []
    for r in data.get("results", []):
        findings.append({
            "tool": "bandit",
            "severity": r["issue_severity"].upper(),  # LOW/MEDIUM/HIGH
            "title": r["issue_text"],
            "location": f"{r['filename']}:{r['line_number']}",
        })
    return findings


def parse_trivy(path: str) -> list[dict]:
    """Trivy: severity ada di tiap vulnerability, bukan di level Result."""
    data = json.loads(Path(path).read_text())
    findings = []
    for result in data.get("Results", []) or []:
        for vuln in result.get("Vulnerabilities", []) or []:
            findings.append({
                "tool": "trivy",
                "severity": vuln.get("Severity", "LOW").upper(),  # sudah termasuk CRITICAL
                "title": f"{vuln['VulnerabilityID']}: {vuln.get('Title', '')}",
                "location": result.get("Target", "unknown"),
            })
    return findings


def parse_gitleaks(path: str) -> list[dict]:
    """
    Gitleaks TIDAK punya field severity.
    Keputusan desain: setiap secret yang bocor = HIGH, tanpa pengecualian.

    Output gitleaks-action berformat SARIF (dict dengan key "runs"),
    BUKAN list datar. Kalau tidak ada leak, workflow kita nulis "[]"
    (list kosong) sebagai fallback -- jadi fungsi ini harus menangani
    dua bentuk: dict SARIF asli, atau list kosong dari fallback.
    """
    raw = Path(path).read_text().strip()
    if not raw or raw in ("[]", "null"):
        return []

    data = json.loads(raw)
    if isinstance(data, list):
        return []

    findings = []
    for run in data.get("runs", []):
        for result in run.get("results", []):
            rule_id = result.get("ruleId", "unknown-rule")
            message = result.get("message", {}).get("text", "")

            location = "?"
            locations = result.get("locations", [])
            if locations:
                phys = locations[0].get("physicalLocation", {})
                uri = phys.get("artifactLocation", {}).get("uri", "?")
                line = phys.get("region", {}).get("startLine", "?")
                location = f"{uri}:{line}"

            findings.append({
                "tool": "gitleaks",
                "severity": "HIGH",
                "title": f"Secret terdeteksi: {rule_id} - {message}".strip(" -"),
                "location": location,
            })
    return findings


def parse_pip_audit(path: str) -> list[dict]:
    """
    pip-audit juga tanpa severity langsung.
    Keputusan desain: default MEDIUM, kecuali kamu cross-check CVE
    ke NVD/OSV untuk dapat skor CVSS asli (di luar scope pipeline ringan ini).
    """
    data = json.loads(Path(path).read_text())
    findings = []
    for dep in data.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            findings.append({
                "tool": "pip-audit",
                "severity": "MEDIUM",
                "title": f"{dep['name']}=={dep['version']} rentan ({vuln['id']})",
                "location": "requirements.txt",
            })
    return findings


def combine_all(bandit_path: str, trivy_path: str,
                 gitleaks_path: str, pip_audit_path: str) -> list[dict]:
    """Gabungkan 4 sumber jadi satu list untuk dilempar ke TriageState."""
    findings = []
    findings += parse_bandit(bandit_path)
    findings += parse_trivy(trivy_path)
    findings += parse_gitleaks(gitleaks_path)
    findings += parse_pip_audit(pip_audit_path)
    return findings


if __name__ == "__main__":
    # sesuaikan path output tiap tool dari GitHub Actions artifact
    combined = combine_all(
        bandit_path="scan_results/bandit.json",
        trivy_path="scan_results/trivy.json",
        gitleaks_path="scan_results/gitleaks.json",
        pip_audit_path="scan_results/pip-audit.json",
    )
    Path("scan_results/combined.json").write_text(json.dumps(combined, indent=2))
    print(f"{len(combined)} findings digabungkan -> scan_results/combined.json")
