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
# rc16 (2026-10-07): do final anterior (rc15/rc7/rc4, já varrido em secrets-rc15) ao final novo de runtime_targets.json;
# o transporte (rc7) e o cripto (rc4) não mudam, então só o cain tem intervalo novo. Os intervalos anteriores:
# rc13→rc15 (secrets-rc15), base→rc13 (secrets-rc13). O clone do ecosystem usa o nome atual do repositório.
_TARGETS = json.loads((Path(__file__).resolve().parents[1] / "runtime_targets.json").read_text(encoding="utf-8"))
DIFFS = {
    "cain": ("ae00017ab4a2ce602998e8fbdb8b20be95aad99d", _TARGETS["cain"]["commit"]),
    _TARGETS["transport"]["repo"].split("/")[1]: ("b0da4fd8d0c472b3ab7d33acf0946e5d10a02754", _TARGETS["transport"]["commit"]),
    "cripto-predictor": ("21f8b182286248859e1b2cb8fa2bab0138a58e2a", _TARGETS["cripto"]["commit"]),
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
