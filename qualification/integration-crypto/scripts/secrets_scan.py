"""integration-crypto, SECRETS_CLEAN: nenhum segredo nos diffs da missão, nos logs, nos relatórios e nos artefatos de CI.

Varre (1) o diff de cada repositório alterado pela missão, da base até o commit final (git diff, linhas acrescentadas),
e (2) todos os arquivos de qualification/integration-crypto/ (RAW_LOGS, relatórios, scripts, fixtures), procurando
padrões de token/chave (GitHub, AWS, chaves privadas PEM, Slack, Google, OpenAI/Anthropic, atribuições de segredo com
valor). O relatório lista só o arquivo, a linha e o nome do padrão, nunca o valor. Complementa, sem substituir, os
scanners dos CIs (gitleaks do ecosystem, scan_secrets.py do cripto).
Uso: python secrets_scan.py <clones> <checkout predictor-qualification> <out.json>
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

PATTERNS = {
    "github_token": re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}"),
    "github_pat": re.compile(r"github_pat_[A-Za-z0-9_]{40,}"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "pem_private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "slack_token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    "llm_api_key": re.compile(r"\b(sk-ant-[A-Za-z0-9_\-]{20,}|sk-[A-Za-z0-9]{40,})"),
    "secret_assignment": re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\b\s*[:=]\s*['\"][A-Za-z0-9/+_\-]{16,}['\"]"),
}
DIFFS = {
    "cain": ("f343701937a7a798d66e11d2d8aa18e24395e215", "6b460afd5f19e8a1739a09a9eaabab1dbe98084f"),
    "ecosystem-predictor": ("49ffb16380d2e91eb7e4a2a936e63ba779c29033", "a19655f45f84842fea9f331429aa30d2c9ee4394"),
    "cripto-predictor": ("341d270e4d709150c581c3cd93f4518d483009eb", "ee3d3d17de0b76cf731808243ffa838a0f5ee8cc"),
}


def scan(label: str, text: str, hits: list) -> int:
    lines = 0
    for n, line in enumerate(text.splitlines(), start=1):
        lines += 1
        for name, pattern in PATTERNS.items():
            if pattern.search(line):
                hits.append({"where": label, "line": n, "pattern": name})
    return lines


def main() -> int:
    repos, qual, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    hits: list = []
    scanned = {}
    for repo, (base, final) in DIFFS.items():
        diff = subprocess.run(["git", "-C", str(repos / repo), "diff", base, final], capture_output=True, text=True,
                              check=True).stdout
        added = "\n".join(line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
        scanned[f"{repo} {base[:12]}..{final[:12]}"] = scan(f"{repo}:diff", added, hits)
    mission = qual / "qualification" / "integration-crypto"
    files = 0
    for path in sorted(mission.rglob("*")):
        if path.is_file() and path.name != "secrets_scan.py":
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            files += 1
            scan(path.relative_to(qual).as_posix(), text, hits)
    scanned["qualification/integration-crypto files"] = files
    doc = {"schema": "integration-crypto/SECRETS_SCAN/1", "patterns": sorted(PATTERNS), "scanned": scanned,
           "findings": hits, "clean": not hits}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"clean": doc["clean"], "findings": len(hits), "scanned": scanned}))
    return 0 if doc["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
