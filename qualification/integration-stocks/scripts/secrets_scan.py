"""integration-stocks, SECRETS_CLEAN: nenhum segredo nos diffs da missão, nos logs, nos relatórios e nos artefatos de CI.

Varre (1) o diff de cada repositório alterado pela missão, da base até o commit final (git diff, linhas acrescentadas),
e (2) todos os arquivos de qualification/integration-stocks/ (RAW_LOGS, relatórios, scripts, fixtures), procurando
padrões de token/chave (GitHub, AWS, chaves privadas PEM, Slack, Google, OpenAI/Anthropic, atribuições de segredo com
valor). O relatório lista só o arquivo, a linha e o nome do padrão, nunca o valor. Complementa, sem substituir, os
scanners dos CIs (gitleaks do ecosystem, scan_secrets.py do cripto).
Adaptado de qualification/integration-crypto/scripts/secrets_scan.py (mesma lógica; missão integration-stocks).
Os commits finais vêm de runtime_targets.json (ciclo 2: cain 0.4.13rc11 e transporte 0.1.0rc5); as bases são as do
baseline da missão.
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
TARGETS = json.loads((Path(__file__).resolve().parents[1] / "runtime_targets.json").read_text(encoding="utf-8"))
# c6 (2026-10-07): o cain é varrido do final do ciclo 5 (rc15) ao final novo; transporte e stocks não mudam (intervalos já varridos em
# secrets-c5); o clone do ecosystem usa o nome atual do repositório (runtime_targets.json).
DIFFS = {
    "cain": ("ae00017ab4a2ce602998e8fbdb8b20be95aad99d", TARGETS["cain"]["commit"]),
    TARGETS["transport"]["repo"].split("/")[1]: ("b0da4fd8d0c472b3ab7d33acf0946e5d10a02754", TARGETS["transport"]["commit"]),
    "stocks-predictor": ("61fc017256ffea815ae96bbe02b847dccdb395cc", TARGETS["stocks"]["commit"]),
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
    mission = qual / "qualification" / "integration-stocks"
    files = 0
    for path in sorted(mission.rglob("*")):
        if path.is_file() and path.name != "secrets_scan.py":
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            files += 1
            scan(path.relative_to(qual).as_posix(), text, hits)
    scanned["qualification/integration-stocks files"] = files
    doc = {"schema": "integration-stocks/SECRETS_SCAN/1", "patterns": sorted(PATTERNS), "scanned": scanned,
           "findings": hits, "clean": not hits}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"clean": doc["clean"], "findings": len(hits), "scanned": scanned}))
    return 0 if doc["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
